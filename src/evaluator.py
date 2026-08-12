"""
Response quality metrics for comparing baseline vs RAG vs fine-tuned approaches.

Tiers:
  1. Reference-based — ROUGE, BERTScore (need ground truth)
  2. RAG-specific — retrieval_hit@k, context utilization, faithfulness proxy
  3. LLM-as-judge — groundedness 1–5 when a generator callable is provided
  4. Heuristics — domain relevance / coherence (diagnostic only)
"""

from __future__ import annotations

import logging
import re
from typing import Callable, Dict, Optional

from bert_score import score as bert_score_fn
from rouge_score import rouge_scorer

logger = logging.getLogger(__name__)

JudgeFn = Callable[[str], str]


class Evaluator:
    """Score generated answers so you can compare approaches in MLflow/Grafana."""

    def __init__(self, judge_fn: JudgeFn | None = None, enable_bertscore: bool = True):
        self.rouge_scorer = rouge_scorer.RougeScorer(
            ["rouge1", "rouge2", "rougeL"], use_stemmer=True
        )
        self.judge_fn = judge_fn
        self.enable_bertscore = enable_bertscore

        # Keywords tailored to ML/NLP paper domain — adjust for your PDF corpus
        self.domain_keywords = {
            "machine_learning": [
                "neural network",
                "deep learning",
                "gradient",
                "optimization",
                "loss function",
                "training",
                "inference",
                "model",
                "parameter",
                "accuracy",
                "precision",
                "recall",
                "f1 score",
                "validation",
            ],
            "technical_terms": [
                "algorithm",
                "computation",
                "convergence",
                "regularization",
                "overfitting",
                "underfitting",
                "hyperparameter",
                "epoch",
                "batch",
                "learning rate",
                "activation",
                "backpropagation",
            ],
        }

    def evaluate_response(
        self,
        question: str,
        response: str,
        ground_truth: Optional[str] = None,
        context: Optional[str] = None,
        k: int = 4,
    ) -> Dict[str, float]:
        """Compute all applicable metrics for one (question, response) pair."""
        metrics: Dict[str, float] = {}

        if ground_truth:
            rouge_scores = self.rouge_scorer.score(ground_truth, response)
            metrics["rouge1"] = rouge_scores["rouge1"].fmeasure
            metrics["rouge2"] = rouge_scores["rouge2"].fmeasure
            metrics["rougeL"] = rouge_scores["rougeL"].fmeasure

            if self.enable_bertscore:
                try:
                    _, _, bert_f1 = bert_score_fn(
                        [response], [ground_truth], lang="en", verbose=False
                    )
                    metrics["bert_score"] = bert_f1.mean().item()
                except Exception as exc:  # noqa: BLE001
                    logger.warning("BERTScore failed: %s", exc)

        metrics["domain_relevance"] = self._calculate_domain_relevance(response)

        if context:
            metrics["context_utilization"] = self._calculate_context_utilization(
                response, context
            )
            # Only meaningful when we have extractive ground truth to find in retrieved chunks
            if ground_truth:
                metrics["retrieval_hit_at_k"] = self.retrieval_hit_at_k(ground_truth, context)
            metrics["faithfulness"] = self._estimate_faithfulness(response, context)

            if self.judge_fn is not None:
                metrics["judge_groundedness"] = self._llm_judge_groundedness(
                    question, response, context
                )

        metrics["coherence"] = self._evaluate_coherence(response)
        metrics["factual_density"] = self._evaluate_factual_density(response)
        metrics["technical_accuracy"] = self._evaluate_technical_accuracy(response)
        metrics["answer_relevancy"] = self._answer_relevancy(question, response)

        return metrics

    @staticmethod
    def retrieval_hit_at_k(answer_or_truth: str, context: str, min_overlap: float = 0.4) -> float:
        """
        1.0 if a substantial span of the ground-truth (or answer) appears in retrieved context.

        Cheap, interpretable retrieval quality signal for newcomers.
        """
        truth = re.sub(r"\s+", " ", (answer_or_truth or "").lower()).strip()
        ctx = re.sub(r"\s+", " ", (context or "").lower()).strip()
        if not truth or not ctx:
            return 0.0

        # Exact substring hit
        if len(truth) >= 20 and truth[: min(80, len(truth))] in ctx:
            return 1.0

        # Token overlap of content words
        stop = {"the", "a", "an", "of", "to", "and", "in", "on", "for", "is", "are", "was"}
        truth_tokens = {t for t in truth.split() if t not in stop and len(t) > 2}
        ctx_tokens = set(ctx.split())
        if not truth_tokens:
            return 0.0
        overlap = len(truth_tokens & ctx_tokens) / len(truth_tokens)
        return 1.0 if overlap >= min_overlap else 0.0

    def _estimate_faithfulness(self, response: str, context: str) -> float:
        """
        Lightweight faithfulness proxy (RAGAS-inspired): fraction of response content
        tokens that also appear in the retrieved context.
        """
        stop = {"the", "a", "an", "of", "to", "and", "in", "on", "for", "is", "are", "was", "be"}
        resp_tokens = [
            t for t in response.lower().split() if t not in stop and len(t) > 2
        ]
        if not resp_tokens:
            return 0.0
        ctx_tokens = set(context.lower().split())
        supported = sum(1 for t in resp_tokens if t in ctx_tokens)
        return supported / len(resp_tokens)

    def _llm_judge_groundedness(self, question: str, response: str, context: str) -> float:
        """Ask the local LLM to score groundedness 1–5; normalize to 0–1."""
        prompt = (
            "Context:\n{context}\n\n"
            "Question: {question}\n"
            "Answer: {response}\n\n"
            "Score 1-5 how well the answer is supported by the context only.\n"
            "5 = fully supported, 3 = partially, 1 = contradicts or ignores context.\n"
            "Return only the integer."
        ).format(context=context[:2000], question=question, response=response[:1000])

        try:
            raw = self.judge_fn(prompt)  # type: ignore[misc]
            match = re.search(r"[1-5]", raw)
            if not match:
                return 0.0
            return (int(match.group()) - 1) / 4.0
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM judge failed: %s", exc)
            return 0.0

    def _answer_relevancy(self, question: str, response: str) -> float:
        """Token overlap between question and response (cheap relevancy proxy)."""
        q = set(question.lower().split())
        r = set(response.lower().split())
        if not q or not r:
            return 0.0
        return len(q & r) / len(q)

    def _calculate_domain_relevance(self, text: str) -> float:
        text_lower = text.lower()
        total_keywords = sum(len(v) for v in self.domain_keywords.values())
        found_keywords = 0
        for keywords in self.domain_keywords.values():
            for keyword in keywords:
                if keyword in text_lower:
                    found_keywords += 1
        return found_keywords / total_keywords if total_keywords > 0 else 0.0

    def _calculate_context_utilization(self, response: str, context: str) -> float:
        response_tokens = set(response.lower().split())
        context_tokens = set(context.lower().split())
        if not response_tokens or not context_tokens:
            return 0.0
        intersection = response_tokens.intersection(context_tokens)
        union = response_tokens.union(context_tokens)
        return len(intersection) / len(union) if union else 0.0

    def _evaluate_coherence(self, text: str) -> float:
        sentences = text.split(".")
        if len(sentences) < 2:
            return 1.0
        coherence_score = 0.0
        for i in range(len(sentences) - 1):
            current = set(sentences[i].lower().split())
            next_sent = set(sentences[i + 1].lower().split())
            if current and next_sent:
                overlap = len(current.intersection(next_sent))
                coherence_score += overlap / min(len(current), len(next_sent))
        return coherence_score / (len(sentences) - 1)

    def _evaluate_factual_density(self, text: str) -> float:
        words = text.split()
        if not words:
            return 0.0
        factual_indicators = 0
        for word in words:
            if any(char.isdigit() for char in word) or word.lower() in {
                "paper",
                "method",
                "result",
                "experiment",
                "dataset",
                "performance",
                "accuracy",
                "model",
                "training",
            }:
                factual_indicators += 1
        return factual_indicators / len(words)

    def _evaluate_technical_accuracy(self, text: str) -> float:
        text_lower = text.lower()
        technical_patterns = [
            "neural network",
            "deep learning",
            "machine learning",
            "training set",
            "test set",
            "validation",
            "hyperparameter",
            "gradient descent",
            "backpropagation",
            "loss function",
        ]
        used_terms = sum(1 for term in technical_patterns if term in text_lower)
        return used_terms / len(technical_patterns) if technical_patterns else 0.0
