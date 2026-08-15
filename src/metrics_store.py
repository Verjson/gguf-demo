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
    "peak_rss_mb",
    "peak_gpu_mem_mb",
)

# Safe to re-run: this is the only migration path, applied on every connect.
# It must stay in step with init-db.sql, which builds a fresh volume —
# tests/test_schema_parity.py fails when the two drift.
_ENSURE_SCHEMA_STATEMENTS = (
    'CREATE EXTENSION IF NOT EXISTS "uuid-ossp"',
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
    # Unquoted rougeL from older init-db — also ensure lowercase alias column exists for queries
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS rougel FLOAT",
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
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS peak_gpu_mem_mb FLOAT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS runtime VARCHAR(32)",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS weight_format VARCHAR(32)",
    # Which pipeline run wrote the row. Nullable with no default on purpose: rows
    # written before this column existed genuinely have no run, and inventing one
    # would make them look like they belong to whichever run is being viewed.
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS run_id TEXT",
    "ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS run_started_at TIMESTAMPTZ",
    "CREATE INDEX IF NOT EXISTS idx_eval_metrics_approach ON evaluation_metrics (approach)",
    "CREATE INDEX IF NOT EXISTS idx_eval_metrics_device ON evaluation_metrics (device)",
    "CREATE INDEX IF NOT EXISTS idx_eval_metrics_ts ON evaluation_metrics (timestamp DESC)",
    "CREATE INDEX IF NOT EXISTS idx_eval_metrics_run_id ON evaluation_metrics (run_id, timestamp DESC)",
)


class MetricsStore:
    """Insert evaluation results into the evaluation_metrics table."""

    _schema_ready = False

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

        try:
            with psycopg2.connect(**self._conn_kwargs) as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, vals)
                conn.commit()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to persist metrics to Postgres: %s", exc)
            # Retry once after schema repair (e.g. missing column on old volume)
            try:
                MetricsStore._schema_ready = False
                self.ensure_schema()
                with psycopg2.connect(**self._conn_kwargs) as conn:
                    with conn.cursor() as cur:
                        cur.execute(sql, vals)
                    conn.commit()
            except Exception as retry_exc:  # noqa: BLE001
                logger.warning("Retry insert also failed: %s", retry_exc)
