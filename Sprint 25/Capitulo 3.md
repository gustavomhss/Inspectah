# Sprint 25 — Capítulo 3 (v2)
## Arquitetura, Domínios e Filemap

> Versão v2 — Refinado pelo Squad Verdade & Interpretação com revisão de Stonebraker, Norvig, Pearl, Percy, Victor, Jobs e Conselho. Este capítulo descreve a **forma** da Sprint 25: quais domínios existem, como se relacionam, onde o código vive, quais invariantes arquiteturais não podem ser violados e como tudo isso se mantém legível e auditável por humanos.

---

### 3.1 Visão arquitetural macro da S25

A Sprint 25 assenta uma **camada de Verdade/Fato v1.5** sobre o núcleo existente do Inspectah. Ela não cria um sistema novo ao lado: ela **atravessa** ingestão, camadas, contestação e console, encaixando um modelo formal de verdade e governança.

Do ponto de vista de arquitetura, a S25 é organizada em sete blocos coesos:

1. **Truth‑DB & TruthState** — armazena estados de verdade de claims/casos e sua evolução temporal.
2. **PromotionPolicy & Evaluation Engine** — define, versiona e aplica regras de promoção/demover.
3. **Layers & Context Service** — orquestra o Sistema de Camadas (intérprete → classifier → comitês → Debunker → humano → decisão) usando Dossiês de Entidade/Caso.
4. **DecisionTrace & Evidence Linking** — conecta camadas, políticas, contexto, threat signals e estados de verdade em uma narrativa única de decisão.
5. **ThreatModel & Métricas Adversariais** — calcula sinais e métricas de vulnerabilidade narrativa/sistêmica.
6. **Console & Agent Studio** — UI e APIs admin para operar a máquina de verdade, agentes de camada, políticas e incidentes.
7. **Incidentes & Governança Operacional** — registra incidentes de verdade, ações corretivas e medidas de contenção.

Cada bloco é:

- mapeado em domínios explícitos (packages/backend);  
- exposto em módulos front‑end próprios (sub‑apps dentro do Console);  
- verificado pelos gates da S25 (Cap. 2) com scorecards e evidências.

Arquiteturalmente, a S25 aplica três princípios inegociáveis:

1. **Separação de domínios por responsabilidade** — Truth‑DB não sabe de UI, UI não sabe de política, política não sabe de storage.
2. **Traços completos de decisão (DecisionTrace)** — qualquer decisão relevante precisa ser reconstruível a partir de dados persistidos.
3. **Código humano** — tudo que implementa verdade, camadas e políticas deve ser código que engenheiros sêniores conseguem ler, revisar e manter.

---

### 3.2 Domínios, bounded contexts e relações

A arquitetura lógica da S25 é organizada em bounded contexts. No backend Python/FastAPI, isso se manifesta em pacotes independentes; no frontend, em módulos/rotas dedicados.

#### 3.2.1 Domínio `truth`

Responsabilidade: representar **o estado de verdade** de claims/casos e sua timeline.

- Não sabe de UI, threatmodel ou layouts.
- Recebe decisões já consolidadas (estado alvo + justificativa).
- Garante invariantes de integridade temporal e referencial.

#### 3.2.2 Domínio `policies`

Responsabilidade: representar e avaliar **políticas de promoção/demover**.

- Não decide “verdade por si” — fornece recomendações baseadas em contexto.
- Não conhece detalhes de UI, apenas recebe `PolicyEvaluationContext` e devolve `Recommendation`.

#### 3.2.3 Domínio `layers`

Responsabilidade: coordenar o **Sistema de Camadas** (interpretação, classificação, comitês, Debunker, humano).

- Orquestra chamadas a agentes GPT, Debunker, humano‑no‑loop.
- Consulta Context Service, ThreatModel e Policies.
- Ao final, cria um `DecisionRecord` usado pelo domínio `truth`.

#### 3.2.4 Domínio `context`

Responsabilidade: fornecer **Dossiês de Entidade/Caso**.

- Consolida tudo que o Inspectah já sabe sobre uma Entidade e seus Casos.
- Fornece snapshots coerentes, reconstituíveis, versionados.

#### 3.2.5 Domínio `threatmodel`

