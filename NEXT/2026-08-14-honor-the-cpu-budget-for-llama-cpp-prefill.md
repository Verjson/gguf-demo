---
date: 2026-08-14
issue:
title: Stop llama.cpp oversubscribing prefill threads
---

`Llama` was given `n_threads` but not `n_threads_batch`, and llama-cpp-python defaults the latter to `multiprocessing.cpu_count()` — every core the host exposes, ignoring both the measured budget and any cgroup quota. That is exactly what `src/cpu_runtime.py` exists to prevent, applied to prefill instead of decode.

A container granted 2 CPUs on a 64-core host spawned 64 prefill threads. On this laptop prefill used 32 threads against a measured budget of 28. Both counts are now logged and recorded in the run's `load_meta`.
