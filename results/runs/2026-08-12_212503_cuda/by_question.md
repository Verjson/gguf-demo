# Results by question

Each question shows quality **and** latency across approach × device.

- **Quality:** higher `quality_score` / `rougeL` is better
- **Time to response:** `retrieval_time` + `generation_time` (seconds) — **lower is better**
- **GPU speedup:** CPU time ÷ GPU time (values **> 1×** mean GPU was faster)
- **Colors:** 🟢 best · 🟡 mid · 🔴 worst within each row (HTML Markdown preview; emoji also visible on GitHub)

_Generated: 2026-08-12T22:09:49.076211+00:00_

## Overview — quality (`quality_score`)

<table>
<thead><tr>
<th>Question</th>
<th><code>baseline|cpu</code></th>
<th><code>baseline|cuda</code></th>
<th><code>rag|cpu</code></th>
<th><code>rag|cuda</code></th>
<th><code>fine_tuned|cpu</code></th>
<th><code>fine_tuned|cuda</code></th>
<th><code>fine_tuned_with_rag|cpu</code></th>
<th><code>fine_tuned_with_rag|cuda</code></th>
</tr></thead>
<tbody>
<tr>
<td style="text-align:left">According to this passage, what is the main claim or cont...</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.280</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.267</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.274</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.290</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.280</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.267</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left">Summarize the contribution of 'Automated Literature Revie...</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.438</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.438</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.566</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.566</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.394</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.394</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left">Summarize the contribution of 'Lightweight and Direct Doc...</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.375</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.375</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.372</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.372</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.375</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.375</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left">What experimental result or finding is reported here?</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.312</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.256</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.243</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.237</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.312</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.256</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left">What is the paper 'MUST-RAG: MUSical Text Question Answer...</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.348</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.348</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.537</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.537</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.348</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.348</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left">What limitation or future work is mentioned in this text?</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.264</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.264</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.218</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.218</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.264</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.264</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.068</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.068</td>
</tr>
<tr>
<td style="text-align:left">What method or approach is described in this excerpt?</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.325</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.317</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.252</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.258</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.325</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.317</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left">What problem does this passage say the work addresses?</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.293</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.282</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.299</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.293</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.293</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.282</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
</tr>
</tbody>
</table>


## Overview — time to response (seconds, lower is better)

<table>
<thead><tr>
<th>Question</th>
<th><code>baseline|cpu</code></th>
<th><code>baseline|cuda</code></th>
<th><code>rag|cpu</code></th>
<th><code>rag|cuda</code></th>
<th><code>fine_tuned|cpu</code></th>
<th><code>fine_tuned|cuda</code></th>
<th><code>fine_tuned_with_rag|cpu</code></th>
<th><code>fine_tuned_with_rag|cuda</code></th>
</tr></thead>
<tbody>
<tr>
<td style="text-align:left">According to this passage, what is the main claim or cont...</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;108.647</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;106.750</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;333.631</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;333.631</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;110.668</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;110.668</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left">Summarize the contribution of 'Automated Literature Revie...</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;375.760</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;525.176</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;761.570</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;761.570</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;528.042</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;528.042</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left">Summarize the contribution of 'Lightweight and Direct Doc...</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;306.410</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;402.611</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;686.257</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;686.257</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;375.141</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;375.141</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left">What experimental result or finding is reported here?</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;218.251</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;225.246</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;553.985</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;553.985</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;199.493</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;199.493</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left">What is the paper 'MUST-RAG: MUSical Text Question Answer...</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;425.570</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;596.087</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;773.050</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;773.050</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;494.006</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;494.006</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left">What limitation or future work is mentioned in this text?</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;106.667</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;103.111</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;132.147</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;132.147</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;108.413</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;108.413</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;3.476</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;3.476</td>
</tr>
<tr>
<td style="text-align:left">What method or approach is described in this excerpt?</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;261.276</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;309.851</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;718.763</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;718.763</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;275.957</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;275.957</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left">What problem does this passage say the work addresses?</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;106.667</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;105.332</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;649.562</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;649.562</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;109.227</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;109.227</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
</tr>
</tbody>
</table>


