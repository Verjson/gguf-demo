---
date: 2026-08-14
issue:
title: Keep a CPU run inside its host
---

Load Phi-3 in its native bfloat16 instead of upcasting to float32 (~8GB instead of ~15GB resident, and faster decode since single-token generation is memory-bandwidth bound), cap the app container's memory so an over-budget run is killed instead of driving a WSL2 VM into swap, and reuse one BERTScorer rather than reloading roberta-large for every scored answer.
