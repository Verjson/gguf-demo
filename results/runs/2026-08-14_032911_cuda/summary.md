# Run summary — 2026-08-14_032911_cuda

- **Exported:** 2026-08-14T04:15:45.271470+00:00
- **Device:** cuda (cuda_available=True)
- **GPU:** NVIDIA GeForce RTX 4080 Laptop GPU
- **Model:** microsoft/Phi-3-mini-4k-instruct
- **Postgres metric rows:** 271

## How to read improvements

Higher is better for quality metrics (ROUGE, BERTScore, faithfulness, quality_score).
Lower is better for `generation_time` / `time_to_response` (latency).
`retrieval_hit_at_k` shows whether retrieved chunks contain the ground-truth answer.

Per-metric cells are colored **green (best) / yellow (mid) / red (worst)** across approaches (open in an HTML-capable Markdown preview).

## Comparison by approach

_Cell colors (per row): 🟢 best · 🟡 mid · 🔴 worst (latency metrics lower-is-better; skipped for cuda_available, cuda_device_count, cuda_used). Colors show in HTML-capable Markdown previews._

<table>
<thead><tr>
<th>Metric</th>
<th>baseline</th>
<th>fine_tuned</th>
<th>fine_tuned_with_rag</th>
<th>rag</th>
</tr></thead>
<tbody>
<tr>
<td style="text-align:left">rougeL</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.0711</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.0659</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.0896</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.0983</td>
</tr>
<tr>
<td style="text-align:left">bert_score</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.8084</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.8060</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.8078</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.8085</td>
</tr>
<tr>
<td style="text-align:left">retrieval_hit_at_k</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">0.0000</td>
<td style="text-align:right">0.0000</td>
</tr>
<tr>
<td style="text-align:left">faithfulness</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.3696</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.4109</td>
</tr>
<tr>
<td style="text-align:left">quality_score</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.2985</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.2923</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.2765</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.2869</td>
</tr>
<tr>
<td style="text-align:left">generation_time</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;1.7355</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.6129</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.1969</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;3.2961</td>
</tr>
<tr>
<td style="text-align:left">cuda_used</td>
<td style="text-align:right">1.0000</td>
<td style="text-align:right">1.0000</td>
<td style="text-align:right">1.0000</td>
<td style="text-align:right">1.0000</td>
</tr>
<tr>
<td style="text-align:left">answer_relevancy</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.4223</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.3853</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.5507</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.5507</td>
</tr>
<tr>
<td style="text-align:left">coherence</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.1370</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.1154</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.2232</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.2462</td>
</tr>
<tr>
<td style="text-align:left">completion_tokens</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;50.9333</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;48.6000</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;104.8000</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;114.3333</td>
</tr>
<tr>
<td style="text-align:left">context_chars</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">1390.6000</td>
<td style="text-align:right">1390.6000</td>
</tr>
<tr>
<td style="text-align:left">context_utilization</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.1229</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.1367</td>
</tr>
<tr>
<td style="text-align:left">cuda_device_count</td>
<td style="text-align:right">1.0000</td>
<td style="text-align:right">1.0000</td>
<td style="text-align:right">1.0000</td>
<td style="text-align:right">1.0000</td>
</tr>
<tr>
<td style="text-align:left">domain_relevance</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.0179</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.0179</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.0641</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.0641</td>
</tr>
<tr>
<td style="text-align:left">factual_density</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.0205</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.0205</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.0506</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.0464</td>
</tr>
<tr>
<td style="text-align:left">n_chunks_retrieved</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">4.0000</td>
<td style="text-align:right">4.0000</td>
</tr>
<tr>
<td style="text-align:left">prompt_chars</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;94.0667</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;94.0667</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1617.6667</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1617.6667</td>
</tr>
<tr>
<td style="text-align:left">prompt_tokens</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;15.3333</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;15.3333</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;645.9333</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;645.9333</td>
</tr>
<tr>
<td style="text-align:left">response_chars</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;259.9333</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;247.0667</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;456.0667</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;505.6667</td>
</tr>
<tr>
<td style="text-align:left">retrieval_time</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.0000</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.0000</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.1406</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.1403</td>
</tr>
<tr>
<td style="text-align:left">rouge1</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.1008</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.0927</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.1298</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.1457</td>
</tr>
<tr>
<td style="text-align:left">rouge2</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.0102</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.0102</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.0131</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.0151</td>
</tr>
<tr>
<td style="text-align:left">speed_chars_per_sec</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;155.9477</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;147.1812</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;143.7188</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;158.9133</td>
</tr>
<tr>
<td style="text-align:left">technical_accuracy</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.0067</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.0067</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.0000</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.0000</td>
</tr>
<tr>
<td style="text-align:left">time_to_response</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;1.7355</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.6129</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.3374</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;3.4364</td>
</tr>
<tr>
<td style="text-align:left">tokens_per_sec</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;30.8010</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;29.2189</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;32.0534</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;34.9928</td>
</tr>
</tbody>
</table>
**RAG quality_score vs baseline:** -3.9%
**Fine-tuned+RAG quality_score vs baseline:** -7.4%


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
