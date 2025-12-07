# Bloco 2 — APIs e Contratos
- `POST /api/flows/{id}/rollout|promote|rollback`: exige actor/operation_id/catalog_hash; valida limites/SLO/hash; logs/auditoria completos; 4xx em ausência/deriva/limite violado.
- `GET /api/flows/{id}/rollout/status`: retorna estado, deadlines, métricas/alertas ativos, hash publish/runtime.
- Schemas incluem flow_id/flow_version_id/mode/operation_id/actor/catalog_hash.
- Eventos enviados a OracleOps/Truth com os mesmos campos + slo_status/slo_breach.
