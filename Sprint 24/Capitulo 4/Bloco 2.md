# 4.2 – Gates, Métricas & Definition of Done (Execução) – v2

Este subcapítulo 4.2 é o **contrato operacional** de validação da sprint: ele traduz o que o Cap. 2 definiu como gates globais e o que o 4.1 estabeleceu como contexto de execução em um **sistema concreto de checagens automatizadas, métricas e critérios de “pronto”**.

Não é uma lista genérica de G0–G8; é a especificação de:
- quais gates efetivamente existem para esta sprint;
- que **scripts** e **artefatos** cada gate produz;
- quais **métricas** (de produto e operacionais) cada gate lê;
- como tudo isso se amarra na **Definition of Done** da sprint.

---

## 4.2.1 – Papel dos gates de execução no contexto da sprint

No Sprint Playbook v2, os gates de sprint são a forma oficial de responder três perguntas:
1. *Podemos afirmar, com base em evidências, que o que prometemos está de pé?*
2. *Onde exatamente está quebrando quando algo não funciona?*
3. *O que falta para esta sprint ser GO sem apelar para “confia em mim”?*

O Capítulo 2 já definiu a existência de uma sequência de gates G0–G8 para cada sprint. Aqui, no 4.2, o foco é o arco S21–S25 (Fontes → Ingestão 2.0 → Cérebro → Comitês & Debunker → Truth‑DB), e a pergunta fica mais específica:

> Que **gates de execução** garantem que essa espinha dorsal está minimamente funcional, observável e auditável, no recorte desta sprint?

Para isso, o 4.2 assume três princípios:

- **Gates são scripts, não slides**: cada gate é uma combinação 
  `script oficial em bin/` → `scorecard em out/scorecards/` → `evidências em out/evidence/`.
- **Gates são cumulativos**: G2 não “substitui” G1; ele constrói por cima. A sprint só é GO quando a cadeia inteira (G0–G8) está em um estado aceitável.
- **Gates são idempotentes**: rodar um gate duas, dez ou cem vezes não pode mudar o significado do resultado; no máximo, atualiza evidências e scorecards.

---

## 4.2.2 – Mapa detalhado de gates G0–G8 para esta sprint

Nesta sprint, os gates assumem os seguintes papéis concretos (nomes definitivos de scripts e scorecards serão preenchidos no Cap. 4.3/4.4, mas o *contrato semântico* está aqui):

### G0 – Grounding & Setup de Execução

**Objetivo:** garantir que o ambiente consegue, de fato, executar a sprint sem truques locais.

**Escopo mínimo:**
- criação/ativação de ambiente (virtualenv, containers, etc.);
- instalação de dependências do backend (e frontend, se aplicável ao recorte);
- aplicação de migrações de base “zero” (até o estado necessário para rodar G1);
- checagem de conectividade com banco relacional, mensageria e stack de observabilidade (quando existirem);
- verificação de variáveis de ambiente obrigatórias para a sprint.

**Artefatos esperados:**
- script oficial (ex.: `bin/sXX_g0_setup.sh`);
- scorecard `out/scorecards/SXX_G0_setup.json` contendo:
  - `env_ok` (boolean),
  - `db_connect_ok`, `broker_connect_ok`, `otel_ok`,
  - `python_version`, `service_versions`,
  - lista de variáveis obrigatórias encontradas/faltantes;
- logs mínimos em `out/evidence/SXX_G0_setup/` mostrando saída de comandos chave.

**Critério de aprovação:** `env_ok = true`, nenhuma dependência crítica com `_ok = false` e nenhuma variável obrigatória ausente.

---

### G1 – Modelos, Migrações & Invariantes Estruturais

**Objetivo:** alinhar o mundo real (schema do banco) ao mundo descrito no Cap. 3.3.

**Escopo mínimo:**
- rodar todas as migrações em uma base limpa;
- verificar a existência de todas as tabelas e colunas descritas no Cap. 3.3;
- garantir que enums/estados correspondem ao esperado (por exemplo, estados de `TruthRecord`);
- aplicar queries de sanidade para invariantes estruturais (FKs, unicidades, constraints, índices críticos).

