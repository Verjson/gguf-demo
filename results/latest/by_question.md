# Results by question

Each question shows quality **and** latency across approach × device.

- **Quality:** higher `quality_score` / `rougeL` is better
- **Time to response:** `retrieval_time` + `generation_time` (seconds) — **lower is better**
- **GPU speedup:** CPU time ÷ GPU time (values **> 1×** mean GPU was faster)

_Generated: 2026-08-12T17:50:47.543872+00:00_

## Overview — quality (`quality_score`)

| Question | `baseline|cpu` | `baseline|cuda` | `rag|cpu` | `rag|cuda` | `fine_tuned|cpu` | `fine_tuned|cuda` | `fine_tuned_with_rag|cpu` | `fine_tuned_with_rag|cuda` |
|----------|------|------|------|------|------|------|------|------|
| According to this passage, what is the main claim or cont... | — | 0.267 | — | 0.290 | — | 0.267 | — | 0.300 |
| Summarize the contribution of 'Automated Literature Revie... | — | 0.438 | — | 0.566 | — | 0.484 | — | 0.593 |
| Summarize the contribution of 'Lightweight and Direct Doc... | — | 0.375 | — | 0.366 | — | 0.382 | — | 0.365 |
| What experimental result or finding is reported here? | — | 0.256 | — | 0.237 | — | 0.256 | — | 0.237 |
| What is the paper 'MUST-RAG: MUSical Text Question Answer... | — | 0.342 | — | 0.538 | — | 0.348 | — | 0.537 |
| What limitation or future work is mentioned in this text? | — | 0.264 | — | 0.218 | — | 0.264 | — | 0.218 |
| What method or approach is described in this excerpt? | — | 0.317 | — | 0.258 | — | 0.317 | — | 0.258 |
| What problem does this passage say the work addresses? | — | 0.282 | — | 0.293 | — | 0.282 | — | 0.293 |

## Overview — time to response (seconds, lower is better)

| Question | `baseline|cpu` | `baseline|cuda` | `rag|cpu` | `rag|cuda` | `fine_tuned|cpu` | `fine_tuned|cuda` | `fine_tuned_with_rag|cpu` | `fine_tuned_with_rag|cuda` |
|----------|------|------|------|------|------|------|------|------|
| According to this passage, what is the main claim or cont... | 1.158 | 1.333 | 2.893 | 2.847 | 1.313 | 1.231 | 5.656 | 6.024 |
| Summarize the contribution of 'Automated Literature Revie... | 9.578 | 10.513 | 11.399 | 11.399 | 6.131 | 6.131 | 7.084 | 7.084 |
| Summarize the contribution of 'Lightweight and Direct Doc... | 5.236 | 5.829 | 7.683 | 7.683 | 6.256 | 6.256 | 8.053 | 8.053 |
| What experimental result or finding is reported here? | 1.671 | 2.248 | 5.477 | 5.690 | 1.804 | 1.800 | 5.719 | 5.675 |
| What is the paper 'MUST-RAG: MUSical Text Question Answer... | 11.321 | 12.022 | 12.329 | 12.329 | 13.842 | 13.842 | 12.798 | 12.798 |
| What limitation or future work is mentioned in this text? | 1.870 | 1.544 | 0.874 | 0.874 | 1.464 | 1.464 | 0.614 | 0.614 |
| What method or approach is described in this excerpt? | 2.900 | 3.253 | 8.224 | 8.104 | 3.014 | 3.039 | 8.565 | 8.383 |
| What problem does this passage say the work addresses? | 1.214 | 1.370 | 6.126 | 5.974 | 1.273 | 1.227 | 6.377 | 5.708 |

---

## Q1. According to this passage, what is the main claim or contribution?

