# S35 — Operação de catálogo de fluxos

## Checklist
- Catálogo em `config/flow_catalog/*.yaml` com hash/assinatura.
- Validar: `bin/s35_g0_scope.sh` e `/api/flows/catalog`.
- Flags: `s35_flow_catalog_enforced` habilitada em produção.
- Drift: alertas `S35_FlowRolloutCatalogDrift` monitorados.

## Operações
- Publicar/validar catálogo via CI: `bin/s35_g0_scope.sh`, `bin/s35_g1_model.sh`.
- Conferir hash/assinatura antes de rollout; bloquear promoções se divergir.

## Evidências
- Scorecards `out/scorecards/S35_G0_scope.json`, `S35_G1_model.json`.
- Painel `s35_flow_rollout_overview` seção catalog_drift.
