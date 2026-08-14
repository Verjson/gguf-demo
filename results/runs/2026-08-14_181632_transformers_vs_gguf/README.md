# Transformers vs GGUF

- **Generated:** 2026-08-14T19:22:11.073971+00:00
- **Transformers:** Hugging Face + PyTorch safetensors (`microsoft/Phi-3-mini-4k-instruct`)
- **GGUF:** llama.cpp (`microsoft/Phi-3-mini-4k-instruct-gguf` Q4_K_M by default)

Same questions, same RAG index. Engines are swapped behind `src.llm.factory`.

## Device: `cpu` (`2026-08-14_181632_cpu`)

### `baseline` vs `baseline_gguf`

- **time_to_response:** Transformers 11.89s → GGUF 8.65s (**1.37×** vs Transformers)
- **tokens_per_sec:** Transformers 4.20 → GGUF 14.95
- **rougeL:** Transformers 0.0727 → GGUF 0.0890 (+0.0163)
- **peak_rss_mb:** Transformers 9449 → GGUF 7199

### `rag` vs `rag_gguf`

- **time_to_response:** Transformers 61.73s → GGUF 29.47s (**2.09×** vs Transformers)
- **tokens_per_sec:** Transformers 1.74 → GGUF 3.81
- **rougeL:** Transformers 0.0952 → GGUF 0.0922 (-0.0030)
- **peak_rss_mb:** Transformers 10773 → GGUF 7216

## Device: `cuda` (`2026-08-14_181632_cuda`)

### `baseline` vs `baseline_gguf`

- **time_to_response:** Transformers 2.20s → GGUF 7.95s (**0.28×** vs Transformers)
- **tokens_per_sec:** Transformers 22.46 → GGUF 16.22
- **rougeL:** Transformers 0.0711 → GGUF 0.0890 (+0.0179)
- **peak_rss_mb:** Transformers 5757 → GGUF 7077

### `rag` vs `rag_gguf`

- **time_to_response:** Transformers 4.07s → GGUF 13.17s (**0.31×** vs Transformers)
- **tokens_per_sec:** Transformers 29.15 → GGUF 8.98
- **rougeL:** Transformers 0.0983 → GGUF 0.0922 (-0.0061)
- **peak_rss_mb:** Transformers 5757 → GGUF 8136