| Approach × Device | quality_score | rougeL | bert_score | retrieval_hit_at_k | faithfulness | retrieval_time | generation_time | time_to_response | speed_chars_per_sec |
|-------------------|---|---|---|---|---|---|---|---|---|
| `baseline|cpu` | — | 0.062 | 0.818 | — | — | 0.000 | 1.158 | 1.158 | 116.565 |
| `baseline|cuda` | 0.267 | 0.049 | 0.813 | — | — | 0.000 | 1.333 | 1.333 | 101.258 |
| `rag|cpu` | — | 0.044 | 0.816 | 0.000 | 0.514 | 0.021 | 2.872 | 2.893 | 122.567 |
| `rag|cuda` | 0.290 | 0.093 | 0.814 | 0.000 | 0.514 | 0.014 | 2.833 | 2.847 | 124.256 |
| `fine_tuned|cpu` | — | 0.062 | 0.818 | — | — | 0.000 | 1.313 | 1.313 | 102.810 |
| `fine_tuned|cuda` | 0.267 | 0.049 | 0.813 | — | — | 0.000 | 1.231 | 1.231 | 109.663 |
| `fine_tuned_with_rag|cpu` | — | 0.061 | 0.811 | 0.000 | 0.625 | 0.013 | 5.643 | 5.656 | 97.297 |
| `fine_tuned_with_rag|cuda` | 0.300 | 0.067 | 0.811 | 0.000 | 0.625 | 0.016 | 6.008 | 6.024 | 91.374 |

**CPU → GPU speedup (time_to_response):**
- **baseline:** 1.16s (CPU) → 1.33s (GPU) = **0.9×** faster time-to-response
- **fine_tuned:** 1.31s (CPU) → 1.23s (GPU) = **1.1×** faster time-to-response
- **fine_tuned_with_rag:** 5.66s (CPU) → 6.02s (GPU) = **0.9×** faster time-to-response
- **rag:** 2.89s (CPU) → 2.85s (GPU) = **1.0×** faster time-to-response

<details><summary>Sample answers</summary>

- **`baseline|cpu`:** I'm sorry, but it seems like there was no passage provided for me to analyze. Could you please provide the passage you're referring to?
- **`baseline|cuda`:** I'm sorry, but it seems like there was no passage provided for me to analyze. Could you please provide the passage you're referring to?
- **`rag|cpu`:** Question: What are the key assumptions about the nature of RAG documents in the discussed setup?  Question: What are the failure cases observed during the attack analysis?  Question: What are the financial costs involved in launching the attack?  Question: What potential count...
- **`rag|cuda`:** Question: What are the key assumptions about the nature of RAG documents in the discussed setup?  Question: What are the failure cases observed during the attack analysis?  Question: What are the financial costs involved in launching the attack?  Question: What potential count...
- **`fine_tuned|cpu`:** I'm sorry, but it seems like there was no passage provided for me to analyze. Could you please provide the passage you're referring to?
- **`fine_tuned|cuda`:** I'm sorry, but it seems like there was no passage provided for me to analyze. Could you please provide the passage you're referring to?
- **`fine_tuned_with_rag|cpu`:** 1. What are the assumptions regarding the nature of the RAG documents in the setup? 2. What are the failure cases observed during the attack? 3. What are the financial costs involved in launching the attack? 4. What potential countermeasures against the attack are discussed, a...
- **`fine_tuned_with_rag|cuda`:** 1. What are the assumptions regarding the nature of the RAG documents in the setup? 2. What are the failure cases observed during the attack? 3. What are the financial costs involved in launching the attack? 4. What potential countermeasures against the attack are discussed, a...

</details>

## Q2. Summarize the contribution of 'Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation'.

| Approach × Device | quality_score | rougeL | bert_score | retrieval_hit_at_k | faithfulness | retrieval_time | generation_time | time_to_response | speed_chars_per_sec |
|-------------------|---|---|---|---|---|---|---|---|---|
| `baseline|cpu` | — | 0.204 | 0.871 | — | — | 0.000 | 9.578 | 9.578 | 135.733 |
| `baseline|cuda` | 0.438 | 0.204 | 0.871 | — | — | 0.000 | 10.513 | 10.513 | 123.657 |
| `rag|cpu` | — | 0.197 | 0.878 | 1.000 | 0.699 | 0.015 | 11.384 | 11.399 | 112.697 |
| `rag|cuda` | 0.566 | 0.197 | 0.878 | 1.000 | 0.699 | 0.015 | 11.384 | 11.399 | 112.697 |
| `fine_tuned|cpu` | — | 0.280 | 0.877 | — | — | 0.000 | 6.131 | 6.131 | 122.659 |
| `fine_tuned|cuda` | 0.484 | 0.280 | 0.877 | — | — | 0.000 | 6.131 | 6.131 | 122.659 |
| `fine_tuned_with_rag|cpu` | — | 0.284 | 0.884 | 1.000 | 0.646 | 0.013 | 7.071 | 7.084 | 105.636 |
| `fine_tuned_with_rag|cuda` | 0.593 | 0.284 | 0.884 | 1.000 | 0.646 | 0.013 | 7.071 | 7.084 | 105.636 |

