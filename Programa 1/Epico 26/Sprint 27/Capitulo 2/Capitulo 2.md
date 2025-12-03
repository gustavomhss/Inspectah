# Inspectah — Sprint 27 (S27)
## Capítulo 2 — Gates, Métricas, Scorecards & ORR

> Arquivo-alvo no repo: `docs/s27_cap_2_gates_metricas_orr.md`
>
> Função: definir, para a Sprint 27, **quais gates existem**, o que cada um protege, **como medimos sucesso/falha** (métricas & scorecards) e **como o ORR consolida a decisão de GO/NO-GO**. Este capítulo é o contrato de verificação da S27.

---

## 1. Visão geral dos gates da S27

A S27 herda a estrutura geral de gates do Sprint Playbook v3 e da S26, adaptando-os ao foco de **Admin v1 para Fontes, Ingestão 2.0 e Debunker**.

Gates propostos para a S27:

- **G0 — Escopo, Grounding & Sanidade de Ambiente**  
  Verifica se o escopo da S27 está bem ancorado (Cap.1), se o repositório/ambiente estão saudáveis e se não há divergência grave de branches/configuração.

- **G1 — Design System Admin v1 (Integridade de Tokens & Componentes)**  
  Garante que `ui/admin` está consistente, compilando e sem violações de padrões básicos, e que consoles alvo usam o design system em vez de clones locais.

- **G2 — Fluxos de Consoles Admin (Fontes/Ingestão/Debunker)**  
  Testa, via suites de testes (unitários, integrações e E2E), os fluxos principais de operação nos três consoles.

- **G3 — Qualidade Global de Frontend Admin**  
  Lint, build, testes de componentes, smoke tests de navegação/admin.

- **G4 — Contratos & APIs relevantes para consoles admin**  
  Verifica se contratos backend necessários para Fontes, Ingestão e Debunker estão coerentes e documentados (sem quebra silenciosa).

- **G5 — Documentação & Runbooks de Operação**  
  Garante existência e consistência de guias e runbooks de Fontes, Ingestão e Debunker sob Admin v1.

- **G6 — ORR & Bundle de Evidências da S27**  
  Consolida resultados dos gates anteriores, cenários E2E e simulações em ponto único de decisão GO/NO-GO para fechamento da sprint e do Épico E26.

Cada gate possui:
- **Escopo** (o que protege),  
- **Entradas** (artefatos/scripts/ambiente),  
- **Saídas** (scorecards, evidências),  
- **Métricas-chave** e critérios de GO/NO-GO.

---

## 2. Gate G0 — Escopo, Grounding & Sanidade de Ambiente

### 2.1 Objetivo

Garantir que a S27 está:
- ancorada no Cap.1 (problema, estados-alvo e escopo),  
- rodando em ambiente reprodutível e saudável (sem sujeira de branches, deps quebradas, etc.),  
- com leitura explícita de dependências e riscos de base.

### 2.2 Escopo

- Validar:
  - repositório em estado consistente (sem migrations pendentes quebrando, sem dependências faltando);  
  - existência dos docs Cap.1 e Cap.2 em paths corretos;  
  - que o escopo S27 não conflita com dívidas/decisões de S26 registradas em Cap.6.

### 2.3 Entradas e scripts

- Script alvo sugerido: `bin/s27_g0_env_repo.sh`  
  - Checa:
    - `git status` limpo ou com alterações compreendidas;  
    - virtualenv configurado (`.venv`), dependências básicas instaladas;  
    - comandos mínimos de sanity (ex.: `pytest -q` rápido; `npm test -- --help` ou equivalente, se aplicável);  
    - presença dos arquivos de docs: `docs/s27_cap_1_*.md`, `docs/s27_cap_2_gates_metricas_orr.md`.

### 2.4 Saídas

- Scorecard: `out/scorecards/S27_G0_scope_and_env.json`  
  - Campos mínimos:  
    - `env_ok` (bool),  
    - `docs_cap_1_present` (bool),  
    - `docs_cap_2_present` (bool),  
    - `notes` (string).

- Evidências:
  - Logs de execução do script em `out/evidence/S27_G0_env_repo/`.

