---
date: 2026-08-14
issue:
title: Halve CPU latency on RAG prompts by enabling SDPA for Phi-3
---

transformers 4.44 ships scaled-dot-product attention for Phi-3 but leaves it disabled behind an unset capability flag, so prefill ran through eager attention. A 440-token prompt generating 64 tokens went from 75s to 36s with identical output. Also stop MLflow spending an extra generation per stage on trace validation.
