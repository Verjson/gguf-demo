"""gguf-demo package: RAG, evaluation, hardware detection, and MLflow tracking.

Deliberately empty of re-exports.

This used to do `from src.hardware import HardwareInfo, detect_hardware`, and
src.hardware imports torch at module scope — so *every* `from src.X import ...`
loaded the entire ML stack, including the modules that never touch a tensor:
run_id, snapshot, metrics_store, question_view, display_metrics, score_colors.
The export step paid for it, and pure-logic tests could not run without the
heaviest dependency in the project (nine of eleven test modules failed to import
without torch installed).

Import from the module that owns the symbol:

    from src.hardware import HardwareInfo, detect_hardware
"""

__version__ = "0.3.0"
__all__ = ["__version__"]
