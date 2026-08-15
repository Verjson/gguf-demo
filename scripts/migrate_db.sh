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

ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS run_id TEXT;
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

-- One row per (run, approach, question). Re-running a stage used to append a second
-- row for the same cell; dashboard 03 defended with DISTINCT ON while 02 and 04 used
-- plain AVG(), so after one re-run the same run reported n=15 on one dashboard and
-- n=30 on another. Historic rows have no run_id and are excluded from the constraint
-- rather than deleted.
CREATE UNIQUE INDEX IF NOT EXISTS uq_eval_metrics_run_cell
    ON evaluation_metrics (run_id, approach, question)
    WHERE run_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_eval_metrics_approach ON evaluation_metrics (approach);
CREATE INDEX IF NOT EXISTS idx_eval_metrics_device ON evaluation_metrics (device);
CREATE INDEX IF NOT EXISTS idx_eval_metrics_ts ON evaluation_metrics ("timestamp" DESC);
CREATE INDEX IF NOT EXISTS idx_eval_metrics_run_id ON evaluation_metrics (run_id, "timestamp" DESC);

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
SQL

# Columns and indexes the current code depends on. Checked by name so a partial
# migration is reported rather than assumed.
REQUIRED_COLUMNS=(run_id run_started_at runtime weight_format n_gpu_layers rss_mb)
REQUIRED_INDEXES=(idx_eval_metrics_run_id uq_eval_metrics_run_cell)

report_drift() {
  local drift=0 col idx
  for col in "${REQUIRED_COLUMNS[@]}"; do
    if ! "${PSQL[@]}" -tAc "SELECT 1 FROM information_schema.columns
         WHERE table_name='evaluation_metrics' AND column_name='${col}'" | grep -q 1; then
      echo "  missing column: ${col}"
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

# A duplicate cell would make the unique index fail to build, which should be a clear
# message rather than a psql constraint error mid-script.
duplicates="$("${PSQL[@]}" -tAc "
  SELECT count(*) FROM (
    SELECT run_id, approach, question FROM evaluation_metrics
    WHERE run_id IS NOT NULL
    GROUP BY 1,2,3 HAVING count(*) > 1
  ) d")"
if [[ "$duplicates" != "0" ]]; then
  echo "ERROR: ${duplicates} (run_id, approach, question) cell(s) already have more than" >&2
  echo "       one row, so the unique index cannot be created. These are re-runs that" >&2
  echo "       were appended rather than replaced. Keep the newest of each with:" >&2
  echo "" >&2
  echo "         DELETE FROM evaluation_metrics a USING evaluation_metrics b" >&2
  echo "          WHERE a.run_id = b.run_id AND a.approach = b.approach" >&2
  echo "            AND a.question = b.question AND a.timestamp < b.timestamp;" >&2
  echo "" >&2
  echo "       Review before running it — it deletes rows." >&2
  exit 1
fi

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
