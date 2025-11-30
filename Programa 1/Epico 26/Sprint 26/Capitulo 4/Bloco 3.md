# Inspectah — Sprint 26 (S26)
## Capítulo 4 — Bloco 4.3
### Plano de Evidências & ORR Local da S26

> Arquivo-alvo no repo: `docs/s26_cap_4_3_plano_de_evidencias.md`
>
> Função: definir **como as evidências da S26 são coletadas, organizadas e usadas no ORR local**, mapeando explicitamente `gate → evidência esperada → paths concretos`. Este bloco complementa:
> - Cap.2 (definição de gates, scorecards e DoD);
> - Cap.3 (filemap e arquitetura);
> - Bloco 4.1 (waves) e Bloco 4.2 (estratégia de dev/CI).

Regra de ouro: **nenhuma afirmação de “S26 está GO” é aceita sem evidência rastreável em `out/evidence/` + scorecards em `out/scorecards/` + bundle em `out/bundles/`.**

---

## 1. Mapa consolidado `Gate → Evidências → Paths`

A tabela abaixo resume, para cada gate S26, **onde** as evidências vivem e **o que minimamente precisa existir** para que o ORR local considere o gate auditável.

### 1.1 G0 — Scope & Baseline

- Script: `bin/s26_g0_scope_and_baseline.sh`
- Scorecard: `out/scorecards/S26_G0_scope_and_baseline.json`
- Pasta de evidências: `out/evidence/S26_G0_scope_and_baseline/`
- Conteúdo mínimo esperado:
  - logs da execução do script (stdout/stderr redirecionados, ex.: `g0_scope_and_baseline.log`);
  - listagens de estrutura (ex.: `ls -R docs/`, `ls -R frontend/inspectah-ui/src/ui/admin/`, `ls -R frontend/inspectah-ui/src/features/sources/`), mostrando a presença dos arquivos de Cap.1–4 e dos diretórios de design system/console de fontes;
  - opcionalmente, extratos dos cabeçalhos dos docs principais (Cap.1–4), apenas para confirmar que não são arquivos vazios.

### 1.2 G1 — Design System Admin v1 (Static Integrity)

- Script: `bin/s26_g1_design_system_static.sh`
- Scorecard: `out/scorecards/S26_G1_design_system_static.json`
- Pasta de evidências: `out/evidence/S26_G1_design_system_static/`
- Conteúdo mínimo esperado:
  - logs de TypeScript compile e lint focados em `frontend/inspectah-ui/src/ui/admin/` (por exemplo, `g1_ts_compile.log`, `g1_lint.log`);
  - logs de testes de componentes do design system (ex.: `g1_ds_components_tests.log`);
  - snapshot de cobertura dos testes de componentes, se disponível (ex.: `g1_coverage_summary.txt`);
  - opcionalmente, um pequeno índice de componentes do design system gerado por script (ex.: `g1_components_index.txt` listando arquivos-chave).

### 1.3 G2 — Console de Fontes v2 (Fluxos Básicos)

- Script: `bin/s26_g2_sources_console_flows.sh`
- Scorecard: `out/scorecards/S26_G2_sources_console_flows.json`
- Pasta de evidências: `out/evidence/S26_G2_sources_console_flows/`
- Conteúdo mínimo esperado:
  - logs da suíte de testes (unit/integration/e2e) aplicada ao Console de Fontes v2 (ex.: `g2_sources_flows_tests.log`);
  - se houver e2e visual, capturas de tela ou snapshots de DOM para os fluxos principais:
    - listagem de fontes;
    - criação de fonte válida;
    - edição de fonte;
    - ativar/desativar/arquivar;
  - um pequeno arquivo índice (`g2_flows_index.md`) listando quais cenários foram cobertos (ex.: `FLOW-01 list_sources`, `FLOW-02 create_source_valid`, etc.).

### 1.4 G3 — Front-End Quality & Regression

- Script: `bin/s26_g3_frontend_quality.sh`
- Scorecard: `out/scorecards/S26_G3_frontend_quality.json`
- Pasta de evidências: `out/evidence/S26_G3_frontend_quality/`
- Conteúdo mínimo esperado:
  - logs de `npm ci` (ou comando equivalente acordado) — `g3_npm_ci.log`;
  - logs de lint do frontend completo — `g3_frontend_lint.log`;
  - logs de testes globais de frontend — `g3_frontend_tests.log`;
  - logs do build de produção — `g3_frontend_build.log`;
  - se houver, resumo de cobertura global do frontend — `g3_frontend_coverage_summary.txt`.

### 1.5 G4 — API & Modelo de Dados de Fontes (Contratos)

