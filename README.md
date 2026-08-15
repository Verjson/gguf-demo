# gguf-demo

Local, containerized demo that compares **baseline LLM**, **RAG (Postgres/pgvector)**, and **LoRA fine-tuning** on a small arXiv paper corpus — with **MLflow**, **Prometheus**, **Postgres**, and **Grafana**.

Packaging uses **`pyproject.toml`**. Exported metrics land in **`results/`** (safe to commit).

---

## Easiest way to run

From a machine with Docker (an NVIDIA GPU is optional):

```bash
chmod +x scripts/run_pipeline.sh
./scripts/run_pipeline.sh
```

The script checks the host GPU and Docker NVIDIA runtime before building the app. It
builds a CPU-only image when either is absent; otherwise it builds the CUDA image and
runs both CPU and GPU evaluations. On GPU hosts, use `SKIP_CPU_EVAL=1` to run only the
accelerated passes.

Then open:

| What | Where |
|------|--------|
| **Results (start here)** | locally `results/latest/README.md`; on GitHub the newest folder in [`results/runs/`](results/runs/) |
| Per-question table | `results/latest/by_question.md`, or `by_question.md` in that run folder |
| Grafana | http://localhost:3000 (admin / admin) → **By Question** |
| MLflow GenAI traces | http://localhost:5000 → **GenAI** → **gguf-demo** → Traces |
| MLflow Model Registry | http://localhost:5000 → **Model Training** → **Models** → `phi-3-mini-gguf-demo` |
| Prometheus | http://localhost:9090/graph (see queries below) |

> **Ports.** If one of these is already taken, `run_pipeline.sh` publishes that
> service on the next free port and prints where it moved to — macOS in
> particular runs an AirPlay Receiver on 5000, which otherwise stops MLflow from
> starting. Pin a port yourself with `MLFLOW_PORT`, `GRAFANA_PORT`,
> `PROMETHEUS_PORT`, `POSTGRES_PORT`, or `APP_PORT`. Only the host side moves;
> the containers still talk to each other on the standard ports.

Device selection can also be forced:

```bash
COMPUTE_DEVICE=cpu ./scripts/run_pipeline.sh
COMPUTE_DEVICE=cuda SKIP_CPU_EVAL=1 ./scripts/run_pipeline.sh
```

The app container is capped so a long CPU run cannot starve the host — important on
WSL2, where an unbounded container drives the whole VM into swap instead of failing on
its own. `run_pipeline.sh` sizes the memory cap from the RAM actually available (two
thirds of it, up to 14 GB) and disables container swap, so an over-budget run is killed
rather than left thrashing. CPU is unrestricted by default; cap it on a shared machine:

```bash
APP_MEM_LIMIT=10g APP_CPUS=8 ./scripts/run_pipeline.sh
```

Both limits are discovered rather than assumed, so the demo behaves the same on a
laptop and on a slice of a shared host:

- **Threads** are capped by the CPU budget the container is actually granted — a cgroup
  quota or a cpuset, whichever is smaller. A container given 2 CPUs still *sees* every
  core on the host, so sizing from `os.cpu_count()` would start 32 threads on a 2-CPU
  grant and spend the difference on cgroup throttling.
- **The thread count under that cap is measured, not guessed**, because both obvious
  guesses are wrong. Filling every logical CPU falls off a cliff: nothing is left for
  the process's own threads, and hyperthread siblings evict each other's cache lines.
  Folding siblings into physical cores instead trusts `/proc/cpuinfo`, which a
  hypervisor is free to invent — under WSL2 an i9-14900HX (8 P-cores + 16 E-cores, 32
  threads) is reported as a uniform "16 cores x 2 threads", so folding hands back 16
  threads and idles 8 real cores. Generating from a RAG-sized prompt on that laptop:
  1.26 tok/s at 16 threads, 1.65 at 24, **1.76 at 28**, and 1.60 at 32. Guessing from
  the reported topology cost 37%. So the first CPU run times a small stand-in for the
  real workload — a memory-bound GEMV chain shaped like decode, a compute-bound GEMM
  shaped like prefill — at five candidate thread counts, and caches the winner per
  machine in `data/processed/cpu_budget.json`. It costs about 10 seconds once, picks 28
  here, and ranks candidates the same way full generations do. Set `CPU_CALIBRATE=0` to
  skip it and take the conservative folded-core heuristic, or `APP_CPUS=8` to both cap
  the container and fix the thread count on a shared machine.
