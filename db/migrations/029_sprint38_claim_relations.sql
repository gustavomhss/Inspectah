-- ============================================================================
-- S38: Claim Relations Migration
-- Task: S38-DB-002
-- Version: claim_relations_v1
-- ============================================================================

-- Claim relations table for semantic linking
CREATE TABLE IF NOT EXISTS claim_relations (
    id SERIAL PRIMARY KEY,
    source_claim_id VARCHAR(100) NOT NULL,
    target_claim_id VARCHAR(100) NOT NULL,
    relation_type VARCHAR(20) NOT NULL,  -- supports, contradicts, related, duplicate
    confidence FLOAT NOT NULL DEFAULT 0.0,
    method VARCHAR(32) DEFAULT 'manual',  -- manual, embedding, llm, rule
    indicators JSONB DEFAULT '{}',  -- evidence for the relation
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(50) DEFAULT 'system',  -- system or user_id
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_claim_relation UNIQUE (source_claim_id, target_claim_id),
    CONSTRAINT chk_confidence CHECK (confidence >= 0 AND confidence <= 1),
    CONSTRAINT chk_relation_type CHECK (relation_type IN ('supports', 'contradicts', 'related', 'duplicate'))
);

CREATE INDEX IF NOT EXISTS idx_claim_relations_source ON claim_relations(source_claim_id);
CREATE INDEX IF NOT EXISTS idx_claim_relations_target ON claim_relations(target_claim_id);
CREATE INDEX IF NOT EXISTS idx_claim_relations_type ON claim_relations(relation_type);
CREATE INDEX IF NOT EXISTS idx_claim_relations_confidence ON claim_relations(confidence DESC);
CREATE INDEX IF NOT EXISTS idx_claim_relations_method ON claim_relations(method);

-- Claim clusters for grouping related claims
CREATE TABLE IF NOT EXISTS claim_clusters (
    id SERIAL PRIMARY KEY,
    cluster_id VARCHAR(64) NOT NULL,
    claim_id VARCHAR(100) NOT NULL,
    similarity_score FLOAT DEFAULT 0.0,
    is_representative BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_cluster_claim UNIQUE (cluster_id, claim_id)
);

CREATE INDEX IF NOT EXISTS idx_claim_clusters_cluster ON claim_clusters(cluster_id);
CREATE INDEX IF NOT EXISTS idx_claim_clusters_claim ON claim_clusters(claim_id);
CREATE INDEX IF NOT EXISTS idx_claim_clusters_representative ON claim_clusters(cluster_id) WHERE is_representative = TRUE;

-- Signal cache for on-demand calculations
CREATE TABLE IF NOT EXISTS signal_cache (
    id SERIAL PRIMARY KEY,
    signal_type VARCHAR(64) NOT NULL,  -- mentiras_em_circulacao, campo_batalha, etc
    domain VARCHAR(64) DEFAULT 'default',
    cache_key VARCHAR(256) NOT NULL,
    value JSONB NOT NULL,
    computed_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    hit_count INTEGER DEFAULT 0,
    CONSTRAINT uq_signal_cache UNIQUE (signal_type, domain, cache_key)
);

CREATE INDEX IF NOT EXISTS idx_signal_cache_type ON signal_cache(signal_type);
CREATE INDEX IF NOT EXISTS idx_signal_cache_domain ON signal_cache(domain);
CREATE INDEX IF NOT EXISTS idx_signal_cache_expires ON signal_cache(expires_at);

-- Schema version
INSERT INTO schema_versions (schema_name, version)
VALUES ('claim_relations', 'v1')
ON CONFLICT (schema_name) DO UPDATE SET version = EXCLUDED.version, applied_at = CURRENT_TIMESTAMP;
