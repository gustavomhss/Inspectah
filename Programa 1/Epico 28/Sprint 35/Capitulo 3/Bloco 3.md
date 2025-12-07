# Bloco 3 — Frontend/Console (OracleOps v3)
- **Componentes (`frontend/inspectah-ui/src/features/flows/`):**
  - `FlowRolloutPanel.tsx`: status por mode, percentuais, deadlines, SLO/alerta, hash do catálogo; ações start/promo/rollback; exibe actor/operation_id.
  - `FlowRolloutDialog.tsx`: inicia canary/teste com hash/actor obrigatórios; valida limites; pede confirmação e mostra checklist.
  - `FlowListMulti.tsx`: lista fluxos com badges de mode, SLO, alertas ativos, hash carregado vs publicado.
  - `FlowDetailMulti.tsx` + `FlowVersionHistory.tsx`: histórico com timeline de promo/rollback, diffs, `catalog_hash`, eventos enviados a OracleOps/Truth.
- **UX:** destaque canary/teste vs ativo; alerta imediato em drift de catálogo; badges “SLO breach”/“Alert firing”; CTA de rollback sempre visível; tela deve bloquear se actor vazio; screenshots reais obrigatórias nos pilotos (sem placeholders).