- **Evaluation runs one sample at a time.** MLflow evaluates 10 concurrently by
  default, but a single local model is one shared resource: extra workers only add a
  KV cache per in-flight request and turn `generation_time` into a measure of
  contention instead of the model. Set `MLFLOW_GENAI_EVAL_MAX_WORKERS` to opt back in.
- **Memory** is read from the cgroup limit before falling back to host RAM, so the
  numbers stay right when the pipeline is itself driven from inside a container.
- **Attention uses SDPA.** transformers 4.44 ships `Phi3SdpaAttention` but leaves the
  `_supports_sdpa` flag off, so the loader silently falls back to eager attention —
  which dominates CPU prefill on RAG prompts. Enabling it cut a 440-token prompt
  generating 64 tokens from 75 s to 36 s, with identical output.

Expect CPU utilization to swing during a run rather than sit near 100%. Prefill and
scoring are compute-bound and use 24–26 of the 28 threads; decode is not, because each
token reads every weight to produce one token and runs ~224 small parallel regions with
a barrier between them, so threads spend much of a token waiting (~1000% CPU, 14–18 GB/s
of weight reads against ~48 GB/s for a pure stream). More threads make that worse, not
better — see [docs/cpu-decode-ceiling.md](docs/cpu-decode-ceiling.md) for the levers that
would actually move it, and [docs/](docs/) for why GGUF exists at all.

---

## Minimum hardware, memory, and disk

| Resource | Minimum (CPU-only) | Recommended (this demo) |
|----------|--------------------|-------------------------|
| **CPU** | 4 cores | 8+ cores |
| **RAM** | **16 GB** system (tight) | **24–32 GB** system |
| **GPU** | None (slow; hours) | NVIDIA **8 GB+** VRAM (e.g. RTX 3060 / 4070 / 4080) |
| **Disk free** | **~25 GB** | **40–60 GB** comfortable |
| **OS** | Linux or **WSL2** + Docker Desktop | WSL2 + recent NVIDIA Windows driver |

> **On macOS and Windows, the number that matters is the Docker VM's memory, not
> the machine's.** Docker Desktop runs containers inside a fixed-size VM — often
> 8 GB by default — so a 32 GB Mac still gives the app container 8 GB, and Phi-3
> needs ~9 GB. The pipeline now sizes itself from `docker info` rather than from
> the host, so it will warn instead of silently requesting more than the VM can
> honor, but the fix is to raise it: **Docker Desktop → Settings → Resources →
> Memory**, to 12 GB or more. Apple Silicon has no CUDA, so those runs are
> CPU-only; GGUF (step 2b/4b) is by far the faster path there.

### What uses the space / RAM

| Item | Approx. size |
|------|----------------|
| App image (CPU or cu130 torch + deps) | ~2–5 GB |
| Hugging Face cache (Phi-3 + MiniLM + BERTScore) | ~8–12 GB first run |
| LoRA adapters under `models/` | ~100–300 MB |
| Postgres + MLflow volumes | ~1–2 GB |
| Papers + `results/` | < 500 MB |
| Docker Desktop / WSL VM disk | leave headroom for layers |

### Runtime expectations (Phi-3-mini, ~5 papers, greedy decode)

| Mode | Full `./scripts/run_pipeline.sh` |
|------|----------------------------------|
| **GPU** (e.g. RTX 4080, 12 GB) | typically **45–90 minutes** (CPU eval passes still run for comparison) |
| **CPU-only** | roughly **1–2 hours** at ~4–5 tokens/sec on 16 cores |

**Notes**

