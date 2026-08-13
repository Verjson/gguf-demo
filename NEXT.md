# Next

## Fixed

- Make the full pipeline build a lean CPU image on CPU-only Docker hosts while automatically selecting CUDA and its GPU-only dependencies when available; honor the default CPU fine-tuning skip, cap evaluation answers at a CPU-practical length, and fix the clean-image LangChain packaging constraint for memory-constrained WSL environments.
