-- Sprint 23 - schema de agentes, versões, comitês e política de modelos

CREATE TABLE IF NOT EXISTS ai_agents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    instructions TEXT,
    role TEXT NOT NULL,
    layer TEXT NOT NULL,
    model_name TEXT,
    recommended_model_name TEXT,
    temperature REAL,
    max_tokens INTEGER,
    top_p REAL,
    status TEXT NOT NULL,
    kb_refs TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    created_by TEXT,
    last_modified_by TEXT
);

CREATE TABLE IF NOT EXISTS ai_agent_versions (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    version_number INTEGER NOT NULL,
    instructions TEXT,
    model_name TEXT,
    temperature REAL,
    max_tokens INTEGER,
    top_p REAL,
    kb_snapshot TEXT,
    changelog TEXT,
    created_at TEXT NOT NULL,
    created_by TEXT,
    FOREIGN KEY (agent_id) REFERENCES ai_agents (id)
);

CREATE TABLE IF NOT EXISTS ai_committees (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    layer TEXT NOT NULL,
    primary_agents TEXT NOT NULL,
    mediator_agent TEXT NOT NULL,
    policy TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ai_model_policy (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    global_default_model TEXT NOT NULL,
    auto_upgrade_enabled INTEGER NOT NULL,
    adoption_delay_days INTEGER NOT NULL,
    allowed_models TEXT,
    last_upgrade_at TEXT,
    next_upgrade_at TEXT,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ai_agent_runs (
    id TEXT PRIMARY KEY,
    committee_id TEXT NOT NULL,
    input_ref TEXT,
    payload_snapshot TEXT,
    result_bundle_ref TEXT,
    status TEXT NOT NULL,
    error TEXT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (committee_id) REFERENCES ai_committees (id)
);
