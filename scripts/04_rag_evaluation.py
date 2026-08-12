#!/usr/bin/env python3
"""
Step 4 — RAG evaluation with retrieval_hit@k, faithfulness, and CUDA metrics.

Uses one MLflow parent run + ``mlflow.genai.evaluate`` with live retrieve/generate traces.
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
    pipeline = RAGPipeline(config, hardware=hardware)

    use_judge = config.get("evaluation", {}).get("llm_judge", False)
    judge_fn = (lambda p: pipeline.generate_response(p)) if use_judge else None

    papers_dir = config.get("paths", {}).get("papers_dir", "/app/data/papers")
    pipeline.ensure_vector_store(papers_dir)

    test_prompts = load_evaluation_prompts(PROMPTS_PATH)
    if not test_prompts:
        raise SystemExit(f"No valid prompts in {PROMPTS_PATH}")

    k = config.get("vector_store", {}).get("top_k", 4)
    logger.info("RAG eval on %s with %d prompts (k=%d)", hardware.summary(), len(test_prompts), k)

    results = run_stage_evaluation(
        approach="rag",
        pipeline=pipeline,
        hardware=hardware,
        config=config,
        prompts=test_prompts,
        use_rag=True,
        stage="rag_evaluation",
        params={
            "model": config["llm"]["model"],
            "chunk_size": config["chunking"]["chunk_size"],
            "k_documents": k,
        },
        model_name=config["llm"]["model"],
        k=k,
        judge_fn=judge_fn,
    )

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
