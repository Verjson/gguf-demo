# Run summary — 2026-08-12_212503_cuda

- **Exported:** 2026-08-12T22:09:49.059271+00:00
- **Device:** cuda (cuda_available=True)
- **GPU:** NVIDIA GeForce RTX 4080 Laptop GPU
- **Model:** microsoft/Phi-3-mini-4k-instruct
- **Postgres metric rows:** 61

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
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.0807</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.0768</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.0400</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.0829</td>
</tr>
<tr>
<td style="text-align:left">bert_score</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.8190</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.8178</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.8168</td>
</tr>
<tr>
<td style="text-align:left">retrieval_hit_at_k</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.0000</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.1333</td>
</tr>
<tr>
<td style="text-align:left">faithfulness</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.2222</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.4684</td>
</tr>
<tr>
<td style="text-align:left">quality_score</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.3117</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.3088</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.0683</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.3145</td>
</tr>
<tr>
<td style="text-align:left">generation_time</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;229.1559</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;214.9315</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;3.4558</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;587.0071</td>
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
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.4880</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.4880</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.2000</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.5614</td>
</tr>
<tr>
<td style="text-align:left">coherence</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.1416</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.1451</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.0000</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.3925</td>
</tr>
<tr>
<td style="text-align:left">context_utilization</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.0252</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.1733</td>
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
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.0179</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.0179</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.0000</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.0385</td>
</tr>
<tr>
<td style="text-align:left">factual_density</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.0166</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.0166</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.0000</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.0689</td>
</tr>
<tr>
<td style="text-align:left">retrieval_time</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.0000</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.0000</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.0203</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.5658</td>
</tr>
<tr>
<td style="text-align:left">rouge1</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.1158</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.1080</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.0400</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.1179</td>
</tr>
<tr>
<td style="text-align:left">rouge2</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.0157</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.0137</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.0000</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.0243</td>
</tr>
<tr>
<td style="text-align:left">speed_chars_per_sec</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;1.5691</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;1.6983</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;19.6770</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;1.0913</td>
</tr>
<tr>
<td style="text-align:left">technical_accuracy</td>
<td style="text-align:right">0.0000</td>
<td style="text-align:right">0.0000</td>
<td style="text-align:right">0.0000</td>
<td style="text-align:right">0.0000</td>
</tr>
<tr>
<td style="text-align:left">time_to_response</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;229.1559</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;214.9315</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;3.4761</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;587.5729</td>
</tr>
</tbody>
</table>
**RAG quality_score vs baseline:** +0.9%
**Fine-tuned+RAG quality_score vs baseline:** -78.1%


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
