"""
Experiment tracking (MLflow), operational metrics (Prometheus), and Postgres persistence.

Every evaluation script calls MLflowTracker.log_evaluation() so runs appear at
http://localhost:5000. Prometheus scrapes :8000/metrics. Rows also land in
evaluation_metrics for Grafana SQL panels.

CUDA vs CPU is tagged on every run so you can compare generation_time by device.
"""

from __future__ import annotations

import logging
import os
import tempfile
from typing import Any, Dict

import mlflow
from prometheus_client import Counter, Gauge, Histogram, start_http_server

from src.hardware import HardwareInfo, detect_hardware
from src.metrics_store import MetricsStore

logger = logging.getLogger(__name__)

# Prometheus instruments — scraped by the prometheus service in docker-compose
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
)
DOMAIN_RELEVANCE = Gauge("domain_relevance_score", "Domain relevance score", ["device"])
CONTEXT_UTILIZATION = Gauge(
    "context_utilization_score", "Context utilization score", ["device"]
)
CUDA_AVAILABLE = Gauge("cuda_available", "1 if CUDA is available, else 0")
CUDA_DEVICE_COUNT = Gauge("cuda_device_count", "Number of CUDA devices")
RETRIEVAL_HIT = Gauge("retrieval_hit_at_k", "Retrieval hit@k for last RAG eval", ["device"])
FAITHFULNESS = Gauge("faithfulness_score", "Faithfulness proxy for last RAG eval", ["device"])


class MLflowTracker:
    """Dual-write evaluation results to MLflow, Prometheus, and Postgres."""

    def __init__(
        self,
        experiment_name: str = "rag_evaluation",
        hardware: HardwareInfo | None = None,
    ):
        self.experiment_name = experiment_name
        self.hardware = hardware or detect_hardware()
        self.metrics_store = MetricsStore()

        mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000"))

        try:
            start_http_server(8000)
            logger.info("Prometheus metrics server listening on :8000")
        except OSError:
            logger.warning("Prometheus metrics server already running on :8000")

        # Publish static hardware gauges once per process
        CUDA_AVAILABLE.set(1.0 if self.hardware.cuda_available else 0.0)
        CUDA_DEVICE_COUNT.set(float(self.hardware.cuda_device_count))
        logger.info("Tracking with %s", self.hardware.summary())

        try:
            self.experiment_id = mlflow.create_experiment(experiment_name)
        except mlflow.exceptions.MlflowException:
            experiment = mlflow.get_experiment_by_name(experiment_name)
            self.experiment_id = experiment.experiment_id

        mlflow.set_experiment(experiment_name)

    def log_evaluation(
        self,
        approach: str,
        question: str,
        response: str,
        metrics: Dict[str, float],
        params: Dict[str, Any] | None = None,
        model_name: str | None = None,
    ) -> None:
        """Log one Q&A evaluation to MLflow, Prometheus, and Postgres."""
        device = self.hardware.device
        EVALUATION_REQUESTS.labels(device=device, approach=approach).inc()

        # Merge CUDA flags into metrics so charts split CUDA vs CPU cleanly
        merged = dict(metrics)
        merged.update(self.hardware.as_metrics())

        quality_score = self._calculate_quality_score(merged)
        merged["quality_score"] = quality_score

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

        with mlflow.start_run(experiment_id=self.experiment_id):
            mlflow.set_tag("approach", approach)
            mlflow.set_tag("question", question[:100])
            mlflow.set_tag("device", device)
            mlflow.set_tag("cuda_available", str(self.hardware.cuda_available))
            if self.hardware.cuda_device_name:
                mlflow.set_tag("cuda_device_name", self.hardware.cuda_device_name)

            run_params = {**(params or {}), **self.hardware.as_params()}
            if model_name:
                run_params["model_name"] = model_name
            mlflow.log_params({k: str(v) for k, v in run_params.items()})

            mlflow.log_metrics(merged)

            with tempfile.TemporaryDirectory() as tmp:
                artifact_path = os.path.join(tmp, "response.txt")
                with open(artifact_path, "w", encoding="utf-8") as f:
                    f.write(
                        f"Device: {self.hardware.summary()}\n"
                        f"Approach: {approach}\n"
                        f"Question: {question}\n\n"
                        f"Response: {response}\n"
                    )
                mlflow.log_artifact(artifact_path)

        self.metrics_store.insert(
            approach=approach,
            question=question,
            response=response,
            metrics=merged,
            device=device,
            cuda_available=self.hardware.cuda_available,
            model_name=model_name,
        )

    def _calculate_quality_score(self, metrics: Dict[str, float]) -> float:
        """
        Weighted blend of available metrics into a single 0–1 score for Grafana.

        Reference / RAG metrics dominate. Heuristics (domain_relevance, coherence,
        factual_density, technical_accuracy) are lightly weighted — diagnostic only.
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
            # Heuristics — small so they don't swamp reference metrics
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