---

## Q1. According to this passage, what is the main claim or contribution?

<table>
<thead><tr>
<th>Approach × Device</th>
<th>quality_score</th>
<th>rougeL</th>
<th>bert_score</th>
<th>retrieval_hit_at_k</th>
<th>faithfulness</th>
<th>retrieval_time</th>
<th>generation_time</th>
<th>time_to_response</th>
<th>speed_chars_per_sec</th>
</tr></thead>
<tbody>
<tr>
<td style="text-align:left"><code>baseline|cpu</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.280</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.062</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.818</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;108.647</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;108.647</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;1.243</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline|cuda</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.267</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.049</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.813</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;106.750</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;106.750</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.265</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cpu</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.274</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.044</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.816</td>
<td style="text-align:right">0.000</td>
<td style="text-align:right">0.514</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.618</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;333.013</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;333.631</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;1.057</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cuda</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.290</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.093</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.814</td>
<td style="text-align:right">0.000</td>
<td style="text-align:right">0.514</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.618</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;333.013</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;333.631</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;1.057</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cpu</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.280</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.062</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.818</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;110.668</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;110.668</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;1.220</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cuda</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.267</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.049</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.813</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;110.668</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;110.668</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;1.220</td>
</tr>
</tbody>
</table>

**CPU → GPU speedup (time_to_response):**
- **baseline:** 108.65s (CPU) → 106.75s (GPU) = **1.0×** faster time-to-response
- **fine_tuned:** 110.67s (CPU) → 110.67s (GPU) = **1.0×** faster time-to-response
- **rag:** 333.63s (CPU) → 333.63s (GPU) = **1.0×** faster time-to-response

<details><summary>Sample answers</summary>

- **`baseline|cpu`:** I'm sorry, but it seems like there was no passage provided for me to analyze. Could you please provide the passage you're referring to?
- **`baseline|cuda`:** I'm sorry, but it seems like there was no passage provided for me to analyze. Could you please provide the passage you're referring to?
- **`rag|cpu`:** Question: What are the key assumptions about the nature of RAG documents in the discussed setup?  Question: What are the failure cases observed during the attack analysis?  Question: What are the financial costs involved in launching the attack?  Question: What potential count...
- **`rag|cuda`:** Question: What are the key assumptions about the nature of RAG documents in the discussed setup?  Question: What are the failure cases observed during the attack analysis?  Question: What are the financial costs involved in launching the attack?  Question: What potential count...
- **`fine_tuned|cpu`:** I'm sorry, but it seems like there was no passage provided for me to analyze. Could you please provide the passage you're referring to?
- **`fine_tuned|cuda`:** I'm sorry, but it seems like there was no passage provided for me to analyze. Could you please provide the passage you're referring to?

</details>

## Q2. Summarize the contribution of 'Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation'.

<table>
<thead><tr>
<th>Approach × Device</th>
<th>quality_score</th>
<th>rougeL</th>
<th>bert_score</th>
<th>retrieval_hit_at_k</th>
<th>faithfulness</th>
<th>retrieval_time</th>
<th>generation_time</th>
<th>time_to_response</th>
<th>speed_chars_per_sec</th>
</tr></thead>
<tbody>
<tr>
<td style="text-align:left"><code>baseline|cpu</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.438</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.204</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.871</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;375.760</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;375.760</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.457</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.438</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.204</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.871</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;525.176</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;525.176</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;2.473</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.566</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.197</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.878</td>
<td style="text-align:right">1.000</td>
<td style="text-align:right">0.699</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.138</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;761.432</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;761.570</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;1.685</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cuda</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.566</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.197</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.878</td>
<td style="text-align:right">1.000</td>
<td style="text-align:right">0.699</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.138</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;761.432</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;761.570</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;1.685</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cpu</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.394</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.144</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.854</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;528.042</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;528.042</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;3.568</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cuda</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.394</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.144</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.854</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;528.042</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;528.042</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;3.568</td>
</tr>
</tbody>
</table>

