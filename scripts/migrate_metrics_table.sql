-- Apply if you already have an older evaluation_metrics table (init-db only runs on first volume create).
-- Usage: docker compose exec postgres psql -U raguser -d rag_eval -f /dev/stdin < scripts/migrate_metrics_table.sql

ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS device VARCHAR(16);
ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS cuda_available BOOLEAN;
ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS model_name TEXT;
ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS rouge1 FLOAT;
ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS rouge2 FLOAT;
ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS "rougeL" FLOAT;
ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS bert_score FLOAT;
ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS retrieval_hit_at_k FLOAT;
ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS faithfulness FLOAT;
ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS answer_relevancy FLOAT;
ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS judge_groundedness FLOAT;
ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS quality_score FLOAT;
ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS generation_time FLOAT;
ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS retrieval_time FLOAT;
ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS time_to_response FLOAT;
ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS speed_chars_per_sec FLOAT;
ALTER TABLE evaluation_metrics ADD COLUMN IF NOT EXISTS cuda_used FLOAT;

CREATE INDEX IF NOT EXISTS idx_eval_metrics_approach ON evaluation_metrics (approach);
CREATE INDEX IF NOT EXISTS idx_eval_metrics_device ON evaluation_metrics (device);
CREATE INDEX IF NOT EXISTS idx_eval_metrics_ts ON evaluation_metrics (timestamp DESC);
