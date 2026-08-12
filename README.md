# gguf-demo

Local, containerized demo that compares **baseline LLM**, **RAG (Postgres/pgvector)**, and **LoRA fine-tuning** on a small arXiv paper corpus — with **MLflow**, **Prometheus**, **Postgres**, and **Grafana**.

Packaging uses **`pyproject.toml`**. Exported metrics land in **`results/`** (safe to commit).

---

## Easiest way to run

From a machine with Docker (GPU recommended):

```bash
# 1. Start everything (app defaults to CUDA 11.8 PyTorch)
docker compose up -d
docker compose exec -T app python scripts/check_cuda.py   # expect PASS on GPU hosts

# 2. Full evaluation (CPU then GPU per step; ~45–90+ min on a laptop GPU)
chmod +x scripts/run_pipeline.sh
./scripts/run_pipeline.sh
```

Then open:

| What | Where |
|------|--------|
| **Results (start here)** | [`results/latest/by_question.md`](results/latest/by_question.md) |
| Device summary | `results/latest/summary.md` (or `results/runs/*_cpu_vs_cuda/`) |
| Grafana | http://localhost:3000 (admin / admin) → **By Question** |
| MLflow | http://localhost:5000 |

CPU-only hosts:

```bash
TORCH_INDEX_URL=https://download.pytorch.org/whl/cpu docker compose build app
docker compose up -d
SKIP_CPU_FINETUNE=0 ./scripts/run_pipeline.sh   # trains LoRA on CPU once
```

---

## Minimum hardware, memory, and disk

| Resource | Minimum (CPU-only) | Recommended (this demo) |
|----------|--------------------|-------------------------|
| **CPU** | 4 cores | 8+ cores |
| **RAM** | **16 GB** system (tight) | **24–32 GB** system |
| **GPU** | None (slow; hours) | NVIDIA **8 GB+** VRAM (e.g. RTX 3060 / 4070 / 4080) |
| **Disk free** | **~25 GB** | **40–60 GB** comfortable |
| **OS** | Linux or **WSL2** + Docker Desktop | WSL2 + recent NVIDIA Windows driver |

### What uses the space / RAM

| Item | Approx. size |
|------|----------------|
| App image (cu118 torch + deps) | ~3–4 GB |
| Hugging Face cache (Phi-3 + MiniLM + BERTScore) | ~8–12 GB first run |
| LoRA adapters under `models/` | ~100–300 MB |
| Postgres + MLflow volumes | ~1–2 GB |
| Papers + `results/` | < 500 MB |
| Docker Desktop / WSL VM disk | leave headroom for layers |

### Runtime expectations (Phi-3-mini, ~5 papers, greedy decode)

| Mode | Full `./scripts/run_pipeline.sh` |
|------|----------------------------------|
| **GPU** (e.g. RTX 4080, 12 GB) | typically **45–90 minutes** (CPU eval passes still run for comparison) |
| **CPU-only** | often **several hours**; skip or shorten evals if needed |

**Notes**

- Default pipeline **skips CPU LoRA** (`SKIP_CPU_FINETUNE=1`) — Phi-3 LoRA on CPU is RAM-heavy and slow.
- Eval uses **greedy decoding** (`do_sample: false`) for stable quality numbers.
- `cuda_used=1.0` means CUDA was **available** to the process (not a per-kernel probe).

---

## What this project does

| Approach | Description |
|----------|-------------|
| **Baseline** | Local LLM answers from parameters alone |
| **RAG** | Retrieve PDF chunks from pgvector, then generate |
| **Fine-tuned** | LoRA adapters trained on instruction Q&A from the corpus |
| **Fine-tuned + RAG** | Domain-tuned model with retrieval |

Every answer logs **quality** (ROUGE, BERTScore, faithfulness, …) and **latency** (`time_to_response` = retrieval + generation) tagged by **device** (`cpu` / `cuda`).

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
│              scripts/ + src/ + local Phi-3 LLM                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites (WSL2 + NVIDIA)

1. **Windows:** NVIDIA driver with WSL support  
2. **WSL:** `nvidia-smi` works  
3. **Docker:** GPU enabled (Docker Desktop → Resources → GPU, or `nvidia-container-toolkit`)  
4. First build uses **cu118** torch by default:

```bash
docker compose build app    # already done if you rebuilt recently
docker compose up -d
docker compose exec -T app python scripts/check_cuda.py
```

---

## Full pipeline details

```bash
./scripts/run_pipeline.sh
```

Shared setup runs once. Metric steps run **CPU first**, then **GPU** (if CUDA works):

| Step | CPU | GPU |
|------|-----|-----|
| 1 / 1b Download + QA | once | — |
| 2 Baseline | ✓ | ✓ |
| 3 Create RAG DB | once | — |
| 4 RAG evaluation | ✓ | ✓ |
| 5 Fine-tune LoRA | optional (`SKIP_CPU_FINETUNE=0`) | ✓ (default) |
| 6 Comparison | ✓ | ✓ |
| 7 Export | `…_cpu` | `…_cuda` |
| 8 Device summary | — | `…_cpu_vs_cuda/` |

```bash
SKIP_CPU_FINETUNE=0 ./scripts/run_pipeline.sh   # also train LoRA on CPU
```

After code/compose changes:

```bash
docker compose up -d --force-recreate app
```

### Manual steps

