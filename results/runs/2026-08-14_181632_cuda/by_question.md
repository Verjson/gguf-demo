# Results by question

Each question shows quality **and** latency across approach × device.

- **rougeL:** overlap with the ground-truth answer — **higher is better** (the RAG quality story)
- **Time to response:** retrieval + generation (seconds) — **lower is better** (the device story)
- **tokens_per_sec:** decode throughput — **higher is better**
- **Colors:** 🟢 best · 🟡 mid · 🔴 worst within each row; ties within noise are left uncolored

_Generated: 2026-08-14T19:22:05.427436+00:00_

## Overview — overlap with ground truth (`rougeL`)

<table>
<thead><tr>
<th>Question</th>
<th><code>baseline|cpu</code></th>
<th><code>baseline|cuda</code></th>
<th><code>baseline_gguf|cpu</code></th>
<th><code>baseline_gguf|cuda</code></th>
<th><code>rag|cpu</code></th>
<th><code>rag|cuda</code></th>
<th><code>rag_gguf|cpu</code></th>
<th><code>rag_gguf|cuda</code></th>
<th><code>fine_tuned|cpu</code></th>
<th><code>fine_tuned|cuda</code></th>
<th><code>fine_tuned_with_rag|cpu</code></th>
<th><code>fine_tuned_with_rag|cuda</code></th>
</tr></thead>
<tbody>
<tr>
<td style="text-align:left">According to this passage, what is the main claim or cont...</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.066</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.066</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.100</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.100</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.098</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.092</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.098</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.098</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.066</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.066</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.092</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.099</td>
</tr>
<tr>
<td style="text-align:left">Summarize the contribution of 'Automated Literature Revie...</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.273</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.204</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.264</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.197</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.144</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left">Summarize the contribution of 'Lightweight and Direct Doc...</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.147</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.147</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.167</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.167</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.211</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.199</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.174</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.174</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.150</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.147</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.200</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.200</td>
</tr>
<tr>
<td style="text-align:left">What experimental result or finding is reported here?</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.042</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.042</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.080</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.080</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.062</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.076</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.102</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.102</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.042</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.042</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.062</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.063</td>
</tr>
<tr>
<td style="text-align:left">What is the paper 'MUST-RAG: MUSical Text Question Answer...</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.088</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.090</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.126</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.157</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.090</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left">What is the paper 'Riddle Me This! Stealthy Membership In...</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.174</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.207</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.177</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.177</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.261</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.164</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.227</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.227</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.208</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.194</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.273</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.164</td>
</tr>
<tr>
<td style="text-align:left">What limitation or future work is mentioned in this text?</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.058</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.058</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.107</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.107</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.037</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.109</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.074</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.074</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.058</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.058</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.037</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.037</td>
</tr>
<tr>
<td style="text-align:left">What method or approach is described in this excerpt?</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.070</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.070</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.020</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.058</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.070</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left">What problem does this passage say the work addresses?</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.128</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.102</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.116</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.116</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.099</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.094</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.088</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.088</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.149</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.067</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.099</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.094</td>
</tr>
</tbody>
</table>


## Overview — time to response (seconds, lower is better)

<table>
<thead><tr>
<th>Question</th>
<th><code>baseline|cpu</code></th>
<th><code>baseline|cuda</code></th>
<th><code>baseline_gguf|cpu</code></th>
<th><code>baseline_gguf|cuda</code></th>
<th><code>rag|cpu</code></th>
<th><code>rag|cuda</code></th>
<th><code>rag_gguf|cpu</code></th>
<th><code>rag_gguf|cuda</code></th>
<th><code>fine_tuned|cpu</code></th>
<th><code>fine_tuned|cuda</code></th>
<th><code>fine_tuned_with_rag|cpu</code></th>
<th><code>fine_tuned_with_rag|cuda</code></th>
</tr></thead>
<tbody>
<tr>
<td style="text-align:left">According to this passage, what is the main claim or cont...</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;8.241</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.439</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;10.051</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;7.673</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;45.783</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;2.832</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;28.732</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;10.304</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;9.357</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.771</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;28.728</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.610</td>
</tr>
<tr>
<td style="text-align:left">Summarize the contribution of 'Automated Literature Revie...</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;302.478</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;525.176</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;962.158</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;761.570</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;528.042</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left">Summarize the contribution of 'Lightweight and Direct Doc...</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;31.561</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;5.699</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;8.846</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;9.544</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;55.702</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;4.324</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;33.606</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;13.986</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;38.793</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;5.057</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;56.326</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;5.432</td>
</tr>
<tr>
<td style="text-align:left">What experimental result or finding is reported here?</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;9.698</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.797</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;8.285</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;7.724</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;108.056</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.252</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;39.398</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;19.738</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;14.064</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.655</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;74.180</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.355</td>
</tr>
<tr>
<td style="text-align:left">What is the paper 'MUST-RAG: MUSical Text Question Answer...</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;302.652</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;596.087</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;961.546</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;773.050</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;494.006</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left">What is the paper 'Riddle Me This! Stealthy Membership In...</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;29.341</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;5.365</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;11.948</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;9.891</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;57.921</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;5.556</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;35.478</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;15.527</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;37.332</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;3.987</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;60.546</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;5.130</td>
</tr>
<tr>
<td style="text-align:left">What limitation or future work is mentioned in this text?</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;8.876</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;1.726</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;7.814</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;7.925</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;16.163</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;2.509</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;29.912</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;11.215</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;9.065</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.094</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;16.452</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.997</td>
</tr>
<tr>
<td style="text-align:left">What method or approach is described in this excerpt?</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;259.139</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;309.851</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;957.854</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;718.763</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;275.957</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left">What problem does this passage say the work addresses?</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;8.252</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.755</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;8.378</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;7.526</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;38.792</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.402</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;17.474</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;7.333</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;10.737</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.122</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;33.090</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.471</td>
</tr>
</tbody>
</table>


