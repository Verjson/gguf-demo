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

from src.hardware import HardwareInfo, detect_hardware, device_for_row
from src.metrics_store import MetricsStore
from src.resource_metrics import memory_snapshot, percentile
from src.run_id import run_group_for

logger = logging.getLogger(__name__)

# Multiprocess directory shared with scripts/metrics_server.py
_MULTIPROC_DIR = os.environ.get("PROMETHEUS_MULTIPROC_DIR", "").strip()
if _MULTIPROC_DIR:
    os.makedirs(_MULTIPROC_DIR, exist_ok=True)

# Prometheus instruments — scraped by the prometheus service in docker-compose.
EVALUATION_REQUESTS = Counter(
    "evaluation_requests_total",
    "Total evaluation requests",
    ["run_id", "device", "approach"],
)
# Buckets sized to this workload, and they have to be stated.
#
# prometheus_client's defaults are built for HTTP handlers and stop at 10 seconds.
# A local Phi-3 answer takes 8 to 962 seconds here (measured across run
# 2026-08-14_181632: 8.2, 10.1, 28.7, 31.6, 45.8, 55.7, 302.5, 525.2, 761.6, 962.2),
# so every single observation landed in the +Inf overflow bucket. histogram_quantile
# has no interpolable range in that state and returns +Inf, which made the p50/p95
# panel on the Live Ops dashboard — the only latency panel there — permanently
# unable to show a number, and the same two queries are published in the README.
#
# The ladder runs from a fast GPU answer to well past the slowest CPU one, roughly
# 2.5x per step. Changing it changes the metric's series set, so old TSDB data for
# evaluation_duration_seconds is not comparable across this edit.
EVALUATION_DURATION_BUCKETS = (
    1.0, 2.5, 5.0, 10.0, 25.0, 50.0, 100.0, 250.0, 500.0, 1000.0, 2500.0, float("inf"),
)

