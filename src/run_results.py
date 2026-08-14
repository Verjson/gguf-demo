"""
Export evaluation artifacts into results/runs/ for version control.

Each export creates a timestamped folder plus a results/latest/ copy so you
can commit structured JSON/CSV/Markdown summaries without large PDFs or models.
"""

from __future__ import annotations

import csv
import json
import logging
import os
import shutil
import stat
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psycopg2
import yaml

from src.display_metrics import select_summary_metrics
from src.hardware import HardwareInfo, detect_hardware
from src.run_id import parse_run_id
from src.score_colors import html_table, ranked_metric_row

logger = logging.getLogger(__name__)

REPO_ROOT = Path(os.environ.get("REPO_ROOT", "/app"))
RESULTS_DIR = REPO_ROOT / "results"
RUNS_DIR = RESULTS_DIR / "runs"
LATEST_DIR = RESULTS_DIR / "latest"

PROCESSED_ARTIFACTS = (
    "comparison_report.json",
    "baseline_results.json",
    "baseline_gguf_results.json",
    "rag_results.json",
    "rag_gguf_results.json",
    "doc_stats.json",
    "qa_pairs.jsonl",
)

METRICS_COLUMNS = (
    "timestamp",
    "approach",
    "device",
    "cuda_available",
    "model_name",
    "question",
    "rouge1",
    "rouge2",
    "rougeL",
    "bert_score",
    "retrieval_hit_at_k",
    "faithfulness",
    "context_utilization",
    "answer_relevancy",
    "judge_groundedness",
    "quality_score",
    "generation_time",
    "retrieval_time",
    "time_to_response",
    "speed_chars_per_sec",
    "cuda_used",
    "domain_relevance",
    "coherence",
    "prompt_chars",
    "response_chars",
    "prompt_tokens",
    "completion_tokens",
    "tokens_per_sec",
    "context_chars",
    "n_chunks_retrieved",
    "cpu_threads",
    "cpu_logical",
    "peak_rss_mb",
    "peak_gpu_mem_mb",
)


def _aggregate(results: list[dict]) -> dict[str, float]:
    if not results:
        return {}
    keys: set[str] = set()
    for r in results:
        keys.update(r.get("metrics", {}).keys())
    agg: dict[str, float] = {}
    for key in keys:
        values = [r["metrics"][key] for r in results if key in r.get("metrics", {})]
        if values:
            agg[key] = sum(values) / len(values)
    return agg


def save_stage_results(
    stage: str,
    results: list[dict],
    hardware: HardwareInfo,
    processed_dir: str | Path,
    extra: dict[str, Any] | None = None,
) -> Path:
    """Write per-stage JSON (baseline, rag, etc.) under data/processed/."""
    processed_dir = Path(processed_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "stage": stage,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "hardware": hardware.as_params(),
        "aggregate": _aggregate(results),
        "results": results,
        **(extra or {}),
    }
    out = processed_dir / f"{stage}_results.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    logger.info("Wrote %s", out)
    return out


def _postgres_conn_kwargs() -> dict[str, str]:
    return {
        "host": os.getenv("POSTGRES_HOST", "postgres"),
        "database": os.getenv("POSTGRES_DB", "rag_eval"),
        "user": os.getenv("POSTGRES_USER", "raguser"),
        "password": os.getenv("POSTGRES_PASSWORD", "ragpass"),
    }