**CPU → GPU speedup (time_to_response):**
- **baseline:** 375.76s (CPU) → 525.18s (GPU) = **0.7×** faster time-to-response
- **fine_tuned:** 528.04s (CPU) → 528.04s (GPU) = **1.0×** faster time-to-response
- **rag:** 761.57s (CPU) → 761.57s (GPU) = **1.0×** faster time-to-response

<details><summary>Sample answers</summary>

- **`baseline|cpu`:** The contribution of 'Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation' lies in the development of a system that streamlines the process of conducting literature reviews in academic research. This system leverages Natural Language Pr...
- **`baseline|cuda`:** The contribution of 'Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation' lies in the development of a system that streamlines the process of conducting literature reviews in academic research. This system leverages Natural Language Pr...
- **`rag|cpu`:** The research paper titled "Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation" by Nurshat Fateh Ali, Shakil Mosharrof, and Md. Mahdi Mohtasim focuses on developing an automated system for generating literature reviews. The primary obj...
- **`rag|cuda`:** The research paper titled "Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation" by Nurshat Fateh Ali, Shakil Mosharrof, and Md. Mahdi Mohtasim focuses on developing an automated system for generating literature reviews. The primary obj...
- **`fine_tuned|cpu`:** The contribution of 'Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation' lies in the development of a system that streamlines the process of conducting literature reviews in academic research. This system leverages Natural Language Pr...
- **`fine_tuned|cuda`:** The contribution of 'Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation' lies in the development of a system that streamlines the process of conducting literature reviews in academic research. This system leverages Natural Language Pr...

</details>

## Q3. Summarize the contribution of 'Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval'.

<table>
<thead><tr>
<th>Approach × Device</th>
<th>quality_score</th>
<th>rougeL</th>
<th>bert_score</th>
<th>retrieval_hit_at_k</th>
<th>faithfulness</th>
<th>retrieval_time</th>
<th>generation_time</th>
<th>time_to_response</th>
<th>speed_chars_per_sec</th>
</tr></thead>
<tbody>
<tr>
<td style="text-align:left"><code>baseline|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.375</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.124</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.841</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;306.410</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;306.410</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;2.513</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline|cuda</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.375</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.124</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.841</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;402.611</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;402.611</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;1.913</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cpu</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.372</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.198</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.850</td>
<td style="text-align:right">0.000</td>
<td style="text-align:right">0.568</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.663</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;685.594</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;686.257</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;1.200</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cuda</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.372</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.198</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.850</td>
<td style="text-align:right">0.000</td>
<td style="text-align:right">0.568</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.663</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;685.594</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;686.257</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;1.200</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.375</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.124</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.841</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;375.141</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;375.141</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;2.053</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cuda</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.375</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.124</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.841</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;375.141</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;375.141</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;2.053</td>
</tr>
</tbody>
</table>

**CPU → GPU speedup (time_to_response):**
- **baseline:** 306.41s (CPU) → 402.61s (GPU) = **0.8×** faster time-to-response
- **fine_tuned:** 375.14s (CPU) → 375.14s (GPU) = **1.0×** faster time-to-response
- **rag:** 686.26s (CPU) → 686.26s (GPU) = **1.0×** faster time-to-response

<details><summary>Sample answers</summary>

- **`baseline|cpu`:** The contribution of 'Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval' lies in enhancing the efficiency and accuracy of information retrieval systems. By focusing on lightweight algorithms, the approach minimizes computational overhea...
- **`baseline|cuda`:** The contribution of 'Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval' lies in enhancing the efficiency and accuracy of information retrieval systems. By focusing on lightweight algorithms, the approach minimizes computational overhea...
- **`rag|cpu`:** The contribution of "Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval" is focused on improving the efficiency and effectiveness of Generative Information Retrieval (GenIR) models. GenIR models, which are based on large pre-trained lan...
- **`rag|cuda`:** The contribution of "Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval" is focused on improving the efficiency and effectiveness of Generative Information Retrieval (GenIR) models. GenIR models, which are based on large pre-trained lan...
- **`fine_tuned|cpu`:** The contribution of 'Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval' lies in enhancing the efficiency and accuracy of information retrieval systems. By focusing on lightweight algorithms, the approach minimizes computational overhea...
- **`fine_tuned|cuda`:** The contribution of 'Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval' lies in enhancing the efficiency and accuracy of information retrieval systems. By focusing on lightweight algorithms, the approach minimizes computational overhea...

