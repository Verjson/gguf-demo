"""
Question-centric visualization of evaluation results.

Instead of one row per (question × approach × device) for storage, present
results as: each question, then columns for baseline/CPU, baseline/GPU, RAG/CPU, etc.
"""

from __future__ import annotations

import csv
import json
import logging
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psycopg2

from src.display_metrics import QUESTION_DISPLAY
from src.score_colors import (
    format_ranked_cell,
    html_table,
    lower_is_better,
    rank_scores,
)

logger = logging.getLogger(__name__)

# Preferred column order for the pivot
APPROACH_ORDER = (
    "baseline",
    "baseline_gguf",
    "rag",
    "rag_gguf",
    "fine_tuned",
    "fine_tuned_with_rag",
    "baseline_comparison",
)
DEVICE_ORDER = ("cpu", "cuda")

# Metrics shown in the compact table (full metrics stay in JSON)
DISPLAY_METRICS = QUESTION_DISPLAY


def _postgres_conn_kwargs() -> dict[str, str]:
    return {
        "host": os.getenv("POSTGRES_HOST", "postgres"),
        "database": os.getenv("POSTGRES_DB", "rag_eval"),
        "user": os.getenv("POSTGRES_USER", "raguser"),
        "password": os.getenv("POSTGRES_PASSWORD", "ragpass"),
    }


def fetch_latest_cells_from_postgres() -> list[dict[str, Any]]:
    """
    One row per (question, approach, device) — latest timestamp wins.
    Returns flat cells ready to pivot.
    """
    sql = """
        SELECT DISTINCT ON (question, approach, COALESCE(device, 'unknown'))
            question,
            approach,
            COALESCE(device, 'unknown') AS device,
            response,
            quality_score,
            rouge1, rouge2, "rougeL",
            bert_score,
            retrieval_hit_at_k,
            faithfulness,
            context_utilization,
            answer_relevancy,
            judge_groundedness,
            generation_time,
            retrieval_time,
            time_to_response,
            tokens_per_sec,
            speed_chars_per_sec,
            cuda_used,
            domain_relevance,
            coherence,
            timestamp
        FROM evaluation_metrics
        WHERE question IS NOT NULL AND approach IS NOT NULL
        ORDER BY question, approach, COALESCE(device, 'unknown'), timestamp DESC
    """
    try:
        with psycopg2.connect(**_postgres_conn_kwargs()) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                cols = [d[0] for d in cur.description]
                return [dict(zip(cols, row)) for row in cur.fetchall()]
    except Exception as exc:  # noqa: BLE001
        logger.warning("Postgres pivot query failed: %s", exc)
        return []


def _cell_key(row: dict[str, Any]) -> tuple[str, str, str]:
    q = (row.get("question") or "").strip()
    approach = row.get("approach") or "unknown"
    device = (row.get("device") or "unknown").lower()
    if device in {"gpu", "cuda"}:
        device = "cuda"
    return (q, approach, device)


