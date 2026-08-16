"""Export helpers: run-id scope and hardware stamping (results/latest/ lives in test_snapshot)."""

from __future__ import annotations

import json

from src.hardware import HardwareInfo
from src.run_results import (
    _hardware_for_run,
    _prompt_snapshot_source,
    _run_scope,
    _stamp_copied_json,
)


def _hw(**overrides) -> HardwareInfo:
    base = {
        "cuda_available": True,
        "device": "cuda",
        "cuda_device_count": 1,
        "cuda_device_name": "RTX 4080",
        "cuda_capability": "8.9",
        "torch_version": "2.13.0",
        "cuda_version": "13.0",
        "cpu_model": "Intel i9",
        "cpu_logical": 32,
        "cpu_threads": 28,
    }
    base.update(overrides)
    return HardwareInfo(**base)


def test_run_scope_parses_pipeline_ids():
    device, started = _run_scope("2026-08-14_032911_cpu")
    assert device == "cpu"
    assert started is not None
    assert started.year == 2026
    device, started = _run_scope("2026-08-14_032911_cuda")
    assert device == "cuda"
    device, started = _run_scope("adhoc")
    assert device is None
    assert started is None


def test_hardware_for_run_cpu_overrides_visible_gpu():
    params = _hardware_for_run(_hw(), "cpu")
    assert params["device"] == "cpu"
    assert params["cuda_available"] is False
    assert params["cuda_device_name"] == "none"
    assert params["cpu_threads"] == 28
    assert params["cpu_model"] == "Intel i9"


def test_hardware_for_run_keeps_gpu_when_exporting_cuda():
    params = _hardware_for_run(_hw(), "cuda")
    assert params["device"] == "cuda"
    assert params["cuda_device_name"] == "RTX 4080"


def test_stamp_copied_json_overwrites_hardware_and_collects_resources(tmp_path):
    run_dir = tmp_path
    payload = {
        "hardware": {"device": "cuda", "cuda_device_name": "RTX 4080"},
        "resources": {"peak_rss_mb": 9600.0, "model_load_seconds": 12.5},
        "aggregate": {},
    }
    (run_dir / "baseline_results.json").write_text(json.dumps(payload), encoding="utf-8")
    hw = {"device": "cpu", "cpu_threads": 28, "cuda_device_name": "none"}
    resources = _stamp_copied_json(run_dir, hw)
    written = json.loads((run_dir / "baseline_results.json").read_text(encoding="utf-8"))
    assert written["hardware"]["device"] == "cpu"
    assert resources["peak_rss_mb"] == 9600.0


def test_prompt_snapshot_prefers_generated_runtime_data(tmp_path, monkeypatch):
    monkeypatch.delenv("PROMPTS_PATH", raising=False)
    processed_dir = tmp_path / "data" / "processed"
    processed_dir.mkdir(parents=True)
    generated = processed_dir / "evaluation_prompts.txt"
    generated.write_text("generated", encoding="utf-8")

    assert _prompt_snapshot_source(tmp_path, processed_dir) == generated


def test_prompt_snapshot_honors_configured_path(tmp_path, monkeypatch):
    configured = tmp_path / "custom" / "evaluation_prompts.txt"
    monkeypatch.setenv("PROMPTS_PATH", str(configured))

    assert _prompt_snapshot_source(tmp_path, tmp_path / "data" / "processed") == configured
