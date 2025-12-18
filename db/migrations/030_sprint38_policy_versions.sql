-- ============================================================================
-- S38: Policy Versions and Memory Controller Migration
-- Task: S38-DB-030
-- Version: policy_versions_v1
-- ============================================================================

-- Policy versions table
CREATE TABLE IF NOT EXISTS policy_versions (
    id SERIAL PRIMARY KEY,
    policy_id VARCHAR(100) NOT NULL,
    version INTEGER NOT NULL,
    content TEXT NOT NULL,
    author VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT FALSE,
    checksum VARCHAR(64) NOT NULL,  -- SHA-256 of content
    parent_version INTEGER,  -- previous version for diff
    metadata JSONB DEFAULT '{}',
    CONSTRAINT uq_policy_version UNIQUE (policy_id, version)
);

-- Partial unique index: only one active version per policy_id
CREATE UNIQUE INDEX IF NOT EXISTS idx_policy_active_unique
ON policy_versions(policy_id) WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_policy_versions_policy ON policy_versions(policy_id);
CREATE INDEX IF NOT EXISTS idx_policy_versions_created ON policy_versions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_policy_versions_active ON policy_versions(policy_id) WHERE is_active = TRUE;

-- Policy audit log for all operations
CREATE TABLE IF NOT EXISTS policy_audit_log (
    id SERIAL PRIMARY KEY,
    policy_id VARCHAR(100) NOT NULL,
    operation VARCHAR(32) NOT NULL,  -- create, update, activate, deactivate, rollback
    from_version INTEGER,
    to_version INTEGER,
    actor VARCHAR(100) NOT NULL,
    reason TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_policy_audit_policy ON policy_audit_log(policy_id);
CREATE INDEX IF NOT EXISTS idx_policy_audit_operation ON policy_audit_log(operation);
CREATE INDEX IF NOT EXISTS idx_policy_audit_created ON policy_audit_log(created_at DESC);

-- Memory context cache for session management
CREATE TABLE IF NOT EXISTS memory_context (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    domain VARCHAR(32) DEFAULT 'default',
    context_key VARCHAR(256) NOT NULL,
    content TEXT NOT NULL,
    token_count INTEGER DEFAULT 0,
    priority INTEGER DEFAULT 0,  -- higher = more important
    ttl_seconds INTEGER DEFAULT 3600,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    last_accessed_at TIMESTAMPTZ DEFAULT NOW(),
    access_count INTEGER DEFAULT 0,
    CONSTRAINT uq_memory_context UNIQUE (session_id, domain, context_key)
);

CREATE INDEX IF NOT EXISTS idx_memory_context_session ON memory_context(session_id);
CREATE INDEX IF NOT EXISTS idx_memory_context_domain ON memory_context(domain);
CREATE INDEX IF NOT EXISTS idx_memory_context_expires ON memory_context(expires_at);
CREATE INDEX IF NOT EXISTS idx_memory_context_priority ON memory_context(priority DESC);

-- Memory context summary for quick lookups
CREATE TABLE IF NOT EXISTS memory_context_summary (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    domain VARCHAR(32) DEFAULT 'default',
    total_tokens INTEGER DEFAULT 0,
    entry_count INTEGER DEFAULT 0,
    last_updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_memory_summary UNIQUE (session_id, domain)
);

CREATE INDEX IF NOT EXISTS idx_memory_summary_session ON memory_context_summary(session_id);

-- Schema version
INSERT INTO schema_versions (schema_name, version)
VALUES ('policy_versions', 'v1')
ON CONFLICT (schema_name) DO UPDATE SET version = EXCLUDED.version, applied_at = CURRENT_TIMESTAMP;
