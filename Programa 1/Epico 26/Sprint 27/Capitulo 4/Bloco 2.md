# Inspectah — Sprint 27 (S27)
## Capítulo 4 — Bloco 2
### Plano de Evidências & Logs

> Arquivo-alvo no repo: `docs/s27_cap_4_2_plano_de_evidencias_e_logs.md`
>
> Função: definir **que evidências** a S27 precisa produzir, **onde** elas devem ser armazenadas e **como** se relacionam com gates, waves e ORR. Este bloco é o contrato de rastreabilidade da sprint: sem o que está aqui, não existe DONE.

---

## 1. Princípios de evidência da S27

A S27 segue os princípios gerais do Inspectah, aplicados ao contexto de Admin v1 e consoles:

1. **Sem evidência, não aconteceu**  
   - Toda conclusão relevante ("G2 está OK", "fluxo X funciona", "contrato Y está estável") precisa de artefato concreto que a suporte.

2. **Evidência precisa ser reexecutável**  
   - Sempre que possível, evidências derivam de scripts (`bin/s27_g*_*.sh`) que possam ser rodados novamente e produzam resultados consistentes.

3. **Organização previsível**  
   - Evidências seguem um filemap padrão: scorecards em `out/scorecards/`, logs em `out/evidence/`, bundle em `out/bundles/`, docs em `docs/`.

4. **Foco no que importa para decisão**  
   - A S27 prioriza evidências que realmente influenciam o veredito de ORR sobre o Épico E26 (Admin v1 em Fontes/Ingestão/Debunker). Não é colecionar logs por fetiche, é coletar o que sustenta decisões.

---

## 2. Tipos de evidência na S27

A S27 trabalha com cinco tipos principais de evidência:

1) **Scorecards de gates (JSON)**  
   - Arquivos gerados por scripts de G0–G6, contendo campos objetivos (`*_ok`, contagens, listas de mismatches, etc.).

2) **Logs de execução (texto)**  
   - Saída de scripts, testes e builds (stdout/stderr), armazenada em subpastas de `out/evidence/` por gate.

3) **Evidência visual (opcional, mas recomendada)**  
   - Capturas de tela das principais telas admin, fluxos E2E e estados relevantes, armazenadas em paths previsíveis.

4) **Documentos de apoio (Markdown)**  
   - Capítulos da S27, guia Admin v1.1, runbooks de operação e notas de ORR.

5) **Bundle consolidado**  
   - Arquivo `.zip` contendo scorecards, evidências e subconjunto de docs-chave, gerado ao final da sprint.

Cada tipo tem caminhos e regras específicas descritas abaixo.

---

## 3. Estrutura padrão de evidências em disco

### 3.1 Scorecards

- Diretório raiz:
  - `out/scorecards/`

- Arquivos da S27:
  - `out/scorecards/S27_G0_scope_and_env.json`  
  - `out/scorecards/S27_G1_admin_design_system.json`  
  - `out/scorecards/S27_G2_admin_flows.json`  
  - `out/scorecards/S27_G3_front_quality_admin.json`  
  - `out/scorecards/S27_G4_admin_contracts.json`  
  - `out/scorecards/S27_G5_docs_runbooks.json`  
  - `out/scorecards/S27_G6_orr_summary.json`

Cada script `bin/s27_g*_*.sh` é responsável por criar ou atualizar seu scorecard correspondente.

### 3.2 Evidências (logs, artefatos derivados)

- Diretório raiz:
  - `out/evidence/`

- Subpastas por gate:
  - `out/evidence/S27_G0_env_repo/`  
  - `out/evidence/S27_G1_admin_design_system/`  
  - `out/evidence/S27_G2_admin_flows/`  
  - `out/evidence/S27_G3_front_quality_admin/`  
  - `out/evidence/S27_G4_admin_contracts/`  
  - `out/evidence/S27_G5_docs_runbooks/`  
  - `out/evidence/S27_G6_orr/`

Dentro de cada subpasta, recomenda-se:

- arquivos `.log` para stdout/stderr (ex.: `lint.log`, `tests.log`, `build.log`, `contracts.log`);  
- arquivos `.json` adicionais quando scripts gerarem relatórios mais ricos;  
- eventualmente `.html` (ex.: relatórios de testes, se existirem), desde que versionados corretamente.