</details>

## Q4. What experimental result or finding is reported here?

<table>
<thead><tr>
<th>Approach × Device</th>
<th>quality_score</th>
<th>rougeL</th>
<th>bert_score</th>
<th>retrieval_hit_at_k</th>
<th>faithfulness</th>
<th>retrieval_time</th>
<th>generation_time</th>
<th>time_to_response</th>
<th>speed_chars_per_sec</th>
</tr></thead>
<tbody>
<tr>
<td style="text-align:left"><code>baseline|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.312</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.081</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.833</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;218.251</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;218.251</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;1.049</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.256</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.015</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.776</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;225.246</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;225.246</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;1.017</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cpu</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.243</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.073</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.812</td>
<td style="text-align:right">0.000</td>
<td style="text-align:right">0.292</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.622</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;553.363</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;553.985</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.922</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cuda</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.237</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.060</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.794</td>
<td style="text-align:right">0.000</td>
<td style="text-align:right">0.292</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.622</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;553.363</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;553.985</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.922</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.312</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.081</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.833</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;199.493</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;199.493</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.148</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.256</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.015</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.776</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;199.493</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;199.493</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.148</td>
</tr>
</tbody>
</table>

**CPU → GPU speedup (time_to_response):**
- **baseline:** 218.25s (CPU) → 225.25s (GPU) = **1.0×** faster time-to-response
- **fine_tuned:** 199.49s (CPU) → 199.49s (GPU) = **1.0×** faster time-to-response
- **rag:** 553.98s (CPU) → 553.98s (GPU) = **1.0×** faster time-to-response

<details><summary>Sample answers</summary>

- **`baseline|cpu`:** I'm sorry, but it seems like you haven't provided any context or content for me to identify an experimental result or finding. Please provide the relevant information or details about the experiment or study you are referring to.
- **`baseline|cuda`:** I'm sorry, but it seems like you haven't provided any context or content for me to identify an experimental result or finding. Please provide the relevant information or details about the experiment or study you are referring to.
- **`rag|cpu`:** The experimental results reported here are the performance metrics of various retrieval-based models on the ICU readmission prediction task. The models evaluated are REMed, VanillaEHR-RAGp, and Mistral 7b. The performance metrics include accuracy, precision, recall, F1-score, ...
- **`rag|cuda`:** The experimental results reported here are the performance metrics of various retrieval-based models on the ICU readmission prediction task. The models evaluated are REMed, VanillaEHR-RAGp, and Mistral 7b. The performance metrics include accuracy, precision, recall, F1-score, ...
- **`fine_tuned|cpu`:** I'm sorry, but it seems like you haven't provided any context or content for me to identify an experimental result or finding. Please provide the relevant information or details about the experiment or study you are referring to.
- **`fine_tuned|cuda`:** I'm sorry, but it seems like you haven't provided any context or content for me to identify an experimental result or finding. Please provide the relevant information or details about the experiment or study you are referring to.

</details>

## Q5. What is the paper 'MUST-RAG: MUSical Text Question Answering with Retrieval Augmented Generation' about?