### 2.5 Critério de GO/NO-GO

- **GO**: `env_ok == true` e `docs_cap_1_present == true` e `docs_cap_2_present == true`.  
- **NO-GO**: qualquer campo essencial falso; repositório ou ambiente inconsistentes.

---

## 3. Gate G1 — Design System Admin v1 (Tokens & Componentes)

### 3.1 Objetivo

Garantir que o **Design System Inspectah Admin v1** está íntegro e que os consoles alvo (Fontes, Ingestão, Debunker) **realmente o utilizam** em vez de padrões ad-hoc.

### 3.2 Escopo

- `ui/admin/` (tokens, layout, componentes base).  
- Pastas de features dos consoles:
  - `frontend/inspectah-ui/features/sources/*`  
  - `frontend/inspectah-ui/features/ingestion/*`  
  - `frontend/inspectah-ui/features/debunker/*`

### 3.3 Entradas e scripts

- Script alvo sugerido: `bin/s27_g1_admin_design_system.sh`  
  - Passos típicos:
    - rodar tipagem/tests específicos do design system (se existirem);  
    - rodar uma checagem de import: garantir que consoles usam componentes de `ui/admin` em vez de imports legados;  
    - opcional: usar um grep/lint customizado para detectar CSS de layout "cru" dentro de features.

### 3.4 Saídas

- Scorecard: `out/scorecards/S27_G1_admin_design_system.json`  
  - Campos mínimos:  
    - `design_system_build_ok` (bool);  
    - `consoles_using_admin_components` (enum: `full`, `partial`, `broken`);  
    - `legacy_layout_usages` (int);  
    - `notes` (string).

- Evidências:  
  - Logs do script em `out/evidence/S27_G1_admin_design_system/`;  
  - eventualmente, relatórios de lint customizado.

### 3.5 Critério de GO/NO-GO

- **GO forte**:  
  - `design_system_build_ok == true`,  
  - `consoles_using_admin_components == "full"`,  
  - `legacy_layout_usages == 0` (ou muito próximo de 0, com justificativa/documentação se > 0).

- **GO com ressalvas** (excepcional, exigindo registro em Cap.6):  
  - `consoles_using_admin_components == "partial"`,  
  - `legacy_layout_usages > 0`, mas mapeados como `S27-DT-XXX` e com plano claro de tratamento.

- **NO-GO**:  
  - `design_system_build_ok == false`, ou  
  - `consoles_using_admin_components == "broken"`.

---

## 4. Gate G2 — Fluxos de Consoles Admin (Fontes/Ingestão/Debunker)

### 4.1 Objetivo

Garantir que os **fluxos principais de operação** nos três consoles (Fontes, Ingestão, Debunker) funcionem de ponta a ponta sob Admin v1.

### 4.2 Escopo

- Cenários básicos de E2E, por exemplo:
  - Fontes: cadastrar fonte, validar config mínima, ativar/desativar;  
  - Ingestão: observar runs, identificar falhas/atrasos em fonte específica, reprocessar ou sinalizar;  
  - Debunker: visualizar disputa originada de dado vindo de uma fonte, tomar decisão (aprovar/rejeitar/escalação).

### 4.3 Entradas e scripts

- Scripts alvo:  
  - `bin/s27_g2_admin_flows.sh`  
    - Pode orquestrar testes de integração/E2E (ex.: Playwright/Cypress ou suíte própria).  
    - Executa cenários pré-definidos e coleta resultados.

### 4.4 Saídas

- Scorecard: `out/scorecards/S27_G2_admin_flows.json`  
  - Campos mínimos:  
    - `sources_flows_ok` (bool);  
    - `ingestion_flows_ok` (bool);  
    - `debunker_flows_ok` (bool);  
    - `combined_flows_ok` (bool);  
    - `failed_scenarios` (lista);  
    - `notes` (string).

- Evidências:  
  - Logs e relatórios de testes em `out/evidence/S27_G2_admin_flows/`;  
  - prints/snapshots de falhas, se existirem.

### 4.5 Critério de GO/NO-GO

