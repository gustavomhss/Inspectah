-- Sprint 36 — trace_schema_v1
-- Estruturas para AgentTrace/CommitteeTrace/ReasoningStep/Feedback* com índices por decisão/TR/domínio.

PRAGMA foreign_keys=OFF;

CREATE TABLE IF NOT EXISTS agent_traces (
  agent_trace_id TEXT PRIMARY KEY,
  agent_run_id TEXT,
  committee_trace_id TEXT,
  truth_record_id TEXT,
  decision_record_id TEXT,
  claim_id TEXT,
  domain TEXT NOT NULL,
  risk_level TEXT,
  trace_schema_version TEXT NOT NULL,
  started_at TEXT,
  finished_at TEXT,
  duration_ms INTEGER,
  steps_json TEXT, -- lista de ReasoningStep embutidos ou ids (json)
  input_hash TEXT,
  redaction_applied INTEGER DEFAULT 0,
  request_id TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_agent_traces_decision ON agent_traces(decision_record_id);
CREATE INDEX IF NOT EXISTS idx_agent_traces_truth ON agent_traces(truth_record_id);
CREATE INDEX IF NOT EXISTS idx_agent_traces_claim ON agent_traces(claim_id);
CREATE INDEX IF NOT EXISTS idx_agent_traces_domain ON agent_traces(domain);
CREATE INDEX IF NOT EXISTS idx_agent_traces_risk ON agent_traces(risk_level);
CREATE INDEX IF NOT EXISTS idx_agent_traces_created ON agent_traces(created_at);

CREATE TABLE IF NOT EXISTS reasoning_steps (
  step_id TEXT PRIMARY KEY,
  agent_trace_id TEXT NOT NULL,
  order_index INTEGER NOT NULL,
  actor_role TEXT,
  step_kind TEXT,
  summary TEXT,
  input_refs TEXT,
  output_refs TEXT,
  evidence_refs TEXT,
  confidence REAL,
  elapsed_ms INTEGER,
  request_id TEXT,
  redaction_applied INTEGER DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_steps_trace ON reasoning_steps(agent_trace_id);
CREATE INDEX IF NOT EXISTS idx_steps_request ON reasoning_steps(request_id);

CREATE TABLE IF NOT EXISTS committee_traces (
  committee_trace_id TEXT PRIMARY KEY,
  committee_id TEXT,
  committee_version TEXT,
  truth_record_id TEXT,
  decision_record_id TEXT,
  claim_id TEXT,
  agent_trace_ids TEXT, -- json list
  summary TEXT,
  domain TEXT NOT NULL,
  risk_level TEXT,
  trace_schema_version TEXT NOT NULL,
  started_at TEXT,
  finished_at TEXT,
  duration_ms INTEGER,
  redaction_applied INTEGER DEFAULT 0,
  request_id TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_committee_traces_decision ON committee_traces(decision_record_id);
CREATE INDEX IF NOT EXISTS idx_committee_traces_truth ON committee_traces(truth_record_id);
CREATE INDEX IF NOT EXISTS idx_committee_traces_domain ON committee_traces(domain);
CREATE INDEX IF NOT EXISTS idx_committee_traces_risk ON committee_traces(risk_level);
CREATE INDEX IF NOT EXISTS idx_committee_traces_created ON committee_traces(created_at);

CREATE TABLE IF NOT EXISTS feedback_on_trace (
  feedback_id TEXT PRIMARY KEY,
  target_type TEXT NOT NULL, -- trace
  target_id TEXT NOT NULL,   -- agent_trace_id ou committee_trace_id
  authored_by_actor TEXT,
  authored_by_role TEXT,
  origin_surface TEXT,
  feedback_kind TEXT,
  severity TEXT,
  comment TEXT,
  suggested_action TEXT,
  pii_tags TEXT,
  redaction_applied INTEGER DEFAULT 0,
  request_id TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_feedback_trace_target ON feedback_on_trace(target_type, target_id);
CREATE INDEX IF NOT EXISTS idx_feedback_trace_created ON feedback_on_trace(created_at);

CREATE TABLE IF NOT EXISTS feedback_on_decision (
  feedback_id TEXT PRIMARY KEY,
  decision_record_id TEXT NOT NULL,
  committee_trace_id TEXT,
  agent_trace_id TEXT,
  authored_by_actor TEXT,
  authored_by_role TEXT,
  origin_surface TEXT,
  feedback_kind TEXT,
  severity TEXT,
  comment TEXT,
  suggested_action TEXT,
  pii_tags TEXT,
  redaction_applied INTEGER DEFAULT 0,
  request_id TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_feedback_decision ON feedback_on_decision(decision_record_id);
CREATE INDEX IF NOT EXISTS idx_feedback_decision_created ON feedback_on_decision(created_at);

-- marca de versão
PRAGMA user_version = 26;
