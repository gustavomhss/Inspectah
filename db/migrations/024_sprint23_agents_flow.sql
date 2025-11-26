-- Sprint 23 - fluxo de camadas de agentes
CREATE TABLE IF NOT EXISTS ai_agent_flow_layers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    layer_type TEXT NOT NULL,
    layer_index INTEGER NOT NULL,
    agent_ids TEXT NOT NULL,
    mediator_agent_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