Responsabilidade: produzir **sinais e métricas adversariais**.

- Observa Truth‑DB, claims, fontes, dossiês e decisões.
- Calcula indicadores de riscos (dependência em fonte única, flood narrativo, taxa de reversão, etc.).

#### 3.2.6 Domínio `agents`

Responsabilidade: gerenciar **agentes de camada** (instruções, KB, ferramentas, versões, testes).

- Fornece ao domínio `layers` as versões de agentes apropriadas.

#### 3.2.7 Domínio `incidents`

Responsabilidade: registrar e acompanhar **incidentes de verdade/governança**.

- Conecta ThreatModel, Truth‑DB, Policies, Layers e Console.

#### 3.2.8 Domínio `console`

Responsabilidade: expor **tudo isso em UI e APIs admin**.

- Páginas de Truth Console, Agent Studio, Threat Dashboard, Incident Console.

As relações entre domínios seguem um fluxo geral:

`layers` → (usa `context` + `agents` + `threatmodel`) → produz `DecisionRecord` → `truth` aplica e registra → `threatmodel` observa e recalcula → `incidents` registra anomalias → `console` expõe e permite ação humana.

---

### 3.3 Modelos centrais e invariantes

Abaixo, os principais modelos que a S25 introduz ou consolida. A modelagem concreta (ORM/SQL) deve seguir estes conceitos.

#### 3.3.1 Verdade: `TruthRecord`, `TruthChangeEvent`, `DecisionRecord`

- `TruthRecord`
  - Representa o “cartão de verdade” de uma claim (ou cluster de claims).
  - Campos essenciais:
    - `id` (UUID ou similar);
    - `claim_id` (FK);
    - `current_state` (TruthState);
    - `current_truth_score` (número ou estrutura);
    - `created_at`, `updated_at`.

- `TruthChangeEvent`
  - Representa uma mudança de estado.
  - Campos essenciais:
    - `id`;
    - `truth_record_id` (FK);
    - `from_state`, `to_state` (TruthState);
    - `reason` (string, curta mas obrigatória);
    - `policy_id`, `policy_version` (referência à PromotionPolicy);
    - `decision_record_id` (FK);
    - `created_at`.

- `DecisionRecord`
  - Conecta a decisão de verdade à cadeia de camadas e sinais.
  - Campos essenciais:
    - `id`;
    - `truth_record_id` (FK);
    - `layers_trace_id` (FK);
    - `context_snapshot_ref` (ref para ContextDossier ou equivalente);
    - `threat_signals_snapshot_ref`;
    - `committee_decisions_refs` (lista de IDs);
    - `debunk_decisions_refs`;
    - `human_decision_ref` (se houver);
    - `explanations` (lista de strings simples, legíveis por humanos);
    - `created_at`.

**Invariantes:**

- Nenhuma mudança em `TruthRecord.current_state` ocorre sem um `TruthChangeEvent`.
- Todo `TruthChangeEvent` aponta para um `DecisionRecord` válido.
- `TruthChangeEvent.from_state` deve bater com o estado anterior do `TruthRecord`.
- `DecisionRecord` sempre consegue ser ligado a um `LayersTrace` ou, em caso excepcional (manutenção manual), tem flag explícita.

#### 3.3.2 Políticas: `PromotionPolicy`, `PromotionPolicyVersion`, `PolicyEvaluationContext`

- `PromotionPolicy`
  - Entidade de alto nível (por domínio/tipo de claim).
  - Campos: `id`, `name`, `scope`, `description`, `is_active`.

- `PromotionPolicyVersion`
  - Versão concretamente aplicável.
  - Campos: `id`, `policy_id`, `version`, `definition` (JSON/YAML), `created_at`, `activated_at`, `deprecated_at`.

- `PolicyEvaluationContext`
  - Estrutura em memória, não necessariamente persistida.
  - Campos típicos: `claim`, `truth_record`, `context_dossiers`, `committee_outputs`, `debunk_outputs`, `human_inputs`, `threat_signals`, `source_stats`.

A engine exposta, por exemplo, como:

```python
Recommendation evaluate_policy(PolicyDefinition policy, PolicyEvaluationContext ctx)
```

`Recommendation` guarda `target_state`, `confidence`, `explanations`, `flags`.

