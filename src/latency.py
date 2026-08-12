"""
Latency / time-to-response helpers for CPU vs GPU comparison.

time_to_response = retrieval_time (0 for baseline) + generation_time
That is the end-to-end wait the user experiences for one answer.
"""

from __future__ import annotations

from typing import Any


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

    if response_chars is not None and gen > 0:
        metrics["speed_chars_per_sec"] = float(response_chars) / gen

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