def export_metrics_csv(
    dest: Path,
    device: str | None = None,
    since: datetime | None = None,
    fill: dict[str, Any] | None = None,
) -> int:
    """
    Dump the evaluation_metrics table to CSV; return the row count.

    `device` and `since` scope the dump to one run. Without them a run folder ends
    up holding every row the database ever collected — a "cpu" export carrying the
    previous GPU run's rows, which is worse than useless when comparing devices.
    """
    from src.metrics_store import MetricsStore

    MetricsStore()  # add any new columns before SELECT lists them

    sql = """
        SELECT timestamp, approach, device, cuda_available, model_name, question,
               rouge1, rouge2, "rougeL", bert_score, retrieval_hit_at_k, faithfulness,
               context_utilization, answer_relevancy, judge_groundedness, quality_score,
               generation_time, retrieval_time, time_to_response, speed_chars_per_sec,
               cuda_used, domain_relevance, coherence,
               prompt_chars, response_chars, prompt_tokens, completion_tokens,
               tokens_per_sec, context_chars, n_chunks_retrieved,
               cpu_threads, cpu_logical, peak_rss_mb, peak_gpu_mem_mb
        FROM evaluation_metrics
    """
    where, params = [], []
    if device:
        where.append("device = %s")
        params.append(device)
    if since:
        where.append("timestamp >= %s")
        params.append(since)
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY timestamp DESC"

    rows: list[tuple] = []
    try:
        with psycopg2.connect(**_postgres_conn_kwargs()) as conn, conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not export Postgres metrics: %s", exc)
        return 0

    with dest.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(METRICS_COLUMNS)
        for row in rows:
            values = list(row)
            if fill:
                for index, column in enumerate(METRICS_COLUMNS):
                    if index < len(values) and values[index] in (None, "") and column in fill:
                        values[index] = fill[column]
            writer.writerow(values)
    return len(rows)


def _improvement_table(comparison: dict[str, dict[str, float]]) -> str:
    """HTML table of headline metrics only — green / yellow / red per row."""
    approaches = list(comparison.keys())
    if not approaches:
        return "_No comparison data._\n"

    metrics = select_summary_metrics(comparison)
    if not metrics:
        return "_No headline metrics in this export._\n"

    rows: list[list[str]] = []
    for metric in metrics:
        values = [comparison[approach].get(metric) for approach in approaches]
        rows.append(ranked_metric_row(metric, values, precision=4))

    legend = (
        "_Cell colors (per row): "
        "🟢 best · 🟡 mid · 🔴 worst "
        "across approaches. Differences smaller than measurement noise are left uncolored. "
        "Latency (`time_to_response`) is lower-is-better._\n"
    )
    body = html_table(["Metric", *approaches], rows, metric_col=0)

    extras: list[str] = []
    if "baseline" in comparison and "rag" in comparison:
        b = comparison["baseline"].get("rougeL")
        r = comparison["rag"].get("rougeL")
        if b and r:
            extras.append(f"**RAG rougeL vs baseline:** {(r - b) / b * 100:+.1f}%")
        b_t = comparison["baseline"].get("time_to_response") or comparison["baseline"].get(
            "generation_time"
        )
        r_t = comparison["rag"].get("time_to_response") or comparison["rag"].get("generation_time")
        if b_t and r_t and b_t > 0:
            extras.append(
                f"**RAG time_to_response vs baseline:** {r_t / b_t:.1f}× longer "
                f"({b_t:.1f}s → {r_t:.1f}s)"
            )

    return legend + "\n" + body + ("\n".join(extras) + "\n" if extras else "")