## Overview — throughput (`tokens_per_sec`, higher is better)

<table>
<thead><tr>
<th>Question</th>
<th><code>baseline|cpu</code></th>
<th><code>baseline|cuda</code></th>
<th><code>baseline_gguf|cpu</code></th>
<th><code>baseline_gguf|cuda</code></th>
<th><code>rag|cpu</code></th>
<th><code>rag|cuda</code></th>
<th><code>rag_gguf|cpu</code></th>
<th><code>rag_gguf|cuda</code></th>
<th><code>fine_tuned|cpu</code></th>
<th><code>fine_tuned|cuda</code></th>
<th><code>fine_tuned_with_rag|cpu</code></th>
<th><code>fine_tuned_with_rag|cuda</code></th>
</tr></thead>
<tbody>
<tr>
<td style="text-align:left">According to this passage, what is the main claim or cont...</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.762</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;21.536</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;12.736</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;16.682</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.807</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;26.881</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.478</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;12.595</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.313</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;17.508</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.525</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;29.308</td>
</tr>
<tr>
<td style="text-align:left">Summarize the contribution of 'Automated Literature Revie...</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left">Summarize the contribution of 'Lightweight and Direct Doc...</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.056</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;22.459</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;14.470</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;13.411</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.304</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;30.627</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.830</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;9.251</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.300</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;25.311</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.279</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;24.353</td>
</tr>
<tr>
<td style="text-align:left">What experimental result or finding is reported here?</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.640</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;25.045</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;15.450</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;16.573</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;1.187</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;31.298</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.264</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;6.534</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.200</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;27.195</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;1.730</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;28.783</td>
</tr>
<tr>
<td style="text-align:left">What is the paper 'MUST-RAG: MUSical Text Question Answer...</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left">What is the paper 'Riddle Me This! Stealthy Membership In...</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.362</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;23.859</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;10.713</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;12.941</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.218</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;20.616</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.635</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;8.360</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.429</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;32.104</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.120</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;22.903</td>
</tr>
<tr>
<td style="text-align:left">What limitation or future work is mentioned in this text?</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.493</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;17.959</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;16.380</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;16.152</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.752</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;26.067</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.302</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;11.559</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.420</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;28.332</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.738</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;14.338</td>
</tr>
<tr>
<td style="text-align:left">What method or approach is described in this excerpt?</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left">What problem does this passage say the work addresses?</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.120</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;21.654</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;15.279</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;17.008</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.264</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;30.112</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.049</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;9.748</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.167</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;27.618</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.643</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;29.771</td>
</tr>
</tbody>
</table>


---

## Q1. According to this passage, what is the main claim or contribution?

<table>
<thead><tr>
<th>Approach × Device</th>
<th>rougeL</th>
<th>faithfulness</th>
<th>quality_score</th>
<th>time_to_response</th>
<th>tokens_per_sec</th>
</tr></thead>
<tbody>
<tr>
<td style="text-align:left"><code>baseline|cpu</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.066</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.270</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;8.241</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.762</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline|cuda</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.066</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.270</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.439</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;21.536</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline_gguf|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.100</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.330</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;10.051</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;12.736</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline_gguf|cuda</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.100</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.330</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;7.673</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;16.682</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.098</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.617</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.295</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;45.783</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.807</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cuda</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.092</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.514</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.284</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;2.832</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;26.881</td>
</tr>
<tr>
<td style="text-align:left"><code>rag_gguf|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.098</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.463</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.268</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;28.732</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.478</td>
</tr>
<tr>
<td style="text-align:left"><code>rag_gguf|cuda</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.098</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.463</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.268</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;10.304</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;12.595</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cpu</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.066</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.270</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;9.357</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.313</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cuda</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.066</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.270</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.771</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;17.508</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned_with_rag|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.092</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.514</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.284</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;28.728</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.525</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned_with_rag|cuda</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.099</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.622</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.300</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.610</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;29.308</td>
</tr>
</tbody>
</table>

**CPU → GPU speedup (time_to_response):**
- **baseline:** 8.24s (CPU) → 1.44s (GPU) = **5.7×** faster time-to-response
- **baseline_gguf:** 10.05s (CPU) → 7.67s (GPU) = **1.3×** faster time-to-response
- **fine_tuned:** 9.36s (CPU) → 1.77s (GPU) = **5.3×** faster time-to-response
- **fine_tuned_with_rag:** 28.73s (CPU) → 4.61s (GPU) = **6.2×** faster time-to-response
- **rag:** 45.78s (CPU) → 2.83s (GPU) = **16.2×** faster time-to-response
- **rag_gguf:** 28.73s (CPU) → 10.30s (GPU) = **2.8×** faster time-to-response

<details><summary>Sample answers</summary>

