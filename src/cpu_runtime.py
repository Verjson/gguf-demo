"""
CPU budget detection and threading policy for local inference.

Token-by-token decoding is memory-bandwidth bound, so throughput comes from letting
one generation use every core it is allowed rather than running several generations
beside each other. Sizing that thread pool from ``os.cpu_count()`` is wrong as soon
as the demo runs in a container: a process granted 2 CPUs still sees every core on
the host, and 32 threads on a 2-CPU quota spend more time in synchronization and
cgroup throttling than they ever return in useful work.

So the ceiling comes from what the process was actually granted — a cgroup quota or
a CPU affinity mask, whichever is smaller. Picking the thread count *under* that
ceiling is the harder half, because the best value is neither the ceiling nor the
physical core count:

* Filling every logical CPU falls off a cliff. Nothing is left for the process's own
  bookkeeping threads, and hyperthread siblings evict each other's cache lines.
* Folding siblings into physical cores assumes ``/proc/cpuinfo`` tells the truth. Under
  WSL2 an i9-14900HX (8 P-cores + 16 E-cores, 32 threads) is reported as a uniform
  "16 cores x 2 threads", so folding hands back 16 threads and idles 8 real cores.

Measured on that laptop, generating 32 tokens from a RAG-sized prompt: 16 threads gave
1.26 tok/s, 24 gave 1.62, 28 gave 1.73, and 32 fell back to 1.50. Guessing from the
reported topology cost 37% against simply measuring.

:func:`calibrate` therefore times a small stand-in for the real workload — one
memory-bound GEMV chain shaped like decode, one compute-bound GEMM shaped like
prefill — at a handful of candidate thread counts, and caches the winner per machine.
It costs a few seconds once and ranks candidates the same way full generations do.
"""

from __future__ import annotations

import json
import logging
import math
import os
import time
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

CGROUP_V2_CPU_MAX = "/sys/fs/cgroup/cpu.max"
CGROUP_V1_QUOTA = "/sys/fs/cgroup/cpu/cpu.cfs_quota_us"
CGROUP_V1_PERIOD = "/sys/fs/cgroup/cpu/cpu.cfs_period_us"
CGROUP_V2_MEMORY_MAX = "/sys/fs/cgroup/memory.max"
CGROUP_V1_MEMORY_MAX = "/sys/fs/cgroup/memory/memory.limit_in_bytes"

# Single knob for "how much CPU may the demo use", shared with docker-compose.yml.
CPU_BUDGET_ENV = "APP_CPUS"
# Set to 0/false to skip measurement and take the conservative heuristic instead.
CALIBRATE_ENV = "CPU_CALIBRATE"
CACHE_PATH_ENV = "CPU_BUDGET_CACHE"

DEFAULT_CACHE_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "processed" / "cpu_budget.json"
)

# Below this many cores there is nothing worth choosing between, and the measurement
# would cost a larger share of the run than it could ever win back.
MIN_CORES_TO_CALIBRATE = 8

# Phi-3-mini's MLP shapes, so the probe stresses the same kernels generation does.
_HIDDEN = 3072
_INTERMEDIATE = 8192
_PREFILL_TOKENS = 256
_WEIGHT_PAIRS = 4
# Score a candidate by the answer it would produce, not by equal parts of each
# phase: a RAG answer prefills one prompt of roughly 2 x _PREFILL_TOKENS and then
# decodes a couple of hundred tokens, so decode is what a run actually waits on.
# Weighting them equally hides the oversubscription cliff, which shows up in decode.
_DECODE_STEPS = 200
_PREFILL_PASSES = 2
TIE_TOLERANCE = 1.05
_SMALL_WEIGHT_PAIRS = 1
# Keep the probe's weights well under a small container's memory limit.
_PAIR_BYTES = 2 * _HIDDEN * _INTERMEDIATE * 2
_MEMORY_FOR_FULL_PROBE = 3 * 1024**3

_budget_cache: int | None = None
_budget_source = "unmeasured"