def merge_cells(
    primary: list[dict[str, Any]],
    fallback: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Prefer Postgres/primary rows; fill missing (question, approach, device) from JSON.
    Also overlay latency fields from fallback when primary is missing them.
    """
    by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in primary:
        key = _cell_key(row)
        if key[0]:
            by_key[key] = dict(row)

    latency_keys = (
        "generation_time",
        "retrieval_time",
        "time_to_response",
        "tokens_per_sec",
        "speed_chars_per_sec",
    )
    for row in fallback:
        key = _cell_key(row)
        if not key[0]:
            continue
        if key not in by_key:
            by_key[key] = dict(row)
            continue
        existing = by_key[key]
        for lk in latency_keys:
            if existing.get(lk) is None and row.get(lk) is not None:
                existing[lk] = row[lk]
        for metric in ("quality_score", "rougeL", "bert_score", "faithfulness", "retrieval_hit_at_k"):
            if existing.get(metric) is None and row.get(metric) is not None:
                existing[metric] = row[metric]

    return list(by_key.values())


def cells_from_stage_json(
    processed_or_run_dir: Path,
    device: str,
) -> list[dict[str, Any]]:
    """Load per-question rows from baseline/rag/comparison JSON for one device."""
    cells: list[dict[str, Any]] = []

    mapping = [
        ("baseline_results.json", "baseline"),
        ("baseline_gguf_results.json", "baseline_gguf"),
        ("rag_results.json", "rag"),
        ("rag_gguf_results.json", "rag_gguf"),
        (f"baseline_results_{device}.json", "baseline"),
        (f"baseline_gguf_results_{device}.json", "baseline_gguf"),
        (f"rag_results_{device}.json", "rag"),
        (f"rag_gguf_results_{device}.json", "rag_gguf"),
    ]
    seen_files: set[str] = set()

    for filename, approach in mapping:
        path = processed_or_run_dir / filename
        if not path.is_file() or str(path) in seen_files:
            continue
        seen_files.add(str(path))
        data = json.loads(path.read_text(encoding="utf-8"))
        for item in data.get("results", []):
            metrics = item.get("metrics", {})
            cells.append(
                {
                    "question": item.get("question", ""),
                    "approach": approach,
                    "device": device,
                    "response": item.get("response", ""),
                    **metrics,
                }
            )

    comp = processed_or_run_dir / "comparison_report.json"
    alt = processed_or_run_dir / f"comparison_report_{device}.json"
    for path in (comp, alt):
        if not path.is_file():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        detailed = data.get("detailed_results", {})
        for approach, items in detailed.items():
            for item in items:
                metrics = item.get("metrics", {})
                cells.append(
                    {
                        "question": item.get("question", ""),
                        "approach": approach,
                        "device": device,
                        "response": item.get("response", ""),
                        **metrics,
                    }
                )
    return cells


def _normalize_latency(metrics: dict[str, float]) -> dict[str, float]:
    """Ensure time_to_response exists even for older rows that only have generation_time."""
    if "time_to_response" not in metrics:
        gen = float(metrics.get("generation_time") or 0.0)
        ret = float(metrics.get("retrieval_time") or 0.0)
        metrics["time_to_response"] = gen + ret
    return metrics


def pivot_by_question(cells: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Build:
      {
        "columns": ["baseline|cpu", "baseline|cuda", ...],
        "questions": [
          {
            "question": "...",
            "cells": {
              "baseline|cpu": {"metrics": {...}, "response": "..."},
              ...
            }
          }
        ]
      }
    """
    by_q: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    column_keys: set[str] = set()

    for row in cells:
        q = (row.get("question") or "").strip()
        if not q:
            continue
        approach = row.get("approach") or "unknown"
        device = (row.get("device") or "unknown").lower()
        if device in {"gpu", "cuda"}:
            device = "cuda"
        key = f"{approach}|{device}"
        # Keep demo approaches only (drop ad-hoc smoke / verify rows from Postgres).
        if (
            approach not in APPROACH_ORDER
            and not approach.startswith("fine_tuned")
            and not approach.endswith("_gguf")
        ):
            continue
        column_keys.add(key)

        metrics = {
            k: float(v)
            for k, v in row.items()
            if k
            not in {
                "question",
                "approach",
                "device",
                "response",
                "timestamp",
                "model_name",
                "cuda_available",
            }
            and isinstance(v, (int, float))
            and v is not None
        }
        metrics = _normalize_latency(metrics)
        by_q[q][key] = {
            "metrics": metrics,
            "response": (row.get("response") or "")[:500],
        }

    def col_sort(key: str) -> tuple:
        approach, _, device = key.partition("|")
        a_idx = APPROACH_ORDER.index(approach) if approach in APPROACH_ORDER else 99
        d_idx = DEVICE_ORDER.index(device) if device in DEVICE_ORDER else 99
        return (a_idx, d_idx, key)

    columns = sorted(column_keys, key=col_sort)
    questions = [
        {"question": q, "cells": by_q[q]}
        for q in sorted(by_q.keys())
    ]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "columns": columns,
        "questions": questions,
    }


def _fmt(val: Any, *, precision: int = 3) -> str:
    if val is None:
        return "—"
    if isinstance(val, float):
        return f"{val:.{precision}f}"
    return str(val)