- Default pipeline **skips CPU LoRA** (`SKIP_CPU_FINETUNE=1`) — Phi-3 LoRA on CPU is RAM-heavy and slow.
- CPU inference loads Phi-3 in **bfloat16** (its native dtype), which keeps the run near
  **8 GB** and decodes several times faster than an upcast float32 load, because
  single-token decode is bound by memory bandwidth rather than arithmetic. Set
  `llm.cpu_dtype: float32` in `config/config.yaml` to trade ~15 GB of RAM for faster
  prompt prefill on CPUs without AVX-512/AMX.
- Eval uses **greedy decoding** (`do_sample: false`) for stable quality numbers.
- `cuda_used=1.0` means CUDA was **available** to the process (not a per-kernel probe).
- Step 05 registers **base = Model Registry v1** and each LoRA as **v2+** (`phi-3-mini-gguf-demo`).

---

## What this project does

| Approach | Description |
|----------|-------------|
| **Baseline** | Transformers Phi-3 answers from parameters alone |
| **Baseline GGUF** | Same questions via llama.cpp Q4 GGUF (`baseline_gguf`) |
| **RAG** | Retrieve PDF chunks from pgvector, then Transformers generate |
| **RAG GGUF** | Same retrieval, llama.cpp generate (`rag_gguf`) |
| **Fine-tuned** | LoRA adapters on Transformers (not converted to GGUF in this demo) |
| **Fine-tuned + RAG** | Domain-tuned Transformers with retrieval |

Every answer logs **quality** (ROUGE, BERTScore, faithfulness, …) and **latency** (`time_to_response` = retrieval + generation) tagged by **device** (`cpu` / `cuda`) and **runtime** (`transformers` / `gguf`).

Generation is an `LlmEngine` port (`src/llm/`). RAG never imports Transformers or llama.cpp directly — register another backend with `src.llm.factory.register_engine`.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Docker Compose                                                 │
│   ┌──────────┐  ┌─────────┐  ┌────────────┐  ┌─────────┐        │
│   │ Postgres │  │ MLflow  │  │ Prometheus │  │ Grafana │        │
│   │ pgvector │  │  :5000  │  │   :9090    │  │  :3000  │        │
│   └────┬─────┘  └────┬────┘  └─────▲──────┘  └────┬────┘        │
│        │             │             │              │             │
│        └─────────────┴─────────────┴──────────────┘             │
│                         app (GPU optional)                      │
│              scripts/ + src/llm engines (Transformers or GGUF)          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Optional NVIDIA GPU acceleration

CPU-only hosts need no GPU drivers or container runtime. For automatic GPU acceleration:

