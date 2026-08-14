#!/usr/bin/env python3
"""
Step 2 — Baseline evaluation (no RAG, no fine-tuning).

Logs quality metrics AND cuda_used so you can compare CPU vs GPU runs.
Uses one MLflow parent run + ``mlflow.genai.evaluate`` with live traces.
"""

from __future__ import annotations

import logging
import os
import sys

import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.eval_prompts import load_evaluation_prompts
from src.eval_runner import run_stage_evaluation
from src.hardware import detect_hardware
from src.llm.runtime import approach_for_runtime, llm_tracking_params, resolve_runtime
from src.rag_pipeline import RAGPipeline
from src.run_results import save_stage_results

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CONFIG_PATH = os.environ.get("CONFIG_PATH", "/app/config/config.yaml")
PROMPTS_PATH = os.environ.get("PROMPTS_PATH", "/app/prompts/evaluation_prompts.txt")


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> None:
    hardware = detect_hardware()
    config = load_config()
    runtime = resolve_runtime(config)
    approach = approach_for_runtime("baseline", runtime)
    pipeline = RAGPipeline(config, hardware=hardware, runtime=runtime)

    test_prompts = load_evaluation_prompts(PROMPTS_PATH)
    if not test_prompts:
        raise SystemExit(f"No valid prompts in {PROMPTS_PATH}. Run 01b_generate_qa_pairs.py.")

    logger.info(
        "Baseline runtime=%s on %s with %d prompts",
        runtime,
        hardware.summary(),
        len(test_prompts),
    )
    tracking = llm_tracking_params(config, runtime)
    results = run_stage_evaluation(
        approach=approach,
        pipeline=pipeline,
        hardware=hardware,
        config=config,
        prompts=test_prompts,
        use_rag=False,
        stage="baseline_evaluation" if runtime == "transformers" else "baseline_gguf_evaluation",
        params={"model": tracking.get("gguf_filename") or config["llm"]["model"], **tracking},
        model_name=str(tracking.get("gguf_filename") or config["llm"]["model"]),
    )

    logger.info("\n=== Baseline Summary (%s / %s) ===", runtime, hardware.device.upper())
    metric_keys: set[str] = set()
    for r in results:
        metric_keys.update(r.get("metrics", {}).keys())
    for metric in sorted(metric_keys):
        values = [r["metrics"][metric] for r in results if metric in r.get("metrics", {})]
        if values:
            logger.info("Average %s: %.4f", metric, sum(values) / len(values))

    save_stage_results(
        approach,
        results,
        hardware,
        config.get("paths", {}).get("processed_dir", "/app/data/processed"),
        extra={"resources": dict(pipeline.last_load_meta), "runtime": runtime},
    )

    pipeline.cleanup()


if __name__ == "__main__":
    main()
