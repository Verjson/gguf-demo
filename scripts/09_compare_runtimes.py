#!/usr/bin/env python3
"""
Step 9 — Transformers (safetensors/PyTorch) vs GGUF (llama.cpp) for the same Phi-3.

Pairs ``baseline`` with ``baseline_gguf`` and ``rag`` with ``rag_gguf`` on each
device that has both stage files. Quality should stay close; speed and RSS are
the runtime story (Q4 GGUF vs BF16/FP16 Transformers).
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
from src.snapshot import refresh_latest

PAIRS = (
    ("baseline", "baseline_gguf"),
    ("rag", "rag_gguf"),
)


def _load_aggregate(run_dir: Path, stage: str) -> dict:
    for name in (f"{stage}_results.json",):
        path = run_dir / name
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8")).get("aggregate") or {}
    return {}


def _metric(agg: dict, key: str) -> float | None:
    val = agg.get(key)
    if isinstance(val, (int, float)):
        return float(val)
    return None


def write_report(
    out_dir: Path,
    *,
    cpu_dir: Path | None,
    cuda_dir: Path | None,
) -> dict:
    lines = [
        "# Transformers vs GGUF",
        "",
        f"- **Generated:** {datetime.now(timezone.utc).isoformat()}",
        "- **Transformers:** Hugging Face + PyTorch safetensors (`microsoft/Phi-3-mini-4k-instruct`)",
        "- **GGUF:** llama.cpp (`microsoft/Phi-3-mini-4k-instruct-gguf` Q4_K_M by default)",
        "",
        "Same questions, same RAG index. Engines are swapped behind `src.llm.factory`.",
        "",
    ]
    payload: dict = {"pairs": {}, "generated_at": datetime.now(timezone.utc).isoformat()}

    for device, run_dir in (("cpu", cpu_dir), ("cuda", cuda_dir)):
        if run_dir is None or not run_dir.is_dir():
            continue
        lines.append(f"## Device: `{device}` (`{run_dir.name}`)")
        lines.append("")
        device_block: dict = {}
        for tf_name, gguf_name in PAIRS:
            tf = _load_aggregate(run_dir, tf_name)
            gg = _load_aggregate(run_dir, gguf_name)
            if not tf and not gg:
                continue
            ttr_tf = _metric(tf, "time_to_response") or _metric(tf, "generation_time")
            ttr_gg = _metric(gg, "time_to_response") or _metric(gg, "generation_time")
            rouge_tf = _metric(tf, "rougeL")
            rouge_gg = _metric(gg, "rougeL")
            tok_tf = _metric(tf, "tokens_per_sec")
            tok_gg = _metric(gg, "tokens_per_sec")
            rss_tf = _metric(tf, "peak_rss_mb")
            rss_gg = _metric(gg, "peak_rss_mb")
            factor = speedup_factor(ttr_tf, ttr_gg)
            lines.append(f"### `{tf_name}` vs `{gguf_name}`")
            lines.append("")
            if ttr_tf is not None and ttr_gg is not None:
                lines.append(
                    f"- **time_to_response:** Transformers {ttr_tf:.2f}s → GGUF {ttr_gg:.2f}s"
                    + (f" (**{factor:.2f}×** vs Transformers)" if factor else "")
                )
            if tok_tf is not None and tok_gg is not None:
                lines.append(
                    f"- **tokens_per_sec:** Transformers {tok_tf:.2f} → GGUF {tok_gg:.2f}"
                )
            if rouge_tf is not None and rouge_gg is not None:
                delta = rouge_gg - rouge_tf
                lines.append(
                    f"- **rougeL:** Transformers {rouge_tf:.4f} → GGUF {rouge_gg:.4f} ({delta:+.4f})"
                )
            if rss_tf is not None and rss_gg is not None:
                lines.append(
                    f"- **peak_rss_mb:** Transformers {rss_tf:.0f} → GGUF {rss_gg:.0f}"
                )
            lines.append("")
            device_block[tf_name] = {
                "transformers": tf,
                "gguf": gg,
                "ttr_speedup_gguf_vs_tf": factor,
            }
        payload["pairs"][device] = device_block

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out_dir / "transformers_vs_gguf.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpu-run-id", default=None)
    parser.add_argument("--cuda-run-id", default=None)
    parser.add_argument("--out", required=True, help="Output directory under the repo")
    parser.add_argument("--repo-root", default=os.environ.get("REPO_ROOT", "/app"))
    args = parser.parse_args()

    root = Path(args.repo_root)
    runs = root / "results" / "runs"
    cpu_dir = runs / args.cpu_run_id if args.cpu_run_id else None
    cuda_dir = runs / args.cuda_run_id if args.cuda_run_id else None
    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = root / out_dir

    with optional_mlflow_run("transformers_vs_gguf"):
        write_report(out_dir, cpu_dir=cpu_dir, cuda_dir=cuda_dir)
    # The comparison folder, never `root` — refresh_latest copies its source, so a
    # repo root here snapshots the Hugging Face cache and results/ into itself.
    refresh_latest(out_dir, root / "results" / "latest")
    print(f"Wrote Transformers vs GGUF summary → {out_dir}")


if __name__ == "__main__":
    main()
