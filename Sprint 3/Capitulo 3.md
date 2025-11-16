# Inspectah — Capítulo 3 v2
## Filemap, Artefatos & Evidências — State of the Art, 100% alinhado aos Gates T0–T8

---

### 0. TL;DR

Capítulo 1: define **o que** é o Inspectah.  
Capítulo 2 v3: define **quando** uma versão é saudável (Gates T0–T8, linha dura 15/10).  
Capítulo 3 v2: define **onde** tudo isso mora no repositório, **qual arquivo pratica qual Gate** e **onde ficam as evidências**.

Princípios centrais:

1. **Gate‑first** — Toda pasta, arquivo e script existe para suportar **algum Gate T0–T8**. Se não encaixa em Gate, não é prioridade da sprint.
2. **Evidence‑by‑design** — Nenhum teste relevante é “invisível”: toda execução de Gate gera scorecard e artefatos em locais canônicos.
3. **Um único lugar óbvio** — Para cada tipo de coisa (docs, schema, configs de fonte, ORR, evidências), existe um **endereço padrão**.
4. **Simetria local ↔ CI** — O mesmo conjunto de scripts/paths é usado localmente e em CI; a diferença é apenas ambiente/variáveis.
5. **Compatível com crescimento** — A estrutura já se prepara para novos Gates (como T5.2 — Calibração) e expansão de fontes, sem virar caos.

Se Capítulo 2 é o **contrato de validação**, Capítulo 3 é o **mapa físico** para o Codex cumprir esse contrato, sem improviso.

---

### 1. Objetivo do Capítulo 3

Transformar os Gates T0–T8 em:

- uma **árvore de diretórios** clara e extensível;
- um **catálogo de artefatos obrigatórios** (scripts, configs, docs, scorecards, evidências);
- um conjunto de **regras de encaixe**: qualquer trabalho da sprint precisa dizer explicitamente em qual Gate cai e quais arquivos deste capítulo ele toca.

Resultado desejado:

- O repositório do Inspectah é legível como um **organismo orientado a Gates**: dá para olhar a árvore e enxergar T0–T8.
- O Codex sabe exatamente **onde criar/editar** arquivos para implementar ou reforçar cada Gate, sem espalhar lógica em lugares ad‑hoc.

---

### 2. Princípios de design do filemap (versão lapidada)

1. **Reflexo direto do Capítulo 2**  
   Cada Gate tem uma “zona de responsabilidade” no repositório (scripts, dados, evidências). Não existem pastas órfãs.

2. **Separação clara: definição vs. execução vs. evidência**  
   - Definições (Cap.1, Cap.2, Cap.3, blueprint) → `docs/`.  
   - Execução (código, configs, scripts) → `src/`, `schema/`, `configs/`, `ops/`, `bin/`, `.ci/`.  
   - Evidências (scorecards, artefatos de run) → `out/`.

3. **Nomeação previsível**  
   Scripts de Gates seguem o padrão `orr_tX_*`; scorecards `T*_*.json`; evidências em `out/evidence/T*_*/`.  
   Quem conhece Capítulo 2 reconhece um Gate só de olhar o nome do arquivo.

4. **Reprodutibilidade**  
   Qualquer pessoa (ou o CI) pode rodar `bin/orr_all.sh` e obter uma fotografia consistente de todos os Gates, com paths previsíveis.

5. **Extensibilidade controlada**  
   Quando surgirem novos Gates (ex.: T5.2 Calibração), eles ganham **subárvores dedicadas** (`out/evidence/T5_2_calibration/`, `bin/orr_t5_2_calibration.sh`), mantendo o padrão.

---

### 3. Visão geral da árvore de diretórios (refinada)

Layout proposto para a raiz `inspectah/`:

```text
inspectah/
  docs/
    inspectah_cap_1_produto.md
    inspectah_cap_2_gates_orr.md
    inspectah_cap_3_filemap_evidencias.md
    blueprint/
      inspectah_oracleops_blueprint_v1.2.1.md

  schema/
    inspectah_ddl.sql
    migrations/
      V001_init.sql
      V002_add_confidence_engine.sql
      ...

  configs/
    sources/
      rss_*.yaml
      api_*.yaml
      html_*.yaml
      # cada arquivo representa uma Fonte configurável
    profiles/
      confidence_profiles.yaml      # define perfis de confiança

  src/
    field_designer/
    watchers/
    evidence_vault/
    explore/
    confidence_engine/
    observability/
    # cada subpasta mapeia 1:1 com blocos de Cap.1 + Cap.2

  ops/
    otel/
    prometheus/
    grafana/

  .ci/
    orr_pipeline.yml
    tests.yml

  bin/
    orr_t0_spec_lock.sh
    orr_t1_schema_check.sh
    orr_t2_field_designer_smoke.sh
    orr_t3_pipeline_invariants.sh
    orr_t4_evidence_audit.sh
    orr_t5_performance_gate.sh
    orr_t5_1_confidence_gate.sh
    orr_t6_observability_smoke.sh
    orr_t7_orr_pipeline.sh
    orr_t8_go_nogo_helper.sh
    orr_all.sh

  out/
    evidence/
      T0_spec_lock/
      T1_schema/
      T2_field_designer/
      T3_pipeline_invariants/
      T4_evidence_vault/
      T5_performance/
      T5_1_confidence/
      T6_observability/
      T7_orr/
      T8_go_nogo/
    scorecards/
      T0_spec_lock.json
      T1_schema.json
      T2_field_designer.json
      T3_pipeline_invariants.json
      T4_evidence_vault.json
      T5_performance.json
      T5_1_confidence.json
      T6_observability.json
      T7_orr.json
      T8_go_nogo.json
```

Observação: nomes exatos podem ser ajustados na implementação, mas qualquer mudança precisa ser refletida aqui. **Cap.3 é a fonte de verdade da topologia.**

---

### 4. Mapa Gate → artefatos (visão 360°)

Tabela que Martin Kleppmann e Knuth pediriam como header técnico, agora explícita:

| Gate | Docs de referência | Scripts de execução | Código/Configs chave | Scorecard | Evidências |
|---|---|---|---|---|---|
| **T0** | Cap.1, Cap.2, Cap.3, Blueprint | `bin/orr_t0_spec_lock.sh` | — | `out/scorecards/T0_spec_lock.json` | `out/evidence/T0_spec_lock/*` |
| **T1** | Cap.1 (modelo), Blueprint (objetivos de dados) | `bin/orr_t1_schema_check.sh` | `schema/inspectah_ddl.sql`, `schema/migrations/*` | `T1_schema.json` | `T1_schema/*` |
| **T2** | Cap.1 (Fonte/Campos), Cap.2 (T2) | `bin/orr_t2_field_designer_smoke.sh` | `src/field_designer/*`, `configs/sources/*.yaml` | `T2_field_designer.json` | `T2_field_designer/*` |
| **T3** | Cap.1 (Observação/Item/Log), Cap.2 (T3) | `bin/orr_t3_pipeline_invariants.sh` | `src/watchers/*`, `src/evidence_vault/*` | `T3_pipeline_invariants.json` | `T3_pipeline_invariants/*` |
| **T4** | Cap.1 (Evidence Vault), Cap.2 (T4) | `bin/orr_t4_evidence_audit.sh` | `src/evidence_vault/vault_audit.py` | `T4_evidence_vault.json` | `T4_evidence_vault/*` |
| **T5** | Cap.2 (T5), Blueprint (SLOs) | `bin/orr_t5_performance_gate.sh` | `src/watchers/*`, `src/explore/*`, `ops/prometheus/*` | `T5_performance.json` | `T5_performance/*` |
| **T5.1** | Cap.1 (confidence), Cap.2 (T5.1) | `bin/orr_t5_1_confidence_gate.sh` | `src/confidence_engine/*`, `configs/profiles/confidence_profiles.yaml` | `T5_1_confidence.json` | `T5_1_confidence/*` |
| **T6** | Cap.2 (T6) | `bin/orr_t6_observability_smoke.sh` | `ops/otel/*`, `ops/prometheus/*`, `ops/grafana/*`, `src/observability/*` | `T6_observability.json` | `T6_observability/*` |
| **T7** | Cap.2 (T7) | `bin/orr_t7_orr_pipeline.sh`, `.ci/orr_pipeline.yml` | `.ci/*`, `bin/orr_*.sh` | `T7_orr.json` | `T7_orr/*` |
| **T8** | Cap.2 (T8) | `bin/orr_t8_go_nogo_helper.sh` | métricas em produção interna, feedback operadores | `T8_go_nogo.json` | `T8_go_nogo/*` |