<table>
<thead><tr>
<th>Approach × Device</th>
<th>quality_score</th>
<th>rougeL</th>
<th>bert_score</th>
<th>retrieval_hit_at_k</th>
<th>faithfulness</th>
<th>retrieval_time</th>
<th>generation_time</th>
<th>time_to_response</th>
<th>speed_chars_per_sec</th>
</tr></thead>
<tbody>
<tr>
<td style="text-align:left"><code>baseline|cpu</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.348</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.090</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.827</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;425.570</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;425.570</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;3.969</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline|cuda</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.348</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.090</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.827</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;596.087</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;596.087</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;2.833</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.537</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.157</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.848</td>
<td style="text-align:right">1.000</td>
<td style="text-align:right">0.716</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.673</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;772.377</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;773.050</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;1.788</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cuda</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.537</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.157</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.848</td>
<td style="text-align:right">1.000</td>
<td style="text-align:right">0.716</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.673</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;772.377</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;773.050</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;1.788</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cpu</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.348</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.090</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.827</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;494.006</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;494.006</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.393</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.348</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.090</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.827</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;494.006</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;494.006</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.393</td>
</tr>
</tbody>
</table>

**CPU → GPU speedup (time_to_response):**
- **baseline:** 425.57s (CPU) → 596.09s (GPU) = **0.7×** faster time-to-response
- **fine_tuned:** 494.01s (CPU) → 494.01s (GPU) = **1.0×** faster time-to-response
- **rag:** 773.05s (CPU) → 773.05s (GPU) = **1.0×** faster time-to-response

<details><summary>Sample answers</summary>

- **`baseline|cpu`:** The paper "MUST-RAG: MUSical Text Question Answering with Retrieval Augmented Generation" focuses on developing a system for answering questions about musical texts, such as lyrics or scores, using a combination of retrieval-augmented generation (RAG) and a pre-trained languag...
- **`baseline|cuda`:** The paper "MUST-RAG: MUSical Text Question Answering with Retrieval Augmented Generation" focuses on developing a system for answering questions about musical texts, such as lyrics or scores, using a combination of retrieval-augmented generation (RAG) and a pre-trained languag...
- **`rag|cpu`:** The paper 'MUST-RAG: MUSical Text Question Answering with Retrieval Augmented Generation' by Daeyong Kwon, SeungHeon Doh, and Juhan Nam, from the Graduate School of Culture Technology at KAIST, South Korea, focuses on addressing the limitations of Large Language Models (LLMs) ...
- **`rag|cuda`:** The paper 'MUST-RAG: MUSical Text Question Answering with Retrieval Augmented Generation' by Daeyong Kwon, SeungHeon Doh, and Juhan Nam, from the Graduate School of Culture Technology at KAIST, South Korea, focuses on addressing the limitations of Large Language Models (LLMs) ...
- **`fine_tuned|cpu`:** The paper "MUST-RAG: MUSical Text Question Answering with Retrieval Augmented Generation" focuses on developing a system for answering questions about musical texts, such as lyrics or scores, using a combination of retrieval-augmented generation (RAG) and a pre-trained languag...
- **`fine_tuned|cuda`:** The paper "MUST-RAG: MUSical Text Question Answering with Retrieval Augmented Generation" focuses on developing a system for answering questions about musical texts, such as lyrics or scores, using a combination of retrieval-augmented generation (RAG) and a pre-trained languag...

</details>

## Q6. What limitation or future work is mentioned in this text?

<table>
<thead><tr>
<th>Approach × Device</th>
<th>quality_score</th>
<th>rougeL</th>
<th>bert_score</th>
<th>retrieval_hit_at_k</th>
<th>faithfulness</th>
<th>retrieval_time</th>
<th>generation_time</th>
<th>time_to_response</th>
<th>speed_chars_per_sec</th>
</tr></thead>
<tbody>
<tr>
<td style="text-align:left"><code>baseline|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.264</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.062</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.821</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;106.667</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;106.667</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;1.209</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline|cuda</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.264</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.062</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.821</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;103.111</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;103.111</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;1.251</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cpu</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.218</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.040</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.834</td>
<td style="text-align:right">0.000</td>
<td style="text-align:right">0.222</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.550</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;131.598</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;132.147</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.517</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.218</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.040</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.834</td>
<td style="text-align:right">0.000</td>
<td style="text-align:right">0.222</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.550</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;131.598</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;132.147</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.517</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.264</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.062</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.821</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;108.413</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;108.413</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;1.190</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cuda</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.264</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.062</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.821</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;108.413</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;108.413</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;1.190</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned_with_rag|cpu</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.068</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.040</td>
<td style="text-align:right">—</td>
<td style="text-align:right">0.000</td>
<td style="text-align:right">0.222</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.020</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;3.456</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;3.476</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;19.677</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned_with_rag|cuda</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.068</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.040</td>
<td style="text-align:right">—</td>
<td style="text-align:right">0.000</td>
<td style="text-align:right">0.222</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.020</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;3.456</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;3.476</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;19.677</td>
</tr>
</tbody>
</table>

