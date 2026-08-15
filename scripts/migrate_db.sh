#!/usr/bin/env bash
# Bring an existing Postgres volume up to the current evaluation_metrics schema.
#
# Why this exists as a separate script rather than only inside the app:
#
#   init-db.sql runs once, when a volume is first created. Every later column was
#   added by MetricsStore.ensure_schema(), which runs when the *app container*
#   connects. That is fine until the app container is the thing that is broken —
#   and for several weeks it was unbuildable, which left the only migration path
#   behind the failure it needed to fix. A developer volume created before run_id
#   existed therefore had no run_id column, no index on it, and 631 rows that every
#   dashboard filtered out (all four require `run_id IS NOT NULL`), with no way to
#   repair it short of deleting the volume.
#
#   This needs only the postgres service, so it works whatever state the app is in.
#
# It is idempotent, and run_pipeline.sh calls it after the stack is up.
#
#   scripts/migrate_db.sh              # migrate
#   scripts/migrate_db.sh --check      # report drift, change nothing, exit 1 if any
set -euo pipefail

cd "$(dirname "$0")/.."

MODE=migrate
case "${1:-}" in
  "")        ;;
  --check)   MODE=check ;;
  -h|--help) sed -n '2,22p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
  *)         echo "unknown option: $1" >&2; exit 2 ;;
esac

COMPOSE=(docker compose)
PSQL=("${COMPOSE[@]}" exec -T postgres psql -U "${POSTGRES_USER:-raguser}" \
      -d "${POSTGRES_DB:-rag_eval}" -v ON_ERROR_STOP=1)

if ! "${PSQL[@]}" -c 'SELECT 1' >/dev/null 2>&1; then
  echo "ERROR: cannot reach the postgres service. Start it first:" >&2
  echo "         docker compose up -d postgres" >&2
  exit 1
fi

# Kept deliberately in step with init-db.sql and with _ENSURE_SCHEMA_STATEMENTS in
# src/metrics_store.py. tests/test_schema_parity.py fails when the three drift.
read -r -d '' MIGRATION <<'SQL' || true
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS evaluation_runs (
  run_id TEXT NOT NULL, approach VARCHAR(50) NOT NULL,
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), completed_at TIMESTAMPTZ,
  status VARCHAR(16) NOT NULL DEFAULT 'running', expected_samples INTEGER NOT NULL,
  recorded_samples INTEGER NOT NULL DEFAULT 0, requested_device VARCHAR(16),
  actual_device VARCHAR(16), runtime VARCHAR(32), weight_format VARCHAR(32),
  model_name TEXT, mlflow_run_id TEXT, error TEXT,
  PRIMARY KEY (run_id, approach)
);

ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS run_id TEXT;
ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS sample_id TEXT;
ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS run_started_at TIMESTAMPTZ;
ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS runtime VARCHAR(32);
ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS weight_format VARCHAR(32);
ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS n_gpu_layers FLOAT;
ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS rss_mb FLOAT;

-- The lowercase twin of "rougeL". Nothing ever wrote it — METRIC_COLUMNS only ever
-- emitted the quoted camelCase name — so it was permanently NULL while looking like
-- a real column, which is worse than not having it: an unquoted `rougeL` in a query
-- folds to this name and returns silence instead of an error.
ALTER TABLE evaluation_metrics DROP COLUMN IF EXISTS rougel;

