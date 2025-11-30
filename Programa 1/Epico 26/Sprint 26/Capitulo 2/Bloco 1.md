# Inspectah — Sprint 26 (S26)
## Capítulo 2 — Bloco 2.2
### Scripts de Gates, Scorecards & Métricas

Este bloco detalha como cada gate da S26 é implementado em termos de:
- script de execução (em `bin/`),
- diretório de evidências (em `out/evidence/`),
- scorecard JSON (em `out/scorecards/`),
- métricas mínimas e critérios objetivos de GO/NO-GO.

Todos os scripts seguem o padrão:
- exit code `0` ⇒ gate **PASS** (GO);
- exit code diferente de `0` ⇒ gate **FAIL** (NO-GO) até correção.

---

### 1. G0 — Scope & Baseline

**Script:** `bin/s26_g0_scope_and_baseline.sh`  
**Evidências:** `out/evidence/S26_G0_scope_and_baseline/`  
**Scorecard:** `out/scorecards/S26_G0_scope_and_baseline.json`

Responsabilidade do script:
- Verificar presença dos documentos principais da sprint:
  - `docs/sprint_26_cap_1_contexto.md` (Cap.1);
  - `docs/sprint_26_cap_2_gates_e_metricas.md` (Cap.2);
  - `docs/sprint_26_cap_3_arquitetura_e_filemap.md` (Cap.3);
  - `docs/sprint_26_cap_4_execucao_e_evidencias.md` (Cap.4).
- Verificar existência das estruturas base de código:
  - diretório do Design System Admin v1 (ex.: `frontend/inspectah-ui/src/ui/admin/` ou equivalente definido no Cap.3);
  - diretório do Console de Fontes v2.
- Checar sanidade mínima de ambiente:
  - `npm ci` ou `npm install` executado com sucesso no frontend;
  - dependências de backend instaladas quando necessárias para testes vinculados à sprint.

Campos esperados no scorecard G0:
- `docs_present` (boolean)
- `frontend_deps_ok` (boolean)
- `backend_deps_ok` (boolean)
- `design_system_skeleton_present` (boolean)
- `sources_console_skeleton_present` (boolean)

Critério de GO para G0: todos os campos acima devem ser `true`.

---

### 2. G1 — Design System Admin v1 (Static Integrity)

**Script:** `bin/s26_g1_design_system_static.sh`  
**Evidências:** `out/evidence/S26_G1_design_system_static/`  
**Scorecard:** `out/scorecards/S26_G1_design_system_static.json`

Responsabilidade do script:
- Rodar TypeScript compile para a pasta do design system admin.
- Rodar linters relevantes (ESLint, etc.) no diretório do design system.
- Executar testes automatizados dos componentes nucleares (unitários e/ou snapshot).
- Verificar, via busca por paths, se existem componentes admin fora da árvore do design system (componentes órfãos).

Campos esperados no scorecard G1:
- `ts_compile_errors_count` (number)
- `lint_errors_count` (number)
- `ds_component_tests_total` (number)
- `ds_component_tests_passed` (number)
- `orphan_admin_components_found` (number)

Critério de GO para G1:
- `ts_compile_errors_count == 0`
- `lint_errors_count == 0`
- `ds_component_tests_passed == ds_component_tests_total`
- `orphan_admin_components_found == 0`

---

### 3. G2 — Console de Fontes v2 (Fluxos Básicos)

**Script:** `bin/s26_g2_sources_console_flows.sh`  
**Evidências:** `out/evidence/S26_G2_sources_console_flows/`  
**Scorecard:** `out/scorecards/S26_G2_sources_console_flows.json`

Responsabilidade do script:
- Executar uma suíte de testes automatizados focada nos fluxos principais do Console de Fontes v2:
  - listagem de fontes;
  - criação bem-sucedida de fonte válida;
  - tratamento de erros de validação em campos obrigatórios;
  - edição de fonte existente;
  - operações de ativar, desativar e arquivar fontes, incluindo diálogos de confirmação.

Os testes podem ser implementados em nível unitário/integrado (React Testing Library) ou e2e leve (ex.: Playwright/Cypress), conforme definido em Cap.3/Cap.4.

Campos esperados no scorecard G2:
- `flows_total` (number)
- `flows_passed` (number)
- `flows_blocking_failures` (number)
- `ui_regression_detected` (boolean)

Critério de GO para G2:
- `flows_passed == flows_total`
- `flows_blocking_failures == 0`
- `ui_regression_detected == false`

---

### 4. G3 — Front-End Quality & Regression

