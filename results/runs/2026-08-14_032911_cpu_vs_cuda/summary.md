# Aggregate CPU vs CUDA — 2026-08-14_032911_cpu vs 2026-08-14_032911_cuda

- **Generated:** 2026-08-14T12:41:29.559765+00:00
- **CPU:** Intel(R) Core(TM) i9-14900HX (28 of 32 threads)
- **GPU:** NVIDIA GeForce RTX 4080 Laptop GPU
- **Per-question breakdown:** [by_question.md](./by_question.md)

Quality (`rougeL`, `bert_score`, `faithfulness`) should stay within noise across
devices. **Speed is the device story:** lower `time_to_response`, higher `tokens_per_sec`.

## What changed

### Speed (CPU → GPU, `time_to_response`)

- **baseline:** 9.98s → 1.74s (**5.8×** faster on GPU)
- **fine_tuned:** 14.36s → 1.61s (**8.9×** faster on GPU)
- **fine_tuned_with_rag:** 52.15s → 3.34s (**15.6×** faster on GPU)
- **rag:** 45.05s → 3.44s (**13.1×** faster on GPU)

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
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;9.9804</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.7355</td>
</tr>
<tr>
<td style="text-align:left">tokens_per_sec</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;4.9042</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;30.8010</td>
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
<td style="text-align:right">0.0714</td>
<td style="text-align:right">0.0659</td>
</tr>
<tr>
<td style="text-align:left">bert_score</td>
<td style="text-align:right">0.8080</td>
<td style="text-align:right">0.8060</td>
</tr>
<tr>
<td style="text-align:left">quality_score</td>
<td style="text-align:right">0.2987</td>
<td style="text-align:right">0.2923</td>
</tr>
<tr>
<td style="text-align:left">time_to_response</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;14.3553</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.6129</td>
</tr>
<tr>
<td style="text-align:left">tokens_per_sec</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;3.3396</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;29.2189</td>
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
<td style="text-align:right">0.0957</td>
<td style="text-align:right">0.0896</td>
</tr>
<tr>
<td style="text-align:left">bert_score</td>
<td style="text-align:right">0.8078</td>
<td style="text-align:right">0.8078</td>
</tr>
<tr>
<td style="text-align:left">faithfulness</td>
<td style="text-align:right">0.3625</td>
<td style="text-align:right">0.3696</td>
</tr>
<tr>
<td style="text-align:left">quality_score</td>
<td style="text-align:right">0.2773</td>
<td style="text-align:right">0.2765</td>
</tr>
<tr>
<td style="text-align:left">time_to_response</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;52.1549</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;3.3374</td>
</tr>
<tr>
<td style="text-align:left">tokens_per_sec</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.1279</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;32.0534</td>
</tr>
<tr>
<td style="text-align:left">context_utilization</td>
<td style="text-align:right">0.1224</td>
<td style="text-align:right">0.1229</td>
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
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;45.0460</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;3.4364</td>
</tr>
<tr>
<td style="text-align:left">tokens_per_sec</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.2037</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;34.9928</td>
</tr>
<tr>
<td style="text-align:left">context_utilization</td>
<td style="text-align:right">0.1281</td>
<td style="text-align:right">0.1367</td>
</tr>
</tbody>
</table>