def _write_summary_md(
    dest: Path,
    manifest: dict[str, Any],
    comparison: dict[str, dict[str, float]] | None,
) -> None:
    hw = manifest.get("hardware", {})
    device = hw.get("device", "unknown")
    lines = [
        f"# Run summary — {manifest['run_id']}",
        "",
        f"- **Exported:** {manifest['exported_at']}",
        f"- **Device:** {device}",
    ]
    # Describe the hardware that produced these seconds. A CPU run's timings are
    # meaningless without the CPU and the thread count behind them.
    if device == "cuda":
        lines.append(f"- **GPU:** {hw.get('cuda_device_name', 'n/a')}")
    else:
        lines.append(
            f"- **CPU:** {hw.get('cpu_model', 'unknown')} "
            f"({hw.get('cpu_threads', '?')} of {hw.get('cpu_logical', '?')} threads)"
        )
    lines += [
        f"- **Model:** {manifest.get('llm_model', 'n/a')}",
        f"- **Metric rows (this run):** {manifest.get('postgres_rows', 0)}",
    ]
    resources = manifest.get("resources") or {}
    rss = resources.get("peak_rss_mb")
    load_s = resources.get("model_load_seconds")
    if isinstance(rss, (int, float)) and rss > 0:
        lines.append(f"- **Peak RSS:** {rss:.0f} MiB")
    gpu_mem = resources.get("peak_gpu_mem_mb")
    if isinstance(gpu_mem, (int, float)) and gpu_mem > 0:
        lines.append(f"- **Peak GPU memory:** {gpu_mem:.0f} MiB")
    if isinstance(load_s, (int, float)) and load_s > 0:
        lines.append(f"- **Model load:** {load_s:.1f}s")
    lines += [
        "",
        "## How to read improvements",
        "",
        "Higher is better for `rougeL`, `bert_score`, `faithfulness`.",
        "Lower is better for `time_to_response` (retrieval + generation — the wait for an answer).",
        "Higher is better for `tokens_per_sec`. `quality_score` is a blend and can fall when",
        "RAG's `retrieval_hit_at_k` is 0 even if overlap (`rougeL`) improved — trust rougeL",
        "for 'did RAG help?', and time_to_response / tokens_per_sec for device speed.",
        "",
        (
            "Per-metric cells are colored **green (best) / yellow (mid) / red (worst)** "
            "across approaches (open in an HTML-capable Markdown preview)."
        ),
        "",
        "## Comparison by approach",
        "",
    ]
    if comparison:
        lines.append(_improvement_table(comparison))
    else:
        lines.append("_Run step 06 or export after comparison_report.json exists._\n")

    lines.extend(
        [
            "",
            "## Expected improvement pattern",
            "",
            "| Approach | What improves |",
            "|----------|----------------|",
            "| **RAG** | rougeL, faithfulness (costs time_to_response) |",
            "| **Fine-tuned** | modest style shift, similar rougeL |",
            "| **Fine-tuned + RAG** | same RAG quality lift, same latency cost |",
            "| **CPU vs GPU** | quality within noise; GPU wins time_to_response and tokens_per_sec |",
            "",
            "## Files in this folder",
            "",
            "- `by_question.md` — every question, side by side",
            "- `manifest.json` — run metadata and CPU/GPU identity",
            "- `evaluation_metrics.csv` — one row per question (full column set)",
            "- `comparison_report.json` / `baseline_results.json` / `rag_results.json` — raw stage output",
            "- `config.yaml` — config snapshot",
            "",
        ]
    )
    dest.write_text("\n".join(lines), encoding="utf-8")


_LATEST_README_INTRO = """<!-- Generated by the pipeline: edits here are overwritten. -->
# Latest results — {title}

Copied from [`results/runs/{source}/`]({source_link}), which is the permanent home of
this export. Anything in `results/latest/` is replaced by the next run.

{files}
---

"""


# results/latest/ is a bind mount onto the host, so anything copied here is written
# to the host disk for real. Two invariants keep that bounded, and both are enforced
# below rather than trusted: the source is one export folder that does not contain
# latest_dir, and only flat text artifacts are copied — never a subtree, a cache, or
# model weights. Copying a parent of latest_dir once recursed six levels deep and
# wrote ~100GB of duplicated Hugging Face cache to the host.
SNAPSHOT_SUFFIXES = frozenset({".csv", ".json", ".jsonl", ".md", ".txt", ".yaml", ".yml"})
SNAPSHOT_MAX_BYTES = 64 * 1024 * 1024
# Per-file size alone bounds nothing: a run folder of many just-under-cap files still
# lands on the host disk. The total is what the host actually pays.
#
# It bounds the artifacts *copied from the source*, not the total bytes written: the
# README refresh_latest generates afterwards embeds summary.md's body and is not
# counted, so the directory can exceed this by roughly one summary. That is deliberate
# — the README is the point of the folder, and dropping it to satisfy an accounting
# rule would be the wrong trade. The number is a bound on what a runaway source can
# push onto the host, not a promise about the directory's final size.
SNAPSHOT_MAX_TOTAL_BYTES = 256 * 1024 * 1024
# The half-written files _replace_artifact renames into place. A crash between mkstemp
# and the rename leaves one behind, so the clear step removes them: they are this
# function's own litter, and telling a human to delete them by hand would be reporting
# our mess as theirs.
SNAPSHOT_TEMP_PREFIX = ".snapshot-"