### 3.3 Evidência visual (screenshots)

Caso a equipe queira documentar estados específicos da UI Admin (recomendado para ORR e Cap.6):

- Diretório sugerido:
  - `docs/screenshots/s27_admin/`

Nomes de arquivo sugeridos:

- `s27_admin_fontes_list.png`  
- `s27_admin_fontes_detail.png`  
- `s27_admin_ingestao_overview.png`  
- `s27_admin_debunker_case_detail.png`  
- `s27_admin_flow_fontes_ingestao_debunker.png`

Essas imagens podem ser referenciadas em Cap.5 (ORR) e Cap.6 (learnings), mas não são obrigatórias para os gates.

### 3.4 Documentos de apoio

- Diretório: `docs/`

- Arquivos principais da S27:
  - `docs/s27_cap_1_*.md`  
  - `docs/s27_cap_2_*.md`  
  - `docs/s27_cap_3_*.md`  
  - `docs/s27_cap_4_*.md`  
  - `docs/s27_cap_5_orr_local_summary.md`  
  - `docs/s27_cap_6_learnings_dividas_roadmap.md`  
  - `docs/guia_consoles_admin_v1_1.md`  
  - `docs/runbook_operacao_fontes_vX.md`  
  - `docs/runbook_operacao_ingestao_vX.md`  
  - `docs/runbook_operacao_debunker_vX.md`

G5 se apoia diretamente nesses últimos quatro.

### 3.5 Bundle consolidado

- Diretório de bundles:
  - `out/bundles/`

- Arquivo da S27:
  - `out/bundles/inspectah_s27_evidence_bundle.zip`

Gerado por `bin/s27_g6_orr_bundle.sh`.

---

## 4. Evidências por gate (G0–G6)

### 4.1 G0 — Escopo, Grounding & Sanidade de Ambiente

- Scorecard:  
  - `out/scorecards/S27_G0_scope_and_env.json`

- Evidências mínimas:
  - `out/evidence/S27_G0_env_repo/env_check.log` — resultado dos comandos de sanity (git, venv, py_compile, etc.).  
  - `out/evidence/S27_G0_env_repo/docs_presence.log` — verificação da presença de docs Cap.1/Cap.2/Cap.3.

### 4.2 G1 — Admin Design System (Tokens & Componentes)

- Scorecard:  
  - `out/scorecards/S27_G1_admin_design_system.json`

- Evidências mínimas:
  - `out/evidence/S27_G1_admin_design_system/design_build.log` — build/tests específicos de `ui/admin`.  
  - `out/evidence/S27_G1_admin_design_system/imports_scan.log` — resultado da varredura de imports em `features/sources`, `features/ingestion`, `features/debunker`.

### 4.3 G2 — Fluxos de Consoles Admin

- Scorecard:  
  - `out/scorecards/S27_G2_admin_flows.json`

- Evidências mínimas:
  - `out/evidence/S27_G2_admin_flows/e2e_results.log` — saída do runner de testes E2E (Playwright/Cypress/etc.).  
  - `out/evidence/S27_G2_admin_flows/scenarios.json` — lista de cenários executados e seu status (opcional, mas recomendado).

Evidência visual opcional:

- screenshots dos principais cenários em `docs/screenshots/s27_admin/`.

### 4.4 G3 — Qualidade de Frontend Admin

- Scorecard:  
  - `out/scorecards/S27_G3_front_quality_admin.json`

- Evidências mínimas:
  - `out/evidence/S27_G3_front_quality_admin/lint.log`  
  - `out/evidence/S27_G3_front_quality_admin/tests.log`  
  - `out/evidence/S27_G3_front_quality_admin/build.log`

### 4.5 G4 — Contratos & APIs

- Scorecard:  
  - `out/scorecards/S27_G4_admin_contracts.json`

- Evidências mínimas:
  - `out/evidence/S27_G4_admin_contracts/contracts_tests.log` — saída dos testes de contrato.  
  - `out/evidence/S27_G4_admin_contracts/schema_validation.log` — saída da validação de schemas (OpenAPI/JSON Schema), se houver.

