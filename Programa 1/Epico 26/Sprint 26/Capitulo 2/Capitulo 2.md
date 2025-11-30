# Inspectah — Sprint 26 (S26)
## Capítulo 2 — Gates, Métricas & Definition of Done

Este capítulo transforma o contexto da S26 (Capítulo 1) em **gates objetivos**, métricas claras e um Definition of Done binário: ou a sprint cumpre os critérios e é **GO**, ou permanece **NO-GO** até correção.

Cap.2 é organizado em quatro blocos:
- **Bloco 2.1** — Lista de gates da S26 e propósito de cada um.
- **Bloco 2.2** — Scripts de gates, scorecards e métricas/thresholds.
- **Bloco 2.3** — Mapa de evidências da sprint.
- **Bloco 2.4** — Definition of Done (DoD) da S26 e regras de NO-GO.

---

## Bloco 2.1 — Lista de Gates da S26 e Propósito de Cada Um

A Sprint 26 é protegida por **6 gates formais**. Eles formam o contrato objetivo da sprint: **sem todos verdes, não existe GO**.

### Visão geral dos gates

- **G0 — Scope & Baseline**  
  Garante que a sprint começou em terreno sólido: docs, filemap, estrutura mínima do design system e do Console de Fontes, dependências instaladas e ambiente minimamente saudável.

- **G1 — Design System Admin v1 (Static Integrity)**  
  Verifica que o Design System Admin v1 existe como biblioteca concreta, com tokens centralizados, componentes nucleares implementados e sem violações estruturais (componentes órfãos, dependências proibidas, erros de tipo/estilo).

- **G2 — Console de Fontes v2 (Fluxos Básicos)**  
  Garante que os fluxos críticos do Console de Fontes — lista, criação, edição, ativar/desativar/arquivar — funcionam ponta a ponta e estão cobertos por testes automatizados.

- **G3 — Front-End Quality & Regression**  
  Atende pela sanidade do front como um todo: lint, testes e build de produção precisam continuar íntegros após a introdução do design system e da refatoração do console.

- **G4 — API & Modelo de Dados de Fontes (Contratos)**  
  Garante que o Console de Fontes v2 fala com APIs e modelos coerentes: contratos de request/response respeitados, invariantes básicos de fontes preservados e testados.

- **G5 — Documentação & Runbooks S26**  
  Assegura que o que foi construído é ensinável e repetível: guia do Design System Admin v1 e runbook de operação de fontes existem, têm corpo e foram minimamente validados.

- **G6 — Evidence & ORR Bundle S26**  
  Fecha a sprint em termos de auditabilidade: todas as pastas de evidência de G0–G5 existem e um bundle único da S26 é gerado com os artefatos principais.

### Propósito de cada gate em relação ao objetivo da S26

- **G0 — "Começar em chão firme"**  
  S26 só faz sentido se a base documental, de filemap e de ambiente estiver no lugar. G0 evita começar a sprint em modo improviso, sem contrato nem estrutura mínima.

- **G1 — "Existe mesmo um Design System Admin v1"**  
  O objetivo central da sprint é criar esse design system. G1 responde, de forma binária, se ele existe como código organizado, testável e livre de erros óbvios.

- **G2 — "O Console de Fontes realmente funciona sobre o design system"**  
  Não basta ter componentes bonitos; o Console de Fontes precisa operar o ciclo de vida básico de fontes usando o design system. G2 valida isso na prática, via testes de fluxo.

- **G3 — "Não quebramos o resto do front"**  
  A refatoração de S26 tem impacto transversal. G3 garante que a introdução do Design System Admin v1 não deixou o resto da UI em ruínas.

- **G4 — "A UI não mente sobre o backend"**  
  Um console perfeito em aparência, mas descolado do modelo de dados, é inutilizável. G4 assegura alinhamento entre Console de Fontes v2 e APIs/modelos de fontes.

- **G5 — "O conhecimento saiu da cabeça do time"**  
  Programa 1 exige operação via consoles com runbooks claros. G5 força a materialização desse conhecimento em docs reais: guia de design system + runbook de fontes.

