# Bloco 3 — Gate G3 (Observabilidade rollout)
- Métricas em `app/flows/instrumentation.py`: `flow_rollout_requests_total`, `flow_rollout_success_total`, `flow_rollout_rollback_total`, `flow_rollout_duration_seconds`, `flow_policy_violations_total`, `flow_catalog_hash_mismatch_total`, sempre com labels `{flow_id,flow_version_id,mode}`. Expostas e verificadas via `curl /metrics` + `promtool`.
- Logs incluem eventos de canary/promoção/rollback/SLO breach com `flow_id`, `flow_version_id`, `mode`, `operation_id`, `actor`, `catalog_hash`.
- Painel `observability/dashboards/s35_flow_rollout_overview.json` deve renderizar séries não vazias para news_v2 e contestacao_v0; export JSON/PNG obrigatório no bundle.
- Alertas `observability/alerts/s35/*.yaml`: rollbacks acima do limite, violações de política, breach de SLO (usando s35_slos.md), drift de catálogo, canary_stuck_duration, indisponibilidade API rollout.
- `bin/s35_g3_obs.sh` precisa: rodar promtool, consultar métricas com labels corretos, simular alert firing (ex.: incrementar rollback/policy_violation), capturar firing/resolution. Falha se qualquer alerta não dispara ou painel vazio.
