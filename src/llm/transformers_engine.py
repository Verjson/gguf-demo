"""
Hugging Face Transformers + PyTorch engine (safetensors / PEFT adapters).
"""

from __future__ import annotations

import logging
import time
from typing import Any

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline

from src.hardware import HardwareInfo
from src.llm.port import DecodeSettings, GenerationResult
from src.llm.prompting import apply_chat_template, count_tokens, load_instruct_tokenizer
from src.llm.runtime import RUNTIME_TRANSFORMERS

logger = logging.getLogger(__name__)


def _sdpa_available() -> bool:
    """
    Whether Phi-3 can use SDPA attention, patching the old flag when it must.

    transformers 4.44 shipped Phi3SdpaAttention but left ``_supports_sdpa`` off, so the
    loader silently fell back to eager attention — which dominates CPU prefill on RAG
    prompts (a 440-token prompt generating 64 tokens went from 75s to 36s once enabled).
    That flag had to be forced on.

    4.48 removed ``PHI3_ATTENTION_CLASSES`` and made SDPA support native, so the old
    probe now reports False on a version where SDPA is not merely available but the
    default — and the caller stopped asking for it explicitly, leaving the choice to a
    library default that could change again. Ask the class what it supports instead.
    """
    try:
        from transformers.models.phi3 import modeling_phi3
    except ImportError:
        return False

    legacy_classes = getattr(modeling_phi3, "PHI3_ATTENTION_CLASSES", None)
    if legacy_classes is not None:
        if "sdpa" not in legacy_classes:
            return False
        modeling_phi3.Phi3PreTrainedModel._supports_sdpa = True
        return True

    return bool(getattr(modeling_phi3.Phi3PreTrainedModel, "_supports_sdpa", False))


def _cpu_dtype(config: dict) -> torch.dtype:
    name = str(config.get("llm", {}).get("cpu_dtype", "bfloat16"))
    dtype = getattr(torch, name, None)
    if not isinstance(dtype, torch.dtype):
        logger.warning("Unknown llm.cpu_dtype %r; using bfloat16", name)
        return torch.bfloat16
    return dtype


def _generation_kwargs(settings: DecodeSettings) -> dict:
    kwargs: dict = {
        "max_new_tokens": settings.max_new_tokens,
        "do_sample": settings.do_sample,
        "return_full_text": False,
    }
    if settings.do_sample:
        kwargs["temperature"] = max(settings.temperature, 1e-5)
    return kwargs


def _model_load_kwargs(config: dict, hardware: HardwareInfo) -> dict:
    use_cuda = hardware.cuda_available
    kwargs: dict = {"low_cpu_mem_usage": True}
    if _sdpa_available():
        kwargs["attn_implementation"] = "sdpa"
    if use_cuda:
        load_8bit = bool(config.get("llm", {}).get("load_in_8bit", False))
        if load_8bit:
            kwargs["quantization_config"] = BitsAndBytesConfig(load_in_8bit=True)
        else:
            kwargs["torch_dtype"] = torch.float16
        kwargs["device_map"] = {"": 0}
    else:
        kwargs["torch_dtype"] = _cpu_dtype(config)
    return kwargs


def _from_pretrained(model_id: str, config: dict, hardware: HardwareInfo):
    model_kwargs = _model_load_kwargs(config, hardware)
    try:
        return AutoModelForCausalLM.from_pretrained(model_id, **model_kwargs)
    except ValueError as exc:
        msg = str(exc)
        if "scaled_dot_product_attention" in msg and "attn_implementation" in model_kwargs:
            logger.warning("%s does not support SDPA; using the default attention", model_id)
            model_kwargs.pop("attn_implementation")
            return AutoModelForCausalLM.from_pretrained(model_id, **model_kwargs)
        if "8-bit" not in msg and "4-bit" not in msg:
            raise
        logger.warning("Quantized load failed (%s); falling back to float16", exc)
        return AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            device_map={"": 0},
            low_cpu_mem_usage=True,
        )