# The files the snapshot README links, and why each is worth opening.
SNAPSHOT_HIGHLIGHTS = {
    "by_question.md": "every question, side by side across approaches",
    "cpu_vs_cuda.json": "aggregate CPU vs GPU deltas, machine readable",
    "evaluation_metrics.csv": "one row per question, straight from Postgres",
    "manifest.json": "what ran, on which hardware",
    "by_question_throughput.csv": "tokens/sec per question × approach × device",
    "by_question_latency.csv": "time_to_response per question × approach × device",
}

# What the aggregate cap must keep when it cannot keep everything. Alphabetical order
# sheds manifest.json before by_question*.json, which costs the snapshot its run
# identity — which run, on which hardware — while keeping bulk per-question data that
# is then unattributable. Identity and the human summary come first, then the files
# the README links, then everything else.
SNAPSHOT_PRIORITY = ("manifest.json", "summary.md") + tuple(
    name for name in SNAPSHOT_HIGHLIGHTS if name != "manifest.json"
)


def _snapshot_order(source_dir: Path) -> list[Path]:
    """`source_dir` entries, most worth keeping first, then the rest alphabetically."""
    remaining = {entry.name: entry for entry in sorted(source_dir.iterdir())}
    ordered = [remaining.pop(name) for name in SNAPSHOT_PRIORITY if name in remaining]
    return ordered + list(remaining.values())


def _atomic_write(dest: Path, fill) -> None:
    """
    Put bytes at `dest` without any step following a symlink that may sit there.

    `fill(out)` writes to a descriptor mkstemp opened on a file it created
    exclusively; the path is never reopened by name, so a link appearing at it
    afterwards has nothing left to redirect. Permissions and timestamps are set on
    that same descriptor rather than through `shutil.copystat`, which takes a path
    and would follow such a link.

    One window remains, between closing the descriptor and `os.replace`: a link
    swapped in there is installed at `dest` by the rename — `os.replace` does not
    follow symlinks — orphaning the bytes just written. Nothing follows that link:
    the next refresh's clear loop removes it before anything reads or writes it. It
    costs one stale snapshot, not a write outside results/latest, so it is left.
    """
    fd, tmp_name = tempfile.mkstemp(dir=dest.parent, prefix=SNAPSHOT_TEMP_PREFIX)
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as out:
            fill(out)
        os.replace(tmp, dest)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


def _replace_artifact(src: Path, dest: Path) -> None:
    """Copy `src` onto `dest`, carrying its mode and mtime, following no symlink."""
    info = src.stat()

    def fill(out):
        with open(src, "rb") as reader:
            shutil.copyfileobj(reader, out)
        os.fchmod(out.fileno(), stat.S_IMODE(info.st_mode))
        if os.utime in os.supports_fd:
            os.utime(out.fileno(), ns=(info.st_atime_ns, info.st_mtime_ns))

    _atomic_write(dest, fill)


def _write_snapshot_text(dest: Path, text: str) -> None:
    """Write generated text (the README) as safely as a copied artifact."""
    _atomic_write(dest, lambda out: out.write(text.encode("utf-8")))


def _report_snapshot_residue(latest_dir: Path) -> None:
    """
    Name whatever the clear step deliberately left behind.

    Leaving unrelated files is the policy — it is what stops a mistargeted destination
    from being destroyed. Leaving them *silently* is the problem: a directory here is
    skipped by every step of a refresh, and a results/latest/results/ left by the old
    recursive copy then aborts the pipeline at startup with nothing saying that the
    export will not clear it either. Only a human deleting it resolves that state.
    """
    residue = sorted(
        f"{entry.name}/" if entry.is_dir() else entry.name
        for entry in latest_dir.iterdir()
        if entry.is_dir() or entry.suffix.lower() not in SNAPSHOT_SUFFIXES
    )
    if residue:
        logger.warning(
            "Snapshot left %d unrelated entries in %s (refresh does not remove these; "
            "delete them by hand if they are stale): %s",
            len(residue),
            latest_dir,
            ", ".join(residue),
        )


