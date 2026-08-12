# Run summary — 2026-08-12_173828_cuda

- **Exported:** 2026-08-12T17:50:47.532839+00:00
- **Device:** cuda (cuda_available=True)
- **GPU:** NVIDIA GeForce RTX 4080 Laptop GPU
- **Model:** microsoft/Phi-3-mini-4k-instruct
- **Postgres metric rows:** 75

## How to read improvements

Higher is better for quality metrics (ROUGE, BERTScore, faithfulness, quality_score).
Lower is better for `generation_time` (latency).
`retrieval_hit_at_k` shows whether retrieved chunks contain the ground-truth answer.

## Comparison by approach

| Metric | baseline | fine_tuned | fine_tuned_with_rag | rag |
|---|---|---|---|---|
| rougeL | 0.0804 | 0.0863 | 0.0871 | 0.0819 |
| bert_score | 0.8192 | 0.8196 | 0.8165 | 0.8165 |
| retrieval_hit_at_k | — | — | 0.1333 | 0.1333 |
| faithfulness | — | — | 0.4786 | 0.4682 |
| generation_time | 3.3192 | 3.0743 | 6.6189 | 6.3568 |
| cuda_used | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| answer_relevancy | 0.4880 | 0.4880 | 0.5687 | 0.5614 |
| coherence | 0.1423 | 0.1416 | 0.3083 | 0.3942 |
| context_utilization | — | — | 0.1746 | 0.1734 |
| cuda_device_count | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| domain_relevance | 0.0179 | 0.0179 | 0.0385 | 0.0385 |
| factual_density | 0.0162 | 0.0166 | 0.0853 | 0.0692 |
| retrieval_time | 0.0000 | 0.0000 | 0.0130 | 0.0136 |
| rouge1 | 0.1147 | 0.1248 | 0.1270 | 0.1171 |
| rouge2 | 0.0146 | 0.0178 | 0.0281 | 0.0239 |
| speed_chars_per_sec | 118.9653 | 124.4054 | 102.2191 | 106.5727 |
| technical_accuracy | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| time_to_response | 3.3192 | 3.0743 | 6.6319 | 6.3704 |


## Expected improvement pattern

| Approach | What improves |
|----------|----------------|
| **RAG** | rougeL, faithfulness, retrieval_hit@k |
| **Fine-tuned** | domain_relevance, answer style |
| **Fine-tuned + RAG** | best combined quality_score |

## Files in this folder

- `manifest.json` — run metadata
- `comparison_report.json` — full step-06 output
- `baseline_results.json` / `rag_results.json` — per-stage details
- `evaluation_metrics.csv` — all rows from Postgres
- `config.yaml` — config snapshot
