# Bloco 1 — Mapa de escopo por área
- **Backend:** modos rollout (teste/canary/ativo) + engine de políticas/limites + catálogo versionado/assinado + auditoria.
- **APIs:** rotas de catálogo/rollout/promote/rollback/status com RBAC, payloads completos (`flow_id`, `flow_version_id`, `mode`, `operation_id`, `catalog_hash`, `actor`).
- **Observabilidade:** métricas/logs/alertas por modo; painel rollout; SLOs; integração com lógica/Truth via labels.
- **Frontend (OracleOps v3):** listagem multi-fluxo com estado/hash; painel e timeline de rollout; diffs; ações seguras.
- **CI/ORR & Evidências:** scripts `bin/s35_*`, workflow `s35-gates.yml`, bundle com scorecards e dumps; runbooks operacionais 24/7.