**CPU → GPU speedup (time_to_response):**
- **baseline:** 106.67s (CPU) → 103.11s (GPU) = **1.0×** faster time-to-response
- **fine_tuned:** 108.41s (CPU) → 108.41s (GPU) = **1.0×** faster time-to-response
- **fine_tuned_with_rag:** 3.48s (CPU) → 3.48s (GPU) = **1.0×** faster time-to-response
- **rag:** 132.15s (CPU) → 132.15s (GPU) = **1.0×** faster time-to-response

<details><summary>Sample answers</summary>

- **`baseline|cpu`:** I'm sorry, but it seems like there was no text provided for me to analyze. Could you please provide the text you're referring to?
- **`baseline|cuda`:** I'm sorry, but it seems like there was no text provided for me to analyze. Could you please provide the text you're referring to?
- **`rag|cpu`:** The text does not explicitly mention any limitations or future work.
- **`rag|cuda`:** The text does not explicitly mention any limitations or future work.
- **`fine_tuned|cpu`:** I'm sorry, but it seems like there was no text provided for me to analyze. Could you please provide the text you're referring to?
- **`fine_tuned|cuda`:** I'm sorry, but it seems like there was no text provided for me to analyze. Could you please provide the text you're referring to?
- **`fine_tuned_with_rag|cpu`:** The text does not explicitly mention any limitations or future work.
- **`fine_tuned_with_rag|cuda`:** The text does not explicitly mention any limitations or future work.

</details>

## Q7. What method or approach is described in this excerpt?

<table>
<thead><tr>
<th>Approach × Device</th>
<th>quality_score</th>
<th>rougeL</th>
<th>bert_score</th>
<th>retrieval_hit_at_k</th>
<th>faithfulness</th>
<th>retrieval_time</th>
<th>generation_time</th>
<th>time_to_response</th>
<th>speed_chars_per_sec</th>
</tr></thead>
<tbody>
<tr>
<td style="text-align:left"><code>baseline|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.325</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.064</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.818</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;261.276</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;261.276</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.527</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.317</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.070</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.796</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;309.851</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;309.851</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;1.288</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cpu</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.252</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.034</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.774</td>
<td style="text-align:right">0.000</td>
<td style="text-align:right">0.508</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.512</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;718.251</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;718.763</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.799</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.258</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.058</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.758</td>
<td style="text-align:right">0.000</td>
<td style="text-align:right">0.508</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.512</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;718.251</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;718.763</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.799</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.325</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.064</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.818</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;275.957</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;275.957</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;1.446</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.317</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.070</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.796</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;275.957</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;275.957</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;1.446</td>
</tr>
</tbody>
</table>

**CPU → GPU speedup (time_to_response):**
- **baseline:** 261.28s (CPU) → 309.85s (GPU) = **0.8×** faster time-to-response
- **fine_tuned:** 275.96s (CPU) → 275.96s (GPU) = **1.0×** faster time-to-response
- **rag:** 718.76s (CPU) → 718.76s (GPU) = **1.0×** faster time-to-response

<details><summary>Sample answers</summary>

