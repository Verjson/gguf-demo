import pytest

import src.evaluator as ev
from src.evaluator import Evaluator
from src.genai_scorers import build_metric_scorers


@pytest.fixture(autouse=True)
def disable_external_mlflow_tracing(monkeypatch):
    """Unit scoring tests must not initialize MLflow's filesystem/SQL trace store."""
    monkeypatch.setattr(Evaluator, "evaluate_response", Evaluator.evaluate_response.__wrapped__)
    monkeypatch.setattr(Evaluator, "_judge_uncached", Evaluator._judge_uncached.__wrapped__)


class CountingScorer:
    """Stand-in for BERTScorer that records how often the model was asked to score."""

    def __init__(self):
        self.calls = 0

    def score(self, responses, references):
        self.calls += 1

        class _F1:
            def mean(self):
                return self

            def item(self):
                return 0.75

        return None, None, _F1()


def _install_counting_scorer(monkeypatch) -> CountingScorer:
    counter = CountingScorer()
    monkeypatch.setattr(ev, "_get_bert_scorer", lambda device: counter)
    ev.bert_f1.cache_clear()
    return counter


def test_bert_score_is_computed_once_per_answer(monkeypatch):
    counter = _install_counting_scorer(monkeypatch)
    evaluator = Evaluator(bertscore_device="cpu")

    first = evaluator.bert_score("an answer", "the truth")
    second = evaluator.bert_score("an answer", "the truth")

    assert first == second == 0.75
    assert counter.calls == 1


def test_all_three_callers_share_one_bertscore_pass(monkeypatch):
    """The two scorers and the ops dual-write ask for the same number."""
    counter = _install_counting_scorer(monkeypatch)
    evaluator = Evaluator(bertscore_device="cpu")
    scorers = {s.name: s for s in build_metric_scorers(evaluator, include_rag=False)}
    outputs = {"answer": "an answer"}
    expectations = {"ground_truth": "the truth"}

    scorers["bert_score"](outputs=outputs, expectations=expectations)
    scorers["quality_score"](
        inputs={"question": "a question"}, outputs=outputs, expectations=expectations
    )
    evaluator.evaluate_response(
        question="a question", response="an answer", ground_truth="the truth"
    )

    assert counter.calls == 1


def test_distinct_answers_are_scored_separately(monkeypatch):
    counter = _install_counting_scorer(monkeypatch)
    evaluator = Evaluator(bertscore_device="cpu")

    evaluator.bert_score("first answer", "the truth")
    evaluator.bert_score("second answer", "the truth")
    evaluator.bert_score("first answer", "a different truth")

    assert counter.calls == 3


def test_llm_judge_scores_once_then_uses_the_cached_result():
    calls = []

    def judge(prompt: str) -> str:
        calls.append(prompt)
        return "4"

    evaluator = Evaluator(judge_fn=judge, enable_bertscore=False)

    first = evaluator._llm_judge_groundedness("question", "answer", "context")
    second = evaluator._llm_judge_groundedness("question", "answer", "context")

    assert first == second == 0.75
    assert len(calls) == 1


def test_bert_score_disabled_never_loads_the_model(monkeypatch):
    counter = _install_counting_scorer(monkeypatch)
    evaluator = Evaluator(enable_bertscore=False, bertscore_device="cpu")

    assert evaluator.bert_score("an answer", "the truth") is None
    metrics = evaluator.evaluate_response(
        question="q", response="an answer", ground_truth="the truth"
    )

    assert "bert_score" not in metrics
    assert counter.calls == 0


def test_scoring_failure_degrades_to_no_metric(monkeypatch):
    class Failing:
        def score(self, responses, references):
            raise RuntimeError("model unavailable")

    monkeypatch.setattr(ev, "_get_bert_scorer", lambda device: Failing())
    ev.bert_f1.cache_clear()
    evaluator = Evaluator(bertscore_device="cpu")

    assert evaluator.bert_score("an answer", "the truth") is None
    metrics = evaluator.evaluate_response(
        question="q", response="the model was trained", ground_truth="the model was trained"
    )

    assert "bert_score" not in metrics
    assert metrics["rougeL"] > 0  # the rest of the suite still scores


def test_rouge_returns_all_three_f_measures():
    evaluator = Evaluator(enable_bertscore=False)

    r1, r2, rl = evaluator.rouge("the cat sat on the mat", "the cat sat on the mat")

    assert (r1, r2, rl) == (1.0, 1.0, 1.0)


def test_bertscore_device_defaults_to_cpu_not_the_generation_gpu(monkeypatch):
    monkeypatch.delenv(ev.BERTSCORE_DEVICE_ENV, raising=False)

    assert ev.resolve_bertscore_device(None) == "cpu"
    assert ev.resolve_bertscore_device("cuda") == "cuda"


def test_bertscore_device_env_overrides_the_default(monkeypatch):
    monkeypatch.setenv(ev.BERTSCORE_DEVICE_ENV, "cuda")

    assert ev.resolve_bertscore_device(None) == "cuda"
    assert ev.resolve_bertscore_device("cpu") == "cpu"  # explicit config still wins
