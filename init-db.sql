-- Runs once when the Postgres container is first created.
-- Enables pgvector for embedding storage and uuid generation for metrics rows.

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

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
    -- Lowercase alias of "rougeL" for queries that do not quote the camelCase name.
    rougel FLOAT,
    prompt_chars FLOAT,
    response_chars FLOAT,
    prompt_tokens FLOAT,
    completion_tokens FLOAT,
    tokens_per_sec FLOAT,
    context_chars FLOAT,
    n_chunks_retrieved FLOAT,
    cpu_threads FLOAT,
    cpu_logical FLOAT,
    peak_rss_mb FLOAT,
    peak_gpu_mem_mb FLOAT,
    runtime VARCHAR(32),
    weight_format VARCHAR(32)
);

CREATE INDEX IF NOT EXISTS idx_eval_metrics_approach ON evaluation_metrics (approach);
CREATE INDEX IF NOT EXISTS idx_eval_metrics_device ON evaluation_metrics (device);
CREATE INDEX IF NOT EXISTS idx_eval_metrics_ts ON evaluation_metrics (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_eval_metrics_run_id ON evaluation_metrics (run_id, timestamp DESC);
