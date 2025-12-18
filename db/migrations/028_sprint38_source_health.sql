-- ============================================================================
-- S38: Source Health Tracking Migration
-- Task: S38-DB-001
-- Version: source_health_v1
-- ============================================================================

-- Source health tracking table
CREATE TABLE IF NOT EXISTS source_health (
    id SERIAL PRIMARY KEY,
    source_id VARCHAR(100) NOT NULL,
    source_type VARCHAR(32) NOT NULL DEFAULT 'unknown',  -- official, scraper, rss, api
    status VARCHAR(20) NOT NULL DEFAULT 'unknown',  -- healthy, degraded, unhealthy, unknown
    last_check_at TIMESTAMPTZ DEFAULT NOW(),
    last_success_at TIMESTAMPTZ,
    consecutive_failures INTEGER DEFAULT 0,
    avg_latency_ms INTEGER DEFAULT 0,
    success_rate FLOAT DEFAULT 1.0,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_source_health UNIQUE (source_id)
);

CREATE INDEX IF NOT EXISTS idx_source_health_status ON source_health(status);
CREATE INDEX IF NOT EXISTS idx_source_health_type ON source_health(source_type);
CREATE INDEX IF NOT EXISTS idx_source_health_last_check ON source_health(last_check_at DESC);

-- Source health history for metrics
CREATE TABLE IF NOT EXISTS source_health_history (
    id SERIAL PRIMARY KEY,
    source_id VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    latency_ms INTEGER,
    error_message TEXT,
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_source_health_history_source ON source_health_history(source_id);
CREATE INDEX IF NOT EXISTS idx_source_health_history_recorded ON source_health_history(recorded_at DESC);

-- Rate limiting tracking
CREATE TABLE IF NOT EXISTS rate_limit_state (
    id SERIAL PRIMARY KEY,
    source_id VARCHAR(100) NOT NULL,
    window_start TIMESTAMPTZ NOT NULL,
    request_count INTEGER DEFAULT 0,
    max_requests INTEGER DEFAULT 10,
    window_seconds INTEGER DEFAULT 60,
    CONSTRAINT uq_rate_limit UNIQUE (source_id, window_start)
);

CREATE INDEX IF NOT EXISTS idx_rate_limit_source ON rate_limit_state(source_id);

-- Schema version
INSERT INTO schema_versions (schema_name, version)
VALUES ('source_health', 'v1')
ON CONFLICT (schema_name) DO UPDATE SET version = EXCLUDED.version, applied_at = CURRENT_TIMESTAMP;
