# Sprint 5 — Capítulo 3 (v2)
## Filemap + Plano de Execução da S5 (Inspectah Data Hub Core)

> v2 — Versão 15/10. Este capítulo é o plano operacional definitivo da Sprint 5: filemap, gates × artefatos, DoD por eixo, estratégia de branches/PR, plano de CI e análise de risco/rollback. Ele foi escrito para o Codex e para o time humano conseguirem executar S5 sem ambiguidade.

---

## 0. Papel do Capítulo 3

- Capítulo 1: define **o que** o Inspectah precisa ser ao final de S5 (modelo de estados, claims, invariantes, métricas).
- Capítulo 2: define **como** a sprint será julgada (gates G0–G7, scripts, scorecards, PASS/FAIL).
- Capítulo 3 (este): define **o que criar/alterar, onde e em que ordem**, para que o código encaixe nos Cap. 1 e 2.

Se código, testes, scripts e docs seguirem este capítulo, a sprint tende a passar por todos os gates sem improviso.

---

## 1. Filemap global da Sprint 5

### 1.1 Documentação

- `docs/sprint_5/`
  - `s5_capitulo_1_core_v6.md` — contrato conceitual (Cap. 1).
  - `s5_capitulo_2_gates_v2.md` — contrato de gates (Cap. 2).
  - `s5_capitulo_3_filemap_plano_v2.md` — este capítulo.
  - `s5_contracts_overview.md` — pré/pós-condições por componente.
  - `s5_wrap_exec.md` — wrap executivo final da sprint.

- `docs/sprint_5/gates/`
  - `G0_spec_lock_checklist.md`
  - `G1_schema_contracts_checklist.md`
  - `G2_components_checklist.md`
  - `G3_pipeline_fixtures_checklist.md`
  - `G4_ai_integration_checklist.md`
  - `G5_operator_journey_checklist.md`
  - `G6_observability_checklist.md`
  - `G7_stability_checklist.md`
  - `G5_operator_scenario.md` — roteiro detalhado do operador.

### 1.2 Código central do Inspectah

- `inspectah/`
  - `__init__.py`
  - `config/`
    - `sources_registry.yaml` — registry de fontes.
    - `ai_gpt_4_1mini.yaml` — config do client de IA (sem segredos).
  - `models/`
    - `item.py` — estrutura do Item Inspectah (S0–S4).
    - `claim.py` — estrutura de Claim v0.1.
  - `equivalence_key.py` — função determinística de equivalence_key.
  - `watchers/`
    - `engine.py`
    - `rss_watcher.py`
    - `api_watcher.py`
    - `html_watcher.py`
  - `evidence/`
    - `builder.py`
    - `verifier.py`
  - `normalizer/`
    - `client_ai.py`
    - `normalizer.py`
  - `indexer/`
    - `indexer.py`
    - `query_api.py`
  - `ui/`
    - `admin_sources.py`
    - `explore.py`

### 1.3 Schemas, fixtures e golden data

- `schemas/`
  - `inspectah_item_v0_1.json`
  - `inspectah_claim_v0_1.json`

- `fixtures/s5/`
  - `rss_example_*.xml`
  - `api_example_*.json`
  - `html_example_*.html`
  - `real_texts/` — textos reais para G4.

- `tests/golden/`
  - `item_normalized_*.json` — golden data para G3.

### 1.4 Testes

- `tests/`
  - `test_schema_item.py`
  - `test_schema_claim.py`
  - `test_equivalence_key.py`
  - `components/`
    - `test_watchers_engine.py`
    - `test_evidence_builder.py`
    - `test_evidence_verifier.py`
    - `test_normalizer_stub.py`
    - `test_indexer.py`
  - `pipeline/`
    - `test_pipeline_fixtures.py`

### 1.5 Gates, scripts, outputs e observabilidade

- `bin/`
  - `s5_gate_g0_spec_lock.sh`
  - `s5_gate_g1_schema_contracts.sh`
  - `s5_gate_g2_components.sh`
  - `s5_gate_g3_pipeline_fixtures.sh`
  - `s5_gate_g4_ai_integration.sh`
  - `s5_gate_g5_operator_journey.sh`
  - `s5_gate_g6_observability.sh`
  - `s5_gate_g7_stability_go_no_go.sh`
  - `s5_check_invariants.sh`

- `out/s5_gates/` (somente gerado)
  - `G*/scorecard.json` + demais arquivos descritos no Cap. 2.

