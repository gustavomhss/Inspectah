# Bloco 1 — Learnings
- Governança multi-fluxo funciona quando templates/políticas são versionados e ligados a SLO/incident desde o início.
- Métricas/logs com `flow_id/flow_version_id` simplificam diagnóstico e rollback; sem isso, OracleOps fica cego.
- Pilotos em domínios diferentes expõem políticas específicas; biblioteca de políticas precisa ser viva e testável.
- UI precisa mostrar diffs, estado de teste/ativo e SLO/incident em uma única superfície para evitar ruído operacional.
