---
date: 2026-08-14
issue:
title: Measure the best thread count instead of trusting the reported topology
---

A hypervisor may invent the topology: WSL2 describes an 8 P-core + 16 E-core i9-14900HX as a uniform "16 cores x 2 threads", so folding hyperthread siblings idled 8 real cores and cost 37% (1.26 tok/s at 16 threads against 1.76 at 28 on a RAG-sized prompt), while filling all 32 falls off an oversubscription cliff to 1.60. The first CPU run times a decode-shaped GEMV chain and a prefill-shaped GEMM at five candidate thread counts and caches the winner per machine, which ranks candidates the same way full generations do, for about 10 seconds once.
