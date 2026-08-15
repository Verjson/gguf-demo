# ADR 0001: Treat observability sinks as part of a successful evaluation run

- Status: Accepted
- Date: 2026-08-15

## Context

Answer rows were the only durable run record. A zero-row failure was invisible, a partial
run looked complete, duplicate question text collapsed distinct samples, and MLflow failures
were logged but did not fail the pipeline. Prometheus exposed cumulative device/approach
series with no run identity. The filesystem could therefore say `DONE` while MLflow,
Postgres, Prometheus, and exported results disagreed.

## Decision

Pipeline evaluation stages require MLflow and Postgres. `evaluation_runs` records one
lifecycle per `(run_id, approach)`, including expected and recorded sample counts, requested
and actual execution devices, runtime/format/model, MLflow run ID, completion status, and an
error. Answer rows use an ordinal `sample_id`; their uniqueness is `(run_id, approach,
sample_id)`, so repeated question text remains representable.

Prometheus series include controlled run, device, and approach labels, plus explicit
completion and sample-count gauges. Dead multiprocess shards are cleared when the app
exporter starts; Prometheus's TSDB, not stale exporter files, owns history. Grafana's Run
Integrity dashboard is the entry point for deciding whether a run is trustworthy.

Ad-hoc commands without `RUN_ID` remain best-effort so an unavailable tracking service does
not make a one-off local query unusable. A pipeline run is different: losing a required sink
is a failed benchmark, not a warning.

## Consequences

- A pipeline stops instead of exporting incomplete evidence.
- Existing answer rows receive UUID-derived legacy sample IDs during migration; their facts
  are preserved without inventing parent lifecycle records.
- Run IDs add limited Prometheus cardinality. Question, response, and model text remain out
  of labels.
- PostgreSQL stays on major 15 while the image moves to current pgvector and PostgreSQL 15
  patches. PostgreSQL 18 requires an explicit dump/restore or `pg_upgrade`; it is not safe to
  smuggle a major data migration into a dependency refresh.