- `dashboards/`
  - `s5_inspectah_core.json`

---

## 2. Tabela Gate × Artefatos

Mapa de dependências entre gates (Cap. 2) e artefatos (Cap. 3).

| Gate | Script oficial                           | Artefatos necessários principais                                                                 |
|------|------------------------------------------|---------------------------------------------------------------------------------------------------|
| G0   | `bin/s5_gate_g0_spec_lock.sh`           | `docs/sprint_5/s5_capitulo_1_core_v6.md`, `docs/sprint_5/s5_capitulo_2_gates_v2.md`, Cap. 3 v2   |
| G1   | `bin/s5_gate_g1_schema_contracts.sh`    | `schemas/inspectah_item_v0_1.json`, `schemas/inspectah_claim_v0_1.json`, `inspectah/equivalence_key.py`, `docs/sprint_5/s5_contracts_overview.md`, testes de schema/equivalence_key |
| G2   | `bin/s5_gate_g2_components.sh`          | `inspectah/watchers/*`, `inspectah/evidence/*`, `inspectah/normalizer/normalizer.py` (stub IA), `inspectah/indexer/indexer.py`, `tests/components/*` |
| G3   | `bin/s5_gate_g3_pipeline_fixtures.sh`   | watchers, evidence, normalizer stub, indexer, `fixtures/s5/*`, `tests/golden/*`, `bin/s5_check_invariants.sh`, `tests/pipeline/test_pipeline_fixtures.py` |
| G4   | `bin/s5_gate_g4_ai_integration.sh`      | `inspectah/normalizer/client_ai.py` (IA real), `inspectah/normalizer/normalizer.py`, `config/ai_gpt_4_1mini.yaml`, `fixtures/s5/real_texts/*` |
| G5   | `bin/s5_gate_g5_operator_journey.sh`    | `inspectah/ui/admin_sources.py`, `inspectah/ui/explore.py`, `inspectah/indexer/query_api.py`, templates de UI, `docs/sprint_5/gates/G5_operator_scenario.md` |
| G6   | `bin/s5_gate_g6_observability.sh`       | instrumentação de métricas em `inspectah/*`, endpoint de métricas, `dashboards/s5_inspectah_core.json` |
| G7   | `bin/s5_gate_g7_stability_go_no_go.sh`  | sistema rodando (tudo acima), coleta de séries temporais, scripts de replay/simulação, `docs/sprint_5/s5_wrap_exec.md` |

Esta tabela deve ser usada pelo Codex para ordenar o trabalho e verificar se um gate pode ser executado (todos os artefatos listados prontos).

---

## 3. Estratégia de branches, PRs e fluxo de trabalho

### 3.1 Convenções de branch

- Branch base da sprint: `sprint-5/inspectah-core` (ou equivalente definido no repo).
- Branches por eixo:
  - `feature/s5-eixo-a-watchers`
  - `feature/s5-eixo-b-evidence-vault`
  - `feature/s5-eixo-c-normalizer`
  - `feature/s5-eixo-d-ui-indexer`
  - `feature/s5-eixo-e-observability-gates`

Branches adicionais para ajustes finos podem seguir a convenção `chore/s5-...` ou `fix/s5-...`, sempre baseadas no branch da sprint.

### 3.2 Política de PR

- Cada eixo A–E deve ser implementado em 1 ou mais PRs pequenos e revisáveis.
- Nenhum PR pode ser mesclado sem CI verde e, quando aplicável, sem o gate correspondente em condição de PASS.
- PRs devem referenciar explicitamente:
  - o eixo (A–E),
  - o(s) gate(s) afetado(s),
  - arquivos principais alterados.

### 3.3 Ordem recomendada de branches/PRs

1. `feature/s5-eixo-c-normalizer` (models, schemas, equivalence_key, base do Eixo C) — prepara G1.
2. `feature/s5-eixo-a-watchers` + `feature/s5-eixo-b-evidence-vault` — prepara G2/G3.
3. `feature/s5-eixo-d-ui-indexer` — prepara G5.
4. `feature/s5-eixo-e-observability-gates` — amarra G0–G7, métricas e dashboards.

CI deve ser configurado para rodar ao menos testes de schema, componentes e pipeline em todos os PRs dos eixos centrais.

---

## 4. DoD por Eixo (A–E)

