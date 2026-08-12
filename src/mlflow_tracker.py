"""
Experiment tracking (MLflow), operational metrics (Prometheus), and Postgres persistence.

MLflow UI has two modes:
  - **GenAI** — traces (question → retrieve → generate → score). This is the primary
    view for RAG / LLM evaluation.
  - **Model Training** — classic runs with params/metrics/artifacts (also logged).

Open http://localhost:5000 → GenAI → Experiments → **gguf-demo** (override with
MLFLOW_EXPERIMENT_NAME). Prometheus scrapes the persistent metrics server on
app:8000. Rows also land in evaluation_metrics for Grafana SQL panels.
"""

from __future__ import annotations

import logging
import os
import tempfile
from typing import Any, Dict

import mlflow
from mlflow.entities import SpanType
from prometheus_client import Counter, Gauge, Histogram, start_http_server

from src.hardware import HardwareInfo, detect_hardware
from src.metrics_store import MetricsStore

logger = logging.getLogger(__name__)

# Multiprocess directory shared with scripts/metrics_server.py
_MULTIPROC_DIR = os.environ.get("PROMETHEUS_MULTIPROC_DIR", "").strip()
if _MULTIPROC_DIR:
    os.makedirs(_MULTIPROC_DIR, exist_ok=True)

# Prometheus instruments — scraped by the prometheus service in docker-compose.
EVALUATION_REQUESTS = Counter(
    "evaluation_requests_total",
    "Total evaluation requests",
    ["device", "approach"],
)
EVALUATION_DURATION = Histogram(
    "evaluation_duration_seconds",
    "Evaluation / generation duration",
    ["device", "approach"],
)
RESPONSE_QUALITY = Gauge(
    "response_quality_score",
    "Overall response quality score",
    ["device"],
    multiprocess_mode="livemostrecent",
)
DOMAIN_RELEVANCE = Gauge(
    "domain_relevance_score",
    "Domain relevance score",
    ["device"],
    multiprocess_mode="livemostrecent",
)
CONTEXT_UTILIZATION = Gauge(
    "context_utilization_score",
    "Context utilization score",
    ["device"],
    multiprocess_mode="livemostrecent",
)
CUDA_AVAILABLE = Gauge(
    "cuda_available",
    "1 if CUDA is available, else 0",
    multiprocess_mode="livemostrecent",
)
CUDA_DEVICE_COUNT = Gauge(
    "cuda_device_count",
    "Number of CUDA devices",
    multiprocess_mode="livemostrecent",
)
RETRIEVAL_HIT = Gauge(
    "retrieval_hit_at_k",
    "Retrieval hit@k for last RAG eval",
    ["device"],
    multiprocess_mode="livemostrecent",
)
FAITHFULNESS = Gauge(
    "faithfulness_score",
    "Faithfulness proxy for last RAG eval",
    ["device"],
    multiprocess_mode="livemostrecent",
)

_PROMETHEUS_HTTP_STARTED = False


def _ensure_prometheus_http() -> None:
    """Start an in-process :8000 only when no persistent multiproc server is configured."""
    global _PROMETHEUS_HTTP_STARTED
    if _PROMETHEUS_HTTP_STARTED or _MULTIPROC_DIR:
        return
    try:
        start_http_server(8000)
        logger.info("Prometheus metrics server listening on :8000 (in-process fallback)")
        _PROMETHEUS_HTTP_STARTED = True
    except OSError:
        logger.warning("Prometheus metrics server already running on :8000")
        _PROMETHEUS_HTTP_STARTED = True


def _numeric_metrics(metrics: Dict[str, Any]) -> Dict[str, float]:
    return {
        k: float(v)
        for k, v in metrics.items()
        if isinstance(v, (int, float)) and not isinstance(v, bool)
    }


