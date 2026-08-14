# Results by question

Each question shows quality **and** latency across approach × device.

- **rougeL:** overlap with the ground-truth answer — **higher is better** (the RAG quality story)
- **Time to response:** retrieval + generation (seconds) — **lower is better** (the device story)
- **tokens_per_sec:** decode throughput — **higher is better**
- **Colors:** 🟢 best · 🟡 mid · 🔴 worst within each row; ties within noise are left uncolored

_Generated: 2026-08-14T12:41:27.826072+00:00_

## Overview — overlap with ground truth (`rougeL`)

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
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.066</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.066</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.098</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.092</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.066</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.066</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.098</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.092</td>
</tr>
<tr>
<td style="text-align:left">Summarize the contribution of 'Automated Literature Revie...</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.273</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.204</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.264</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.197</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.144</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left">Summarize the contribution of 'Lightweight and Direct Doc...</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.147</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.147</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.211</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.199</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.133</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.132</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.196</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.200</td>
</tr>
<tr>
<td style="text-align:left">What experimental result or finding is reported here?</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.042</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.042</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.062</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.076</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.022</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.042</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.065</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.063</td>
</tr>
<tr>
<td style="text-align:left">What is the paper 'MUST-RAG: MUSical Text Question Answer...</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.088</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.090</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.126</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.157</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.090</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left">What is the paper 'Riddle Me This! Stealthy Membership In...</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.174</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.207</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.261</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.164</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.210</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.193</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.261</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.164</td>
</tr>
<tr>
<td style="text-align:left">What limitation or future work is mentioned in this text?</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.058</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.058</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.037</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.109</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.058</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.058</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.037</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.037</td>
</tr>
<tr>
<td style="text-align:left">What method or approach is described in this excerpt?</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.070</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.070</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.020</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.058</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.070</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left">What problem does this passage say the work addresses?</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.128</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.102</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.099</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.094</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.128</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.067</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.095</td>
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
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;6.541</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.011</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;41.408</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;2.219</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;9.547</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.076</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;45.056</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;2.359</td>
</tr>
<tr>
<td style="text-align:left">Summarize the contribution of 'Automated Literature Revie...</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;302.478</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;525.176</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;962.158</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;761.570</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;528.042</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left">Summarize the contribution of 'Lightweight and Direct Doc...</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;24.264</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;4.414</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;52.644</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;3.621</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;36.305</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;3.842</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;56.402</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;4.171</td>
</tr>
<tr>
<td style="text-align:left">What experimental result or finding is reported here?</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;9.003</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.374</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;68.645</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.849</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;12.402</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.513</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;73.174</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.742</td>
</tr>
<tr>
<td style="text-align:left">What is the paper 'MUST-RAG: MUSical Text Question Answer...</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;302.652</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;596.087</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;961.546</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;773.050</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;494.006</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left">What is the paper 'Riddle Me This! Stealthy Membership In...</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;25.471</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;5.556</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;54.712</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;5.014</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;36.517</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;3.908</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;59.182</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;3.593</td>
</tr>
<tr>
<td style="text-align:left">What limitation or future work is mentioned in this text?</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;6.593</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;1.010</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;14.589</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;1.915</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;9.614</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;1.126</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;15.143</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.653</td>
</tr>
<tr>
<td style="text-align:left">What method or approach is described in this excerpt?</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;259.139</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;309.851</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;957.854</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;718.763</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;275.957</td>
<td style="text-align:right">—</td>
<td style="text-align:right">—</td>
</tr>
<tr>
<td style="text-align:left">What problem does this passage say the work addresses?</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;7.046</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.232</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;30.905</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.523</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;10.344</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.111</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;45.106</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.985</td>
</tr>
</tbody>
</table>


