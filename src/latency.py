"""
Latency / time-to-response helpers for CPU vs GPU comparison.

time_to_response = retrieval_time (0 for baseline) + generation_time
That is the end-to-end wait the user experiences for one answer.
"""

from __future__ import annotations

from typing import Any

GENERATION_META_KEYS = (
    "generation_time",
    "prompt_chars",
    "response_chars",
    "prompt_tokens",
    "completion_tokens",
    "tokens_per_sec",
    "cuda_used",
)

RETRIEVAL_META_KEYS = (
    "retrieval_time",
    "context_chars",
    "n_chunks_retrieved",
)


def _copy_numeric(metrics: dict[str, float], source: dict[str, Any], keys: tuple[str, ...]) -> None:
    for key in keys:
        value = source.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            metrics[key] = float(value)


def attach_generation_meta(metrics: dict[str, float], meta: dict[str, Any] | None) -> dict[str, float]:
    """Copy tokenizer / size fields from ``RAGPipeline.last_generation_meta``."""
    if meta:
        _copy_numeric(metrics, meta, GENERATION_META_KEYS)
    return metrics


def attach_retrieval_meta(metrics: dict[str, float], meta: dict[str, Any] | None) -> dict[str, float]:
    """Copy chunk / context size fields from ``RAGPipeline.last_retrieval_meta``."""
    if meta:
        _copy_numeric(metrics, meta, RETRIEVAL_META_KEYS)
    return metrics


def llm_run_params(config: dict[str, Any] | None) -> dict[str, Any]:
    """Decode / dtype knobs for the parent evaluation run (includes runtime)."""
    from src.llm.runtime import llm_tracking_params

    return llm_tracking_params(config)


def attach_latency_metrics(
    metrics: dict[str, float],
    *,
    generation_time: float,
    retrieval_time: float = 0.0,
    response_chars: float | None = None,
) -> dict[str, float]:
    """
    Mutate and return metrics with latency fields used for CPU vs GPU comparison.

    - generation_time: LLM inference only (CUDA-synchronized when on GPU)
    - retrieval_time: vector search (RAG only)
    - time_to_response: end-to-end = retrieval + generation
    - speed_chars_per_sec: rough throughput from response length / generation_time
    """
    gen = float(generation_time or 0.0)
    ret = float(retrieval_time or 0.0)
    metrics["generation_time"] = gen
    metrics["retrieval_time"] = ret
    metrics["time_to_response"] = gen + ret

    chars = response_chars
    if chars is None and "response_chars" in metrics:
        chars = metrics["response_chars"]
    if chars is not None and gen > 0:
        metrics["speed_chars_per_sec"] = float(chars) / gen

    return metrics


def speedup_factor(cpu_seconds: float | None, gpu_seconds: float | None) -> float | None:
    """CPU time / GPU time — values > 1 mean GPU was faster."""
    if cpu_seconds is None or gpu_seconds is None:
        return None
    if gpu_seconds <= 0:
        return None
    return float(cpu_seconds) / float(gpu_seconds)


def latency_summary_line(approach: str, cpu_ttr: float | None, gpu_ttr: float | None) -> str:
    if cpu_ttr is None or gpu_ttr is None or gpu_ttr <= 0:
        return f"- **{approach}:** incomplete latency pair"
    factor = cpu_ttr / gpu_ttr
    return (
        f"- **{approach}:** CPU {cpu_ttr:.2f}s → GPU {gpu_ttr:.2f}s "
        f"(**{factor:.1f}×** faster time-to-response on GPU)"
    )
