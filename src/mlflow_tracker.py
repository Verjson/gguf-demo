"""
Experiment tracking (MLflow), operational metrics (Prometheus), and Postgres persistence.

MLflow layout (one parent evaluation run per stage×device):

  Experiment: gguf-demo
  └── Evaluation run  (e.g. baseline@cuda)
      ├── Aggregated metrics + registry lineage tags
      └── Traces (one per question; live retrieve/generate spans)
           └── Assessments (rougeL, faithfulness, quality_score, …)

Prometheus scrapes the persistent metrics server on app:8000. Rows also land in
evaluation_metrics for Grafana SQL panels.
"""

from __future__ import annotations

import logging
import os
import tempfile
from contextlib import contextmanager
from typing import Any, Dict, Iterator, List

import mlflow
from prometheus_client import Counter, Gauge, Histogram, start_http_server

from src.hardware import HardwareInfo, detect_hardware
from src.metrics_store import MetricsStore
from src.resource_metrics import percentile

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

# Metrics surfaced as GenAI assessments (skip bulky hardware gauges).
_ASSESSMENT_KEYS = (
    "quality_score",
    "rouge1",
    "rouge2",
    "rougeL",
    "bert_score",
    "faithfulness",
    "retrieval_hit_at_k",
    "judge_groundedness",
    "answer_relevancy",
    "domain_relevance",
    "context_utilization",
    "coherence",
    "factual_density",
    "technical_accuracy",
    "generation_time",
    "retrieval_time",
    "time_to_response",
    "speed_chars_per_sec",
    "prompt_chars",
    "response_chars",
    "prompt_tokens",
    "completion_tokens",
    "tokens_per_sec",
    "context_chars",
    "n_chunks_retrieved",
    "cuda_used",
)

_PERCENTILE_METRIC_KEYS = (
    "time_to_response",
    "generation_time",
    "retrieval_time",
)


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


def calculate_quality_score(metrics: Dict[str, float]) -> float:
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