## Overview — throughput (`tokens_per_sec`, higher is better)

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
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.739</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;30.650</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;3.105</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;34.477</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;3.247</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;28.808</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.852</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;32.332</td>
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
</tr>
<tr>
<td style="text-align:left">Summarize the contribution of 'Lightweight and Direct Doc...</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;5.275</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;29.001</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.440</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;37.056</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.526</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;33.314</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.276</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;31.696</td>
</tr>
<tr>
<td style="text-align:left">What experimental result or finding is reported here?</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.999</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;32.754</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;1.869</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;34.620</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.386</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;29.751</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;1.754</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;32.910</td>
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
</tr>
<tr>
<td style="text-align:left">What is the paper 'Riddle Me This! Stealthy Membership In...</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;5.025</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;23.039</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.350</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;23.113</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.505</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;32.756</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.168</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;32.701</td>
</tr>
<tr>
<td style="text-align:left">What limitation or future work is mentioned in this text?</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.702</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;30.696</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.834</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;34.228</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.224</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;27.543</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.802</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;26.654</td>
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
</tr>
<tr>
<td style="text-align:left">What problem does this passage say the work addresses?</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.825</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;30.833</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.830</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;37.738</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;3.287</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;27.913</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.850</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;33.242</td>
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
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;6.541</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.739</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline|cuda</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.066</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.270</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.011</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;30.650</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.098</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.617</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.295</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;41.408</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;3.105</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cuda</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.092</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.514</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.284</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;2.219</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;34.477</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cpu</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.066</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.270</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;9.547</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;3.247</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cuda</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.066</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.270</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.076</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;28.808</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned_with_rag|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.098</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.617</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.295</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;45.056</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.852</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned_with_rag|cuda</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.092</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.543</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.288</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;2.359</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;32.332</td>
</tr>
</tbody>
</table>

**CPU → GPU speedup (time_to_response):**
- **baseline:** 6.54s (CPU) → 1.01s (GPU) = **6.5×** faster time-to-response
- **fine_tuned:** 9.55s (CPU) → 1.08s (GPU) = **8.9×** faster time-to-response
- **fine_tuned_with_rag:** 45.06s (CPU) → 2.36s (GPU) = **19.1×** faster time-to-response
- **rag:** 41.41s (CPU) → 2.22s (GPU) = **18.7×** faster time-to-response

<details><summary>Sample answers</summary>

- **`baseline|cpu`:** I'm sorry, but it seems like there was no passage provided for me to analyze. Could you please provide the passage you're referring to?
- **`baseline|cuda`:** I'm sorry, but it seems like there was no passage provided for me to analyze. Could you please provide the passage you're referring to?
- **`rag|cpu`:** 1. What are the key assumptions about the nature of RAG documents in the setup discussed? 2. What are the failure cases observed during the attack analysis? 3. What are the financial costs involved in launching the attack? 4. What potential countermeasures against the attack a...
- **`rag|cuda`:** Question: What are the key assumptions about the nature of RAG documents in the discussed setup?  Question: What are the failure cases observed during the attack analysis?  Question: What are the financial costs involved in launching the attack?  Question: What potential count...
- **`fine_tuned|cpu`:** I'm sorry, but it seems like there was no passage provided for me to analyze. Could you please provide the passage you're referring to?
- **`fine_tuned|cuda`:** I'm sorry, but it seems like there was no passage provided for me to analyze. Could you please provide the passage you're referring to?
- **`fine_tuned_with_rag|cpu`:** 1. What are the key assumptions about the nature of RAG documents in the setup discussed? 2. What are the failure cases observed during the attack analysis? 3. What are the financial costs involved in launching the attack? 4. What potential countermeasures against the attack a...
- **`fine_tuned_with_rag|cuda`:** Question: What are the key assumptions about the nature of RAG documents in the setup discussed?  Question: What are the failure cases observed during the attack analysis?  Question: What are the financial costs involved in launching the attack?  Question: What potential count...

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
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;24.264</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;5.275</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline|cuda</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.147</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.389</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;4.414</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;29.001</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.211</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.607</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.387</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;52.644</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.440</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cuda</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.199</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.625</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.384</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;3.621</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;37.056</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cpu</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.133</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.381</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;36.305</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.526</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cuda</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.132</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.380</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;3.842</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;33.314</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned_with_rag|cpu</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.196</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.525</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.369</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;56.402</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.276</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned_with_rag|cuda</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.200</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.649</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.389</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;4.171</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;31.696</td>
</tr>
</tbody>
</table>

