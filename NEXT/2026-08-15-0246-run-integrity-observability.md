---
date: 2026-08-15
issue:
title: Make evaluation run integrity observable and fail closed
---

Evaluation stages now have durable lifecycle rows and stable sample IDs. Duplicate prompt
text remains distinct, incomplete answers or failed MLflow/Postgres writes fail the stage,
Prometheus identifies runs and exposes completion counts, and Grafana adds a Run Integrity
dashboard. Existing-volume migrations install the same integrity constraints as fresh
volumes, live and peak memory are presented separately, and mixed models/runtimes remain
visible. The LLM judge cache and MLflow/Compose host validation integration also receive
adversarial fixes.