**CPU → GPU speedup (time_to_response):**
- **baseline:** 9.58s (CPU) → 10.51s (GPU) = **0.9×** faster time-to-response
- **fine_tuned:** 6.13s (CPU) → 6.13s (GPU) = **1.0×** faster time-to-response
- **fine_tuned_with_rag:** 7.08s (CPU) → 7.08s (GPU) = **1.0×** faster time-to-response
- **rag:** 11.40s (CPU) → 11.40s (GPU) = **1.0×** faster time-to-response

<details><summary>Sample answers</summary>

- **`baseline|cpu`:** The contribution of 'Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation' lies in the development of a system that streamlines the process of conducting literature reviews in academic research. This system leverages Natural Language Pr...
- **`baseline|cuda`:** The contribution of 'Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation' lies in the development of a system that streamlines the process of conducting literature reviews in academic research. This system leverages Natural Language Pr...
- **`rag|cpu`:** The research paper titled "Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation" by Nurshat Fateh Ali, Shakil Mosharrof, and Md. Mahdi Mohtasim focuses on developing an automated system for generating literature reviews. The primary obj...
- **`rag|cuda`:** The research paper titled "Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation" by Nurshat Fateh Ali, Shakil Mosharrof, and Md. Mahdi Mohtasim focuses on developing an automated system for generating literature reviews. The primary obj...
- **`fine_tuned|cpu`:** The contribution of 'Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation' lies in the development of a system that streamlines the process of conducting literature reviews. This system leverages Natural Language Processing (NLP) techni...
- **`fine_tuned|cuda`:** The contribution of 'Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation' lies in the development of a system that streamlines the process of conducting literature reviews. This system leverages Natural Language Processing (NLP) techni...
- **`fine_tuned_with_rag|cpu`:** The research paper titled "Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation" aims to develop an automated system for generating literature reviews from research articles. The authors, Nurshat Fateh Ali, Shakil Mosharrof, and Md. Mah...
- **`fine_tuned_with_rag|cuda`:** The research paper titled "Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation" aims to develop an automated system for generating literature reviews from research articles. The authors, Nurshat Fateh Ali, Shakil Mosharrof, and Md. Mah...

</details>

## Q3. Summarize the contribution of 'Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval'.

| Approach × Device | quality_score | rougeL | bert_score | retrieval_hit_at_k | faithfulness | retrieval_time | generation_time | time_to_response | speed_chars_per_sec |
|-------------------|---|---|---|---|---|---|---|---|---|
| `baseline|cpu` | — | 0.124 | 0.841 | — | — | 0.000 | 5.236 | 5.236 | 147.063 |
| `baseline|cuda` | 0.375 | 0.124 | 0.841 | — | — | 0.000 | 5.829 | 5.829 | 132.096 |
| `rag|cpu` | — | 0.183 | 0.845 | 0.000 | 0.565 | 0.014 | 7.669 | 7.683 | 114.881 |
| `rag|cuda` | 0.366 | 0.183 | 0.845 | 0.000 | 0.565 | 0.014 | 7.669 | 7.683 | 114.881 |
| `fine_tuned|cpu` | — | 0.131 | 0.844 | — | — | 0.000 | 6.256 | 6.256 | 131.722 |
| `fine_tuned|cuda` | 0.382 | 0.131 | 0.844 | — | — | 0.000 | 6.256 | 6.256 | 131.722 |
| `fine_tuned_with_rag|cpu` | — | 0.184 | 0.846 | 0.000 | 0.553 | 0.012 | 8.041 | 8.053 | 109.190 |
| `fine_tuned_with_rag|cuda` | 0.365 | 0.184 | 0.846 | 0.000 | 0.553 | 0.012 | 8.041 | 8.053 | 109.190 |

