-- Sprint 40: Truth-DB Estável - DecisionBlocks + Experiences
-- Migration: 033_sprint40_decision_blocks.sql
-- Tasks: S40-DB-001, S40-DB-002, S40-DB-003

-- ============================================================
-- S40-DB-001: Tabela decision_blocks
-- ============================================================

CREATE TABLE IF NOT EXISTS decision_blocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_id VARCHAR(64) NOT NULL UNIQUE,
    claim_id VARCHAR(64) NOT NULL,
    domain VARCHAR(64) NOT NULL,
    gate VARCHAR(64) NOT NULL,

    -- State transition
    initial_state VARCHAR(32) NOT NULL,
    final_state VARCHAR(32) NOT NULL,
    transition_reason TEXT NOT NULL,

    -- References (provenance) - JSONB para flexibilidade
    references JSONB NOT NULL DEFAULT '{}',

    -- Policy info
    policy_name VARCHAR(128),
    policy_version VARCHAR(32) NOT NULL,

    -- Committee decision
    committee_summary TEXT,

    -- Evidence and experience references
    evidence_refs JSONB DEFAULT '[]',
    experience_ref JSONB DEFAULT '[]',

    -- Metrics
    latency_ms INTEGER,

    -- Metadata
    metadata JSONB DEFAULT '{}',

    -- Timestamps (append-only: created_at only, no updated_at)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT decision_blocks_initial_state_check CHECK (
        initial_state IN ('UNKNOWN', 'CLAIMED', 'UNDER_REVIEW', 'PROVISIONAL',
                          'ESTABLISHED_FACT', 'UNDER_DISPUTE', 'RETRACTED', 'BLOCKED', 'DEGRADED')
    ),
    CONSTRAINT decision_blocks_final_state_check CHECK (
        final_state IN ('UNKNOWN', 'CLAIMED', 'UNDER_REVIEW', 'PROVISIONAL',
                        'ESTABLISHED_FACT', 'UNDER_DISPUTE', 'RETRACTED', 'BLOCKED', 'DEGRADED')
    ),
    -- INV-DB-01: references.guias[] não pode ser vazio
    CONSTRAINT decision_blocks_guias_required CHECK (
        jsonb_array_length(COALESCE(references->'guias', '[]'::jsonb)) > 0
    ),
    -- INV-DB-04: references.pilares[] não pode ser vazio
    CONSTRAINT decision_blocks_pilares_required CHECK (
        jsonb_array_length(COALESCE(references->'pilares', '[]'::jsonb)) > 0
    ),
    -- INV-DB-02: references.e40_5 deve existir
    CONSTRAINT decision_blocks_e40_5_required CHECK (
        references ? 'e40_5' AND references->'e40_5' ? 'status'
    )
);

-- Comentários para documentação
COMMENT ON TABLE decision_blocks IS 'Unidade de verdade: registro imutável de decisões sobre claims (S40)';
COMMENT ON COLUMN decision_blocks.references IS 'Provenance completa: guias[], pilares[], policy{}, e40_5{}';
COMMENT ON COLUMN decision_blocks.experience_ref IS 'IDs de experiências similares consultadas';

-- ============================================================
-- S40-DB-002: Índices para decision_blocks
-- ============================================================

-- Índice para consulta de timeline por claim_id (objetivo: < 50ms)
CREATE INDEX IF NOT EXISTS idx_decision_blocks_claim_timeline
    ON decision_blocks (claim_id, created_at DESC);

-- Índice para filtro por domínio
CREATE INDEX IF NOT EXISTS idx_decision_blocks_domain
    ON decision_blocks (domain);

-- Índice para filtro por gate
CREATE INDEX IF NOT EXISTS idx_decision_blocks_gate
    ON decision_blocks (gate);

-- Índice composto para queries comuns
CREATE INDEX IF NOT EXISTS idx_decision_blocks_domain_gate_created
    ON decision_blocks (domain, gate, created_at DESC);

-- Índice para final_state (útil para dashboards)
CREATE INDEX IF NOT EXISTS idx_decision_blocks_final_state
    ON decision_blocks (final_state);

-- Índice GIN para busca em references JSONB
CREATE INDEX IF NOT EXISTS idx_decision_blocks_references_gin
    ON decision_blocks USING GIN (references);

-- ============================================================
-- S40-DB-003: Tabela experiences (append-only)
-- ============================================================

-- Verificar se extensão pgvector está disponível
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector') THEN
        RAISE NOTICE 'pgvector extension not installed. Using JSONB fallback for embeddings.';
    END IF;
END
$$;

CREATE TABLE IF NOT EXISTS experiences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experience_id VARCHAR(64) NOT NULL UNIQUE,
    claim_id VARCHAR(64) NOT NULL,
    decision_id VARCHAR(64) NOT NULL,

    -- Texto do claim para referência
    claim_text TEXT NOT NULL,

    -- Embedding (usar VECTOR se pgvector disponível, senão JSONB fallback)
    -- Dimensão 384 para sentence-transformers/all-MiniLM-L6-v2
    embedding JSONB, -- Fallback: array de floats em JSONB

    -- Resultado/outcome da experiência
    outcome VARCHAR(32) NOT NULL,

    -- Metadados
    domain VARCHAR(64),
    metadata JSONB DEFAULT '{}',

    -- Timestamp (append-only)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT experiences_outcome_check CHECK (
        outcome IN ('ESTABLISHED_FACT', 'RETRACTED', 'UNDER_DISPUTE', 'PROVISIONAL')
    )
);

-- Comentários
COMMENT ON TABLE experiences IS 'Experiências de decisões passadas para retrieval por similaridade (S40)';
COMMENT ON COLUMN experiences.embedding IS 'Embedding do claim (384 dims all-MiniLM-L6-v2) em JSONB';
COMMENT ON COLUMN experiences.outcome IS 'Resultado final da experiência para aprendizado';

-- Índices para experiences
CREATE INDEX IF NOT EXISTS idx_experiences_claim_id
    ON experiences (claim_id);

CREATE INDEX IF NOT EXISTS idx_experiences_domain
    ON experiences (domain);

CREATE INDEX IF NOT EXISTS idx_experiences_outcome
    ON experiences (outcome);

CREATE INDEX IF NOT EXISTS idx_experiences_created
    ON experiences (created_at DESC);

-- Índice GIN para embedding (busca de similaridade básica)
CREATE INDEX IF NOT EXISTS idx_experiences_embedding_gin
    ON experiences USING GIN (embedding);

-- ============================================================
-- Função para adicionar coluna VECTOR se pgvector estiver disponível
-- ============================================================

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector') THEN
        -- Adicionar coluna vector se pgvector disponível
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'experiences' AND column_name = 'embedding_vector'
        ) THEN
            ALTER TABLE experiences ADD COLUMN embedding_vector vector(384);
            CREATE INDEX idx_experiences_embedding_ivfflat
                ON experiences USING ivfflat (embedding_vector vector_cosine_ops);
            RAISE NOTICE 'Added vector column with ivfflat index for experiences';
        END IF;
    END IF;
END
$$;

-- ============================================================
-- Rollback script (para referência)
-- ============================================================
-- DROP TABLE IF EXISTS experiences;
-- DROP TABLE IF EXISTS decision_blocks;
