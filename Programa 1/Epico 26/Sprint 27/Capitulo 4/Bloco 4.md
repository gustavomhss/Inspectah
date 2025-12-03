# Inspectah — Sprint 27 (S27)
## Capítulo 4 — Bloco 4
### Tabela Oficial de Tasks S27-T-XXX

> Arquivo-alvo no repo: `docs/s27_cap_4_4_tasks_oficiais_s27.md`
>
> Função: definir a lista oficial de tasks da Sprint 27 (S27-T-XXX), com ligação explícita a waves, gates, estados-alvo e filemap. Este bloco é a trilha de execução concreta da S27.

---

## 1. Convenções para as tasks S27-T-XXX

Cada task segue o formato:

ID: `S27-T-XXX`  
Wave: `W0`, `W1`, `W2`, `W3`  
Categoria: `frontend`, `backend`, `gates`, `tests`, `docs`, `ops` (ou combinações)  
Descrição: frase iniciada com verbo, clara e objetiva  
Artefatos: paths específicos do Cap.3 (frontend, backend, scripts, docs, etc.)  
Gates: lista `[G0..G6]` diretamente impactados ou protegidos  
Estados-alvo: referências a estados da S27 (ex.: `SA-01` Admin v1 padrão real, `SA-02` fluxos E2E, `SA-03` contratos estáveis, `SA-04` operação documentada, `SA-05` ORR objetivo)  
Done: condição objetiva de conclusão  
Evidências: arquivos esperados em `out/scorecards/`, `out/evidence/`, `docs/` ou `out/bundles/`

Estados-alvo (para referência rápida):

SA-01 — Admin v1 é padrão real em Fontes, Ingestão e Debunker  
SA-02 — Fluxos admin críticos funcionam de ponta a ponta  
SA-03 — Contratos de API estão consistentes e verificáveis  
SA-04 — Operadores têm docs e runbooks fiéis à realidade  
SA-05 — A S27 e o Épico E26 podem ser julgados objetivamente via ORR

---

## 2. Tasks da Wave W0 — Groundwork & Sanidade

### S27-T-001 — Implementar e parametrizar o script G0 da S27

Wave: W0  
Categoria: gates, ops  
Descrição: Implementar `bin/s27_g0_env_repo.sh` para verificar sanidade mínima de repositório, ambiente e presença de docs Cap.1–Cap.3 da S27.  
Artefatos:  
- `bin/s27_g0_env_repo.sh`  
- `out/scorecards/S27_G0_scope_and_env.json`  
- `out/evidence/S27_G0_env_repo/env_check.log`  
- `out/evidence/S27_G0_env_repo/docs_presence.log`  
Gates: [G0]  
Estados-alvo: [SA-01, SA-02, SA-03]  
Done: Script executa sem erro em ambiente local, gera scorecard com `env_ok == true` e flags de presença de docs corretas; logs são criados nas pastas de evidência.  
Evidências: Scorecard G0 preenchido e logs em `out/evidence/S27_G0_env_repo/`.

### S27-T-002 — Validar presença e leitura dos capítulos 1, 2 e 3 da S27

Wave: W0  
Categoria: docs, ops  
Descrição: Garantir que `docs/s27_cap_1_*.md`, `docs/s27_cap_2_*.md` e `docs/s27_cap_3_*.md` existem, foram revisados pelo squad e estão coerentes entre si.  
Artefatos:  
- `docs/s27_cap_1_*.md`  
- `docs/s27_cap_2_*.md`  
- `docs/s27_cap_3_*.md`  
Gates: [G0]  
Estados-alvo: [SA-01..SA-05]  
Done: Todos os capítulos existem, foram lidos pelo squad e eventuais ajustes de coerência foram aplicados; `docs_presence.log` atualizado.  
Evidências: Anotação em `out/evidence/S27_G0_env_repo/docs_presence.log` e nota sintética em Cap.4 ou Cap.6.

### S27-T-003 — Levantamento do estado atual de Admin v1 e consoles