def _read_text(path: str) -> str | None:
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read().strip()
    except OSError:
        return None


def cgroup_cpu_quota() -> float | None:
    """CPUs granted by a cgroup quota, or None when unlimited or unreadable."""
    v2 = _read_text(CGROUP_V2_CPU_MAX)
    if v2:
        quota, _, period = v2.partition(" ")
        if quota == "max":
            return None
        try:
            return int(quota) / (int(period) or 100_000)
        except ValueError:
            logger.debug("Unparsable %s: %r", CGROUP_V2_CPU_MAX, v2)

    quota_text = _read_text(CGROUP_V1_QUOTA)
    period_text = _read_text(CGROUP_V1_PERIOD)
    if quota_text and period_text:
        try:
            quota_us, period_us = int(quota_text), int(period_text)
        except ValueError:
            return None
        if quota_us > 0 and period_us > 0:
            return quota_us / period_us
    return None


def cgroup_memory_limit() -> int | None:
    """Bytes of memory this process may use, or None when effectively unlimited."""
    for path in (CGROUP_V2_MEMORY_MAX, CGROUP_V1_MEMORY_MAX):
        text = _read_text(path)
        if not text or text == "max":
            continue
        try:
            limit = int(text)
        except ValueError:
            continue
        # cgroup v1 reports a sentinel near 2^63 to mean "no limit".
        if 0 < limit < 1 << 60:
            return limit
    return None


def allowed_cpus() -> set[int]:
    """Logical CPUs this process may be scheduled on (honors cpuset / taskset)."""
    try:
        return set(os.sched_getaffinity(0))
    except (AttributeError, OSError):
        return set(range(os.cpu_count() or 1))


def physical_cores(allowed: set[int] | None = None) -> int | None:
    """
    Distinct physical cores behind `allowed`, or None if topology is not exposed.

    Only trustworthy on bare metal. Hypervisors are free to invent the sibling map,
    which is why this feeds the fallback heuristic rather than the measured budget.
    """
    text = _read_text("/proc/cpuinfo")
    if not text:
        return None
    allowed = allowed if allowed is not None else allowed_cpus()

    cores: set[tuple[str, str]] = set()
    for block in text.split("\n\n"):
        fields = {}
        for line in block.splitlines():
            key, sep, value = line.partition(":")
            if sep:
                fields[key.strip()] = value.strip()
        try:
            cpu = int(fields["processor"])
        except (KeyError, ValueError):
            continue
        if cpu not in allowed:
            continue
        package, core = fields.get("physical id"), fields.get("core id")
        if package is None or core is None:
            return None  # Common on VMs and ARM; fall back to the logical count.
        cores.add((package, core))
    return len(cores) or None


def cpu_model() -> str:
    """CPU model string, used to tell one machine's cached budget from another's."""
    text = _read_text("/proc/cpuinfo") or ""
    for line in text.splitlines():
        key, sep, value = line.partition(":")
        if sep and key.strip() == "model name":
            return value.strip()
    return "unknown"


def cpu_ceiling() -> int:
    """Most threads the process may run without exceeding its grant."""
    ceiling = len(allowed_cpus()) or 1
    quota = cgroup_cpu_quota()
    if quota:
        # Floor, so a fractional grant (say 2.5 CPUs) still leaves room for the
        # process's own bookkeeping threads instead of provoking throttling.
        ceiling = min(ceiling, max(1, math.floor(quota)))
    return max(1, ceiling)


def heuristic_budget() -> int:
    """
    Thread count to use when measurement is unavailable or switched off.

    Folds hyperthread siblings when the topology is exposed. That under-uses hybrid
    CPUs behind a hypervisor, but never oversubscribes, which is the safer error.
    """
    ceiling = cpu_ceiling()
    cores = physical_cores()
    return max(1, min(ceiling, cores) if cores else ceiling)


