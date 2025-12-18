# S41 — Plano Tecnico v4.0 (Ciclo 2/3)
## Refinamento Exaustivo de Tasks

> **Data:** 2025-12-16
> **Base:** v4.0 Ciclo 1 (289 tasks, 100% coverage)
> **Foco:** DONE criteria detalhados, dependencias validadas, testes

---

# ANALISE DE DEPENDENCIAS CRITICAS

## Grafo de Dependencias (Critical Path)

```
W0.01 (verificar S40)
  │
  └──> W0.5.01 (CVI schema specs)
         │
         ├──> W1.01 (IncentiveExtractor)
         │      │
         │      └──> W1.19 (eventos IncentiveSignal*)
         │             │
         │             └──> W2.01 (pipeline sinais)
         │
         ├──> W1.02 (ActorProfiler)
         │      │
         │      └──> W1.22 (actor_profile schema)
         │
         └──> W1.03 (FieldAssembler)
                │
                ├──> W1.20 (modo batch)
                │
                └──> W1.04 (ImpactAnalyzer)
                       │
                       └──> W3.01 (CVIQueryService)
                              │
                              ├──> W3.23 (GetDecisionContextIncentives)
                              │
                              ├──> W3.02 (CVIAdminService)
                              │      │
                              │      └──> W3.24 (upsert_incentive_signal)
                              │
                              └──> W5.01 (integracao Explain)
                                     │
                                     └──> W6.01 (CVIOverlayPanel)
                                            │
                                            └──> W6.21 (maquina estados)
```

---

# TASKS REFINADAS COM DONE CRITERIA DETALHADOS

## Wave W0 — Baseline (14 tasks)

### W0.01 — Verificar estabilidade S40

```yaml
task_id: W0.01
title: "Verificar estabilidade baseline S40"
type: CHECK
priority: P0
gate: G29

dependencies: []

done_criteria:
  - S40 baseline acessivel (ou fallback sintetico configurado)
  - IDs estaveis: case_id, theme_id, actor_id disponiveis
  - Trilhas de decisao existentes para piloto
  - Documentar estado em out/evidence/S41_baseline.json

test_requirements:
  - Test: query case_id retorna dados
  - Test: query theme_id retorna dados
  - Test: query actor_id retorna dados

evidence:
  - out/evidence/S41_baseline.json
  - logs de verificacao

owner: ACE Exec
estimated_complexity: LOW
```

### W0.02 — Definir conjunto piloto

```yaml
task_id: W0.02
title: "Definir conjunto piloto (temas/casos)"
type: CONFIG
priority: P0
gate: G26

dependencies:
  - W0.01

done_criteria:
  - Minimo 2 temas selecionados
  - Minimo 4 casos por tema (8 total)
  - Minimo 10 atores mapeados
  - Minimo 50 sinais de incentivo disponiveis
  - Documentar em data/cvi_pilot/config.yaml

config_schema:
  themes:
    - theme_id: string
      domain: D1|D2|D3|D4
      cases:
        - case_id: string
          actors: [actor_id]
          signals_count: int

evidence:
  - data/cvi_pilot/config.yaml
  - data/cvi_pilot/*/

owner: ACE Exec
estimated_complexity: MEDIUM
```

---

## Wave W1 — CVI Core (22 tasks refinadas)

### W1.01 — IncentiveExtractor

```yaml
task_id: W1.01
title: "Implementar IncentiveExtractor"
type: CODE
priority: P0
gate: G26

dependencies:
  - W0.5.01 (schema specs)

done_criteria:
  - Classe IncentiveExtractor em app/cvi/extractors/incentive_extractor.py
  - Metodos:
    - extract_from_source(source_ref) -> List[IncentiveSignal]
    - normalize_signal(raw_signal) -> IncentiveSignal
    - resolve_actor_id(entity) -> actor_id | None
    - resolve_theme_id(context) -> theme_id | None
  - Suporta source_types: public_record, declared, decision_history, manual_input
  - Marca qualidade_score por fonte
  - Gera eventos via W1.19

test_requirements:
  - tests/cvi/test_incentive_extractor.py
  - Test: extract retorna sinais normalizados
  - Test: resolve_actor_id funciona com IDs P2/P3
  - Test: sinais duplicados sao detectados
  - Coverage: >= 95%

evidence:
  - Codigo em app/cvi/extractors/
  - Testes passando

owner: ACE Exec
estimated_complexity: HIGH
```