| Script | What happens |
|--------|--------------|
| `check_cuda.py` | Verify GPU inside the container |
| `01_download_papers.py` | Fetch ~5 arXiv `cs.LG` PDFs → `data/papers/` |
| `01b_generate_qa_pairs.py` | Extractive Q&A → prompts + train pairs |
| `02_baseline_evaluation.py` | LLM-only answers |
| `03_create_rag_db.py` | Chunk, embed, store in pgvector |
| `04_rag_evaluation.py` | Retrieve + generate |
| `05_fine_tune.py` | LoRA → `models/fine_tuned/adapter_*` |
| `06_fine_tuned_evaluation.py` | Baseline / FT / FT+RAG comparison |
| `07_export_results.py` | Snapshot → `results/runs/<id>/` |
| `08_compare_devices.py` | CPU vs CUDA summary |

### Ad-hoc query

```bash
docker compose exec -T app python scripts/00_query.py \
  --prompt "What is the main contribution?" \
  --pdf data/papers/<paper>.pdf
```

Add `--no-rag` for baseline. Add `--judge` for LLM groundedness scoring.

---

## Recent improvements

- **Default cu118 torch** in compose / Dockerfile (override with CPU wheel index if needed)
- **Greedy eval** + **Phi-3 chat template** for more stable, instruction-faithful answers
- **`time_to_response`** as primary latency metric; CPU÷GPU speedup in exports and Grafana
- **Question-centric views** — `by_question.md` / CSV + Grafana **By Question** dashboard
- **RAG rebuild** clears collections (no duplicate chunks); Postgres connect is lazy
- **Schema auto-migrate** on metrics write; quoted `"rougeL"` column
- **`results/` volume mount** so exports appear on the host for git
- **Skip CPU LoRA by default**; PEFT load uses the same 8-bit / dtype policy as the base model
- **`quality_score`** weighted toward ROUGE / BERT / faithfulness (heuristics are diagnostic only)

---

## Metrics

A weighted **`quality_score`** (0–1) blends available metrics for Grafana and summaries.

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
| **time_to_response** | Retrieval + generation | lower |
| **generation_time** | LLM only (CUDA-synced on GPU) | lower |
| **retrieval_time** | pgvector search | lower |
| **speed_chars_per_sec** | Throughput proxy | higher |
| **cuda_used** | 1.0 if CUDA available | — |

**GPU speedup** = `time_to_response_cpu ÷ time_to_response_gpu` (e.g. `4.2×`).

### Where metrics land

| Store | Use |
|-------|-----|
| **`results/`** | Commit-friendly snapshots |
| **MLflow** :5000 | Per-question runs |
| **Prometheus** :9090 | Live gauges |
| **Grafana** :3000 | Dashboards |
| **Postgres** `evaluation_metrics` | SQL / Grafana |

### Expected pattern

```
baseline          → lowest rougeL / faithfulness
rag               → ↑ rougeL, ↑ hit@k, ↑ faithfulness
fine_tuned        → modest domain lift
fine_tuned + RAG  → often best quality_score
```

### Visualization: by question

```
results/latest/by_question.md
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
| MLflow | http://localhost:5000 | Experiment tracking |
| Prometheus | http://localhost:9090 | Scrapes app `:8000/metrics` |
| Grafana | http://localhost:3000 | Dashboards (admin / admin) |
| Postgres | localhost:5432 | pgvector + metrics |

### Grafana dashboards (provisioned)

| Dashboard | When |
|-----------|------|
| **gguf-demo · By Question** | After a run — same layout as `by_question.md` |
| **gguf-demo · Quality & Latency** | Aggregates + GPU speedup |
| **gguf-demo · Live Ops** | While the pipeline is running |

```bash
docker compose up -d prometheus grafana
docker compose restart grafana   # if panels missing
```

---

## Configuration

`config/config.yaml`:

| Key | Default | Notes |
|-----|---------|-------|
| `llm.model` | `microsoft/Phi-3-mini-4k-instruct` | Base model |
| `llm.do_sample` | `false` | Greedy eval |
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
├── scripts/                 # 00–08 + run_pipeline.sh
├── src/                     # RAG, evaluator, hardware, export
├── grafana/provisioning/
├── docker-compose.yml
├── Dockerfile.app
└── pyproject.toml
```

---

## Packaging & build args

```bash
pip install -e .                    # local Python (optional)
docker compose build app            # cu118 by default
TORCH_INDEX_URL=https://download.pytorch.org/whl/cpu docker compose build app
PRELOAD_MODELS=true docker compose build app   # bake models into image
```

| Build arg | Default | Purpose |
|-----------|---------|---------|
| `TORCH_INDEX_URL` | cu118 wheels | Use `…/cpu` without a GPU |
| `PRELOAD_MODELS` | `false` | Download models at build time |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `cuda: False` in container | Enable GPU in Docker; `gpus: all`; rebuild (cu118 default) |
| No eval prompts | Run `01b_generate_qa_pairs.py` |
| Old Postgres schema | Auto-migrates on insert; or apply `scripts/migrate_metrics_table.sql` |
| Empty host `results/` | Confirm `./results:/app/results` mount; re-export |
| OOM during CPU LoRA | Keep `SKIP_CPU_FINETUNE=1` (default) |
| Grafana empty | `docker compose up -d prometheus grafana` then open **By Question** |

---

## Local install (app outside Docker)

```bash
pip install -e .
export POSTGRES_HOST=localhost MLFLOW_TRACKING_URI=http://localhost:5000
python scripts/check_cuda.py
```

Easiest path is still **all services in Compose** and scripts via `docker compose exec -T app …`.