Wave: W0  
Categoria: frontend, docs  
Descrição: Mapear e registrar o estado atual de `ui/admin` e dos consoles de Fontes, Ingestão e Debunker, incluindo gaps conhecidos versus filemap-alvo da S27.  
Artefatos:  
- `docs/s27_cap_3_*.md` (atualizações)  
- nota em `docs/s27_cap_6_learnings_dividas_roadmap.md` (estado inicial)  
Gates: [G0, G1, G2, G3]  
Estados-alvo: [SA-01, SA-02]  
Done: Filemap de Cap.3 está alinhado à realidade (ou gaps são explicitamente marcados) e há nota de estado inicial registrada.  
Evidências: Entrada em Cap.6 descrevendo o snapshot inicial.

---

## 3. Tasks da Wave W1 — Núcleo funcional Admin v1 nos consoles

### S27-T-010 — Alinhar SourcesListPage ao AdminShell

Wave: W1  
Categoria: frontend  
Descrição: Refatorar `SourcesListPage` para usar `AdminShell`, `AdminHeader` e `AdminContent` do Admin v1 de forma canônica.  
Artefatos:  
- `frontend/inspectah-ui/features/sources/pages/SourcesListPage.tsx`  
Gates: [G1, G2, G3]  
Estados-alvo: [SA-01, SA-02]  
Done: Página de lista de fontes renderiza dentro de AdminShell sem quebras de layout, cenários E2E mínimos de listagem de fontes passam em G2, G3 roda com sucesso.  
Evidências: Atualização no scorecard G1 indicando uso de Admin v1 em Fontes; logs de G2/G3 sem falhas relacionadas à tela de fontes.

### S27-T-011 — Alinhar IngestionOverviewPage ao AdminShell

Wave: W1  
Categoria: frontend  
Descrição: Refatorar `IngestionOverviewPage` para usar layout e componentes base do Admin v1, garantindo consistência com Fontes e Debunker.  
Artefatos:  
- `frontend/inspectah-ui/features/ingestion/pages/IngestionOverviewPage.tsx`  
Gates: [G1, G2, G3]  
Estados-alvo: [SA-01, SA-02]  
Done: Tela principal de ingestão está integrada ao AdminShell e participa do cenário E2E mínimo de ingestão em G2, com G3 verde.  
Evidências: Scorecards G1, G2, G3 atualizados e logs de E2E contendo o cenário de ingestão.

### S27-T-012 — Alinhar DebunkerCasesListPage ao AdminShell

Wave: W1  
Categoria: frontend  
Descrição: Refatorar `DebunkerCasesListPage` para usar AdminShell, com header e conteúdo padronizados, mantendo filtros e lista de casos.  
Artefatos:  
- `frontend/inspectah-ui/features/debunker/pages/DebunkerCasesListPage.tsx`  
Gates: [G1, G2, G3]  
Estados-alvo: [SA-01, SA-02]  
Done: Lista de casos de disputa funciona em AdminShell, cenário E2E mínimo de Debunker roda em G2, G3 verde para esta página.  
Evidências: Scorecards G1/G2/G3 com referências à tela; logs de E2E.

### S27-T-013 — Implementar script G1 para Admin v1

Wave: W1  
Categoria: gates, tests  
Descrição: Implementar `bin/s27_g1_admin_design_system.sh` para validar build de `ui/admin`, rodar testes específicos e checar imports em consoles admin.  
Artefatos:  
- `bin/s27_g1_admin_design_system.sh`  
- `out/scorecards/S27_G1_admin_design_system.json`  
- `out/evidence/S27_G1_admin_design_system/design_build.log`  
- `out/evidence/S27_G1_admin_design_system/imports_scan.log`  
Gates: [G1]  
Estados-alvo: [SA-01]  
Done: Script executa sem erro, scorecard preenche campos de adesão ao Admin v1, logs de build e scan estão presentes.  
Evidências: Scorecard e logs atualizados.

### S27-T-014 — Implementar script G2 com cenários E2E mínimos

Wave: W1  
Categoria: tests, gates  
Descrição: Implementar `bin/s27_g2_admin_flows.sh` com pelo menos 3 cenários E2E (Fontes, Ingestão, Debunker) usando a UI sob Admin v1.  
Artefatos:  
- `bin/s27_g2_admin_flows.sh`  
- testes E2E em `tests/e2e/admin_flows/` (ou equivalente)  
- `out/scorecards/S27_G2_admin_flows.json`  
- `out/evidence/S27_G2_admin_flows/e2e_results.log`  
Gates: [G2, G3]  
Estados-alvo: [SA-02]  
Done: Os 3 cenários mínimos rodam com sucesso, scorecard G2 mostra esses cenários como `status: "pass"`.  
Evidências: E2E log e scorecard G2.