def thread_candidates(ceiling: int) -> list[int]:
    """Thread counts worth measuring under `ceiling`, smallest first."""
    if ceiling < MIN_CORES_TO_CALIBRATE:
        return [ceiling]
    candidates = {ceiling, ceiling - 2, ceiling - 4, ceiling * 3 // 4, ceiling // 2}
    return sorted(c for c in candidates if 1 <= c <= ceiling)


def _probe_weights(pairs: int):
    import torch

    def block(rows: int, cols: int):
        # fill_ touches every page: freshly allocated pages would otherwise all map to
        # the shared zero page and the probe would measure cache, not memory.
        return torch.empty(rows, cols, dtype=torch.bfloat16).fill_(0.01)

    ups = [block(_INTERMEDIATE, _HIDDEN) for _ in range(pairs)]
    downs = [block(_HIDDEN, _INTERMEDIATE) for _ in range(pairs)]
    return ups, downs


def _probe(threads: int, ups, downs, decode_in, prefill_in) -> float:
    """Modelled seconds per answer at `threads`; lower is better."""
    import torch
    from torch.nn.functional import linear

    torch.set_num_threads(threads)

    def per_pass(x, reps: int) -> float:
        for up, down in zip(ups, downs):  # warm the pool and the weights
            linear(linear(x, up), down)
        start = time.perf_counter()
        for _ in range(reps):
            for up, down in zip(ups, downs):
                linear(linear(x, up), down)
        return (time.perf_counter() - start) / reps

    decode = per_pass(decode_in, 20)
    prefill = per_pass(prefill_in, 2)
    return _DECODE_STEPS * decode + _PREFILL_PASSES * prefill


def calibrate(ceiling: int | None = None) -> tuple[int, dict[str, float]]:
    """Measure candidate thread counts and return the best, with the raw timings."""
    import torch

    ceiling = ceiling if ceiling is not None else cpu_ceiling()
    candidates = thread_candidates(ceiling)
    if len(candidates) == 1:
        return candidates[0], {}

    limit = cgroup_memory_limit()
    pairs = (
        _SMALL_WEIGHT_PAIRS
        if limit and limit < _MEMORY_FOR_FULL_PROBE
        else _WEIGHT_PAIRS
    )

    previous = torch.get_num_threads()
    try:
        with torch.inference_mode():
            ups, downs = _probe_weights(pairs)
            decode_in = torch.empty(1, _HIDDEN, dtype=torch.bfloat16).fill_(0.01)
            prefill_in = torch.empty(
                _PREFILL_TOKENS, _HIDDEN, dtype=torch.bfloat16
            ).fill_(0.01)
            # Best of two sweeps: a single pass can lose to a passing background
            # task, and neighbouring candidates are often within a few percent.
            timings: dict[str, float] = {}
            for _ in range(2):
                for n in candidates:
                    seconds = _probe(n, ups, downs, decode_in, prefill_in)
                    key = str(n)
                    timings[key] = min(timings.get(key, seconds), seconds)
    finally:
        torch.set_num_threads(previous)

    best = min(timings.values())
    # Prefer the smallest thread count within a few percent of the winner. Neighbouring
    # candidates land inside the probe's own noise, and the probe has the machine to
    # itself while a real run shares it with Postgres, MLflow and Prometheus — so spare
    # cores are worth more than a difference this measurement cannot resolve.
    budget = min(
        int(n) for n, seconds in timings.items() if seconds <= best * TIE_TOLERANCE
    )
    return budget, timings


def _cache_path() -> Path:
    return Path(os.environ.get(CACHE_PATH_ENV) or DEFAULT_CACHE_PATH)


def _signature(ceiling: int) -> str:
    import torch

    quota = cgroup_cpu_quota()
    return "|".join(
        (
            cpu_model(),
            f"allowed={len(allowed_cpus())}",
            f"ceiling={ceiling}",
            f"quota={quota:.2f}" if quota else "quota=none",
            f"torch={torch.__version__}",
        )
    )


def _load_cached(signature: str) -> int | None:
    try:
        with _cache_path().open(encoding="utf-8") as handle:
            entry = json.load(handle).get(signature)
    except (OSError, ValueError):
        return None
    if isinstance(entry, dict) and isinstance(entry.get("budget"), int):
        return entry["budget"]
    return None


def _store_cached(signature: str, budget: int, timings: dict[str, float]) -> None:
    path = _cache_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with path.open(encoding="utf-8") as handle:
                cache = json.load(handle)
        except (OSError, ValueError):
            cache = {}
        cache[signature] = {
            "budget": budget,
            "seconds_by_threads": {k: round(v, 4) for k, v in timings.items()},
            "measured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        tmp = path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as handle:
            json.dump(cache, handle, indent=2, sort_keys=True)
        tmp.replace(path)
    except OSError as exc:  # A read-only mount must not fail the run.
        logger.debug("Could not cache the CPU budget: %s", exc)


def _calibration_enabled() -> bool:
    return os.environ.get(CALIBRATE_ENV, "1").strip().lower() not in {
        "0",
        "false",
        "no",
    }


def cpu_budget(allow_calibration: bool | None = None) -> int:
    """
    Number of threads the demo should actually use (always at least 1).

    Measures once per machine unless `allow_calibration` (or CPU_CALIBRATE) says not
    to, then remembers the answer for the life of the process.
    """
    global _budget_cache, _budget_source
    if _budget_cache is not None:
        return _budget_cache

    if allow_calibration is None:
        allow_calibration = _calibration_enabled()

    override = os.environ.get(CPU_BUDGET_ENV, "").strip()
    if override:
        try:
            _budget_cache, _budget_source = max(1, int(float(override))), "override"
            return _budget_cache
        except ValueError:
            logger.warning("Ignoring invalid %s=%r", CPU_BUDGET_ENV, override)

    ceiling = cpu_ceiling()
    if ceiling >= MIN_CORES_TO_CALIBRATE and allow_calibration:
        try:
            signature = _signature(ceiling)
            cached = _load_cached(signature)
            if cached:
                _budget_cache, _budget_source = min(cached, ceiling), "cached"
                return _budget_cache
            logger.info("Measuring the best thread count for this machine once...")
            budget, timings = calibrate(ceiling)
            logger.info(
                "Thread probe: %s -> %d threads",
                ", ".join(f"{n}:{s:.2f}s" for n, s in sorted(timings.items(), key=lambda kv: int(kv[0]))),
                budget,
            )
            _store_cached(signature, budget, timings)
            _budget_cache, _budget_source = budget, "measured"
            return _budget_cache
        except Exception as exc:  # noqa: BLE001 - never block a run on a benchmark
            logger.warning("CPU calibration failed (%s); using the heuristic", exc)

    _budget_cache, _budget_source = heuristic_budget(), "heuristic"
    return _budget_cache


def describe_budget() -> str:
    quota = cgroup_cpu_quota()
    budget = cpu_budget()
    return (
        f"{budget} thread(s) [{_budget_source}, visible={os.cpu_count()}, "
        f"allowed={len(allowed_cpus())}, physical={physical_cores() or 'unknown'}, "
        f"cgroup_quota={f'{quota:.2f}' if quota else 'none'}]"
    )


def configure_threads(allow_calibration: bool | None = None) -> int:
    """Point torch's thread pools at the granted budget. Returns the budget."""
    import torch

    if allow_calibration is None and torch.cuda.is_available():
        # With a GPU in play the CPU pool is not the bottleneck; skip the probe.
        allow_calibration = False

    budget = cpu_budget(allow_calibration)
    torch.set_num_threads(budget)
    try:
        torch.set_num_interop_threads(1)
    except RuntimeError:
        # Fixed by an earlier parallel region; the intra-op pool is what matters.
        pass
    logger.info("CPU budget: %s", describe_budget())
    return budget


if __name__ == "__main__":  # Support tests/test_cpu_runtime.sh
    print(cpu_budget())
