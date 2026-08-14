---
date: 2026-08-14
issue:
title: Add a swappable LlmEngine port for Transformers and GGUF
---

Add a swappable `LlmEngine` port (`src/llm/`) so Transformers and GGUF/llama.cpp run the same eval, MLflow traces, and Grafana series (`baseline_gguf`, `rag_gguf`).
