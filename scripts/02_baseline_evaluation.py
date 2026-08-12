#!/usr/bin/env python3
"""
Step 2 — Baseline evaluation (no RAG, no fine-tuning).

Logs quality metrics AND cuda_used so you can compare CPU vs GPU runs.
"""

from __future__ import annotations

import logging
import os
import sys
import time

import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.evaluator import Evaluator
from src.hardware import detect_hardware
from src.latency import attach_latency_metrics
from src.mlflow_tracker import MLflowTracker
from src.rag_pipeline import RAGPipeline
from src.run_results import save_stage_results

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CONFIG_PATH = os.environ.get("CONFIG_PATH", "/app/config/config.yaml")
PROMPTS_PATH = os.environ.get("PROMPTS_PATH", "/app/prompts/evaluation_prompts.txt")


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_evaluation_prompts() -> list[dict]:
    prompts = []
    with open(PROMPTS_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "|" not in line:
                continue
            question, ground_truth = line.split("|", 1)
            prompts.append({"question": question.strip(), "ground_truth": ground_truth.strip()})
    return prompts


def main() -> None:
    hardware = detect_hardware()
    config = load_config()
    pipeline = RAGPipeline(config, hardware=hardware)
    evaluator = Evaluator(enable_bertscore=config.get("evaluation", {}).get("bertscore", True))
    tracker = MLflowTracker("baseline_evaluation", hardware=hardware)

    test_prompts = load_evaluation_prompts()
    if not test_prompts:
        raise SystemExit(f"No valid prompts in {PROMPTS_PATH}. Run 01b_generate_qa_pairs.py.")

    logger.info("Baseline on %s with %d prompts", hardware.summary(), len(test_prompts))
    results = []

    for i, prompt_data in enumerate(test_prompts):
        logger.info("Evaluating prompt %d/%d", i + 1, len(test_prompts))
        start_time = time.time()
        response = pipeline.generate_response(prompt_data["question"])
        wall = time.time() - start_time
        gen = float(pipeline.last_generation_meta.get("generation_time", wall))

        metrics = evaluator.evaluate_response(
            question=prompt_data["question"],
            response=response,
            ground_truth=prompt_data["ground_truth"],
        )
        attach_latency_metrics(
            metrics,
            generation_time=gen,
            retrieval_time=0.0,
            response_chars=float(len(response)),
        )
        metrics.update(hardware.as_metrics())

        tracker.log_evaluation(
            approach="baseline",
            question=prompt_data["question"],
            response=response,
            metrics=metrics,
            params={"model": config["llm"]["model"]},
            model_name=config["llm"]["model"],
        )
        results.append({"question": prompt_data["question"], "response": response, "metrics": metrics})

    logger.info("\n=== Baseline Summary (%s) ===", hardware.device.upper())
    for metric in results[0]["metrics"]:
        avg = sum(r["metrics"][metric] for r in results) / len(results)
        logger.info("Average %s: %.4f", metric, avg)

    save_stage_results(
        "baseline",
        results,
        hardware,
        config.get("paths", {}).get("processed_dir", "/app/data/processed"),
    )

    pipeline.cleanup()


if __name__ == "__main__":
    main()
