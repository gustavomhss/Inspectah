# Bloco 4 — Observabilidade, Evidências e Mini-esquemas
- **Painel/alertas:** `observability/dashboards/s35_flow_rollout_overview.json` (execuções por modo, rollbacks, violações de política, SLO/alertas, progresso canary); alertas em `observability/alerts/s35/*.yaml`.
- **Evidências por fluxo:** `dataset_noticias.json`, `dataset_contestacao.json`; `ingest_log.txt`; `exec_dump.json`; `metrics_logs_snapshot.*`; `console_screenshots/`; `rollout_timeline.json` (promoções/rollback).
- **Mini-esquema — `exec_dump.json` (por item):**
  ```json
  {
    "item_id": "news-abc-123",
    "flow_id": "fluxo_noticias_v2",
    "flow_version_id": "v2.1.0",
    "mode": "canary",
    "operation_id": "op-789",
    "steps": [
      {"stage": "interpretacao", "agent_ref": "agent_interpreter_v2", "status": "ok", "latency_ms": 1200, "summary": "..."}
    ],
    "policies": {"min_confidence": 0.72, "block_on_missing_entities": true},
    "slo": {"slo_id": "slo_noticias_latency", "status": "pass", "p95_ms": 1900},
    "rollout": {"test_percentual": 10, "criteria_met": true}
  }
  ```
- **Mini-esquema — `rollout_timeline.json` (por fluxo):**
  ```json
  {
    "flow_id": "fluxo_noticias_v2",
    "flow_version_id": "v2.1.0",
    "catalog_hash": "<sha256>",
    "events": [
      {"ts": "2024-10-01T10:00:00Z", "action": "start_canary", "percentual": 10, "actor": "ops_user", "notes": ""},
      {"ts": "2024-10-01T14:00:00Z", "action": "promote", "criteria": "slo_noticias_latency pass"},
      {"ts": "2024-10-01T16:00:00Z", "action": "rollback", "reason": "alert_policy_violation"}
    ]
  }
  ```
- **Mini-esquema — `ingest_log.txt` (linha):** `timestamp | flow_id | flow_version_id | mode | operation_id | stage | status | latency_ms | policy_violation? | message`
