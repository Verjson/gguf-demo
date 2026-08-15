"""
Shared chat templating.

Both engines format prompts with the Hugging Face *instruct* tokenizer so a
GGUF vs Transformers comparison uses the same Phi-3 markup, not llama.cpp's
built-in chat_format (which can differ slightly from ``apply_chat_template``).
"""

from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# Chat-control markup that must never survive into a prompt from retrieved text.
#
# Retrieved chunks are arbitrary PDF content — arXiv today, whatever the corpus
# holds tomorrow — and they are concatenated into the user turn. A document
# containing `<|end|><|assistant|>` closes the turn and speaks as the model. The
# same text is also interpolated into the LLM-judge prompt, where a paper that
# instructs the judge to answer 5 scores its own groundedness.
#
# Phi-3's special tokens plus the common Llama/ChatML equivalents, so swapping the
# model does not quietly reopen this.
_CONTROL_TOKEN = re.compile(
    r"<\|(?:end|user|assistant|system|endoftext|im_start|im_end|eot_id|"
    r"start_header_id|end_header_id|begin_of_text)\|>",
    re.IGNORECASE,
)


def strip_control_tokens(text: str) -> str:
    """
    Neutralise chat-control markup in untrusted text.

    Replaced with a visible placeholder rather than deleted: a chunk that legitimately
    discusses these tokens (a paper about prompt formats, say) stays readable, and a
    chunk that was trying to break out leaves a trace in the logged prompt.
    """
    if not text:
        return text
    return _CONTROL_TOKEN.sub("[control-token removed]", text)


def load_instruct_tokenizer(model_id: str, *, revision: str | None = None):
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(model_id, revision=revision)


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
