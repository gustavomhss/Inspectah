# Inspectah — Sprint 26 (S26)
## Capítulo 2 — Bloco 2.3
### Mapa de Evidências da Sprint 26

Este bloco define o **mapa oficial de evidências** da Sprint 26. Ele responde a três perguntas:

1. **Onde** ficam as evidências de cada gate?  
2. **Que tipo de artefato** é esperado em cada pasta de evidência?  
3. **Como** essas evidências se conectam ao ORR e ao Programa 1?

A regra é simples: qualquer evidência relevante para gates da S26 deve estar dentro dessa estrutura. Evidências “espalhadas” fora desse mapa não fazem parte do contrato oficial da sprint.

---

## 1. Estrutura de Diretórios de Evidência da S26

Todas as evidências da S26 ficam em subpastas de `out/evidence/` e em um bundle final em `out/bundles/`.

### 1.1. G0 — Scope & Baseline

- **Path:** `out/evidence/S26_G0_scope_and_baseline/`
- **Conteúdo esperado:**
  - logs da execução de `bin/s26_g0_scope_and_baseline.sh` (stdout/stderr redirecionados para arquivos de log);  
  - snapshots simples (por exemplo, `ls -R` em `docs/` e `frontend/inspectah-ui/src/ui/admin/`) que demonstrem a existência dos principais arquivos e diretórios;  
  - opcionalmente, cópias ou extratos dos cabeçalhos dos docs de Cap.1–4, apenas o suficiente para comprovar que existem e não estão vazios.

### 1.2. G1 — Design System Admin v1 (Static Integrity)

- **Path:** `out/evidence/S26_G1_design_system_static/`
- **Conteúdo esperado:**
  - logs de TypeScript compile e lint executados no diretório do design system;  
  - logs de testes dos componentes nucleares (unit/snapshot);  
  - se relevante, relatórios de ferramentas de cobertura de testes específicos do design system;  
  - artefatos auxiliares, como um pequeno "catálogo" estático de componentes (por exemplo, um HTML de storybook/light playground, se for gerado como parte dos testes).

### 1.3. G2 — Console de Fontes v2 (Fluxos Básicos)

- **Path:** `out/evidence/S26_G2_sources_console_flows/`
- **Conteúdo esperado:**
  - logs da suíte de testes de fluxo (unit/integration/e2e) do Console de Fontes v2;  
  - screenshots (ou gravações curtas em formato leve) ilustrando os principais fluxos: listagem, criação, edição, ativar/desativar/arquivar;  
  - se for usado teste e2e, relatórios de execução (por exemplo, resumo de Playwright/Cypress) com status dos cenários.

### 1.4. G3 — Front-End Quality & Regression

- **Path:** `out/evidence/S26_G3_frontend_quality/`
- **Conteúdo esperado:**
  - logs de `npm ci` (ou comando equivalente firmado no Cap.4);  
  - logs da execução de linters do frontend completo;  
  - logs da suíte de testes global de frontend;  
  - logs do build de produção do frontend;  
  - opcionalmente, relatórios de cobertura globais do frontend, se já forem gerados pelo pipeline.

### 1.5. G4 — API & Modelo de Dados de Fontes (Contratos)

- **Path:** `out/evidence/S26_G4_sources_api_contracts/`
- **Conteúdo esperado:**
  - logs dos testes de API específicos de fontes (ex.: pytest em `tests/api/test_sources_console.py` ou nome equivalente);  
  - dumps controlados de requests/responses relevantes, com dados sensíveis removidos ou anonimizados;  
  - se houver, relatórios de ferramentas de contrato de API (ex.: schemas gerados, validação de OpenAPI), desde que sejam pequenos e úteis.

### 1.6. G5 — Documentação & Runbooks S26

