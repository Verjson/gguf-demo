---
date: 2026-08-13
issue:
title: Build a lean CPU image by default and auto-select CUDA when available
---

Make the full pipeline build a lean CPU image on CPU-only Docker hosts while automatically selecting CUDA and its GPU-only dependencies when available; honor the default CPU fine-tuning skip, cap evaluation answers at a CPU-practical length, and fix the clean-image LangChain packaging constraint for memory-constrained WSL environments.
