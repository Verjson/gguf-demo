---
date: 2026-08-14
issue:
title: Delete the third definition of evaluation_metrics
---

`scripts/migrate_metrics_table.sql` was a third definition of the table, alongside
`init-db.sql` and `_ENSURE_SCHEMA_STATEMENTS`. It had drifted to 22 columns while the other
two reached 43 — missing `run_id`, `run_started_at`, `runtime`, `weight_format`,
`tokens_per_sec` and the rest — and `src/metrics_store.py` still claimed to match it.

It had no job left: `ensure_schema()` runs on every connect and applies the same additive
migrations automatically, which is why nobody noticed the drift. Deleting it leaves the two
definitions `tests/test_schema_parity.py` already holds in step, and that test now also
fails if a third one reappears.

The README's troubleshooting row no longer sends readers to a file that would have
under-migrated their volume.
