"""
Hardware / device detection for CUDA vs CPU runs.

Every evaluation should log whether inference used CUDA so you can compare
latency and quality when the same pipeline runs on GPU vs CPU.
"""

from __future__ import annotations

import logging
import os
from dataclasses import asdict, dataclass
from typing import Any

# torch is imported inside the functions that need it, not here.
#
# HardwareInfo is a plain dataclass, and the modules that consume it — run_results,
# question_view, metrics_store, the exporters — never touch a tensor. A module-scope
# `import torch` made all of them depend on a 2GB install: the export step paid
# seconds of import time for nothing, and the pure-logic tests could not run at all
# without the full ML stack present.
#
# Only detect_hardware() and _cuda_is_usable() actually need it, and both are called
# from processes that are about to load a model anyway.

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class HardwareInfo:
    """Snapshot of the compute device used for a run."""

    cuda_available: bool
    device: str  # "cuda" or "cpu"
    cuda_device_count: int
    cuda_device_name: str | None
    cuda_capability: str | None
    torch_version: str
    cuda_version: str | None
    # A CPU run's seconds mean nothing without the machine behind them, and the
    # thread count is measured per machine rather than fixed — so record both.
    cpu_model: str
    cpu_logical: int
    cpu_threads: int

    def as_params(self) -> dict[str, Any]:
        """Flat dict suitable for MLflow params / Prometheus labels."""
        return {
            "cuda_available": self.cuda_available,
            "device": self.device,
            "cuda_device_count": self.cuda_device_count,
            "cuda_device_name": self.cuda_device_name or "none",
            "cuda_capability": self.cuda_capability or "none",
            "torch_version": self.torch_version,
            "cuda_version": self.cuda_version or "none",
            "cpu_model": self.cpu_model,
            "cpu_logical": self.cpu_logical,
            "cpu_threads": self.cpu_threads,
        }

    def as_metrics(self) -> dict[str, float]:
        """
        Machine facts, as numbers, for MLflow charts and CSV exports.

        Deliberately does **not** include ``cuda_used``. It used to, defined as "CUDA
        was visible to this process" — and because every caller applies these with
        ``metrics.update(...)`` *after* attaching the engine's own measurement, that
        ambient definition silently overwrote the measured one.

        That was not a theoretical loss of precision. Dockerfile.app installs the CPU
        llama.cpp wheel on CUDA 13 hosts, so ``GgufEngine`` correctly reports
        ``n_gpu_layers=0`` and ``cuda_used=0.0`` — and the row was written as
        ``cuda_used=1.0, device=cuda`` anyway. Run 2026-08-14_181632_cuda has the
        contradiction on record: its manifest says ``n_gpu_layers: 0.0`` and
        ``peak_gpu_mem_mb: 86`` while every GGUF row claims the GPU. The dashboard
        that compares the two engines was reading a GPU-vs-CPU difference as an
        engine difference.

        ``cuda_used`` is a property of one generation, so the engine that performed it
        owns it. This function reports only what is true of the machine.
        """
        return {
            "cuda_device_count": float(self.cuda_device_count),
            "cpu_threads": float(self.cpu_threads),
            "cpu_logical": float(self.cpu_logical),
        }

    def summary(self) -> str:
        if self.cuda_available:
            return (
                f"CUDA ON | device={self.cuda_device_name} "
                f"| count={self.cuda_device_count} | capability={self.cuda_capability}"
            )
        return (
            f"CUDA OFF | running on CPU | {self.cpu_model} "
            f"| {self.cpu_threads}/{self.cpu_logical} threads"
        )


def device_for_row(measured_cuda_used: float | None, fallback_device: str) -> str:
    """
    The device label a metric row should carry.

    ``cuda`` only when the engine reports that this generation actually ran on the
    GPU. It lives here, next to HardwareInfo, because the whole point is that it is
    *not* a property of the machine — and because keeping it free of any MLflow or
    torch import means it can be tested without either.

    ``fallback_device`` is used when no engine measurement reached the row, e.g. an
    ad-hoc caller that never went through RAGPipeline. Falling back to what the
    process can see keeps the old behaviour for those; defaulting to ``cpu`` would
    just be a different wrong answer.
    """
    if measured_cuda_used is None:
        return fallback_device
    return "cuda" if float(measured_cuda_used) > 0 else "cpu"


def _env_forces_cpu() -> bool:
    """True when the caller asked for CPU inference, even if a GPU is present.

    ``CUDA_VISIBLE_DEVICES`` empty or ``-1`` is how the pipeline pins a CPU pass
    inside a GPU image. PyTorch's ``torch.cuda.is_available()`` can still return
    True in that case, which would mis-label Grafana/Postgres rows as ``cuda``.
    ``COMPUTE_DEVICE=cpu`` is the explicit compose/pipeline override.
    """
    visible = os.environ.get("CUDA_VISIBLE_DEVICES")
    if visible is not None and visible.strip().lower() in {"", "-1", "none"}:
        return True
    return os.environ.get("COMPUTE_DEVICE", "").strip().lower() == "cpu"


def _cuda_is_usable() -> bool:
    """Whether this process should load the model on GPU and log device=cuda."""
    if _env_forces_cpu():
        return False
    try:
        import torch
    except ImportError:
        # A reporting process without torch installed is on the CPU by definition.
        return False
    if not torch.cuda.is_available():
        return False
    try:
        return torch.cuda.device_count() > 0
    except Exception:  # noqa: BLE001
        return False


def detect_hardware() -> HardwareInfo:
    """Inspect torch for CUDA availability and return a HardwareInfo snapshot."""
    import torch

    cuda_available = _cuda_is_usable()
    device_name = None
    capability = None

    if cuda_available:
        device_name = torch.cuda.get_device_name(0)
        major, minor = torch.cuda.get_device_capability(0)
        capability = f"{major}.{minor}"

    # Never measure from here: detection runs in export and reporting processes too,
    # and cpu_budget() only reads the override, the per-machine cache, or the
    # heuristic unless a caller explicitly asks it to calibrate.
    from src.cpu_runtime import allowed_cpus, cpu_budget, cpu_model

    info = HardwareInfo(
        cuda_available=cuda_available,
        device="cuda" if cuda_available else "cpu",
        cuda_device_count=torch.cuda.device_count() if cuda_available else 0,
        cuda_device_name=device_name,
        cuda_capability=capability,
        torch_version=torch.__version__,
        cuda_version=getattr(torch.version, "cuda", None),
        cpu_model=cpu_model(),
        cpu_logical=len(allowed_cpus()),
        cpu_threads=cpu_budget(allow_calibration=False),
    )
    logger.info("Hardware: %s", info.summary())
    return info


def hardware_as_dict(info: HardwareInfo | None = None) -> dict[str, Any]:
    info = info or detect_hardware()
    return asdict(info)