class TransformersEngine:
    runtime = RUNTIME_TRANSFORMERS
    weight_format = "safetensors"

    def __init__(
        self,
        *,
        pipe,
        tokenizer,
        model_id: str,
        hardware: HardwareInfo,
        load_info: dict[str, Any],
    ):
        self._pipe = pipe
        self.tokenizer = tokenizer
        self.model_id = model_id
        self._hardware = hardware
        self._load_info = load_info

    @classmethod
    def load(cls, config: dict, hardware: HardwareInfo) -> TransformersEngine:
        llm_cfg = config.get("llm") or {}
        adapter = llm_cfg.get("fine_tuned_path")
        if adapter:
            return cls._load_fine_tuned(config, hardware, str(adapter))
        return cls._load_base(config, hardware)

    @classmethod
    def _load_base(cls, config: dict, hardware: HardwareInfo) -> TransformersEngine:
        model_id = config["llm"]["model"]
        tokenizer = load_instruct_tokenizer(model_id)
        from src.llm.runtime import decode_settings

        settings = decode_settings(config)
        use_cuda = hardware.cuda_available
        load_8bit = bool(config.get("llm", {}).get("load_in_8bit", False)) and use_cuda
        logger.info(
            "Loading Transformers %s on %s (8-bit=%s)",
            model_id,
            "CUDA" if use_cuda else "CPU",
            load_8bit,
        )
        model = _from_pretrained(model_id, config, hardware)
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            **_generation_kwargs(settings),
        )
        return cls(
            pipe=pipe,
            tokenizer=tokenizer,
            model_id=model_id,
            hardware=hardware,
            load_info={
                "runtime": RUNTIME_TRANSFORMERS,
                "weight_format": "safetensors",
                "model_id": model_id,
                "load_in_8bit": float(load_8bit),
            },
        )

    @classmethod
    def _load_fine_tuned(
        cls, config: dict, hardware: HardwareInfo, model_path: str
    ) -> TransformersEngine:
        import os

        from src.llm.runtime import decode_settings

        settings = decode_settings(config)
        use_cuda = hardware.cuda_available
        logger.info("Loading fine-tuned Transformers weights from %s", model_path)
        adapter_config = os.path.join(model_path, "adapter_config.json")
        if os.path.isfile(adapter_config):
            from peft import PeftModel

            base_id = config["fine_tuning"]["base_model"]
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            base = _from_pretrained(base_id, config, hardware)
            model = PeftModel.from_pretrained(base, model_path)
            # Evaluation only ever does a forward pass, and an unmerged adapter makes
            # every one of them compute base and delta separately. Folding the
            # adapter into the base weights speeds up decode and frees the adapter
            # tensors. It is slightly lossy in bfloat16 — the delta is rounded into
            # the base — which is the accepted trade for inference, not for training.
            try:
                model = model.merge_and_unload()
                logger.info("Merged LoRA adapter into the base weights for inference")
            except Exception as exc:  # noqa: BLE001 - an unmerged adapter still evaluates
                logger.warning("Could not merge the LoRA adapter (%s); evaluating unmerged", exc)
            pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                **_generation_kwargs(settings),
            )
            model_id = f"peft:{model_path}"
        else:
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            pipe = pipeline(
                "text-generation",
                model=model_path,
                tokenizer=tokenizer,
                device=0 if use_cuda else -1,
                **_generation_kwargs(settings),
            )
            model_id = model_path
        return cls(
            pipe=pipe,
            tokenizer=tokenizer,
            model_id=model_id,
            hardware=hardware,
            load_info={
                "runtime": RUNTIME_TRANSFORMERS,
                "weight_format": "safetensors",
                "model_id": model_id,
                "fine_tuned": 1.0,
            },
        )

    def format_user_prompt(self, user_text: str) -> str:
        return apply_chat_template(self.tokenizer, user_text)

    def count_tokens(self, text: str) -> int:
        return count_tokens(self.tokenizer, text)

    def complete(self, prompt: str, settings: DecodeSettings) -> GenerationResult:
        cuda_live = bool(self._hardware.cuda_available and torch.cuda.is_available())
        start = time.perf_counter()
        if cuda_live:
            torch.cuda.synchronize()
        raw = self._pipe(prompt, **_generation_kwargs(settings))[0]["generated_text"]
        if cuda_live:
            torch.cuda.synchronize()
        elapsed = time.perf_counter() - start
        if raw.startswith(prompt):
            text = raw[len(prompt) :].strip()
        else:
            text = raw.strip()
        return GenerationResult(
            text=text,
            elapsed_seconds=elapsed,
            prompt_tokens=float(self.count_tokens(prompt)),
            completion_tokens=float(self.count_tokens(text)),
            extra={"cuda_used": 1.0 if cuda_live else 0.0},
        )

    def load_meta(self) -> dict[str, Any]:
        return dict(self._load_info)

    def cleanup(self) -> None:
        self._pipe = None
        self.tokenizer = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
