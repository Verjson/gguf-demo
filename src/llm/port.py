"""
Inference port: RAG and eval talk to this, not to Transformers or llama.cpp.

Swap implementations via ``src.llm.factory.build_engine`` / ``register_engine``.
A third runtime (vLLM, ONNX, a remote API) only needs to satisfy ``LlmEngine``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass(frozen=True)
class DecodeSettings:
    """Sampling knobs shared across engines (from ``config.llm``)."""

    max_new_tokens: int = 128
    do_sample: bool = False
    temperature: float = 0.0


@dataclass
class GenerationResult:
    """One completion plus timings/token counts for MLflow and Grafana."""

    text: str
    elapsed_seconds: float
    prompt_tokens: float = 0.0
    completion_tokens: float = 0.0
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def tokens_per_sec(self) -> float:
        if self.elapsed_seconds <= 0:
            return 0.0
        return self.completion_tokens / self.elapsed_seconds


@runtime_checkable
class LlmEngine(Protocol):
    """Local (or remote) text generator used by ``RAGPipeline``."""

    runtime: str
    weight_format: str
    model_id: str

    def format_user_prompt(self, user_text: str) -> str:
        """Apply the model's chat template, or return ``user_text`` unchanged."""

    def complete(self, prompt: str, settings: DecodeSettings) -> GenerationResult:
        """Generate a continuation of ``prompt``. Must not mutate caller state."""

    def count_tokens(self, text: str) -> int:
        ...

    def load_meta(self) -> dict[str, Any]:
        """Engine identity + load-time facts (quant, n_gpu_layers, …)."""

    def cleanup(self) -> None:
        """Release weights so the next engine in-process can reuse RAM/VRAM."""
