"""
Engine registry: RAG/eval call ``build_engine``, never a concrete class.

Register a new runtime without touching ``RAGPipeline``:

    from src.llm.factory import register_engine
    register_engine("vllm", VllmEngine.load)
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from src.hardware import HardwareInfo
from src.llm.port import LlmEngine
from src.llm.runtime import RUNTIME_GGUF, RUNTIME_TRANSFORMERS, resolve_runtime

logger = logging.getLogger(__name__)

EngineLoader = Callable[[dict, HardwareInfo], LlmEngine]

_REGISTRY: dict[str, EngineLoader] = {}


def register_engine(name: str, loader: EngineLoader) -> None:
    _REGISTRY[str(name).strip().lower()] = loader


def _default_registry() -> None:
    if _REGISTRY:
        return
    from src.llm.gguf_engine import GgufEngine
    from src.llm.transformers_engine import TransformersEngine

    register_engine(RUNTIME_TRANSFORMERS, TransformersEngine.load)
    register_engine(RUNTIME_GGUF, GgufEngine.load)


def build_engine(
    config: dict[str, Any],
    hardware: HardwareInfo,
    runtime: str | None = None,
) -> LlmEngine:
    """Construct the engine named by ``runtime`` / ``LLM_RUNTIME`` / config."""
    _default_registry()
    name = resolve_runtime(config, runtime)
    loader = _REGISTRY.get(name)
    if loader is None:
        known = ", ".join(sorted(_REGISTRY)) or "(empty)"
        raise ValueError(f"No LLM engine registered for {name!r}. Known: {known}")
    logger.info("Building LLM engine runtime=%s", name)
    return loader(config, hardware)


def registered_runtimes() -> tuple[str, ...]:
    _default_registry()
    return tuple(sorted(_REGISTRY))