#### 3.3.3 Camadas & Contexto: `LayersTrace`, `LayerExecution`, `ContextDossier`

- `LayerExecution`
  - Uma passagem por uma camada.
  - Campos: `id`, `claim_id`, `layer_name`, `input_snapshot_ref`, `output_snapshot_ref`, `context_used_ref`, `agent_version_id`, `status`, `executed_at`.

- `LayersTrace`
  - Coleção ordenada de execuções de camada.
  - Campos: `id`, `claim_id`, `executions` (relacionamento), `created_at`.

- `ContextDossier`
  - Snapshot de contexto usado por uma decisão.
  - Campos: `id`, `entity_id`, `case_id`, `claims_refs`, `facts_refs`, `time_window`, `generated_at`, `generator_version`.

**Invariantes de contexto:**

- Decisões em domínios marcados como sensíveis nunca podem ser tomadas sem um `ContextDossier` associado.
- `LayerExecution.context_used_ref` deve ser preenchido para todas as camadas que dependem de contexto.

#### 3.3.4 ThreatModel: `ThreatSignal`, `ThreatMetricSnapshot`

- `ThreatSignal`
  - Registro atômico: “algo potencialmente perigoso foi detectado aqui”.
  - Ex.: concentração de fontes, padrão de reversão, ingestão suspeita.

- `ThreatMetricSnapshot`
  - Agregação periódica de métricas; referência para painéis.

#### 3.3.5 Agents & Incident

- `Agent` / `AgentVersion` / `AgentTestRun`
  - Permitem versionar cérebro de camada, anexar KB, rodar regressões.

- `Incident` / `IncidentAction`
  - Ligam eventos de amenaza/erro a ações de contenção e correção.

---

### 3.4 Filemap back‑end (Python/FastAPI)

Abaixo, um filemap proposto e organizado, respeitando domínios e separação de responsabilidades. Nomes exatos podem ser ajustados ao repo, mas a estrutura lógica deve ser mantida.

#### 3.4.1 Núcleo de verdade (`app/truth`)

- `app/truth/__init__.py`
- `app/truth/enums.py`
  - `TruthState` e enums auxiliares.
- `app/truth/models.py`
  - `TruthRecord`, `TruthChangeEvent`, `DecisionRecord`.
- `app/truth/service.py`
  - Funções de domínio (curtas, testáveis):
    - `apply_transition(...)`;
    - `get_timeline(truth_record_id)`;
    - verificações de invariantes.
- `app/truth/repository.py`
  - Acesso ao banco.
- `app/truth/api.py`
  - Endpoints admin/dev para consulta de Truth‑DB.

- `migrations/versions/XXXX_s25_truth_models.py`
- `tests/truth/test_truth_transitions.py`
- `tests/truth/test_truth_invariants.py`

#### 3.4.2 Políticas (`app/policies`)

- `app/policies/__init__.py`
- `app/policies/models.py`
  - `PromotionPolicy`, `PromotionPolicyVersion`.
- `app/policies/schema.py`
  - Definição de esquema de políticas (pydantic, etc.).
- `app/policies/engine.py`
  - `evaluate_policy(...)` — pura, legível, testada.
- `app/policies/context_builder.py`
  - construção de `PolicyEvaluationContext` a partir de IDs.
- `app/policies/api.py`
  - listagem de políticas, versões, simulação.

- `configs/promotion_policies/global_default.yaml`
- `configs/promotion_policies/domain_politics.yaml`

- `tests/policies/test_policy_engine.py`
- `tests/policies/test_policy_simulation.py`

#### 3.4.3 Camadas & Contexto (`app/layers`, `app/context`)

- `app/layers/__init__.py`
- `app/layers/models.py`
  - `LayerExecution`, `LayersTrace`.
- `app/layers/orchestrator.py`
  - entrada única para pipeline.
- `app/layers/router.py`
  - define pipelines por domínio/tipo de claim.
- `app/layers/api.py`
  - inspeção de traces (admin/dev).

- `app/context/__init__.py`
- `app/context/models.py`
  - `ContextDossier` (persistido ou referenciado).
- `app/context/service.py`
  - geração de dossiês, com funções explícitas para entidades/casos.