-- One row per (run, approach, sample). Re-running a stage used to append a second
-- row for the same cell; dashboard 03 defended with DISTINCT ON while 02 and 04 used
-- plain AVG(), so after one re-run the same run reported n=15 on one dashboard and
-- n=30 on another. Historic rows have no run_id and are excluded from the constraint
-- rather than deleted.
UPDATE evaluation_metrics SET sample_id = id::text
WHERE run_id IS NOT NULL AND sample_id IS NULL;
DROP INDEX IF EXISTS uq_eval_metrics_run_cell;
CREATE UNIQUE INDEX IF NOT EXISTS uq_eval_metrics_run_sample
ON evaluation_metrics (run_id, approach, sample_id)
WHERE run_id IS NOT NULL AND sample_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_eval_metrics_approach ON evaluation_metrics (approach);
CREATE INDEX IF NOT EXISTS idx_eval_metrics_device ON evaluation_metrics (device);
CREATE INDEX IF NOT EXISTS idx_eval_metrics_ts ON evaluation_metrics ("timestamp" DESC);
CREATE INDEX IF NOT EXISTS idx_eval_metrics_run_id ON evaluation_metrics (run_id, "timestamp" DESC);
CREATE INDEX IF NOT EXISTS idx_evaluation_runs_started ON evaluation_runs (started_at DESC);

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'eval_metrics_run_identity') THEN
    ALTER TABLE evaluation_metrics ADD CONSTRAINT eval_metrics_run_identity
    CHECK (run_id IS NULL OR (sample_id IS NOT NULL AND approach IS NOT NULL AND question IS NOT NULL)) NOT VALID;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'eval_metrics_device_known') THEN
    ALTER TABLE evaluation_metrics ADD CONSTRAINT eval_metrics_device_known
    CHECK (device IS NULL OR device IN ('cpu', 'cuda')) NOT VALID;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'eval_metrics_runtime_known') THEN
    ALTER TABLE evaluation_metrics ADD CONSTRAINT eval_metrics_runtime_known
    CHECK (runtime IS NULL OR runtime IN ('transformers', 'gguf')) NOT VALID;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'eval_metrics_weight_format_known') THEN
    ALTER TABLE evaluation_metrics ADD CONSTRAINT eval_metrics_weight_format_known
    CHECK (weight_format IS NULL OR weight_format IN ('safetensors', 'gguf')) NOT VALID;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'eval_metrics_quality_score_ranged') THEN
    ALTER TABLE evaluation_metrics ADD CONSTRAINT eval_metrics_quality_score_ranged
    CHECK (quality_score IS NULL OR quality_score BETWEEN 0 AND 1) NOT VALID;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'eval_metrics_durations_nonnegative') THEN
    ALTER TABLE evaluation_metrics ADD CONSTRAINT eval_metrics_durations_nonnegative
    CHECK ((generation_time IS NULL OR generation_time >= 0)
      AND (retrieval_time IS NULL OR retrieval_time >= 0)
      AND (time_to_response IS NULL OR time_to_response >= 0)) NOT VALID;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'evaluation_runs_status_known') THEN
    ALTER TABLE evaluation_runs ADD CONSTRAINT evaluation_runs_status_known
    CHECK (status IN ('running', 'completed', 'failed')) NOT VALID;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'evaluation_runs_counts_valid') THEN
    ALTER TABLE evaluation_runs ADD CONSTRAINT evaluation_runs_counts_valid
    CHECK (expected_samples >= 0 AND recorded_samples >= 0) NOT VALID;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'evaluation_runs_devices_known') THEN
    ALTER TABLE evaluation_runs ADD CONSTRAINT evaluation_runs_devices_known
    CHECK ((requested_device IS NULL OR requested_device IN ('cpu', 'cuda'))
      AND (actual_device IS NULL OR actual_device IN ('cpu', 'cuda', 'mixed'))) NOT VALID;
  END IF;
END $$;

-- Grafana's read-only role. Existing volumes were provisioned before this existed
-- and had the datasource connecting as the database owner.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'grafana_ro') THEN
        CREATE ROLE grafana_ro LOGIN PASSWORD 'grafanaro';
    END IF;
END
$$;
GRANT CONNECT ON DATABASE rag_eval TO grafana_ro;
GRANT USAGE ON SCHEMA public TO grafana_ro;
GRANT SELECT ON evaluation_metrics TO grafana_ro;
GRANT SELECT ON evaluation_runs TO grafana_ro;
SQL

