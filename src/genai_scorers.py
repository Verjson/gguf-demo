"""
Custom MLflow GenAI scorers wrapping this project's Evaluator metrics.

Used by ``mlflow.genai.evaluate`` so GenAI assessments and experiment-run
aggregates come from the same scoring code as Grafana/Postgres.
"""

from __future__ import annotations

from typing import Any

from mlflow.genai.scorers import scorer

from src.evaluator import Evaluator


def _answer(outputs: Any) -> str:
    if isinstance(outputs, str):
        return outputs
    if isinstance(outputs, dict):
        for key in ("answer", "response", "output", "text"):
            if key in outputs and outputs[key] is not None:
                return str(outputs[key])
    return str(outputs)


def _context(outputs: Any) -> str:
    if isinstance(outputs, dict):
        return str(outputs.get("context") or "")
    return ""


def _ground_truth(expectations: Any) -> str | None:
    if expectations is None:
        return None
    if isinstance(expectations, str):
        return expectations
    if isinstance(expectations, dict):
        for key in ("ground_truth", "expected_response", "answer", "expected_answer"):
            if key in expectations and expectations[key] is not None:
                return str(expectations[key])
    return None


def build_metric_scorers(
    evaluator: Evaluator,
    *,
    include_rag: bool = False,
) -> list:
    """
    Build ``@scorer`` callables for reference / RAG / latency-friendly metrics.

    Latency gauges (generation_time) are logged from the eval runner side-channel
    because scorers only see inputs/outputs/expectations/trace — not pipeline meta —
    unless present on the trace.
    """

    @scorer(name="rouge1", aggregations=["mean"])
    def rouge1(outputs, expectations):
        gt = _ground_truth(expectations)
        if not gt:
            return None
        return float(evaluator.rouge_scorer.score(gt, _answer(outputs))["rouge1"].fmeasure)

    @scorer(name="rouge2", aggregations=["mean"])
    def rouge2(outputs, expectations):
        gt = _ground_truth(expectations)
        if not gt:
            return None
        return float(evaluator.rouge_scorer.score(gt, _answer(outputs))["rouge2"].fmeasure)

    @scorer(name="rougeL", aggregations=["mean"])
    def rougeL(outputs, expectations):  # noqa: N802 — metric name matches Grafana
        gt = _ground_truth(expectations)
        if not gt:
            return None
        return float(evaluator.rouge_scorer.score(gt, _answer(outputs))["rougeL"].fmeasure)

    @scorer(name="bert_score", aggregations=["mean"])
    def bert_score(outputs, expectations):
        gt = _ground_truth(expectations)
        if not gt or not evaluator.enable_bertscore:
            return None
        metrics = evaluator.evaluate_response(
            question="",
            response=_answer(outputs),
            ground_truth=gt,
        )
        return metrics.get("bert_score")

    @scorer(name="answer_relevancy", aggregations=["mean"])
    def answer_relevancy(inputs, outputs):
        question = ""
        if isinstance(inputs, dict):
            question = str(inputs.get("question") or "")
        return float(evaluator._answer_relevancy(question, _answer(outputs)))

    @scorer(name="coherence", aggregations=["mean"])
    def coherence(outputs):
        return float(evaluator._evaluate_coherence(_answer(outputs)))

    @scorer(name="domain_relevance", aggregations=["mean"])
    def domain_relevance(outputs):
        return float(evaluator._calculate_domain_relevance(_answer(outputs)))

    scorers = [
        rouge1,
        rouge2,
        rougeL,
        bert_score,
        answer_relevancy,
        coherence,
        domain_relevance,
    ]

    if include_rag:

        @scorer(name="faithfulness", aggregations=["mean"])
        def faithfulness(outputs):
            ctx = _context(outputs)
            if not ctx:
                return None
            return float(evaluator._estimate_faithfulness(_answer(outputs), ctx))

        @scorer(name="retrieval_hit_at_k", aggregations=["mean"])
        def retrieval_hit_at_k(outputs, expectations):
            ctx = _context(outputs)
            gt = _ground_truth(expectations)
            if not ctx or not gt:
                return None
            return float(evaluator.retrieval_hit_at_k(gt, ctx))

        @scorer(name="context_utilization", aggregations=["mean"])
        def context_utilization(outputs):
            ctx = _context(outputs)
            if not ctx:
                return None
            return float(evaluator._calculate_context_utilization(_answer(outputs), ctx))

        scorers.extend([faithfulness, retrieval_hit_at_k, context_utilization])

    @scorer(name="quality_score", aggregations=["mean"])
    def quality_score(inputs, outputs, expectations):
        """Same weighted blend used by Grafana / historical tracker."""
        question = ""
        if isinstance(inputs, dict):
            question = str(inputs.get("question") or "")
        metrics = evaluator.evaluate_response(
            question=question,
            response=_answer(outputs),
            ground_truth=_ground_truth(expectations),
            context=_context(outputs) or None,
        )
        # Inline blend (avoid circular import with tracker)
        weights = {
            "rouge1": 0.10,
            "rouge2": 0.10,
            "rougeL": 0.18,
            "bert_score": 0.18,
            "retrieval_hit_at_k": 0.14,
            "faithfulness": 0.14,
            "judge_groundedness": 0.08,
            "answer_relevancy": 0.04,
            "domain_relevance": 0.02,
            "context_utilization": 0.01,
            "coherence": 0.01,
        }
        score = 0.0
        total = 0.0
        for key, weight in weights.items():
            if key in metrics and weight > 0:
                score += metrics[key] * weight
                total += weight
        return score / total if total else 0.0

    scorers.append(quality_score)
    return scorers
