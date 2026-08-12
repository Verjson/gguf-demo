-- Runs once when the Postgres container is first created.
-- Enables pgvector for embedding storage and uuid generation for metrics rows.

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS evaluation_metrics (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
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
    cuda_used FLOAT
);

CREATE INDEX IF NOT EXISTS idx_eval_metrics_approach ON evaluation_metrics (approach);
CREATE INDEX IF NOT EXISTS idx_eval_metrics_device ON evaluation_metrics (device);
CREATE INDEX IF NOT EXISTS idx_eval_metrics_ts ON evaluation_metrics (timestamp DESC);
