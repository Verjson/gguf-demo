#!/usr/bin/env python3
"""
CLI: run a single prompt against one PDF and print response quality + CUDA metrics.

Usage:
  python scripts/00_query.py --prompt "What is the main contribution?" --pdf data/papers/foo.pdf
  python scripts/00_query.py --runtime gguf --prompt "..." --pdf data/papers/foo.pdf --no-rag
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import time

import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.evaluator import Evaluator
from src.hardware import detect_hardware
from src.latency import attach_generation_meta, attach_latency_metrics, attach_retrieval_meta
from src.llm.runtime import approach_for_runtime, resolve_runtime
from src.mlflow_tracker import MLflowTracker
from src.model_registry import resolve_model_lineage
from src.rag_pipeline import RAGPipeline

import mlflow
from mlflow.entities import SpanType

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CONFIG_PATH = os.environ.get("CONFIG_PATH", "/app/config/config.yaml")


def load_config(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt", required=True, help="Question to ask about the document")
    parser.add_argument("--pdf", required=True, help="Path to a domain PDF")
    parser.add_argument("--no-rag", action="store_true", help="Skip retrieval (baseline)")
    parser.add_argument("--ground-truth", default=None, help="Optional reference answer")
    parser.add_argument("--k", type=int, default=4)
    parser.add_argument("--config", default=CONFIG_PATH)
    parser.add_argument("--no-bertscore", action="store_true")
    parser.add_argument("--judge", action="store_true", help="Enable LLM-as-judge groundedness")
    parser.add_argument(
        "--runtime",
        default=None,
        help="LLM engine: transformers (default) or gguf. Overrides LLM_RUNTIME.",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.pdf):
        raise SystemExit(f"PDF not found: {args.pdf}")

    hardware = detect_hardware()
    config = load_config(args.config)
    runtime = resolve_runtime(config, args.runtime)
    pipeline = RAGPipeline(config, hardware=hardware, runtime=runtime)

    judge_fn = (lambda p: pipeline.judge_response(p)) if args.judge else None
    evaluator = Evaluator(judge_fn=judge_fn, enable_bertscore=not args.no_bertscore)
    tracker = MLflowTracker("single_query", hardware=hardware)

    use_rag = not args.no_rag
    approach = approach_for_runtime("rag" if use_rag else "baseline", runtime)
    lineage = resolve_model_lineage(config, approach=approach)
    logger.info("Mode: %s runtime=%s | %s", approach, runtime, hardware.summary())

    with tracker.stage_run(
        approach,
        params={"pdf": args.pdf, "use_rag": use_rag, "k": args.k},
        lineage=lineage,
        model_name=config["llm"]["model"],
        run_name=f"query-{approach}@{hardware.device}",
    ):
        tracker.log_run_metrics(pipeline.last_load_meta)
        start = time.time()
        context = ""
        retrieval_time = 0.0

        with mlflow.start_span(name=f"eval.{approach}", span_type=SpanType.CHAIN) as root:
            root.set_inputs({"question": args.prompt})
            if use_rag:
                papers_dir = os.path.dirname(os.path.abspath(args.pdf))
                pipeline.ensure_vector_store(papers_dir)
                t0 = time.time()
                context = pipeline.retrieve_context(args.prompt, k=args.k)
                retrieval_time = time.time() - t0
                response = pipeline.generate_response(args.prompt, context=context)
            else:
                response = pipeline.generate_response(args.prompt)
            root.set_outputs({"answer": response})

            elapsed = time.time() - start
            gen = float(pipeline.last_generation_meta.get("generation_time", elapsed))

            metrics = evaluator.evaluate_response(
                question=args.prompt,
                response=response,
                ground_truth=args.ground_truth,
                context=context if use_rag else None,
                k=args.k,
            )
            attach_latency_metrics(
                metrics,
                generation_time=gen,
                retrieval_time=retrieval_time if use_rag else 0.0,
                response_chars=pipeline.last_generation_meta.get("response_chars"),
            )
            attach_generation_meta(metrics, pipeline.last_generation_meta)
            if use_rag:
                attach_retrieval_meta(metrics, pipeline.last_retrieval_meta)
            metrics.update(hardware.as_metrics())

            # Attach assessments while the chain span is still active
            tracker.log_evaluation(
                approach=approach,
                question=args.prompt,
                response=response,
                metrics=metrics,
                params={"pdf": args.pdf, "use_rag": use_rag},
                model_name=config["llm"]["model"],
                context=context if use_rag else None,
            )

    print("\n" + "=" * 72)
    print("HARDWARE")
    print("=" * 72)
    print(hardware.summary())
    print(f"  cuda_used metric: {metrics.get('cuda_used')}")
    print("\n" + "=" * 72)
    print("QUESTION")
    print("=" * 72)
    print(args.prompt)
    if use_rag:
        print("\n" + "=" * 72)
        print("RETRIEVED CONTEXT (truncated)")
        print("=" * 72)
        print(context[:1500] + ("..." if len(context) > 1500 else ""))
    print("\n" + "=" * 72)
    print("RESPONSE")
    print("=" * 72)
    print(response)
    print("\n" + "=" * 72)
    print("QUALITY + DEVICE METRICS")
    print("=" * 72)
    for name, value in sorted(metrics.items()):
        print(f"  {name:<25} {value:.4f}" if isinstance(value, float) else f"  {name:<25} {value}")
    print("=" * 72)
    print("MLflow http://localhost:5000 | Grafana http://localhost:3000 | Prometheus :9090")

    pipeline.cleanup()


if __name__ == "__main__":
    main()