class MLflowTracker:
    """
    Parent evaluation run + GenAI assessments + Prometheus/Postgres.

    Use ``stage_run()`` around a batch of questions, then ``log_evaluation()``
    (or ``eval_runner``) so traces nest under one run and scores become assessments.
    """

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
        self._parent_run_id: str | None = None
        self._question_metrics: List[Dict[str, float]] = []
        self._lineage: Dict[str, str] = {}

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
            if hasattr(mlflow, "tracing") and hasattr(mlflow.tracing, "enable"):
                mlflow.tracing.enable()
            self._mlflow_ok = True
            logger.info(
                "MLflow ready: experiment=%s id=%s — parent runs + GenAI traces "
                "(http://localhost:5000 → GenAI → %s)",
                self.experiment_name,
                self.experiment_id,
                self.experiment_name,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("MLflow unavailable (%s) — continuing with Prometheus/Postgres only", exc)
            self.experiment_id = None
            self._mlflow_ok = False

    def log_run_metrics(self, metrics: dict[str, Any] | None) -> None:
        """Log numeric metrics on the active parent run (not per-question averages)."""
        numeric = _numeric_metrics(metrics or {})
        if not numeric or not self._mlflow_ok or not mlflow.active_run():
            return
        try:
            mlflow.log_metrics(numeric)
        except Exception as exc:  # noqa: BLE001
            logger.debug("log_run_metrics failed: %s", exc)

    @contextmanager
    def stage_run(
        self,
        approach: str,
        *,
        params: Dict[str, Any] | None = None,
        lineage: Dict[str, str] | None = None,
        model_name: str | None = None,
        run_name: str | None = None,
    ) -> Iterator["MLflowTracker"]:
        """
        One classic Model Training run for the whole stage; traces nest under it.

        ``mlflow.genai.evaluate`` reuses this active run when called inside the block.
        """
        self._question_metrics = []
        self._lineage = dict(lineage or {})
        name = run_name or f"{approach}@{self.hardware.device}"

        if not self._mlflow_ok or self.experiment_id is None:
            logger.warning("stage_run without MLflow — ops metrics only")
            try:
                yield self
            finally:
                self._parent_run_id = None
            return

        with mlflow.start_run(experiment_id=self.experiment_id, run_name=name) as run:
            self._parent_run_id = run.info.run_id
            mlflow.set_tag("stage", self.stage)
            mlflow.set_tag("approach", approach)
            mlflow.set_tag("device", self.hardware.device)
            mlflow.set_tag("cuda_available", str(self.hardware.cuda_available))
            mlflow.set_tag("mlflow.ui.mode", "evaluation_parent")
            if self.hardware.cuda_device_name:
                mlflow.set_tag("cuda_device_name", self.hardware.cuda_device_name)
            if model_name:
                mlflow.set_tag("model_name", model_name)

            for key, value in self._lineage.items():
                if value is not None and str(value):
                    mlflow.set_tag(key, str(value)[:250])

            # Link LoggedModel / registry when possible (MLflow 3)
            reg = self._lineage.get("registered_model")
            ver = self._lineage.get("model_version")
            if reg and ver and ver not in {"", "unregistered"}:
                try:
                    mlflow.set_active_model(name=f"{reg}/{ver}")
                except Exception as exc:  # noqa: BLE001
                    logger.debug("set_active_model skipped: %s", exc)

            run_params = {**(params or {}), **self.hardware.as_params()}
            if model_name:
                run_params["model_name"] = model_name
            for key, value in self._lineage.items():
                run_params[f"lineage_{key}"] = value
            mlflow.log_params({str(k)[:250]: str(v)[:250] for k, v in run_params.items()})

            try:
                yield self
            finally:
                self._log_parent_aggregates()
                self._parent_run_id = None

    def log_evaluation(
        self,
        approach: str,
        question: str,
        response: str,
        metrics: Dict[str, float],
        params: Dict[str, Any] | None = None,
        model_name: str | None = None,
        context: str | None = None,
        *,
        skip_assessments: bool = False,
    ) -> None:
        """
        Log one Q&A to Prometheus, Postgres, and (when under a parent run) GenAI assessments.

        Does **not** create a new classic run per question. Live retrieve/generate spans
        come from ``RAGPipeline``; this method attaches scores as feedback on the last trace.
        """
        device = self.hardware.device
        EVALUATION_REQUESTS.labels(device=device, approach=approach).inc()

        merged = dict(metrics)
        merged.update(self.hardware.as_metrics())
        quality_score = calculate_quality_score(merged)
        merged["quality_score"] = quality_score
        numeric = _numeric_metrics(merged)
        self._question_metrics.append(numeric)

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

        if self._mlflow_ok:
            if not skip_assessments:
                self._attach_trace_assessments(
                    approach=approach,
                    question=question,
                    response=response,
                    context=context,
                    numeric=numeric,
                    quality_score=quality_score,
                    model_name=model_name,
                )
            # Single-question CLI without stage_run: still open a short parent
            if self._parent_run_id is None:
                self._log_orphan_parent_snapshot(
                    approach=approach,
                    question=question,
                    response=response,
                    numeric=numeric,
                    params=params,
                    model_name=model_name,
                )

        self.metrics_store.insert(
            approach=approach,
            question=question,
            response=response,
            metrics=merged,
            device=device,
            cuda_available=self.hardware.cuda_available,
            model_name=model_name,
        )

    def record_row_metrics(self, metrics: Dict[str, float]) -> None:
        """Append numeric metrics for parent-run aggregation (used by eval_runner)."""
        numeric = _numeric_metrics(metrics)
        if "quality_score" not in numeric:
            numeric["quality_score"] = calculate_quality_score(numeric)
        self._question_metrics.append(numeric)

    def _resolve_trace_id(self) -> str | None:
        """Prefer the in-progress root span's id (needed for buffered assessments)."""
        try:
            span = mlflow.get_current_active_span()
            if span is not None and getattr(span, "trace_id", None):
                return str(span.trace_id)
        except Exception:  # noqa: BLE001
            pass
        try:
            return mlflow.get_last_active_trace_id()
        except Exception:  # noqa: BLE001
            return None

    def _attach_trace_assessments(
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
        try:
            trace_id = self._resolve_trace_id()
            tags = {
                "stage": self.stage,
                "approach": approach,
                "device": self.hardware.device,
                "question_preview": question[:120],
            }
            if model_name:
                tags["model_name"] = model_name
            for key, value in self._lineage.items():
                if value:
                    tags[key] = str(value)[:250]

            if hasattr(mlflow, "update_current_trace"):
                try:
                    mlflow.update_current_trace(
                        tags=tags,
                        request_preview=question[:200],
                        response_preview=response[:200],
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.debug("update_current_trace: %s", exc)
                    if trace_id:
                        try:
                            client = mlflow.MlflowClient()
                            for k, v in tags.items():
                                client.set_trace_tag(trace_id, k, str(v)[:250])
                        except Exception as tag_exc:  # noqa: BLE001
                            logger.debug("set_trace_tag: %s", tag_exc)

            if not trace_id:
                logger.debug("No trace id — assessments skipped")
                return

            for key in _ASSESSMENT_KEYS:
                if key not in numeric:
                    continue
                try:
                    mlflow.log_feedback(
                        trace_id=trace_id,
                        name=key,
                        value=float(numeric[key]),
                        rationale=f"stage={self.stage} approach={approach}",
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.debug("log_feedback %s failed: %s", key, exc)
        except Exception as exc:  # noqa: BLE001
            logger.error("Trace assessment attach failed: %s", exc)

    def _log_orphan_parent_snapshot(
        self,
        *,
        approach: str,
        question: str,
        response: str,
        numeric: Dict[str, float],
        params: Dict[str, Any] | None,
        model_name: str | None,
    ) -> None:
        """One-off query without ``stage_run``: single parent run for that Q&A."""
        try:
            with mlflow.start_run(
                experiment_id=self.experiment_id,
                run_name=f"{approach}@{self.hardware.device}-adhoc",
            ):
                mlflow.set_tag("stage", self.stage)
                mlflow.set_tag("approach", approach)
                mlflow.set_tag("device", self.hardware.device)
                mlflow.set_tag("question", question[:100])
                mlflow.set_tag("adhoc", "true")
                run_params = {**(params or {}), **self.hardware.as_params()}
                if model_name:
                    run_params["model_name"] = model_name
                mlflow.log_params({str(k)[:250]: str(v)[:250] for k, v in run_params.items()})
                mlflow.log_metrics(numeric)
                with tempfile.TemporaryDirectory() as tmp:
                    path = os.path.join(tmp, "response.txt")
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(f"Question: {question}\n\nResponse: {response}\n")
                    mlflow.log_artifact(path)
        except Exception as exc:  # noqa: BLE001
            logger.error("Ad-hoc parent run failed: %s", exc)

    def _log_parent_aggregates(self) -> None:
        if not self._question_metrics or not mlflow.active_run():
            return
        keys: set[str] = set()
        for row in self._question_metrics:
            keys.update(row.keys())
        aggregates: Dict[str, float] = {}
        for key in sorted(keys):
            values = [row[key] for row in self._question_metrics if key in row]
            if values:
                aggregates[key] = sum(values) / len(values)
        try:
            mlflow.log_metrics(aggregates)
            mlflow.log_metric("n_questions", float(len(self._question_metrics)))
            for key in _PERCENTILE_METRIC_KEYS:
                values = [row[key] for row in self._question_metrics if key in row]
                if values:
                    mlflow.log_metric(f"{key}_p50", percentile(values, 50))
                    mlflow.log_metric(f"{key}_p95", percentile(values, 95))
            logger.info(
                "Parent run aggregates (%d questions): quality_score=%.4f rougeL=%s",
                len(self._question_metrics),
                aggregates.get("quality_score", 0.0),
                f"{aggregates['rougeL']:.4f}" if "rougeL" in aggregates else "n/a",
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to log parent aggregates: %s", exc)

    def _calculate_quality_score(self, metrics: Dict[str, float]) -> float:
        """Back-compat alias for older callers."""
        return calculate_quality_score(metrics)


def init_mlflow_experiment() -> bool:
    """Point the process at the shared gguf-demo experiment. Returns False if unreachable."""
    try:
        mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000"))
        name = os.getenv("MLFLOW_EXPERIMENT_NAME", "gguf-demo")
        mlflow.set_experiment(name)
        if hasattr(mlflow, "tracing") and hasattr(mlflow.tracing, "enable"):
            mlflow.tracing.enable()
        return True
    except Exception as exc:  # noqa: BLE001
        logger.warning("MLflow init failed: %s", exc)
        return False


def optional_mlflow_run(run_name: str):
    """Return ``mlflow.start_run`` or a no-op context if tracking is down."""
    from contextlib import nullcontext

    if not init_mlflow_experiment():
        return nullcontext()
    try:
        return mlflow.start_run(run_name=run_name)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not open MLflow run %s: %s", run_name, exc)
        return nullcontext()
