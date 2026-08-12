#!/usr/bin/env python3
"""
Step 6 — Compare baseline vs fine-tuned vs fine-tuned+RAG.

Reports quality metrics and CUDA vs CPU device info for each approach.
Each approach uses one MLflow parent run + GenAI evaluate.
"""

from __future__ import annotations

import json
import logging
import os
import sys

import mlflow
import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.eval_prompts import load_evaluation_prompts
from src.eval_runner import run_stage_evaluation
from src.hardware import detect_hardware
from src.rag_pipeline import RAGPipeline
from src.run_results import export_run

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CONFIG_PATH = os.environ.get("CONFIG_PATH", "/app/config/config.yaml")
PROMPTS_PATH = os.environ.get("PROMPTS_PATH", "/app/prompts/evaluation_prompts.txt")
# Allow pipeline to point at device-specific adapters (adapter_cpu / adapter_cuda)
FINE_TUNED_PATH = os.environ.get("FINE_TUNED_PATH", "/app/models/fine_tuned/adapter")


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if os.path.isdir(FINE_TUNED_PATH):
        config.setdefault("llm", {})["fine_tuned_path"] = FINE_TUNED_PATH
        logger.info("Using fine-tuned adapter at %s", FINE_TUNED_PATH)
    elif not config.get("llm", {}).get("fine_tuned_path"):
        raise SystemExit(
            f"No fine-tuned model at {FINE_TUNED_PATH}. Run 05_fine_tune.py first."
        )
    return config


def run_approach(
    label: str,
    config: dict,
    test_prompts: list[dict],
    use_rag: bool,
    papers_dir: str,
    hardware,
) -> list[dict]:
    run_config = yaml.safe_load(yaml.dump(config))
    if label == "baseline":
        run_config["llm"]["fine_tuned_path"] = None

    pipeline = RAGPipeline(run_config, hardware=hardware)
    use_judge = config.get("evaluation", {}).get("llm_judge", False)
    judge_fn = (lambda p: pipeline.generate_response(p)) if use_judge and use_rag else None
    k = config.get("vector_store", {}).get("top_k", 4)

    if use_rag:
        pipeline.ensure_vector_store(papers_dir)

    model_name = run_config["llm"].get("fine_tuned_path") or run_config["llm"]["model"]
    results = run_stage_evaluation(
        approach=label,
        pipeline=pipeline,
        hardware=hardware,
        config=run_config,
        prompts=test_prompts,
        use_rag=use_rag,
        stage=f"comparison_{label}",
        params={"use_rag": use_rag},
        model_name=model_name,
        k=k,
        judge_fn=judge_fn,
    )
    pipeline.cleanup()
    return results


def aggregate(results: list[dict]) -> dict[str, float]:
    if not results:
        return {}
    keys: set[str] = set()
    for r in results:
        keys.update(r.get("metrics", {}).keys())
    return {
        k: sum(r["metrics"][k] for r in results if k in r.get("metrics", {}))
        / max(1, sum(1 for r in results if k in r.get("metrics", {})))
        for k in keys
    }


def main() -> None:
    hardware = detect_hardware()
    config = load_config()
    test_prompts = load_evaluation_prompts(PROMPTS_PATH)
    if not test_prompts:
        raise SystemExit(f"No valid prompts in {PROMPTS_PATH}")

    papers_dir = config.get("paths", {}).get("papers_dir", "/app/data/papers")
    processed_dir = config.get("paths", {}).get("processed_dir", "/app/data/processed")

    logger.info("Full comparison | %s", hardware.summary())

    all_results = {
        "baseline": run_approach(
            "baseline", config, test_prompts, use_rag=False, papers_dir=papers_dir, hardware=hardware
        ),
        "fine_tuned": run_approach(
            "fine_tuned", config, test_prompts, use_rag=False, papers_dir=papers_dir, hardware=hardware
        ),
        "fine_tuned_with_rag": run_approach(
            "fine_tuned_with_rag",
            config,
            test_prompts,
            use_rag=True,
            papers_dir=papers_dir,
            hardware=hardware,
        ),
    }

    summary = {k: aggregate(v) for k, v in all_results.items()}
    report = {
        "hardware": hardware.as_params(),
        "comparison_summary": summary,
        "detailed_results": all_results,
    }

    os.makedirs(processed_dir, exist_ok=True)
    report_path = os.path.join(processed_dir, "comparison_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n" + "=" * 72)
    print(f"HARDWARE: {hardware.summary()}")
    print("COMPARISON SUMMARY")
    print("=" * 72)
    for approach, metrics in summary.items():
        print(f"\n{approach.upper()}:")
        for name, value in sorted(metrics.items()):
            print(f"  {name:<25} {value:.4f}")

    with mlflow.start_run(run_name="final_comparison_summary"):
        mlflow.set_tag("device", hardware.device)
        mlflow.set_tag("cuda_available", str(hardware.cuda_available))
        mlflow.log_params({k: str(v) for k, v in hardware.as_params().items()})
        for approach, metrics in summary.items():
            for name, value in metrics.items():
                mlflow.log_metric(f"{approach}_{name}", value)
        mlflow.log_artifact(report_path)

    print("\nReport:", report_path)
    print("MLflow UI: http://localhost:5000")
    print("Grafana:   http://localhost:3000 (admin/admin)")

    # Pipeline sets SKIP_AUTO_EXPORT=1 and calls 07_export_results.py itself
    if os.environ.get("SKIP_AUTO_EXPORT", "").lower() in {"1", "true", "yes"}:
        logger.info("SKIP_AUTO_EXPORT set — leaving export to scripts/07_export_results.py")
        return

    run_dir = export_run(repo_root="/app")
    print(f"\nExported for git commit: {run_dir}")
    print("  git add results/ && git commit -m \"results: full comparison run\"")


if __name__ == "__main__":
    main()