def _overview_table(pivot: dict[str, Any], metric: str) -> list[str]:
    columns: list[str] = pivot.get("columns", [])
    header = ["Question", *[f"<code>{c}</code>" for c in columns]]
    rows: list[list[Any]] = []
    for item in pivot.get("questions", []):
        q = item["question"]
        q_short = q if len(q) <= 60 else q[:57] + "..."
        values = []
        for col in columns:
            metrics = item["cells"].get(col, {}).get("metrics", {})
            raw = metrics.get(metric)
            values.append(float(raw) if isinstance(raw, (int, float)) else None)
        ranks = rank_scores(values, lower_is_better=lower_is_better(metric))
        row: list[Any] = [q_short]
        for val, rank in zip(values, ranks):
            row.append(format_ranked_cell(val, rank, precision=3, html=True))
        rows.append(row)
    return [
        html_table(header, rows, metric_col=0).rstrip(),
        "",
    ]


def _speedup_lines_for_question(item: dict[str, Any], columns: list[str]) -> list[str]:
    """Per-question CPU→GPU speedup on time_to_response for each approach."""
    lines: list[str] = []
    approaches = sorted(
        {
            c.partition("|")[0]
            for c in columns
            if c.endswith("|cpu") or c.endswith("|cuda")
        }
    )
    for approach in approaches:
        cpu = item["cells"].get(f"{approach}|cpu", {}).get("metrics", {})
        gpu = item["cells"].get(f"{approach}|cuda", {}).get("metrics", {})
        cpu_t = cpu.get("time_to_response", cpu.get("generation_time"))
        gpu_t = gpu.get("time_to_response", gpu.get("generation_time"))
        if cpu_t is None or gpu_t is None or gpu_t <= 0:
            continue
        factor = cpu_t / gpu_t
        lines.append(
            f"- **{approach}:** {cpu_t:.2f}s (CPU) → {gpu_t:.2f}s (GPU) = "
            f"**{factor:.1f}×** faster time-to-response"
        )
    return lines


def render_by_question_markdown(pivot: dict[str, Any], primary_metric: str = "rougeL") -> str:
    """Human-friendly view: one section per question, table of approach×device."""
    columns: list[str] = pivot.get("columns", [])
    lines = [
        "# Results by question",
        "",
        "Each question shows quality **and** latency across approach × device.",
        "",
        "- **rougeL:** overlap with the ground-truth answer — **higher is better** (the RAG quality story)",
        "- **Time to response:** retrieval + generation (seconds) — **lower is better** (the device story)",
        "- **tokens_per_sec:** decode throughput — **higher is better**",
        "- **Colors:** 🟢 best · 🟡 mid · 🔴 worst within each row; ties within noise are left uncolored",
        "",
        f"_Generated: {pivot.get('generated_at', '')}_",
        "",
        "## Overview — overlap with ground truth (`rougeL`)",
        "",
    ]
    lines.extend(_overview_table(pivot, "rougeL"))
    lines.extend(["", "## Overview — time to response (seconds, lower is better)", ""])
    lines.extend(_overview_table(pivot, "time_to_response"))
    lines.extend(["", "## Overview — throughput (`tokens_per_sec`, higher is better)", ""])
    lines.extend(_overview_table(pivot, "tokens_per_sec"))
    lines.extend(["", "---", ""])

    for i, item in enumerate(pivot.get("questions", []), 1):
        q = item["question"]
        lines.append(f"## Q{i}. {q}")
        lines.append("")

        # Rank each metric column across approaches (row = approach×device).
        header = ["Approach × Device", *DISPLAY_METRICS]
        detail_rows: list[list[Any]] = []
        # Collect values per metric for ranking across columns present
        col_present = [col for col in columns if item["cells"].get(col)]
        metric_values: dict[str, list[float | None]] = {m: [] for m in DISPLAY_METRICS}
        for col in col_present:
            metrics = item["cells"][col].get("metrics", {})
            for m in DISPLAY_METRICS:
                raw = metrics.get(m)
                metric_values[m].append(
                    float(raw) if isinstance(raw, (int, float)) else None
                )
        metric_ranks = {
            m: rank_scores(vals, lower_is_better=lower_is_better(m))
            for m, vals in metric_values.items()
        }

        for row_i, col in enumerate(col_present):
            metrics = item["cells"][col].get("metrics", {})
            row: list[Any] = [f"<code>{col}</code>"]
            for m in DISPLAY_METRICS:
                raw = metrics.get(m)
                val = float(raw) if isinstance(raw, (int, float)) else None
                rank = metric_ranks[m][row_i]
                row.append(format_ranked_cell(val, rank, precision=3, html=True))
            detail_rows.append(row)

        lines.append(html_table(header, detail_rows, metric_col=0).rstrip())
        lines.append("")

        speedups = _speedup_lines_for_question(item, columns)
        if speedups:
            lines.append("**CPU → GPU speedup (time_to_response):**")
            lines.extend(speedups)
            lines.append("")

        lines.append("<details><summary>Sample answers</summary>")
        lines.append("")
        for col in columns:
            cell = item["cells"].get(col)
            if not cell or not cell.get("response"):
                continue
            resp = cell["response"].replace("\n", " ").strip()
            if len(resp) > 280:
                resp = resp[:277] + "..."
            lines.append(f"- **`{col}`:** {resp}")
        lines.append("")
        lines.append("</details>")
        lines.append("")

    return "\n".join(lines)