**CPU → GPU speedup (time_to_response):**
- **baseline:** 5.24s (CPU) → 5.83s (GPU) = **0.9×** faster time-to-response
- **fine_tuned:** 6.26s (CPU) → 6.26s (GPU) = **1.0×** faster time-to-response
- **fine_tuned_with_rag:** 8.05s (CPU) → 8.05s (GPU) = **1.0×** faster time-to-response
- **rag:** 7.68s (CPU) → 7.68s (GPU) = **1.0×** faster time-to-response

<details><summary>Sample answers</summary>

- **`baseline|cpu`:** The contribution of 'Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval' lies in enhancing the efficiency and accuracy of information retrieval systems. By focusing on lightweight algorithms, the approach minimizes computational overhea...
- **`baseline|cuda`:** The contribution of 'Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval' lies in enhancing the efficiency and accuracy of information retrieval systems. By focusing on lightweight algorithms, the approach minimizes computational overhea...
- **`rag|cpu`:** The contribution of "Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval" is focused on improving the performance of Generative Information Retrieval (GenIR) models. GenIR models, which are based on large pre-trained language models like...
- **`rag|cuda`:** The contribution of "Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval" is focused on improving the performance of Generative Information Retrieval (GenIR) models. GenIR models, which are based on large pre-trained language models like...
- **`fine_tuned|cpu`:** The contribution of 'Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval' lies in enhancing the efficiency and accuracy of information retrieval systems. By focusing on lightweight algorithms, the approach reduces computational overhead,...
- **`fine_tuned|cuda`:** The contribution of 'Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval' lies in enhancing the efficiency and accuracy of information retrieval systems. By focusing on lightweight algorithms, the approach reduces computational overhead,...
- **`fine_tuned_with_rag|cpu`:** The contribution of "Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval" is focused on improving the performance of Generative Information Retrieval (GenIR) models. GenIR models, which are based on large pre-trained language models like...
- **`fine_tuned_with_rag|cuda`:** The contribution of "Lightweight and Direct Document Relevance Optimization for Generative Information Retrieval" is focused on improving the performance of Generative Information Retrieval (GenIR) models. GenIR models, which are based on large pre-trained language models like...

</details>

## Q4. What experimental result or finding is reported here?

| Approach × Device | quality_score | rougeL | bert_score | retrieval_hit_at_k | faithfulness | retrieval_time | generation_time | time_to_response | speed_chars_per_sec |
|-------------------|---|---|---|---|---|---|---|---|---|
| `baseline|cpu` | — | 0.081 | 0.833 | — | — | 0.000 | 1.671 | 1.671 | 137.030 |
| `baseline|cuda` | 0.256 | 0.015 | 0.776 | — | — | 0.000 | 2.248 | 2.248 | 101.858 |
| `rag|cpu` | — | 0.073 | 0.812 | 0.000 | 0.292 | 0.010 | 5.467 | 5.477 | 93.282 |
| `rag|cuda` | 0.237 | 0.060 | 0.794 | 0.000 | 0.292 | 0.011 | 5.679 | 5.690 | 89.805 |
| `fine_tuned|cpu` | — | 0.081 | 0.833 | — | — | 0.000 | 1.804 | 1.804 | 126.949 |
| `fine_tuned|cuda` | 0.256 | 0.015 | 0.776 | — | — | 0.000 | 1.800 | 1.800 | 127.230 |
| `fine_tuned_with_rag|cpu` | — | 0.073 | 0.812 | 0.000 | 0.292 | 0.011 | 5.707 | 5.719 | 89.358 |
| `fine_tuned_with_rag|cuda` | 0.237 | 0.060 | 0.794 | 0.000 | 0.292 | 0.014 | 5.661 | 5.675 | 90.098 |

**CPU → GPU speedup (time_to_response):**
- **baseline:** 1.67s (CPU) → 2.25s (GPU) = **0.7×** faster time-to-response
- **fine_tuned:** 1.80s (CPU) → 1.80s (GPU) = **1.0×** faster time-to-response
- **fine_tuned_with_rag:** 5.72s (CPU) → 5.67s (GPU) = **1.0×** faster time-to-response
- **rag:** 5.48s (CPU) → 5.69s (GPU) = **1.0×** faster time-to-response

<details><summary>Sample answers</summary>

