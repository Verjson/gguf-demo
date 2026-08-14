"""
Runtime names, approach suffixes, and tracking params.

``LLM_RUNTIME`` env overrides ``llm.runtime`` in config so the same scripts can
run Transformers then GGUF without editing YAML.
"""

from __future__ import annotations

import os
from typing import Any

RUNTIME_TRANSFORMERS = "transformers"
RUNTIME_GGUF = "gguf"
KNOWN_RUNTIMES = (RUNTIME_TRANSFORMERS, RUNTIME_GGUF)

ENV_RUNTIME = "LLM_RUNTIME"


def resolve_runtime(config: dict[str, Any] | None = None, explicit: str | None = None) -> str:
    """Pick an engine name: explicit arg → env → config.llm.runtime → transformers.

    Unknown names are returned as-is so ``register_engine`` can add runtimes
    without editing this module; ``build_engine`` raises if nothing is registered.
    """
    candidates = (
        explicit,
        os.environ.get(ENV_RUNTIME, "").strip() or None,
        ((config or {}).get("llm") or {}).get("runtime"),
    )
    for raw in candidates:
        if not raw:
            continue
        return str(raw).strip().lower()
    return RUNTIME_TRANSFORMERS


def approach_for_runtime(base: str, runtime: str) -> str:
    """``baseline`` + gguf → ``baseline_gguf`` so Grafana/MLflow can split series."""
    if runtime == RUNTIME_TRANSFORMERS:
        return base
    suffix = f"_{runtime}"
    if base.endswith(suffix):
        return base
    return f"{base}{suffix}"


def gguf_section(config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Defaults for the official Phi-3 Mini GGUF package on the Hub."""
    section = dict((config or {}).get("gguf") or {})
    section.setdefault("repo_id", "microsoft/Phi-3-mini-4k-instruct-gguf")
    section.setdefault("filename", "Phi-3-mini-4k-instruct-q4.gguf")
    section.setdefault("n_ctx", 4096)
    # -1 = offload every layer when llama.cpp was built with CUDA; 0 = CPU only.
    section.setdefault("n_gpu_layers", -1)
    section.setdefault("chat_stop", ["<|end|>", "<|user|>", "<|endoftext|>"])
    return section


def decode_settings(config: dict[str, Any] | None = None):
    from src.llm.port import DecodeSettings

    llm = (config or {}).get("llm") or {}
    return DecodeSettings(
        max_new_tokens=int(llm.get("max_new_tokens", 128)),
        do_sample=bool(llm.get("do_sample", False)),
        temperature=float(llm.get("temperature", 0.0)),
    )


def llm_tracking_params(config: dict[str, Any] | None = None, runtime: str | None = None) -> dict[str, Any]:
    """Flat params for the MLflow parent run (Transformers + GGUF knobs)."""
    llm = (config or {}).get("llm") or {}
    runtime = resolve_runtime(config, runtime)
    params: dict[str, Any] = {
        "runtime": runtime,
        "weight_format": "gguf" if runtime == RUNTIME_GGUF else "safetensors",
        "max_new_tokens": llm.get("max_new_tokens", 128),
        "temperature": llm.get("temperature", 0.0),
        "do_sample": bool(llm.get("do_sample", False)),
        "cpu_dtype": llm.get("cpu_dtype", "bfloat16"),
        "load_in_8bit": bool(llm.get("load_in_8bit", False)),
    }
    if runtime == RUNTIME_GGUF:
        gguf = gguf_section(config)
        params.update(
            {
                "gguf_repo_id": gguf["repo_id"],
                "gguf_filename": gguf["filename"],
                "gguf_n_ctx": int(gguf["n_ctx"]),
                "gguf_n_gpu_layers": int(gguf["n_gpu_layers"]),
            }
        )
    return params
