# S35 — Handoff lógica/Truth para rollout governado

## Contratos
- Cada operação inclui `flow_id`, `flow_version_id`, `mode`, `operation_id`, `catalog_hash`.
- SLO IDs expostos em `rollout_criteria` e status.
- RBAC aplicado: atores permitidos em `config/flow_rollout_rbac.yaml`.

## Entregáveis para lógica/Truth
- API rollout/status: `/api/flows/{flow_id}/rollout/status` retorna `slo_status`, `alerts`, `catalog_hash`.
- Logs/Auditoria: `flow_flow_operation_logs` com actor/mode/catalog_hash.
- Observabilidade: métricas `inspectah_flow_rollout_*`, alertas s35.

## Checklist de handoff
- Catálogo hash/assinatura alinhado com runtime.
- SLO IDs e labels documentados em `Programa 1/Epico 28/Sprint 35/s35_slos.md`.
- Atores para promo/rollback acordados com Ops.
