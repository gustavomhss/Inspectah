# Bloco 4 — Observabilidade, Evidências e Mini-esquemas
- **Painel/alertas:** `observability/dashboards/s35_flow_rollout_overview.json` (execuções por mode, rollbacks, violações de política, drift de catálogo, SLO/alertas, progresso canary); alertas em `observability/alerts/s35/*.yaml` validados por promtool + firing simulado.
- **Evidências por fluxo:** datasets reais (`dataset_noticias.json`, `dataset_contestacao.json`), `ingest_log.txt`, `exec_dump.json`, `metrics_logs_snapshot.*` (curl /metrics + promtool), `console_screenshots/*.png` reais, `rollout_timeline.json`, comparação de hash (publish vs runtime), prints de alert firing/resolution.
- **Mini-esquema — `exec_dump.json` (por item):**
  ```json
  {
    "item_id": "news-abc-123",
    "flow_id": "news_v2",
    "flow_version_id": "v2.1.0",
    "mode": "canary",
    "operation_id": "op-789",
    "actor": "ops_user",
    "catalog_hash": "<sha256-publish>",
    "steps": [{"stage": "interpretacao", "agent_ref": "agent_interpreter_v2", "status": "ok", "latency_ms": 1200}],
    "policies": {"min_confidence": 0.72, "block_on_missing_entities": true},
    "slo": {"slo_id": "s35_slo_rollout_duration_news_v2", "status": "pass", "p95_ms": 1900},
    "rollout": {"test_percentual": 10, "criteria_met": true}
  }
  ```
- **Mini-esquema — `rollout_timeline.json` (por fluxo):**
  ```json
  {
    "flow_id": "news_v2",
    "flow_version_id": "v2.1.0",
    "catalog_hash": "<sha256-publish>",
    "events": [
      {"ts": "2025-12-06T10:00:00Z", "action": "start_canary", "percentual": 10, "actor": "ops_user", "notes": ""},
      {"ts": "2025-12-06T10:30:00Z", "action": "slo_breach", "slo_id": "s35_slo_policy_violations_news_v2"},
      {"ts": "2025-12-06T10:35:00Z", "action": "rollback", "reason": "policy_violation"},
      {"ts": "2025-12-06T11:30:00Z", "action": "promote", "criteria": "slo pass"}
    ]
  }
  ```
- **Mini-esquema — `ingest_log.txt` (linha):** `timestamp | flow_id | flow_version_id | mode | operation_id | actor | catalog_hash | stage | status | latency_ms | policy_violation? | message`