**Artefatos esperados:**
- script (ex.: `bin/sXX_g1_models_and_migrations.sh`);
- scorecard `out/scorecards/SXX_G1_models_and_migrations.json` com campos como:
  - `migrations_total`, `migrations_failed`,
  - `invariants_checked`, `invariants_violated`,
  - `unexpected_tables`, `unexpected_columns`,
  - `schema_hash` (resumo da estrutura aplicada);
- queries e resultados de sanity em `out/evidence/SXX_G1_schema_sanity/`.

**Critério de aprovação:**
- `migrations_failed = 0`;
- `invariants_violated = 0`;
- lista de `unexpected_*` vazia ou explicitamente justificada.

---

### G2 – Ingestão 2.0 (Sources → Runs → Itens Normais)

**Objetivo:** garantir que a pipeline de ingestão/normalização está viva para o recorte de fontes da sprint.

**Escopo mínimo:**
- cadastrar fontes de teste (podem ser seeds ou via scripts);
- criar `IngestionConfig` para cada fonte relevante;
- disparar `IngestionRun` para cada fonte;
- registrar `IngestionItemRaw` e `IngestionItemNormalized`;
- emitir eventos `ingestion.item.normalized` na mensageria (ou registrá-los em store de teste, se mensageria ainda for mock).

**Artefatos esperados:**
- script (ex.: `bin/sXX_g2_ingestion.sh`);
- scorecard `out/scorecards/SXX_G2_ingestion.json` contendo, por fonte:
  - `runs_started`, `runs_success`, `runs_failed`,
  - `items_raw_count`, `items_normalized_count`,
  - `latency_run_p95_ms`, `latency_item_p95_ms`,
  - `external_errors_by_code` (HTTP 4xx/5xx, timeouts);
- dumps de amostragem de `IngestionItemRaw/Normalized` em `out/evidence/SXX_G2_ingestion/` (anônimos ou com dados públicos);
- amostras de eventos `ingestion.item.normalized` em formato JSON.

**Critério de aprovação:**
- para cada tipo de fonte no escopo da sprint, pelo menos uma run `SUCCESS` (ou `PARTIAL_SUCCESS` com justificativa explícita de falha externa);
- ausência de duplicação indevida de itens (respeito à unicidade por `source_item_id`);
- eventos emitidos com payloads compatíveis com os modelos do Cap. 3.3.

---

### G3 – Cérebro v1 (Interpretação, Classificação & Claims)

**Objetivo:** testar a camada que lê itens normalizados e produz unidades interpretadas, classificações e claims.

**Escopo mínimo:**
- consumir `IngestionItemNormalized` de teste;
- gerar `InterpretationUnit` para esses itens;
- gerar `ClassificationResult` (quando aplicável à sprint);
- criar `Claim` associadas a unidades de interpretação;
- emitir eventos `interpretation.unit.created` e `claim.created`.

**Artefatos esperados:**
- script (ex.: `bin/sXX_g3_brain_and_claims.sh`);
- scorecard `out/scorecards/SXX_G3_brain_and_claims.json` com campos como:
  - `normalized_items_processed`,
  - `interpretation_units_created`,
  - `claims_created`,
  - `claims_expected` (para cenários anotados),
  - `claims_missing`, `claims_spurious`,
  - `pipeline_errors`;
- tabela de comparação cenário → claims (por exemplo, em CSV/JSON) em `out/evidence/SXX_G3_claims/`, descrevendo, para cada input, quais claims eram esperadas e quais foram obtidas;
- amostras de eventos de claims/interpretation.

**Critério de aprovação:**
- nenhuma Claim estruturalmente inválida (sem cadeia `Claim → InterpretationUnit → IngestionItemNormalized → Source`);
- para o conjunto de cenários da sprint, taxa mínima de cobertura de claims esperadas (limiar definido no Cap. 2, ex.: ≥ X%);
- taxa de claims “lixo” (sem sentido, duplicadas ou fora do escopo) abaixo de um limiar definido.

