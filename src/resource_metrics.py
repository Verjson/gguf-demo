"""
Process RSS / GPU memory snapshots and simple percentiles for MLflow.

Linux ``ru_maxrss`` is kilobytes; macOS reports bytes. GPU memory uses
``torch.cuda.max_memory_allocated`` when CUDA is actually usable.
"""

from __future__ import annotations

import resource
import sys
from typing import Iterable


def peak_rss_mb() -> float:
    """Peak resident set size for this process, in MiB."""
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == "darwin":
        return float(rss) / (1024.0 * 1024.0)
    return float(rss) / 1024.0


def peak_gpu_mem_mb() -> float:
    """Peak CUDA allocator usage in MiB, or 0 when CUDA is not usable."""
    try:
        import torch

        from src.hardware import _cuda_is_usable

        if not _cuda_is_usable():
            return 0.0
        return float(torch.cuda.max_memory_allocated()) / (1024.0 * 1024.0)
    except Exception:  # noqa: BLE001
        return 0.0


def memory_snapshot() -> dict[str, float]:
    return {
        "peak_rss_mb": peak_rss_mb(),
        "peak_gpu_mem_mb": peak_gpu_mem_mb(),
    }


def percentile(values: Iterable[float], p: float) -> float:
    """Linear-interpolated percentile. ``p`` is 0–100."""
    xs = sorted(float(v) for v in values)
    if not xs:
        return 0.0
    if len(xs) == 1:
        return xs[0]
    p = min(100.0, max(0.0, float(p)))
    k = (len(xs) - 1) * (p / 100.0)
    lo = int(k)
    hi = min(lo + 1, len(xs) - 1)
    if lo == hi:
        return xs[lo]
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)
