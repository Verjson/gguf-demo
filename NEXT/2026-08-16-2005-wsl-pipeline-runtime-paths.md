---
date: 2026-08-16
issue:
title: Repair WSL pipeline runtime paths and PostgreSQL collation metadata
---

- Write generated evaluation prompts to the writable processed-data mount while keeping
  application source and configuration read-only.
- Detect PostgreSQL collation drift after container image upgrades, rebuild affected
  indexes, and refresh the database metadata once before running schema migrations.
