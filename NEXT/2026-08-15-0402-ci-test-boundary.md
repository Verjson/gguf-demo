---
date: 2026-08-15
issue:
title: Keep ML integration tests in the container job
---

- Exclude the Torch- and LangChain-dependent integration modules from the lightweight unit
  job; the full image job continues to run them against the production dependency set.
