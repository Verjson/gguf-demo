---
date: 2026-08-14
issue:
title: Score each answer once instead of three times
---

`Evaluator.evaluate_response` runs the BERTScore forward pass, and three callers asked for the same number per answer — the `bert_score` scorer, the `quality_score` scorer, and the ops dual-write in `eval_runner`. So roberta-large, the most expensive metric in the suite, ran three times per prompt and ROUGE six times, for identical results.

Keying the result on `(response, ground_truth)` collapses them to one pass without any caller having to know about the others, and the `bert_score` scorer now asks for the one metric it reports rather than computing the whole suite and discarding the rest.