### W1.02 — ActorProfiler

```yaml
task_id: W1.02
title: "Implementar ActorProfiler"
type: CODE
priority: P0
gate: G26

dependencies:
  - W0.5.01

done_criteria:
  - Classe ActorProfiler em app/cvi/profiler/actor_profiler.py
  - Metodos:
    - get_profile(actor_id) -> ActorProfile
    - update_profile(actor_id, data) -> ActorProfile
    - calculate_influence_weight(actor_id) -> float
  - NAO atribui vetores de incentivo (apenas contexto)
  - Expoe dados para calculo de alpha_a

test_requirements:
  - tests/cvi/test_actor_profiler.py
  - Test: get_profile retorna perfil completo
  - Test: influence_weight calculado corretamente
  - Test: update_profile gera audit_event
  - Coverage: >= 95%

evidence:
  - Codigo em app/cvi/profiler/
  - Testes passando

owner: ACE Exec
estimated_complexity: MEDIUM
```

### W1.03 — FieldAssembler

```yaml
task_id: W1.03
title: "Implementar FieldAssembler (core)"
type: CODE
priority: P0
gate: G26

dependencies:
  - W1.01
  - W1.02
  - W0.5.01

done_criteria:
  - Classe FieldAssembler em app/cvi/assembler/field_assembler.py
  - Metodos:
    - compute_vector(actor_id, theme_id, case_id, signals) -> IncentiveVector
    - compute_field(theme_id, case_id, window) -> CVIField
    - create_snapshot(field, timestamp) -> CVISnapshot
  - Calcula vetores por classe (econ, pol, rep, inst, leg)
  - Calcula intensidades I_atk
  - Calcula risco de mascaramento R_mask

test_requirements:
  - tests/cvi/test_field_assembler.py
  - Test: compute_vector retorna vetor por classe
  - Test: compute_field agrega vetores de todos atores
  - Test: snapshot inclui provenance completo
  - Coverage: >= 95%

evidence:
  - Codigo em app/cvi/assembler/
  - Testes passando

owner: ACE Exec
estimated_complexity: HIGH
```

### W1.19 — Eventos IncentiveSignal

```yaml
task_id: W1.19
title: "Implementar eventos IncentiveSignalAdded/Updated/Retracted"
type: CODE
priority: P0
gate: G26

dependencies:
  - W1.01

done_criteria:
  - Eventos definidos em app/cvi/events/
  - IncentiveSignalAdded(signal_id, actor_id, theme_id, case_id, payload)
  - IncentiveSignalUpdated(signal_id, old_payload, new_payload)
  - IncentiveSignalRetracted(signal_id, reason)
  - Publisher em IncentiveExtractor
  - Schema de evento documentado em schemas/cvi_events_v1.json

test_requirements:
  - tests/cvi/test_events.py
  - Test: IncentiveSignalAdded publicado em create
  - Test: IncentiveSignalUpdated publicado em update
  - Test: IncentiveSignalRetracted publicado em delete
  - Test: Consumer de teste recebe eventos

evidence:
  - Codigo em app/cvi/events/
  - Schema em schemas/
  - Testes passando

owner: ACE Exec
estimated_complexity: MEDIUM
```

### W1.20 — FieldAssembler modo batch

```yaml
task_id: W1.20
title: "Implementar FieldAssembler modo batch (rebuild)"
type: CODE
priority: P0
gate: G26

dependencies:
  - W1.03

done_criteria:
  - Metodo rebuild_fields(theme_id, window_start, window_end) implementado
  - Recalcula todos os campos para janela temporal
  - Compara com campos atuais e registra diff
  - Gera novos snapshots se diferenca > threshold
  - Suporta execucao via job scheduler

test_requirements:
  - tests/cvi/test_field_assembler_batch.py
  - Test: rebuild recalcula campos corretamente
  - Test: diff entre online e batch e registrado
  - Test: job pode ser agendado
  - Coverage: >= 95%

evidence:
  - Codigo em app/cvi/assembler/
  - Job script em bin/cvi_rebuild_batch.py

owner: ACE Exec
estimated_complexity: HIGH
```

