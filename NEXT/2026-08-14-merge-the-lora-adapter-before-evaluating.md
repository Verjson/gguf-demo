---
date: 2026-08-14
issue:
title: Merge the LoRA adapter before evaluating it
---

Step 06 wrapped the base model in a `PeftModel` and evaluated it unmerged, so every forward pass computed the base and the delta separately. Evaluation only ever does forward passes, so `merge_and_unload()` folds the adapter into the base weights — faster decode, and the adapter tensors are freed.

Merging is slightly lossy in bfloat16, since the delta is rounded into the base. That is the accepted trade for inference, not for training, and the load falls back to the unmerged adapter if merging fails.
