#!/usr/bin/env python3
"""
Step 8 — Question-centric CPU vs CUDA visualization.

Builds a view where each question is a row/section and columns are:
  baseline|cpu, baseline|cuda, rag|cpu, rag|cuda, fine_tuned|cpu, ...

Outputs (under --out):
  summary.md / README.md  ← start here: speed + quality callouts, then compact tables
  by_question.md          ← every question, side by side
  by_question.json        ← full metrics + answer snippets
  by_question_quality.csv ← wide table of rougeL
  by_question_latency.csv ← wide table of time_to_response
  by_question_throughput.csv ← wide table of tokens_per_sec
  cpu_vs_cuda.json        ← aggregate payloads
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.display_metrics import select_summary_metrics
from src.latency import speedup_factor
from src.mlflow_tracker import optional_mlflow_run
from src.question_view import build_question_view
from src.score_colors import html_table, ranked_metric_row
from src.snapshot import refresh_latest, resolve_results_output


def load_comparison(run_dir: Path) -> dict:
    path = run_dir / "comparison_report.json"
    if not path.is_file():
        summary = {}
        for stage in ("baseline", "rag"):
            stage_path = run_dir / f"{stage}_results.json"
            if stage_path.is_file():
                summary[stage] = json.loads(stage_path.read_text()).get("aggregate", {})
        return {"comparison_summary": summary, "hardware": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def load_manifest(run_dir: Path) -> dict:
    path = run_dir / "manifest.json"
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def _device_line(run_dir: Path, device: str) -> str:
    """One-line description of the hardware a run used, from its manifest."""
    try:
        hw = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))["hardware"]
    except (OSError, ValueError, KeyError):
        return "unknown"
    if device == "cuda":
        return str(hw.get("cuda_device_name") or "unknown")
    return (
        f"{hw.get('cpu_model', 'unknown')} "
        f"({hw.get('cpu_threads', '?')} of {hw.get('cpu_logical', '?')} threads)"
    )


def write_aggregate_summary(
    out_dir: Path,
    cpu_run_id: str,
    cuda_run_id: str,
    cpu_sum: dict,
    cuda_sum: dict,
) -> None:
    approaches = sorted(set(cpu_sum) | set(cuda_sum))
    lines = [
        f"# Aggregate CPU vs CUDA — {cpu_run_id} vs {cuda_run_id}",
        "",
        f"- **Generated:** {datetime.now(timezone.utc).isoformat()}",
        f"- **CPU:** {_device_line(out_dir.parent / cpu_run_id, 'cpu')}",
        f"- **GPU:** {_device_line(out_dir.parent / cuda_run_id, 'cuda')}",
        "- **Per-question breakdown:** [by_question.md](./by_question.md)",
        "",
        "Quality (`rougeL`, `bert_score`, `faithfulness`) should stay within noise across",
        "devices. **Speed is the device story:** lower `time_to_response`, higher `tokens_per_sec`.",
        "",
        "## What changed",
        "",
        "### Speed (CPU → GPU, `time_to_response`)",
        "",
    ]
    for approach in approaches:
        c = cpu_sum.get(approach, {}).get("time_to_response") or cpu_sum.get(approach, {}).get(
            "generation_time"
        )
        g = cuda_sum.get(approach, {}).get("time_to_response") or cuda_sum.get(approach, {}).get(
            "generation_time"
        )
        if c and g and g > 0:
            lines.append(
                f"- **{approach}:** {c:.2f}s → {g:.2f}s (**{c / g:.1f}×** faster on GPU)"
            )
    lines.append("")
    lines.append("### Quality (RAG vs baseline, `rougeL`)")
    lines.append("")
    for device, summary in (("CPU", cpu_sum), ("GPU", cuda_sum)):
        b = summary.get("baseline", {}).get("rougeL")
        r = summary.get("rag", {}).get("rougeL")
        if b and r:
            lines.append(f"- **{device}:** RAG rougeL {b:.4f} → {r:.4f} ({(r - b) / b * 100:+.1f}%)")
    lines.append("")

    for approach in approaches:
        cpu_m = cpu_sum.get(approach, {})
        cuda_m = cuda_sum.get(approach, {})
        paired = {"cpu": cpu_m, "cuda": cuda_m}
        metrics = select_summary_metrics(paired)
        lines.append(f"## Approach: `{approach}`")
        lines.append("")
        rows: list[list[str]] = []
        for key in metrics:
            rows.append(ranked_metric_row(key, [cpu_m.get(key), cuda_m.get(key)], precision=4))
        lines.append(
            html_table(["Metric", "CPU", "CUDA"], rows, metric_col=0).rstrip()
        )
        lines.append("")

    (out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpu-run-id", required=True)
    parser.add_argument("--cuda-run-id", required=True)
    parser.add_argument("--out", required=True, help="Output folder under repo root")
    parser.add_argument("--repo-root", default=os.environ.get("REPO_ROOT", "/app"))
    args = parser.parse_args()

    root = Path(args.repo_root)
    cpu_dir = root / "results" / "runs" / args.cpu_run_id
    cuda_dir = root / "results" / "runs" / args.cuda_run_id
    out_dir = resolve_results_output(root, args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not cpu_dir.is_dir():
        raise SystemExit(f"CPU run not found: {cpu_dir}")
    if not cuda_dir.is_dir():
        raise SystemExit(f"CUDA run not found: {cuda_dir}")

    # Prefer run-folder JSON when both device dirs are provided (avoids mixing old DB rows)
    prefer_pg = not (cpu_dir and cuda_dir)
    pivot = build_question_view(
        out_dir=out_dir,
        cpu_run_dir=cpu_dir,
        cuda_run_dir=cuda_dir,
        processed_dir=root / "data" / "processed",
        prefer_postgres=prefer_pg,
    )

    cpu = load_comparison(cpu_dir)
    cuda = load_comparison(cuda_dir)
    cpu_sum = dict(cpu.get("comparison_summary", {}))
    cuda_sum = dict(cuda.get("comparison_summary", {}))

    for folder, summary, device in (
        (cpu_dir, cpu_sum, "cpu"),
        (cuda_dir, cuda_sum, "cuda"),
    ):
        for stage in ("baseline", "rag"):
            if stage not in summary:
                p = folder / f"{stage}_results.json"
                if p.is_file():
                    summary[stage] = json.loads(p.read_text()).get("aggregate", {})

    write_aggregate_summary(out_dir, args.cpu_run_id, args.cuda_run_id, cpu_sum, cuda_sum)

    payload = {
        "cpu_run_id": args.cpu_run_id,
        "cuda_run_id": args.cuda_run_id,
        "cpu": cpu_sum,
        "cuda": cuda_sum,
        "cpu_manifest": load_manifest(cpu_dir),
        "cuda_manifest": load_manifest(cuda_dir),
        "n_questions": len(pivot.get("questions", [])),
        "columns": pivot.get("columns", []),
    }
    (out_dir / "cpu_vs_cuda.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    import mlflow

    with optional_mlflow_run("cpu_vs_cuda_compare") as run:
        if run:
            mlflow.set_tag("stage", "compare_devices")
            mlflow.log_params(
                {
                    "cpu_run_id": args.cpu_run_id,
                    "cuda_run_id": args.cuda_run_id,
                    "n_questions": len(pivot.get("questions", [])),
                }
            )
            for approach in sorted(set(cpu_sum) | set(cuda_sum)):
                cpu_ttr = cpu_sum.get(approach, {}).get("time_to_response") or cpu_sum.get(
                    approach, {}
                ).get("generation_time")
                cuda_ttr = cuda_sum.get(approach, {}).get("time_to_response") or cuda_sum.get(
                    approach, {}
                ).get("generation_time")
                factor = speedup_factor(cpu_ttr, cuda_ttr)
                if cpu_ttr is not None:
                    mlflow.log_metric(f"{approach}_cpu_time_to_response", float(cpu_ttr))
                if cuda_ttr is not None:
                    mlflow.log_metric(f"{approach}_cuda_time_to_response", float(cuda_ttr))
                if factor is not None:
                    mlflow.log_metric(f"{approach}_gpu_speedup_x", factor)
            summary_path = out_dir / "summary.md"
            if summary_path.is_file():
                mlflow.log_artifact(str(summary_path))
            mlflow.log_artifact(str(out_dir / "cpu_vs_cuda.json"))

    # Point latest at this combined folder (best single place to look)
    refresh_latest(out_dir, root / "results" / "latest")

    print("\n" + "=" * 72)
    print("QUESTION-CENTRIC VIEW READY")
    print("=" * 72)
    print(f"  Open: {out_dir / 'by_question.md'}")
    print(f"  Columns: {', '.join(pivot.get('columns', []))}")
    print(f"  Questions: {len(pivot.get('questions', []))}")
    print("  Also: results/latest/README.md")
    print("=" * 72)


if __name__ == "__main__":
    main()
