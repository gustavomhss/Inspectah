# Bloco 2 — Plano por eixo (checklist operacional)
- **Backend:** migração/template loader/policy_engine/versioning multi-fluxo; ops_integration emitindo eventos de SLO/incident.
- **APIs:** rotas multi-fluxo (lista/detalhe/versions/diffs/rollback/state/ops) com RBAC e auditoria.
- **Frontend:** lista/detalhe multi-fluxo; histórico/diffs; rollback/promoção; painel de ops (SLO/incident) no detalhe.
- **Observabilidade:** métricas/logs com `flow_id/flow_version_id`; alertas e painel `s34_flow_ops_overview`.
- **E2E:** pilotos notícias e contestação v0 executados em teste/ativo; rollback e políticas exercitados; evidências completas.
- **Gates/CI:** `bin/s34_g0..g5.sh`, metrics_summary, bundle, workflow `s34-gates.yml`.
