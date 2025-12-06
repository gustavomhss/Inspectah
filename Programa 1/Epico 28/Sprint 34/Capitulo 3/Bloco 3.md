# Bloco 3 — Frontend/Console
- **Páginas/Componentes (`frontend/inspectah-ui/src/features/flows/`):**
  - `FlowListMulti.tsx`: lista fluxos com estado, domínio, versão ativa/teste, SLO status, alertas/incident.
  - `FlowDetailMulti.tsx`: detalhe do fluxo; exibe diagrama textual, políticas, versões, SLO/incident timeline.
  - `FlowVersionHistory.tsx`: histórico com diffs, filtros por domínio/estado/data.
  - `FlowRollbackDialog.tsx`: confirma rollback (impacto, políticas, SLO).
  - `FlowOpsPanel.tsx`: bloco OracleOps v2 com SLOs, incidentes, links para dashboards/logs.
- **Hooks/serviços:** `flowApi.ts` com chamadas às rotas de G2 e interpretação de `ops_links`.
- **UX:** destacar modo teste/percentual; badges de política/SLO; alertas inline para violações; loading/empty states; uso dos componentes admin de E26.
