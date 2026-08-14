"""
Which metrics belong on a human-facing summary.

CSV / JSON / Postgres keep every column. Markdown, Grafana headlines, and the
per-question tables should only show metrics that can change a decision:

- Did RAG or fine-tuning move quality against the ground truth?
- How much longer does the user wait on CPU than on GPU?

Everything else (device flags, prompt sizes, always-zero heuristics) stays in
the machine-readable export.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

# Display order on summaries. rougeL is the overlap metric that actually moves
# when RAG helps. quality_score is the existing blend (can fall when hit@k is 0).
HEADLINE = (
    "rougeL",
    "bert_score",
    "faithfulness",
    "quality_score",
    "time_to_response",
    "tokens_per_sec",
)

# Shown only when at least one compared cell is a real, non-zero value.
# retrieval_time is folded into time_to_response; heuristic scores stay in JSON.
SUPPORTING = (
    "context_utilization",
    "retrieval_hit_at_k",
)

# Device flags, input sizes, and duplicates of a headline metric.
OMIT_FROM_SUMMARY = frozenset(
    {
        "cuda_used",
        "cuda_device_count",
        "cuda_available",
        "cpu_threads",
        "cpu_logical",
        "peak_rss_mb",
        "peak_gpu_mem_mb",
        "model_load_seconds",
        "prompt_chars",
        "prompt_tokens",
        "response_chars",
        "completion_tokens",
        "context_chars",
        "n_chunks_retrieved",
        "speed_chars_per_sec",  # weaker duplicate of tokens_per_sec
        "generation_time",  # folded into time_to_response
        "rouge1",
        "rouge2",  # rougeL is the overlap headline
        "technical_accuracy",
        "factual_density",
        "domain_relevance",
        "coherence",
        "answer_relevancy",
        "judge_groundedness",
        "retrieval_time",
    }
)

# Compact per-question table (full metrics remain in by_question.json).
QUESTION_DISPLAY = (
    "rougeL",
    "faithfulness",
    "quality_score",
    "time_to_response",
    "tokens_per_sec",
)


def _nums(values: Sequence[Any]) -> list[float]:
    return [float(v) for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)]


def worth_showing(values: Sequence[Any]) -> bool:
    """True when at least one value is a real number that is not identically zero."""
    nums = _nums(values)
    return bool(nums) and any(v != 0.0 for v in nums)


def select_summary_metrics(
    comparison: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    """Headline metrics first, then supporting ones that actually vary."""
    keys: set[str] = set()
    for row in comparison.values():
        keys.update(row)

    chosen = [
        name
        for name in HEADLINE
        if name in keys and worth_showing([row.get(name) for row in comparison.values()])
    ]
    for name in SUPPORTING:
        if name in chosen or name not in keys:
            continue
        if not worth_showing([row.get(name) for row in comparison.values()]):
            continue
        chosen.append(name)
    return chosen
