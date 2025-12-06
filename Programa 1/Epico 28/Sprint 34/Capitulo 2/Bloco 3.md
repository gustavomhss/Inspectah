# Bloco 3 — Gate G3 (Observabilidade & SLO)
- Métricas em `app/flows/instrumentation.py`: `flow_exec_total`, `flow_exec_latency_seconds` (hist), `flow_policy_violations_total`, `flow_rollback_total`, `flow_ops_slo_breach_total`, sempre com `flow_id`, `flow_version_id`, `operation_id`.
- Logs estruturados em `app/flows/logs.py` com correlação (`request_id`, `flow_id`, `flow_version_id`, `operation_id`, `slo_id`, `incident_id?`).
- Painel `observability/dashboards/s34_flow_ops_overview.json` mostrando execuções por versão, violações de política, rollbacks, SLO breaches, incident timeline.
- Alertas em `observability/alerts/s34/` (ex.: rollbacks > threshold, violações de política > threshold, SLO breach em 15 min).
- SLOs versionados em `Programa 1/Sprint 34/s34_slos.md` com mapeamento para métricas reais e componentes; script `bin/s34_g3_obs.sh` PASS.
