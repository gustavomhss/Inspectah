# Bloco 3 — Observabilidade
- Métricas: `flow_rollout_*`, `flow_policy_violations_total`, `flow_catalog_hash_mismatch_total`, `inspectah_flow_slo_breach_total` com labels `{flow_id,flow_version_id,mode}`.
- Alertas: rollback_rate, policy_violation, slo_breach, catalog_hash_drift, canary_stuck_duration, api_rollout_unavailable.
- Painel `s35_flow_rollout_overview` deve mostrar séries reais (news_v2, contestacao_v0); export JSON/PNG obrigatório.
- `bin/s35_g3_obs.sh`: `curl /metrics`, promtool, simulação de firing/resolution; fail se série vazia.
