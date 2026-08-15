---
date: 2026-08-15
issue:
title: Harden dependencies, model inputs, and containers
---

The app moves to current compatible Python and ML packages, including Transformers 5.15 to
remove model-loading vulnerabilities. Direct dependencies now have one source of truth in
`pyproject.toml`; a generated lock constrains the complete Python 3.14 dependency graph
in both images after installing the selected Torch build. The
sunset `langchain-community` package is replaced by a small pypdf loader. Model downloads
are pinned to immutable Hub revisions.

Python, pgvector/PostgreSQL 15, Prometheus, Grafana, and GitHub Actions are pinned to reviewed
versions and immutable digests/commits. Docker build context and dependency-layer ordering
are tightened, containers run without unnecessary capabilities, source/config mounts are
read-only, MLflow's wildcard host/CORS bypass is removed, and Grafana requires an explicit
admin secret. PostgreSQL remains on major 15 because an 18 upgrade requires a separately
verified data migration.

arXiv redirect validation, comparison output containment, source revision tagging, and
model-tokenizer revision handling also receive adversarial fixes.
