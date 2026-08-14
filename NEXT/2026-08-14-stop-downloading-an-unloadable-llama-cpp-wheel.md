---
date: 2026-08-14
issue:
title: Stop downloading a 1.9GB llama.cpp wheel that cannot load
---

The GPU build branch installed the cu124 llama-cpp-python wheel, which needs `libcudart.so.12`. A CUDA 13 torch supplies `libcudart.so.13`, so the import always failed and the build fell back to the 23MB CPU wheel — measured at 137 seconds of build time, and 1.9GB of download, discarded on every GPU rebuild.

Only a cu12x build can use that wheel, so cu13x now goes straight to the CPU wheel. The cost is that GGUF runs on CPU on a CUDA 13 host, which also means a GGUF-versus-Transformers comparison on a GPU run is partly a CPU-versus-GPU comparison — check `n_gpu_layers` before attributing a difference to the format. Restoring GPU offload means shipping a `libcudart.so.12` alongside CUDA 13 torch, which needs its own build verification.