**Script:** `bin/s26_g3_frontend_quality.sh`  
**Evidências:** `out/evidence/S26_G3_frontend_quality/`  
**Scorecard:** `out/scorecards/S26_G3_frontend_quality.json`

Responsabilidade do script:
- Executar `npm ci` (ou comando equivalente aprovado) para garantir reprodutibilidade de dependências.
- Rodar lint do frontend completo (não apenas do design system).
- Rodar a suíte de testes de frontend (unitários e integrados globais), incluindo testes não específicos de S26.
- Rodar o build de produção do frontend.

Campos esperados no scorecard G3:
- `lint_errors_count` (number)
- `frontend_tests_total` (number)
- `frontend_tests_passed` (number)
- `build_succeeded` (boolean)

Critério de GO para G3:
- `lint_errors_count == 0`
- `frontend_tests_passed == frontend_tests_total`
- `build_succeeded == true`

---

### 5. G4 — API & Modelo de Dados de Fontes (Contratos)

**Script:** `bin/s26_g4_sources_api_contracts.sh`  
**Evidências:** `out/evidence/S26_G4_sources_api_contracts/`  
**Scorecard:** `out/scorecards/S26_G4_sources_api_contracts.json`

Responsabilidade do script:
- Executar testes de API específicos para o domínio de fontes (ex.: `pytest tests/api/test_sources_console.py` ou equivalente), cobrindo:
  - listagem de fontes (GET);
  - criação de fonte válida e inválida (POST);
  - atualização de fonte (PUT/PATCH);
  - ativação, desativação e arquivamento de fontes (endpoints dedicados ou parâmetros de estado).
- Verificar invariantes de modelo (pode ser via testes ou checks adicionais):
  - campos obrigatórios nunca ausentes em respostas;
  - estados inválidos não persistidos;
  - transições proibidas retornam erro adequado.

Campos esperados no scorecard G4:
- `api_tests_total` (number)
- `api_tests_passed` (number)
- `contract_violations_found` (number)

Critério de GO para G4:
- `api_tests_passed == api_tests_total`
- `contract_violations_found == 0`

---

### 6. G5 — Documentação & Runbooks S26

**Script:** `bin/s26_g5_docs_and_runbooks.sh`  
**Evidências:** `out/evidence/S26_G5_docs_and_runbooks/`  
**Scorecard:** `out/scorecards/S26_G5_docs_and_runbooks.json`

Responsabilidade do script:
- Confirmar a existência dos docs mínimos:
  - guia do Design System Admin v1 (ex.: `docs/design_system_admin_v1.md`);
  - runbook de operação de fontes (ex.: `docs/runbook_operacao_fontes_v1.md`).
- Rodar checks simples para garantir que não são cascas vazias:
  - contagem mínima de linhas;
  - presença de seções obrigatórias (por exemplo, títulos como "Objetivo", "Como usar", "Fluxos básicos").

Campos esperados no scorecard G5:
- `design_system_guide_present` (boolean)
- `runbook_fontes_present` (boolean)
- `design_system_guide_min_size_lines` (number)
- `runbook_fontes_min_size_lines` (number)

Critério de GO para G5:
- `design_system_guide_present == true`
- `runbook_fontes_present == true`
- `design_system_guide_min_size_lines >= 30`
- `runbook_fontes_min_size_lines >= 30`

---

### 7. G6 — Evidence & ORR Bundle S26

**Script:** `bin/s26_g6_orr_bundle.sh`  
**Evidências:** `out/evidence/S26_G6_orr_bundle/`  
**Bundle:** `out/bundles/inspectah_s26_evidence_bundle.zip`  
**Scorecard:** `out/scorecards/S26_G6_orr_bundle.json`

Responsabilidade do script:
- Verificar a presença das pastas de evidência de todos os gates anteriores (G0–G5).
- Gerar o bundle ZIP de evidências da S26, contendo os artefatos principais da sprint.
- Registrar metadados mínimos do bundle no scorecard (por exemplo, tamanho, lista de pastas incluídas).

Campos esperados no scorecard G6:
- `gates_expected` (number)
- `gates_with_evidence` (number)
- `bundle_created` (boolean)
- `bundle_size_bytes` (number)

Critério de GO para G6:
- `gates_with_evidence == gates_expected`
- `bundle_created == true`
- `bundle_size_bytes > 0`

---

### Síntese do Bloco 2.2

O Bloco 2.2 traduz os gates da S26 em scripts, arquivos e métricas concretas. Em conjunto com o Bloco 2.1, ele garante que não existe ambiguidade: para cada gate sabemos **o que rodar**, **onde ficam as evidências**, **como ler o scorecard** e **qual é o limiar exato de GO/NO-GO**.