- **`baseline|cpu`:** I'm sorry, but it seems like you haven't provided any context or content for me to identify an experimental result or finding. Please provide the relevant information or details about the experiment or study you are referring to.
- **`baseline|cuda`:** I'm sorry, but it seems like you haven't provided any context or content for me to identify an experimental result or finding. Please provide the relevant information or details about the experiment or study you are referring to.
- **`rag|cpu`:** The experimental results reported here are the performance metrics of various retrieval-based models on the ICU readmission prediction task. The models evaluated are REMed, VanillaEHR-RAGp, and Mistral 7b. The performance metrics include accuracy, precision, recall, F1-score, ...
- **`rag|cuda`:** The experimental results reported here are the performance metrics of various retrieval-based models on the ICU readmission prediction task. The models evaluated are REMed, VanillaEHR-RAGp, and Mistral 7b. The performance metrics include accuracy, precision, recall, F1-score, ...
- **`fine_tuned|cpu`:** I'm sorry, but it seems like you haven't provided any context or content for me to identify an experimental result or finding. Please provide the relevant information or details about the experiment or study you are referring to.
- **`fine_tuned|cuda`:** I'm sorry, but it seems like you haven't provided any context or content for me to identify an experimental result or finding. Please provide the relevant information or details about the experiment or study you are referring to.
- **`fine_tuned_with_rag|cpu`:** The experimental results reported here are the performance metrics of various retrieval-based models on the ICU readmission prediction task. The models evaluated are REMed, VanillaEHR-RAGp, and Mistral 7b. The performance metrics include accuracy, precision, recall, F1-score, ...
- **`fine_tuned_with_rag|cuda`:** The experimental results reported here are the performance metrics of various retrieval-based models on the ICU readmission prediction task. The models evaluated are REMed, VanillaEHR-RAGp, and Mistral 7b. The performance metrics include accuracy, precision, recall, F1-score, ...

</details>

## Q5. What is the paper 'MUST-RAG: MUSical Text Question Answering with Retrieval Augmented Generation' about?

| Approach × Device | quality_score | rougeL | bert_score | retrieval_hit_at_k | faithfulness | retrieval_time | generation_time | time_to_response | speed_chars_per_sec |
|-------------------|---|---|---|---|---|---|---|---|---|
| `baseline|cpu` | — | 0.085 | 0.830 | — | — | 0.000 | 11.321 | 11.321 | 134.261 |
| `baseline|cuda` | 0.342 | 0.085 | 0.830 | — | — | 0.000 | 12.022 | 12.022 | 126.430 |
| `rag|cpu` | — | 0.157 | 0.848 | 1.000 | 0.716 | 0.012 | 12.318 | 12.329 | 112.033 |
| `rag|cuda` | 0.538 | 0.157 | 0.848 | 1.000 | 0.716 | 0.012 | 12.318 | 12.329 | 112.033 |
| `fine_tuned|cpu` | — | 0.090 | 0.827 | — | — | 0.000 | 13.842 | 13.842 | 122.022 |
| `fine_tuned|cuda` | 0.348 | 0.090 | 0.827 | — | — | 0.000 | 13.842 | 13.842 | 122.022 |
| `fine_tuned_with_rag|cpu` | — | 0.157 | 0.848 | 1.000 | 0.716 | 0.015 | 12.782 | 12.798 | 108.041 |
| `fine_tuned_with_rag|cuda` | 0.537 | 0.157 | 0.848 | 1.000 | 0.716 | 0.015 | 12.782 | 12.798 | 108.041 |

**CPU → GPU speedup (time_to_response):**
- **baseline:** 11.32s (CPU) → 12.02s (GPU) = **0.9×** faster time-to-response
- **fine_tuned:** 13.84s (CPU) → 13.84s (GPU) = **1.0×** faster time-to-response
- **fine_tuned_with_rag:** 12.80s (CPU) → 12.80s (GPU) = **1.0×** faster time-to-response
- **rag:** 12.33s (CPU) → 12.33s (GPU) = **1.0×** faster time-to-response

<details><summary>Sample answers</summary>