- **Path:** `out/evidence/S26_G5_docs_and_runbooks/`
- **Conteúdo esperado:**
  - logs da execução do script que verifica presença e tamanho mínimo dos docs (guia do Design System Admin v1 e runbook de operação de fontes);  
  - contagem de linhas dos arquivos de documentação (saída de `wc -l` ou script equivalente);  
  - opcionalmente, exports em PDF/HTML dos docs principais para facilitar leitura no ORR, desde que não substituam os arquivos-fonte em `docs/`.

### 1.7. G6 — Evidence & ORR Bundle S26

- **Path:** `out/evidence/S26_G6_orr_bundle/`
- **Conteúdo esperado:**
  - log de execução de `bin/s26_g6_orr_bundle.sh`;  
  - listagem dos arquivos e diretórios incluídos no bundle (ex.: saída de `zipinfo` ou `unzip -l`);  
  - hash (por exemplo SHA256) do arquivo `inspectah_s26_evidence_bundle.zip` para fins de auditabilidade básica.

---

## 2. Bundle de Evidências da S26

Além das pastas em `out/evidence/`, a S26 deve produzir um **bundle único**:

- **Arquivo:** `out/bundles/inspectah_s26_evidence_bundle.zip`

Esse bundle deve conter, no mínimo:

1. Todas as pastas `out/evidence/S26_G*/` (G0 a G6).  
2. Todos os scorecards relevantes em `out/scorecards/S26_G*.json`.  
3. Opcionalmente, uma cópia dos docs-chave da sprint (Cap.1–4, guia de design system, runbook de fontes), para consumo rápido pelo ORR, desde que isso não crie divergência em relação à fonte da verdade em `docs/`.

O script de bundle (G6) é responsável por montar esse ZIP e escrever, no scorecard de G6:

- lista de diretórios incluídos;  
- tamanho em bytes do bundle;  
- hash do arquivo, se calculado.

---

## 3. Evidência Cruzada com o Programa 1

Certos artefatos de evidência da S26 não servem apenas para esta sprint; eles são **sementes para os gates globais do Programa 1** (por exemplo, G-P1.1 Operação via consoles, G-P1.3 Audit trail transversal).

Recomenda-se marcar explicitamente, nos nomes dos arquivos ou em um pequeno índice, os artefatos que têm relevância além da S26, por exemplo:

- `out/evidence/S26_G5_docs_and_runbooks/design_system_admin_v1_guide_P1.md`  
- `out/evidence/S26_G5_docs_and_runbooks/runbook_fontes_v1_P1.md`  
- `out/evidence/S26_G2_sources_console_flows/demo_fluxos_fontes_P1.mp4`

Esses artefatos podem ser citados futuramente nos capítulos de Programa 1 como evidência de que:

- existe operação via consoles para fontes;  
- existe documentação de como usar o Design System Admin v1;  
- os fluxos de fontes foram demonstrados e capturados em registros visuais.

---

## 4. Regras de Organização & Boas Práticas

Para manter o mapa de evidências útil e sustentável:

1. **Nada de evidências soltas na raiz do repositório** — tudo que for resultado de scripts de gates deve ir para `out/evidence/` ou `out/bundles/`.
2. **Arquivos grandes e brutos (vídeos longos, logs gigantes)** devem ser evitados; priorizar recortes relevantes e comprimidos.
3. **Nomear arquivos de forma descritiva** dentro de cada pasta de evidência (por exemplo, `g2_create_source_success.log`, `g2_create_source_validation_error.log`, etc.).
4. **Evitar dados sensíveis** nas evidências; quando necessário, anonimizar exemplos ou usar ambientes/seeds de teste.

---

### Síntese do Bloco 2.3

O Bloco 2.3 define o “mapa do tesouro” de S26: qualquer pessoa, ao olhar `out/evidence/` e o bundle da sprint, deve conseguir entender **o que foi testado, validado e documentado** sem depender da memória do time. Isso é pré-requisito para um ORR honesto e para o Programa 1 conseguir, no futuro, provar que a operação via consoles e a auditabilidade prometidas realmente existem na prática.