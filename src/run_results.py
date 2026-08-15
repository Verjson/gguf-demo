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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psycopg2
import yaml

from src.display_metrics import select_summary_metrics
from src.hardware import HardwareInfo, detect_hardware
from src.run_id import is_safe_run_id, parse_run_id, run_group_for
from src.score_colors import html_table, ranked_metric_row
from src.snapshot import refresh_latest

logger = logging.getLogger(__name__)

REPO_ROOT = Path(os.environ.get("REPO_ROOT", "/app"))
RESULTS_DIR = REPO_ROOT / "results"
RUNS_DIR = RESULTS_DIR / "runs"

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
    "rss_mb",
    "peak_rss_mb",
    "peak_gpu_mem_mb",
    # Layers the engine actually offloaded. 0 on a GGUF row means it ran on the
    # CPU whatever `device` says, which is the fact that decides whether a
    # Transformers-vs-GGUF comparison built from this CSV means anything.
    "n_gpu_layers",
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
    run_id: str | None = None,
    device: str | None = None,
    since: datetime | None = None,
    fill: dict[str, Any] | None = None,
) -> int:
    """
    Dump this run's evaluation_metrics rows to CSV; return the row count.

    ``run_id`` is the scope. It replaces an earlier ``device`` + ``since`` pair, which
    approximated "this run" as "rows for this device written after the run started" —
    close enough most of the time, and wrong whenever anything else wrote a row in the
    window (an ad-hoc ``docker compose exec`` evaluation, an overlapping run). It also
    meant the project carried three different definitions of a run at once: this one,
    the dashboards' ``run_id``, and ``question_view``'s no-filter-at-all. There is now
    one.

    ``device`` and ``since`` remain as a fallback for rows written before ``run_id``
    existed, and are only consulted when no ``run_id`` is given.
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
               cpu_threads, cpu_logical, rss_mb, peak_rss_mb, peak_gpu_mem_mb,
               n_gpu_layers
        FROM evaluation_metrics
    """
    where, params = [], []
    if run_id:
        where.append("run_id = %s")
        params.append(run_id)
    else:
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

    # Checked before the path is built, because the next thing that happens to it is a
    # recursive delete. `--run-id ../../something` would otherwise resolve outside
    # results/runs/ and rmtree it.
    if not is_safe_run_id(run_id):
        raise ValueError(
            f"refusing to export to run id {run_id!r}: expected the pipeline's shape, "
            "e.g. 2026-08-14_181632_cpu (see src/run_id.py)"
        )

    run_device, run_started = _run_scope(run_id)
    hardware = detect_hardware()
    runs_dir.mkdir(parents=True, exist_ok=True)
    run_dir = runs_dir / run_id
    # Belt and braces: even a run id that matches the shape must land inside runs_dir.
    if run_dir.resolve().parent != runs_dir.resolve():
        raise ValueError(f"run directory {run_dir} escapes {runs_dir}")
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
        run_id=run_id,
        device=run_device,
        since=run_started,
        fill={
            "cpu_threads": hw_params.get("cpu_threads"),
            "cpu_logical": hw_params.get("cpu_logical"),
        },
    )
    if n_rows:
        copied.append("evaluation_metrics.csv")
    elif copied:
        # Stage JSON exists but the database has nothing for this run. That is not an
        # empty run, it is a run whose metric writes did not land — and it used to
        # export a header-only CSV, record postgres_rows: 0, and print DONE.
        logger.error(
            "No evaluation_metrics rows for run_id=%s, but %d stage artifact(s) were "
            "exported. The metric writes did not reach Postgres — check the app "
            "container's logs for 'Failed to persist metrics'.",
            run_id,
            len(copied),
        )

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
            # Scope the pivot to this pipeline invocation. Unscoped, it read the whole
            # table and wrote whichever rows happened to be newest — which is how a
            # ..._cpu folder came to contain CUDA columns from a different run.
            run_group=run_group_for(run_id),
        )
        copied.append("by_question.md")
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not build by_question view: %s", exc)

    refresh_latest(run_dir, latest_dir)

    logger.info("Exported run to %s (%d artifacts)", run_dir, len(copied))
    return run_dir