1. **Windows:** NVIDIA driver with WSL support  
2. **WSL:** `nvidia-smi` works  
3. **Docker:** GPU enabled (Docker Desktop → Resources → GPU, or `nvidia-container-toolkit`)  
4. The pipeline selects **cu130** torch after both checks pass (CUDA 13.0 userland —
   native INT8 routing, newer cuBLAS GEMM paths, and tighter fatbin load for Ada
   Lovelace / RTX 40-series):
   ```bash
   ./scripts/run_pipeline.sh
   # Older CUDA 12.6 userland (still fine; misses CUDA 13 polish):
   TORCH_INDEX_URL=https://download.pytorch.org/whl/cu126 ./scripts/run_pipeline.sh
   ```
   Host driver must support CUDA 13 userland (this repo’s RTX 4080 Laptop path is sm_89;
   driver 610.x is sufficient). Then verify GPU inside the container:
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.gpu.yml exec -T app \
     python scripts/check_cuda.py
   ```

---

## Full pipeline details

```bash
./scripts/run_pipeline.sh
```

This command builds and starts the stack. Shared setup runs once. Metric steps run
**CPU first**, then **GPU** (if CUDA works):

| Step | CPU | GPU |
|------|-----|-----|
| 1 / 1b Download + QA | once | — |
| 2 Baseline (Transformers) | ✓ | ✓ |
| 2b Baseline (GGUF / llama.cpp) | ✓ unless `SKIP_GGUF=1` | ✓ |
| 3 Create RAG DB | once | — |
| 4 RAG (Transformers) | ✓ | ✓ |
| 4b RAG (GGUF) | ✓ unless `SKIP_GGUF=1` | ✓ |
| 5 Fine-tune LoRA | optional (`SKIP_CPU_FINETUNE=0`) | ✓ (default) |
| 6 Comparison | ✓ | ✓ |
| 7 Export | `…_cpu` | `…_cuda` |
| 8 Device summary | — | `…_cpu_vs_cuda/` |
| 9 Runtime summary | `…_transformers_vs_gguf/` | same |

```bash
SKIP_CPU_FINETUNE=0 ./scripts/run_pipeline.sh   # also train LoRA on CPU
SKIP_CPU_EVAL=1 ./scripts/run_pipeline.sh       # GPU-only evals (safer on WSL)
SKIP_GGUF=1 ./scripts/run_pipeline.sh           # Transformers only (no llama.cpp)
COMPUTE_DEVICE=cpu ./scripts/run_pipeline.sh    # force the portable CPU image
COMPUTE_DEVICE=cuda ./scripts/run_pipeline.sh   # require GPU startup; do not fall back
LLM_RUNTIME=gguf python scripts/00_query.py --prompt "..." --pdf data/papers/x.pdf
```

After code/compose changes:

```bash
./scripts/run_pipeline.sh
```

### Manual steps

| Script | What happens |
|--------|--------------|
| `check_cuda.py` | Verify GPU inside the container |
| `01_download_papers.py` | Fetch ~5 arXiv `cs.LG` PDFs → `data/papers/` |
| `01b_generate_qa_pairs.py` | Extractive Q&A → prompts + train pairs |
| `02_baseline_evaluation.py` | LLM-only (`LLM_RUNTIME=gguf` → `baseline_gguf`) |
| `03_create_rag_db.py` | Chunk, embed, store in pgvector |
| `04_rag_evaluation.py` | Retrieve + generate (`LLM_RUNTIME=gguf` → `rag_gguf`) |
| `05_fine_tune.py` | LoRA → `models/fine_tuned/adapter_*` |
| `06_fine_tuned_evaluation.py` | Baseline / FT / FT+RAG comparison |
| `07_export_results.py` | Snapshot → `results/runs/<id>/` |
| `08_compare_devices.py` | CPU vs CUDA summary |
| `09_compare_runtimes.py` | Transformers vs GGUF summary |

### Ad-hoc query

```bash
docker compose exec -T app python scripts/00_query.py \
  --prompt "What is the main contribution?" \
  --pdf data/papers/<paper>.pdf
docker compose exec -T app python scripts/00_query.py \
  --runtime gguf --prompt "..." --pdf data/papers/<paper>.pdf
