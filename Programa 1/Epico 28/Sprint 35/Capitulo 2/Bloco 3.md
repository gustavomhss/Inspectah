# Bloco 3 — Gate G3 (Observabilidade rollout)
- Métricas em `app/flows/instrumentation.py`: `flow_rollout_requests_total`, `flow_rollout_success_total`, `flow_rollout_rollback_total`, `flow_exec_total{mode}`, `flow_exec_latency_seconds{mode}`, `flow_policy_violations_total`, sempre com labels `flow_id`, `flow_version_id`, `operation_id`.
- Logs em `app/flows/logs.py` incluem eventos de canary/promoção/rollback, SLO/alerta relacionados, hash do catálogo carregado.
- Painel `observability/dashboards/s35_flow_rollout_overview.json` com: execuções por modo, rollbacks, violações de política, alertas, comparação canary vs ativo.
- Alertas em `observability/alerts/s35/*.yaml`: rollbacks acima do limite, violações de política em canary, breach de SLO em teste/ativo, divergência catálogo vs runtime.
- SLOs rollout em `Programa 1/Sprint 35/s35_slos.md`; script `bin/s35_g3_obs.sh` PASS.