**CPU → GPU speedup (time_to_response):**
- **baseline:** 24.26s (CPU) → 4.41s (GPU) = **5.5×** faster time-to-response
- **fine_tuned:** 36.30s (CPU) → 3.84s (GPU) = **9.4×** faster time-to-response
- **fine_tuned_with_rag:** 56.40s (CPU) → 4.17s (GPU) = **13.5×** faster time-to-response
- **rag:** 52.64s (CPU) → 3.62s (GPU) = **14.5×** faster time-to-response

<details><summary>Sample answers</summary>

- **`baseline|cpu`:** The contribution of 'Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval' lies in enhancing the efficiency and effectiveness of information retrieval systems. By focusing on lightweight algorithms, the approach minimizes computational ov...
- **`baseline|cuda`:** The contribution of 'Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval' lies in enhancing the efficiency and accuracy of information retrieval systems. By focusing on lightweight algorithms, the approach reduces computational overhead,...
- **`rag|cpu`:** The contribution of "Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval" is focused on improving the performance of Generative Information Retrieval (GenIR) models. These models, which are based on large pre-trained language models like...
- **`rag|cuda`:** The contribution of "Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval" is focused on improving the efficiency and effectiveness of Generative Information Retrieval (GenIR) models. GenIR models, which are based on large pre-trained lan...
- **`fine_tuned|cpu`:** The contribution of 'Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval' lies in enhancing the efficiency and accuracy of information retrieval systems. By focusing on lightweight algorithms, the approach minimizes computational overhea...
- **`fine_tuned|cuda`:** The contribution of 'Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval' lies in enhancing the efficiency and accuracy of information retrieval systems. By focusing on lightweight algorithms, the approach minimizes computational overhea...
- **`fine_tuned_with_rag|cpu`:** The contribution of "Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval" is focused on improving the performance of Generative Information Retrieval (GenIR) models. These models, which are based on large pre-trained language models like...
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
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.042</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.273</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;9.003</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.999</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.042</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.273</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.374</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;32.754</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.062</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.213</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.228</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;68.645</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;1.869</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cuda</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.076</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.265</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.246</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.849</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;34.620</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cpu</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.022</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.269</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;12.402</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.386</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.042</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.273</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.513</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;29.751</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned_with_rag|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.065</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.205</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.226</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;73.174</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;1.754</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned_with_rag|cuda</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.063</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.200</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.226</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.742</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;32.910</td>
</tr>
</tbody>
</table>

**CPU → GPU speedup (time_to_response):**
- **baseline:** 9.00s (CPU) → 1.37s (GPU) = **6.6×** faster time-to-response
- **fine_tuned:** 12.40s (CPU) → 1.51s (GPU) = **8.2×** faster time-to-response
- **fine_tuned_with_rag:** 73.17s (CPU) → 3.74s (GPU) = **19.6×** faster time-to-response
- **rag:** 68.64s (CPU) → 3.85s (GPU) = **17.8×** faster time-to-response

<details><summary>Sample answers</summary>

- **`baseline|cpu`:** I'm sorry, but it seems like you haven't provided any context or content for me to identify an experimental result or finding. Please provide the relevant information or details about the experiment or study you are referring to.
- **`baseline|cuda`:** I'm sorry, but it seems like you haven't provided any context or content for me to identify an experimental result or finding. Please provide the relevant information or details about the experiment or study you are referring to.
- **`rag|cpu`:** The experimental results reported here are the performance metrics of various retrieval-based models on the ICU readmission prediction task. The models evaluated are REMed, VanillaEHR-RAGp, and Mistral 7b. The performance metrics include accuracy, precision, recall, F1-score, ...
- **`rag|cuda`:** The experimental results reported here are the performance metrics of various retrieval-based models on the ICU readmission prediction task. The models evaluated are REMed, VanillaEHR-RAGp, and Mistral 7b. The performance metrics include accuracy, precision, recall, F1-score, ...
- **`fine_tuned|cpu`:** I'm sorry, but it seems like you haven't provided any context or content for me to identify an experimental result or finding. Please provide the relevant information or text so I can assist you further.
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
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;25.471</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;5.025</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.207</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.430</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;5.556</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;23.039</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.261</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.475</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.381</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;54.712</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.350</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cuda</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.164</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.574</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.356</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;5.014</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;23.113</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cpu</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.210</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.428</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;36.517</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.505</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.193</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.425</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;3.908</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;32.756</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned_with_rag|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.261</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.500</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.386</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;59.182</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.168</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned_with_rag|cuda</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.164</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.574</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.356</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;3.593</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;32.701</td>
</tr>
</tbody>
</table>

