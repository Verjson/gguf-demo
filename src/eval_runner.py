"""
Stage evaluation via ``mlflow.genai.evaluate`` + custom scorers.

Creates one parent evaluation run (reused by GenAI evaluate), live traces from
``RAGPipeline``, GenAI assessments from scorers, and dual-writes Prometheus/Postgres
for ops dashboards.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Callable

import mlflow
import yaml

from src.eval_prompts import load_evaluation_prompts
from src.evaluator import Evaluator
from src.genai_scorers import build_metric_scorers
from src.hardware import HardwareInfo
from src.latency import attach_latency_metrics
from src.mlflow_tracker import MLflowTracker, calculate_quality_score
from src.model_registry import resolve_model_lineage
from src.rag_pipeline import RAGPipeline

logger = logging.getLogger(__name__)


def _load_config(config: dict | str | None) -> dict:
    if isinstance(config, dict):
        return config
    path = config or "/app/config/config.yaml"
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_stage_evaluation(
    *,
    approach: str,
    pipeline: RAGPipeline,
    hardware: HardwareInfo,
    config: dict | None = None,
    prompts: list[dict] | None = None,
    use_rag: bool = False,
    stage: str | None = None,
    params: dict[str, Any] | None = None,
    model_name: str | None = None,
    k: int | None = None,
    judge_fn: Callable[[str], str] | None = None,
) -> list[dict]:
    """
    Evaluate prompts with ``mlflow.genai.evaluate`` under a parent stage run.

    Returns the same list-of-dict shape used by ``save_stage_results``.
    """
    cfg = _load_config(config)
    test_prompts = prompts if prompts is not None else load_evaluation_prompts()
    if not test_prompts:
        raise ValueError("No evaluation prompts loaded")

    top_k = k if k is not None else int(cfg.get("vector_store", {}).get("top_k", 4))
    evaluator = Evaluator(
        judge_fn=judge_fn,
        enable_bertscore=cfg.get("evaluation", {}).get("bertscore", True),
    )
    scorers = build_metric_scorers(evaluator, include_rag=use_rag)
    lineage = resolve_model_lineage(cfg, approach=approach)
    resolved_model = model_name or (
        (cfg.get("llm") or {}).get("fine_tuned_path")
        or (cfg.get("llm") or {}).get("model")
        or lineage.get("base_model_id")
    )

    tracker = MLflowTracker(stage or f"{approach}_evaluation", hardware=hardware)
    side_channel: list[dict] = []

    def predict_fn(question: str) -> dict[str, Any]:
        context = ""
        retrieval_time = 0.0
        if use_rag:
            t0 = time.time()
            context = pipeline.retrieve_context(question, k=top_k)
            retrieval_time = time.time() - t0
        response = pipeline.generate_response(
            question, context=context if use_rag else None
        )
        gen = float(pipeline.last_generation_meta.get("generation_time", 0.0))
        row = {
            "question": question,
            "answer": response,
            "response": response,
            "context": context if use_rag else "",
            "generation_time": gen,
            "retrieval_time": retrieval_time,
        }
        side_channel.append(row)
        return row

    data = [
        {
            "inputs": {"question": p["question"]},
            "expectations": {"ground_truth": p["ground_truth"]},
            "tags": {"approach": approach, "device": hardware.device},
        }
        for p in test_prompts
    ]

    run_params = {
        **(params or {}),
        "use_rag": use_rag,
        "top_k": top_k if use_rag else 0,
        "n_prompts": len(test_prompts),
    }

    results: list[dict] = []
    with tracker.stage_run(
        approach,
        params=run_params,
        lineage=lineage,
        model_name=str(resolved_model),
    ):
        logger.info(
            "mlflow.genai.evaluate approach=%s n=%d rag=%s lineage=%s",
            approach,
            len(data),
            use_rag,
            lineage,
        )
        try:
            eval_result = mlflow.genai.evaluate(
                data=data,
                predict_fn=predict_fn,
                scorers=scorers,
            )
            logger.info(
                "GenAI evaluate finished; metrics=%s",
                getattr(eval_result, "metrics", None),
            )
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "mlflow.genai.evaluate failed (%s); falling back to manual loop",
                exc,
            )
            return _manual_fallback(
                approach=approach,
                pipeline=pipeline,
                hardware=hardware,
                tracker=tracker,
                evaluator=evaluator,
                test_prompts=test_prompts,
                use_rag=use_rag,
                top_k=top_k,
                resolved_model=str(resolved_model),
                params=run_params,
            )

        # Ops dual-write + parent aggregates (scorers already attached assessments)
        by_question = {row["question"]: row for row in side_channel}
        for prompt in test_prompts:
            q = prompt["question"]
            row = by_question.get(q)
            if not row:
                continue
            response = str(row.get("answer") or row.get("response") or "")
            context = str(row.get("context") or "") if use_rag else None
            metrics = evaluator.evaluate_response(
                question=q,
                response=response,
                ground_truth=prompt["ground_truth"],
                context=context,
                k=top_k,
            )
            attach_latency_metrics(
                metrics,
                generation_time=float(row.get("generation_time") or 0.0),
                retrieval_time=float(row.get("retrieval_time") or 0.0) if use_rag else 0.0,
                response_chars=float(len(response)),
            )
            metrics.update(hardware.as_metrics())
            metrics["quality_score"] = calculate_quality_score(metrics)

            tracker.log_evaluation(
                approach=approach,
                question=q,
                response=response,
                metrics=metrics,
                params=run_params,
                model_name=str(resolved_model),
                context=context,
                skip_assessments=True,  # scorers already wrote GenAI assessments
            )
            out: dict[str, Any] = {
                "question": q,
                "response": response,
                "metrics": metrics,
            }
            if use_rag and context:
                out["context"] = context
            results.append(out)

    return results


def _manual_fallback(
    *,
    approach: str,
    pipeline: RAGPipeline,
    hardware: HardwareInfo,
    tracker: MLflowTracker,
    evaluator: Evaluator,
    test_prompts: list[dict],
    use_rag: bool,
    top_k: int,
    resolved_model: str,
    params: dict[str, Any],
) -> list[dict]:
    """If genai.evaluate is unavailable, keep parent-run + live traces + assessments."""
    from mlflow.entities import SpanType

    results: list[dict] = []
    # Caller already holds stage_run; continue logging into it.
    for i, prompt_data in enumerate(test_prompts):
        logger.info("Fallback eval %d/%d (%s)", i + 1, len(test_prompts), approach)
        question = prompt_data["question"]

        with mlflow.start_span(name=f"eval.{approach}", span_type=SpanType.CHAIN) as root:
            root.set_inputs({"question": question})
            context = ""
            retrieval_time = 0.0
            if use_rag:
                t0 = time.time()
                context = pipeline.retrieve_context(question, k=top_k)
                retrieval_time = time.time() - t0
            response = pipeline.generate_response(
                question,
                context=context if use_rag else None,
            )
            root.set_outputs({"answer": response})

            gen = float(pipeline.last_generation_meta.get("generation_time", 0.0))
            metrics = evaluator.evaluate_response(
                question=question,
                response=response,
                ground_truth=prompt_data["ground_truth"],
                context=context if use_rag else None,
                k=top_k,
            )
            attach_latency_metrics(
                metrics,
                generation_time=gen,
                retrieval_time=retrieval_time if use_rag else 0.0,
                response_chars=float(len(response)),
            )
            metrics.update(hardware.as_metrics())
            tracker.log_evaluation(
                approach=approach,
                question=question,
                response=response,
                metrics=metrics,
                params=params,
                model_name=resolved_model,
                context=context if use_rag else None,
            )

        item: dict[str, Any] = {
            "question": question,
            "response": response,
            "metrics": metrics,
        }
        if use_rag:
            item["context"] = context
        results.append(item)
    return results
