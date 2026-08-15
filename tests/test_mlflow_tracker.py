from __future__ import annotations

from prometheus_client import generate_latest

from src.hardware import HardwareInfo
from src.mlflow_tracker import MLflowTracker, _source_revision_tags


class _RunStore:
    def __init__(self):
        self.finished = []
        self.inserted = []

    def finish_run(self, **values):
        self.finished.append(values)

    def insert(self, **values):
        self.inserted.append(values)


def _hardware() -> HardwareInfo:
    return HardwareInfo(
        cuda_available=False,
        device="cpu",
        cuda_device_count=0,
        cuda_device_name=None,
        cuda_capability=None,
        torch_version="test",
        cuda_version=None,
        cpu_model="test",
        cpu_logical=2,
        cpu_threads=2,
    )


def _tracker(store: _RunStore) -> MLflowTracker:
    tracker = MLflowTracker.__new__(MLflowTracker)
    tracker.hardware = _hardware()
    tracker.metrics_store = store
    tracker._mlflow_ok = False
    tracker._parent_run_id = None
    tracker._question_metrics = []
    tracker._actual_devices = set()
    return tracker


def test_incomplete_stage_is_persisted_as_failed_and_raises():
    store = _RunStore()
    tracker = _tracker(store)
    tracker._question_metrics.append({"quality_score": 0.5})
    tracker._actual_devices.add("cpu")

    try:
        tracker._finish_pipeline_run(
            "2026-08-15_030000_cpu",
            "baseline",
            "completed",
            expected_samples=2,
        )
    except RuntimeError as exc:
        assert "1 of 2 expected samples" in str(exc)
    else:
        raise AssertionError("an incomplete stage was accepted as completed")

    assert store.finished == [
        {
            "run_id": "2026-08-15_030000_cpu",
            "approach": "baseline",
            "status": "failed",
            "recorded_samples": 1,
            "actual_device": "cpu",
            "error": "stage recorded 1 of 2 expected samples; a partial run cannot be marked completed",
        }
    ]


def test_evaluation_dual_write_uses_run_identity_in_prometheus_and_postgres(
    monkeypatch,
):
    run_id = "2099-12-31_235959_cpu"
    monkeypatch.setenv("RUN_ID", run_id)
    monkeypatch.setattr(
        "src.mlflow_tracker.memory_snapshot",
        lambda: {"rss_mb": 10.0, "peak_rss_mb": 12.0},
    )
    store = _RunStore()
    tracker = _tracker(store)

    tracker.log_evaluation(
        approach="baseline",
        question="duplicate text",
        response="answer",
        metrics={"generation_time": 1.5, "rougeL": 0.5},
        params={"runtime": "transformers", "weight_format": "safetensors"},
        model_name="model",
        sample_id="7",
    )

    assert store.inserted[0]["sample_id"] == "7"
    assert store.inserted[0]["approach"] == "baseline"
    metrics = generate_latest().decode()
    labels = f'approach="baseline",device="cpu",run_id="{run_id}"'
    assert f"evaluation_requests_total{{{labels}}} 1.0" in metrics
    assert f"evaluation_duration_seconds_count{{{labels}}} 1.0" in metrics


def test_source_revision_tags_are_explicit_even_outside_the_host_pipeline(monkeypatch):
    monkeypatch.delenv("SOURCE_GIT_SHA", raising=False)
    monkeypatch.delenv("SOURCE_GIT_DIRTY", raising=False)
    assert _source_revision_tags() == {
        "source_git_sha": "unknown",
        "source_git_dirty": "unknown",
    }

    monkeypatch.setenv("SOURCE_GIT_SHA", "abc123")
    monkeypatch.setenv("SOURCE_GIT_DIRTY", "false")
    assert _source_revision_tags() == {
        "source_git_sha": "abc123",
        "source_git_dirty": "false",
    }