**CPU → GPU speedup (time_to_response):**
- **baseline:** 25.47s (CPU) → 5.56s (GPU) = **4.6×** faster time-to-response
- **fine_tuned:** 36.52s (CPU) → 3.91s (GPU) = **9.3×** faster time-to-response
- **fine_tuned_with_rag:** 59.18s (CPU) → 3.59s (GPU) = **16.5×** faster time-to-response
- **rag:** 54.71s (CPU) → 5.01s (GPU) = **10.9×** faster time-to-response

<details><summary>Sample answers</summary>

- **`baseline|cpu`:** The paper "Riddle Me This! Stealthy Membership Inference for Retrieval-Augmented Generation" explores the issue of membership inference attacks in the context of retrieval-augmented generation (RAG) models. Membership inference attacks aim to determine whether a particular dat...
- **`baseline|cuda`:** The paper "Riddle Me This! Stealthy Membership Inference for Retrieval-Augmented Generation" explores the issue of membership inference attacks in the context of retrieval-augmented generation (RAG) models. These models combine large language models with external knowledge sou...
- **`rag|cpu`:** The paper "Riddle Me This! Stealthy Membership Inference for Retrieval-Augmented Generation" discusses a near-perfect membership inference attack on Retrieval Augmented Generation (RAG) models. RAG is a technique that combines Large Language Models (LLMs) with a knowledge base...
- **`rag|cuda`:** The paper "Riddle Me This! Stealthy Membership Inference for Retrieval-Augmented Generation" discusses a near-perfect membership inference attack on Retrieval Augmented Generation (RAG) models. The authors propose a method to determine whether a given data point was part of th...
- **`fine_tuned|cpu`:** The paper "Riddle Me This! Stealthy Membership Inference for Retrieval-Augmented Generation" explores the issue of membership inference attacks in the context of retrieval-augmented generation (RAG) models. These models combine large language models with external knowledge sou...
- **`fine_tuned|cuda`:** The paper "Riddle Me This! Stealthy Membership Inference for Retrieval-Augmented Generation" explores the issue of membership inference attacks in the context of retrieval-augmented generation (RAG) models. These models combine large language models with external knowledge sou...
- **`fine_tuned_with_rag|cpu`:** The paper "Riddle Me This! Stealthy Membership Inference for Retrieval-Augmented Generation" discusses a near-perfect membership inference attack on Retrieval Augmented Generation (RAG) models. RAG is a technique that combines Large Language Models (LLMs) with retrieval from a...
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
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.265</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;6.593</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.702</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.058</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.265</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;1.010</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;30.696</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cpu</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.037</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.222</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.215</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;14.589</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.834</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cuda</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.109</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.395</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.270</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;1.915</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;34.228</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cpu</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.058</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.265</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;9.614</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.224</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.058</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.265</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;1.126</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;27.543</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned_with_rag|cpu</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.037</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.222</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.215</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;15.143</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.802</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned_with_rag|cuda</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.037</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.222</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.215</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.653</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;26.654</td>
</tr>
</tbody>
</table>

**CPU → GPU speedup (time_to_response):**
- **baseline:** 6.59s (CPU) → 1.01s (GPU) = **6.5×** faster time-to-response
- **fine_tuned:** 9.61s (CPU) → 1.13s (GPU) = **8.5×** faster time-to-response
- **fine_tuned_with_rag:** 15.14s (CPU) → 0.65s (GPU) = **23.2×** faster time-to-response
- **rag:** 14.59s (CPU) → 1.91s (GPU) = **7.6×** faster time-to-response