- **`baseline|cpu`:** The paper "MUST-RAG: MUSical Text Question Answering with Retrieval Augmented Generation" focuses on developing a system for answering questions about musical texts, such as lyrics or scores, using a combination of retrieval-augmented generation (RAG) and a specialized knowled...
- **`baseline|cuda`:** The paper "MUST-RAG: MUSical Text Question Answering with Retrieval Augmented Generation" focuses on developing a system for answering questions about musical texts, such as lyrics or scores, using a combination of retrieval-augmented generation (RAG) and a specialized knowled...
- **`rag|cpu`:** The paper 'MUST-RAG: MUSical Text Question Answering with Retrieval Augmented Generation' by Daeyong Kwon, SeungHeon Doh, and Juhan Nam, from the Graduate School of Culture Technology at KAIST, South Korea, focuses on addressing the limitations of Large Language Models (LLMs) ...
- **`rag|cuda`:** The paper 'MUST-RAG: MUSical Text Question Answering with Retrieval Augmented Generation' by Daeyong Kwon, SeungHeon Doh, and Juhan Nam, from the Graduate School of Culture Technology at KAIST, South Korea, focuses on addressing the limitations of Large Language Models (LLMs) ...
- **`fine_tuned|cpu`:** The paper "MUST-RAG: MUSical Text Question Answering with Retrieval Augmented Generation" focuses on developing a system for answering questions about musical texts, such as lyrics or scores, using a combination of retrieval-augmented generation (RAG) and a pre-trained languag...
- **`fine_tuned|cuda`:** The paper "MUST-RAG: MUSical Text Question Answering with Retrieval Augmented Generation" focuses on developing a system for answering questions about musical texts, such as lyrics or scores, using a combination of retrieval-augmented generation (RAG) and a pre-trained languag...
- **`fine_tuned_with_rag|cpu`:** The paper 'MUST-RAG: MUSical Text Question Answering with Retrieval Augmented Generation' by Daeyong Kwon, SeungHeon Doh, and Juhan Nam, from the Graduate School of Culture Technology at KAIST, South Korea, focuses on addressing the limitations of Large Language Models (LLMs) ...
- **`fine_tuned_with_rag|cuda`:** The paper 'MUST-RAG: MUSical Text Question Answering with Retrieval Augmented Generation' by Daeyong Kwon, SeungHeon Doh, and Juhan Nam, from the Graduate School of Culture Technology at KAIST, South Korea, focuses on addressing the limitations of Large Language Models (LLMs) ...

</details>

## Q6. What limitation or future work is mentioned in this text?

| Approach × Device | quality_score | rougeL | bert_score | retrieval_hit_at_k | faithfulness | retrieval_time | generation_time | time_to_response | speed_chars_per_sec |
|-------------------|---|---|---|---|---|---|---|---|---|
| `baseline|cpu` | — | 0.062 | 0.821 | — | — | 0.000 | 1.870 | 1.870 | 68.977 |
| `baseline|cuda` | 0.264 | 0.062 | 0.821 | — | — | 0.000 | 1.544 | 1.544 | 83.533 |
| `rag|cpu` | — | 0.040 | 0.834 | 0.000 | 0.222 | 0.015 | 0.859 | 0.874 | 79.173 |
| `rag|cuda` | 0.218 | 0.040 | 0.834 | 0.000 | 0.222 | 0.015 | 0.859 | 0.874 | 79.173 |
| `fine_tuned|cpu` | — | 0.062 | 0.821 | — | — | 0.000 | 1.464 | 1.464 | 88.116 |
| `fine_tuned|cuda` | 0.264 | 0.062 | 0.821 | — | — | 0.000 | 1.464 | 1.464 | 88.116 |
| `fine_tuned_with_rag|cpu` | — | 0.040 | 0.834 | 0.000 | 0.222 | 0.014 | 0.600 | 0.614 | 113.365 |
| `fine_tuned_with_rag|cuda` | 0.218 | 0.040 | 0.834 | 0.000 | 0.222 | 0.014 | 0.600 | 0.614 | 113.365 |

**CPU → GPU speedup (time_to_response):**
- **baseline:** 1.87s (CPU) → 1.54s (GPU) = **1.2×** faster time-to-response
- **fine_tuned:** 1.46s (CPU) → 1.46s (GPU) = **1.0×** faster time-to-response
- **fine_tuned_with_rag:** 0.61s (CPU) → 0.61s (GPU) = **1.0×** faster time-to-response
- **rag:** 0.87s (CPU) → 0.87s (GPU) = **1.0×** faster time-to-response

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

