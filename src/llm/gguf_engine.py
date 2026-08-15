"""
llama.cpp GGUF engine.

Weights are a single ``.gguf`` file (Hub or local path). Generation goes through
``llama-cpp-python`` so quantized integer kernels stay quantized — unlike
``transformers.from_pretrained(..., gguf_file=)``, which dequantizes to fp32.

https://github.com/ggerganov/gguf
https://github.com/abetlen/llama-cpp-python
"""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any

from src.cpu_runtime import cpu_budget
from src.hardware import HardwareInfo
from src.llm.port import DecodeSettings, GenerationResult
from src.llm.prompting import apply_chat_template, count_tokens, load_instruct_tokenizer
from src.llm.runtime import RUNTIME_GGUF, gguf_section

logger = logging.getLogger(__name__)


def resolve_gguf_path(config: dict) -> Path:
    """Download (or reuse) the GGUF file. Override with ``GGUF_PATH`` for a local file."""
    override = os.environ.get("GGUF_PATH", "").strip()
    if override:
        path = Path(override)
        if not path.is_file():
            raise FileNotFoundError(f"GGUF_PATH={override} is not a file")
        return path

    gguf = gguf_section(config)
    local = gguf.get("local_path")
    if local:
        path = Path(local)
        if path.is_file():
            return path

    from huggingface_hub import hf_hub_download

    models_dir = Path(config.get("paths", {}).get("models_dir", "models"))
    dest = models_dir / "gguf"
    dest.mkdir(parents=True, exist_ok=True)
    logger.info("Fetching GGUF %s/%s → %s", gguf["repo_id"], gguf["filename"], dest)
    downloaded = hf_hub_download(
        repo_id=str(gguf["repo_id"]),
        filename=str(gguf["filename"]),
        revision=str(gguf["revision"]),
        local_dir=str(dest),
    )
    return Path(downloaded)


def _n_gpu_layers(config: dict, hardware: HardwareInfo) -> int:
    requested = int(gguf_section(config)["n_gpu_layers"])
    if requested == 0 or not hardware.cuda_available:
        return 0
    try:
        from llama_cpp import llama_supports_gpu_offload

        if not llama_supports_gpu_offload():
            logger.warning(
                "llama.cpp was built without GPU offload (CPU wheel vs Torch CUDA 13); "
                "forcing n_gpu_layers=0"
            )
            return 0
    except Exception:
        return 0
    return requested


