# Run summary — 2026-08-14_032911_cpu

- **Exported:** 2026-08-14T12:41:26.596203+00:00
- **Device:** cpu
- **CPU:** Intel(R) Core(TM) i9-14900HX (28 of 32 threads)
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
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.0727</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.0714</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.0957</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.0952</td>
</tr>
<tr>
<td style="text-align:left">bert_score</td>
<td style="text-align:right">0.8051</td>
<td style="text-align:right">0.8080</td>
<td style="text-align:right">0.8078</td>
<td style="text-align:right">0.8107</td>
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
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.2987</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.2987</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.2773</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.2765</td>
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
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.2037</td>
</tr>
<tr>
<td style="text-align:left">context_utilization</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">0.1224</td>
<td style="text-align:right">0.1281</td>
</tr>
</tbody>
</table>
**RAG rougeL vs baseline:** +31.0%
**RAG time_to_response vs baseline:** 4.5× longer (10.0s → 45.0s)


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
