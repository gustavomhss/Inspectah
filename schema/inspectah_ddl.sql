-- Inspectah canonical DDL (Sprint 3 — Gate T1 baseline)
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS sources (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  source_type TEXT NOT NULL,
  config TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active',
  created_at TEXT NOT NULL DEFAULT (DATETIME('now')),
  updated_at TEXT NOT NULL DEFAULT (DATETIME('now'))
);

CREATE TABLE IF NOT EXISTS source_runs (
  id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  status TEXT NOT NULL,
  error_message TEXT,
  UNIQUE(source_id, started_at),
  FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS observations (
  id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL,
  run_id TEXT,
  canonical_key TEXT NOT NULL,
  observed_at TEXT NOT NULL,
  payload_hash TEXT NOT NULL,
  payload_path TEXT NOT NULL,
  payload_mime TEXT,
  created_at TEXT NOT NULL DEFAULT (DATETIME('now')),
  UNIQUE(source_id, canonical_key, observed_at),
  FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE CASCADE,
  FOREIGN KEY (run_id) REFERENCES source_runs(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_id TEXT NOT NULL,
  canonical_url TEXT NOT NULL,
  canonical_key TEXT,
  content_hash TEXT NOT NULL,
  collected_at TEXT NOT NULL,
  manifest_path TEXT NOT NULL,
  latest_observation_id TEXT,
  confidence_score REAL NOT NULL DEFAULT 0,
  confidence_profile_id TEXT,
  created_at TEXT NOT NULL DEFAULT (DATETIME('now')),
  updated_at TEXT NOT NULL DEFAULT (DATETIME('now')),
  UNIQUE(source_id, content_hash),
  FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE CASCADE,
  FOREIGN KEY (latest_observation_id) REFERENCES observations(id)
);

CREATE TABLE IF NOT EXISTS item_versions (
  id TEXT PRIMARY KEY,
  item_id INTEGER NOT NULL,
  observation_id TEXT NOT NULL,
  source_run_id TEXT,
  collected_at TEXT NOT NULL,
  manifest_path TEXT NOT NULL,
  snapshot_path TEXT,
  version INTEGER NOT NULL,
  diff_summary TEXT,
  created_at TEXT NOT NULL DEFAULT (DATETIME('now')),
  FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
  FOREIGN KEY (observation_id) REFERENCES observations(id) ON DELETE CASCADE,
  FOREIGN KEY (source_run_id) REFERENCES source_runs(id) ON DELETE SET NULL,
  UNIQUE(item_id, version)
);

CREATE TABLE IF NOT EXISTS item_kv (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  item_id INTEGER NOT NULL,
  field_name TEXT NOT NULL,
  field_type TEXT NOT NULL,
  value_string TEXT,
  value_numeric REAL,
  value_timestamp TEXT,
  value_boolean INTEGER,
  FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_item_kv_field_name ON item_kv (field_name);
CREATE INDEX IF NOT EXISTS idx_item_kv_item ON item_kv (item_id);

CREATE TABLE IF NOT EXISTS field_definitions (
  id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL,
  version INTEGER NOT NULL,
  status TEXT NOT NULL,
  definition TEXT NOT NULL,
  created_by TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (DATETIME('now')),
  UNIQUE(source_id, version),
  FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS evidence_records (
  id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL,
  item_id INTEGER,
  item_version_id TEXT,
  evidence_type TEXT NOT NULL,
  collected_at TEXT NOT NULL,
  ingested_at TEXT NOT NULL,
  storage_key TEXT NOT NULL,
  hash_alg TEXT NOT NULL,
  hash_value TEXT NOT NULL,
  lgpd_tags TEXT NOT NULL,
  size_bytes INTEGER NOT NULL,
  checksum_status TEXT NOT NULL,
  FOREIGN KEY (source_id) REFERENCES sources(id),
  FOREIGN KEY (item_id) REFERENCES items(id),
  FOREIGN KEY (item_version_id) REFERENCES item_versions(id)
);
