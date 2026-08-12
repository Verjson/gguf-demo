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

from src.hardware import HardwareInfo, detect_hardware

logger = logging.getLogger(__name__)

REPO_ROOT = Path(os.environ.get("REPO_ROOT", "/app"))
RESULTS_DIR = REPO_ROOT / "results"
RUNS_DIR = RESULTS_DIR / "runs"
LATEST_DIR = RESULTS_DIR / "latest"

PROCESSED_ARTIFACTS = (
    "comparison_report.json",
    "baseline_results.json",
    "rag_results.json",
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


def export_metrics_csv(dest: Path) -> int:
    """Dump evaluation_metrics table to CSV; return row count."""
    sql = """
        SELECT timestamp, approach, device, cuda_available, model_name, question,
               rouge1, rouge2, "rougeL", bert_score, retrieval_hit_at_k, faithfulness,
               context_utilization, answer_relevancy, judge_groundedness, quality_score,
               generation_time, retrieval_time, time_to_response, speed_chars_per_sec,
               cuda_used, domain_relevance, coherence
        FROM evaluation_metrics
        ORDER BY timestamp DESC
    """
    rows: list[tuple] = []
    try:
        with psycopg2.connect(**_postgres_conn_kwargs()) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not export Postgres metrics: %s", exc)
        return 0

    with dest.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(METRICS_COLUMNS)
        for row in rows:
            writer.writerow(row)
    return len(rows)


def _improvement_table(comparison: dict[str, dict[str, float]]) -> str:
    """Markdown table: baseline vs rag vs fine_tuned vs fine_tuned_with_rag."""
    approaches = list(comparison.keys())
    if not approaches:
        return "_No comparison data._\n"

    # Key metrics to highlight
    highlight = [
        "rougeL",
        "bert_score",
        "retrieval_hit_at_k",
        "faithfulness",
        "quality_score",
        "generation_time",
        "cuda_used",
    ]
    all_keys = set()
    for m in comparison.values():
        all_keys.update(m.keys())
    metrics = [k for k in highlight if k in all_keys]
    metrics += sorted(k for k in all_keys if k not in metrics)

    lines = ["| Metric | " + " | ".join(approaches) + " |", "|" + "---|" * (len(approaches) + 1)]
    baseline = comparison.get("baseline", {})
    for metric in metrics:
        cells = []
        for approach in approaches:
            val = comparison[approach].get(metric)
            cells.append(f"{val:.4f}" if val is not None else "—")
        lines.append(f"| {metric} | " + " | ".join(cells) + " |")

    # Add improvement row for quality_score vs baseline
    if "baseline" in comparison and "rag" in comparison:
        b = comparison["baseline"].get("quality_score", 0)
        r = comparison["rag"].get("quality_score", 0)
        if b:
            pct = (r - b) / b * 100
            lines.append(f"\n**RAG quality_score vs baseline:** {pct:+.1f}%")

    if "baseline" in comparison and "fine_tuned_with_rag" in comparison:
        b = comparison["baseline"].get("quality_score", 0)
        f = comparison["fine_tuned_with_rag"].get("quality_score", 0)
        if b:
            pct = (f - b) / b * 100
            lines.append(f"\n**Fine-tuned+RAG quality_score vs baseline:** {pct:+.1f}%")

    return "\n".join(lines) + "\n"


def _write_summary_md(
    dest: Path,
    manifest: dict[str, Any],
    comparison: dict[str, dict[str, float]] | None,
) -> None:
    hw = manifest.get("hardware", {})
    lines = [
        f"# Run summary — {manifest['run_id']}",
        "",
        f"- **Exported:** {manifest['exported_at']}",
        f"- **Device:** {hw.get('device', 'unknown')} (cuda_available={hw.get('cuda_available')})",
        f"- **GPU:** {hw.get('cuda_device_name', 'n/a')}",
        f"- **Model:** {manifest.get('llm_model', 'n/a')}",
        f"- **Postgres metric rows:** {manifest.get('postgres_rows', 0)}",
        "",
        "## How to read improvements",
        "",
        "Higher is better for quality metrics (ROUGE, BERTScore, faithfulness, quality_score).",
        "Lower is better for `generation_time` (latency).",
        "`retrieval_hit_at_k` shows whether retrieved chunks contain the ground-truth answer.",
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
            "| **RAG** | rougeL, faithfulness, retrieval_hit@k |",
            "| **Fine-tuned** | domain_relevance, answer style |",
            "| **Fine-tuned + RAG** | best combined quality_score |",
            "",
            "## Files in this folder",
            "",
            "- `manifest.json` — run metadata",
            "- `comparison_report.json` — full step-06 output",
            "- `baseline_results.json` / `rag_results.json` — per-stage details",
            "- `evaluation_metrics.csv` — all rows from Postgres",
            "- `config.yaml` — config snapshot",
            "",
        ]
    )
    dest.write_text("\n".join(lines), encoding="utf-8")


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

    hardware = detect_hardware()
    run_dir = runs_dir / run_id
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)

    # Copy processed artifacts
    copied = []
    for name in PROCESSED_ARTIFACTS:
        src = processed_dir / name
        if src.is_file():
            shutil.copy2(src, run_dir / name)
            copied.append(name)

    # Config + prompts snapshot
    if config_path.is_file():
        shutil.copy2(config_path, run_dir / "config.yaml")
        copied.append("config.yaml")

    prompts_src = repo_root / "prompts" / "evaluation_prompts.txt"
    if prompts_src.is_file():
        shutil.copy2(prompts_src, run_dir / "evaluation_prompts.txt")
        copied.append("evaluation_prompts.txt")

    # Postgres CSV
    n_rows = export_metrics_csv(run_dir / "evaluation_metrics.csv")
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
        "hardware": hardware.as_params(),
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

    # Refresh results/latest/
    if latest_dir.exists():
        shutil.rmtree(latest_dir)
    shutil.copytree(run_dir, latest_dir)

    logger.info("Exported run to %s (%d artifacts)", run_dir, len(copied))
    return run_dir