- **`baseline|cpu`:** I'm sorry, but it seems like there was no passage provided for me to analyze. Could you please provide the passage you're referring to?
- **`baseline|cuda`:** I'm sorry, but it seems like there was no passage provided for me to analyze. Could you please provide the passage you're referring to?
- **`baseline_gguf|cpu`:** To provide an accurate answer, I would need the specific passage in question. However, I can guide you on how to determine the main claim or contribution from a passage.   To identify the main claim or contribution of a passage, follow these steps:   1. **Read the Passage Thor...
- **`baseline_gguf|cuda`:** To provide an accurate answer, I would need the specific passage in question. However, I can guide you on how to determine the main claim or contribution from a passage.   To identify the main claim or contribution of a passage, follow these steps:   1. **Read the Passage Thor...
- **`rag|cpu`:** 1. What are the key assumptions about the nature of RAG documents in the setup discussed? 2. What are the failure cases observed during the attack analysis? 3. What are the financial costs involved in launching the attack? 4. What potential countermeasures against the attack a...
- **`rag|cuda`:** Question: What are the key assumptions about the nature of RAG documents in the discussed setup?  Question: What are the failure cases observed during the attack analysis?  Question: What are the financial costs involved in launching the attack?  Question: What potential count...
- **`rag_gguf|cpu`:** 1. What assumptions are made about the RAG documents in the discussed setup? 2. What failure cases were observed during the attack analysis? 3. How are the financial costs of launching the attack quantified in the context? 4. What potential countermeasures against the attack a...
- **`rag_gguf|cuda`:** 1. What assumptions are made about the RAG documents in the discussed setup? 2. What failure cases were observed during the attack analysis? 3. How are the financial costs of launching the attack quantified in the context? 4. What potential countermeasures against the attack a...
- **`fine_tuned|cpu`:** I'm sorry, but it seems like there was no passage provided for me to analyze. Could you please provide the passage you're referring to?
- **`fine_tuned|cuda`:** I'm sorry, but it seems like there was no passage provided for me to analyze. Could you please provide the passage you're referring to?
- **`fine_tuned_with_rag|cpu`:** Question: What are the key assumptions about the nature of RAG documents in the discussed setup?  Question: What are the failure cases observed during the attack analysis?  Question: What are the financial costs involved in launching the attack?  Question: What potential count...
- **`fine_tuned_with_rag|cuda`:** 1. What are the assumptions regarding the nature of the RAG documents in the setup? 2. What are the failure cases observed during the attack? 3. What are the financial costs involved in launching the attack? 4. What potential countermeasures against the attack are discussed, a...

</details>

## Q2. Summarize the contribution of 'Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation'.

<table>
<thead><tr>
<th>Approach × Device</th>
<th>rougeL</th>
<th>faithfulness</th>
<th>quality_score</th>
<th>time_to_response</th>
<th>tokens_per_sec</th>
</tr></thead>
<tbody>
<tr>
<td style="text-align:left"><code>baseline|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.273</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.492</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;302.478</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.204</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.438</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;525.176</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.264</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.750</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.583</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;962.158</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.197</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.699</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.566</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;761.570</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cuda</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.144</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.394</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;528.042</td>
<td style="text-align:right">—</td>
</tr>
</tbody>
</table>

**CPU → GPU speedup (time_to_response):**
- **baseline:** 302.48s (CPU) → 525.18s (GPU) = **0.6×** faster time-to-response
- **rag:** 962.16s (CPU) → 761.57s (GPU) = **1.3×** faster time-to-response

<details><summary>Sample answers</summary>

- **`baseline|cpu`:** The contribution of "Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation" lies in the development of a system that streamlines the process of conducting literature reviews in academic research. This system leverages Natural Language Pr...
- **`baseline|cuda`:** The contribution of 'Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation' lies in the development of a system that streamlines the process of conducting literature reviews in academic research. This system leverages Natural Language Pr...
- **`rag|cpu`:** The research paper titled "Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation" by Nurshat Fateh Ali, Shakil Mosharrof, and Md. Mahdi Mohtasim focuses on developing an automated system for generating literature reviews. The primary obj...
- **`rag|cuda`:** The research paper titled "Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation" by Nurshat Fateh Ali, Shakil Mosharrof, and Md. Mahdi Mohtasim focuses on developing an automated system for generating literature reviews. The primary obj...
- **`fine_tuned|cuda`:** The contribution of 'Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation' lies in the development of a system that streamlines the process of conducting literature reviews in academic research. This system leverages Natural Language Pr...

</details>

## Q3. Summarize the contribution of 'Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval'.

<table>
<thead><tr>
<th>Approach × Device</th>
<th>rougeL</th>
<th>faithfulness</th>
<th>quality_score</th>
<th>time_to_response</th>
<th>tokens_per_sec</th>
</tr></thead>
<tbody>
<tr>
<td style="text-align:left"><code>baseline|cpu</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.147</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.386</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;31.561</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.056</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline|cuda</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.147</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.389</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;5.699</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;22.459</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline_gguf|cpu</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.167</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.397</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;8.846</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;14.470</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline_gguf|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.167</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.397</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;9.544</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;13.411</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.211</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.607</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.387</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;55.702</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.304</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cuda</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.199</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.625</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.384</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;4.324</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;30.627</td>
</tr>
<tr>
<td style="text-align:left"><code>rag_gguf|cpu</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.174</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.349</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.331</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;33.606</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.830</td>
</tr>
<tr>
<td style="text-align:left"><code>rag_gguf|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.174</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.349</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.331</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;13.986</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;9.251</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cpu</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.150</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.388</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;38.793</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.300</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cuda</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.147</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.389</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;5.057</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;25.311</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned_with_rag|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.200</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.661</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.391</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;56.326</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.279</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned_with_rag|cuda</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.200</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.649</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.389</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;5.432</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;24.353</td>
</tr>
</tbody>
</table>

