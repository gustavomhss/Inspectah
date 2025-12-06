# Bloco 2 — Gate G2 (Console/API rollout)
- Console multi-fluxo mostra estado de rollout/canary/teste (percentual, critérios de promoção, SLO/alertas) e ações de promoção/rollback/teste com autorização.
- APIs em `app/api/flow_console_routes.py` incluem:
  - `POST /api/flows/{id}/rollout` (inicia canary/teste percentual com limites/alertas).
  - `POST /api/flows/{id}/promote` (promove versão se SLO/alertas ok).
  - `POST /api/flows/{id}/rollback` (rollback de rollout em curso).
  - `GET /api/flows/{id}/rollout/status` (estado atual, métricas e alertas ativos).
- Auditoria grava `flow_id`, `flow_version_id`, `mode` (teste, canary, ativo), `operation_id`, `actor`.
- G2 PASS: UI consome APIs reais; RBAC aplicado; logs/auditoria completos; script `bin/s35_g2_console.sh` PASS.
