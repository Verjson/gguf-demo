"""
Shared chat templating.

Both engines format prompts with the Hugging Face *instruct* tokenizer so a
GGUF vs Transformers comparison uses the same Phi-3 markup, not llama.cpp's
built-in chat_format (which can differ slightly from ``apply_chat_template``).
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def load_instruct_tokenizer(model_id: str):
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(model_id)


def apply_chat_template(tokenizer: Any, user_text: str) -> str:
    if tokenizer is not None and getattr(tokenizer, "chat_template", None):
        try:
            return tokenizer.apply_chat_template(
                [{"role": "user", "content": user_text}],
                tokenize=False,
                add_generation_prompt=True,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("chat_template failed (%s); using raw prompt", exc)
    return user_text


def count_tokens(tokenizer: Any, text: str) -> int:
    if tokenizer is None or not text:
        return 0
    try:
        return len(tokenizer.encode(text, add_special_tokens=False))
    except Exception:  # noqa: BLE001
        return 0