**CPU → GPU speedup (time_to_response):**
- **baseline:** 31.56s (CPU) → 5.70s (GPU) = **5.5×** faster time-to-response
- **baseline_gguf:** 8.85s (CPU) → 9.54s (GPU) = **0.9×** faster time-to-response
- **fine_tuned:** 38.79s (CPU) → 5.06s (GPU) = **7.7×** faster time-to-response
- **fine_tuned_with_rag:** 56.33s (CPU) → 5.43s (GPU) = **10.4×** faster time-to-response
- **rag:** 55.70s (CPU) → 4.32s (GPU) = **12.9×** faster time-to-response
- **rag_gguf:** 33.61s (CPU) → 13.99s (GPU) = **2.4×** faster time-to-response

<details><summary>Sample answers</summary>

- **`baseline|cpu`:** The contribution of 'Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval' lies in enhancing the efficiency and effectiveness of information retrieval systems. By focusing on lightweight algorithms, the approach minimizes computational ov...
- **`baseline|cuda`:** The contribution of 'Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval' lies in enhancing the efficiency and accuracy of information retrieval systems. By focusing on lightweight algorithms, the approach reduces computational overhead,...
- **`baseline_gguf|cpu`:** "Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval" is a research paper that focuses on improving the efficiency and accuracy of information retrieval systems. The paper introduces a novel approach that combines lightweight models and ...
- **`baseline_gguf|cuda`:** "Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval" is a research paper that focuses on improving the efficiency and accuracy of information retrieval systems. The paper introduces a novel approach that combines lightweight models and ...
- **`rag|cpu`:** The contribution of "Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval" is focused on improving the performance of Generative Information Retrieval (GenIR) models. These models, which are based on large pre-trained language models like...
- **`rag|cuda`:** The contribution of "Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval" is focused on improving the efficiency and effectiveness of Generative Information Retrieval (GenIR) models. GenIR models, which are based on large pre-trained lan...
- **`rag_gguf|cpu`:** The contribution of "Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval" is not explicitly detailed in the provided context. However, based on the title and the context surrounding Generative Information Retrieval (GenIR), it can be inf...
- **`rag_gguf|cuda`:** The contribution of "Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval" is not explicitly detailed in the provided context. However, based on the title and the context surrounding Generative Information Retrieval (GenIR), it can be inf...
- **`fine_tuned|cpu`:** The contribution of 'Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval' lies in enhancing the efficiency and accuracy of information retrieval systems. By focusing on lightweight algorithms, the approach minimizes computational overhea...
- **`fine_tuned|cuda`:** The contribution of 'Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval' lies in enhancing the efficiency and accuracy of information retrieval systems. By focusing on lightweight algorithms, the approach reduces computational overhead,...
- **`fine_tuned_with_rag|cpu`:** The contribution of "Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval" is focused on improving the performance of Generative Information Retrieval (GenIR) models. GenIR models, which are based on large pre-trained language models like...
- **`fine_tuned_with_rag|cuda`:** The contribution of "Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval" is focused on improving the performance of Generative Information Retrieval (GenIR) models. GenIR models, which are based on large pre-trained language models like...

</details>

## Q4. What experimental result or finding is reported here?

<table>
<thead><tr>
<th>Approach × Device</th>
<th>rougeL</th>
<th>faithfulness</th>
<th>quality_score</th>
<th>time_to_response</th>
<th>tokens_per_sec</th>
</tr></thead>
<tbody>
<tr>
<td style="text-align:left"><code>baseline|cpu</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.042</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.273</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;9.698</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.640</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline|cuda</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.042</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.273</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.797</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;25.045</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline_gguf|cpu</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.080</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.318</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;8.285</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;15.450</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline_gguf|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.080</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.318</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;7.724</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;16.573</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cpu</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.062</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.213</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.228</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;108.056</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;1.187</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.076</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.265</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.246</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.252</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;31.298</td>
</tr>
<tr>
<td style="text-align:left"><code>rag_gguf|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.102</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.250</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.258</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;39.398</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.264</td>
</tr>
<tr>
<td style="text-align:left"><code>rag_gguf|cuda</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.102</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.250</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.258</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;19.738</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;6.534</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cpu</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.042</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.273</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;14.064</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.200</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cuda</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.042</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.273</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.655</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;27.195</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned_with_rag|cpu</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.062</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.213</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.228</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;74.180</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;1.730</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned_with_rag|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.063</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.200</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.226</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.355</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;28.783</td>
</tr>
</tbody>
</table>

**CPU → GPU speedup (time_to_response):**
- **baseline:** 9.70s (CPU) → 1.80s (GPU) = **5.4×** faster time-to-response
- **baseline_gguf:** 8.28s (CPU) → 7.72s (GPU) = **1.1×** faster time-to-response
- **fine_tuned:** 14.06s (CPU) → 1.65s (GPU) = **8.5×** faster time-to-response
- **fine_tuned_with_rag:** 74.18s (CPU) → 4.35s (GPU) = **17.0×** faster time-to-response
- **rag:** 108.06s (CPU) → 4.25s (GPU) = **25.4×** faster time-to-response
- **rag_gguf:** 39.40s (CPU) → 19.74s (GPU) = **2.0×** faster time-to-response

<details><summary>Sample answers</summary>

