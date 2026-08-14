---
date: 2026-08-14
issue:
title: Release the embedding model in RAGPipeline.cleanup()
---

`cleanup()` dropped the vector store, engine, llm and tokenizer but left the sentence-transformer resident — a second model holding VRAM on a GPU run, and a gap against what the method promises its callers.
