"""
Persist evaluation rows to Postgres `evaluation_metrics` for Grafana SQL panels.

Also applies additive schema migrations so older volumes pick up new columns
without requiring a manual psql step on every upgrade.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import psycopg2

from src.run_id import run_started_at

logger = logging.getLogger(__name__)

def run_started_from_id(run_id: str) -> str | None:
    """
    The UTC start time encoded in a run id, as an ISO string, or None.

    Lets a row carry when its run began even when only RUN_ID reaches the container,
    so the dashboards' run header has a real clock time rather than the timestamp of
    whichever row happened to be written first. src.run_id owns the shape.
    """
    return run_started_at(run_id)


# Columns we know how to write; unknown metric keys are ignored
METRIC_COLUMNS = (
    "rouge1",
    "rouge2",
    "rougeL",
    "bert_score",
    "domain_relevance",
    "context_utilization",
    "coherence",
    "factual_density",
    "technical_accuracy",
    "retrieval_hit_at_k",
    "faithfulness",
    "answer_relevancy",
    "judge_groundedness",
    "quality_score",
    "generation_time",
    "retrieval_time",
    "time_to_response",
    "speed_chars_per_sec",
    "cuda_used",
    "prompt_chars",
    "response_chars",
    "prompt_tokens",
    "completion_tokens",
    "tokens_per_sec",
    "context_chars",
    "n_chunks_retrieved",
    "cpu_threads",
    "cpu_logical",
    "rss_mb",
    "peak_rss_mb",
    "peak_gpu_mem_mb",
    # 0 = the engine offloaded nothing and ran on the CPU, whatever device says.
    "n_gpu_layers",
)

# Safe to re-run: this is the only migration path, applied on every connect.
# It must stay in step with init-db.sql, which builds a fresh volume —
# tests/test_schema_parity.py fails when the two drift.
_ENSURE_SCHEMA_STATEMENTS = (
    'CREATE EXTENSION IF NOT EXISTS "uuid-ossp"',
    """
    CREATE TABLE IF NOT EXISTS evaluation_runs (
        run_id TEXT NOT NULL,
        approach VARCHAR(50) NOT NULL,
        started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        completed_at TIMESTAMPTZ,
        status VARCHAR(16) NOT NULL DEFAULT 'running',
        expected_samples INTEGER NOT NULL,
        recorded_samples INTEGER NOT NULL DEFAULT 0,
        requested_device VARCHAR(16),
        actual_device VARCHAR(16),
        runtime VARCHAR(32),
        weight_format VARCHAR(32),
        model_name TEXT,
        mlflow_run_id TEXT,
        error TEXT,
        PRIMARY KEY (run_id, approach)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS evaluation_metrics (
        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
        timestamp TIMESTAMPTZ DEFAULT NOW(),
        approach VARCHAR(50),
        question TEXT,
        response TEXT,
        device VARCHAR(16),
        cuda_available BOOLEAN,
        model_name TEXT
    )
    """,
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS device VARCHAR(16)",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS cuda_available BOOLEAN",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS model_name TEXT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS rouge1 FLOAT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS rouge2 FLOAT",
    'ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS "rougeL" FLOAT',
    # `rougel` was added as a lowercase alias "for queries that do not quote the
    # camelCase name" — but METRIC_COLUMNS only ever wrote "rougeL", so the column
    # was permanently NULL while looking like a real one. That is worse than not
    # having it: Postgres folds an unquoted rougeL to this name, so the query it
    # existed to help returned silence instead of an error. All four dashboards
    # quote correctly; nothing reads it.
    "ALTER TABLE evaluation_metrics DROP COLUMN IF EXISTS rougel",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS bert_score FLOAT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS domain_relevance FLOAT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS context_utilization FLOAT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS coherence FLOAT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS factual_density FLOAT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS technical_accuracy FLOAT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS retrieval_hit_at_k FLOAT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS faithfulness FLOAT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS answer_relevancy FLOAT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS judge_groundedness FLOAT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS quality_score FLOAT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS generation_time FLOAT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS retrieval_time FLOAT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS time_to_response FLOAT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS speed_chars_per_sec FLOAT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS cuda_used FLOAT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS prompt_chars FLOAT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS response_chars FLOAT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS prompt_tokens FLOAT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS completion_tokens FLOAT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS tokens_per_sec FLOAT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS context_chars FLOAT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS n_chunks_retrieved FLOAT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS cpu_threads FLOAT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS cpu_logical FLOAT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS peak_rss_mb FLOAT",
    # Live RSS, which unlike peak_rss_mb can go down — the per-question figure.
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS rss_mb FLOAT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS peak_gpu_mem_mb FLOAT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS runtime VARCHAR(32)",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS weight_format VARCHAR(32)",
    # Which pipeline run wrote the row. Nullable with no default on purpose: rows
    # written before this column existed genuinely have no run, and inventing one
    # would make them look like they belong to whichever run is being viewed.
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS run_id TEXT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS sample_id TEXT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS run_started_at TIMESTAMPTZ",
    # Layers actually offloaded to the GPU; 0 means the engine ran on the CPU no
    # matter what `device` says. See init-db.sql for why that distinction is load-bearing.
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS n_gpu_layers FLOAT",
    "UPDATE evaluation_metrics SET sample_id = id::text "
    "WHERE run_id IS NOT NULL AND sample_id IS NULL",
    """
    DO $$ BEGIN
      IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'eval_metrics_run_identity') THEN
        ALTER TABLE evaluation_metrics ADD CONSTRAINT eval_metrics_run_identity
        CHECK (run_id IS NULL OR (sample_id IS NOT NULL AND approach IS NOT NULL AND question IS NOT NULL))
        NOT VALID;
      END IF;
    END $$
    """,
    """
    DO $$ BEGIN
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
    END $$
    """,
    """
    DO $$ BEGIN
      IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'eval_metrics_quality_score_ranged') THEN
        ALTER TABLE evaluation_metrics ADD CONSTRAINT eval_metrics_quality_score_ranged
        CHECK (quality_score IS NULL OR quality_score BETWEEN 0 AND 1) NOT VALID;
      END IF;
      IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'eval_metrics_durations_nonnegative') THEN
        ALTER TABLE evaluation_metrics ADD CONSTRAINT eval_metrics_durations_nonnegative
        CHECK (
          (generation_time IS NULL OR generation_time >= 0)
          AND (retrieval_time IS NULL OR retrieval_time >= 0)
          AND (time_to_response IS NULL OR time_to_response >= 0)
        ) NOT VALID;
      END IF;
    END $$
    """,
    """
    DO $$ BEGIN
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
        CHECK (
          (requested_device IS NULL OR requested_device IN ('cpu', 'cuda'))
          AND (actual_device IS NULL OR actual_device IN ('cpu', 'cuda', 'mixed'))
        ) NOT VALID;
      END IF;
    END $$
    """,
    "CREATE INDEX IF NOT EXISTS idx_eval_metrics_approach ON evaluation_metrics (approach)",
    "CREATE INDEX IF NOT EXISTS idx_eval_metrics_device ON evaluation_metrics (device)",
    "CREATE INDEX IF NOT EXISTS idx_eval_metrics_ts ON evaluation_metrics (timestamp DESC)",
    "CREATE INDEX IF NOT EXISTS idx_eval_metrics_run_id ON evaluation_metrics (run_id, timestamp DESC)",
    # Target of the ON CONFLICT in insert(): a re-run of a stage replaces its rows
    # instead of appending a second set. Partial so pre-run_id rows do not collide.
    "DROP INDEX IF EXISTS uq_eval_metrics_run_cell",
    "CREATE UNIQUE INDEX IF NOT EXISTS uq_eval_metrics_run_sample "
    "ON evaluation_metrics (run_id, approach, sample_id) "
    "WHERE run_id IS NOT NULL AND sample_id IS NOT NULL",
    "CREATE INDEX IF NOT EXISTS idx_evaluation_runs_started "
    "ON evaluation_runs (started_at DESC)",
)


class MetricsStore:
    """
    Insert evaluation results into the evaluation_metrics table.

    Write failures are counted, not just logged. They used to be swallowed into a
    ``logger.warning`` with nothing propagating, so a pipeline whose database was
    unreachable for its entire duration finished green, exported a header-only CSV,
    recorded ``postgres_rows: 0`` and printed DONE. ``failed_writes`` lets a caller
    assert at the end of a stage that what it thinks it measured was actually stored —
    see ``raise_if_writes_failed``.
    """

    _schema_ready = False

    #: Rows this process failed to persist, across every instance. Class-scoped
    #: because eval scripts construct a store per tracker but are one run.
    failed_writes = 0
    successful_writes = 0

    def __init__(self) -> None:
        self._conn_kwargs = {
            "host": os.getenv("POSTGRES_HOST", "postgres"),
            "database": os.getenv("POSTGRES_DB", "rag_eval"),
            "user": os.getenv("POSTGRES_USER", "raguser"),
            "password": os.getenv("POSTGRES_PASSWORD", "ragpass"),
        }
        self.ensure_schema()

    def ensure_schema(self) -> None:
        """Create table / add missing columns (idempotent)."""
        if MetricsStore._schema_ready:
            return
        try:
            with psycopg2.connect(**self._conn_kwargs) as conn:
                with conn.cursor() as cur:
                    for stmt in _ENSURE_SCHEMA_STATEMENTS:
                        cur.execute(stmt)
                conn.commit()
            MetricsStore._schema_ready = True
            logger.info("Postgres evaluation_metrics schema is up to date")
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not ensure evaluation_metrics schema: %s", exc)

    def insert(
        self,
        approach: str,
        question: str,
        response: str,
        metrics: dict[str, float],
        device: str = "cpu",
        cuda_available: bool = False,
        model_name: str | None = None,
        runtime: str | None = None,
        weight_format: str | None = None,
        run_id: str | None = None,
        run_started_at: str | None = None,
        sample_id: str | None = None,
    ) -> None:
        cols = ["approach", "question", "response", "device", "cuda_available", "model_name"]
        vals: list[Any] = [
            approach,
            question,
            response,
            device,
            cuda_available,
            model_name,
        ]
        if runtime:
            cols.append("runtime")
            vals.append(runtime)
        if weight_format:
            cols.append("weight_format")
            vals.append(weight_format)

        # From the environment by default so every eval script stamps its rows without
        # a signature change at each call site — run_pipeline.sh exports RUN_ID per
        # device. A step run by hand has no RUN_ID and writes NULL, which is honest:
        # it belongs to no pipeline run.
        run_id = run_id or os.getenv("RUN_ID") or None
        if run_id:
            cols.append("run_id")
            vals.append(run_id)
            if sample_id is not None:
                cols.append("sample_id")
                vals.append(sample_id)
            started = run_started_at or os.getenv("RUN_STARTED_AT") or run_started_from_id(run_id)
            if started:
                cols.append("run_started_at")
                vals.append(started)

        for col in METRIC_COLUMNS:
            if col in metrics:
                # Quote camelCase columns for Postgres
                cols.append(f'"{col}"' if col == "rougeL" else col)
                vals.append(float(metrics[col]))

        placeholders = ", ".join(["%s"] * len(cols))
        col_sql = ", ".join(cols)
        sql = f"INSERT INTO evaluation_metrics ({col_sql}) VALUES ({placeholders})"

        # A re-run of a stage replaces its own rows rather than appending a second
        # set. Without this, dashboards that dedupe (03) and dashboards that do not
        # (02, 04) disagreed about how many answers a run contained, and the averages
        # on the latter were weighted toward whichever attempt had been repeated.
        #
        # Only when the row carries a run_id: the unique index is partial, so rows
        # with NULL run_id have no conflict target and must plain-insert.
        if run_id:
            updates = ", ".join(
                f"{col} = EXCLUDED.{col}" for col in cols
                if col not in ("run_id", "approach", "question")
            )
            sql += (
                " ON CONFLICT (run_id, approach, sample_id) "
                "WHERE run_id IS NOT NULL AND sample_id IS NOT NULL "
                f"DO UPDATE SET {updates}"
            ) if sample_id is not None else ""

        try:
            self._execute(sql, vals)
            MetricsStore.successful_writes += 1
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to persist metrics to Postgres: %s", exc)
            # Retry once after schema repair (e.g. missing column on old volume)
            try:
                MetricsStore._schema_ready = False
                self.ensure_schema()
                self._execute(sql, vals)
                MetricsStore.successful_writes += 1
            except Exception as retry_exc:  # noqa: BLE001
                MetricsStore.failed_writes += 1
                logger.error(
                    "Metric row LOST for approach=%s question=%r — retry after schema "
                    "repair also failed: %s",
                    approach,
                    (question or "")[:60],
                    retry_exc,
                )

    def start_run(
        self,
        *,
        run_id: str,
        approach: str,
        expected_samples: int,
        requested_device: str,
        runtime: str | None,
        weight_format: str | None,
        model_name: str | None,
        mlflow_run_id: str | None,
    ) -> None:
        self._execute(
            """
            INSERT INTO evaluation_runs (
                run_id, approach, expected_samples, requested_device, runtime,
                weight_format, model_name, mlflow_run_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (run_id, approach) DO UPDATE SET
                started_at = NOW(), completed_at = NULL, status = 'running',
                expected_samples = EXCLUDED.expected_samples, recorded_samples = 0,
                requested_device = EXCLUDED.requested_device, actual_device = NULL,
                runtime = EXCLUDED.runtime, weight_format = EXCLUDED.weight_format,
                model_name = EXCLUDED.model_name, mlflow_run_id = EXCLUDED.mlflow_run_id,
                error = NULL
            """,
            [
                run_id,
                approach,
                expected_samples,
                requested_device,
                runtime,
                weight_format,
                model_name,
                mlflow_run_id,
            ],
        )

    def finish_run(
        self,
        *,
        run_id: str,
        approach: str,
        status: str,
        recorded_samples: int,
        actual_device: str | None,
        error: str | None = None,
    ) -> None:
        self._execute(
            """
            UPDATE evaluation_runs
            SET completed_at = NOW(), status = %s, recorded_samples = %s,
                actual_device = %s, error = %s
            WHERE run_id = %s AND approach = %s
            """,
            [status, recorded_samples, actual_device, error, run_id, approach],
        )

    def _execute(self, sql: str, vals: list[Any]) -> None:
        """
        Run one statement and close the connection.

        `with psycopg2.connect(...)` is a *transaction* context manager: it commits or
        rolls back, and leaves the connection open for refcounting to collect later.
        Closing it explicitly is what the `with` block reads as if it does, and it
        stops a stage from depending on GC timing for its connection budget.
        """
        conn = psycopg2.connect(**self._conn_kwargs)
        try:
            with conn, conn.cursor() as cur:
                cur.execute(sql, vals)
        finally:
            conn.close()

    @classmethod
    def raise_if_writes_failed(cls, context: str) -> None:
        """
        Fail the step when any row did not reach Postgres.

        Called at the end of a stage. A run that silently persisted nothing is the
        failure mode this whole class of check exists for: the dashboards read from
        Postgres, so losing the write loses the result even though the answers were
        generated and the JSON was written.
        """
        if cls.failed_writes:
            raise RuntimeError(
                f"{cls.failed_writes} metric row(s) were not persisted to Postgres "
                f"({context}); {cls.successful_writes} succeeded. The dashboards read "
                "from this table, so these answers would be invisible. Check that the "
                "postgres service is up and that scripts/migrate_db.sh has run."
            )