- **`baseline|cpu`:** I'm sorry, but it seems like you haven't provided any context or content for me to identify an experimental result or finding. Please provide the relevant information or details about the experiment or study you are referring to.
- **`baseline|cuda`:** I'm sorry, but it seems like you haven't provided any context or content for me to identify an experimental result or finding. Please provide the relevant information or details about the experiment or study you are referring to.
- **`baseline_gguf|cpu`:** To provide you with the experimental result or finding reported here, I would need the specific details of the experiment or study in question. Since you haven't provided any context or details, I can't give you a specific result. However, I can guide you on how to extract and...
- **`baseline_gguf|cuda`:** To provide you with the experimental result or finding reported here, I would need the specific details of the experiment or study in question. Since you haven't provided any context or details, I can't give you a specific result. However, I can guide you on how to extract and...
- **`rag|cpu`:** The experimental results reported here are the performance metrics of various retrieval-based models on the ICU readmission prediction task. The models evaluated are REMed, VanillaEHR-RAGp, and Mistral 7b. The performance metrics include accuracy, precision, recall, F1-score, ...
- **`rag|cuda`:** The experimental results reported here are the performance metrics of various retrieval-based models on the ICU readmission prediction task. The models evaluated are REMed, VanillaEHR-RAGp, and Mistral 7b. The performance metrics include accuracy, precision, recall, F1-score, ...
- **`rag_gguf|cpu`:** The experimental result reported in the context is the effect of varying the number of prototypes on performance. As the number of prototypes increases, the performance consistently improves for ICU readmissions. This is shown in Table 6, which displays the performance metrics...
- **`rag_gguf|cuda`:** The experimental result reported in the context is the effect of varying the number of prototypes on performance. As the number of prototypes increases, the performance consistently improves for ICU readmissions. This is shown in Table 6, which displays the performance metrics...
- **`fine_tuned|cpu`:** I'm sorry, but it seems like you haven't provided any context or content for me to identify an experimental result or finding. Please provide the relevant information or details about the experiment or study you are referring to.
- **`fine_tuned|cuda`:** I'm sorry, but it seems like you haven't provided any context or content for me to identify an experimental result or finding. Please provide the relevant information or details about the experiment or study you are referring to.
- **`fine_tuned_with_rag|cpu`:** The experimental results reported here are the performance metrics of various retrieval-based models on the ICU readmission prediction task. The models evaluated are REMed, VanillaEHR-RAGp, and Mistral 7b. The performance metrics include accuracy, precision, recall, F1-score, ...
- **`fine_tuned_with_rag|cuda`:** The experimental results reported here are the performance metrics of various retrieval-based models on the ICU readmission prediction task. The models evaluated are REMed, VanillaEHR-RAGp, and Mistral 7b. The performance metrics include accuracy, precision, recall, F1-score, ...

</details>

## Q5. What is the paper 'MUST-RAG: MUSical Text Question Answering with Retrieval Augmented Generation' about?

<table>
<thead><tr>
<th>Approach × Device</th>
<th>rougeL</th>
<th>faithfulness</th>
<th>quality_score</th>
<th>time_to_response</th>
<th>tokens_per_sec</th>
</tr></thead>
<tbody>
<tr>
<td style="text-align:left"><code>baseline|cpu</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.088</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.352</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;302.652</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline|cuda</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.090</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.348</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;596.087</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cpu</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.126</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.660</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.518</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;961.546</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cuda</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.157</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.716</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.537</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;773.050</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cuda</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.090</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.348</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;494.006</td>
<td style="text-align:right">—</td>
</tr>
</tbody>
</table>

**CPU → GPU speedup (time_to_response):**
- **baseline:** 302.65s (CPU) → 596.09s (GPU) = **0.5×** faster time-to-response
- **rag:** 961.55s (CPU) → 773.05s (GPU) = **1.2×** faster time-to-response

<details><summary>Sample answers</summary>

- **`baseline|cpu`:** The paper "MUST-RAG: MUSical Text Question Answering with Retrieval Augmented Generation" introduces a novel approach to answering questions about music-related texts. The acronym MUST-RAG stands for "MUSical Text Question Answering with Retrieval Augmented Generation."  The m...
- **`baseline|cuda`:** The paper "MUST-RAG: MUSical Text Question Answering with Retrieval Augmented Generation" focuses on developing a system for answering questions about musical texts, such as lyrics or scores, using a combination of retrieval-augmented generation (RAG) and a pre-trained languag...
- **`rag|cpu`:** The paper 'MUST-RAG: MUSical Text Question Answering with Retrieval Augmented Generation' by Daeyong Kwon, SeungHeon Doh, and Juhan Nam, from the Graduate School of Culture Technology at KAIST, South Korea, introduces the MusT-RAG framework. This framework aims to adapt genera...
- **`rag|cuda`:** The paper 'MUST-RAG: MUSical Text Question Answering with Retrieval Augmented Generation' by Daeyong Kwon, SeungHeon Doh, and Juhan Nam, from the Graduate School of Culture Technology at KAIST, South Korea, focuses on addressing the limitations of Large Language Models (LLMs) ...
- **`fine_tuned|cuda`:** The paper "MUST-RAG: MUSical Text Question Answering with Retrieval Augmented Generation" focuses on developing a system for answering questions about musical texts, such as lyrics or scores, using a combination of retrieval-augmented generation (RAG) and a pre-trained languag...

</details>

## Q6. What is the paper 'Riddle Me This! Stealthy Membership Inference for Retrieval-Augmented Generation' about?