class GgufEngine:
    runtime = RUNTIME_GGUF
    weight_format = "gguf"

    def __init__(
        self,
        *,
        llama,
        tokenizer,
        model_id: str,
        model_path: Path,
        n_gpu_layers: int,
        n_ctx: int,
        n_threads: int,
        n_threads_batch: int,
        stop: list[str],
    ):
        self._llama = llama
        self.tokenizer = tokenizer
        self.model_id = model_id
        self.model_path = model_path
        self.n_gpu_layers = n_gpu_layers
        self.n_ctx = n_ctx
        self.n_threads = n_threads
        self.n_threads_batch = n_threads_batch
        self._stop = stop

    @classmethod
    def load(cls, config: dict, hardware: HardwareInfo) -> GgufEngine:
        try:
            from llama_cpp import Llama
        except (ImportError, OSError, RuntimeError) as exc:
            raise ImportError(
                "GGUF runtime requires a loadable llama-cpp-python (CPU wheels, "
                "or a CUDA wheel matching the image libcudart). "
                "This stack uses Torch CUDA 13; abetlen cu124 wheels need libcudart.so.12. "
                "https://abetlen.github.io/llama-cpp-python/whl/"
            ) from exc

        gguf = gguf_section(config)
        path = resolve_gguf_path(config)
        n_ctx = int(gguf["n_ctx"])
        n_threads = int(gguf.get("n_threads") or cpu_budget(allow_calibration=False))
        # Prefill needs its own count, and llama.cpp's default for it is
        # `multiprocessing.cpu_count()` — every core the host exposes, which ignores
        # both the measured budget and any cgroup quota. Left unset, a container
        # granted 2 CPUs on a 64-core box spawns 64 prefill threads.
        n_threads_batch = int(gguf.get("n_threads_batch") or n_threads)
        n_gpu_layers = _n_gpu_layers(config, hardware)
        instruct_id = (config.get("llm") or {}).get("model") or "microsoft/Phi-3-mini-4k-instruct"
        tokenizer = load_instruct_tokenizer(
            str(instruct_id), revision=(config.get("llm") or {}).get("revision")
        )
        stop = list(gguf.get("chat_stop") or ["<|end|>", "<|user|>", "<|endoftext|>"])

        logger.info(
            "Loading llama.cpp GGUF %s n_ctx=%d n_threads=%d n_threads_batch=%d n_gpu_layers=%d",
            path,
            n_ctx,
            n_threads,
            n_threads_batch,
            n_gpu_layers,
        )
        llama = Llama(
            model_path=str(path),
            n_ctx=n_ctx,
            n_threads=n_threads,
            n_threads_batch=n_threads_batch,
            n_gpu_layers=n_gpu_layers,
            verbose=False,
            logits_all=False,
        )
        model_id = f"{gguf['repo_id']}/{gguf['filename']}"
        return cls(
            llama=llama,
            tokenizer=tokenizer,
            model_id=model_id,
            model_path=path,
            n_gpu_layers=n_gpu_layers,
            n_ctx=n_ctx,
            n_threads=n_threads,
            n_threads_batch=n_threads_batch,
            stop=stop,
        )

    def format_user_prompt(self, user_text: str) -> str:
        return apply_chat_template(self.tokenizer, user_text)

    def count_tokens(self, text: str) -> int:
        return count_tokens(self.tokenizer, text)

    def complete(self, prompt: str, settings: DecodeSettings) -> GenerationResult:
        kwargs: dict[str, Any] = {
            "max_tokens": int(settings.max_new_tokens),
            "stop": self._stop,
            # Every sampler knob is stated, because llama.cpp's defaults are not
            # neutral and are not the same as Hugging Face's. Leaving them unset meant
            # GGUF decoded with repeat_penalty=1.1, top_k=40 and top_p=0.95 while the
            # Transformers engine used repetition_penalty=1.0 and no truncation — so
            # "same weights, two engines" was also two different samplers, at
            # temperature 0, where both are supposed to be deterministic and identical.
            # These values are the neutral ones; changing them is now a visible edit.
            "repeat_penalty": 1.0,
            "top_k": 0,
            "top_p": 1.0,
            "min_p": 0.0,
        }
        if settings.do_sample:
            kwargs["temperature"] = max(float(settings.temperature), 1e-5)
        else:
            kwargs["temperature"] = 0.0

        start = time.perf_counter()
        out = self._llama.create_completion(prompt, **kwargs)
        elapsed = time.perf_counter() - start
        text = str((out.get("choices") or [{}])[0].get("text") or "").strip()
        usage = out.get("usage") or {}
        prompt_tokens = float(usage.get("prompt_tokens") or self.count_tokens(prompt))
        completion_tokens = float(usage.get("completion_tokens") or self.count_tokens(text))
        return GenerationResult(
            text=text,
            elapsed_seconds=elapsed,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            extra={
                "cuda_used": 1.0 if self.n_gpu_layers != 0 else 0.0,
                # Carried per row, not just in load_meta, because this is the number
                # that decides whether a Transformers-vs-GGUF comparison means
                # anything. It lived only in the manifest, so a run could record
                # n_gpu_layers=0 in one file and device=cuda in every other.
                "n_gpu_layers": float(self.n_gpu_layers),
            },
        )

    def load_meta(self) -> dict[str, Any]:
        return {
            "runtime": RUNTIME_GGUF,
            "weight_format": "gguf",
            "model_id": self.model_id,
            "gguf_path": str(self.model_path),
            "n_ctx": float(self.n_ctx),
            "n_gpu_layers": float(self.n_gpu_layers),
            "n_threads": float(self.n_threads),
            "n_threads_batch": float(self.n_threads_batch),
        }

    def cleanup(self) -> None:
        self._llama = None
        self.tokenizer = None