| Approach × Device | quality_score | rougeL | bert_score | retrieval_hit_at_k | faithfulness | retrieval_time | generation_time | time_to_response | speed_chars_per_sec |
|-------------------|---|---|---|---|---|---|---|---|---|
| `baseline|cpu` | — | 0.064 | 0.818 | — | — | 0.000 | 2.900 | 2.900 | 137.595 |
| `baseline|cuda` | 0.317 | 0.070 | 0.796 | — | — | 0.000 | 3.253 | 3.253 | 122.665 |
| `rag|cpu` | — | 0.034 | 0.774 | 0.000 | 0.508 | 0.014 | 8.211 | 8.224 | 69.909 |
| `rag|cuda` | 0.258 | 0.058 | 0.758 | 0.000 | 0.508 | 0.014 | 8.089 | 8.104 | 70.957 |
| `fine_tuned|cpu` | — | 0.064 | 0.818 | — | — | 0.000 | 3.014 | 3.014 | 132.393 |
| `fine_tuned|cuda` | 0.317 | 0.070 | 0.796 | — | — | 0.000 | 3.039 | 3.039 | 131.314 |
| `fine_tuned_with_rag|cpu` | — | 0.034 | 0.774 | 0.000 | 0.508 | 0.013 | 8.552 | 8.565 | 67.119 |
| `fine_tuned_with_rag|cuda` | 0.258 | 0.058 | 0.758 | 0.000 | 0.508 | 0.011 | 8.372 | 8.383 | 68.559 |

**CPU → GPU speedup (time_to_response):**
- **baseline:** 2.90s (CPU) → 3.25s (GPU) = **0.9×** faster time-to-response
- **fine_tuned:** 3.01s (CPU) → 3.04s (GPU) = **1.0×** faster time-to-response
- **fine_tuned_with_rag:** 8.56s (CPU) → 8.38s (GPU) = **1.0×** faster time-to-response
- **rag:** 8.22s (CPU) → 8.10s (GPU) = **1.0×** faster time-to-response

<details><summary>Sample answers</summary>

- **`baseline|cpu`:** The method or approach described in this excerpt is the scientific method. The scientific method is a systematic and logical approach to discovering how things in the universe work. It involves making observations, forming a hypothesis, conducting experiments, analyzing data, ...
- **`baseline|cuda`:** The method or approach described in this excerpt is the scientific method. The scientific method is a systematic and logical approach to discovering how things in the universe work. It involves making observations, forming a hypothesis, conducting experiments, analyzing data, ...
- **`rag|cpu`:** [MASK_1]: extension [MASK_2]: PageRank [MASK_3]: comprehensive [MASK_4]: PageRank model [MASK_5]: storage issues [MASK_6]: possible alterations [MASK_7]: sensitivity and conditioning [MASK_8]: introduce [MASK_9]: extensive reference list [MASK_10]: exciting areas of future res...
- **`rag|cuda`:** [MASK_1]: extension [MASK_2]: PageRank [MASK_3]: comprehensive [MASK_4]: PageRank model [MASK_5]: storage issues [MASK_6]: possible alterations [MASK_7]: sensitivity and conditioning [MASK_8]: introduce [MASK_9]: extensive reference list [MASK_10]: exciting areas of future res...
- **`fine_tuned|cpu`:** The method or approach described in this excerpt is the scientific method. The scientific method is a systematic and logical approach to discovering how things in the universe work. It involves making observations, forming a hypothesis, conducting experiments, analyzing data, ...
- **`fine_tuned|cuda`:** The method or approach described in this excerpt is the scientific method. The scientific method is a systematic and logical approach to discovering how things in the universe work. It involves making observations, forming a hypothesis, conducting experiments, analyzing data, ...
- **`fine_tuned_with_rag|cpu`:** [MASK_1]: extension [MASK_2]: PageRank [MASK_3]: comprehensive [MASK_4]: PageRank model [MASK_5]: storage issues [MASK_6]: possible alterations [MASK_7]: sensitivity and conditioning [MASK_8]: introduce [MASK_9]: extensive reference list [MASK_10]: exciting areas of future res...
- **`fine_tuned_with_rag|cuda`:** [MASK_1]: extension [MASK_2]: PageRank [MASK_3]: comprehensive [MASK_4]: PageRank model [MASK_5]: storage issues [MASK_6]: possible alterations [MASK_7]: sensitivity and conditioning [MASK_8]: introduce [MASK_9]: extensive reference list [MASK_10]: exciting areas of future res...