<table>
<thead><tr>
<th>Approach × Device</th>
<th>rougeL</th>
<th>faithfulness</th>
<th>quality_score</th>
<th>time_to_response</th>
<th>tokens_per_sec</th>
</tr></thead>
<tbody>
<tr>
<td style="text-align:left"><code>baseline|cpu</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.174</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.420</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;29.341</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.362</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.207</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.430</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;5.365</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;23.859</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline_gguf|cpu</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.177</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.398</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;11.948</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;10.713</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline_gguf|cuda</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.177</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.398</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;9.891</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;12.941</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.261</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.475</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.381</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;57.921</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.218</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cuda</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.164</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.574</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.356</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;5.556</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;20.616</td>
</tr>
<tr>
<td style="text-align:left"><code>rag_gguf|cpu</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.227</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.429</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.365</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;35.478</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.635</td>
</tr>
<tr>
<td style="text-align:left"><code>rag_gguf|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.227</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.429</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.365</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;15.527</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;8.360</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cpu</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.208</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.430</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;37.332</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.429</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.194</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.425</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;3.987</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;32.104</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned_with_rag|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.273</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.484</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.384</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;60.546</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.120</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned_with_rag|cuda</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.164</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.574</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.356</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;5.130</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;22.903</td>
</tr>
</tbody>
</table>

**CPU → GPU speedup (time_to_response):**
- **baseline:** 29.34s (CPU) → 5.36s (GPU) = **5.5×** faster time-to-response
- **baseline_gguf:** 11.95s (CPU) → 9.89s (GPU) = **1.2×** faster time-to-response
- **fine_tuned:** 37.33s (CPU) → 3.99s (GPU) = **9.4×** faster time-to-response
- **fine_tuned_with_rag:** 60.55s (CPU) → 5.13s (GPU) = **11.8×** faster time-to-response
- **rag:** 57.92s (CPU) → 5.56s (GPU) = **10.4×** faster time-to-response
- **rag_gguf:** 35.48s (CPU) → 15.53s (GPU) = **2.3×** faster time-to-response

<details><summary>Sample answers</summary>

- **`baseline|cpu`:** The paper "Riddle Me This! Stealthy Membership Inference for Retrieval-Augmented Generation" explores the issue of membership inference attacks in the context of retrieval-augmented generation (RAG) models. Membership inference attacks aim to determine whether a particular dat...
- **`baseline|cuda`:** The paper "Riddle Me This! Stealthy Membership Inference for Retrieval-Augmented Generation" explores the issue of membership inference attacks in the context of retrieval-augmented generation (RAG) models. These models combine large language models with external knowledge sou...
- **`baseline_gguf|cpu`:** The paper "Riddle Me This! Stealthy Membership Inference for Retrieval-Augmented Generation" explores the vulnerability of retrieval-augmented generation models to membership inference attacks. Membership inference attacks aim to determine whether a particular data record was ...
- **`baseline_gguf|cuda`:** The paper "Riddle Me This! Stealthy Membership Inference for Retrieval-Augmented Generation" explores the vulnerability of retrieval-augmented generation models to membership inference attacks. Membership inference attacks aim to determine whether a particular data record was ...
- **`rag|cpu`:** The paper "Riddle Me This! Stealthy Membership Inference for Retrieval-Augmented Generation" discusses a near-perfect membership inference attack on Retrieval Augmented Generation (RAG) models. RAG is a technique that combines Large Language Models (LLMs) with a knowledge base...
- **`rag|cuda`:** The paper "Riddle Me This! Stealthy Membership Inference for Retrieval-Augmented Generation" discusses a near-perfect membership inference attack on Retrieval Augmented Generation (RAG) models. The authors propose a method to determine whether a given data point was part of th...
- **`rag_gguf|cpu`:** The paper "Riddle Me This! Stealthy Membership Inference for Retrieval-Augmented Generation" is about a research study conducted by a team of researchers from various universities. The paper focuses on the concept of Retrieval-Augmented Generation (RAG), which is a method prop...
- **`rag_gguf|cuda`:** The paper "Riddle Me This! Stealthy Membership Inference for Retrieval-Augmented Generation" is about a research study conducted by a team of researchers from various universities. The paper focuses on the concept of Retrieval-Augmented Generation (RAG), which is a method prop...
- **`fine_tuned|cpu`:** The paper "Riddle Me This! Stealthy Membership Inference for Retrieval-Augmented Generation" explores the issue of membership inference attacks in the context of retrieval-augmented generation (RAG) models. These models combine large language models with external knowledge sou...
- **`fine_tuned|cuda`:** The paper "Riddle Me This! Stealthy Membership Inference for Retrieval-Augmented Generation" explores the issue of membership inference attacks in the context of retrieval-augmented generation (RAG) models. These models combine large language models with external knowledge sou...
- **`fine_tuned_with_rag|cpu`:** The paper "Riddle Me This! Stealthy Membership Inference for Retrieval-Augmented Generation" discusses a near-perfect membership inference attack on Retrieval Augmented Generation (RAG) models. RAG is a technique that combines Large Language Models (LLMs) with a knowledge base...
- **`fine_tuned_with_rag|cuda`:** The paper "Riddle Me This! Stealthy Membership Inference for Retrieval-Augmented Generation" discusses a near-perfect membership inference attack on Retrieval Augmented Generation (RAG) models. The authors propose a method to determine whether a given data point was part of th...

</details>

## Q7. What limitation or future work is mentioned in this text?