class MLflowTracker:
    """Dual-write evaluation results to MLflow (GenAI traces + classic runs), Prometheus, Postgres."""

    def __init__(
        self,
        experiment_name: str = "gguf-demo",
        hardware: HardwareInfo | None = None,
        *,
        stage: str | None = None,
    ):
        # Callers historically passed stage-like names ("baseline_evaluation"); keep
        # that as a tag and force the visible experiment to MLFLOW_EXPERIMENT_NAME.
        self.stage = stage or experiment_name
        self.experiment_name = os.getenv("MLFLOW_EXPERIMENT_NAME", "gguf-demo")
        self.hardware = hardware or detect_hardware()
        self.metrics_store = MetricsStore()
        self._mlflow_ok = False

        tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
        mlflow.set_tracking_uri(tracking_uri)

        _ensure_prometheus_http()

        CUDA_AVAILABLE.set(1.0 if self.hardware.cuda_available else 0.0)
        CUDA_DEVICE_COUNT.set(float(self.hardware.cuda_device_count))
        logger.info(
            "Tracking stage=%s experiment=%s uri=%s | %s",
            self.stage,
            self.experiment_name,
            tracking_uri,
            self.hardware.summary(),
        )

        try:
            exp = mlflow.get_experiment_by_name(self.experiment_name)
            if exp is None:
                self.experiment_id = mlflow.create_experiment(self.experiment_name)
            else:
                self.experiment_id = exp.experiment_id
            mlflow.set_experiment(self.experiment_name)
            # GenAI UI reads traces from the active experiment
            if hasattr(mlflow, "tracing") and hasattr(mlflow.tracing, "enable"):
                mlflow.tracing.enable()
            self._mlflow_ok = True
            logger.info(
                "MLflow ready: experiment=%s id=%s — GenAI traces + Model Training runs "
                "(http://localhost:5000 → GenAI → %s)",
                self.experiment_name,
                self.experiment_id,
                self.experiment_name,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("MLflow unavailable (%s) — continuing with Prometheus/Postgres only", exc)
            self.experiment_id = None
            self._mlflow_ok = False

    def log_evaluation(
        self,
        approach: str,
        question: str,
        response: str,
        metrics: Dict[str, float],
        params: Dict[str, Any] | None = None,
        model_name: str | None = None,
        context: str | None = None,
    ) -> None:
        """Log one Q&A evaluation to MLflow (trace + run), Prometheus, and Postgres."""
        device = self.hardware.device
        EVALUATION_REQUESTS.labels(device=device, approach=approach).inc()

        merged = dict(metrics)
        merged.update(self.hardware.as_metrics())
        quality_score = self._calculate_quality_score(merged)
        merged["quality_score"] = quality_score
        numeric = _numeric_metrics(merged)

        RESPONSE_QUALITY.labels(device=device).set(quality_score)
        if "domain_relevance" in merged:
            DOMAIN_RELEVANCE.labels(device=device).set(merged["domain_relevance"])
        if "context_utilization" in merged:
            CONTEXT_UTILIZATION.labels(device=device).set(merged["context_utilization"])
        if "retrieval_hit_at_k" in merged:
            RETRIEVAL_HIT.labels(device=device).set(merged["retrieval_hit_at_k"])
        if "faithfulness" in merged:
            FAITHFULNESS.labels(device=device).set(merged["faithfulness"])
        if "generation_time" in merged or "time_to_response" in merged:
            duration = merged.get("time_to_response") or merged.get("generation_time")
            if duration is not None:
                EVALUATION_DURATION.labels(device=device, approach=approach).observe(duration)

        if self._mlflow_ok and self.experiment_id is not None:
            self._log_genai_trace(
                approach=approach,
                question=question,
                response=response,
                context=context,
                numeric=numeric,
                quality_score=quality_score,
                model_name=model_name,
            )
            self._log_training_run(
                approach=approach,
                question=question,
                response=response,
                numeric=numeric,
                params=params,
                model_name=model_name,
            )
        else:
            logger.debug("Skipping MLflow write (not connected)")

        self.metrics_store.insert(
            approach=approach,
            question=question,
            response=response,
            metrics=merged,
            device=device,
            cuda_available=self.hardware.cuda_available,
            model_name=model_name,
        )

    def _log_genai_trace(
        self,
        *,
        approach: str,
        question: str,
        response: str,
        context: str | None,
        numeric: Dict[str, float],
        quality_score: float,
        model_name: str | None,
    ) -> None:
        """Emit an OpenTelemetry-style trace for the GenAI Experiments UI."""
        try:
            with mlflow.start_span(name=f"eval.{approach}", span_type=SpanType.CHAIN) as root:
                root.set_inputs(
                    {
                        "question": question,
                        "approach": approach,
                        "stage": self.stage,
                        "device": self.hardware.device,
                    }
                )
                root.set_attributes(
                    {
                        "stage": self.stage,
                        "approach": approach,
                        "device": self.hardware.device,
                        "cuda_available": str(self.hardware.cuda_available),
                        "model_name": model_name or "",
                        "quality_score": quality_score,
                    }
                )

                if context:
                    with mlflow.start_span(name="retrieve", span_type=SpanType.RETRIEVER) as ret:
                        ret.set_inputs({"query": question})
                        ret.set_outputs(
                            {
                                "context_preview": context[:2000],
                                "context_chars": float(len(context)),
                            }
                        )

                with mlflow.start_span(name="generate", span_type=SpanType.LLM) as gen:
                    gen.set_inputs(
                        {
                            "question": question,
                            "has_context": bool(context),
                            "model_name": model_name or "",
                        }
                    )
                    gen.set_outputs({"response": response})
                    if "generation_time" in numeric:
                        gen.set_attributes({"generation_time": numeric["generation_time"]})

                with mlflow.start_span(name="score", span_type=SpanType.TOOL) as score:
                    score.set_inputs({"metric_names": sorted(numeric.keys())})
                    score.set_outputs(numeric)

                highlight = {
                    k: numeric[k]
                    for k in (
                        "quality_score",
                        "rougeL",
                        "bert_score",
                        "faithfulness",
                        "retrieval_hit_at_k",
                        "time_to_response",
                    )
                    if k in numeric
                }
                root.set_outputs({"response": response, **highlight})
        except Exception as exc:  # noqa: BLE001
            logger.error("MLflow GenAI trace failed: %s", exc)

    def _log_training_run(
        self,
        *,
        approach: str,
        question: str,
        response: str,
        numeric: Dict[str, float],
        params: Dict[str, Any] | None,
        model_name: str | None,
    ) -> None:
        """Classic run for the Model Training UI toggle."""
        try:
            with mlflow.start_run(experiment_id=self.experiment_id):
                mlflow.set_tag("stage", self.stage)
                mlflow.set_tag("approach", approach)
                mlflow.set_tag("question", question[:100])
                mlflow.set_tag("device", self.hardware.device)
                mlflow.set_tag("cuda_available", str(self.hardware.cuda_available))
                mlflow.set_tag("mlflow.ui.mode", "model_training")
                if self.hardware.cuda_device_name:
                    mlflow.set_tag("cuda_device_name", self.hardware.cuda_device_name)

                run_params = {**(params or {}), **self.hardware.as_params()}
                if model_name:
                    run_params["model_name"] = model_name
                mlflow.log_params({str(k)[:250]: str(v)[:250] for k, v in run_params.items()})
                mlflow.log_metrics(numeric)

                with tempfile.TemporaryDirectory() as tmp:
                    artifact_path = os.path.join(tmp, "response.txt")
                    with open(artifact_path, "w", encoding="utf-8") as f:
                        f.write(
                            f"Device: {self.hardware.summary()}\n"
                            f"Stage: {self.stage}\n"
                            f"Approach: {approach}\n"
                            f"Question: {question}\n\n"
                            f"Response: {response}\n"
                        )
                    mlflow.log_artifact(artifact_path)
        except Exception as exc:  # noqa: BLE001
            logger.error("MLflow Model Training run failed: %s", exc)

    def _calculate_quality_score(self, metrics: Dict[str, float]) -> float:
        """
        Weighted blend of available metrics into a single 0–1 score for Grafana.

        Reference / RAG metrics dominate. Heuristics are lightly weighted.
        """
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
            "factual_density": 0.0,
            "technical_accuracy": 0.0,
        }

        score = 0.0
        total_weight = 0.0
        for metric, weight in weights.items():
            if weight <= 0:
                continue
            if metric in metrics:
                score += metrics[metric] * weight
                total_weight += weight

        return score / total_weight if total_weight > 0 else 0.0
