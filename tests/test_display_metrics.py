"""Headline metric selection for human-facing summaries."""

from src.display_metrics import select_summary_metrics, worth_showing
from src.score_colors import rank_scores


def test_worth_showing_rejects_all_zero_and_empty():
    assert worth_showing([]) is False
    assert worth_showing([0.0, 0.0, None]) is False
    assert worth_showing([0.0, 0.18]) is True


def test_select_summary_metrics_drops_flags_and_zero_hit():
    comparison = {
        "baseline": {
            "rougeL": 0.07,
            "bert_score": 0.80,
            "quality_score": 0.30,
            "time_to_response": 10.0,
            "tokens_per_sec": 5.0,
            "cuda_used": 0.0,
            "prompt_chars": 94.0,
            "retrieval_hit_at_k": 0.0,
        },
        "rag": {
            "rougeL": 0.10,
            "bert_score": 0.81,
            "quality_score": 0.28,
            "time_to_response": 45.0,
            "tokens_per_sec": 2.2,
            "cuda_used": 0.0,
            "prompt_chars": 1600.0,
            "retrieval_hit_at_k": 0.0,
            "faithfulness": 0.42,
            "retrieval_time": 0.17,
            "answer_relevancy": 0.42,
            "coherence": 0.18,
        },
    }
    chosen = select_summary_metrics(comparison)
    assert "rougeL" in chosen
    assert "time_to_response" in chosen
    assert "tokens_per_sec" in chosen
    assert "faithfulness" in chosen
    assert "retrieval_time" not in chosen
    assert "answer_relevancy" not in chosen
    assert "coherence" not in chosen
    assert "cuda_used" not in chosen
    assert "prompt_chars" not in chosen
    assert "retrieval_hit_at_k" not in chosen
    assert "generation_time" not in chosen


def test_select_summary_metrics_drops_all_zero_headline():
    comparison = {
        "baseline": {"rougeL": 0.07, "faithfulness": 0.0, "time_to_response": 10.0},
        "rag": {"rougeL": 0.10, "faithfulness": 0.0, "time_to_response": 45.0},
    }
    chosen = select_summary_metrics(comparison)
    assert "rougeL" in chosen
    assert "faithfulness" not in chosen


def test_rank_scores_ignores_quality_noise():
    ranks = rank_scores([0.2987, 0.2985, 0.2986])
    assert ranks == [None, None, None]


def test_rank_scores_ignores_small_device_wobble():
    ranks = rank_scores([0.0714, 0.0659])
    assert ranks == [None, None]
    ranks = rank_scores([0.2765, 0.2869])
    assert ranks == [None, None]


def test_rank_scores_colors_real_rag_lift():
    ranks = rank_scores([0.0727, 0.0952])
    assert ranks[0] == "worst"
    assert ranks[1] == "best"


def test_rank_scores_groups_near_extremes():
    ranks = rank_scores([0.0727, 0.0714, 0.0957, 0.0952])
    assert ranks == ["worst", "worst", "best", "best"]


def test_rank_scores_colors_latency():
    ranks = rank_scores([9.98, 1.74], lower_is_better=True)
    assert ranks[0] == "worst"
    assert ranks[1] == "best"
