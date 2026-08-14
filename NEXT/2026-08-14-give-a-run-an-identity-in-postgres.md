---
date: 2026-08-14
issue:
title: Give a run an identity in Postgres and scope the dashboards to it
---

`evaluation_metrics` had no run column. `timestamp` is per-row, so a run had no boundary —
rows just smeared across a span — and because `gguf-demo_postgres_data` outlives every run,
each Grafana panel averaged every run ever recorded. Measured on a seeded database: three runs
plus one pre-GGUF row made `baseline · cpu` read `rougeL` 0.519, a number belonging to no run;
scoped to a run it reads 0.400 with n=3.

`run_id` (`<utc stamp>_<device>`, matching `results/runs/<run_id>/`) and `run_started_at` are
now written by `MetricsStore.insert()` from `RUN_ID` in the environment, which
`scripts/run_pipeline.sh` sets per step — `${TIMESTAMP}_cpu` for CPU steps and
`${TIMESTAMP}_cuda` for GPU steps, so the two legs stay separable while sharing the stamp that
groups them. Both columns are nullable with no default: a step run by hand, and every row
predating this change, belongs to no run and says so. Nothing is backfilled.

The three Postgres dashboards gained a **Run** picker (newest first) and lost their time
picker, which filtered nothing while implying it did. Quality & Latency also gained a
*Compare with* picker for an A/B against an earlier run. Every panel now filters on the
selected run, leads with a run header naming the run and its export folder, and reports `n`
next to each average with p50/p95 beside the mean. Live Ops is a live Prometheus scrape, is a
genuine time series, and keeps its time picker.

The GPU speedup panels joined their CPU and GPU legs on `approach` alone, so they could divide
one run's CPU latency by another run's GPU latency — different model, prompts and thread
budget — and print the quotient as a headline "×". Both legs are now pinned to one run.
Verified against a real Postgres: a run with only CPU data returns no rows rather than a
fabricated number, and a two-device run returns one row per approach.

`init-db.sql` and `_ENSURE_SCHEMA_STATEMENTS` had drifted by 16 columns — a fresh volume and
an existing one disagreed until the first write. They are back in step, and
`tests/test_schema_parity.py` fails when a column is added to one and not the other.