Se uma tarefa não consegue apontar, pelo menos, para uma célula desta tabela, ela está fora do escopo da sprint ou precisa ser recortada de outra forma.

---

### 5. Convenções de scorecards (formato lógico)

Para facilitar a vida do Codex e do CI, todos os scorecards `T*_*.json` seguem uma estrutura mínima comum:

```json
{
  "gate": "T5",
  "name": "performance",
  "version": "v1",
  "status": "PASS",       
  "timestamp": "2025-11-14T12:34:56Z",
  "metrics": {
    "detection_latency_p95": 73.2,
    "explore_query_p95": 142.5,
    "explore_query_p99": 310.0,
    "field_resolution_success": 0.997,
    "run_success_rate": 0.995
  },
  "thresholds": {
    "detection_latency_p95": "<= 120 s",
    "explore_query_p95": "<= 200 ms",
    "explore_query_p99": "<= 400 ms",
    "field_resolution_success": ">= 0.995",
    "run_success_rate": ">= 0.995"
  },
  "details": {
    "window": "last_7_days",
    "source": "prometheus://inspectah"
  }
}
```

Pontos importantes:

- `gate` e `name` sempre presentes; `status ∈ {"PASS","FAIL"}`;  
- `metrics` traz valores numéricos, mapeados diretamente aos SLOs do Cap.2;  
- `thresholds` documenta a regra que foi aplicada;  
- `details` registra contexto mínimo (janela, fonte de dados, observações).

Essa padronização permite que:

- `bin/orr_all.sh` agregue resultados de forma programática;  
- futuros dashboards de ORR leiam esses JSONs diretamente.

---

### 6. T0 & T1 — Onde vivem spec e schema

#### 6.1 T0 — Spec Lock

- **Docs canônicos:**
  - `docs/inspectah_cap_1_produto.md` (Capítulo 1 vFinal);  
  - `docs/inspectah_cap_2_gates_orr.md` (Capítulo 2 v3);  
  - `docs/inspectah_cap_3_filemap_evidencias.md` (este doc);  
  - `docs/blueprint/inspectah_oracleops_blueprint_v1.2.1.md`.

- **Script:** `bin/orr_t0_spec_lock.sh` faz, no mínimo:
  - verificar presença/legibilidade desses arquivos;  
  - extrair hashes/commits/versionamento;  
  - gerar `T0_spec_lock.json` com um resumo da matriz Objetivo → Métrica → Gate;  
  - opcional: consolidar uma visão em Markdown em `out/evidence/T0_spec_lock/spec_lock.md`.

#### 6.2 T1 — Modelo & Schema

- **Schema & migrações:**
  - `schema/inspectah_ddl.sql` (estado atual do modelo);  
  - `schema/migrations/V*.sql` (histórico de migrações).

- **Script:** `bin/orr_t1_schema_check.sh`:
  - sobe DB limpo de teste;  
  - aplica migrations;  
  - confere a presença das tabelas/índices/constraints mínimos citados no Cap.2 (Fonte, Observação, Item, Sinal, `confidence_score`, `confidence_profile_id` etc.);  
  - em caso de erro, marca `status=FAIL` e registra detalhes em `out/evidence/T1_schema/*`.

Capítulo 3 garante que não exista “schema paralelo”: **qualquer modelo que não passe por `schema/` + T1 está fora de contrato.**

---

### 7. T2 & T3 — Field Designer e pipeline, encaixados

#### 7.1 T2 — Field Designer