- `app/context/api.py`
  - APIs para consulta de contexto.

- `tests/layers/test_pipeline_end_to_end.py`
- `tests/context/test_context_dossiers.py`

#### 3.4.4 ThreatModel (`app/threatmodel`)

- `app/threatmodel/__init__.py`
- `app/threatmodel/models.py`
  - `ThreatSignal`, `ThreatMetricSnapshot`.
- `app/threatmodel/computations.py`
  - funções de métricas (`compute_single_source_dependency`, etc.).
- `app/threatmodel/service.py`
  - orquestra cálculo periódico ou on‑demand.
- `app/threatmodel/api.py`
  - endpoints para métricas e sinais.

- `configs/threatmodel/thresholds.yaml`
- `tests/threatmodel/test_metrics_basic.py`

#### 3.4.5 Agents & Incidents (`app/agents`, `app/incidents`)

- `app/agents/__init__.py`
- `app/agents/models.py`
  - `Agent`, `AgentVersion`, `AgentTestRun`.
- `app/agents/service.py`
  - CRUD + orquestração de testes/regressão.
- `app/agents/api.py`
  - APIs do Agent Studio.

- `app/incidents/__init__.py`
- `app/incidents/models.py`
  - `Incident`, `IncidentAction`.
- `app/incidents/service.py`
  - abertura, update, fechamento.
- `app/incidents/api.py`
  - CRUD de incidentes.

- `tests/agents/test_agent_versioning.py`
- `tests/incidents/test_incident_lifecycle.py`

#### 3.4.6 Scripts de gates e ORR (`bin/`)

- `bin/s25_g0_scope_and_baseline.sh`
- `bin/s25_g1_truthstate_machine.sh`
- `bin/s25_g2_promotion_policy.sh`
- `bin/s25_g3_layers_pipeline_integrated.sh`
- `bin/s25_g4_console_and_agent_studio.sh`
- `bin/s25_g5_threatmodel_signals_and_metrics.sh`
- `bin/s25_g6_human_code_quality.sh`
- `bin/s25_g7_threat_model_coverage.sh`
- `bin/s25_orr.sh`

Cada script:

- chama comandos Python/tests específicos dos domínios;
- escreve scorecards em `out/scorecards/` e evidências em `out/evidence/`;
- nunca contém lógica de negócio relevante (apenas orquestração).

---

### 3.5 Filemap front‑end (Inspectah UI)

Assumindo `frontend/inspectah-ui/src/` como base, a S25 organiza o Console em sub‑módulos focados.

#### 3.5.1 Truth Console

- `src/truth/TruthRecordPage.tsx`
- `src/truth/components/TruthTimeline.tsx`
- `src/truth/components/ThoughtTraceView.tsx`
- `src/truth/components/DecisionTraceView.tsx`
- `src/truth/hooks/useTruthRecord.ts`

Função: permitir inspeção profunda de uma claim/caso, com TruthState, timeline, camadas e contexto.

#### 3.5.2 Agent Studio

- `src/agents/AgentStudioPage.tsx`
- `src/agents/components/AgentSidebar.tsx`
- `src/agents/components/AgentVersionEditor.tsx`
- `src/agents/components/AgentKBUploader.tsx`
- `src/agents/components/AgentTestRunner.tsx`
- `src/agents/hooks/useAgents.ts`
- `src/agents/hooks/useAgentTests.ts`

Função: operar cérebro de camada como objeto de primeira classe, com versões e regressões.

#### 3.5.3 Threat Dashboard & Incidentes

- `src/threat/ThreatDashboardPage.tsx`
- `src/threat/components/ThreatMetricCard.tsx`
- `src/threat/components/ThreatSignalsTable.tsx`

- `src/incidents/IncidentListPage.tsx`
- `src/incidents/IncidentDetailPage.tsx`
- `src/incidents/components/IncidentTimeline.tsx`

#### 3.5.4 Integração com layout/admin

- `src/routes/admin.tsx`
  - inclui rotas novas para Truth Console, Agent Studio, Threat Dashboard, Incident Console.

- `src/api/truth.ts`, `src/api/agents.ts`, `src/api/incidents.ts`, `src/api/threat.ts`
  - wrappers tipos‑seguros para as APIs backend.

