"""gguf-demo package: RAG, evaluation, hardware detection, and MLflow tracking."""

from src.hardware import HardwareInfo, detect_hardware

__version__ = "0.3.0"
__all__ = ["HardwareInfo", "detect_hardware", "__version__"]