- Script: `bin/s26_g4_sources_api_contracts.sh`
- Scorecard: `out/scorecards/S26_G4_sources_api_contracts.json`
- Pasta de evidências: `out/evidence/S26_G4_sources_api_contracts/`
- Conteúdo mínimo esperado:
  - logs da execução de `pytest tests/api/test_sources_console.py` (ou nome final equivalente) — `g4_sources_api_tests.log`;
  - dumps controlados de requests/responses relevantes (anonimizados quando necessário), ex.: `g4_request_create_source.json`, `g4_response_create_source.json`;
  - se houver validação de schema/OpenAPI, relatórios compactos desses checks — `g4_openapi_validation.log`.

### 1.6 G5 — Documentação & Runbooks S26

- Script: `bin/s26_g5_docs_and_runbooks.sh`
- Scorecard: `out/scorecards/S26_G5_docs_and_runbooks.json`
- Pasta de evidências: `out/evidence/S26_G5_docs_and_runbooks/`
- Conteúdo mínimo esperado:
  - logs do script de verificação de docs (existência, tamanho mínimo, seções obrigatórias) — `g5_docs_check.log`;
  - resultados de `wc -l` ou equivalente para:
    - `docs/design_system_admin_v1.md`;
    - `docs/runbook_operacao_fontes_v1.md`;
  - opcionalmente, exports em PDF/HTML dos docs principais, ex.: `design_system_admin_v1.pdf`, `runbook_operacao_fontes_v1.pdf` (apenas como cópia de leitura rápida, sem substituir os `.md`).

### 1.7 G6 — Evidence & ORR Bundle S26

- Script: `bin/s26_g6_orr_bundle.sh`
- Scorecard: `out/scorecards/S26_G6_orr_bundle.json`
- Pasta de evidências: `out/evidence/S26_G6_orr_bundle/`
- Bundle: `out/bundles/inspectah_s26_evidence_bundle.zip`
- Conteúdo mínimo esperado:
  - log de execução do script de bundle — `g6_bundle_creation.log`;
  - listagem dos arquivos/diretórios incluídos no ZIP (ex.: `g6_bundle_contents.txt`, produzido via `unzip -l` ou `zipinfo`);
  - hash do bundle (ex.: `g6_bundle_sha256.txt`), contendo o SHA256 de `inspectah_s26_evidence_bundle.zip`.

---

## 2. Plano de Coleta de Evidências por Wave

A coleta de evidências não acontece só no fim da sprint; ela é distribuída pelas waves, alinhada ao progresso de código.

### 2.1 W0 — Grounding & Sanidade

- Evidências principais:
  - notas de grounding (podem ser registradas em `docs/s26_cap_0_notas_de_grounding.md` ou similar, fora do escopo direto de gates mas úteis para ORR);
  - se G0 já for executado em W0, guardar o log inicial em `out/evidence/S26_G0_scope_and_baseline/` (mesmo que G0 ainda não esteja totalmente green).
- Meta: evidências de W0 ajudam o ORR a entender **como a sprint começou** (estado inicial do repo, dúvidas levantadas, riscos conhecidos).

### 2.2 W1 — Fundação de Design System & Filemap

- Evidências principais:
  - primeira execução significativa de G0, G1 e G3 com a nova estrutura de `ui/admin` e `features/sources`;
  - logs de criação/ajuste de filemap (ex.: listagens `ls -R` antes/depois, se relevante, em `S26_G0...` e `S26_G1...`).
- Meta: provar que o filemap e a fundação do design system/console **existem e são compiláveis**, mesmo que ainda sem todos os fluxos prontos.

### 2.3 W2 — Console de Fontes v2 & Contratos de Fontes

- Evidências principais:
  - execuções verdes de G2 (fluxos do console) e G4 (contratos de API);
  - logs de testes de UI/API cobrindo caminho feliz dos fluxos básicos de fontes;
  - eventuais gravações curtas (GIF/MP4 leve) demonstrando uso real do Console de Fontes v2 em ambiente de dev (guardados em `S26_G2_sources_console_flows/`, se o tamanho for razoável).
- Meta: provar que **existe operação ponta a ponta de fontes via console**, sustentada por contratos de backend sólidos.

### 2.4 W3 — Hardening, UX mínima & Evidências finais

- Evidências principais:
  - execuções finais verdes de G0–G6, com scorecards atualizados;
  - versão final dos docs (guia do design system e runbook de fontes) + logs de verificação de G5;
  - bundle final de evidências S26 (G6), com hash registrado.
- Meta: fechar a sprint com um **pacote auditável**, capaz de sustentar ORR local e futuras revisões de Programa 1.