Padrão de código front‑end:

- componentes pequenos e compostáveis;
- lógica de dados em hooks;
- uso consistente de tipos/DTOs espelhando os modelos backend.

---

### 3.6 Fluxos arquiteturais críticos

#### 3.6.1 Fluxo: claim → TruthState → Console

1. Uma claim é criada/atualizada na ingestão e enviada ao domínio `layers`.
2. `layers.orchestrator` roda o pipeline configurado:
   - chama agentes, comitês, Debunker, humano;
   - registra `LayerExecution` e monta `LayersTrace`.
3. `context.service` gera `ContextDossier` para Entidade/Caso relevante.
4. `policies.context_builder` monta `PolicyEvaluationContext` com claim, dossiês, outputs de camadas, sinais de ThreatModel.
5. `policies.engine.evaluate_policy` devolve `Recommendation`.
6. `truth.service.apply_transition` aplica a recomendação (se válida), grava `TruthChangeEvent` e `DecisionRecord`.
7. `threatmodel.service` observa a nova decisão e recalcula métricas relevantes.
8. Console (TruthRecordPage) consulta `TruthRecord`, `TruthChangeEvents`, `LayersTrace`, `DecisionRecord` e `ContextDossier`, exibindo ThoughtTrace/DecisionTrace.

#### 3.6.2 Fluxo: cenário adversarial (ThreatModel em ação)

1. Scripts de G7 injetam cenários adversariais (flood, virada sem evidência etc.).
2. Sistema processa cenários pelo pipeline normal.
3. `threatmodel.computations` detectam anomalias (ex.: `M_adv_single_source_dependency` alto).
4. Threat dashboard exibe métricas; incidentes podem ser abertos automaticamente ou por operadores.
5. `incidents.service` registra incidente, vinculando TruthRecords, políticas, agentes e dossiês.
6. Operadores usam Console para revisar decisões, ajustar políticas/agentes, e eventualmente disparar ações (ex.: segurar promoções em domínio afetado).

Esses fluxos são a base para os gates S25_G3, S25_G4, S25_G5 e S25_G7.

---

### 3.7 Padrões de código humano e manutenção

Para garantir que a S25 não se transforme em “caixa‑preta sagrada”, a arquitetura é acompanhada de padrões concretos de código:

1. **Módulos pequenos e focados**
   - Um arquivo, uma ideia central (domínio truth, engine de política, etc.).

2. **Funções coesas e nomeadas por intenção**
   - Nada de funções enormes; dividir por responsabilidade.

3. **Type hints e docstrings cirúrgicos**
   - Especialmente em pontos de verdade/política/camadas.

4. **Separação domínio/infraestrutura**
   - Regra de negócio não depende de HTTP/ORM diretamente; estas ficam em camadas de borda.

5. **Testes próximos dos domínios**
   - `tests/truth`, `tests/policies`, `tests/layers`, etc., com cenários pequenos, explícitos.

6. **Ausência de lógica crítica em prompts não versionados**
   - prompts de agentes fazem parte de `AgentVersion` e passam por teste/regressão.

Esses padrões são verificados pelo gate S25_G6 (human code quality) e devem ser perceptíveis ao abrir o repo.

---

### 3.8 Compatibilidade com Fase 2 (Sistema de Blocos)

Mesmo sem implementar blocos e blockchain agora, a arquitetura da S25 é desenhada como se a Fase 2 fosse certa:

- `TruthRecord` e `TruthChangeEvent` funcionam como blocos lógicos encadeáveis;
- `DecisionRecord`, `LayersTrace`, `ContextDossier` e `ThreatSignal` formam o “payload de prova” de decisões futuras;
- IDs estáveis, timestamps, referências cruzadas e relações claras permitem hashing e ancoragem;
- o filemap separa domínios de forma que a camada de blocos possa “envelopar” a atual Truth‑DB sem reescrever tudo.

Este capítulo 3, em conjunto com os Capítulos 0, 0.A, 0.5, 0.5.A, 1, 2 e 7, entrega ao Codex e ao time um mapa completo: **onde cada parte da Verdade/Fato v1.5 vive**, como elas se conectam, e quais restrições de legibilidade e governança não podem ser violadas durante a implementação da Sprint 25.

