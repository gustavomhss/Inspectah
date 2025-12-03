# Sprint 29 — ORR Summary

## Resumo executivo
- Sprint 29 (Domain Agent Flow Config v1) entregou fluxo de agentes configurável por domínio com modelo, API, UI admin e consumo em runtime. Operadores admin conseguem visualizar/editar fluxos lineares, o validador aplica invariantes mínimas e o pipeline de ingestão consulta o fluxo configurado com fallback explícito e logs.

## Escopo planejado vs. entregue
- Planejado: filemap completo, modelos + migration, validador + API admin, UI linear de fluxo, runtime consumindo fluxo configurado, evidências/bundle.
- Entregue: todos os gates G0–G4 em PASS, UI /admin/agent-flows integrada ao router/menu, runtime adapter em uso pelo pipeline (com fallback), evidências e scorecards gerados conforme Cap.2.

## Estado dos gates S29_G0–S29_G5
- S29_G0_scope_and_baseline — PASS (`out/scorecards/S29_G0_scope_and_baseline.json`) — Docs e filemap conferidos.
- S29_G1_model_and_migrations — PASS (`out/scorecards/S29_G1_model_and_migrations.json`) — Modelos/schemas/migration/testes aplicáveis.
- S29_G2_api_and_validator — PASS (`out/scorecards/S29_G2_api_and_validator.json`) — Validador + API admin com testes.
- S29_G3_ui_and_frontend_quality — PASS (`out/scorecards/S29_G3_ui_and_frontend_quality.json`) — UI de fluxos + lint/test/build.
- S29_G4_runtime_and_observability — PASS (`out/scorecards/S29_G4_runtime_and_observability.json`) — Runtime adapter integrado ao pipeline + logs/fallback.
- S29_G5_orr_and_bundle — (este ORR) — PASS após geração do bundle.

## Evidências principais e bundle
- Evidências por gate: `out/evidence/S29_G0_scope_and_baseline/` … `S29_G4_runtime_and_observability/`.
- Scorecards: `out/scorecards/S29_G0_*.json` … `S29_G4_*.json`.
- Bundle consolidado: `out/bundles/inspectah_s29_evidence_bundle.zip` (inclui evidências G0–G4, scorecards e este ORR).

## Impacto no produto e no Programa 1
- Fluxo de agentes sai do hardcode e passa a ser configurável por domínio, visível e auditável na UI admin.
- Validador evita combinações perigosas (faltam papéis mínimos, posição quebrada, decision maker fora do fim).
- Runtime de ingestão consulta o fluxo configurado e registra fallback explícito quando não há config.
- Alinha-se ao MUST READ de LLM: papéis claros, sem “agente mágico” e com rastro de responsabilidade.

## Riscos residuais e limitações
- Cobertura inicial de domínios: fluxos configurados precisam ser expandidos para mais domínios; fallback ainda pode ser usado em domínios não migrados.
- Observabilidade básica: métricas estruturadas podem ser enriquecidas (contadores por domínio/resultado).
- Warnings de testes legacy (act warnings) ainda aparecem, embora não quebrem suites.
- Fallback default é linear e genérico; domínios críticos devem ter fluxos explícitos para reduzir dependência de fallback.

## Recomendações para próximas sprints (E28.x)
- E28.2/S30: versionamento/histórico de fluxos + approvals para domínios sensíveis.
- E28.3: fluxos condicionais/branching e catálogo mais rico de papéis parametrizados.
- Observabilidade: métricas e painéis dedicados para execução de fluxos e uso de fallback.
- Expandir UI com validação pré-envio (sem duplicar regras de negócio) e melhor UX de edição em domínios grandes.