- **Configs de fontes:** `configs/sources/*.yaml`:
  - definem campos relevantes por Fonte, tipo de dado, origem (selector/JSONPath/etc.), validações básicas;
  - podem incluir um mapeamento inicial para Sinais.

- **Código:** `src/field_designer/*` implementa:
  - APIs/UX para criar Fonte;  
  - preview/dry‑run com destaque;  
  - publicação de Fonte para coleta.

- **Script:** `bin/orr_t2_field_designer_smoke.sh`:
  - carrega um conjunto mínimo de fontes de teste (RSS/API/HTML);  
  - passa pelo fluxo "Add Source" → dry‑run → publish;  
  - verifica existência de Observações/Itens resultantes;  
  - calcula `field_resolution_success_test` e grava scorecard.

#### 7.2 T3 — Invariantes de pipeline

- **Código:** `src/watchers/*`, `src/evidence_vault/*`.  
- **Fixtures:** opcionalmente `tests/fixtures/pipeline/*`.

- **Script:** `bin/orr_t3_pipeline_invariants.sh`:
  - injeta feeds sintéticos;  
  - verifica se `pipeline_dedup_violations` e `immutability_violations` são 0;  
  - em caso de FAIL, grava exemplos concretos de violação em `out/evidence/T3_pipeline_invariants/*` para debug.

Ideia de Steve Jobs aqui: “Não existe ‘parece ok’. Ou o teste de invariantes passa e os arquivos em `T3_pipeline_invariants` provam isso, ou não passou e o release não sobe.”

---

### 8. T4 — Evidence Vault & integridade

- **Código:**
  - `src/evidence_vault/vault_store.py` — grava bundles;  
  - `src/evidence_vault/vault_audit.py` — lê e audita bundles.

- **Script:** `bin/orr_t4_evidence_audit.sh`:
  - escaneia Itens válidos na janela de 7 dias;  
  - verifica manifest + HTML + texto + metadados + SHA;  
  - calcula `evidence_completeness` e `evidence_hash_valid_rate`;
  - joga resultados no scorecard T4 e lista de exceções (se houver) em `T4_evidence_vault/*`.

Capítulo 3 fixa que **qualquer auditoria de evidência que importe para Gate T4 precisa passar por esse script e gravar nesses paths**.

---

### 9. T5 & T5.1 — Performance, qualidade e certeza (%) bem ancorados

#### 9.1 T5 — Performance & qualidade

- **Código:**
  - `src/watchers/*` (ingestão);  
  - `src/explore/*` (consulta);  
  - `src/observability/metrics.py` (coleta de métricas).

- **Configs de métricas:** `ops/prometheus/rules-inspectah.yml` define:
  - histogramas para latência de ingest e explore;  
  - métricas de `field_resolution_success` e `run_success_rate`;
  - alertas mínimos.

- **Script:** `bin/orr_t5_performance_gate.sh`:
  - consulta o backend de métricas (Prometheus ou similar);  
  - consolida percentis e taxas, compara com thresholds do Cap.2;  
  - marca `PASS/FAIL` com base na tabela de thresholds;  
  - grava scorecard/perf.

#### 9.2 T5.1 — `confidence_score`

- **Código:** `src/confidence_engine/*` implementa cálculo e atribuição de score.
- **Configs:** `configs/profiles/confidence_profiles.yaml` define perfis (`confidence_profile_id`).

- **Script:** `bin/orr_t5_1_confidence_gate.sh`:
  - coleta respostas com `confidence_score` em janela de 7 dias;  
  - calcula cobertura (`confidence_coverage_multi_source`), histograma de buckets, detecção de valores inválidos;  
  - persiste tudo como evidência.

Capítulo 3 garante que **o Confidence Engine nunca é “caixa preta”**: seu comportamento estatístico está sempre materializado em `out/evidence/T5_1_confidence`.

---

### 10. T6 — Observabilidade & SRE

- **Configs:**
  - `ops/otel/collector-dev.yaml` — pipeline de coleta;  
  - `ops/prometheus/rules-inspectah.yml` — regras e alertas;  
  - `ops/grafana/dashboards/*.json` — painéis oficiais.