def _snapshot_artifacts(source_dir: Path) -> list[Path]:
    """Files in `source_dir` eligible for results/latest/ — flat, small, text."""
    keep: list[Path] = []
    skipped: list[str] = []
    total = 0
    for entry in _snapshot_order(source_dir):
        if not entry.is_file() or entry.is_symlink():
            skipped.append(f"{entry.name} (not a regular file)")
            continue
        if entry.suffix.lower() not in SNAPSHOT_SUFFIXES:
            skipped.append(f"{entry.name} ({entry.suffix or 'no suffix'} is not an artifact type)")
            continue
        size = entry.stat().st_size
        if size > SNAPSHOT_MAX_BYTES:
            skipped.append(f"{entry.name} ({size} bytes, over the {SNAPSHOT_MAX_BYTES} per-file cap)")
            continue
        if total + size > SNAPSHOT_MAX_TOTAL_BYTES:
            skipped.append(
                f"{entry.name} ({size} bytes would pass the {SNAPSHOT_MAX_TOTAL_BYTES} total cap)"
            )
            continue
        total += size
        keep.append(entry)
    if skipped:
        logger.warning(
            "Snapshot of %s kept %d files (%d bytes) and skipped %d: %s",
            source_dir,
            len(keep),
            total,
            len(skipped),
            "; ".join(skipped),
        )
    return keep