> Observação: caso a sprint ainda não use LLM de verdade, G3 se concentra em testar a infraestrutura do pipeline, com fixtures simulando as respostas de interpretação/classificação.

---

### G4 – Comitês & Debunker v0

**Objetivo:** garantir que a camada de avaliação, decisão e contestação funciona ponta a ponta.

**Escopo mínimo:**
- gerar (ou carregar) um conjunto de Claims de teste com `Evidence` associadas;
- registrar `CommitteeEvaluation` feitas por N avaliadores (podem ser agents ou mocks);
- consolidar `CommitteeDecision` a partir dessas avaliações;
- abrir `DebunkIssue` contra claims ou decisões selecionadas;
- atribuir e completar `DebunkTask`, registrando resultados;
- emitir eventos `committee.decision.made`, `debunk.issue.opened`, `debunk.issue.resolved`.

**Artefatos esperados:**
- script (ex.: `bin/sXX_g4_committees_and_debunker.sh`);
- scorecard `out/scorecards/SXX_G4_committees_and_debunker.json` contendo:
  - `decisions_total`,
  - distribuição de `final_verdict` (TRUE/FALSE/UNDECIDED/CONTESTED),
  - `uncertainty_score_avg`, `uncertainty_score_p95`,
  - `debunk_issues_opened`, `debunk_issues_resolved`,
  - `debunk_resolution_time_p95`,
  - `committee_debunker_disagreements` (casos em que o debunker contestou o comitê);
- logs estruturados e dumps das trilhas completas committee → debunker em `out/evidence/SXX_G4_committees/`.

**Critério de aprovação:**
- fluxo completo (Claim → Evaluations → Decision → Issue → Tasks → Resolution) funcionando para os cenários da sprint;
- nenhuma decisão “solta” (por exemplo, Decision sem Evaluations ou sem Claim);
- nenhuma issue presa em estado intermediário não previsto;
- presença consistente dos eventos esperados.

---

### G5 – Truth‑DB Operacional

**Objetivo:** validar que a máquina de estados de `TruthRecord` e `TruthChangeEvent` se comporta conforme o modelo desenhado.

**Escopo mínimo:**
- criar claims candidatas;
- promover algumas a FACT com base em decisões de comitê;
- marcar algumas como CONTESTED via issues de debunker;
- rebaixar FACT para REJECTED ou outro estado coerente após resolução;
- encerrar claims quando aplicável (por exemplo, estado RETIRED/ARCHIVED).

**Artefatos esperados:**
- script (ex.: `bin/sXX_g5_truthdb.sh`);
- scorecard `out/scorecards/SXX_G5_truthdb.json` com campos como:
  - `claims_total`,
  - contagem de `truth_by_state` (CANDIDATE/FACT/CONTESTED/REJECTED/etc.),
  - `claims_with_multiple_active_truth`,
  - `change_events_total`,
  - `change_events_missing_reason`,
  - `timeline_inconsistencies`;
- dumps de timelines de truth para claims selecionadas em `out/evidence/SXX_G5_truth_timelines/`.

**Critério de aprovação:**
- `claims_with_multiple_active_truth = 0`;
- nenhuma mudança de estado sem `TruthChangeEvent` correspondente e explicativo;
- estados finais condizentes com as decisões e issues exercitadas em G4.

---

### G6 – Observabilidade & Falhas Controladas

**Objetivo:** assegurar que a sprint não apenas “roda”, mas é **visível e resiliente**.

**Escopo mínimo:**
- verificar que logs estruturados, métricas e, quando aplicável, traces, estão sendo emitidos em operações críticas (ingestão, criação de claims, decisões, debunker, truth);
- rodar cenários de falha controlada:
  - banco indisponível por curto período;
  - mensageria indisponível ou lenta;
  - fonte externa lenta ou fora do ar;
  - Evidence Vault indisponível.

