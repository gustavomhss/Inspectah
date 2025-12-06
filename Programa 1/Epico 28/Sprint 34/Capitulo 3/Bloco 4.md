# Bloco 4 — Observabilidade, Evidências e Mini-esquemas
- **Métricas/alertas:** painel `observability/dashboards/s34_flow_ops_overview.json`; alertas em `observability/alerts/s34/*.yaml` (rollbacks, violações de política, SLO breach, incident backlog).
- **Evidências por fluxo:**  
  - `dataset_noticias.json`, `dataset_contestacao.json` (amostras usadas nos pilotos).  
  - `ingest_log.txt` (logs das execuções por fluxo/versão).  
  - `exec_dump.json` (trilha de execuções com `flow_id`, `flow_version_id`, `operation_id`, etapas, status, outputs resumidos).  
  - `metrics_logs_snapshot.*` (dump de métricas/logs com labels de fluxo/versão).  
  - `console_screenshots/` (UI com histórico, diffs, rollback, SLO/incident).
- **Mini-esquema — `exec_dump.json` (por item):**
  ```json
  {
    "item_id": "news-abc-123",
    "flow_id": "fluxo_noticias_v2",
    "flow_version_id": "v2.1.0",
    "operation_id": "op-789",
    "steps": [
      {"stage": "interpretacao", "agent_ref": "agent_interpreter_v2", "status": "ok", "latency_ms": 1200, "summary": "..."},
      {"stage": "classificacao", "agent_ref": "agent_classifier_v3", "status": "ok", "latency_ms": 900, "summary": "..."}
    ],
    "policies": {"min_confidence": 0.72, "block_on_missing_entities": true},
    "slo": {"slo_id": "slo_noticias_latency", "status": "pass", "p95_ms": 1900},
    "rollback_exercised": false
  }
  ```
- **Mini-esquema — `ingest_log.txt` (linha):** `timestamp | flow_id | flow_version_id | operation_id | stage | status | latency_ms | policy_violation? | message`