- **GO**:  
  - todos os `*_flows_ok == true`,  
  - `failed_scenarios` vazio (ou contendo apenas cenários explicitamente recortados de escopo e anotados como tal).

- **NO-GO**:  
  - qualquer `*_flows_ok == false` em cenário in-scope da S27.

---

## 5. Gate G3 — Qualidade Global de Frontend Admin

### 5.1 Objetivo

Assegurar que a base de frontend admin está saudável:
- projeto compila;  
- lint e testes de componentes passam;  
- navegação básica não quebra.

### 5.2 Escopo

- Subconjunto de comandos padrão front-end (ex.: `npm test`, `npm run lint`, `npm run build`) focados na parte admin, se segmentado, ou no projeto todo se compartilhado.

### 5.3 Entradas e scripts

- Script alvo: `bin/s27_g3_front_quality_admin.sh`  
  - Executa:  
    - lint;  
    - testes unitários;  
    - build.

### 5.4 Saídas

- Scorecard: `out/scorecards/S27_G3_front_quality_admin.json`  
  - Campos mínimos:  
    - `lint_ok` (bool);  
    - `tests_ok` (bool);  
    - `build_ok` (bool);  
    - `notes` (string).

- Evidências: logs em `out/evidence/S27_G3_front_quality_admin/`.

### 5.5 Critério de GO/NO-GO

- **GO**: todos os flags `*_ok == true`.  
- **NO-GO**: qualquer falha sem justificativa excepcional.

---

## 6. Gate G4 — Contratos & APIs relevantes

### 6.1 Objetivo

Evitar que a migração para Admin v1 esconda ou masqueie que **contratos e APIs** usados por Fontes, Ingestão e Debunker estão incoerentes ou quebrados.

### 6.2 Escopo

- Schemas e endpoints utilizados pelos consoles alvo (ex.: `/api/sources/*`, `/api/ingestion/*`, `/api/debunker/*`).

### 6.3 Entradas e scripts

- Script alvo: `bin/s27_g4_admin_contracts.sh`  
  - Pode incluir:  
    - validação de OpenAPI/JSON Schema;  
    - testes automatizados de contratos (ex.: usando `schemathesis` ou suíte interna);  
    - checagens de compatibilidade entre modelos front e back.

### 6.4 Saídas

- Scorecard: `out/scorecards/S27_G4_admin_contracts.json`  
  - Campos mínimos:  
    - `sources_api_ok` (bool);  
    - `ingestion_api_ok` (bool);  
    - `debunker_api_ok` (bool);  
    - `schema_mismatches` (lista);  
    - `notes` (string).

- Evidências: `out/evidence/S27_G4_admin_contracts/`.

### 6.5 Critério de GO/NO-GO

- **GO**: todos `*_api_ok == true`, e `schema_mismatches` vazio ou com entradas explicitamente mapeadas como dívidas de risco controlado.  
- **NO-GO**: quebra de contrato que impeça operação segura dos consoles.

---

## 7. Gate G5 — Documentação & Runbooks de Operação

### 7.1 Objetivo

Garantir que docs e runbooks de Fontes, Ingestão e Debunker:
- refletem a realidade pós-S27;  
- usam o mesmo idioma de Admin v1;  
- são suficientes para operadores e on-call.

### 7.2 Escopo

- `docs/guia_consoles_admin_v1_1.md` (ou nome final equivalente);  
- runbooks: `docs/runbook_operacao_fontes_vX.md`, `docs/runbook_operacao_ingestao_vX.md`, `docs/runbook_operacao_debunker_vX.md`.

### 7.3 Entradas e scripts

- Script alvo: `bin/s27_g5_docs_runbooks.sh`  
  - Verifica presença dos arquivos;  
  - opcionalmente, roda checks de estrutura mínima (seções obrigatórias).

- Além do script, revisão manual em ORR (Cap.5) para verificar qualidade de conteúdo.

### 7.4 Saídas

- Scorecard: `out/scorecards/S27_G5_docs_runbooks.json`  
  - Campos mínimos:  
    - `guides_present` (bool);  
    - `runbooks_present` (bool);  
    - `runbooks_reviewed_in_orr` (bool);  
    - `notes` (string).