EVALUATION_DURATION = Histogram(
    "evaluation_duration_seconds",
    "Evaluation / generation duration",
    ["run_id", "device", "approach"],
    buckets=EVALUATION_DURATION_BUCKETS,
)
RESPONSE_QUALITY = Gauge(
    "response_quality_score",
    "Overall response quality score",
    ["run_id", "device", "approach"],
    multiprocess_mode="livemostrecent",
)
DOMAIN_RELEVANCE = Gauge(
    "domain_relevance_score",
    "Domain relevance score",
    ["run_id", "device", "approach"],
    multiprocess_mode="livemostrecent",
)
CONTEXT_UTILIZATION = Gauge(
    "context_utilization_score",
    "Context utilization score",
    ["run_id", "device", "approach"],
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
CPU_THREADS = Gauge(
    "cpu_threads",
    "Thread budget configured for this process",
    multiprocess_mode="livemostrecent",
)
PEAK_RSS_MB = Gauge(
    "peak_rss_mb",
    "Peak resident set size in MiB",
    ["run_id", "device", "approach"],
    multiprocess_mode="livemostrecent",
)
RETRIEVAL_HIT = Gauge(
    "retrieval_hit_at_k",
    "Retrieval hit@k for last RAG eval",
    ["run_id", "device", "approach"],
    multiprocess_mode="livemostrecent",
)
FAITHFULNESS = Gauge(
    "faithfulness_score",
    "Faithfulness proxy for last RAG eval",
    ["run_id", "device", "approach"],
    multiprocess_mode="livemostrecent",
)
EVALUATION_RUN_COMPLETE = Gauge(
    "evaluation_run_complete",
    "1 when all samples reached required sinks, 0 while running or failed",
    ["run_id", "approach"],
    multiprocess_mode="livemostrecent",
)
EVALUATION_RUN_SAMPLES = Gauge(
    "evaluation_run_samples",
    "Expected and recorded samples for a pipeline stage",
    ["run_id", "approach", "kind"],
    multiprocess_mode="livemostrecent",
)

_PROMETHEUS_HTTP_STARTED = False


def _tracking_required() -> bool:
    return bool(os.getenv("RUN_ID")) or os.getenv("MLFLOW_STRICT", "").lower() in {
        "1",
        "true",
        "yes",
    }


def _source_revision_tags() -> dict[str, str]:
    """Source identity passed in by the host, which owns the Git checkout."""
    return {
        "source_git_sha": os.getenv("SOURCE_GIT_SHA", "unknown"),
        "source_git_dirty": os.getenv("SOURCE_GIT_DIRTY", "unknown"),
    }

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


#: The single definition of the blend. `genai_scorers` imports this rather than
#: keeping its own copy — the copy it used to keep had already drifted by two keys,
#: and a scoring function that exists twice is a scoring function that will disagree
#: with itself eventually.
QUALITY_WEIGHTS: Dict[str, float] = {
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

#: Metrics only a RAG approach can produce. Their absence from a baseline row is a
#: property of the approach, not a gap in the measurement, which is why the
#: denominator has to be fixed — see calculate_quality_score.
_RAG_ONLY_METRICS = frozenset({"retrieval_hit_at_k", "faithfulness", "context_utilization"})


def calculate_quality_score(metrics: Dict[str, float]) -> float:
    """
    Weighted blend of the available metrics into a single 0–1 score.

    The denominator is the **full** weight table, not the subset that happened to be
    present. That is the fix for a comparison the dashboards make on every panel:

      * a RAG row carries retrieval_hit_at_k (0.14) and faithfulness (0.14);
      * a baseline row carries neither, because there is no retrieval to score.

    Dividing by "weights I found" gave the baseline row a denominator 0.28 smaller and
    scaled its remaining metrics up to compensate, so baseline and RAG scores were on
    different scales — and dashboard 02 subtracts one from the other. Dividing by the
    full table instead means an absent metric contributes 0, which is the honest
    reading: an approach that does no retrieval earns no retrieval quality.

    The visible consequence is that baseline quality_score drops relative to before.
    That is the bug being removed, not a regression: the old number was inflated.
    Both are still 0–1, and `rougeL` remains the metric to use for "did RAG help?".
    """
    if not metrics:
        return 0.0

    score = 0.0
    for metric, weight in QUALITY_WEIGHTS.items():
        if weight > 0 and metric in metrics:
            score += float(metrics[metric]) * weight

    total_weight = sum(w for w in QUALITY_WEIGHTS.values() if w > 0)
    return score / total_weight if total_weight > 0 else 0.0


def quality_score_denominator(include_rag: bool) -> float:
    """
    The weight total a fully-scored row of this kind can reach.

    Reporting can use this to show quality_score as a fraction of what the approach
    was eligible for, when comparing a baseline against a RAG run head-to-head is the
    actual question rather than "which produced the better answer overall".
    """
    return sum(
        weight
        for metric, weight in QUALITY_WEIGHTS.items()
        if weight > 0 and (include_rag or metric not in _RAG_ONLY_METRICS)
    )


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
        self._actual_devices: set[str] = set()

        tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
        mlflow.set_tracking_uri(tracking_uri)

        _ensure_prometheus_http()

        CUDA_AVAILABLE.set(1.0 if self.hardware.cuda_available else 0.0)
        CUDA_DEVICE_COUNT.set(float(self.hardware.cuda_device_count))
        CPU_THREADS.set(float(self.hardware.cpu_threads))
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
            self.experiment_id = None
            self._mlflow_ok = False
            if _tracking_required():
                raise RuntimeError(f"MLflow is required for pipeline runs but unavailable: {exc}") from exc
            logger.error("MLflow unavailable (%s) — continuing with Prometheus/Postgres only", exc)

    def log_run_metrics(self, metrics: dict[str, Any] | None) -> None:
        """Log numeric metrics on the active parent run (not per-question averages)."""
        numeric = _numeric_metrics(metrics or {})
        if not numeric or not self._mlflow_ok or not mlflow.active_run():
            return
        try:
            mlflow.log_metrics(numeric)
        except Exception as exc:  # noqa: BLE001
            if _tracking_required():
                raise RuntimeError(f"MLflow metric write failed: {exc}") from exc
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
        self._actual_devices = set()
        self._lineage = dict(lineage or {})
        name = run_name or f"{approach}@{self.hardware.device}"
        pipeline_run_id = os.getenv("RUN_ID")
        expected_samples = int((params or {}).get("n_prompts") or 0)
        if pipeline_run_id:
            EVALUATION_RUN_COMPLETE.labels(run_id=pipeline_run_id, approach=approach).set(0)
            EVALUATION_RUN_SAMPLES.labels(
                run_id=pipeline_run_id, approach=approach, kind="expected"
            ).set(expected_samples)
            EVALUATION_RUN_SAMPLES.labels(
                run_id=pipeline_run_id, approach=approach, kind="recorded"
            ).set(0)

        if not self._mlflow_ok or self.experiment_id is None:
            logger.warning("stage_run without MLflow — ops metrics only")
            try:
                yield self
            finally:
                self._parent_run_id = None
            return

        with mlflow.start_run(experiment_id=self.experiment_id, run_name=name) as run:
            self._parent_run_id = run.info.run_id
            if pipeline_run_id:
                self.metrics_store.start_run(
                    run_id=pipeline_run_id,
                    approach=approach,
                    expected_samples=expected_samples,
                    requested_device=self.hardware.device,
                    runtime=str((params or {}).get("runtime") or "") or None,
                    weight_format=str((params or {}).get("weight_format") or "") or None,
                    model_name=model_name,
                    mlflow_run_id=self._parent_run_id,
                )
            mlflow.set_tag("stage", self.stage)
            mlflow.set_tag("approach", approach)
            mlflow.set_tag("device", self.hardware.device)
            if params:
                if params.get("runtime"):
                    mlflow.set_tag("runtime", str(params["runtime"]))
                if params.get("weight_format"):
                    mlflow.set_tag("weight_format", str(params["weight_format"]))
            mlflow.set_tag("cuda_available", str(self.hardware.cuda_available))
            mlflow.set_tag("mlflow.ui.mode", "evaluation_parent")
            for key, value in _source_revision_tags().items():
                mlflow.set_tag(key, value)
            # The third leg of the same story. Postgres rows carry RUN_ID, the results
            # folder is named after it and the dashboards filter on it — but the MLflow
            # run recorded stage/approach/device only, so with several runs a day on one
            # device there was no way back from a run in the UI to the rows or the
            # artifacts it produced.
            if pipeline_run_id:
                mlflow.set_tag("run_id", pipeline_run_id)
                mlflow.set_tag("run_group", run_group_for(pipeline_run_id) or "")
                mlflow.log_param("results_dir", f"results/runs/{pipeline_run_id}")
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
                self._log_parent_aggregates()
            except BaseException as exc:
                if pipeline_run_id:
                    self._finish_pipeline_run(
                        pipeline_run_id,
                        approach,
                        "failed",
                        str(exc),
                        expected_samples=expected_samples,
                    )
                raise
            else:
                if pipeline_run_id:
                    self._finish_pipeline_run(
                        pipeline_run_id,
                        approach,
                        "completed",
                        expected_samples=expected_samples,
                    )
            finally:
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
        sample_id: str | None = None,
    ) -> None:
        """
        Log one Q&A to Prometheus, Postgres, and (when under a parent run) GenAI assessments.

        Does **not** create a new classic run per question. Live retrieve/generate spans
        come from ``RAGPipeline``; this method attaches scores as feedback on the last trace.
        """
        merged = dict(metrics)
        merged.update(self.hardware.as_metrics())
        merged.update(memory_snapshot())

        # The device a row is labelled with is the device that generated the answer,
        # which is not always the device the process can see. On a CUDA 13 host the
        # GGUF engine runs on the CPU wheel with n_gpu_layers=0 while torch reports a
        # usable GPU, so trusting self.hardware.device here labelled a CPU run `cuda`
        # and made the Transformers-vs-GGUF dashboard a GPU-vs-CPU comparison in
        # disguise. The engine measured it; believe the engine.
        device = self._device_for_row(merged)
        self._actual_devices.add(device)
        run_id = os.getenv("RUN_ID") or "adhoc"
        prom_labels = {"run_id": run_id, "device": device, "approach": approach}
        EVALUATION_REQUESTS.labels(**prom_labels).inc()
        quality_score = calculate_quality_score(merged)
        merged["quality_score"] = quality_score
        numeric = _numeric_metrics(merged)
        self._question_metrics.append(numeric)

        RESPONSE_QUALITY.labels(**prom_labels).set(quality_score)
        if "domain_relevance" in merged:
            DOMAIN_RELEVANCE.labels(**prom_labels).set(merged["domain_relevance"])
        if "context_utilization" in merged:
            CONTEXT_UTILIZATION.labels(**prom_labels).set(merged["context_utilization"])
        if "retrieval_hit_at_k" in merged:
            RETRIEVAL_HIT.labels(**prom_labels).set(merged["retrieval_hit_at_k"])
        if "faithfulness" in merged:
            FAITHFULNESS.labels(**prom_labels).set(merged["faithfulness"])
        if "generation_time" in merged or "time_to_response" in merged:
            duration = merged.get("time_to_response") or merged.get("generation_time")
            if duration is not None:
                EVALUATION_DURATION.labels(**prom_labels).observe(duration)
        if "peak_rss_mb" in merged:
            PEAK_RSS_MB.labels(**prom_labels).set(merged["peak_rss_mb"])

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
            runtime=str((params or {}).get("runtime") or "") or None,
            weight_format=str((params or {}).get("weight_format") or "") or None,
            sample_id=sample_id,
        )

    def _finish_pipeline_run(
        self,
        run_id: str,
        approach: str,
        status: str,
        error: str | None = None,
        *,
        expected_samples: int | None = None,
    ) -> None:
        if len(self._actual_devices) > 1:
            actual_device = "mixed"
        else:
            actual_device = next(iter(self._actual_devices), None)
        recorded = len(self._question_metrics)
        incomplete = (
            status == "completed"
            and expected_samples is not None
            and recorded != expected_samples
        )
        if incomplete:
            status = "failed"
            error = (
                f"stage recorded {recorded} of {expected_samples} expected samples; "
                "a partial run cannot be marked completed"
            )
        self.metrics_store.finish_run(
            run_id=run_id,
            approach=approach,
            status=status,
            recorded_samples=recorded,
            actual_device=actual_device,
            error=error[:2000] if error else None,
        )
        EVALUATION_RUN_SAMPLES.labels(
            run_id=run_id, approach=approach, kind="recorded"
        ).set(recorded)
        EVALUATION_RUN_COMPLETE.labels(run_id=run_id, approach=approach).set(
            1 if status == "completed" else 0
        )
        if incomplete:
            raise RuntimeError(error)

    def _device_for_row(self, merged: Dict[str, float]) -> str:
        """The device this row belongs to; see ``src.hardware.device_for_row``."""
        return device_for_row(merged.get("cuda_used"), self.hardware.device)

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
            if _tracking_required():
                raise RuntimeError(f"MLflow parent aggregate write failed: {exc}") from exc
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


@contextmanager
def optional_mlflow_run(run_name: str):
    """Open a run when available; pipeline runs fail if required tracking is down."""
    from contextlib import nullcontext

    if not init_mlflow_experiment():
        if _tracking_required():
            raise RuntimeError(f"MLflow is required for pipeline run {os.getenv('RUN_ID')}")
        with nullcontext() as run:
            yield run
        return
    try:
        run_context = mlflow.start_run(run_name=run_name)
    except Exception as exc:  # noqa: BLE001
        if _tracking_required():
            raise
        logger.warning("Could not open MLflow run %s: %s", run_name, exc)
        with nullcontext() as run:
            yield run
        return
    with run_context as run:
        run_id = os.getenv("RUN_ID")
        if run_id:
            mlflow.set_tag("run_id", run_id)
            mlflow.set_tag("run_group", run_group_for(run_id) or "")
        for key, value in _source_revision_tags().items():
            mlflow.set_tag(key, value)
        yield run
