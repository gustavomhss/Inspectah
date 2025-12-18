-- ============================================================================
-- S39: Sharding Infrastructure Migration
-- Task: S39-DB-031
-- Version: sharding_v1
--
-- This migration creates the schema for domain-based sharding.
-- It should be applied to ALL shard databases (default, politica, economia, saude).
-- ============================================================================

-- Schema versions table (if not exists)
CREATE TABLE IF NOT EXISTS schema_versions (
    id SERIAL PRIMARY KEY,
    schema_name VARCHAR(100) NOT NULL UNIQUE,
    version VARCHAR(50) NOT NULL,
    applied_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- CLAIMS TABLE (core fact-checking content)
-- ============================================================================
CREATE TABLE IF NOT EXISTS claims (
    id VARCHAR(36) PRIMARY KEY,
    text TEXT NOT NULL,
    normalized_text TEXT,
    domain VARCHAR(32) NOT NULL DEFAULT 'default',
    source_id VARCHAR(100),
    source_url TEXT,
    source_type VARCHAR(50),
    status VARCHAR(32) DEFAULT 'pending',  -- pending, analyzing, verified, false, misleading
    confidence_score DECIMAL(3, 2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    analyzed_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    tags VARCHAR(100)[] DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_claims_domain ON claims(domain);
CREATE INDEX IF NOT EXISTS idx_claims_status ON claims(status);
CREATE INDEX IF NOT EXISTS idx_claims_source ON claims(source_id);
CREATE INDEX IF NOT EXISTS idx_claims_created ON claims(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_claims_text_trgm ON claims USING GIN (normalized_text gin_trgm_ops);

-- ============================================================================
-- SIGNALS TABLE (derived metrics from claims)
-- ============================================================================
CREATE TABLE IF NOT EXISTS signals (
    id SERIAL PRIMARY KEY,
    claim_id VARCHAR(36) NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    signal_type VARCHAR(64) NOT NULL,  -- lies_in_circulation, battleground, silence_radar, fragility
    value DECIMAL(10, 4) NOT NULL,
    components JSONB DEFAULT '{}',
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    version INTEGER DEFAULT 1,
    metadata JSONB DEFAULT '{}',
    CONSTRAINT uq_claim_signal_version UNIQUE (claim_id, signal_type, version)
);

CREATE INDEX IF NOT EXISTS idx_signals_claim ON signals(claim_id);
CREATE INDEX IF NOT EXISTS idx_signals_type ON signals(signal_type);
CREATE INDEX IF NOT EXISTS idx_signals_calculated ON signals(calculated_at DESC);
CREATE INDEX IF NOT EXISTS idx_signals_value ON signals(signal_type, value DESC);

-- ============================================================================
-- EVIDENCE TABLE (supporting/refuting evidence for claims)
-- ============================================================================
CREATE TABLE IF NOT EXISTS evidence (
    id VARCHAR(36) PRIMARY KEY,
    claim_id VARCHAR(36) NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    type VARCHAR(32) NOT NULL,  -- supporting, refuting, contextual
    source_url TEXT NOT NULL,
    source_name VARCHAR(200),
    source_credibility DECIMAL(3, 2),
    title TEXT,
    excerpt TEXT,
    relevance_score DECIMAL(3, 2),
    collected_at TIMESTAMPTZ DEFAULT NOW(),
    verified_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_evidence_claim ON evidence(claim_id);
CREATE INDEX IF NOT EXISTS idx_evidence_type ON evidence(type);
CREATE INDEX IF NOT EXISTS idx_evidence_source ON evidence(source_name);
CREATE INDEX IF NOT EXISTS idx_evidence_collected ON evidence(collected_at DESC);

-- ============================================================================
-- ENTITIES TABLE (named entities extracted from claims)
-- ============================================================================
CREATE TABLE IF NOT EXISTS entities (
    id SERIAL PRIMARY KEY,
    claim_id VARCHAR(36) NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    type VARCHAR(50) NOT NULL,  -- PERSON, ORGANIZATION, LOCATION, EVENT, DATE
    normalized_name VARCHAR(200),
    wikidata_id VARCHAR(50),
    confidence DECIMAL(3, 2),
    start_pos INTEGER,
    end_pos INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_entities_claim ON entities(claim_id);
CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(normalized_name);
CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type);
CREATE INDEX IF NOT EXISTS idx_entities_wikidata ON entities(wikidata_id) WHERE wikidata_id IS NOT NULL;

-- ============================================================================
-- CLAIM RELATIONS TABLE (relationships between claims)
-- ============================================================================
CREATE TABLE IF NOT EXISTS claim_relations (
    id SERIAL PRIMARY KEY,
    source_claim_id VARCHAR(36) NOT NULL,
    target_claim_id VARCHAR(36) NOT NULL,
    relation_type VARCHAR(50) NOT NULL,  -- contradicts, supports, similar, derived_from
    strength DECIMAL(3, 2) DEFAULT 0.5,
    confidence DECIMAL(3, 2) DEFAULT 0.5,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100),
    metadata JSONB DEFAULT '{}',
    CONSTRAINT uq_claim_relation UNIQUE (source_claim_id, target_claim_id, relation_type)
);

CREATE INDEX IF NOT EXISTS idx_claim_relations_source ON claim_relations(source_claim_id);
CREATE INDEX IF NOT EXISTS idx_claim_relations_target ON claim_relations(target_claim_id);
CREATE INDEX IF NOT EXISTS idx_claim_relations_type ON claim_relations(relation_type);

-- ============================================================================
-- SHARD METADATA TABLE (shard-specific metadata)
-- ============================================================================
CREATE TABLE IF NOT EXISTS shard_metadata (
    id SERIAL PRIMARY KEY,
    domain VARCHAR(32) NOT NULL UNIQUE,
    shard_id INTEGER NOT NULL,
    claims_count BIGINT DEFAULT 0,
    signals_count BIGINT DEFAULT 0,
    last_sync_at TIMESTAMPTZ,
    health_status VARCHAR(32) DEFAULT 'healthy',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- MIGRATION TRACKING TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS migration_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id VARCHAR(100) NOT NULL,
    source_shard VARCHAR(32),
    target_shard VARCHAR(32),
    status VARCHAR(32) DEFAULT 'pending',  -- pending, in_progress, completed, failed
    migrated_at TIMESTAMPTZ,
    error_message TEXT,
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_migration_log_table ON migration_log(table_name);
CREATE INDEX IF NOT EXISTS idx_migration_log_status ON migration_log(status);
CREATE INDEX IF NOT EXISTS idx_migration_log_migrated ON migration_log(migrated_at DESC);

-- ============================================================================
-- FUNCTIONS FOR SHARD MANAGEMENT
-- ============================================================================

-- Function to update claims count in shard metadata
CREATE OR REPLACE FUNCTION update_shard_claims_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE shard_metadata
    SET claims_count = (SELECT COUNT(*) FROM claims),
        updated_at = NOW()
    WHERE domain = (SELECT current_setting('app.shard_domain', true) COALESCE 'default');
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Function to update signals count in shard metadata
CREATE OR REPLACE FUNCTION update_shard_signals_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE shard_metadata
    SET signals_count = (SELECT COUNT(*) FROM signals),
        updated_at = NOW()
    WHERE domain = (SELECT current_setting('app.shard_domain', true) COALESCE 'default');
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create triggers (disabled by default, enable after migration)
-- DROP TRIGGER IF EXISTS trg_update_claims_count ON claims;
-- CREATE TRIGGER trg_update_claims_count
-- AFTER INSERT OR DELETE ON claims
-- FOR EACH STATEMENT
-- EXECUTE FUNCTION update_shard_claims_count();

-- DROP TRIGGER IF EXISTS trg_update_signals_count ON signals;
-- CREATE TRIGGER trg_update_signals_count
-- AFTER INSERT OR DELETE ON signals
-- FOR EACH STATEMENT
-- EXECUTE FUNCTION update_shard_signals_count();

-- ============================================================================
-- EXTENSION FOR TEXT SEARCH (if not exists)
-- ============================================================================
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ============================================================================
-- SCHEMA VERSION
-- ============================================================================
INSERT INTO schema_versions (schema_name, version)
VALUES ('sharding', 'v1')
ON CONFLICT (schema_name) DO UPDATE SET version = EXCLUDED.version, applied_at = CURRENT_TIMESTAMP;