---

## Wave W3 — Services/APIs (25 tasks refinadas)

### W3.23 — GetDecisionContextIncentives

```yaml
task_id: W3.23
title: "Implementar GetDecisionContextIncentives para MQV/MAC"
type: CODE
priority: P0
gate: G26

dependencies:
  - W3.01 (CVIQueryService)

done_criteria:
  - Endpoint GET /api/v1/cvi/decision-context/{decision_id}
  - Input: decision_id (referencia MQV/MAC)
  - Output:
    - field_id, snapshot_ts
    - aggregate_field_vector V_tk
    - actors com intensities I_atk
    - concentration_index
    - model_version
  - Registra uso em DecisionRecord se aplicavel

contract:
  request:
    path: /api/v1/cvi/decision-context/{decision_id}
    method: GET
    headers:
      Authorization: Bearer <token>
  response:
    status: 200
    body:
      field_id: string
      snapshot_ts: timestamp
      aggregate_vector: [float]
      actors:
        - actor_id: string
          intensity_total: float
          intensities_by_class:
            econ: float
            pol: float
            rep: float
            inst: float
            leg: float
      concentration_hhi: float
      model_version: string

test_requirements:
  - tests/api/test_cvi_decision_context.py
  - Test: endpoint retorna dados corretos
  - Test: authorization required
  - Test: decision_id invalido retorna 404
  - Contract test com schema validation

evidence:
  - Codigo em app/api/cvi_routes.py
  - OpenAPI spec atualizado

owner: ACE Exec
estimated_complexity: MEDIUM
```

### W3.24 — upsert_incentive_signal

```yaml
task_id: W3.24
title: "Implementar upsert_incentive_signal com governanca"
type: CODE
priority: P0
gate: G28

dependencies:
  - W3.02 (CVIAdminService)
  - W4.01 (RBAC)

done_criteria:
  - Endpoint POST /api/v1/cvi/admin/signals
  - Somente role truth_admin pode criar/editar
  - Gera audit_event com autor, motivo, diff
  - Dispara IncentiveSignalAdded/Updated
  - Validacao de schema obrigatoria

contract:
  request:
    path: /api/v1/cvi/admin/signals
    method: POST
    headers:
      Authorization: Bearer <token>
    body:
      actor_id: string
      theme_id: string
      case_id: string | null
      class: econ|pol|rep|inst|leg
      source_type: string
      source_ref: string
      value_descriptor: string
      reason: string (obrigatorio)
  response:
    status: 201
    body:
      signal_id: string
      audit_event_id: string

test_requirements:
  - tests/api/test_cvi_admin_signals.py
  - Test: criar sinal como truth_admin
  - Test: rejeitar como ops_ingest (403)
  - Test: audit_event gerado
  - Test: evento IncentiveSignalAdded publicado

evidence:
  - Codigo em app/api/cvi_routes.py
  - Audit trail verificavel

owner: ACE Exec
estimated_complexity: MEDIUM
```

---

## Wave W4 — Governance (38 tasks refinadas)

### W4.34 — Catalogo completo de papeis P5-5

```yaml
task_id: W4.34
title: "Criar catalogo completo de papeis P5-5"
type: CODE
priority: P0
gate: G28

dependencies:
  - W4.01 (RBAC base)

done_criteria:
  - Arquivo app/governance/roles/role_catalog.py
  - Enum GovernanceRole com todos os papeis
  - Cada papel com:
    - role_id: string
    - display_name: string
    - description: string
    - allowed_actions: List[Action]
    - forbidden_actions: List[Action]
    - incompatible_with: List[GovernanceRole]
    - nomination_rules: string
    - mandate_duration: Optional[Duration]
  - Papeis obrigatorios:
    - GovernanceActor
    - Judge
    - PanelMember
    - Chair
    - Observer
    - ExternalAuditor
    - StakeholderRepresentative
    - SystemAdmin
    - Operator

test_requirements:
  - tests/governance/test_role_catalog.py
  - Test: todos os papeis definidos
  - Test: incompatibilidades corretas
  - Test: allowed/forbidden actions completos
  - Coverage: 100%

evidence:
  - Codigo em app/governance/roles/
  - Documentacao em docs/governance/RBAC.md

owner: ACE Exec
estimated_complexity: MEDIUM
```