```

Add `--no-rag` for baseline. Add `--judge` for LLM groundedness scoring.

---

## Recent improvements

- **Pre-build device selection** uses CPU PyTorch without GPU-only dependencies on CPU
  hosts and the cu130 stack on supported NVIDIA hosts
- **Greedy eval** + **Phi-3 chat template** for more stable, instruction-faithful answers
- **`time_to_response`** as primary latency metric; CPU÷GPU speedup in exports and Grafana
- **Question-centric views** — `by_question.md` / CSV + Grafana **By Question** dashboard
- **RAG rebuild** clears collections (no duplicate chunks); Postgres connect is lazy
- **Schema migration** via `scripts/migrate_db.sh` (needs only the postgres service, so
  it still works when the app image does not build) plus the same statements on metrics
  write; quoted `"rougeL"` column
- **`results/` volume mount** so exports appear on the host for git
- **Skip CPU LoRA by default**; PEFT load uses the same 8-bit / dtype policy as the base model
- **`quality_score`** weighted toward ROUGE / BERT / faithfulness (heuristics are diagnostic only)

---

## Metrics

A weighted **`quality_score`** (0–1) blends available metrics for Grafana and summaries.

> **The denominator is the full weight table, not the metrics that were present.**
> This matters for the comparison the dashboards make on every panel. A RAG row carries
> `retrieval_hit_at_k` (0.14) and `faithfulness` (0.14); a baseline row carries neither,
> because there is no retrieval to score. Dividing by "the weights I found" gave the
> baseline row a denominator 0.28 smaller and scaled its remaining metrics up to
> compensate — so baseline and RAG scores sat on different scales while dashboard 02
> subtracted one from the other. An absent metric now contributes 0, which reads
> correctly: an approach that does no retrieval earns no retrieval quality.
>
> Baseline `quality_score` is therefore **lower than in runs exported before this
> change**, and the two are not comparable. The old number was inflated. `rougeL`
> remains the metric to use for "did RAG help?" and is unaffected.

### Tier 1 — Reference-based (primary)

Ground truth from `prompts/evaluation_prompts.txt` (`question|answer`, from step 1b).

| Metric | Meaning | Higher = better? |
|--------|---------|------------------|
| **rougeL** | LCS overlap with ground truth | ✓ |
| **rouge1 / rouge2** | Unigram / bigram overlap | ✓ |
| **bert_score** | Semantic similarity | ✓ |

### Tier 2 — RAG-specific

| Metric | Meaning | Higher = better? |
|--------|---------|------------------|
| **retrieval_hit_at_k** | Retrieved chunks contain the answer span | ✓ |
| **faithfulness** | Response tokens supported by context | ✓ |
| **judge_groundedness** | Optional LLM 1–5 score | ✓ |

### Tier 3 — Heuristic (diagnostic only)

`domain_relevance`, `coherence`, `answer_relevancy` — do **not** treat as primary decision metrics.

### Tier 4 — Latency / hardware

| Metric | Meaning | Prefer |
|--------|---------|--------|
| **time_to_response** | Retrieval + generation (the wait for an answer) | lower |
| **tokens_per_sec** | Decode throughput | higher |
| **generation_time** | LLM only (CUDA-synced on GPU); folded into time_to_response | lower |
| **retrieval_time** | pgvector search | lower |

Human summaries (`results/latest/README.md`, `by_question.md`) show `rougeL`,
`bert_score`, `faithfulness`, `quality_score`, `time_to_response`, and
`tokens_per_sec`. Device flags, prompt sizes, retrieval microseconds, and
heuristic scores (`answer_relevancy`, `coherence`, …) stay in the CSV / JSON.
`quality_score` **falls** on RAG when `retrieval_hit_at_k` is 0 even if `rougeL`
improved — use `rougeL` to judge "did RAG help?" and `time_to_response` /
`tokens_per_sec` to judge devices.

**Reading device columns on a GGUF run.** `device` is now taken from what the engine
actually did, not from what the process could see. That distinction is load-bearing:
`Dockerfile.app` installs the **CPU** llama.cpp wheel on CUDA 13 hosts, so a GGUF leg
of a "cuda" run offloads nothing and is correctly labelled `cpu`. The `n_gpu_layers`
column (0 = CPU, -1 = all layers) records it per row and appears on the runtime
dashboard. Runs exported before this change labelled those rows `cuda` with
`cuda_used=1.0`, which made the Transformers-vs-GGUF comparison a GPU-vs-CPU
comparison in disguise — treat their `*_gguf | cuda` columns as CPU numbers.

`speed_chars_per_sec` and `cuda_used` remain in Postgres for Grafana ops panels
but are not headline comparison metrics.

**GPU speedup** = `time_to_response_cpu ÷ time_to_response_gpu` (e.g. `4.2×`).

### Where metrics land

| Store | Use |
|-------|-----|
| **`results/`** | Commit-friendly snapshots |
| **MLflow** :5000 | Parent stage runs + GenAI traces/assessments |
| **Prometheus** :9090 | Live gauges |
| **Grafana** :3000 | Dashboards |
| **Postgres** `evaluation_metrics` | SQL / Grafana |

### Expected pattern

```
baseline          → lowest rougeL
rag               → ↑ rougeL, ↑ faithfulness; ↓ tokens_per_sec (longer prompts)
fine_tuned        → small style shift, similar rougeL
fine_tuned + RAG  → same RAG quality lift, same latency cost
CPU vs GPU        → quality within noise; GPU 6–15× faster time_to_response
```

### Visualization: by question

```
results/latest/README.md          ← start here (summary + hardware)
results/latest/by_question.md     ← every question, side by side
```

Also: `by_question.json`, `by_question_quality.csv`, `by_question_latency.csv`.

---

## Capturing results for git

```bash
# Automatic at end of run_pipeline.sh, or:
docker compose exec -T app python scripts/07_export_results.py
```

```bash
git add results/
git commit -m "results: Phi-3 RAG eval on arXiv corpus"
```

**Committed:** JSON / CSV / Markdown under `results/`  
**Not committed:** PDFs, weights, Docker volumes, HF cache

---

## Services

| Service | URL | Purpose |
|---------|-----|---------|
| MLflow | http://localhost:5000 | Experiment tracking (all stages → **gguf-demo**) |
| Prometheus | http://localhost:9090 | Scrapes persistent app `:8000/metrics` |
| Grafana | http://localhost:3000 | Dashboards (admin / admin) |
| Postgres | localhost:5432 | pgvector + metrics |

### MLflow — GenAI vs Model Training

MLflow 3’s UI toggle:

| Toggle | What it shows | What this demo logs |
|--------|---------------|---------------------|
| **GenAI** | Traces + assessments | One live trace per question (`retrieve` / `generate`), scores as feedback |
| **Model Training** | Classic runs | **One parent run per stage×device** (e.g. `rag@cuda`) with mean metrics + lineage tags |

**Layout:**

```text
Experiment: gguf-demo
└── Evaluation run  (baseline@cuda | rag@cuda | fine_tuned@cuda | …)
    ├── Aggregated metrics: mean rougeL, bert_score, quality_score, latency, …
    ├── Tags: registered_model, model_version, approach, device
    └── Traces (one per question)  ← GenAI UI
         ├── retrieve / generate (live @mlflow.trace on RAGPipeline)
         └── Assessments: rougeL, faithfulness, quality_score, …