<table>
<thead><tr>
<th>Approach × Device</th>
<th>rougeL</th>
<th>faithfulness</th>
<th>quality_score</th>
<th>time_to_response</th>
<th>tokens_per_sec</th>
</tr></thead>
<tbody>
<tr>
<td style="text-align:left"><code>baseline|cpu</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.058</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.265</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;8.876</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.493</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.058</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.265</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;1.726</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;17.959</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline_gguf|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.107</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.319</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;7.814</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;16.380</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline_gguf|cuda</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.107</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.319</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;7.925</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;16.152</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cpu</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.037</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.222</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.215</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;16.163</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.752</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cuda</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.109</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.395</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.270</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;2.509</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;26.067</td>
</tr>
<tr>
<td style="text-align:left"><code>rag_gguf|cpu</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.074</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.452</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.279</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;29.912</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.302</td>
</tr>
<tr>
<td style="text-align:left"><code>rag_gguf|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.074</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.452</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.279</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;11.215</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;11.559</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cpu</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.058</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.265</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;9.065</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.420</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.058</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.265</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.094</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;28.332</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned_with_rag|cpu</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.037</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.222</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.215</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;16.452</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.738</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned_with_rag|cuda</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.037</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.222</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.215</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.997</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;14.338</td>
</tr>
</tbody>
</table>

**CPU → GPU speedup (time_to_response):**
- **baseline:** 8.88s (CPU) → 1.73s (GPU) = **5.1×** faster time-to-response
- **baseline_gguf:** 7.81s (CPU) → 7.92s (GPU) = **1.0×** faster time-to-response
- **fine_tuned:** 9.07s (CPU) → 1.09s (GPU) = **8.3×** faster time-to-response
- **fine_tuned_with_rag:** 16.45s (CPU) → 1.00s (GPU) = **16.5×** faster time-to-response
- **rag:** 16.16s (CPU) → 2.51s (GPU) = **6.4×** faster time-to-response
- **rag_gguf:** 29.91s (CPU) → 11.21s (GPU) = **2.7×** faster time-to-response

<details><summary>Sample answers</summary>

- **`baseline|cpu`:** I'm sorry, but it seems like there was no text provided for me to analyze. Could you please provide the text you're referring to?
- **`baseline|cuda`:** I'm sorry, but it seems like there was no text provided for me to analyze. Could you please provide the text you're referring to?
- **`baseline_gguf|cpu`:** To provide an accurate response, I would need the specific text in question. However, I can guide you on how to identify limitations or future work mentioned in a text.  When looking for limitations or future work in a text, you should:  1. Identify the main findings or conclu...
- **`baseline_gguf|cuda`:** To provide an accurate response, I would need the specific text in question. However, I can guide you on how to identify limitations or future work mentioned in a text.  When looking for limitations or future work in a text, you should:  1. Identify the main findings or conclu...
- **`rag|cpu`:** The text does not explicitly mention any limitations or future work.
- **`rag|cuda`:** The text does not explicitly mention any limitations or future work. It outlines the structure of the discussion section, which includes assumptions about RAG documents, analysis of failure cases, financial costs, and potential countermeasures against attacks. However, it does...
- **`rag_gguf|cpu`:** Yes, the text mentions limitations and future work in Section 7.4, where potential countermeasures against the attack are discussed along with their limitations.  Referencing the first author's paper, "7 Discussion" from the provided context, we can elaborate on the limitation...
- **`rag_gguf|cuda`:** Yes, the text mentions limitations and future work in Section 7.4, where potential countermeasures against the attack are discussed along with their limitations.  Referencing the first author's paper, "7 Discussion" from the provided context, we can elaborate on the limitation...
- **`fine_tuned|cpu`:** I'm sorry, but it seems like there was no text provided for me to analyze. Could you please provide the text you're referring to?
- **`fine_tuned|cuda`:** I'm sorry, but it seems like there was no text provided for me to analyze. Could you please provide the text you're referring to?
- **`fine_tuned_with_rag|cpu`:** The text does not explicitly mention any limitations or future work.
- **`fine_tuned_with_rag|cuda`:** The text does not explicitly mention any limitations or future work.

</details>

## Q8. What method or approach is described in this excerpt?

<table>
<thead><tr>
<th>Approach × Device</th>
<th>rougeL</th>
<th>faithfulness</th>
<th>quality_score</th>
<th>time_to_response</th>
<th>tokens_per_sec</th>
</tr></thead>
<tbody>
<tr>
<td style="text-align:left"><code>baseline|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.070</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.317</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;259.139</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline|cuda</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.070</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.317</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;309.851</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cpu</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.020</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.400</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.227</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;957.854</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cuda</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.058</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.508</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.258</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;718.763</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cuda</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.070</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.317</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;275.957</td>
<td style="text-align:right">—</td>
</tr>
</tbody>
</table>

**CPU → GPU speedup (time_to_response):**
- **baseline:** 259.14s (CPU) → 309.85s (GPU) = **0.8×** faster time-to-response
- **rag:** 957.85s (CPU) → 718.76s (GPU) = **1.3×** faster time-to-response

<details><summary>Sample answers</summary>

- **`baseline|cpu`:** The method or approach described in this excerpt is the scientific method. The scientific method is a systematic and logical approach to discovering how things in the universe work. It involves making observations, forming a hypothesis, conducting experiments, analyzing data, ...
- **`baseline|cuda`:** The method or approach described in this excerpt is the scientific method. The scientific method is a systematic and logical approach to discovering how things in the universe work. It involves making observations, forming a hypothesis, conducting experiments, analyzing data, ...
- **`rag|cpu`:** [MASK_1]: extension [MASK_2]: PageRank [MASK_3]: comprehensive [MASK_4]: PageRank [MASK_5]: storage [MASK_6]: possible alterations [MASK_7]: sensitivity [MASK_8]: introduce [MASK_9]: extensive [MASK_10]: exciting  Answer: [MASK_1]: extension [MASK_2]: PageRank [MASK_3]: compre...
- **`rag|cuda`:** [MASK_1]: extension [MASK_2]: PageRank [MASK_3]: comprehensive [MASK_4]: PageRank model [MASK_5]: storage issues [MASK_6]: possible alterations [MASK_7]: sensitivity and conditioning [MASK_8]: introduce [MASK_9]: extensive reference list [MASK_10]: exciting areas of future res...
- **`fine_tuned|cuda`:** The method or approach described in this excerpt is the scientific method. The scientific method is a systematic and logical approach to discovering how things in the universe work. It involves making observations, forming a hypothesis, conducting experiments, analyzing data, ...