### 4.6 G5 — Documentação & Runbooks

- Scorecard:  
  - `out/scorecards/S27_G5_docs_runbooks.json`

- Evidências mínimas:
  - `out/evidence/S27_G5_docs_runbooks/presence_check.log` — checagem de existência dos docs/runbooks.  
  - `out/evidence/S27_G5_docs_runbooks/structure_check.log` — validação de headings obrigatórios.  
  - registro em `docs/s27_cap_5_orr_local_summary.md` de que runbooks foram usados em simulações.

### 4.7 G6 — ORR & Bundle de Evidências

- Scorecard:  
  - `out/scorecards/S27_G6_orr_summary.json`

- Evidências mínimas:
  - `out/evidence/S27_G6_orr/orr_session.log` — notas ou transcrição resumida da sessão de ORR.  
  - `out/evidence/S27_G6_orr/gates_overview.json` — snapshot agregando o status de G0–G5 no momento do ORR (pode ser gerado pelo script).  
  - bundle `out/bundles/inspectah_s27_evidence_bundle.zip` contendo scorecards + evidências principais + subset de docs.

---

## 5. Evidências por wave (W0–W3)

### 5.1 W0 — Groundwork

Evidências mínimas:

- Scorecard G0 inicial.  
- Logs básicos de sanidade (env_check, docs_presence).  
- Nota breve (pode ser anexada a Cap.4 ou Cap.6) sobre estado inicial de Admin v1 + consoles.

### 5.2 W1 — Núcleo Admin v1

Evidências mínimas:

- Scorecards iniciais de G1, G2 (mínimo de cenários) e G3.  
- Logs de execução dos scripts correspondentes.  
- Se possível, primeira leva de screenshots das telas principais já sob Admin v1.

### 5.3 W2 — Refinos & Operação

Evidências mínimas:

- Scorecards atualizados de G2, G3, G4, G5.  
- Logs de testes E2E ampliados, contratos e validação de docs.  
- Guia Admin v1.1 e runbooks presentes e referenciados em Cap.5/Cap.6.  
- Evidências de que runbooks foram utilizados em simulações (podem ser notas no ORR ou em Cap.6).

### 5.4 W3 — Hardening & ORR

Evidências mínimas:

- Scorecards finais de G0–G6.  
- Logs finais em `out/evidence/S27_G*/`.  
- Bundle zip gerado.  
- Documento de ORR preenchido com decisão e riscos.  
- Atualização em Cap.6 alinhando learnings/dívidas ao que as evidências mostram.

---

## 6. Boas práticas de logs e ruído

Para evitar uma pasta `out/` inservível, a S27 recomenda:

1. Logs focados  
   - Não despejar builds completos de horas se não houver necessidade; manter logs suficientes para diagnosticar falhas.

2. Rotação mínima (manual)  
   - Em caso de múltiplas execuções do mesmo gate, pode-se numerar logs (`lint_1.log`, `lint_2.log`) ou sobrescrever, desde que o estado final seja representado.

3. Comentários claros em scorecards  
   - O campo `notes` de cada `S27_GX_*.json` deve ser usado para apontar decisões, exceções e detalhes relevantes.

4. Alinhamento com ORR  
   - Durante o ORR, se surgir uma dúvida, a equipe deve ser capaz de apontar exatamente qual log e qual scorecard respondem à questão.

---

## 7. Como este plano alimenta Cap.5 e Cap.6

- **Cap.5 (ORR)** usa diretamente:
  - scorecards G0–G6,  
  - logs chave de cada gate,  
  - screenshots de consoles admin,  
  - guia Admin v1.1 e runbooks.

- **Cap.6 (Learnings & Dívidas)** usa:
  - scorecards (especialmente campos de `notes`, `schema_mismatches`, `gates_with_ressalvas`),  
  - ORR summary,  
  - evidências de falhas/flakiness em logs,  
  - gaps em docs/runbooks.

Com este Bloco 4.2, a S27 passa a ter um plano de evidência que amarra execução, verificação e aprendizado: toda decisão importante ficará encostada em um rastro claro em `out/`, `docs/` e no bundle final da sprint.