def refresh_latest(source_dir: Path, latest_dir: Path | None = None) -> Path:
    """
    Replace results/latest/ with the artifacts of `source_dir`, led by a README.

    The README is the folder's summary rather than a pointer to one, so it is what
    GitHub and most file browsers show first, and it names the run it came from.
    """
    source_dir = Path(source_dir)
    latest_dir = Path(latest_dir or LATEST_DIR)

    if not source_dir.is_dir():
        raise NotADirectoryError(f"Snapshot source is not a directory: {source_dir}")
    source_resolved = source_dir.resolve()
    latest_resolved = latest_dir.resolve()

    # The destination is the one directory this function owns. Checking its shape
    # first means transposed arguments — refresh_latest(run_dir, repo_root) — are
    # rejected before anything is deleted, rather than clearing the repo.
    #
    # Deliberately name-based, not anchored to RESULTS_DIR: that constant is
    # REPO_ROOT/results with REPO_ROOT defaulting to /app, while 08_compare_devices
    # and 09_compare_runtimes both accept --repo-root and every test builds its tree
    # under tmp_path. Anchoring would reject those legitimate callers and force a
    # test-only escape hatch, which is worse than the narrow exposure it closes: any
    # */results/latest passes, but a destination named neither cannot.
    if latest_resolved.name != "latest" or latest_resolved.parent.name != "results":
        raise ValueError(
            f"Refusing to snapshot into {latest_dir}: the destination must be a "
            "results/latest/ directory. Check the argument order — the source "
            "folder comes first."
        )
    if latest_resolved == source_resolved or latest_resolved.is_relative_to(source_resolved):
        raise ValueError(
            f"Refusing to snapshot {source_dir} into {latest_dir}: the destination is "
            "inside the source, which copies the tree into itself. Pass the single "
            "export folder (results/runs/<run_id>/), not a parent of it."
        )
    if source_resolved.is_relative_to(latest_resolved):
        raise ValueError(
            f"Refusing to snapshot {source_dir} into {latest_dir}: the source is inside "
            "the destination, so clearing the destination would delete the source first."
        )

    artifacts = _snapshot_artifacts(source_dir)
    # Clear by unlinking the artifact types this function writes, never by removing
    # the directory: a mistargeted destination that slipped past the checks above
    # then loses at most files of those types instead of its whole tree. README.md
    # is covered by `.md`.
    #
    # Symlinks go unconditionally, whatever they point at or are named. results/ is a
    # container-writable bind mount, so a link planted there is a write outside
    # results/ waiting for the next snapshot to follow it — copying onto a symlinked
    # destination writes through to its target.
    latest_dir.mkdir(parents=True, exist_ok=True)
    for stale in latest_dir.iterdir():
        if stale.is_symlink():
            logger.warning("Snapshot removes symlink %s -> %s", stale, os.readlink(stale))
            stale.unlink()
        elif stale.is_file() and (
            stale.suffix.lower() in SNAPSHOT_SUFFIXES
            or stale.name.startswith(SNAPSHOT_TEMP_PREFIX)
        ):
            stale.unlink()

    _report_snapshot_residue(latest_dir)

    for artifact in artifacts:
        _replace_artifact(artifact, latest_dir / artifact.name)

    # A link here is never legitimate — the clear loop says so — and read_text would
    # follow it, folding a host file's contents into the README this writes. Treat it
    # as absent, exactly as if the source had no summary.
    summary = latest_dir / "summary.md"
    if summary.is_symlink():
        logger.warning("Snapshot ignores symlinked summary.md -> %s", os.readlink(summary))
        summary.unlink()
        body = ""
    else:
        body = summary.read_text(encoding="utf-8") if summary.is_file() else ""
    # summary.md's own H1 would collide with the README's, and keeping both files
    # would leave two copies of the same text to drift apart.
    body = "\n".join(line for line in body.splitlines() if not line.startswith("# "))
    summary.unlink(missing_ok=True)

    listed = [
        f"- [`{name}`](./{name}) — {why}"
        for name, why in SNAPSHOT_HIGHLIGHTS.items()
        if (latest_dir / name).is_file()
    ]
    files = "**In this folder**\n\n" + "\n".join(listed) + "\n\n" if listed else ""

    # write_text follows a symlink planted here after the clear loop ran, which is an
    # arbitrary host write. The one file written on every refresh takes the safest
    # path, not the least safe one.
    _write_snapshot_text(
        latest_dir / "README.md",
        _LATEST_README_INTRO.format(
            title=source_dir.name,
            source=source_dir.name,
            source_link=f"../runs/{source_dir.name}/",
            files=files,
        )
        + body.lstrip("\n"),
    )
    return latest_dir


def _run_scope(run_id: str) -> tuple[str | None, datetime | None]:
    """
    Device and start time encoded in a pipeline run id, e.g. ``2026-08-14_032911_cpu``.

    src.run_id owns the shape: a suffix test here once read ``..._cpu_vs_cuda`` as a
    CUDA run and stamped a comparison export with GPU hardware.
    """
    return parse_run_id(run_id)


def _hardware_for_run(hardware: HardwareInfo, device: str | None) -> dict[str, Any]:
    """
    Machine facts, corrected to the device the run actually used.

    The export can run in a process that still sees the GPU — that is how a CPU run
    came to report an RTX 4080 as its device — so the run id wins over detection.
    """
    params = hardware.as_params()
    if not device or device == hardware.device:
        return params
    params["device"] = device
    if device == "cpu":
        params.update(
            cuda_available=False,
            cuda_device_count=0,
            cuda_device_name="none",
            cuda_capability="none",
        )
    return params


def _stamp_copied_json(run_dir: Path, hardware: dict[str, Any]) -> dict[str, Any]:
    """
    Put this run's hardware on copied stage JSON, and collect any load-time
    resource snapshot those files already carry.

    Stage JSON written before HardwareInfo recorded cpu_model still says the
    export process's GPU was the device. Overwriting the top-level hardware
    object is cheap and stops a CPU folder from advertising an RTX 4080.
    """
    resources: dict[str, Any] = {}
    for name in PROCESSED_ARTIFACTS:
        path = run_dir / name
        if path.suffix != ".json" or not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            continue
        if not isinstance(data, dict):
            continue
        data["hardware"] = hardware
        found = data.get("resources")
        if isinstance(found, dict) and found:
            resources = found
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return resources


