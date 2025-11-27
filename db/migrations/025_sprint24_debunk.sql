-- Sprint 24 - Debunker v0 & humano-no-loop (Camada de Contestação)
-- Estrutura mínima para DebunkIssues, DebunkTasks, DebunkDecisions e trilha de eventos.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS debunk_issues (
    id TEXT PRIMARY KEY,
    target_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    question TEXT NOT NULL,
    reason TEXT NOT NULL,
    risk_level TEXT NOT NULL,
    priority INTEGER NOT NULL,
    status TEXT NOT NULL,
    origin TEXT NOT NULL,
    opened_by TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS debunk_issue_target_open_idx
    ON debunk_issues(target_type, target_id)
    WHERE status IN ('OPEN','TRIAGED','IN_REVIEW','PENDING_ADDITIONAL_EVIDENCE','READY_FOR_DECISION','ESCALATED');

CREATE TABLE IF NOT EXISTS debunk_tasks (
    id TEXT PRIMARY KEY,
    issue_id TEXT NOT NULL REFERENCES debunk_issues(id) ON DELETE CASCADE,
    task_type TEXT NOT NULL,
    instructions TEXT NOT NULL,
    status TEXT NOT NULL,
    assigned_to TEXT,
    result TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    due_at TEXT
);

CREATE INDEX IF NOT EXISTS debunk_tasks_issue_idx ON debunk_tasks(issue_id);

CREATE TABLE IF NOT EXISTS debunk_decisions (
    id TEXT PRIMARY KEY,
    issue_id TEXT NOT NULL REFERENCES debunk_issues(id) ON DELETE CASCADE,
    decision_type TEXT NOT NULL,
    confidence REAL,
    rationale TEXT NOT NULL,
    recommended_truth_action TEXT NOT NULL,
    evidence_refs TEXT,
    residual_uncertainties TEXT,
    created_by TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS debunk_decisions_issue_idx ON debunk_decisions(issue_id);

CREATE TABLE IF NOT EXISTS debunk_issue_events (
    id TEXT PRIMARY KEY,
    issue_id TEXT NOT NULL REFERENCES debunk_issues(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    payload TEXT,
    created_by TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS debunk_issue_events_issue_idx ON debunk_issue_events(issue_id);