- **`baseline|cpu`:** The method or approach described in this excerpt is the scientific method. The scientific method is a systematic and logical approach to discovering how things in the universe work. It involves making observations, forming a hypothesis, conducting experiments, analyzing data, ...
- **`baseline|cuda`:** The method or approach described in this excerpt is the scientific method. The scientific method is a systematic and logical approach to discovering how things in the universe work. It involves making observations, forming a hypothesis, conducting experiments, analyzing data, ...
- **`rag|cpu`:** [MASK_1]: extension [MASK_2]: PageRank [MASK_3]: comprehensive [MASK_4]: PageRank model [MASK_5]: storage issues [MASK_6]: possible alterations [MASK_7]: sensitivity and conditioning [MASK_8]: introduce [MASK_9]: extensive reference list [MASK_10]: exciting areas of future res...
- **`rag|cuda`:** [MASK_1]: extension [MASK_2]: PageRank [MASK_3]: comprehensive [MASK_4]: PageRank model [MASK_5]: storage issues [MASK_6]: possible alterations [MASK_7]: sensitivity and conditioning [MASK_8]: introduce [MASK_9]: extensive reference list [MASK_10]: exciting areas of future res...
- **`fine_tuned|cpu`:** The method or approach described in this excerpt is the scientific method. The scientific method is a systematic and logical approach to discovering how things in the universe work. It involves making observations, forming a hypothesis, conducting experiments, analyzing data, ...
- **`fine_tuned|cuda`:** The method or approach described in this excerpt is the scientific method. The scientific method is a systematic and logical approach to discovering how things in the universe work. It involves making observations, forming a hypothesis, conducting experiments, analyzing data, ...

</details>

## Q8. What problem does this passage say the work addresses?

<table>
<thead><tr>
<th>Approach × Device</th>
<th>quality_score</th>
<th>rougeL</th>
<th>bert_score</th>
<th>retrieval_hit_at_k</th>
<th>faithfulness</th>
<th>retrieval_time</th>
<th>generation_time</th>
<th>time_to_response</th>
<th>speed_chars_per_sec</th>
</tr></thead>
<tbody>
<tr>
<td style="text-align:left"><code>baseline|cpu</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.293</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.074</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.803</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;106.667</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;106.667</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;1.566</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline|cuda</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.282</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.050</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.803</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;105.332</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;105.332</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.585</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.299</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.077</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.804</td>
<td style="text-align:right">0.000</td>
<td style="text-align:right">0.438</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.592</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;648.970</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;649.562</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;1.125</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.293</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.052</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.815</td>
<td style="text-align:right">0.000</td>
<td style="text-align:right">0.438</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.592</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;648.970</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;649.562</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;1.125</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cpu</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.293</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.074</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.803</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;109.227</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;109.227</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;1.529</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cuda</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.282</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.050</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.803</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.000</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;109.227</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;109.227</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;1.529</td>
</tr>
</tbody>
</table>

**CPU → GPU speedup (time_to_response):**
- **baseline:** 106.67s (CPU) → 105.33s (GPU) = **1.0×** faster time-to-response
- **fine_tuned:** 109.23s (CPU) → 109.23s (GPU) = **1.0×** faster time-to-response
- **rag:** 649.56s (CPU) → 649.56s (GPU) = **1.0×** faster time-to-response

<details><summary>Sample answers</summary>

- **`baseline|cpu`:** The passage you provided does not contain any information or context. Please provide the passage you are referring to, so I can help identify the problem it addresses.
- **`baseline|cuda`:** The passage you provided does not contain any information or context. Please provide the passage you are referring to, so I can help identify the problem it addresses.
- **`rag|cpu`:** The passage discusses the issue of generating topic-focused descriptions using a RAG (Retrieval-Augmented Generation) system. It outlines the assumptions about the nature of the RAG documents in their setup, analyzes the failure cases observed during the attack, examines the f...
- **`rag|cuda`:** The passage discusses the issue of generating topic-focused descriptions using a RAG (Retrieval-Augmented Generation) system. It outlines the assumptions about the nature of the RAG documents in their setup, analyzes the failure cases observed during the attack, examines the f...
- **`fine_tuned|cpu`:** The passage you provided does not contain any information or context. Please provide the passage you are referring to, so I can help identify the problem it addresses.
- **`fine_tuned|cuda`:** The passage you provided does not contain any information or context. Please provide the passage you are referring to, so I can help identify the problem it addresses.

</details>