```

Stages call ``mlflow.genai.evaluate`` with custom scorers wrapping this repo’s `Evaluator`
(`src/genai_scorers.py` + `src/eval_runner.py`). Prometheus/Postgres still get per-question
rows for Grafana; MLflow is the experiment-compare + debug layer.

How to view:

1. Open http://localhost:5000  
2. **GenAI** → **Experiments** → **`gguf-demo`** → **Traces** (open a trace → Assessments)  
3. **Model Training** → same experiment → runs named `baseline@cuda`, `rag@cuda`, …  
4. **Models** → `phi-3-mini-gguf-demo` for registry versions tagged on those runs  

Ignore empty older GenAI experiment names (`pipeline_smoke`, `baseline_evaluation`, …) unless you re-run under those names; new work goes to **`gguf-demo`**.

Smoke-check (parent run + assessments; no full model load):

```bash
docker compose exec -T app python - <<'PY'
import mlflow
from mlflow.entities import SpanType
from src.hardware import detect_hardware
from src.mlflow_tracker import MLflowTracker

t = MLflowTracker("readme_smoke", hardware=detect_hardware())
with t.stage_run("smoke", params={"readme": True}, lineage={"registered_model": "phi-3-mini-gguf-demo"}):
    with mlflow.start_span(name="eval.smoke", span_type=SpanType.CHAIN) as root:
        root.set_inputs({"question": "Does GenAI tracing work?"})
        root.set_outputs({"answer": "yes"})
    t.log_evaluation(
        approach="smoke",
        question="Does GenAI tracing work?",
        response="yes",
        metrics={"rougeL": 0.5, "bert_score": 0.8, "generation_time": 0.2},
        context="optional retrieved chunk text",
    )
