-- Sprint 22 - Ingestão 2.0 (metadados em SQLite)
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS ingestion_configs (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    enabled INTEGER NOT NULL,
    mode TEXT NOT NULL,
    interval_minutes INTEGER NOT NULL,
    max_attempts INTEGER NOT NULL,
    timeout_seconds INTEGER NOT NULL,
    last_run_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_by TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS ingestion_configs_source_idx ON ingestion_configs(source_id);

CREATE TABLE IF NOT EXISTS ingestion_runs (
    id TEXT PRIMARY KEY,
    config_id TEXT NOT NULL REFERENCES ingestion_configs(id) ON DELETE CASCADE,
    source_id TEXT NOT NULL,
    trigger TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    items_processed INTEGER NOT NULL DEFAULT 0,
    error_code TEXT,
    error_message TEXT,
    payload_ref TEXT,
    meta TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS ingestion_runs_source_idx ON ingestion_runs(source_id);
CREATE INDEX IF NOT EXISTS ingestion_runs_config_idx ON ingestion_runs(config_id);
CREATE INDEX IF NOT EXISTS ingestion_runs_started_at_idx ON ingestion_runs(started_at);
