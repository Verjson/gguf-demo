"""Unit tests for runtime names, engine registry, and tracking params."""

import sys
from pathlib import Path
from types import SimpleNamespace

from src.latency import llm_run_params
from src.llm import gguf_engine
from src.llm.factory import build_engine, register_engine, registered_runtimes
from src.llm.port import DecodeSettings, GenerationResult
from src.llm.runtime import (
    RUNTIME_GGUF,
    RUNTIME_TRANSFORMERS,
    approach_for_runtime,
    llm_tracking_params,
    resolve_runtime,
)
from src.llm.transformers_engine import _model_load_kwargs


def test_gguf_tokenizer_uses_the_reviewed_transformers_revision(monkeypatch):
    calls = []
    monkeypatch.setitem(sys.modules, "llama_cpp", SimpleNamespace(Llama=lambda **kwargs: object()))
    monkeypatch.setattr(gguf_engine, "resolve_gguf_path", lambda config: Path("model.gguf"))
    monkeypatch.setattr(gguf_engine, "_n_gpu_layers", lambda config, hardware: 0)
    monkeypatch.setattr(
        gguf_engine,
        "load_instruct_tokenizer",
        lambda model_id, **kwargs: calls.append((model_id, kwargs)) or object(),
    )
    config = {
        "llm": {"model": "org/model", "revision": "reviewed-sha"},
        "gguf": {
            "repo_id": "org/gguf",
            "filename": "model.gguf",
            "n_ctx": 128,
            "n_threads": 1,
            "n_threads_batch": 1,
            "n_gpu_layers": 0,
        },
    }

    gguf_engine.GgufEngine.load(config, _hardware())

    assert calls == [("org/model", {"revision": "reviewed-sha"})]


def _hardware():
    from src.hardware import HardwareInfo

    return HardwareInfo(
        cuda_available=False,
        device="cpu",
        cuda_device_count=0,
        cuda_device_name=None,
        cuda_capability=None,
        torch_version="0",
        cuda_version=None,
        cpu_model="test",
        cpu_logical=1,
        cpu_threads=1,
    )


def test_fine_tune_base_revision_overrides_the_inference_revision():
    kwargs = _model_load_kwargs(
        {"llm": {"revision": "inference-sha"}},
        _hardware(),
        revision="training-base-sha",
    )
    assert kwargs["revision"] == "training-base-sha"


def test_resolve_runtime_default():
    assert resolve_runtime({}) == RUNTIME_TRANSFORMERS


def test_resolve_runtime_env(monkeypatch):
    monkeypatch.setenv("LLM_RUNTIME", "gguf")
    assert resolve_runtime({}) == RUNTIME_GGUF
    monkeypatch.delenv("LLM_RUNTIME")


def test_approach_suffix():
    assert approach_for_runtime("baseline", "transformers") == "baseline"
    assert approach_for_runtime("baseline", "gguf") == "baseline_gguf"
    assert approach_for_runtime("rag_gguf", "gguf") == "rag_gguf"


def test_llm_tracking_params_include_gguf(monkeypatch):
    monkeypatch.setenv("LLM_RUNTIME", "gguf")
    params = llm_tracking_params({"llm": {"max_new_tokens": 128}})
    assert params["runtime"] == "gguf"
    assert params["weight_format"] == "gguf"
    assert "Phi-3-mini-4k-instruct-q4.gguf" in params["gguf_filename"]
    monkeypatch.delenv("LLM_RUNTIME")
    tf = llm_run_params({"llm": {"max_new_tokens": 128, "cpu_dtype": "bfloat16"}})
    assert tf["runtime"] == "transformers"
    assert tf["max_new_tokens"] == 128


def test_register_engine_is_swappable():
    class FakeEngine:
        runtime = "fake"
        weight_format = "none"
        model_id = "fake"

        def format_user_prompt(self, user_text: str) -> str:
            return user_text

        def complete(self, prompt: str, settings: DecodeSettings) -> GenerationResult:
            return GenerationResult(text="ok", elapsed_seconds=0.01)

        def count_tokens(self, text: str) -> int:
            return 0

        def load_meta(self) -> dict:
            return {"runtime": "fake"}

        def cleanup(self) -> None:
            return None

        @classmethod
        def load(cls, config, hardware):
            return cls()

    register_engine("fake", FakeEngine.load)
    assert "fake" in registered_runtimes()
    engine = build_engine({}, _hardware(), runtime="fake")
    assert engine.complete("hi", DecodeSettings()).text == "ok"
