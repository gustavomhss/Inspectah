# Bloco 3 — Frontend/Console (OracleOps v3)
- **Componentes (`frontend/inspectah-ui/src/features/flows/`):**
  - `FlowRolloutPanel.tsx`: status de canary/teste/ativo, percentuais, critérios, SLO/alertas, ações de promover/rollback.
  - `FlowRolloutDialog.tsx`: inicia canary/teste com critérios/percentuais; confirmação de rollback/promoção.
  - `FlowListMulti.tsx`: lista fluxos com estado de rollout, SLO/incident, hash do catálogo carregado.
  - `FlowDetailMulti.tsx` + `FlowVersionHistory.tsx`: histórico com modos, diffs, promoções/rollback, catálogo de origem.
- **UX:** ressaltar modo ativo vs canary/teste; avisos quando catálogo diverge; badges de SLO/alerta; timeline de promoções/rollback; diffs claros por versão.
