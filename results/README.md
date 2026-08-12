# Run results (committed to git)

This folder stores **structured evaluation outputs** — small JSON, CSV, and Markdown files suitable for version control.

Large artifacts stay **out** of git (see root `.gitignore`):
- PDFs → `data/papers/` (re-download with script 01)
- Model weights → `models/` (re-train with script 05)
- Docker volumes → MLflow DB, pgvector tables (rebuilt locally)

## Layout

```
results/
├── latest/                    ← start here after a pipeline run
│   ├── by_question.md         ← PRIMARY VIEW (question × approach × device)
│   ├── by_question.json
│   ├── by_question_quality.csv
│   ├── by_question_latency.csv
│   ├── summary.md             ← aggregate CPU vs CUDA deltas
│   ├── manifest.json
│   └── ...
└── runs/
    ├── <stamp>_cpu/
    ├── <stamp>_cuda/
    └── <stamp>_cpu_vs_cuda/   ← combined by_question view after dual-device run
```

## How to read results

**Best for visualization:** open `by_question.md` or `summary.md` in an HTML-capable
Markdown preview. Per-row cells are tinted 🟢 best / 🟡 mid / 🔴 worst (latency metrics
use lower-is-better). Emoji markers remain visible on GitHub even when background
colors are stripped.

**Storage** (MLflow / Postgres) remains one row per question × approach × device so Grafana can filter and chart freely.

## Export after a pipeline run

```bash
# Automatic at end of step 6:
docker compose exec app python scripts/06_fine_tuned_evaluation.py

# Or manually anytime processed artifacts exist:
docker compose exec app python scripts/07_export_results.py
```

## Commit results

From the **host** repo root (paths are bind-mounted from `./data` and `./results`):

```bash
git add results/
git status   # verify only JSON/CSV/MD — no PDFs or models
git commit -m "results: baseline vs RAG vs fine-tune on Phi-3 (CUDA)"
```

Compare runs over time with:

```bash
diff results/runs/RUN_A/summary.md results/runs/RUN_B/summary.md
```

Or inspect `comparison_summary` in each run's `comparison_report.json`.