**Artefatos esperados:**
- script (ex.: `bin/sXX_g6_observability_and_failures.sh`);
- scorecard `out/scorecards/SXX_G6_observability_and_failures.json` com campos como:
  - `metrics_present` (lista de métricas mínimas encontradas),
  - `logs_structured_ratio`,
  - `traces_end_to_end_count`,
  - resultados por cenário de falha (`db_down_ok`, `broker_down_ok`, `external_down_ok`, `vault_down_ok`),
  - descrição de qualquer divergência entre comportamento esperado e observado;
- amostras de logs/metrics/traces antes, durante e depois das falhas em `out/evidence/SXX_G6_failures/`.

**Critério de aprovação:**
- métricas mínimas e logs estruturados presentes em todos os pontos críticos definidos no Cap. 3.4;
- em cada cenário de falha, o sistema se comporta conforme o design (fail fast, retries limitados, marcação de status, nenhuma corrupção de estado);
- pelo menos um trace ponta a ponta completo registrado em ambiente de teste.

---

### G7 – ORR de Sprint (Consolidação de Evidências)

**Objetivo:** consolidar em um único lugar a visão de saúde da sprint, para inspeção humana e decisão informada.

**Escopo mínimo:**
- checar a presença de todos os scorecards G0–G6;
- validar se todos os gates obrigatórios estão em estado OK (ou WARN com justificativa);
- montar um pequeno relatório (JSON ou markdown) com o resumo da sprint.

**Artefatos esperados:**
- script (ex.: `bin/sXX_g7_orr.sh`);
- scorecard `out/scorecards/SXX_G7_orr.json` com campos como:
  - `gates_status` (mapa G0–G6 → OK/WARN/FAIL),
  - `blocking_issues` (lista),
  - `warnings_with_justification`,
  - `summary_metrics` (métricas-chave da sprint);
- relatório humano em `out/evidence/SXX_G7_orr_report.md` ou similar.

**Critério de aprovação:**
- nenhum gate crítico em estado FAIL;
- qualquer WARN devidamente documentado com impacto e plano de tratamento em sprints futuras.

---

### G8 – GO/NO‑GO

**Objetivo:** registrar a decisão final sobre a sprint, com last‑mile técnico e assinatura de governança.

**Escopo mínimo:**
- reexecutar um subconjunto de cenários ponta a ponta (os mais críticos);
- verificar que o bundle de evidências foi gerado e é consistente;
- registrar a decisão GO, GO com restrições ou NO‑GO, com nomes e justificativa.

**Artefatos esperados:**
- script (ex.: `bin/sXX_g8_go_no_go.sh`);
- scorecard `out/scorecards/SXX_G8_go_no_go.json` com campos como:
  - `decision` (GO/GO_WITH_RISKS/NO_GO),
  - `decision_participants`,
  - `rationale`,
  - `residual_risks`,
  - `followup_actions`;
- referência explícita ao bundle em `out/bundles/inspectah_sXX_evidence_bundle.zip`.

**Critério de aprovação:**
- decisão alinhada ao estado dos gates e às métricas da sprint;
- qualquer GO condicionado vem acompanhado de ações claras.

---

## 4.2.3 – Métricas oficiais da sprint (o que é medido, onde e por quê)

Os gates acima consomem um conjunto de **métricas oficiais** que a sprint se compromete a expor. O 4.2 documenta, em termos de execução, quais são essas métricas, onde elas vivem e qual papel cumprem.

### 4.2.3.1 – Métricas estruturais (G1)

- `migrations_total`, `migrations_failed`: derivadas da ferramenta de migração (Alembic ou similar).
- `invariants_checked`, `invariants_violated`: contadores provenientes de scripts SQL/Python que verificam FKs, unicidade e enums.
- `schema_hash`: hash calculado a partir da descrição do schema (tabelas, colunas, tipos), útil para detectar divergência entre ambientes.

### 4.2.3.2 – Métricas de ingestão (G2)

- `ingestion_runs_total`, `ingestion_runs_success`, `ingestion_runs_failed` (por fonte);
- `ingestion_items_raw_total`, `ingestion_items_normalized_total`;
- `ingestion_run_latency_seconds` (histograma, com p95/p99);
- `ingestion_external_errors_total` (por código de erro HTTP ou tipo de falha);
- `source_health_status` (contagem por estado OK/DEGRADED/DOWN).

