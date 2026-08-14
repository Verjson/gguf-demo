# Run summary — 2026-08-14_032911_cpu

- **Exported:** 2026-08-14T04:13:22.087914+00:00
- **Device:** cuda (cuda_available=True)
- **GPU:** NVIDIA GeForce RTX 4080 Laptop GPU
- **Model:** microsoft/Phi-3-mini-4k-instruct
- **Postgres metric rows:** 226

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
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.0727</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.0714</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.0957</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.0952</td>
</tr>
<tr>
<td style="text-align:left">bert_score</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.8051</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.8080</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.8078</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.8107</td>
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
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.3625</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.4189</td>
</tr>
<tr>
<td style="text-align:left">quality_score</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.2987</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.2987</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.2773</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.2765</td>
</tr>
<tr>
<td style="text-align:left">generation_time</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;9.9804</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;14.3553</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;51.9744</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;44.8746</td>
</tr>
<tr>
<td style="text-align:left">cuda_used</td>
<td style="text-align:right">0.0000</td>
<td style="text-align:right">0.0000</td>
<td style="text-align:right">0.0000</td>
<td style="text-align:right">0.0000</td>
</tr>
<tr>
<td style="text-align:left">answer_relevancy</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.4223</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.4223</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.5555</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.3332</td>
</tr>
<tr>
<td style="text-align:left">coherence</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.1357</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.1148</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.1992</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.1713</td>
</tr>
<tr>
<td style="text-align:left">completion_tokens</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;49.6000</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;48.6000</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;112.5333</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;98.8667</td>
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
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.1224</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.1281</td>
</tr>
<tr>
<td style="text-align:left">cuda_device_count</td>
<td style="text-align:right">0.0000</td>
<td style="text-align:right">0.0000</td>
<td style="text-align:right">0.0000</td>
<td style="text-align:right">0.0000</td>
</tr>
<tr>
<td style="text-align:left">domain_relevance</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.0179</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.0179</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.0615</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.0615</td>
</tr>
<tr>
<td style="text-align:left">factual_density</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.0215</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.0125</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.0526</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.0510</td>
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
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;254.9333</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;249.8000</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;470.4000</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;417.9333</td>
</tr>
<tr>
<td style="text-align:left">retrieval_time</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.0000</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.0000</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.1805</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.1714</td>
</tr>
<tr>
<td style="text-align:left">rouge1</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.1034</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.1029</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.1335</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.1345</td>
</tr>
<tr>
<td style="text-align:left">rouge2</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.0121</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.0118</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.0174</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.0170</td>
</tr>
<tr>
<td style="text-align:left">speed_chars_per_sec</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;25.4852</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;17.1536</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;9.1941</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;9.7215</td>
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
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;9.9804</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;14.3553</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;52.1549</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;45.0460</td>
</tr>
<tr>
<td style="text-align:left">tokens_per_sec</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;4.9042</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.3396</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.1279</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;2.2037</td>
</tr>
</tbody>
</table>
**RAG quality_score vs baseline:** -7.4%
**Fine-tuned+RAG quality_score vs baseline:** -7.1%


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