### W4.36 — Validacao de acumulo de poderes

```yaml
task_id: W4.36
title: "Implementar validacao de acumulo de poderes incompativeis"
type: CODE
priority: P0
gate: G28

dependencies:
  - W4.34 (catalogo papeis)
  - W4.35 (poderes)

done_criteria:
  - Classe RoleValidator em app/governance/validators/role_validator.py
  - Metodo validate_role_assignment(user_id, new_role) -> ValidationResult
  - Verifica incompatibilidades:
    - Chair != SystemAdmin
    - Judge != Stakeholder (em mesmo caso)
    - Auditor != Operator
  - Se violacao: bloqueia + gera audit_event
  - Integrado com middleware de autorizacao

test_requirements:
  - tests/governance/test_role_validator.py
  - Test: Chair + SystemAdmin bloqueado
  - Test: Judge + Stakeholder bloqueado
  - Test: audit_event gerado em violacao
  - Test: atribuicao valida permitida
  - Coverage: 100%

evidence:
  - Codigo em app/governance/validators/
  - Testes passando

owner: ACE Exec
estimated_complexity: MEDIUM
```

---

## Wave W6 — Frontend CVI (24 tasks refinadas)

### W6.21 — Maquina de estados CVIOverlay

```yaml
task_id: W6.21
title: "Implementar maquina de estados completa CVIOverlay"
type: CODE
priority: P0
gate: G27

dependencies:
  - W6.01 (CVIOverlayPanel)

done_criteria:
  - Arquivo frontend/inspectah-ui/src/features/cvi/hooks/useCVIState.ts
  - Estados implementados:
    - idle: inicial, aguardando trigger
    - loading: buscando snapshot
    - ready: dados carregados com sucesso
    - no_data: cobertura insuficiente
    - unauthorized: sem permissao (403)
    - error: erro de rede/servidor
    - stale: snapshot desatualizado (pct_atualizado < threshold)
    - pending_recompute: aguardando recalculo batch
  - Transicoes corretas entre estados
  - UI adequada para cada estado

test_requirements:
  - tests/features/cvi/useCVIState.test.ts
  - Test: transicao idle -> loading
  - Test: transicao loading -> ready
  - Test: transicao loading -> no_data
  - Test: transicao loading -> unauthorized
  - Test: ready -> stale quando pct_atualizado baixo
  - Coverage: >= 90%

evidence:
  - Codigo em frontend/
  - Testes passando

owner: ACE Exec
estimated_complexity: MEDIUM
```

---

# DEPENDENCIAS ENTRE WAVES (VALIDADAS)

| Wave | Depende De | Pode Paralelo Com |
|------|------------|-------------------|
| W0 | - | - |
| W0.5 | W0 | - |
| W1 | W0.5 | - |
| W2 | W1 | - |
| W3 | W2 | W4 (parcial) |
| W4 | W0.5 | W3 (parcial), W5 (parcial) |
| W5 | W3 | W4 |
| W6 | W3, W5 | W7 |
| W7 | W4 | W6 |
| W8 | W6, W7 | - |
| W9 | W8 | W10 |
| W10 | W0.5 | W1-W9 |
| W11 | W1-W10 | - |
| W12 | W11 | - |

---

# GRUPOS DE PARALELISMO

## Grupo 1 (Early Parallel)
- W3 (services) e W4 (governance) podem iniciar juntas apos W2

## Grupo 2 (Frontend Parallel)
- W6 (FE CVI) e W7 (FE governance) podem rodar em paralelo apos W3/W4

## Grupo 3 (Continuous Parallel)
- W10 (observabilidade) pode rodar durante todo o sprint

---

# METRICAS DE QUALIDADE

| Metrica | Target | Minimo |
|---------|--------|--------|
| Test coverage total | 97% | 95% |
| Unit tests per CODE task | >= 5 | >= 3 |
| Contract tests per endpoint | >= 3 | >= 2 |
| E2E tests per journey | >= 2 | >= 1 |
| Documentation per component | Complete | Skeleton |

---

**Gerado por:** Sprint Planner Tecnico v7
**Ciclo:** 2/3
**Data:** 2025-12-16