### S27-T-015 — Implementar script G3 de qualidade de frontend admin

Wave: W1  
Categoria: gates, tests  
Descrição: Implementar `bin/s27_g3_front_quality_admin.sh` para rodar lint, tests e build do `frontend/inspectah-ui`, produzindo logs separados e scorecard.  
Artefatos:  
- `bin/s27_g3_front_quality_admin.sh`  
- `out/scorecards/S27_G3_front_quality_admin.json`  
- logs em `out/evidence/S27_G3_front_quality_admin/`  
Gates: [G3]  
Estados-alvo: [SA-01, SA-02]  
Done: Script executa sem erro, scorecard G3 tem flags `lint_ok`, `tests_ok`, `build_ok` coerentes com o estado do front.  
Evidências: Logs de lint/tests/build e scorecard G3.

---

## 4. Tasks da Wave W2 — Refinos, Contratos & Operação

### S27-T-020 — Ampliar cenários E2E combinados Fontes → Ingestão → Debunker

Wave: W2  
Categoria: tests  
Descrição: Adicionar cenários E2E que percorrem o fluxo completo de Fontes → Ingestão → Debunker, incluindo pelo menos um caso em que um problema de ingestão leva a um caso em Debunker.  
Artefatos:  
- `tests/e2e/admin_flows/*`  
- `out/scorecards/S27_G2_admin_flows.json` (atualizado)  
Gates: [G2, G3]  
Estados-alvo: [SA-02]  
Done: Cenários combinados são executados com sucesso em G2, e scorecard documenta esses cenários explicitamente.  
Evidências: E2E log com identificação dos cenários combinados.

### S27-T-021 — Consolidar filemap de APIs de Fontes para contratos admin

Wave: W2  
Categoria: backend, docs  
Descrição: Revisar e, se necessário, alinhar `app/api/sources_routes.py`, `app/models/sources.py` e `app/schemas/sources.py` aos contratos esperados pelos consoles admin e pelos testes de contrato.  
Artefatos:  
- `app/api/sources_routes.py`  
- `app/models/sources.py`  
- `app/schemas/sources.py`  
- `tests/api/test_admin_sources_contracts.py`  
Gates: [G2, G4]  
Estados-alvo: [SA-02, SA-03]  
Done: Testes de contrato de Fontes passam em G4; cenários E2E de Fontes não quebram por inconsistência de contrato.  
Evidências: `contracts_tests.log` atualizado e campos de Fontes em `S27_G4_admin_contracts.json` marcados como OK.

### S27-T-022 — Consolidar filemap de APIs de Ingestão 2.0 para contratos admin

Wave: W2  
Categoria: backend, tests  
Descrição: Alinhar `app/api/ingestion_routes.py`, `app/models/ingestion.py` e `app/schemas/ingestion.py` com as necessidades dos consoles de ingestão e dos testes de contrato.  
Artefatos:  
- `app/api/ingestion_routes.py`  
- `app/models/ingestion.py`  
- `app/schemas/ingestion.py`  
- `tests/api/test_admin_ingestion_contracts.py`  
Gates: [G2, G4]  
Estados-alvo: [SA-02, SA-03]  
Done: Testes de contrato de Ingestão passam em G4; cenários E2E de ingestão continuam verdes.  
Evidências: Atualização em `contracts_tests.log` e scorecard G4.

### S27-T-023 — Consolidar filemap de APIs do Debunker para contratos admin

Wave: W2  
Categoria: backend, tests  
Descrição: Harmonizar `app/api/debunker_routes.py`, `app/models/debunker.py` e `app/schemas/debunker.py` com os requisitos do console Debunker e dos testes de contrato.  
Artefatos:  
- `app/api/debunker_routes.py`  
- `app/models/debunker.py`  
- `app/schemas/debunker.py`  
- `tests/api/test_admin_debunker_contracts.py`  
Gates: [G2, G4]  
Estados-alvo: [SA-02, SA-03]  
Done: Testes de contrato de Debunker passam em G4; E2E de Debunker e fluxos combinados continuam verdes.  
Evidências: `contracts_tests.log` e scorecard G4 com blocos de Debunker ok.