- Evidências:  
  - logs em `out/evidence/S27_G5_docs_runbooks/`;  
  - ata/resumo do ORR citando docs.

### 7.5 Critério de GO/NO-GO

- **GO**: todos os docs e runbooks existem e foram usados/revisados em simulações de ORR.  
- **NO-GO**: ausência de runbooks ou guias para consoles críticos.

---

## 8. Gate G6 — ORR & Bundle de Evidências da S27

### 8.1 Objetivo

Consolidar os resultados de todos os gates e cenários E2E em um **veredito estruturado** sobre a S27 e o Épico E26:
- a sprint pode ser considerada GO para merge e uso;  
- o Épico E26 pode ser considerado encerrado do ponto de vista de UI/Admin.

### 8.2 Escopo

- Execução de um ORR local e/ou remoto, como na S26, mas agora cobrindo Fontes + Ingestão + Debunker.  
- Verificação da integridade do **bundle de evidências** da S27.

### 8.3 Entradas

- Scorecards G0–G5 em `out/scorecards/S27_G*_*.json`.  
- Evidências em `out/evidence/S27_G*/`.  
- Resultados de testes E2E de S27.  
- Docs atualizados (Cap.1–Cap.6).

### 8.4 Saídas

- Scorecard ORR: `out/scorecards/S27_G6_orr_summary.json`  
  - Campos mínimos:  
    - `overall_status` ("GO" | "NO_GO" | "GO_WITH_RISKS");  
    - `gates_failed` (lista);  
    - `major_risks` (lista);  
    - `recommendations` (lista).

- Documento ORR: `docs/s27_cap_5_orr_local_summary.md` (Cap.5).  
- Bundle de evidências: `out/bundles/inspectah_s27_evidence_bundle.zip`.

### 8.5 Critério de GO/NO-GO

- **GO**:  
  - `overall_status == "GO"`, sem gates críticos falhando (G1, G2, G3, G5) e sem riscos inaceitáveis.  
- **GO_WITH_RISKS**:  
  - `overall_status == "GO_WITH_RISKS"`, com riscos claramente mapeados em Cap.6 e plano de tratamento.  
- **NO-GO**:  
  - `overall_status == "NO_GO"` ou qualquer gate crítico falhando de forma não mitigada.

---

## 9. Métricas agregadas e scorecards da S27

### 9.1 Métricas foco

Algumas métricas para leitura rápida da saúde da S27 do ponto de vista de Admin v1:

- **Cobertura de uso de Admin v1 nos consoles alvo**:  
  - % de componentes de layout oriundos de `ui/admin` vs ad-hoc.  
- **Pass rate de fluxos E2E Admin** (G2):  
  - `N_ok / N_total` de cenários que cruzam Fontes, Ingestão e Debunker.  
- **Presença e uso de runbooks em ORR**:  
  - runbooks existentes vs usados em simulações;  
  - número de ajustes feitos após primeira rodada de ORR.

### 9.2 Scorecard agregador (opcional)

Opcionalmente, a S27 pode introduzir um scorecard agregador de Admin v1:

- Arquivo: `out/scorecards/S27_admin_v1_overview.json`  
  - Campos:  
    - `admin_v1_coverage_score` (0–100);  
    - `e2e_flows_pass_rate` (0–100);  
    - `docs_runbooks_score` (0–100);  
    - `overall_admin_health` ("green" | "yellow" | "red").

Esse scorecard pode ser derivado dos G1, G2, G3, G5.

---

## 10. Integração com Cap.1, Cap.3 e Cap.4

- **Cap.1**: define problema, estados-alvo e escopo. Cada gate deve ser traçável a pelo menos um estado-alvo do Bloco 3.  
- **Cap.3**: detalhará a arquitetura/filemap de `ui/admin` e dos consoles, incluindo a localização dos scripts de gates.  
- **Cap.4**: quebrará os gates em tasks explícitas (S27-T-XXX) e ligará cada task a evidências esperadas.

Cap.2 é, portanto, a "cerca elétrica" da S27: se algo não passa pelos gates ou não gera scorecard/evidência, não existe do ponto de vista de DONE da sprint.