### 4.2.3.3 – Métricas de cérebro & claims (G3)

- `claims_created_total`;
- `claims_by_source`;
- `claims_coverage_ratio` (claims esperadas x obtidas em cenários anotados);
- `claims_garbage_ratio` (claims descartadas por regras de sanidade);
- `brain_pipeline_latency_seconds`.

### 4.2.3.4 – Métricas de comitê & debunker (G4)

- `committee_decisions_total` e distribuição de `final_verdict`;
- `committee_uncertainty_score_mean` e `p95`;
- `debunk_issues_open_total`, `debunk_issues_resolved_total`;
- `debunk_issue_resolution_time_seconds` (histograma);
- `committee_debunker_disagreement_total`.

### 4.2.3.5 – Métricas de truth (G5)

- `truth_records_total`;
- `truth_records_by_state` (CANDIDATE/FACT/CONTESTED/REJECTED/etc.);
- `truth_change_events_total`;
- `claims_with_multiple_active_truth_total`;
- `truth_timeline_length_mean`.

### 4.2.3.6 – Métricas de observabilidade & falhas (G6)

- `logs_structured_ratio` (amostra de logs contendo campos mínimos: `trace_id`, `entity_type`, `entity_id`, `event`);
- `traces_end_to_end_total` (fluxos ponta a ponta com trace completo);
- `failure_scenario_success_total` (cenários de falha que se comportaram como esperado);
- `failure_scenario_regressions_total`.

### 4.2.3.7 – Métricas de processo (G7–G8)

- `gates_ok_total`, `gates_warn_total`, `gates_fail_total`;
- `scorecards_present_total` versus `scorecards_expected_total`;
- `bundles_generated_total`;
- `go_decisions_total` e distribuição por tipo (GO/GO_WITH_RISKS/NO_GO).

---

## 4.2.4 – Definition of Done (Execução) acoplada a gates & métricas

A **Definition of Done** de execução desta sprint é deliberadamente rígida. Um item (feature, fluxo, parte da arquitetura) só é considerado “done” quando atende cumulativamente a quatro camadas:

1. **Código & testes**
   - Implementação está em branch correta, com commits limpos;
   - existe cobertura de testes adequada (unitários/integrados/e2e) para o comportamento crítico;
   - testes passam em ambiente local **e** no CI.

2. **Gate correspondente em estado OK**
   - Pelo menos um gate toca essa parte do sistema (G1–G6);
   - o script do gate roda em ambiente limpo;
   - o scorecard resultante marca os checks relevantes como OK (sem FAIL oculto em campos “secundários”).

3. **Evidências registradas**
   - Há evidências em `out/evidence/` mostrando o item em ação: logs, dumps de entidades, snapshots de métricas/painéis, trilhas de truth, etc.;
   - essas evidências podem ser inspecionadas por qualquer pessoa da equipe sem depender de contexto invisível.

4. **Coerência com o Cap. 3 e com os objetivos do 4.1**
   - Não há divergência entre o comportamento observado (em dados e eventos) e o que o Cap. 3 define como modelo e invariantes;
   - o item contribui claramente para os objetivos não negociáveis de execução listados no 4.1 (ponta a ponta mínima, reprodutibilidade, sanidade estrutural, simetria local/CI, evidências como produto).

Se qualquer uma dessas camadas faltar, o item é considerado “em progresso” ou “experimental”, mas **não done**.

> Atalho explícito proibido: marcar algo como done apenas porque “está funcionando na demo” sem gate, scorecard e evidência. Isso quebra o contrato do Cap. 4 e volta a trazer execução tribal para dentro da sprint.

Com isso, o 4.2 fixa a malha de segurança da sprint: uma rede de gates, métricas e critérios de aceitação que tornam o estado da execução verificável, auditável e, principalmente, **reprodutível** – condição mínima para que o Inspectah possa um dia se vender como “plataforma de verdade” sem corar de vergonha.