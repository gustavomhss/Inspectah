# S35 — Runbook rollout fluxo contestação v0

## Resumo
- Fluxo: `flow_contestacao_v0` (flow_version_id: `v0.1.0`)
- Modos: teste/canary com limites em `config/flows_limits.yaml`
- Flags: `s35_flow_rollout_enabled`, `s35_flow_catalog_enforced`
- Catálogo: `config/flow_catalog/contestacao_v0.yaml`

## Passo a passo
1) Verificar catálogo e hash em `/api/flows/catalog`.
2) Iniciar teste:
   - POST `/api/flows/{flow_id}/rollout` com `mode=test`, `test_percentual<=20`, `actor=ops_user`, `criteria={"slo_id":"slo_contestacao_latency"}`.
3) Monitorar painel `s35_flow_rollout_overview`.
4) Promover ou rollback:
   - Promo: POST `/api/flows/{flow_id}/promote` (`actor=ops_admin`).
   - Rollback: POST `/api/flows/{flow_id}/rollback_rollout` (`actor=ops_admin`).

## Evidências
- Artefatos em `out/evidence/S35_G4_pilotos_rollout/` (dataset_contestacao.json, ingest_log, exec_dump, rollout_timeline, metrics_logs_snapshot, screenshots).
