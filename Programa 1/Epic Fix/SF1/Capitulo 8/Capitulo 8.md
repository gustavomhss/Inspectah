# SF1 — Capítulo 8 — Frontend Engineering (Console Rollout)

## Superfícies
- FlowListMulti: badges de mode, SLO/alertas, hash publish/runtime.
- FlowRolloutPanel: estado, percentuais, deadlines, alertas, drift, hash, actor/operation_id.
- FlowRolloutDialog: start canary/teste com actor/hash obrigatórios; valida limites.
- FlowVersionHistory: timeline promo/rollback, eventos, hash.

## Requisitos FE
- Bloquear ações se actor ausente ou hash divergente; toasts/erros claros e específicos (drift/alerta/actor); feedback imediato.
- Mostrar alertas “SLO breach”, “Drift de catálogo”, “Limite excedido”; badges visíveis na lista e painel; CTA rollback destacado quando alerta ativo.
- Capturar screenshots reais (Playwright/Cypress) nos pilotos; falha se placeholder; export de painel incluído; registrar hash/operation_id visível nas capturas.
