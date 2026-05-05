CREATE TABLE IF NOT EXISTS jobs (
  job_id VARCHAR PRIMARY KEY,
  status VARCHAR NOT NULL,
  assigned_worker VARCHAR,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  retry_count INT NOT NULL DEFAULT 0,
  result JSONB,
  idempotency_key VARCHAR UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
