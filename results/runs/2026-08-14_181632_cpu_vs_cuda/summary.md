# Aggregate CPU vs CUDA — 2026-08-14_181632_cpu vs 2026-08-14_181632_cuda

- **Generated:** 2026-08-14T19:22:07.701212+00:00
- **CPU:** Intel(R) Core(TM) i9-14900HX (28 of 32 threads)
- **GPU:** NVIDIA GeForce RTX 4080 Laptop GPU
- **Per-question breakdown:** [by_question.md](./by_question.md)

Quality (`rougeL`, `bert_score`, `faithfulness`) should stay within noise across
devices. **Speed is the device story:** lower `time_to_response`, higher `tokens_per_sec`.

## What changed

### Speed (CPU → GPU, `time_to_response`)

- **baseline:** 11.78s → 2.25s (**5.2×** faster on GPU)
- **fine_tuned:** 15.17s → 1.79s (**8.5×** faster on GPU)
- **fine_tuned_with_rag:** 47.66s → 4.09s (**11.7×** faster on GPU)
- **rag:** 61.73s → 4.07s (**15.2×** faster on GPU)

### Quality (RAG vs baseline, `rougeL`)

- **CPU:** RAG rougeL 0.0727 → 0.0952 (+31.0%)
- **GPU:** RAG rougeL 0.0711 → 0.0983 (+38.2%)

## Approach: `baseline`

<table>
<thead><tr>
<th>Metric</th>
<th>CPU</th>
<th>CUDA</th>
</tr></thead>
<tbody>
<tr>
<td style="text-align:left">rougeL</td>
<td style="text-align:right">0.0727</td>
<td style="text-align:right">0.0711</td>
</tr>
<tr>
<td style="text-align:left">bert_score</td>
<td style="text-align:right">0.8051</td>
<td style="text-align:right">0.8084</td>
</tr>
<tr>
<td style="text-align:left">quality_score</td>
<td style="text-align:right">0.2987</td>
<td style="text-align:right">0.2985</td>
</tr>
<tr>
<td style="text-align:left">time_to_response</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;11.7762</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;2.2476</td>
</tr>
<tr>
<td style="text-align:left">tokens_per_sec</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;4.1979</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;22.4846</td>
</tr>
</tbody>
</table>

## Approach: `fine_tuned`

<table>
<thead><tr>
<th>Metric</th>
<th>CPU</th>
<th>CUDA</th>
</tr></thead>
<tbody>
<tr>
<td style="text-align:left">rougeL</td>
<td style="text-align:right">0.0784</td>
<td style="text-align:right">0.0670</td>
</tr>
<tr>
<td style="text-align:left">bert_score</td>
<td style="text-align:right">0.8047</td>
<td style="text-align:right">0.8060</td>
</tr>
<tr>
<td style="text-align:left">quality_score</td>
<td style="text-align:right">0.3008</td>
<td style="text-align:right">0.2929</td>
</tr>
<tr>
<td style="text-align:left">time_to_response</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;15.1746</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.7926</td>
</tr>
<tr>
<td style="text-align:left">tokens_per_sec</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;3.2474</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;27.0436</td>
</tr>
</tbody>
</table>

## Approach: `fine_tuned_with_rag`

<table>
<thead><tr>
<th>Metric</th>
<th>CPU</th>
<th>CUDA</th>
</tr></thead>
<tbody>
<tr>
<td style="text-align:left">rougeL</td>
<td style="text-align:right">0.0949</td>
<td style="text-align:right">0.0900</td>
</tr>
<tr>
<td style="text-align:left">bert_score</td>
<td style="text-align:right">0.8111</td>
<td style="text-align:right">0.8076</td>
</tr>
<tr>
<td style="text-align:left">faithfulness</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.4163</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.3749</td>
</tr>
<tr>
<td style="text-align:left">quality_score</td>
<td style="text-align:right">0.2762</td>
<td style="text-align:right">0.2773</td>
</tr>
<tr>
<td style="text-align:left">time_to_response</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;47.6570</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;4.0863</td>
</tr>
<tr>
<td style="text-align:left">tokens_per_sec</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.0176</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;26.5340</td>
</tr>
<tr>
<td style="text-align:left">context_utilization</td>
<td style="text-align:right">0.1247</td>
<td style="text-align:right">0.1268</td>
</tr>
</tbody>
</table>

## Approach: `rag`

<table>
<thead><tr>
<th>Metric</th>
<th>CPU</th>
<th>CUDA</th>
</tr></thead>
<tbody>
<tr>
<td style="text-align:left">rougeL</td>
<td style="text-align:right">0.0952</td>
<td style="text-align:right">0.0983</td>
</tr>
<tr>
<td style="text-align:left">bert_score</td>
<td style="text-align:right">0.8107</td>
<td style="text-align:right">0.8085</td>
</tr>
<tr>
<td style="text-align:left">faithfulness</td>
<td style="text-align:right">0.4189</td>
<td style="text-align:right">0.4109</td>
</tr>
<tr>
<td style="text-align:left">quality_score</td>
<td style="text-align:right">0.2765</td>
<td style="text-align:right">0.2869</td>
</tr>
<tr>
<td style="text-align:left">time_to_response</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;61.7314</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;4.0667</td>
</tr>
<tr>
<td style="text-align:left">tokens_per_sec</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;1.7391</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;29.1540</td>
</tr>
<tr>
<td style="text-align:left">context_utilization</td>
<td style="text-align:right">0.1281</td>
<td style="text-align:right">0.1367</td>
</tr>
</tbody>
</table>
