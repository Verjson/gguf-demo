-- Runs once when the Postgres container is first created.
-- Enables pgvector for embedding storage and uuid generation for metrics rows.

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

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
    PRIMARY KEY (run_id, approach),
    CONSTRAINT evaluation_runs_status_known
        CHECK (status IN ('running', 'completed', 'failed')),
    CONSTRAINT evaluation_runs_counts_valid
        CHECK (expected_samples >= 0 AND recorded_samples >= 0),
    CONSTRAINT evaluation_runs_devices_known
        CHECK (
            (requested_device IS NULL OR requested_device IN ('cpu', 'cuda'))
            AND (actual_device IS NULL OR actual_device IN ('cpu', 'cuda', 'mixed'))
        )
);

-- This table is defined twice: here, for a fresh volume, and as
-- _ENSURE_SCHEMA_STATEMENTS in src/metrics_store.py, which runs on every connect and
-- migrates existing volumes. They converge on an existing volume but a fresh one shows
-- only what is written here until the first eval row, so a column added to one and not
-- the other makes two stacks disagree. tests/test_schema_parity.py fails when they do
-- — add every new column in both places, in the same commit.
CREATE TABLE IF NOT EXISTS evaluation_metrics (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    -- Which pipeline run wrote this row: the UTC start stamp plus device, e.g.
    -- 2026-08-14_181632_cpu, matching results/runs/<run_id>/. Nullable with no
    -- default — rows predating this column belong to no run and must not be
    -- attributed to one.
    run_id TEXT,
    sample_id TEXT,
    run_started_at TIMESTAMPTZ,
    approach VARCHAR(50),
    question TEXT,
    response TEXT,
    device VARCHAR(16),
    cuda_available BOOLEAN,
    model_name TEXT,
    rouge1 FLOAT,
    rouge2 FLOAT,
    "rougeL" FLOAT,
    bert_score FLOAT,
    domain_relevance FLOAT,
    context_utilization FLOAT,
    coherence FLOAT,
    factual_density FLOAT,
    technical_accuracy FLOAT,
    retrieval_hit_at_k FLOAT,
    faithfulness FLOAT,
    answer_relevancy FLOAT,
    judge_groundedness FLOAT,
    quality_score FLOAT,
    generation_time FLOAT,
    retrieval_time FLOAT,
    time_to_response FLOAT,
    speed_chars_per_sec FLOAT,
    cuda_used FLOAT,
    prompt_chars FLOAT,
    response_chars FLOAT,
    prompt_tokens FLOAT,
    completion_tokens FLOAT,
    tokens_per_sec FLOAT,
    context_chars FLOAT,
    n_chunks_retrieved FLOAT,
    cpu_threads FLOAT,
    cpu_logical FLOAT,
    -- Live RSS at the time the answer finished; unlike peak_rss_mb this can
    -- fall, so a per-question series and its average both mean something.
    rss_mb FLOAT,
    peak_rss_mb FLOAT,
    peak_gpu_mem_mb FLOAT,
    runtime VARCHAR(32),
    weight_format VARCHAR(32),
    -- How many transformer layers the engine actually offloaded to the GPU.
    -- 0 means it ran on the CPU whatever the device column says, which is not
    -- hypothetical: Dockerfile.app installs the CPU llama.cpp wheel on CUDA 13
    -- hosts, so a GGUF leg of a "cuda" run offloads nothing. Without this column
    -- the runtime dashboard compared GPU-Transformers against CPU-llama.cpp and
    -- called the difference an engine difference. -1 means "all layers".
    n_gpu_layers FLOAT,

    -- Closed vocabularies, so a typo fails the insert instead of quietly creating
    -- a new series that then shows up as an extra bar on every dashboard.
    CONSTRAINT eval_metrics_device_known
        CHECK (device IS NULL OR device IN ('cpu', 'cuda')),
    CONSTRAINT eval_metrics_runtime_known
        CHECK (runtime IS NULL OR runtime IN ('transformers', 'gguf')),
    CONSTRAINT eval_metrics_weight_format_known
        CHECK (weight_format IS NULL OR weight_format IN ('safetensors', 'gguf')),
    -- Scores are 0-1 by construction in src/evaluator.py; a value outside that
    -- range means a scorer changed its contract without the blend being updated.
    CONSTRAINT eval_metrics_quality_score_ranged
        CHECK (quality_score IS NULL OR quality_score BETWEEN 0 AND 1),
    -- Durations cannot be negative. A negative one means a clock went backwards
    -- mid-measurement, which should be loud rather than averaged in.
    CONSTRAINT eval_metrics_durations_nonnegative
        CHECK (
            (generation_time IS NULL OR generation_time >= 0)
            AND (retrieval_time IS NULL OR retrieval_time >= 0)
            AND (time_to_response IS NULL OR time_to_response >= 0)
        ),
    CONSTRAINT eval_metrics_run_identity
        CHECK (
            run_id IS NULL
            OR (sample_id IS NOT NULL AND approach IS NOT NULL AND question IS NOT NULL)
        )
);

CREATE INDEX IF NOT EXISTS idx_eval_metrics_approach ON evaluation_metrics (approach);
CREATE INDEX IF NOT EXISTS idx_eval_metrics_device ON evaluation_metrics (device);
CREATE INDEX IF NOT EXISTS idx_eval_metrics_ts ON evaluation_metrics (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_eval_metrics_run_id ON evaluation_metrics (run_id, timestamp DESC);

-- One row per (run, approach, sample). Question text is not an identity: evaluation
-- sets can legitimately ask the same question against different expectations.
--
-- Re-running a stage used to append a second row for the same cell. Dashboard 03
-- defended against that with DISTINCT ON; dashboards 02 and 04 used plain AVG() and
-- COUNT(*), so after one re-run the same run reported n=15 on one dashboard and n=30
-- on another, with the averages pulled toward whichever attempt was repeated. The
-- insert now upserts against this index, so a re-run replaces.
--
-- Partial, because rows written before run_id existed all have NULL there and would
-- otherwise collide with each other.
CREATE UNIQUE INDEX IF NOT EXISTS uq_eval_metrics_run_sample
ON evaluation_metrics (run_id, approach, sample_id)
WHERE run_id IS NOT NULL AND sample_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_evaluation_runs_started
ON evaluation_runs (started_at DESC);

-- Least privilege for Grafana.
--
-- The datasource executes raw SQL from every panel. Connecting it as raguser — the
-- owner of this database — meant the query editor could DROP TABLE. This role can
-- read the one table the dashboards use and nothing else.
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
