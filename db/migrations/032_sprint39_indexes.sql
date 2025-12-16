-- Sprint 39 - Performance Indexes
-- Adiciona indexes para queries frequentes identificadas em code review.

PRAGMA foreign_keys=OFF;

-- Index composto para ordenação de debunk_issues por status+priority
-- Usado em queries como: SELECT * FROM debunk_issues WHERE status = 'OPEN' ORDER BY priority DESC
CREATE INDEX IF NOT EXISTS idx_debunk_issues_status_priority
    ON debunk_issues(status, priority DESC);

-- Index composto para consultas de runs por fonte ordenadas por tempo
-- Usado em queries como: SELECT * FROM ingestion_runs WHERE source_id = ? ORDER BY started_at DESC LIMIT 10
CREATE INDEX IF NOT EXISTS idx_ingestion_runs_source_time
    ON ingestion_runs(source_id, started_at DESC);

-- Index para config_id + status (consultas de runs ativos por config)
CREATE INDEX IF NOT EXISTS idx_ingestion_runs_config_status
    ON ingestion_runs(config_id, status);

-- Index para debunk_tasks por status (para filas de trabalho)
CREATE INDEX IF NOT EXISTS idx_debunk_tasks_status
    ON debunk_tasks(status);

-- Index para debunk_tasks assignee (queries de tasks do usuário)
CREATE INDEX IF NOT EXISTS idx_debunk_tasks_assigned
    ON debunk_tasks(assigned_to) WHERE assigned_to IS NOT NULL;

-- marca de versão
PRAGMA user_version = 32;
