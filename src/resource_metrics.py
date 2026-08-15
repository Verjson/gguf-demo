"""
Process RSS / GPU memory snapshots and simple percentiles for MLflow.

Linux ``ru_maxrss`` is kilobytes; macOS reports bytes. GPU memory uses
``torch.cuda.max_memory_allocated`` when CUDA is actually usable.
"""

from __future__ import annotations

import os
import resource
import sys
from typing import Iterable


def peak_rss_mb() -> float:
    """
    Peak resident set size for this process since it started, in MiB.

    Monotonic by definition — ``ru_maxrss`` is a high-water mark and never falls. That
    makes it a per-*process* number, so it is a per-stage fact, not a per-question one.
    Recorded on every row it produced a staircase whose first question was always the
    lowest, and averaging a staircase (the runtime dashboard did) describes nothing.
    Use :func:`current_rss_mb` for a value that can go down.
    """
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == "darwin":
        return float(rss) / (1024.0 * 1024.0)
    return float(rss) / 1024.0


def current_rss_mb() -> float:
    """
    Resident set size *right now*, in MiB, or 0.0 where it cannot be read.

    This is the one that is meaningful per question: it rises and falls with the KV
    cache and the batch, so a per-row series and its average both mean something.
    """
    try:
        with open("/proc/self/statm", encoding="utf-8") as handle:
            pages = int(handle.read().split()[1])
    except (OSError, IndexError, ValueError):
        return 0.0
    return pages * os.sysconf("SC_PAGE_SIZE") / (1024.0 * 1024.0)


def peak_gpu_mem_mb() -> float:
    """Peak CUDA allocator usage in MiB, or 0 when CUDA is not usable."""
    try:
        import torch

        from src.hardware import _cuda_is_usable

        if not _cuda_is_usable():
            return 0.0
        return float(torch.cuda.max_memory_allocated()) / (1024.0 * 1024.0)
    except Exception:  # noqa: BLE001
        return 0.0


def memory_snapshot() -> dict[str, float]:
    """
    Per-row memory figures.

    ``rss_mb`` is the live value and is what belongs on a question. ``peak_rss_mb``
    stays for continuity with existing rows and dashboards, but read it as "peak so
    far in this stage" — it is the same number for every row after the model loads.
    """
    return {
        "rss_mb": current_rss_mb(),
        "peak_rss_mb": peak_rss_mb(),
        "peak_gpu_mem_mb": peak_gpu_mem_mb(),
    }


def percentile(values: Iterable[float], p: float) -> float:
    """Linear-interpolated percentile. ``p`` is 0–100."""
    xs = sorted(float(v) for v in values)
    if not xs:
        return 0.0
    if len(xs) == 1:
        return xs[0]
    p = min(100.0, max(0.0, float(p)))
    k = (len(xs) - 1) * (p / 100.0)
    lo = int(k)
    hi = min(lo + 1, len(xs) - 1)
    if lo == hi:
        return xs[lo]
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)
