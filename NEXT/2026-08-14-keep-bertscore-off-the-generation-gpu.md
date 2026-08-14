---
date: 2026-08-14
issue:
title: Keep BERTScore off the GPU the model is generating on
---

`BERTScorer(lang="en")` left `device` unset, which bert_score resolves to cuda when a GPU is present. Scoring therefore put roberta-large (~1.4GB) on the card already holding Phi-3 fp16 (~7.6GB) and its KV cache: tight on a 12GB card, an out-of-memory failure on an 8GB one, and only at scoring time — after generation had already looked fine, which makes it hard to attribute.

It now defaults to CPU, configurable via `evaluation.bertscore_device` (`cpu` / `cuda` / `auto`) or the `BERTSCORE_DEVICE` environment variable. Scoring is off the generation critical path and, once deduplicated, runs once per answer, so the CPU cost is small next to the VRAM it returns to the KV cache.
