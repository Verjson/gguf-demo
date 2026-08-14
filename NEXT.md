# Next

## Known ceiling: CPU decode leaves cores idle by nature

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

So more threads is the wrong lever. The two that would work are fewer bytes per weight
(int8/int4 — dynamic quantization measured slower and unstable here, so the real answer
is a GGUF/llama.cpp path, which is what this repo is named for) and batching several
sequences into one forward pass so a single set of weight reads serves all of them.
Batching would, however, make `generation_time` a property of the batch rather than the
sample, so it needs a separate latency measurement to stay honest.

## Fixed

- Make the full pipeline build a lean CPU image on CPU-only Docker hosts while automatically selecting CUDA and its GPU-only dependencies when available; honor the default CPU fine-tuning skip, cap evaluation answers at a CPU-practical length, and fix the clean-image LangChain packaging constraint for memory-constrained WSL environments.
- Keep a CPU run inside its host: load Phi-3 in its native bfloat16 instead of upcasting to float32 (~8GB instead of ~15GB resident, and faster decode since single-token generation is memory-bandwidth bound), cap the app container's memory so an over-budget run is killed instead of driving a WSL2 VM into swap, and reuse one BERTScorer rather than reloading roberta-large for every scored answer.
- Size the run to the machine it lands on rather than the machine it can see: cap thread pools by the CPU budget the container is actually granted (cgroup quota or cpuset), evaluate one sample at a time so a single local model is not contended by ten concurrent requests, and read memory limits from cgroups so the numbers hold when the pipeline itself runs in a container. Together these took CPU throttling from 80% of scheduling periods to near zero.
- Choose the thread count under that cap by measuring instead of trusting the reported topology, which a hypervisor may invent: WSL2 describes an 8 P-core + 16 E-core i9-14900HX as a uniform "16 cores x 2 threads", so folding hyperthread siblings idled 8 real cores and cost 37% (1.26 tok/s at 16 threads against 1.76 at 28 on a RAG-sized prompt), while filling all 32 falls off an oversubscription cliff to 1.60. The first CPU run times a decode-shaped GEMV chain and a prefill-shaped GEMM at five candidate thread counts and caches the winner per machine, which ranks candidates the same way full generations do for about 10 seconds once.
- Halve CPU latency on RAG prompts by using the scaled-dot-product attention that transformers 4.44 ships for Phi-3 but leaves disabled behind an unset capability flag, so prefill no longer runs through eager attention; a 440-token prompt generating 64 tokens went from 75s to 36s with identical output. Also stop MLflow spending an extra generation per stage on trace validation.
- Survive a transient arXiv outage by retrying the search and falling back to the corpus already on disk.