### 4.1 Eixo A — Sources & Watchers v0

**DoD Eixo A:**

- `inspectah/config/sources_registry.yaml` suporta pelo menos 3 tipos de fonte (RSS, API, HTML) com campos descritos no Cap. 1.
- `inspectah/watchers/engine.py` executa ciclos de ingestão e produz itens S1 com logs estruturados.
- `inspectah/watchers/rss_watcher.py`, `api_watcher.py` e `html_watcher.py` funcionam com fixtures.
- `tests/components/test_watchers_engine.py` cobre sucesso + falhas típicas (timeout, HTTP ruim, payload inválido).
- Métricas de ingestão básicas (runs, falhas, latência) expostas.
- Contribui para: G2, G3, G6, G7.

### 4.2 Eixo B — Evidence Vault v0

**DoD Eixo B:**

- `inspectah/evidence/builder.py` cria Evidence Bundles no layout canônico.
- `inspectah/evidence/verifier.py` valida 100% dos bundles gerados.
- Estrutura física de bundles definida e aplicada (paths determinísticos).
- `tests/components/test_evidence_builder.py` e `test_evidence_verifier.py` passam com cobertura satisfatória.
- `bin/s5_check_invariants.sh` verifica integridade (sem violar invariantes de evidência).
- Contribui para: G2, G3, G6, G7.

### 4.3 Eixo C — AI Claim Normalizer v0.1

**DoD Eixo C:**

- `inspectah/models/item.py` e `claim.py` implementam 1:1 o schema v0.1.
- `schemas/inspectah_item_v0_1.json` e `inspectah_claim_v0_1.json` validados por testes.
- `inspectah/equivalence_key.py` com função determinística coberta por testes e exemplos.
- `inspectah/normalizer/client_ai.py` implementa interface de client com stub + GPT‑4.1 mini real.
- `inspectah/normalizer/normalizer.py` aplica invariantes de não-invenção e valida JSON.
- `tests/test_schema_item.py`, `test_schema_claim.py`, `test_equivalence_key.py`, `test_normalizer_stub.py` verdes.
- `fixtures/s5/real_texts/` preparados para G4.
- Contribui para: G1, G2, G3, G4, G6, G7.

### 4.4 Eixo D — Indexação + UI Admin & Explore v0

**DoD Eixo D:**

- `inspectah/indexer/indexer.py` recebe itens S3 e publica em storage de consulta.
- `inspectah/indexer/query_api.py` expõe endpoints internos para listar itens por fonte, tempo e equivalence_key.
- `inspectah/ui/admin_sources.py` + templates permitem CRUD de fontes simples.
- `inspectah/ui/explore.py` + templates listam itens S4 e exibem detalhe com evidência + texto + claims.
- `docs/sprint_5/gates/G5_operator_scenario.md` descreve jornada de teste.
- `tests/components/test_indexer.py` e `tests/pipeline/test_pipeline_fixtures.py` incluem pelo menos um teste de leitura de itens S4.
- Contribui para: G3, G5, G6, G7.

### 4.5 Eixo E — Observability + Gates & Fixtures

**DoD Eixo E:**

- Instrumentação de métricas implementada em watchers, evidence, normalizer e indexer.
- Endpoint de métricas expõe métricas definidas no Cap. 1.
- `dashboards/s5_inspectah_core.json` inclui gráficos por fonte, por estado, por normalização.
- Todos os scripts de gate (G0–G7) implementados em `bin/` e rodando localmente.
- Fixtures em `fixtures/s5/` e golden data em `tests/golden/` completos.
- Primeiro ciclo de G0–G3 é executado com PASS em ambiente local.
- Contribui para: G0–G7.

---

## 5. Plano de CI (jobs, gatilhos e integração com gates)

### 5.1 Jobs mínimos

Sugestão para pipeline CI (por exemplo via GitHub Actions):

- `ci-schema-and-models`  
  Roda: `pytest tests/test_schema_item.py tests/test_schema_claim.py tests/test_equivalence_key.py`.

- `ci-components`  
  Roda: `pytest tests/components/`.

- `ci-pipeline-fixtures`  
  Roda: `pytest tests/pipeline/test_pipeline_fixtures.py` + `bin/s5_check_invariants.sh`.

- `ci-ui-smoke`  
  Roda smoke tests das rotas principais (admin_sources, explore).

- `ci-metrics-smoke`  
  Verifica se endpoint de métricas sobe e expõe métricas centrais.