---

## 3. Regras de Coleta, Nomeação & Qualidade de Evidências

Para evitar evidências inúteis ou caóticas, a S26 adota as seguintes regras:

1. As saídas de scripts de gates (`bin/s26_g*.sh`) devem ser sempre redirecionadas para arquivos de log dentro da pasta de evidência correspondente (ex.: `g2_sources_flows_tests.log`).
2. Logs muito verbosos podem ser comprimidos (`.gz`) se necessário, desde que haja um `README.md` na pasta explicando como visualizar.
3. Capturas de tela e vídeos devem ser curtos e focados; a prioridade é mostrar fluxos, não criar "slides" de marketing.
4. Dados sensíveis reais **não** devem aparecer nas evidências. Sempre que possível, usar seeds de teste ou anonimização.
5. Qualquer evidência manual (por exemplo, notas de validação de UX) deve ser salva como `.md` ou `.txt` na pasta de evidência mais relacionada, com data e autor (ex.: `ux_notes_2025-11-29.md`).

---

## 4. ORR Local da Sprint 26

O ORR local da S26 é o ritual que, ao final da sprint (ou em milestones internos), verifica se o pacote de evidências sustenta um veredito de GO/NO-GO.

### 4.1 Pré-requisitos para ORR local

Antes de iniciar o ORR local, deve ser verdade que:

1. Todos os scripts `bin/s26_g0_*.sh` a `bin/s26_g6_*.sh` existem e rodam localmente.
2. Todos os scorecards `out/scorecards/S26_G*.json` existem (mesmo que algum gate ainda esteja NO-GO).  
3. A estrutura básica de `out/evidence/S26_G*/` existe, mesmo que parcialmente preenchida.

### 4.2 Passos recomendados para ORR local

1. Rodar, em sequência, os gates S26 a partir da branch de release:

```bash
bin/s26_g0_scope_and_baseline.sh
bin/s26_g1_design_system_static.sh
bin/s26_g2_sources_console_flows.sh
bin/s26_g3_frontend_quality.sh
bin/s26_g4_sources_api_contracts.sh
bin/s26_g5_docs_and_runbooks.sh
bin/s26_g6_orr_bundle.sh
```

2. Verificar todos os scorecards `S26_G*.json`, confirmando que os campos críticos respeitam os thresholds de GO definidos em Cap.2.
3. Abrir o bundle `inspectah_s26_evidence_bundle.zip` e conferir, amostralmente, se os logs e artefatos listados neste Bloco 4.3 de fato existem e correspondem ao que é alegado.
4. Registrar o resultado do ORR local (GO/NO-GO, com justificativa) em um doc próprio, por exemplo:

- `docs/s26_cap_5_orr_local_summary.md` (a ser detalhado no Cap.5).

### 4.3 Critério de GO/NO-GO no ORR local

- **GO S26**: todos os gates G0–G6 em estado GREEN, evidências mínimas presentes conforme mapeado neste bloco, bundle gerado e verificado, docs/runbooks utilizáveis.  
- **NO-GO S26**: qualquer gate em estado FAIL ou ausência de evidências mínimas; neste caso, registrar gaps e plano de correção em Cap.6.

---

## 5. Ligação entre Tasks, Gates e Evidências

O Bloco 4.4 (Tasks & Checklists) deve seguir a regra:

- **toda task crítica (`S26-T-XXX`) aponta para pelo menos uma evidência** direta ou indireta.

Para cada task, o campo `artefatos` deve incluir, sempre que fizer sentido:

- paths de código (ex.: `frontend/inspectah-ui/src/ui/admin/components/Button.tsx`);
- scripts/gates associados (ex.: `bin/s26_g1_design_system_static.sh`);
- pasta de evidência principal (ex.: `out/evidence/S26_G1_design_system_static/`).

Isso garante que, durante o ORR, seja possível traçar a linha:

> "Task S26-T-012 → mexeu em X/Y/Z → rodou gates A/B → gerou evidências em `out/evidence/S26_G*` → está coberta no bundle."

---

## 6. Síntese do Bloco 4.3

O Bloco 4.3 transforma o conceito de evidência da S26 em um **plano operacional**:

- define, gate a gate, quais artefatos são esperados e onde vivem;  
- distribui a coleta de evidências ao longo das waves W0–W3;  
- estabelece regras de qualidade e organização de logs, prints e bundles;  
- descreve como conduzir um ORR local honesto para a sprint;  
- exige que tasks críticas apontem explicitamente para evidências.

Com isso, a S26 deixa de depender de memória oral ou "confiança" e passa a ser julgada por um pacote de evidências claro, reprodutível e auditável.