### S27-T-024 — Implementar script G4 de contratos & APIs

Wave: W2  
Categoria: gates, tests  
Descrição: Implementar `bin/s27_g4_admin_contracts.sh` para rodar os testes de contrato de Fontes, Ingestão e Debunker, além de validações de schemas, consolidando resultado em G4.  
Artefatos:  
- `bin/s27_g4_admin_contracts.sh`  
- `out/scorecards/S27_G4_admin_contracts.json`  
- `out/evidence/S27_G4_admin_contracts/contracts_tests.log`  
Gates: [G4]  
Estados-alvo: [SA-03]  
Done: Script roda com sucesso, scorecard G4 lista serviços cobertos e possíveis mismatches; logs aparecem em `contracts_tests.log`.  
Evidências: Scorecard G4 e log.

### S27-T-025 — Escrever Guia de Consoles Admin v1.1

Wave: W2  
Categoria: docs  
Descrição: Produzir `docs/guia_consoles_admin_v1_1.md` descrevendo princípios, componentes e padrões de uso do Admin v1 nos consoles de Fontes, Ingestão e Debunker.  
Artefatos:  
- `docs/guia_consoles_admin_v1_1.md`  
Gates: [G5]  
Estados-alvo: [SA-01, SA-04]  
Done: Guia existe, contém seções mínimas (objetivo, componentes principais, exemplos, anti-padrões) e foi lido pelo squad; G5 reconhece sua presença.  
Evidências: `presence_check.log` com guia listado; `S27_G5_docs_runbooks.json` com `guides_present == true`.

### S27-T-026 — Escrever runbook de operação do console de Fontes

Wave: W2  
Categoria: docs, ops  
Descrição: Criar `docs/runbook_operacao_fontes_vX.md` com objetivos, personas, fluxos críticos, incidentes típicos e estados da UI do console de Fontes.  
Artefatos:  
- `docs/runbook_operacao_fontes_vX.md`  
Gates: [G5]  
Estados-alvo: [SA-04]  
Done: Runbook existe com estrutura mínima definida em Cap.3/Cap.2; foi usado em pelo menos uma simulação de operação.  
Evidências: `presence_check.log` e `structure_check.log` em `out/evidence/S27_G5_docs_runbooks/`; ORR menciona o uso do runbook.

### S27-T-027 — Escrever runbook de operação do console de Ingestão

Wave: W2  
Categoria: docs, ops  
Descrição: Criar `docs/runbook_operacao_ingestao_vX.md` para orientar operação diária e resposta a incidentes em Ingestão 2.0.  
Artefatos:  
- `docs/runbook_operacao_ingestao_vX.md`  
Gates: [G5]  
Estados-alvo: [SA-04]  
Done: Runbook segue as seções mínimas (fluxos, incidentes, estados de tela, como navegar) e foi testado em simulação.  
Evidências: Logs de G5; referência no ORR.

### S27-T-028 — Escrever runbook de operação do console Debunker

Wave: W2  
Categoria: docs, ops  
Descrição: Criar `docs/runbook_operacao_debunker_vX.md` cobrindo trabalho com casos, evidências e decisões no Debunker.  
Artefatos:  
- `docs/runbook_operacao_debunker_vX.md`  
Gates: [G5]  
Estados-alvo: [SA-04]  
Done: Runbook completo e testado em simulação de casos em ORR ou pré-ORR.  
Evidências: Logs de G5 e menções em ORR.

---

## 5. Tasks da Wave W3 — Hardening, ORR & Bundle

### S27-T-030 — Rodada de hardening em Admin v1 + consoles

Wave: W3  
Categoria: frontend, tests  
Descrição: Corrigir bugs críticos e problemas de UX descobertos em W1/W2 nos consoles admin, mantendo aderência ao Admin v1.  
Artefatos:  
- ajustes em `ui/admin/*` e `features/*`  
Gates: [G1, G2, G3]  
Estados-alvo: [SA-01, SA-02]  
Done: Lista de issues críticos resolvidos; G1, G2 e G3 rodam verdes na rodada final pré-ORR.  
Evidências: Scorecards finais G1/G2/G3, changelog interno em Cap.6 se necessário.