### 5.2 Gatilhos

- Em PRs para branches `feature/s5-*` e `chore/s5-*`: rodar `ci-schema-and-models` + `ci-components` + `ci-pipeline-fixtures`.
- Em merges para o branch da sprint `sprint-5/inspectah-core`: rodar todos os jobs acima.

### 5.3 Relação CI × Gates

- G1 só pode ser considerado PASS se `ci-schema-and-models` estiver verde.
- G2 depende de `ci-components` verde.
- G3 depende de `ci-pipeline-fixtures` verde.
- G6 depende de `ci-metrics-smoke` verde.

Os scripts de gate podem ser chamados a partir dos jobs de CI ou executados manualmente, mas o ideal é que exista um job específico de **ORR da sprint** que rode pelo menos G1–G3 em modo automatizado antes do G7.

---

## 6. Riscos e rollback por eixo

### 6.1 Tabela de riscos

| Eixo | Risco principal                                      | Mitigação                                              | Rollback/isolamento                                      |
|------|------------------------------------------------------|--------------------------------------------------------|----------------------------------------------------------|
| A    | Watchers sobrecarregarem fontes ou quebrarem parsing | Usar fixtures e limites de taxa; validar manualmente  | Desativar fonte via registry; feature flag p/ watcher   |
| B    | Corrupção de evidência ou layout instável            | Verificador forte + testes de golden bundles          | Manter versões de layout; ler-only bundles antigos      |
| C    | IA gerar claims incorretos ou instáveis              | Stubs e golden data; revisão manual de amostras       | Desligar IA real e cair para stub/"sem claims"         |
| D    | UI confusa ou quebrada para operador                 | Teste G5 com operador externo; UX mínima obrigatória  | Esconder rotas experimentais; toggle de recursos        |
| E    | Métricas ausentes ou gates inexecutáveis             | Scripts simples, incrementais; validar local primeiro | Rodar apenas subset de gates até corrigir; logs fallback|

### 6.2 Feature flags e toggles

Idealmente, componentes que podem introduzir instabilidade (IA real, novas fontes, novas telas) devem ser protegidos por flags simples (config em YAML ou env vars), de modo que:

- Em caso de problema em produção interna, seja possível:
  - desabilitar fontes específicas;
  - desativar normalização por IA temporariamente;
  - ocultar seções experimentais da UI.

Essas flags devem ser documentadas em `s5_contracts_overview.md`.

---

## 7. Sequência de entrega de valor para o operador

Para maximizar valor percebido cedo (e não só no fim da sprint), a execução deve priorizar:

1. **Primeira visão clicável (sem IA real)**  
   Watchers + Evidence Vault + Indexer + UI Explore com dados de fixtures.  
   Permite que o operador veja fontes cadastradas, itens chegando e evidência bruta.

2. **Claims por fonte com IA stub**  
   Normalizer operando com stub, exibindo claims determinísticos derivados de fixtures/golden.  
   Permite testar a experiência de "ver o que cada fonte diz" sem depender da IA real.

3. **IA real com supervisão**  
   Ativar GPT‑4.1 mini para subconjunto de fontes, com amostras sendo revistas (G4).

4. **Jornada completa com operador externo (G5)**  
   Operador consegue cadastrar fonte real, ver ingestão, evidência e claims.

5. **Consolidação de métricas e estabilidade (G6–G7)**  
   Painel pronto, execução prolongada e decisão final GO/NO-GO.

Esta sequência garante que o Inspectah se torne útil para inspeção interna o quanto antes, mesmo antes do fechamento formal da sprint.

---

## 8. Regras finais de disciplina

- Se algum artefato listado neste Capítulo 3 não puder ser criado dentro da sprint, isso deve ser explicitado em wrap, com ajuste claro de escopo.
- Nenhum script de gate pode ser um stub: todos precisam executar checks reais.
- Qualquer mudança de nomes de arquivos, caminhos ou estrutura central exige atualização imediata deste Capítulo 3.
- O Codex deve tratar este capítulo como mapa de verdade: criar arquivos onde está escrito, com os nomes especificados, e só divergir se houver motivo forte registrado em commit/PR.

Com os Capítulos 1, 2 e 3 neste nível de detalhe, a Sprint 5 do Inspectah deixa de ser "boa intenção" e passa a ser um plano executável, rastreável e auditável de ponta a ponta.

