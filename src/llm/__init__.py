"""Swappable local LLM engines (Transformers, GGUF/llama.cpp, …)."""

from src.llm.factory import build_engine, register_engine, registered_runtimes
from src.llm.port import DecodeSettings, GenerationResult, LlmEngine
from src.llm.runtime import (
    RUNTIME_GGUF,
    RUNTIME_TRANSFORMERS,
    approach_for_runtime,
    llm_tracking_params,
    resolve_runtime,
)

__all__ = [
    "DecodeSettings",
    "GenerationResult",
    "LlmEngine",
    "RUNTIME_GGUF",
    "RUNTIME_TRANSFORMERS",
    "approach_for_runtime",
    "build_engine",
    "llm_tracking_params",
    "register_engine",
    "registered_runtimes",
    "resolve_runtime",
]