</details>

## Q8. What problem does this passage say the work addresses?

| Approach × Device | quality_score | rougeL | bert_score | retrieval_hit_at_k | faithfulness | retrieval_time | generation_time | time_to_response | speed_chars_per_sec |
|-------------------|---|---|---|---|---|---|---|---|---|
| `baseline|cpu` | — | 0.074 | 0.803 | — | — | 0.000 | 1.214 | 1.214 | 137.558 |
| `baseline|cuda` | 0.282 | 0.050 | 0.803 | — | — | 0.000 | 1.370 | 1.370 | 121.866 |
| `rag|cpu` | — | 0.077 | 0.804 | 0.000 | 0.438 | 0.014 | 6.112 | 6.126 | 119.429 |
| `rag|cuda` | 0.293 | 0.052 | 0.815 | 0.000 | 0.438 | 0.011 | 5.963 | 5.974 | 122.414 |
| `fine_tuned|cpu` | — | 0.074 | 0.803 | — | — | 0.000 | 1.273 | 1.273 | 131.145 |
| `fine_tuned|cuda` | 0.282 | 0.050 | 0.803 | — | — | 0.000 | 1.227 | 1.227 | 136.148 |
| `fine_tuned_with_rag|cpu` | — | 0.077 | 0.804 | 0.000 | 0.438 | 0.014 | 6.363 | 6.377 | 114.727 |
| `fine_tuned_with_rag|cuda` | 0.293 | 0.052 | 0.815 | 0.000 | 0.438 | 0.010 | 5.698 | 5.708 | 128.123 |

**CPU → GPU speedup (time_to_response):**
- **baseline:** 1.21s (CPU) → 1.37s (GPU) = **0.9×** faster time-to-response
- **fine_tuned:** 1.27s (CPU) → 1.23s (GPU) = **1.0×** faster time-to-response
- **fine_tuned_with_rag:** 6.38s (CPU) → 5.71s (GPU) = **1.1×** faster time-to-response
- **rag:** 6.13s (CPU) → 5.97s (GPU) = **1.0×** faster time-to-response

<details><summary>Sample answers</summary>

- **`baseline|cpu`:** The passage you provided does not contain any information or context. Please provide the passage you are referring to, so I can help identify the problem it addresses.
- **`baseline|cuda`:** The passage you provided does not contain any information or context. Please provide the passage you are referring to, so I can help identify the problem it addresses.
- **`rag|cpu`:** The passage discusses the issue of generating topic-focused descriptions using a RAG (Retrieval-Augmented Generation) system. It outlines the assumptions about the nature of the RAG documents in their setup, analyzes the failure cases observed during the attack, examines the f...
- **`rag|cuda`:** The passage discusses the issue of generating topic-focused descriptions using a RAG (Retrieval-Augmented Generation) system. It outlines the assumptions about the nature of the RAG documents in their setup, analyzes the failure cases observed during the attack, examines the f...
- **`fine_tuned|cpu`:** The passage you provided does not contain any information or context. Please provide the passage you are referring to, so I can help identify the problem it addresses.
- **`fine_tuned|cuda`:** The passage you provided does not contain any information or context. Please provide the passage you are referring to, so I can help identify the problem it addresses.
- **`fine_tuned_with_rag|cpu`:** The passage discusses the issue of generating topic-focused descriptions using a RAG (Retrieval-Augmented Generation) system. It outlines the assumptions about the nature of the RAG documents in their setup, analyzes the failure cases observed during the attack, examines the f...
- **`fine_tuned_with_rag|cuda`:** The passage discusses the issue of generating topic-focused descriptions using a RAG (Retrieval-Augmented Generation) system. It outlines the assumptions about the nature of the RAG documents in their setup, analyzes the failure cases observed during the attack, examines the f...

</details>
