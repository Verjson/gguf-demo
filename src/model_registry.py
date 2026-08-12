"""
MLflow Model Registry helpers for the base HF model and LoRA adapters.

Registered model (default name ``phi-3-mini-gguf-demo``):
  - Version 1  → base microsoft/Phi-3-mini-4k-instruct (metadata pointer)
  - Version 2+ → each LoRA fine-tune (adapter artifacts under the run)
"""

from __future__ import annotations

import logging
import os
from typing import Any

import mlflow
from mlflow.tracking import MlflowClient

logger = logging.getLogger(__name__)

DEFAULT_REGISTERED_MODEL = "phi-3-mini-gguf-demo"


def registered_model_name(config: dict | None = None) -> str:
    if config:
        name = (config.get("mlflow") or {}).get("registered_model_name")
        if name:
            return str(name)
    return os.getenv("MLFLOW_REGISTERED_MODEL_NAME", DEFAULT_REGISTERED_MODEL)


def _client() -> MlflowClient:
    return MlflowClient(tracking_uri=os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000"))


def ensure_base_model_registered(
    *,
    base_model_id: str,
    registered_name: str | None = None,
    tags: dict[str, str] | None = None,
) -> str:
    """
    Ensure version 1 exists for the base HF model (lightweight card + tags).

    Returns the registered model name.
    """
    name = registered_name or registered_model_name()
    client = _client()

    try:
        versions = client.search_model_versions(f"name='{name}'")
    except Exception:  # noqa: BLE001
        versions = []

    if versions:
        logger.info(
            "Registered model %s already has %d version(s); skipping base registration",
            name,
            len(versions),
        )
        return name

    try:
        client.create_registered_model(
            name,
            description="Phi-3 mini for gguf-demo: v1=base HF, v2+=LoRA adapters",
        )
    except Exception:  # noqa: BLE001
        pass

    exp = os.getenv("MLFLOW_EXPERIMENT_NAME", "gguf-demo")
    mlflow.set_experiment(exp)
    with mlflow.start_run(run_name="register-base-model") as run:
        mlflow.set_tag("model_role", "base")
        mlflow.set_tag("base_model_id", base_model_id)
        mlflow.log_param("base_model_id", base_model_id)
        mlflow.log_param("flavor", "huggingface_reference")
        card = (
            f"# {name} — base\n\n"
            f"- Hugging Face id: `{base_model_id}`\n"
            f"- Weights: loaded from HF cache at runtime (not duplicated in the registry)\n"
            f"- Role: registry lineage root (version 1)\n"
        )
        mlflow.log_text(card, artifact_file="model_card.md")
        source = f"runs:/{run.info.run_id}/artifacts"
        mv = client.create_model_version(
            name=name,
            source=source,
            run_id=run.info.run_id,
            description=f"Base HF model reference: {base_model_id}",
        )
        client.set_model_version_tag(name, mv.version, "role", "base")
        client.set_model_version_tag(name, mv.version, "base_model_id", base_model_id)
        client.set_model_version_tag(name, mv.version, "artifact_kind", "hf_reference")
        for k, v in (tags or {}).items():
            client.set_model_version_tag(name, mv.version, k, str(v))
        try:
            client.set_registered_model_alias(name, "base", mv.version)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not set alias 'base': %s", exc)
        logger.info("Registered base model %s version %s", name, mv.version)
    return name


def register_lora_adapter(
    *,
    adapter_path: str,
    base_model_id: str,
    train_metrics: dict[str, Any],
    hardware_params: dict[str, Any],
    registered_name: str | None = None,
    extra_tags: dict[str, str] | None = None,
) -> str:
    """
    Log the LoRA adapter directory and register it as the next model version.

    Returns the new version string (e.g. \"2\").
    """
    name = registered_name or registered_model_name()
    ensure_base_model_registered(base_model_id=base_model_id, registered_name=name)

    client = _client()
    exp = os.getenv("MLFLOW_EXPERIMENT_NAME", "gguf-demo")
    mlflow.set_experiment(exp)

    # Ensure the registered model parent exists
    try:
        client.create_registered_model(
            name,
            description="Phi-3 mini for gguf-demo: v1=base HF, v2+=LoRA adapters",
        )
    except Exception:  # noqa: BLE001
        pass

    with mlflow.start_run(run_name="register-lora-adapter") as run:
        mlflow.set_tag("model_role", "lora_adapter")
        mlflow.set_tag("base_model_id", base_model_id)
        mlflow.log_params(
            {
                "base_model_id": base_model_id,
                "adapter_path": adapter_path,
                **{f"hw_{k}": str(v) for k, v in hardware_params.items()},
            }
        )
        numeric = {
            k: float(v)
            for k, v in train_metrics.items()
            if isinstance(v, (int, float)) and not isinstance(v, bool)
        }
        if numeric:
            mlflow.log_metrics(numeric)

        mlflow.log_artifacts(adapter_path, artifact_path="adapter")
        card = (
            f"# {name} — LoRA fine-tune\n\n"
            f"- Base: `{base_model_id}`\n"
            f"- Artifacts: `adapter/` (PEFT weights + tokenizer)\n"
            f"- Train metrics: {numeric}\n"
        )
        mlflow.log_text(card, artifact_file="model_card.md")

        mv = client.create_model_version(
            name=name,
            source=f"runs:/{run.info.run_id}/artifacts/adapter",
            run_id=run.info.run_id,
            description=f"LoRA adapter on {base_model_id}",
        )
        client.set_model_version_tag(name, mv.version, "role", "lora_adapter")
        client.set_model_version_tag(name, mv.version, "base_model_id", base_model_id)
        client.set_model_version_tag(name, mv.version, "artifact_kind", "peft_adapter")
        for k, v in (extra_tags or {}).items():
            client.set_model_version_tag(name, mv.version, k, str(v))

        try:
            client.set_registered_model_alias(name, "champion", mv.version)
            client.set_registered_model_alias(name, "latest-lora", mv.version)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not set registry aliases: %s", exc)

        try:
            client.transition_model_version_stage(
                name=name,
                version=mv.version,
                stage="Staging",
                archive_existing_versions=False,
            )
        except Exception as exc:  # noqa: BLE001
            logger.debug("Stage transition skipped: %s", exc)

        logger.info(
            "Registered LoRA adapter as %s version %s (alias champion). "
            "UI: Model Training → Models → %s",
            name,
            mv.version,
            name,
        )
        return str(mv.version)