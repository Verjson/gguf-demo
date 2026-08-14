# Run summary — 2026-08-14_181632_cuda

- **Exported:** 2026-08-14T19:22:05.413039+00:00
- **Device:** cuda
- **GPU:** NVIDIA GeForce RTX 4080 Laptop GPU
- **Model:** microsoft/Phi-3-mini-4k-instruct
- **Metric rows (this run):** 105
- **Peak RSS:** 6011 MiB
- **Peak GPU memory:** 87 MiB
- **Model load:** 7.8s

## How to read improvements

Higher is better for `rougeL`, `bert_score`, `faithfulness`.
Lower is better for `time_to_response` (retrieval + generation — the wait for an answer).
Higher is better for `tokens_per_sec`. `quality_score` is a blend and can fall when
RAG's `retrieval_hit_at_k` is 0 even if overlap (`rougeL`) improved — trust rougeL
for 'did RAG help?', and time_to_response / tokens_per_sec for device speed.

Per-metric cells are colored **green (best) / yellow (mid) / red (worst)** across approaches (open in an HTML-capable Markdown preview).

## Comparison by approach

_Cell colors (per row): 🟢 best · 🟡 mid · 🔴 worst across approaches. Differences smaller than measurement noise are left uncolored. Latency (`time_to_response`) is lower-is-better._

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
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.0711</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.0670</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.0900</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.0983</td>
</tr>
<tr>
<td style="text-align:left">bert_score</td>
<td style="text-align:right">0.8084</td>
<td style="text-align:right">0.8060</td>
<td style="text-align:right">0.8076</td>
<td style="text-align:right">0.8085</td>
</tr>
<tr>
<td style="text-align:left">faithfulness</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.3749</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.4109</td>
</tr>
<tr>
<td style="text-align:left">quality_score</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.2985</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.2929</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.2773</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.2869</td>
</tr>
<tr>
<td style="text-align:left">time_to_response</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;2.2476</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.7926</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;4.0863</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;4.0667</td>
</tr>
<tr>
<td style="text-align:left">tokens_per_sec</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;22.4846</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;27.0436</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;26.5340</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;29.1540</td>
</tr>
<tr>
<td style="text-align:left">context_utilization</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">0.1268</td>
<td style="text-align:right">0.1367</td>
</tr>
</tbody>
</table>
**RAG rougeL vs baseline:** +38.2%
**RAG time_to_response vs baseline:** 1.8× longer (2.2s → 4.1s)


## Expected improvement pattern

| Approach | What improves |
|----------|----------------|
| **RAG** | rougeL, faithfulness (costs time_to_response) |
| **Fine-tuned** | modest style shift, similar rougeL |
| **Fine-tuned + RAG** | same RAG quality lift, same latency cost |
| **CPU vs GPU** | quality within noise; GPU wins time_to_response and tokens_per_sec |

## Files in this folder

- `by_question.md` — every question, side by side
- `manifest.json` — run metadata and CPU/GPU identity
- `evaluation_metrics.csv` — one row per question (full column set)
- `comparison_report.json` / `baseline_results.json` / `rag_results.json` — raw stage output
- `config.yaml` — config snapshot
