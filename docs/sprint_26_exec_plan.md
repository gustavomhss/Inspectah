# Plano de Execução — Sprint 26 (Programa 1)

## Objetivo sucinto
Implementar o Design System Inspectah Admin v1 e reconstruir o Console de Fontes em cima dele, entregando CRUD + ON/OFF/arquivamento operáveis só via UI, com documentação, testes e evidências alinhadas aos gates G0–G6.

## Entregas técnicas concretas
- Design System Admin v1 materializado em `frontend/inspectah-ui/src/ui/admin/` com tokens, layout e componentes nucleares (botões, inputs, select, tabela, badge, modal, toast, banner, form field) testados.
- Console de Fontes v2 em `frontend/inspectah-ui/src/features/sources/` usando apenas o design system: lista com filtros, criação/edição, ações de ativar/desativar/arquivar, badges de status e feedbacks de erro/sucesso/loading.
- Client de API tipado em `features/sources/api/sourcesApi.ts` + tipos em `features/sources/types/Source.ts` consumindo rotas de fontes.
- Contratos de backend de fontes alinhados em `app/sources/` (models/schemas/routes) com testes em `tests/api/test_sources_console.py`.
- Scripts de gates S26 em `bin/s26_g0_*.sh` … `bin/s26_g6_*.sh` produzindo scorecards `out/scorecards/S26_G*.json` e evidências em `out/evidence/S26_G*/`.
- Docs de apoio: `docs/design_system_admin_v1.md`, `docs/runbook_operacao_fontes_v1.md` e bundle `out/bundles/inspectah_s26_evidence_bundle.zip`.

## Mapeamento Capítulos/Blocos → Paths de trabalho
- **Cap 1 (Contexto, Escopo In/Out, Personas)** → direciona foco das telas/admin e evita temas fora de fontes/design system; referência para textos de UI e runbook.
- **Cap 2 (Gates, Métricas, DoD)** → `bin/s26_g0_*.sh` … `bin/s26_g6_*.sh`, `out/scorecards/S26_G*.json`, `out/evidence/S26_G*/`, `out/bundles/inspectah_s26_evidence_bundle.zip`.
- **Cap 3.2 (Design System filemap)** → `frontend/inspectah-ui/src/ui/admin/` (`tokens/`, `layout/`, `components/`, `hooks/`, `index.ts`).
- **Cap 3.3 (Console de Fontes filemap)** → `frontend/inspectah-ui/src/features/sources/` (`pages/`, `components/`, `api/`, `types/`, `index.ts`).
- **Cap 3.3 (APIs de fontes)** → `app/sources/models.py`, `app/sources/schemas.py`, `app/sources/routes.py` (ou equivalente), `tests/api/test_sources_console.py`.
- **Cap 4.1 (Waves)** → ordena execução W0–W3; checkpoints: W1 (esqueletos + G0/G1/G3 rodando), W2 (fluxos fontes + G2/G4), W3 (UX/hardening + G5/G6).
- **Cap 4.2 (Estratégia Dev/CI)** → branches de trabalho `feature/s26_*`, uso de `bin/ci_local.sh` e workflow `s26-gates`.
- **Cap 4.3 (Plano de evidências)** → organização de logs/prints em `out/evidence/S26_G*/`, hash e índice do bundle.
- **Cap 4.4 (Tasks)** → lista de tasks `S26-T-XXX` guiando ordem de implementação e dependências.

## Checks/Gates a rodar localmente
- **G0** `bin/s26_g0_scope_and_baseline.sh`: confirma docs Cap1–4, presença de `ui/admin` e `features/sources`, deps instaladas.
- **G1** `bin/s26_g1_design_system_static.sh`: compile TS + lint + testes do design system; zero componentes órfãos fora de `ui/admin`.
- **G2** `bin/s26_g2_sources_console_flows.sh`: testes de fluxos do Console de Fontes (lista, criar, editar, ativar/desativar/arquivar, validação).
- **G3** `bin/s26_g3_frontend_quality.sh`: lint/testes/build do frontend completo.
- **G4** `bin/s26_g4_sources_api_contracts.sh`: testes de API de fontes cobrindo contratos e transições de status.
- **G5** `bin/s26_g5_docs_and_runbooks.sh`: checa existência/tamanho mínimo de `docs/design_system_admin_v1.md` e `docs/runbook_operacao_fontes_v1.md`.
- **G6** `bin/s26_g6_orr_bundle.sh`: valida pastas de evidência G0–G5 e gera `out/bundles/inspectah_s26_evidence_bundle.zip` com hash e índice.

## Notas e alinhamentos
- Escopo fora (Cap 1.5): não criar temas extras/dark mode, não migrar outros consoles além de fontes, não mexer em métricas avançadas de ingestão nesta sprint.
- Invariantes estruturais (Cap 3.4): design system é agnóstico de domínio; console usa apenas `@/ui/admin`; nenhum campo exposto na UI sem respaldo no backend; tokens como fonte única de estilos.
- Ordem sugerida (W0→W3): grounding + G0 baseline → esqueleto DS/console e ajustes de scripts → implementação de fluxos e contratos + testes → hardening/UX + docs/runbooks + bundle final.
- Estado atual (pós-W1): branch `feature/programa1_s26_admin_v1` ativo; design system/base de console criados; lint verde para `src/ui/admin` e `src/features/sources`; docs-ponte Cap1–4 e Cap1–6 criados; G0 verde. Próximos passos W2: implementar `sourcesApi.ts` contra backend real, completar páginas `SourcesListPage` e `SourceEditPage` com componentes admin, ligar rotas/admin shell, fortalecer scripts G1–G3 e criar testes de fluxos (G2).
- Estado final (wrap/W3): Console de Fontes v2 integrado ao backend real (listagem, criação/edição, mudança de estado) com testes RTL/MSW em `src/features/sources/__tests__/sourcesPages.test.tsx` sem warnings relevantes; scripts G0–G3 executáveis e verdes; rotas /admin/sources apontam para o console v2; docs-ponte completos; plano e notas atualizados. Dívidas: aprimorar cobertura além dos fluxos principais (ex.: validações avançadas), completar Cap 5/6 com evidências finais e runbook dedicado (G5/G6 futuro).