<details><summary>Sample answers</summary>

- **`baseline|cpu`:** I'm sorry, but it seems like there was no text provided for me to analyze. Could you please provide the text you're referring to?
- **`baseline|cuda`:** I'm sorry, but it seems like there was no text provided for me to analyze. Could you please provide the text you're referring to?
- **`rag|cpu`:** The text does not explicitly mention any limitations or future work.
- **`rag|cuda`:** The text does not explicitly mention any limitations or future work. It outlines the structure of the discussion section, which includes assumptions about RAG documents, analysis of failure cases, financial costs, and potential countermeasures against attacks. However, it does...
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
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.128</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.333</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;7.046</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;4.825</td>
</tr>
<tr>
<td style="text-align:left"><code>baseline|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.102</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.320</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.232</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;30.833</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cpu</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.099</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.615</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.307</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;30.905</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.830</td>
</tr>
<tr>
<td style="text-align:left"><code>rag|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.094</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.467</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.315</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.523</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;37.738</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cpu</code></td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.128</td>
<td style="text-align:right">—</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;0.333</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;10.344</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;3.287</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned|cuda</code></td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.067</td>
<td style="text-align:right">—</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.290</td>
<td style="background-color:#c6efce;text-align:right;white-space:nowrap">🟢&nbsp;1.111</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;27.913</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned_with_rag|cpu</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.095</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.466</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.315</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;45.106</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;2.850</td>
</tr>
<tr>
<td style="text-align:left"><code>fine_tuned_with_rag|cuda</code></td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.094</td>
<td style="background-color:#ffc7ce;text-align:right;white-space:nowrap">🔴&nbsp;0.467</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;0.315</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;3.985</td>
<td style="background-color:#ffeb9c;text-align:right;white-space:nowrap">🟡&nbsp;33.242</td>
</tr>
</tbody>
</table>

**CPU → GPU speedup (time_to_response):**
- **baseline:** 7.05s (CPU) → 1.23s (GPU) = **5.7×** faster time-to-response
- **fine_tuned:** 10.34s (CPU) → 1.11s (GPU) = **9.3×** faster time-to-response
- **fine_tuned_with_rag:** 45.11s (CPU) → 3.98s (GPU) = **11.3×** faster time-to-response
- **rag:** 30.91s (CPU) → 3.52s (GPU) = **8.8×** faster time-to-response

<details><summary>Sample answers</summary>

- **`baseline|cpu`:** The passage you provided does not contain any information or context to identify a specific problem that the work addresses. Please provide the passage or additional details for a more accurate response.
- **`baseline|cuda`:** The passage you provided does not contain any information or context about a specific problem or work. Please provide the relevant passage or details about the work in question so that I can assist you better.
- **`rag|cpu`:** The passage discusses the problem of generating topic-focused descriptions using a RAG (Retrieval-Augmented Generation) system. It outlines the assumptions about the nature of the RAG documents in the setup, analyzes the failure cases observed during the attack, examines the f...
- **`rag|cuda`:** The passage discusses the issue of generating topic-focused descriptions using a RAG (Retrieval-Augmented Generation) system. It outlines the assumptions about the nature of the RAG documents in their setup, analyzes the failure cases observed during the attack, examines the f...
- **`fine_tuned|cpu`:** The passage you provided does not contain any information or context to identify a specific problem that the work addresses. Please provide the passage or additional details for a more accurate response.
- **`fine_tuned|cuda`:** The passage you provided does not contain any information or context. Please provide the passage you are referring to, so I can help identify the problem it addresses.
- **`fine_tuned_with_rag|cpu`:** The passage discusses the issue of generating topic-focused descriptions using a RAG (Retrieval-Augmented Generation) system. It outlines the assumptions about the nature of the RAG documents in the setup, analyzes the failure cases observed during the attack, examines the fin...
- **`fine_tuned_with_rag|cuda`:** The passage discusses the issue of generating topic-focused descriptions using a RAG (Retrieval-Augmented Generation) system. It outlines the assumptions about the nature of the RAG documents in their setup, analyzes the failure cases observed during the attack, examines the f...

</details>
