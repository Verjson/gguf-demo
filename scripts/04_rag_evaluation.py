#!/usr/bin/env python3
"""
Step 4 — RAG evaluation with retrieval_hit@k, faithfulness, and CUDA metrics.
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
    """Parse question|answer lines; join continuation lines into the prior answer."""
    prompts: list[dict] = []
    current: dict | None = None
    with open(PROMPTS_PATH, encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "|" in line:
                if current:
                    prompts.append(current)
                question, ground_truth = line.split("|", 1)
                current = {
                    "question": question.strip(),
                    "ground_truth": " ".join(ground_truth.split()),
                }
            elif current:
                current["ground_truth"] = " ".join(
                    f"{current['ground_truth']} {stripped}".split()
                )
        if current:
            prompts.append(current)
    return prompts


def main() -> None:
    hardware = detect_hardware()
    config = load_config()
    pipeline = RAGPipeline(config, hardware=hardware)

    use_judge = config.get("evaluation", {}).get("llm_judge", False)
    judge_fn = (lambda p: pipeline.generate_response(p)) if use_judge else None
    evaluator = Evaluator(
        judge_fn=judge_fn,
        enable_bertscore=config.get("evaluation", {}).get("bertscore", True),
    )
    tracker = MLflowTracker("rag_evaluation", hardware=hardware)

    papers_dir = config.get("paths", {}).get("papers_dir", "/app/data/papers")
    pipeline.ensure_vector_store(papers_dir)

    test_prompts = load_evaluation_prompts()
    if not test_prompts:
        raise SystemExit(f"No valid prompts in {PROMPTS_PATH}")

    k = config.get("vector_store", {}).get("top_k", 4)
    logger.info("RAG eval on %s with %d prompts (k=%d)", hardware.summary(), len(test_prompts), k)
    results = []

    for i, prompt_data in enumerate(test_prompts):
        logger.info("Evaluating prompt %d/%d", i + 1, len(test_prompts))
        t0 = time.time()
        context = pipeline.retrieve_context(prompt_data["question"], k=k)
        retrieval_time = time.time() - t0

        response = pipeline.generate_response(prompt_data["question"], context=context)
        # Snapshot immediately — llm_judge inside evaluate_response would overwrite this
        gen = float(pipeline.last_generation_meta.get("generation_time", 0.0))

        metrics = evaluator.evaluate_response(
            question=prompt_data["question"],
            response=response,
            ground_truth=prompt_data["ground_truth"],
            context=context,
            k=k,
        )
        attach_latency_metrics(
            metrics,
            generation_time=gen,
            retrieval_time=retrieval_time,
            response_chars=float(len(response)),
        )
        metrics.update(hardware.as_metrics())

        tracker.log_evaluation(
            approach="rag",
            question=prompt_data["question"],
            response=response,
            metrics=metrics,
            params={
                "model": config["llm"]["model"],
                "chunk_size": config["chunking"]["chunk_size"],
                "k_documents": k,
            },
            model_name=config["llm"]["model"],
            context=context,
        )
        results.append({
            "question": prompt_data["question"],
            "response": response,
            "context": context,
            "metrics": metrics,
        })

    logger.info("\n=== RAG Summary (%s) ===", hardware.device.upper())
    metric_keys: set[str] = set()
    for r in results:
        metric_keys.update(r.get("metrics", {}).keys())
    for metric in sorted(metric_keys):
        values = [r["metrics"][metric] for r in results if metric in r.get("metrics", {})]
        if values:
            logger.info("Average %s: %.4f", metric, sum(values) / len(values))

    save_stage_results(
        "rag",
        results,
        hardware,
        config.get("paths", {}).get("processed_dir", "/app/data/processed"),
    )

    pipeline.cleanup()


if __name__ == "__main__":
    main()
