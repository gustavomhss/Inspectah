-- ============================================================================
-- S37: ClaimGraph Schema Migration
-- Version: claimgraph_schema_v1
-- ============================================================================

-- Nodes table
CREATE TABLE IF NOT EXISTS graph_nodes (
    id VARCHAR(64) PRIMARY KEY,
    node_type VARCHAR(32) NOT NULL,
    content TEXT,
    attributes JSONB DEFAULT '{}',
    status VARCHAR(32) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_graph_nodes_type ON graph_nodes(node_type);
CREATE INDEX IF NOT EXISTS idx_graph_nodes_status ON graph_nodes(status);
CREATE INDEX IF NOT EXISTS idx_graph_nodes_created ON graph_nodes(created_at);

-- Edges table
CREATE TABLE IF NOT EXISTS graph_edges (
    id VARCHAR(64) PRIMARY KEY,
    edge_type VARCHAR(32) NOT NULL,
    source_id VARCHAR(64) NOT NULL,
    target_id VARCHAR(64) NOT NULL,
    weight FLOAT DEFAULT 1.0,
    attributes JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES graph_nodes(id),
    FOREIGN KEY (target_id) REFERENCES graph_nodes(id)
);

CREATE INDEX IF NOT EXISTS idx_graph_edges_type ON graph_edges(edge_type);
CREATE INDEX IF NOT EXISTS idx_graph_edges_source ON graph_edges(source_id);
CREATE INDEX IF NOT EXISTS idx_graph_edges_target ON graph_edges(target_id);
CREATE INDEX IF NOT EXISTS idx_graph_edges_pair ON graph_edges(source_id, target_id);

-- Schema version
CREATE TABLE IF NOT EXISTS schema_versions (
    schema_name VARCHAR(64) PRIMARY KEY,
    version VARCHAR(32) NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO schema_versions (schema_name, version)
VALUES ('claimgraph', 'v1')
ON CONFLICT (schema_name) DO UPDATE SET version = EXCLUDED.version, applied_at = CURRENT_TIMESTAMP;
