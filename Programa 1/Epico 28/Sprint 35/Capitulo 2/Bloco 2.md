# Bloco 2 — Gate G2 (Console/API rollout)
- Console multi-fluxo mostra estado de rollout/teste/canary (percentual, limites, SLO/alertas) e ações start/promo/rollback com autorização obrigatória.
- APIs em `app/api/flow_console_routes.py` devem:
  - recusar requests sem `actor` (4xx) e registrar tentativa;
  - aceitar `POST /api/flows/{id}/rollout|promote|rollback` apenas se catálogo/hash conferem e limites não violados;
  - expor `GET /api/flows/{id}/rollout/status` com labels `flow_id`, `flow_version_id`, `mode`, `catalog_hash`, métricas/alertas relevantes.
- Auditoria obrigatória: `flow_id`, `flow_version_id`, `mode`, `operation_id`, `actor`, `catalog_hash`, `request_id`, timestamp.
- G2 PASS: UI consome APIs reais (sem mock); RBAC aplicado; casos negativos (sem actor, hash divergente, limite violado) retornam erro e são evidenciados; script `bin/s35_g2_console.sh` captura logs/JSON reais.