### S27-T-031 — Rodada completa final de G0–G5

Wave: W3  
Categoria: gates, ops  
Descrição: Executar G0, G1, G2, G3, G4 e G5 em sequência, registrando o commit/estado do repo e consolidando scorecards finais.  
Artefatos:  
- `out/scorecards/S27_G0_scope_and_env.json` (final)  
- `out/scorecards/S27_G1_admin_design_system.json` (final)  
- `out/scorecards/S27_G2_admin_flows.json` (final)  
- `out/scorecards/S27_G3_front_quality_admin.json` (final)  
- `out/scorecards/S27_G4_admin_contracts.json` (final)  
- `out/scorecards/S27_G5_docs_runbooks.json` (final)  
Gates: [G0, G1, G2, G3, G4, G5]  
Estados-alvo: [SA-01..SA-04]  
Done: Todos os scorecards refletem a situação final; eventuais falhas ou ressalvas estão documentadas em `notes`.  
Evidências: Logs finais em `out/evidence/S27_G*/`.

### S27-T-032 — Implementar e rodar script G6 de ORR & bundle

Wave: W3  
Categoria: gates, ops  
Descrição: Implementar e executar `bin/s27_g6_orr_bundle.sh` para montar o bundle de evidências, checar presença de scorecards e docs-chave e gerar scorecard G6.  
Artefatos:  
- `bin/s27_g6_orr_bundle.sh`  
- `out/scorecards/S27_G6_orr_summary.json`  
- `out/bundles/inspectah_s27_evidence_bundle.zip`  
Gates: [G6]  
Estados-alvo: [SA-05]  
Done: Script roda sem erro, bundle é gerado com scorecards, evidências e docs principais; G6 registra `bundle_created == true` e um veredito preliminar.  
Evidências: bundle zip e scorecard G6.

### S27-T-033 — Conduzir ORR da S27 e registrar decisão sobre o Épico E26

Wave: W3  
Categoria: docs, ops  
Descrição: Conduzir a sessão formal de ORR da S27 com participação dos owners relevantes, registrar decisões, riscos e o veredito sobre a S27 e o Épico E26.  
Artefatos:  
- `docs/s27_cap_5_orr_local_summary.md`  
- `out/evidence/S27_G6_orr/orr_session.log`  
- `out/scorecards/S27_G6_orr_summary.json` (atualizado pós-ORR)  
Gates: [G6]  
Estados-alvo: [SA-05]  
Done: ORR conduzido, documento preenchido com lista de participantes, resumo de G0–G5, cenários E2E, riscos e veredito; scorecard G6 reflete decisão final.  
Evidências: ORR summary, orr_session.log e scorecard G6.

### S27-T-034 — Consolidar learnings, dívidas e ajustes de roadmap pós-S27

Wave: W3  
Categoria: docs, ops  
Descrição: Registrar em `docs/s27_cap_6_learnings_dividas_roadmap.md` os principais aprendizados da S27, dívidas técnicas e de produto, e impactos no roadmap futuro.  
Artefatos:  
- `docs/s27_cap_6_learnings_dividas_roadmap.md`  
Gates: [G5, G6]  
Estados-alvo: [SA-04, SA-05]  
Done: Cap.6 preenche seções de learnings, dívidas e roadmap com base em scorecards, logs e ORR; contém referência explícita a tasks e artefatos da sprint.  
Evidências: Cap.6 atualizado e citado no ORR.

---

## 6. Uso da tabela de tasks na prática

- Cada task S27-T-XXX deve constar no board da sprint (físico ou digital), com seu ID e wave correspondentes.  
- Novas tasks só devem ser criadas se puderem ser mapeadas a estados-alvo, gates e paths do Cap.3; caso contrário, Cap.1–3 precisam ser revisados.  
- Ao dar DONE em uma task, o time deve conferir se as evidências listadas estão de fato presentes.  
- Cap.5 e Cap.6 devem referenciar IDs de tasks ao explicar decisões, riscos e aprendizados.

Com este Bloco 4.4, a S27 deixa de ser apenas um conjunto de intenções e desenhos: passa a ter uma lista explícita de trabalhos concretos, com começo, meio, fim e rastro claro no repositório e nas evidências.