print("logged parent run + assessments to", t.experiment_name)
PY
# Then: GenAI → gguf-demo → Traces; Model Training → smoke@<device>
```

### Prometheus — how to query in the UI

Prometheus scrapes the **always-on** metrics server inside `app` (`scripts/metrics_server.py` on `:8000`). Eval scripts are short-lived `docker compose exec` processes; they write into `PROMETHEUS_MULTIPROC_DIR` and the metrics server aggregates them.

#### 1. Confirm the scrape is healthy

1. Open http://localhost:9090/targets  
2. Job **`rag-evaluation`** → target `app:8000` should be **UP** (last scrape &lt; 1m)  
3. If **DOWN**: recreate the app so it runs the metrics server:

```bash
docker compose up -d --force-recreate app
docker compose logs -f app   # expect: metrics_server listening on 0.0.0.0:8000
```

#### 2. Use the Graph explorer

1. Open http://localhost:9090/graph  
2. Switch to the **Table** or **Graph** tab  
3. Paste a query (below) → **Execute**  
4. For time series, set the range to **Last 15m** / **Last 1h** while a pipeline is running  
5. Optional: **Add graph** / compare two queries with the same time range  

#### 3. What is collected (metric → meaning)

| PromQL | Type | Meaning |
|--------|------|---------|
| `rag_metrics_server_up` | gauge | `1` while the persistent `:8000` exporter is alive |
| `rag_metrics_server_heartbeat_unixtime` | gauge | Last heartbeat unix time |
| `cuda_available` | gauge | `1` if the last eval process saw CUDA |
| `cuda_device_count` | gauge | GPU count from the last eval process |
| `evaluation_requests_total` | counter | Q&A evals finished (labels: `device`, `approach`) |
| `evaluation_duration_seconds` | histogram | End-to-end latency observations (`device`, `approach`). Buckets run 1s → 2500s — see the note under the p50/p95 queries below |
| `response_quality_score` | gauge | Latest blended quality score (`device`) |
| `domain_relevance_score` | gauge | Latest heuristic domain score |
| `context_utilization_score` | gauge | Latest context-overlap score (RAG) |
| `retrieval_hit_at_k` | gauge | Latest retrieval hit@k (RAG) |
| `faithfulness_score` | gauge | Latest faithfulness proxy (RAG) |

Label values you will see:

- `device`: `cuda` or `cpu`  
- `approach`: `baseline`, `rag`, `fine_tuned`, `fine_tuned_with_rag`, …  

#### 4. Useful queries to paste

**Is the exporter up?**
```promql
rag_metrics_server_up
```

**How many evaluations so far (by approach)?**
```promql
sum by (approach, device) (evaluation_requests_total)
```

**Eval rate (per minute) while the pipeline runs:**
```promql
sum by (approach) (rate(evaluation_requests_total[5m])) * 60
```

**Latest quality by device:**
```promql
response_quality_score
```

**p50 / p95 latency (seconds) by approach:**
```promql
histogram_quantile(0.50, sum by (le, approach) (rate(evaluation_duration_seconds_bucket[15m])))
```
```promql
histogram_quantile(0.95, sum by (le, approach) (rate(evaluation_duration_seconds_bucket[15m])))
```

> **Bucket sizing matters here, and it is not the library default.** `prometheus_client`'s
> default histogram buckets are built for HTTP handlers and stop at 10 seconds. A local
> Phi-3 answer in this project takes 8–962 seconds, so with the defaults *every*
> observation landed in the `+Inf` overflow bucket and both queries above returned
> `+Inf` — for months, including on the Live Ops dashboard that publishes them.
> `EVALUATION_DURATION_BUCKETS` in `src/mlflow_tracker.py` now runs 1s → 2500s.
> If you change the ladder, old `evaluation_duration_seconds` data is not comparable
> across the change: the series set changes with it.

**RAG faithfulness / hit@k (latest gauges):**
```promql
faithfulness_score
```
```promql
retrieval_hit_at_k
```

**CUDA status:**
```promql
cuda_available
```

#### 5. Raw scrape (optional)

```bash
curl -s http://localhost:8000/metrics | head
curl -s 'http://localhost:9090/api/v1/query?query=evaluation_requests_total'
```

Gauges show the **most recent** eval process values (multiprocess `livemostrecent`).
Counters and histograms accumulate across eval processes *and* across restarts of the
app container: the exporter keeps the multiproc files written by exited eval scripts
rather than clearing them at startup, which used to discard the history of every
completed run on each rebuild. Set `RESET_METRICS=1` on the app service when you
genuinely want a clean slate.

Grafana **Live Ops** reads the same series during a run; **By Question** / **Quality & Latency** use Postgres, not Prometheus.

### Grafana dashboards (provisioned)

| Dashboard | When | Scope |
|-----------|------|-------|
| **gguf-demo · By Question** | After a run — same layout as `by_question.md` | Run picker |
| **gguf-demo · Quality & Latency** | Aggregates + GPU speedup, and A/B against an earlier run | Run picker |
| **gguf-demo · Live Ops** | While the pipeline is running (Prometheus) | Time picker |
| **gguf-demo · Transformers vs GGUF** | Same model, two engines (`baseline` vs `baseline_gguf`) | Run picker |

The three Postgres dashboards are scoped by a **Run** picker, not the time picker — these
are discrete benchmark runs, not a time series, and the Postgres volume outlives them. Pick
the run at the top; every panel follows it, and the run header names the `run_id` and the
`results/runs/<run_id>/` folder the same numbers were exported to. The time picker is hidden
there because no panel filtered on it. **Live Ops** is a live Prometheus scrape and keeps its
time picker.

Rows written before run identity was added to the schema have no `run_id`, so they appear in
no run and are excluded from every panel. They are not backfilled — they belong to no run.

```bash
docker compose up -d prometheus grafana
docker compose restart grafana   # if panels missing
```

---

## Configuration

`config/config.yaml`:

| Key | Default | Notes |
|-----|---------|-------|
| `llm.model` | `microsoft/Phi-3-mini-4k-instruct` | Transformers Hub id (safetensors) |
| `llm.do_sample` | `false` | Greedy eval |
| `gguf.repo_id` | `microsoft/Phi-3-mini-4k-instruct-gguf` | Official GGUF package |
| `gguf.filename` | `Phi-3-mini-4k-instruct-q4.gguf` | Q4_K_M (~2.2 GB) |
| `gguf.n_gpu_layers` | `-1` | Offload all layers if llama.cpp has CUDA |
| `evaluation.llm_judge` | `false` | Slower groundedness judge |
| `evaluation.bertscore` | `true` | Disable to speed up |
| `vector_store.top_k` | `4` | Chunks per question |

---

## Project layout

```
.
├── config/config.yaml
├── data/papers/             # PDFs (gitignored)
├── data/processed/          # Working artifacts (gitignored)
├── results/                 # Exported runs (commit)
├── scripts/                 # 00–09 + run_pipeline.sh
├── src/                     # RAG, llm engines, evaluator, hardware, export
├── src/llm/                 # LlmEngine port: Transformers + GGUF implementations
├── grafana/provisioning/
├── docker-compose.yml
├── Dockerfile.app
└── pyproject.toml
```

---

## Packaging & build args

```bash
pip install -e .                    # local Python (optional)
docker compose build app            # CPU-only default
docker compose -f docker-compose.yml -f docker-compose.gpu.yml build app  # cu130
TORCH_INDEX_URL=https://download.pytorch.org/whl/cu126 \
  docker compose -f docker-compose.yml -f docker-compose.gpu.yml build app
