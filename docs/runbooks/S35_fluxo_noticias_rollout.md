# S35 — Runbook rollout fluxo notícias v2

## Resumo
- Fluxo: `flow_news_v2` (flow_version_id: `v2.1.0`)
- Modos: teste/canary/ativo com limites em `config/flows_limits.yaml`
- Flags: `s35_flow_rollout_enabled`, `s35_flow_catalog_enforced`, `s35_flow_logic_contract_enabled`
- Catálogo: `config/flow_catalog/news_v2.yaml` (hash/signature)

## Passo a passo (canary → promo/rollback)
1) Confirmar catálogo carregado:
   - GET `/api/flows/catalog` → verificar hash/assinatura de `news_v2`.
2) Iniciar canary:
   - POST `/api/flows/{flow_id}/rollout` com `mode=canary`, `test_percentual<=20`, `actor=ops_user`, `criteria={"slo_id":"slo_noticias_latency"}`.
3) Monitorar painel `s35_flow_rollout_overview` e alertas s35.
4) Promover:
   - POST `/api/flows/{flow_id}/promote` com `actor=ops_admin`.
5) Rollback (se alertas/breaches):
   - POST `/api/flows/{flow_id}/rollback_rollout` com `flow_version_id=ativo_anterior`, `actor=ops_admin`.

## Evidências
- `out/evidence/S35_G4_pilotos_rollout/` (datasets, ingest_log, exec_dump, rollout_timeline, metrics_logs_snapshot, screenshots)
- Alertas disparados: `S35_FlowRolloutRollbacksHigh`/`S35_FlowRolloutPolicyViolations` se aplicável.
