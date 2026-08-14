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

import torch

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
        }

    def as_metrics(self) -> dict[str, float]:
        """
        Numeric metrics so CUDA vs CPU shows up in MLflow charts.

        `cuda_used` means CUDA was *available* to this process (1.0 / 0.0),
        not a guarantee that every kernel ran on the GPU. Generation timing
        still uses cuda.synchronize() when available so wall clocks reflect
        GPU compute.
        """
        return {
            "cuda_used": 1.0 if self.cuda_available else 0.0,
            "cuda_device_count": float(self.cuda_device_count),
        }

    def summary(self) -> str:
        if self.cuda_available:
            return (
                f"CUDA ON | device={self.cuda_device_name} "
                f"| count={self.cuda_device_count} | capability={self.cuda_capability}"
            )
        return "CUDA OFF | running on CPU"


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
    if not torch.cuda.is_available():
        return False
    try:
        return torch.cuda.device_count() > 0
    except Exception:  # noqa: BLE001
        return False


def detect_hardware() -> HardwareInfo:
    """Inspect torch for CUDA availability and return a HardwareInfo snapshot."""
    cuda_available = _cuda_is_usable()
    device_name = None
    capability = None

    if cuda_available:
        device_name = torch.cuda.get_device_name(0)
        major, minor = torch.cuda.get_device_capability(0)
        capability = f"{major}.{minor}"

    info = HardwareInfo(
        cuda_available=cuda_available,
        device="cuda" if cuda_available else "cpu",
        cuda_device_count=torch.cuda.device_count() if cuda_available else 0,
        cuda_device_name=device_name,
        cuda_capability=capability,
        torch_version=torch.__version__,
        cuda_version=getattr(torch.version, "cuda", None),
    )
    logger.info("Hardware: %s", info.summary())
    return info


def hardware_as_dict(info: HardwareInfo | None = None) -> dict[str, Any]:
    info = info or detect_hardware()
    return asdict(info)
