# Learning resources

Background reading for this repository, starting with the question it exists to answer:
**the same model weights in two different file formats behave very differently, and the
format you pick is really a statement about where the model is going to run.**

This demo runs Phi-3-mini twice over identical prompts and an identical RAG index — once
from safetensors through Transformers, once from GGUF through llama.cpp — and compares
them. So the format comparison below is not abstract here; you can see each claim in the
pipeline's own output.

| Page | What it covers |
|---|---|
| [CPU decode ceiling](cpu-decode-ceiling.md) | Why a CPU run leaves cores idle, with measurements |
| [Model formats](#model-formats-gguf-vs-safetensors) | Why both exist, and when each one is the right answer |
| [The wider landscape](#the-wider-landscape-awq-exl2-tensorrt-llm) | AWQ, EXL2, TensorRT-LLM and where they fit |
| [Choosing a format](#choosing-a-format) | A decision path, by hardware and goal |
| [Seeing it in this repo](#seeing-it-in-this-repo) | Which files and metrics demonstrate each point |
| [Further reading](#further-reading) | Primary sources first, then comparison write-ups |

---

## Model formats: GGUF vs Safetensors

Both store LLM weights, but they serve different parts of the AI lifecycle. **Safetensors**
is designed for secure storage, training, and high-performance cloud GPU serving.
**GGUF** is designed for fast, single-file local inference on consumer hardware — laptops
and edge devices — through [llama.cpp](https://github.com/ggerganov/llama.cpp).

### Key differences

**Primary use case.** Safetensors is used for training, fine-tuning, and hosting raw
models on server GPUs (for example under vLLM). GGUF is used to run models locally on
personal computers, via tools like Ollama or LM Studio.

**File structure.** Safetensors stores only tensor weights alongside a JSON header;
metadata, configuration files, and tokenizers are kept as separate files. GGUF is
self-describing — a single file bundling weights, metadata, architecture parameters, and
tokenizer data together.

**Quantization support.** Safetensors typically preserves the original high-precision
training weights (FP16 or BF16). GGUF natively embeds block-based quantization — Q4_K_M,
Q5_K_M, Q8 and others — to shrink models dramatically, so a large model fits into limited
RAM or VRAM.

**Security.** Both are safe alternatives to the legacy Python pickle formats
(`.pt` / `.pth`), because neither can execute arbitrary code on load. Safetensors achieves
this with a restricted JSON-plus-tensor layout; GGUF uses a custom binary structure built
for fast parsing.

### One caveat worth knowing early

GGUF is often described as "the CPU format", and the table below keeps that shorthand, but
llama.cpp offloads as many layers to a GPU as you ask it to (`n_gpu_layers`). The honest
distinction is not CPU-versus-GPU, it is **graceful degradation**: a GGUF model that does
not fit in VRAM spills to system RAM and gets slower, where a VRAM-only format simply
fails to load. That property is why GGUF dominates on mixed and unpredictable hardware.

This repository is a live example of the caveat's other edge — see
[Seeing it in this repo](#seeing-it-in-this-repo), where GGUF currently runs CPU-only
because the prebuilt GPU wheels target a different CUDA version than the image's PyTorch.

---

## The wider landscape: AWQ, EXL2, TensorRT-LLM

The main alternatives to GGUF and safetensors are **AWQ**, **EXL2**, and
**TensorRT-LLM**. Like GGUF they focus heavily on quantization, but with different file
architectures, aimed at different hardware.

| Format | Primary hardware target | Quantization style | Ecosystem support | Best for |
|---|---|---|---|---|
| **AWQ** | Dedicated server GPUs (NVIDIA/AMD) | Fixed 4-bit, protecting salient weights | High — natively backed by [vLLM](https://github.com/vllm-project/vllm) and TGI | Production, high-throughput cloud hosting |
| **EXL2** | Consumer and local GPUs (NVIDIA only) | Dynamic variable bit-rate (2.0–8.0 bpw) | Moderate — TabbyAPI, text-generation-webui | Squeezing a large model entirely into VRAM |
| **TensorRT-LLM** | NVIDIA enterprise GPUs (A100/H100/Blackwell) | Compiled hardware-level graphs (FP8/INT4/INT8) | Low — needs a compile step specific to your GPU | Maximizing enterprise hardware |
| **GGUF** | CPU + unified memory (Macs, laptops), with optional GPU offload | Block-based multi-bit (Q4, Q5, Q8, …) | Very high — Ollama, LM Studio, llama.cpp | Balanced local inference and mixed setups |

### AWQ — Activation-aware Weight Quantization

AWQ does not quantize every weight equally. It identifies the roughly 1% of weights that
carry the heaviest activation paths — the *salient* weights — and keeps them at higher
precision. That makes its 4-bit quantization notably accurate, competitive with or better
than standard 4-bit GGUF while running at raw GPU speed. It is a standard choice for cloud
serving.

The trade-off is flexibility: AWQ is recognized natively by the major serving frameworks,
but it cannot gracefully fall back to system RAM when you run out of VRAM.

### EXL2 — ExLlamaV2

EXL2 is tuned specifically for NVIDIA GPUs, with very fast prompt processing (prefill) and
generation (decode). Its distinguishing feature is *fractional* quantization: instead of
being limited to whole bit-widths, you pick an exact rate such as 4.65 bpw to fill a 24GB
card almost exactly.

Its limitation is the mirror image of that precision — no CPU offloading. An EXL2 model
that exceeds VRAM by even a few megabytes fails with an out-of-memory error rather than
slowing down.

### TensorRT-LLM

A compiled inference format built by NVIDIA. It bypasses general-purpose runtimes and
compiles the model's graph for the GPU directly, giving high throughput and very low
latency — especially using FP8 math on recent data-center chips.

It is for advanced infrastructure work. You generally cannot download a TensorRT-LLM file
and run it; you compile it yourself with a toolchain, and the result is tied to the GPU
architecture it was compiled for.

---

## Choosing a format

Start from where the model will run, not from the benchmark table.

**Running locally on a laptop, Mac, or mixed hardware** → GGUF. Pick the quantization by
what fits, leaving headroom for the KV cache and the rest of your system:

| Quantization | Roughly | Use when |
|---|---|---|
| Q8_0 | ~8 bits/weight | You have room and want the smallest quality loss |
| Q5_K_M | ~5.5 bits/weight | A good default when memory allows |
| Q4_K_M | ~4.5 bits/weight | The common balance point — this repo's choice |
| Q3 and below | ~3 bits/weight | Only when nothing else fits; quality falls off |

**Training or fine-tuning** → safetensors. Quantized inference formats are lossy and
one-way; keep the high-precision checkpoint as your source of truth. This repo does
exactly that: LoRA fine-tuning (step 05) runs against the safetensors checkpoint, never
the GGUF file.

**Serving many concurrent users on server GPUs** → AWQ under vLLM, or TensorRT-LLM if you
have the engineering capacity and enterprise hardware to justify the compile step.

**Fitting the largest possible model into one consumer NVIDIA GPU** → EXL2, provided you
are certain it fits.

A useful sanity check: **estimate memory before downloading.** A rough floor is
`parameters × bits-per-weight ÷ 8`, plus the KV cache, plus the runtime's own overhead.
Phi-3-mini at 3.8B parameters is ~7.6GB in BF16 and ~2.3GB at Q4_K_M — which is why the
same model that strains a laptop in safetensors runs comfortably from GGUF.

---

## Seeing it in this repo

The pipeline runs both formats over the same prompts, so the differences show up as
measurements rather than assertions.

| Concept | Where to look |
|---|---|
| The format choice itself | [`config/config.yaml`](../config/config.yaml) — `llm.model` (safetensors) and the `gguf:` section (`Phi-3-mini-4k-instruct-q4.gguf`) |
| One interface, two runtimes | [`src/llm/`](../src/llm/) — `port.py` defines the contract, `transformers_engine.py` and `gguf_engine.py` implement it, `factory.py` picks one from `LLM_RUNTIME` |
| Running both | [`scripts/run_pipeline.sh`](../scripts/run_pipeline.sh) — steps 2/4 are Transformers, steps 2b/4b re-run the same evaluation with `LLM_RUNTIME=gguf` |
| The comparison | [`scripts/09_compare_runtimes.py`](../scripts/09_compare_runtimes.py) → `results/runs/<stamp>_transformers_vs_gguf/` |
| Quantization's effect on memory | `peak_rss_mb` in the exported metrics, BF16 versus Q4_K_M |
| GPU offload in practice | `n_gpu_layers` on the MLflow run — `0` means llama.cpp ran on CPU |
| Why local inference is memory-bound | [CPU decode ceiling](cpu-decode-ceiling.md) — measured numbers for why adding threads stops helping |
| Sizing a run to its host | [`src/cpu_runtime.py`](../src/cpu_runtime.py) — why the thread count is measured rather than inferred from the reported topology |

A caveat this repo currently demonstrates the hard way: the prebuilt llama.cpp GPU wheels
are built against CUDA 12.4 and need `libcudart.so.12`, while this image's PyTorch is
CUDA 13. On such a host GGUF runs CPU-only, so a GGUF-versus-Transformers comparison on a
GPU run is partly a CPU-versus-GPU comparison. Check `n_gpu_layers` before attributing a
difference to the format. See the `llama-cpp-python` notes in
[`Dockerfile.app`](../Dockerfile.app).

---

## Further reading

### Primary sources

- [llama.cpp](https://github.com/ggerganov/llama.cpp) — the GGUF reference implementation
- [GGUF format specification](https://github.com/ggml-org/ggml/blob/master/docs/gguf.md) — the file layout itself
- [Hugging Face — Safetensors](https://huggingface.co/docs/safetensors/index) — format documentation and rationale
- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) — the Python bindings this repo uses
- [vLLM](https://github.com/vllm-project/vllm) — high-throughput GPU serving, AWQ-capable
- [ExLlamaV2](https://github.com/turboderp-org/exllamav2) — the EXL2 format and runtime
- [TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM) — NVIDIA's compiled inference stack
- [AWQ: Activation-aware Weight Quantization](https://arxiv.org/abs/2306.00978) — the original paper
- [Ollama](https://ollama.com) and [LM Studio](https://lmstudio.ai) — the usual on-ramps for running GGUF locally

### Comparisons and explainers

- [GGUF vs Safetensors](https://www.ertas.ai/compare/gguf-vs-safetensors)
- [Understanding Safetensors and GGUF — why both](https://www.linkedin.com/posts/rajuran_understanding-safetensors-and-gguf-why-both-activity-7405242568952680448-a6b6)
- [Open-source LLM formats: Safetensors, GGUF, ONNX and Unsloth](https://levelup.gitconnected.com/open-source-llm-formats-safetensors-gguf-onnx-and-unsloth-292fbde7e1a0)
- [DeepSeek: GGUF vs Safetensors](https://chat-deep.ai/guide/deepseek-gguf-vs-safetensors/)
- [AWQ vs GPTQ vs GGUF vs EXL2](https://gigagpu.com/awq-vs-gptq-vs-gguf-vs-exl2-2026/)
- [GGUF vs GPTQ vs AWQ vs EXL2](https://www.local-llm.net/compare/gguf-vs-gptq-vs-awq-vs-exl2/)
- [Choosing the right format for your AI model](https://discuss.google.dev/t/choosing-the-right-format-for-your-ai-model-a-comprehensive-guide-to-ai-inference-formats/276691)
- [Choose the right AI model format](https://phisonblog.com/choose-the-right-ai-model-format-to-save-time-boost-performance-and-build-smarter-projects/)
- [Quantization methods compared](https://ai.rs/ai-developer/quantization-methods-compared)
- [r/LocalLLaMA — 70B GGUF vs EXL2 benchmark](https://www.reddit.com/r/LocalLLaMA/comments/17w57eu/llm_format_comparisonbenchmark_70b_gguf_vs_exl2/)
- [r/LocalLLaMA — why safetensors or .bin, not GGUF](https://www.reddit.com/r/LocalLLaMA/comments/1cvx0vf/why_safetensors_or_bin_format_not_gguf/)

The comparison articles vary in rigor and in how well they have aged — quantization
tooling moves quickly. Where one contradicts a primary source or a measurement from your
own hardware, trust the measurement.

### Where to go next in this repo

- [Main README](../README.md) — running the stack, hardware requirements, troubleshooting
- [Metrics](../README.md#metrics) — what each metric means and which ones to make decisions on
- [`results/runs/`](../results/runs/) — every committed export; the newest folder holds the
  most recent findings (`results/latest/` mirrors it locally but is not committed)
