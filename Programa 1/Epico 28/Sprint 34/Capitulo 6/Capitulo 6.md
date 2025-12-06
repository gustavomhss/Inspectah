# Inspectah — Sprint 34 — Capítulo 6
## Learnings, Dívidas Técnicas e Impacto (Multi-fluxo governável)

### 6.1 Learnings
- Governança de fluxo precisa nascer multi-domínio, com templates e SLO/incident ligados a versão.
- Operação 24/7 exige correlação clara (flow_id/flow_version_id) em métricas/logs/alertas/runbooks.
- Pilotos em domínios distintos revelam políticas específicas; manter biblioteca de políticas e templates versionados.
- Console e painel só são úteis se diffs/rollback/SLO forem confiáveis e testados com dados reais.

### 6.2 Dívidas Técnicas (S34-DT-*)
- S34-DT-001 — Editor visual simplificado para diffs de fluxo multi-domínio.
- S34-DT-002 — Políticas avançadas por domínio (além dos mínimos de S34).
- S34-DT-003 — Automatizar canary/rollout progressivo por fluxo.
- S34-DT-004 — Catálogo de templates e políticas versionado (CLI/API) para onboarding rápido de novos fluxos.
- S34-DT-005 — Integração profunda com próximos épicos (E40.5/Truth) usando `flow_version_id` nos contratos críticos.

### 6.3 Impacto no roadmap
- E28 avança para fechamento multi-fluxo; OracleOps v2 passa a operar fluxos governáveis.
- Prepara P2/P3 para usar `flow_version_id` em claims/Truth-DB/contestação.
- Base para futuras sprints de governança avançada (canary, multi-tenant) e integração com E40.5.
