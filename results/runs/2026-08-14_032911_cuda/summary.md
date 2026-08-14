# Run summary — 2026-08-14_032911_cuda

- **Exported:** 2026-08-14T12:41:27.816811+00:00
- **Device:** cuda
- **GPU:** NVIDIA GeForce RTX 4080 Laptop GPU
- **Model:** microsoft/Phi-3-mini-4k-instruct
- **Metric rows (this run):** 75

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
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.0659</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.0896</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.0983</td>
</tr>
<tr>
<td style="text-align:left">bert_score</td>
<td style="text-align:right">0.8084</td>
<td style="text-align:right">0.8060</td>
<td style="text-align:right">0.8078</td>
<td style="text-align:right">0.8085</td>
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
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.2923</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.2765</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.2869</td>
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
<tr>
<td style="text-align:left">context_utilization</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">0.1229</td>
<td style="text-align:right">0.1367</td>
</tr>
</tbody>
</table>
**RAG rougeL vs baseline:** +38.2%
**RAG time_to_response vs baseline:** 2.0× longer (1.7s → 3.4s)


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