def write_by_question_csv(pivot: dict[str, Any], dest: Path, metric: str = "quality_score") -> None:
    """Flat CSV: one row per question, columns = approach|device for one metric."""
    columns: list[str] = pivot.get("columns", [])
    with dest.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["question", *columns])
        for item in pivot.get("questions", []):
            row = [item["question"]]
            for col in columns:
                cell = item["cells"].get(col, {})
                val = cell.get("metrics", {}).get(metric)
                row.append("" if val is None else f"{val:.6f}")
            writer.writerow(row)


def build_question_view(
    out_dir: Path,
    cpu_run_dir: Path | None = None,
    cuda_run_dir: Path | None = None,
    processed_dir: Path | None = None,
    prefer_postgres: bool = True,
) -> dict[str, Any]:
    """
    Assemble pivot from Postgres (preferred) and/or exported run folders.
    Writes by_question.json, by_question.md, by_question_quality.csv into out_dir.
    """
    pg_cells: list[dict[str, Any]] = []
    if prefer_postgres:
        pg_cells = fetch_latest_cells_from_postgres()

    json_cells: list[dict[str, Any]] = []
    if processed_dir:
        for device in DEVICE_ORDER:
            json_cells.extend(cells_from_stage_json(processed_dir, device))
    if cpu_run_dir and cpu_run_dir.is_dir():
        json_cells.extend(cells_from_stage_json(cpu_run_dir, "cpu"))
    if cuda_run_dir and cuda_run_dir.is_dir():
        json_cells.extend(cells_from_stage_json(cuda_run_dir, "cuda"))

    if pg_cells and json_cells:
        cells = merge_cells(pg_cells, json_cells)
    elif pg_cells:
        cells = pg_cells
    else:
        cells = json_cells

    pivot = pivot_by_question(cells)
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "by_question.json").write_text(json.dumps(pivot, indent=2), encoding="utf-8")
    (out_dir / "by_question.md").write_text(
        render_by_question_markdown(pivot), encoding="utf-8"
    )
    write_by_question_csv(pivot, out_dir / "by_question_quality.csv", "rougeL")
    write_by_question_csv(pivot, out_dir / "by_question_latency.csv", "time_to_response")
    write_by_question_csv(pivot, out_dir / "by_question_throughput.csv", "tokens_per_sec")
    write_by_question_csv(pivot, out_dir / "by_question_generation_time.csv", "generation_time")

    logger.info(
        "Question view: %d questions × %d columns → %s",
        len(pivot.get("questions", [])),
        len(pivot.get("columns", [])),
        out_dir,
    )
    return pivot