</details>

## Q9. What problem does this passage say the work addresses?

<table>
<thead><tr>
<th>Approach × Device</th>
<th>rougeL</th>
<th>faithfulness</th>
<th>quality_score</th>
<th>time_to_response</th>
<th>tokens_per_sec</th>
</tr></thead>
<tbody>
<tr>
<td style="text-align:left"><code>baseline|cpu</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.128</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.333</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;8.252</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.120</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.102</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.320</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.755</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;21.654</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline_gguf|cpu</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.116</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.325</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;8.378</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;15.279</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline_gguf|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.116</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.325</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;7.526</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;17.008</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cpu</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.099</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.615</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.307</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;38.792</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.264</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.094</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.467</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.315</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.402</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;30.112</td>
</tr>
<tr>
<td style="text-align:left"><code>rag_gguf|cpu</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.088</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.406</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.274</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;17.474</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.049</td>
</tr>
<tr>
<td style="text-align:left"><code>rag_gguf|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.088</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.406</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.274</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;7.333</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;9.748</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.149</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.337</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;10.737</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.167</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cuda</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.067</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.290</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.122</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;27.618</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned_with_rag|cpu</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.099</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.615</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.307</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;33.090</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.643</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned_with_rag|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.094</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.467</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.315</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.471</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;29.771</td>
</tr>
</tbody>
</table>

**CPU → GPU speedup (time_to_response):**
- **baseline:** 8.25s (CPU) → 1.75s (GPU) = **4.7×** faster time-to-response
- **baseline_gguf:** 8.38s (CPU) → 7.53s (GPU) = **1.1×** faster time-to-response
- **fine_tuned:** 10.74s (CPU) → 1.12s (GPU) = **9.6×** faster time-to-response
- **fine_tuned_with_rag:** 33.09s (CPU) → 4.47s (GPU) = **7.4×** faster time-to-response
- **rag:** 38.79s (CPU) → 4.40s (GPU) = **8.8×** faster time-to-response
- **rag_gguf:** 17.47s (CPU) → 7.33s (GPU) = **2.4×** faster time-to-response

<details><summary>Sample answers</summary>

- **`baseline|cpu`:** The passage you provided does not contain any information or context to identify a specific problem that the work addresses. Please provide the passage or additional details for a more accurate response.
- **`baseline|cuda`:** The passage you provided does not contain any information or context about a specific problem or work. Please provide the relevant passage or details about the work in question so that I can assist you better.
- **`baseline_gguf|cpu`:** To provide an accurate answer, I would need the specific passage in question. However, I can guide you on how to analyze a passage to determine the problem it addresses.  When analyzing a passage to identify the problem it addresses, follow these steps:  1. Read the passage ca...
- **`baseline_gguf|cuda`:** To provide an accurate answer, I would need the specific passage in question. However, I can guide you on how to analyze a passage to determine the problem it addresses.  When analyzing a passage to identify the problem it addresses, follow these steps:  1. Read the passage ca...
- **`rag|cpu`:** The passage discusses the problem of generating topic-focused descriptions using a RAG (Retrieval-Augmented Generation) system. It outlines the assumptions about the nature of the RAG documents in the setup, analyzes the failure cases observed during the attack, examines the f...
- **`rag|cuda`:** The passage discusses the issue of generating topic-focused descriptions using a RAG (Retrieval-Augmented Generation) system. It outlines the assumptions about the nature of the RAG documents in their setup, analyzes the failure cases observed during the attack, examines the f...
- **`rag_gguf|cpu`:** The passage addresses the problem of analyzing the failure cases, financial costs, and potential countermeasures against an attack on RAG documents, as well as exploring topic-focused description generation.  However, the specific details of the problem are not provided in the...
- **`rag_gguf|cuda`:** The passage addresses the problem of analyzing the failure cases, financial costs, and potential countermeasures against an attack on RAG documents, as well as exploring topic-focused description generation.  However, the specific details of the problem are not provided in the...
- **`fine_tuned|cpu`:** The passage you provided does not contain any information or context to identify a specific problem that the work addresses. Please provide the passage or more details about the work in question.
- **`fine_tuned|cuda`:** The passage you provided does not contain any information or context. Please provide the passage you are referring to, so I can help identify the problem it addresses.
- **`fine_tuned_with_rag|cpu`:** The passage discusses the problem of generating topic-focused descriptions using a RAG (Retrieval-Augmented Generation) system. It outlines the assumptions about the nature of the RAG documents in the setup, analyzes the failure cases observed during the attack, examines the f...
- **`fine_tuned_with_rag|cuda`:** The passage discusses the issue of generating topic-focused descriptions using a RAG (Retrieval-Augmented Generation) system. It outlines the assumptions about the nature of the RAG documents in their setup, analyzes the failure cases observed during the attack, examines the f...

</details>