def export_run(
    run_id: str | None = None,
    repo_root: str | Path | None = None,
    processed_dir: str | Path | None = None,
    config_path: str | Path | None = None,
) -> Path:
    """
    Copy processed artifacts + Postgres metrics into results/runs/<run_id>/
    and refresh results/latest/.
    """
    repo_root = Path(repo_root or REPO_ROOT)
    processed_dir = Path(processed_dir or repo_root / "data" / "processed")
    config_path = Path(config_path or repo_root / "config" / "config.yaml")
    runs_dir = repo_root / "results" / "runs"
    latest_dir = repo_root / "results" / "latest"

    if run_id is None:
        run_id = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")

    run_device, run_started = _run_scope(run_id)
    hardware = detect_hardware()
    run_dir = runs_dir / run_id
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)

    # Copy processed artifacts, preferring this run's device-tagged snapshot. The
    # pipeline writes both baseline_results_cpu.json and baseline_results.json, and
    # the untagged one belongs to whichever device ran last — so exporting a CPU run
    # from the untagged copy silently fills the folder with the GPU's answers.
    copied = []
    for name in PROCESSED_ARTIFACTS:
        src = processed_dir / name
        if run_device:
            tagged = processed_dir / f"{Path(name).stem}_{run_device}{Path(name).suffix}"
            if tagged.is_file():
                src = tagged
        if src.is_file():
            shutil.copy2(src, run_dir / name)
            copied.append(name)

    hw_params = _hardware_for_run(hardware, run_device)
    resources = _stamp_copied_json(run_dir, hw_params)

    # Config + prompts snapshot
    if config_path.is_file():
        shutil.copy2(config_path, run_dir / "config.yaml")
        copied.append("config.yaml")

    prompts_src = repo_root / "prompts" / "evaluation_prompts.txt"
    if prompts_src.is_file():
        shutil.copy2(prompts_src, run_dir / "evaluation_prompts.txt")
        copied.append("evaluation_prompts.txt")

    n_rows = export_metrics_csv(
        run_dir / "evaluation_metrics.csv",
        device=run_device,
        since=run_started,
        fill={
            "cpu_threads": hw_params.get("cpu_threads"),
            "cpu_logical": hw_params.get("cpu_logical"),
        },
    )
    if n_rows:
        copied.append("evaluation_metrics.csv")

    llm_model = "unknown"
    if config_path.is_file():
        cfg = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        llm_model = cfg.get("llm", {}).get("model", "unknown")

    comparison: dict[str, dict[str, float]] | None = None
    comp_path = run_dir / "comparison_report.json"
    if comp_path.is_file():
        comp = json.loads(comp_path.read_text(encoding="utf-8"))
        comparison = dict(comp.get("comparison_summary", {}))

    # Step 4 writes rag_results.json separately — merge into comparison table
    rag_path = run_dir / "rag_results.json"
    if rag_path.is_file():
        rag_data = json.loads(rag_path.read_text(encoding="utf-8"))
        if comparison is None:
            comparison = {}
        comparison["rag"] = rag_data.get("aggregate", {})

    manifest = {
        "run_id": run_id,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "hardware": hw_params,
        "resources": resources,
        "llm_model": llm_model,
        "artifacts_copied": copied,
        "postgres_rows": n_rows,
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    _write_summary_md(run_dir / "summary.md", manifest, comparison)

    # Question-centric view for this single-device export (columns = approaches)
    try:
        from src.question_view import build_question_view

        build_question_view(
            out_dir=run_dir,
            processed_dir=processed_dir,
            prefer_postgres=True,
        )
        copied.append("by_question.md")
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not build by_question view: %s", exc)

    refresh_latest(run_dir, latest_dir)

    logger.info("Exported run to %s (%d artifacts)", run_dir, len(copied))
    return run_dir