- **Código:** `src/observability/*` — inicialização de métricas/logs.

- **Script:** `bin/orr_t6_observability_smoke.sh`:
  - garante que as métricas usadas em T4–T5–T5.1 existam e tenham dados;  
  - verifica se há dashboards para ingest, explore e confiança;  
  - grava checklist/resultado em `T6_observability.json`.

Aqui entra o “Design by Contract” de Meyer: se não há métricas e dashboards, os SLOs são papel, não contrato.

---

### 11. T7 — CI & ORR integrado

- **Pipeline CI:** `.ci/orr_pipeline.yml` é o **único** lugar onde a orquestração dos Gates vive. Ele:
  - chama os scripts `bin/orr_t1*` até `bin/orr_t6*`;  
  - coleta scorecards e evidências;  
  - gera `T7_orr.json` com visão consolidada.

- **Script local:** `bin/orr_t7_orr_pipeline.sh` (espelho do pipeline para uso local).  
- **Agregador:** `bin/orr_all.sh` lê todos `T*_*.json` e imprime um resumo único.

Capítulo 3 deixa claro: **não há “segundo ORR”** fora desse caminho; se alguém quiser criar um fluxo paralelo, precisa primeiro atualizar este capítulo.

---

### 12. T8 — Go/No‑Go de uso real

- **Dados:** métricas reais (mesmos SLOs T4/T5/T5.1) em produção interna.
- **Feedback de operadores:** `out/evidence/T8_go_nogo/operators_feedback.md` ou `.json` com perguntas padrão.

- **Script:** `bin/orr_t8_go_nogo_helper.sh`:
  - captura snapshot numérico da janela (7–14 dias);  
  - consolida stats de onboarding (pelo menos 10 fontes, p50 ≤ 5 min);  
  - cria um scorecard `T8_go_nogo.json` em estado “draft” para o comitê completar.

A decisão final (Go/No‑Go) é humana, mas o envelope e o lugar onde ficam as provas são sempre os mesmos.

---

### 13. Regra de encaixe: “cai em qual Gate?”

Para cada tarefa da sprint, o Product Owner deve exigir uma resposta explícita:

> 1) Em qual Gate T0–T8 isso encaixa?  
> 2) Quais arquivos/pastas deste Cap.3 serão tocados ou criados?

Exemplos rápidos:

- Criar suporte a uma nova API de preços → T2/T3/T4/T5; tocar `configs/sources/api_nova.yaml`, `src/watchers/api_watcher.py`, rever `orr_t2_*` e `orr_t3_*`, garantir bundles em T4 e métricas em T5.
- Otimizar consultas do Explore → T5; tocar `src/explore/*` e confirmar que `orr_t5_performance_gate.sh` permanece verde com margens melhores.
- Ajustar heurísticas de `confidence_score` → T5.1; tocar `src/confidence_engine/*` e `configs/profiles/confidence_profiles.yaml` e acompanhar o impacto em `T5_1_confidence.json`.

Se a resposta a “cai em qual Gate?” for vaga ou “em nenhum”, o padrão é: **não entra como prioridade da sprint**.

---

### 14. Resumo final para o Codex

Para o Codex, Capítulo 3 v2 é o **GPS do repositório**:

- Diz **onde** colocar cada arquivo de schema, código, config, script, evidência e scorecard.
- Garante que cada Gate T0–T8 do Cap.2 tenha caminho físico bem definido no repo.
- Impõe que qualquer novo trabalho declare o seu encaixe em Gates e pastas.

Capítulo 2 + Capítulo 3 formam o backbone:

- Capítulo 2: contratos dos Gates (pré/pós/thresholds/simultaneidade).  
- Capítulo 3: topologia de arquivos e artefatos que materializam esses contratos.

Se em algum momento o código divergir deste capítulo, **este capítulo é o certo e o código está errado** até ser corrigido. Isso é o que garante que os Gates sejam, de fato, o gargalo máximo de validação de toda a sprint do Inspectah.