- **G6 — "Deixamos trilha para o futuro"**  
  Sem bundle de evidências, não há como auditar S26 nem reaproveitar suas provas na validação do Programa 1. G6 garante que a sprint termina com um pacote único, inspecionável.

---

## Bloco 2.2 — Scripts de Gates, Scorecards & Métricas

Cada gate da S26 é implementado por um **script shell idempotente** em `bin/`, produzindo evidências em `out/evidence/` e um **scorecard JSON** em `out/scorecards/`. Todos os scripts seguem o padrão:

- Saída **exit code 0** = gate passou (GO).  
- Saída **exit code != 0** = gate falhou (NO-GO) até correção.

### G0 — Scope & Baseline

- **Script:** `bin/s26_g0_scope_and_baseline.sh`  
- **Evidências:** `out/evidence/S26_G0_scope_and_baseline/`  
- **Scorecard:** `out/scorecards/S26_G0_scope_and_baseline.json`

Verifica, no mínimo:

1. Presença dos docs de S26:
   - `docs/sprint_26_cap_1_contexto.md` (Cap.1);  
   - `docs/sprint_26_cap_2_gates_e_metricas.md` (este capítulo);  
   - `docs/sprint_26_cap_3_arquitetura_e_filemap.md`;  
   - `docs/sprint_26_cap_4_execucao_e_evidencias.md`.

2. Presença de estrutura base do design system e console de fontes:
   - diretório de design system admin (ex.: `frontend/inspectah-ui/src/ui/admin/` ou equivalente);  
   - diretório do Console de Fontes v2.

3. Sanidade mínima de ambiente:
   - `npm install`/`npm ci` bem-sucedido no frontend;  
   - dependências mínimas de backend instaladas (se necessárias para testes de API).

**Métricas chave no scorecard G0:**

- `docs_present` (boolean)  
- `frontend_deps_ok` (boolean)  
- `backend_deps_ok` (boolean)  
- `design_system_skeleton_present` (boolean)  
- `sources_console_skeleton_present` (boolean)

Condição para **GO**: todos os campos `true`.

---

### G1 — Design System Admin v1 (Static Integrity)

- **Script:** `bin/s26_g1_design_system_static.sh`  
- **Evidências:** `out/evidence/S26_G1_design_system_static/`  
- **Scorecard:** `out/scorecards/S26_G1_design_system_static.json`

Valida que o Design System Admin v1:

1. Possui arquivo único de tokens com definição de cores, tipografia e espaçamentos.  
2. Não possui componentes admin fora da árvore do design system (varredura por paths proibidos).  
3. Passa por testes estáticos:
   - TypeScript compile da pasta do design system;  
   - testes unitários/snapshot dos componentes nucleares;  
   - lint sem erros.

**Métricas chave no scorecard G1:**

- `ts_compile_errors_count` (number)  
- `lint_errors_count` (number)  
- `ds_component_tests_total` (number)  
- `ds_component_tests_passed` (number)  
- `orphan_admin_components_found` (number)

Condições para **GO**:

- `ts_compile_errors_count == 0`  
- `lint_errors_count == 0`  
- `ds_component_tests_passed == ds_component_tests_total`  
- `orphan_admin_components_found == 0`

---

### G2 — Console de Fontes v2 (Fluxos Básicos)

- **Script:** `bin/s26_g2_sources_console_flows.sh`  
- **Evidências:** `out/evidence/S26_G2_sources_console_flows/`  
- **Scorecard:** `out/scorecards/S26_G2_sources_console_flows.json`

Executa uma suíte de testes automatizados cobrindo os fluxos principais do Console de Fontes:

1. Listagem de fontes (carregamento da página, tabela renderizada, filtros básicos funcionando).  
2. Criação de fonte válida: preencher formulário, salvar, ver fonte listada.  
3. Validação de campos obrigatórios: tentativas inválidas geram mensagens claras.  
4. Edição de fonte: alterar campos, salvar e ver atualização.  
5. Ativar/Desativar/Arquivar: executar ações com diálogos de confirmação e mudança correta de estado.

**Métricas chave no scorecard G2:**

- `flows_total` (number)  
- `flows_passed` (number)  
- `flows_blocking_failures` (number)  
- `ui_regression_detected` (boolean)

Condições para **

