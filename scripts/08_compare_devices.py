#!/usr/bin/env python3
"""
Step 8 — Question-centric CPU vs CUDA visualization.

Builds a view where each question is a row/section and columns are:
  baseline|cpu, baseline|cuda, rag|cpu, rag|cuda, fine_tuned|cpu, ...

Outputs (under --out):
  by_question.md          ← primary human view
  by_question.json        ← full metrics + answer snippets
  by_question_quality.csv ← wide table of quality_score
  by_question_latency.csv ← wide table of generation_time
  summary.md              ← short aggregate deltas
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

from src.latency import speedup_factor
from src.mlflow_tracker import optional_mlflow_run
from src.question_view import build_question_view
from src.run_results import refresh_latest


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
    highlight = [
        "rougeL",
        "bert_score",
        "retrieval_hit_at_k",
        "faithfulness",
        "quality_score",
        "retrieval_time",
        "generation_time",
        "time_to_response",
        "tokens_per_sec",
        "speed_chars_per_sec",
        "peak_rss_mb",
        "cpu_threads",
        "cuda_used",
    ]
    lines = [
        f"# Aggregate CPU vs CUDA — {cpu_run_id} vs {cuda_run_id}",
        "",
        f"- **Generated:** {datetime.now(timezone.utc).isoformat()}",
        f"- **Per-question view:** [by_question.md](./by_question.md) ← start here",
        # A speedup figure is only meaningful next to the two machines behind it.
        f"- **CPU:** {_device_line(out_dir.parent / cpu_run_id, 'cpu')}",
        f"- **GPU:** {_device_line(out_dir.parent / cuda_run_id, 'cuda')}",
        "",
        "Higher quality metrics are better. **Lower `time_to_response` is better.**",
        "`time_to_response` = `retrieval_time` + `generation_time` (end-to-end wait for an answer).",
        "GPU speedup = CPU seconds ÷ GPU seconds (e.g. 4.0× means GPU was 4× faster).",
        "",
    ]
    for approach in approaches:
        lines.append(f"## Approach: `{approach}`")
        lines.append("")
        lines.append("| Metric | CPU | CUDA | Delta (CUDA − CPU) |")
        lines.append("|--------|-----|------|---------------------|")
        cpu_m = cpu_sum.get(approach, {})
        cuda_m = cuda_sum.get(approach, {})
        keys = [k for k in highlight if k in cpu_m or k in cuda_m]
        keys += sorted((set(cpu_m) | set(cuda_m)) - set(keys))
        for key in keys:
            c = cpu_m.get(key)
            g = cuda_m.get(key)
            c_s = f"{c:.4f}" if c is not None else "—"
            g_s = f"{g:.4f}" if g is not None else "—"
            d_s = f"{g - c:+.4f}" if c is not None and g is not None else "—"
            lines.append(f"| {key} | {c_s} | {g_s} | {d_s} |")
        lines.append("")

    lines.append("## Latency callout (`time_to_response`)")
    lines.append("")
    for approach in approaches:
        c = cpu_sum.get(approach, {}).get("time_to_response") or cpu_sum.get(approach, {}).get(
            "generation_time"
        )
        g = cuda_sum.get(approach, {}).get("time_to_response") or cuda_sum.get(approach, {}).get(
            "generation_time"
        )
        if c and g and g > 0:
            lines.append(
                f"- **{approach}:** CPU {c:.2f}s → CUDA {g:.2f}s (**{c / g:.1f}×** faster time-to-response)"
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
    out_dir = root / args.out
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
    print(f"  Also: results/latest/README.md")
    print("=" * 72)


if __name__ == "__main__":
    main()