PRELOAD_MODELS=true docker compose build app   # bake models into image
```

| Build arg | Default | Purpose |
|-----------|---------|---------|
| `TORCH_INDEX_URL` | CPU wheels | GPU overlay defaults to cu130; use `…/cu126` for older drivers |
| `PRELOAD_MODELS` | `false` | Download models at build time |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `cuda: False` in container | Confirm `nvidia-smi -L` and the Docker NVIDIA runtime, then rerun with `COMPUTE_DEVICE=cuda` |
| No eval prompts | Run `01b_generate_qa_pairs.py` |
| Old Postgres schema | Auto-migrates on connect — every eval step adds any missing columns |
| Empty host `results/` | Confirm `./results:/app/results` mount; re-export |
| OOM during CPU LoRA | Keep `SKIP_CPU_FINETUNE=1` (default) |
| Grafana empty | `docker compose up -d prometheus grafana` then open **By Question** |
| MLflow looks empty | Open **Experiments → gguf-demo** (not Default); confirm `MLFLOW_TRACKING_URI` |
| Prometheus target DOWN | `docker compose up -d --force-recreate app` — app must run `metrics_server.py` |

---

## Local install (app outside Docker)

```bash
pip install -e .
export POSTGRES_HOST=localhost MLFLOW_TRACKING_URI=http://localhost:5000
python scripts/check_cuda.py
```

Easiest path is still **all services in Compose** and scripts via `docker compose exec -T app …`.