# Columns and indexes the current code depends on. Checked by name so a partial
# migration is reported rather than assumed.
REQUIRED_COLUMNS=(run_id sample_id run_started_at runtime weight_format n_gpu_layers rss_mb)
REQUIRED_INDEXES=(idx_eval_metrics_run_id uq_eval_metrics_run_sample)
REQUIRED_CONSTRAINTS=(
  eval_metrics_run_identity
  eval_metrics_device_known
  eval_metrics_runtime_known
  eval_metrics_weight_format_known
  eval_metrics_quality_score_ranged
  eval_metrics_durations_nonnegative
  evaluation_runs_status_known
  evaluation_runs_counts_valid
  evaluation_runs_devices_known
)

report_drift() {
  local drift=0 col idx constraint
  for col in "${REQUIRED_COLUMNS[@]}"; do
    if ! "${PSQL[@]}" -tAc "SELECT 1 FROM information_schema.columns
         WHERE table_name='evaluation_metrics' AND column_name='${col}'" | grep -q 1; then
      echo "  missing column: ${col}"
      drift=1
    fi
  done
  for constraint in "${REQUIRED_CONSTRAINTS[@]}"; do
    if ! "${PSQL[@]}" -tAc "SELECT 1 FROM pg_constraint
         WHERE conname='${constraint}'" | grep -q 1; then
      echo "  missing constraint: ${constraint}"
      drift=1
    fi
  done
  for idx in "${REQUIRED_INDEXES[@]}"; do
    if ! "${PSQL[@]}" -tAc "SELECT 1 FROM pg_indexes
         WHERE tablename='evaluation_metrics' AND indexname='${idx}'" | grep -q 1; then
      echo "  missing index: ${idx}"
      drift=1
    fi
  done
  if "${PSQL[@]}" -tAc "SELECT 1 FROM information_schema.columns
       WHERE table_name='evaluation_metrics' AND column_name='rougel'" | grep -q 1; then
    echo "  stale column present: rougel"
    drift=1
  fi
  return $drift
}

# A table that does not exist yet is not drift — init-db.sql builds it on a fresh
# volume, and this script has nothing to migrate.
if ! "${PSQL[@]}" -tAc "SELECT to_regclass('public.evaluation_metrics')" | grep -q evaluation_metrics; then
  echo "evaluation_metrics does not exist yet; init-db.sql will create it on first start."
  exit 0
fi

if [[ "$MODE" == check ]]; then
  echo "==> Checking evaluation_metrics against the current schema"
  if report_drift; then
    echo "schema is up to date"
    exit 0
  fi
  echo "" >&2
  echo "Run scripts/migrate_db.sh to apply." >&2
  exit 1
fi

echo "==> Migrating evaluation_metrics"
before="$("${PSQL[@]}" -tAc 'SELECT count(*) FROM evaluation_metrics')"

printf '%s\n' "$MIGRATION" | "${PSQL[@]}" -f - >/dev/null

after="$("${PSQL[@]}" -tAc 'SELECT count(*) FROM evaluation_metrics')"
orphans="$("${PSQL[@]}" -tAc 'SELECT count(*) FROM evaluation_metrics WHERE run_id IS NULL')"

echo "    rows before: ${before}  after: ${after}"
if [[ "$orphans" != "0" ]]; then
  echo ""
  echo "    NOTE: ${orphans} row(s) predate the run_id column and have run_id NULL."
  echo "          Every dashboard filters on 'run_id IS NOT NULL', so these are"
  echo "          invisible there. They are left alone on purpose: inventing a run"
  echo "          id for them would attribute them to a run that did not produce"
  echo "          them. Delete them when you no longer want them:"
  echo "            DELETE FROM evaluation_metrics WHERE run_id IS NULL;"
fi

if report_drift; then
  echo "==> Schema is up to date"
else
  echo "ERROR: migration ran but drift remains (see above)" >&2
  exit 1
fi
