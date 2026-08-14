# Known ceiling: CPU decode leaves cores idle by nature

Watch `docker stats` during a CPU run and utilization swings between roughly 2500% and
1000% of a single core. That is the workload, not a misconfiguration, and it is worth
knowing before chasing it:

- **Prefill and scoring are compute-bound** and use 24–26 of the 28 threads (~80% of a
  32-thread laptop). Samples with short answers sit here for most of their time.
- **Token-by-token decode is not.** Each token reads all ~7.6GB of weights to produce
  one token, and it runs ~224 small parallel regions (32 layers x ~7 ops) with a barrier
  between them. Threads spend much of each token waiting: decode measures 14–18 GB/s of
  weight reads where a pure GEMV stream on this machine reaches ~48 GB/s, and holds
  ~1000% CPU. Adding threads makes it worse — that is the 32-thread cliff.

So more threads is the wrong lever. **GGUF / llama.cpp is now in the pipeline**
(step 2b / 4b, `LLM_RUNTIME=gguf`): Q4_K_M Phi-3 vs the Transformers BF16/FP16
checkpoint, same prompts and RAG index. Remaining CPU-decode ideas:

- Batching several sequences into one forward pass so a single set of weight
  reads serves all of them. Batching would make `generation_time` a property of
  the batch rather than the sample, so it needs a separate latency measurement.
- GPU-built llama.cpp wheels (`cu124`) when the image is CUDA; CPU wheels if
  the CUDA extra-index is missing — check `n_gpu_layers` on the MLflow run.

## Why this is a property of the workload

Decode is memory-bandwidth bound: the arithmetic per byte of weight read is tiny, so the
cores finish their share and wait on memory. That is why the measured optimum
(28 threads on this machine) sits below the core count, and why
[`src/cpu_runtime.py`](../src/cpu_runtime.py) measures the thread count rather than
deriving it from the reported topology — see
[the format guide](README.md#seeing-it-in-this-repo) for where each of these shows up in
the pipeline's own output.
