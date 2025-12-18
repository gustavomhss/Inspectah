# Sprint 42 — Plano v5.0 SENIOR ENTERPRISE

> Reestruturacao completa com metodologia de engenharia senior
> Corrige os 15 problemas estruturais identificados na critica

---

## ESTRUTURA DO PLANO

```
Phase 0: Architecture & Design       [OBRIGATORIA - Sem codigo]
Phase 1: MAC Simulate Core           [Feature completa]
Phase 2: MAC Batch                   [Feature completa]
Phase 3: Adiabatic Plan              [Feature completa]
Phase 4: MI/Experiences Exposure     [Feature completa]
Phase 5: Frontend Integration        [Feature completa]
Phase 6: Hardening & Production      [Chaos, Load, Security]
Phase 7: ORR & Bundle                [Evidencias finais]
```

---

## DEFINITION OF DONE (DoD) — OBRIGATORIO PARA TODAS AS FEATURES

### DoD Nivel 1: Codigo

- [ ] Implementacao completa conforme spec
- [ ] Type hints em 100% do codigo
- [ ] Docstrings em todas funcoes publicas
- [ ] Sem warnings de linter (ruff/mypy)
- [ ] Complexity score < 10 por funcao

### DoD Nivel 2: Testes

- [ ] Testes unitarios: >= 95% coverage do modulo
- [ ] Testes de integracao: todos fluxos principais
- [ ] Testes de erro: todos error paths documentados
- [ ] Testes de contrato: validacao contra OpenAPI spec
- [ ] Testes de performance: baseline estabelecido

### DoD Nivel 3: Observabilidade

- [ ] Metricas Prometheus definidas e exportadas
- [ ] Logs estruturados com correlation_id
- [ ] Spans de tracing configurados
- [ ] Alertas correspondentes criados
- [ ] Dashboard panel adicionado

### DoD Nivel 4: Seguranca

- [ ] Threat model review (se aplicavel)
- [ ] Input validation implementada
- [ ] RBAC configurado (se aplicavel)
- [ ] Audit logging ativo
- [ ] Security tests passando

### DoD Nivel 5: Documentacao

- [ ] ADR atualizado (se decisao arquitetural)
- [ ] README do modulo atualizado
- [ ] Runbook entry criado
- [ ] API docs atualizados

### DoD Nivel 6: Review

- [ ] Code review por 2 engenheiros
- [ ] Security review (se sensivel)
- [ ] Product review (se UX)
- [ ] Feature flag configurada

---

## PHASE 0: ARCHITECTURE & DESIGN

**Duracao:** Primeira semana do sprint
**Objetivo:** Todas as decisoes arquiteturais tomadas e documentadas ANTES de codigo
**Bloqueador:** Nenhum codigo de implementacao comeca sem Phase 0 completa

### P0-ADR: Architecture Decision Records

| ID | Titulo | Decisao | Consequencias |
|----|--------|---------|---------------|
| ADR-001 | SimulationStore vs TruthDB | Separar stores | Isolamento, TTL independente, sem "verdade por simulacao" |
| ADR-002 | Determinismo Strategy | seed + ordenacao + T=0 | Replay 100%, hash verificavel |
| ADR-003 | Batch Execution Model | Jobs assincronos com polling/stream | UI responsiva, cancel possivel |
| ADR-004 | MI RBAC Model | 3 roles (ops/reviewer/council) | Granularidade suficiente, auditavel |
| ADR-005 | Evidence Redaction | Redacted by default | Privacidade garantida, opt-in para detalhes |
| ADR-006 | API Versioning | Path-based (/v1/, /v2/) | Clareza, backward compat |

**Entregaveis:**
- `docs/architecture/adr/ADR-001-simulation-store.md`
- `docs/architecture/adr/ADR-002-determinism.md`
- `docs/architecture/adr/ADR-003-batch-execution.md`
- `docs/architecture/adr/ADR-004-mi-rbac.md`
- `docs/architecture/adr/ADR-005-evidence-redaction.md`
- `docs/architecture/adr/ADR-006-api-versioning.md`

### P0-SPIKE: Provas de Conceito

| ID | Objetivo | Criterio de Sucesso | Descartavel |
|----|----------|---------------------|-------------|
| SPIKE-001 | Validar replay deterministico | 1000 replays identicos | Sim |
| SPIKE-002 | Validar streaming de batch progress | SSE funcional com cancel | Sim |
| SPIKE-003 | Validar RBAC com redaction | 3 roles, dados redatados corretos | Sim |

**Entregaveis:**
- `spikes/s42-spike-001-determinism/` (codigo descartavel + findings.md)
- `spikes/s42-spike-002-streaming/`
- `spikes/s42-spike-003-rbac/`

### P0-CONTRACT: API Contracts (OpenAPI First)

**REGRA:** OpenAPI spec ANTES de implementacao. Implementacao valida contra spec.

| Endpoint | Spec File | Status |
|----------|-----------|--------|
| POST /api/v1/mac/simulate | `openapi/mac-simulate.yaml` | Draft -> Review -> Approved |
| GET /api/v1/mac/simulations/{id} | `openapi/mac-simulations.yaml` | Draft -> Review -> Approved |
| POST /api/v1/mac/simulations/batch | `openapi/mac-batch.yaml` | Draft -> Review -> Approved |
| GET /api/v1/mac/adiabatic-plans | `openapi/mac-adiabatic.yaml` | Draft -> Review -> Approved |
| GET /api/v1/mi/patterns | `openapi/mi-patterns.yaml` | Draft -> Review -> Approved |

**Entregaveis:**
- `openapi/s42_mac_api_v1.yaml` (spec completa, validada)
- `schemas/` (JSON Schemas extraidos)
- Contract tests baseline

### P0-THREAT: Threat Modeling

| Asset | Threats | Controls | Priority |
|-------|---------|----------|----------|
| MI Data | Unauthorized access, Data leak | RBAC, Redaction, Audit | CRITICAL |
| Simulation Results | Confusion with production | Disclaimers, Namespace separation | HIGH |
| Policy Files | Tampering, Injection | Validation, Signing | HIGH |
| Batch Jobs | Resource exhaustion, DoS | Rate limiting, Quotas | MEDIUM |

**Entregaveis:**
- `docs/security/threat-model-s42.md`
- Security requirements por feature

### P0-DEPS: Dependency Mapping

| Dependency | SLA Target | Timeout | Fallback Strategy | Circuit Breaker |
|------------|------------|---------|-------------------|-----------------|
| TruthDB | 99.99% | 100ms | None (fail) | Yes (5 failures) |
| PolicyService | 99.9% | 500ms | Cached policy | Yes (3 failures) |
| SignalsService | 99.5% | 1s | Stale signals with warning | Yes (5 failures) |
| MIService | 99% | 2s | Empty MI refs | Yes (10 failures) |

**Entregaveis:**
- `docs/architecture/dependency-map.md`
- Circuit breaker configs

### P0-DATA: Data Governance Plan

| Dataset | Source | Quality Checks | Lineage | Retention | PII |
|---------|--------|----------------|---------|-----------|-----|
| gold_standard | Curated | Schema, Completeness | Git tracked | Indefinite | No |
| adversarial | Generated | Schema, Balance | Git tracked | Indefinite | No |
| edge_cases | Manual | Schema | Git tracked | Indefinite | No |
| simulation_runs | Runtime | Schema | DB + manifest | 90 days | Possible |

**Entregaveis:**
- `docs/data/data-governance.md`
- `docs/data/data-catalog.md`
- PII scanning rules

### P0-CAPACITY: Capacity Planning

| Metric | Expected | Peak | Target Headroom |
|--------|----------|------|-----------------|
| Simulations/hour | 100 | 500 | 2x peak = 1000 |
| Batch runs/day | 10 | 50 | 2x peak = 100 |
| Concurrent users | 20 | 100 | 2x peak = 200 |
| Dataset size | 1100 cases | 5000 cases | 2x = 10000 |

**Load Test Targets:**
- Sustained: 100 req/s for 1h
- Stress: 500 req/s for 10min
- Soak: 50 req/s for 24h
- Spike: 1000 req/s for 1min

**Entregaveis:**
- `docs/performance/capacity-planning.md`
- Load test configs

### P0-INCIDENT: Incident Readiness Plan

| Severity | Response Time | Escalation | Examples |
|----------|---------------|------------|----------|
| SEV1 (Critical) | 15min | Eng Lead + Product | Data breach, System down |
| SEV2 (High) | 1h | On-call + Backup | Batch failing, Determinism broken |
| SEV3 (Medium) | 4h | On-call | Latency degraded, Alerts firing |
| SEV4 (Low) | 24h | Ticket | UI glitch, Minor bug |

**Entregaveis:**
- `docs/runbooks/incident-response-plan.md`
- `docs/runbooks/escalation-matrix.md`
- `docs/runbooks/communication-templates.md`
- `docs/runbooks/post-mortem-template.md`

---

## PHASE 1: MAC SIMULATE CORE

**Objetivo:** Feature completa de simulacao unitaria (dry-run)
**Gate:** G30

### P1-F001: MacEngine Core

**Descricao:** Motor de avaliacao que calcula custos e recomenda acao.

**Inclui (DoD completo):**

```
Codigo:
- app/mac/engine.py
  - MacEngine.__init__(policy_loader, signals_client)
  - MacEngine.evaluate(allegation_id, candidate_transition, options) -> MacEvaluation
  - MacEngine._calculate_costs(signals, policy) -> CostBreakdown
  - MacEngine._apply_hard_caps(action, domain) -> HardCapResult
  - MacEngine._apply_hysteresis(scores, history) -> AdjustedScores

Testes (JUNTO com codigo):
- tests/mac/test_engine.py
  - test_evaluate_happy_path_promote
  - test_evaluate_happy_path_demote
  - test_evaluate_happy_path_maintain
  - test_evaluate_hard_cap_blocks_action
  - test_evaluate_hysteresis_adjusts_threshold
  - test_evaluate_signals_expired_error
  - test_evaluate_policy_not_found_error
  - test_evaluate_timeout_error
  - test_evaluate_determinism_100_replays
  - test_evaluate_costs_correct_weights
  - test_evaluate_all_modes (NORMAL, ENDURECIDO, EMERGENCIA)
  (minimo 15 testes)

Observabilidade:
- Metrica: mac_engine_evaluate_duration_seconds{mode, domain, action}
- Metrica: mac_engine_evaluate_total{mode, domain, action, status}
- Metrica: mac_engine_hard_cap_triggered_total{domain, cap_id}
- Log: evaluate_started, evaluate_completed, evaluate_failed (com correlation_id)
- Span: mac.engine.evaluate

Seguranca:
- Input validation em todos parametros
- Nao expor detalhes internos em erros

Documentacao:
- Docstrings completas
- README em app/mac/
```

**Criterio de Aceite:**
- [ ] Todos os testes passam
- [ ] Coverage >= 95%
- [ ] Metricas exportando
- [ ] Logs estruturados
- [ ] Code review aprovado

### P1-F002: Determinism Module

**Descricao:** Garantir replay 100% com T=0.

**Inclui:**

```
Codigo:
- app/mac/determinism.py
  - DeterministicContext(seed)
  - deterministic_sort(items, key)
  - deterministic_random(seed, n)
  - verify_determinism(func, inputs, n_replays=100) -> bool

Testes:
- tests/mac/test_determinism.py
  - test_context_same_seed_same_result (1000x)
  - test_context_different_seed_different_result
  - test_sort_deterministic
  - test_random_deterministic
  - test_verify_catches_non_determinism
  - test_verify_passes_deterministic_func
  (minimo 10 testes)

Observabilidade:
- Metrica: mac_determinism_verification_total{result}
- Alerta: mac_determinism_failure (ANY failure = critical)
```

### P1-F003: Manifest & Lineage

**Descricao:** RunManifest com provenance completa.

**Inclui:**

```
Codigo:
- app/mac/manifest.py
  - RunManifest dataclass (todos campos conforme spec)
  - ManifestBuilder.build(simulation, context) -> RunManifest
  - ManifestHasher.hash(manifest) -> str (deterministic)
  - ManifestValidator.validate(manifest) -> ValidationResult

Testes:
- tests/mac/test_manifest.py
  - test_manifest_all_fields_present
  - test_manifest_hash_deterministic
  - test_manifest_hash_changes_with_input
  - test_validator_rejects_incomplete
  - test_validator_accepts_complete
  - test_manifest_serialization_roundtrip
  (minimo 10 testes)

Schemas:
- schemas/run_manifest_v1.json
```

### P1-F004: Simulation Endpoint

**Descricao:** POST /api/v1/mac/simulate

**Inclui:**

```
Codigo:
- app/api/mac_routes.py
  - POST /api/v1/mac/simulate
  - Request validation contra OpenAPI
  - Response validation contra OpenAPI
  - Error handling com codes estaveis

Testes:
- tests/api/test_mac_simulate.py
  - test_simulate_returns_200_valid_request
  - test_simulate_returns_400_invalid_json
  - test_simulate_returns_400_missing_field
  - test_simulate_returns_404_policy_not_found
  - test_simulate_returns_408_timeout
  - test_simulate_response_matches_schema
  - test_simulate_deterministic_replay
  - test_simulate_includes_manifest
  (minimo 15 testes, incluindo contract tests)

Observabilidade:
- Metrica: http_request_duration_seconds{endpoint="/api/v1/mac/simulate"}
- Span: http.mac.simulate

Feature Flag:
- FLAG: mac_simulate_enabled (default: false em prod)
```

### P1-F005: Performance Baseline

**Descricao:** Estabelecer e validar performance targets.

**Inclui:**

```
Testes de Performance:
- tests/performance/test_simulate_perf.py
  - test_simulate_p50_under_200ms
  - test_simulate_p95_under_500ms
  - test_simulate_p99_under_2s
  - test_simulate_throughput_100rps

Baseline:
- performance/baselines/simulate_v1.json (p50, p95, p99, throughput)

CI Gate:
- Falha se performance degradar > 10% vs baseline
```

**Gate G30 Checklist:**
- [ ] P1-F001 completo (DoD)
- [ ] P1-F002 completo (DoD)
- [ ] P1-F003 completo (DoD)
- [ ] P1-F004 completo (DoD)
- [ ] P1-F005 completo (DoD)
- [ ] Integration tests E2E passam
- [ ] Scorecard G30 gerado
- [ ] Evidencias em out/evidence/S42_G30/

---

## PHASE 2: MAC BATCH

**Objetivo:** Feature completa de simulacao em lote
**Gate:** G31

### P2-F001: Batch Runner

**Descricao:** Execucao de batch com progress, cancel, streaming.

**Inclui (DoD completo):**

```
Codigo:
- app/mac/batch_runner.py
  - BatchRunner(engine, config)
  - BatchRunner.start(dataset, options) -> batch_run_id
  - BatchRunner.get_status(batch_run_id) -> BatchStatus
  - BatchRunner.cancel(batch_run_id, reason) -> bool
  - BatchRunner.stream_progress(batch_run_id) -> AsyncIterator[Progress]

Testes:
- test_batch_start_creates_run
- test_batch_status_transitions (queued->running->succeeded)
- test_batch_status_transitions (queued->running->failed)
- test_batch_status_transitions (running->canceled)
- test_batch_cancel_stops_execution
- test_batch_cancel_records_reason
- test_batch_progress_updates
- test_batch_stream_progress_sse
- test_batch_parallel_isolation
- test_batch_determinism (same dataset, same result)
- test_batch_recovery_from_interrupt
- test_batch_retry_transient_failures
(minimo 20 testes)

Observabilidade:
- Metrica: mac_batch_runs_total{status, dataset}
- Metrica: mac_batch_duration_seconds{dataset}
- Metrica: mac_batch_progress{batch_run_id} (gauge)
- Alerta: mac_batch_failure_rate > 10%
```

### P2-F002: Dataset Loader

**Descricao:** Carregar e validar datasets.

**Inclui:**

```
Codigo:
- app/mac/dataset_loader.py
  - DatasetLoader.load(dataset_id) -> Dataset
  - DatasetLoader.validate(dataset) -> ValidationResult
  - DatasetLoader.slice(dataset, filter) -> Dataset

Data Quality Checks:
- Schema validation
- Completeness check
- Uniqueness check
- Balanced distribution check

Testes:
- test_load_valid_dataset
- test_load_invalid_schema_error
- test_load_corrupt_file_error
- test_validate_checks_schema
- test_validate_checks_completeness
- test_slice_by_domain
- test_slice_by_type
(minimo 10 testes)
```

### P2-F003: Scorecard Generator

**Descricao:** Gerar scorecards com todos campos.

**Inclui:**

```
Codigo:
- app/mac/scorecard.py
  - ScorecardGenerator.generate(batch_result, targets) -> Scorecard
  - Scorecard dataclass com TODOS campos (spec Cap.2B3)
  - TargetEvaluator.evaluate(metrics, targets) -> ViolationList

Testes:
- test_scorecard_all_fields_present
- test_scorecard_pass_all_targets_met
- test_scorecard_nogo_critical_target_missed
- test_scorecard_ressalva_desirable_missed
- test_scorecard_includes_evidence_paths
- test_scorecard_includes_limitations
(minimo 10 testes)

Schema:
- schemas/mac_scorecard_v1.json
```

### P2-F004: Batch Endpoints

**Descricao:** APIs de batch.

**Inclui:**

```
Endpoints:
- POST /api/v1/mac/simulations/batch
- GET /api/v1/mac/simulations/batch/{id}
- GET /api/v1/mac/simulations/batch
- POST /api/v1/mac/simulations/batch/{id}/cancel
- GET /api/v1/mac/simulations/batch/{id}/stream (SSE)

Testes:
- Contract tests para todos endpoints
- E2E: start -> progress -> complete -> scorecard
- E2E: start -> cancel -> verify canceled state
(minimo 20 testes)
```

### P2-F005: Gold/Adversarial Datasets

**Descricao:** Datasets canonicos.

**Inclui:**

```
Datasets:
- datasets/mac/gold_standard/health_crises/ (~150 cases)
- datasets/mac/gold_standard/political_scandals/ (~200 cases)
- datasets/mac/gold_standard/historical_claims/ (~100 cases)
- datasets/mac/adversarial/coordinated_attacks/ (~80 cases)
- datasets/mac/adversarial/temporal_attacks/ (~30 cases)
- datasets/mac/adversarial/reversal_attacks/ (~20 cases)
- datasets/mac/edge_cases/threshold_boundary/ (~50 cases)

Quality:
- Cada dataset tem schema validado
- Cada dataset tem hash no manifest
- Data catalog entry
- Lineage documentado

Total: ~1100 cases
```

**Gate G31 Checklist:**
- [ ] P2-F001 completo (DoD)
- [ ] P2-F002 completo (DoD)
- [ ] P2-F003 completo (DoD)
- [ ] P2-F004 completo (DoD)
- [ ] P2-F005 completo (DoD)
- [ ] Batch E2E tests passam
- [ ] accuracy_gold >= 95%
- [ ] attack_detection >= 95%/98%/99%
- [ ] Scorecard G31 gerado

---

## PHASE 3: ADIABATIC PLAN

**Objetivo:** Feature completa de plano adiabatico
**Gate:** G32

### P3-F001: AdiabaticPlan Model

**Descricao:** Modelo de plano com fases e constraints.

**Inclui (DoD completo):**

```
Codigo:
- app/mac/adiabatic.py
  - AdiabaticPlan dataclass (todos campos conforme spec)
  - AdiabaticPhase dataclass
  - RollbackStrategy dataclass

Testes:
- test_plan_all_fields
- test_phase_ordering
- test_rollback_strategy_complete
(minimo 8 testes)
```

### P3-F002: Plan Validator

**Descricao:** Validar limites de derivada e constraints.

**Inclui:**

```
Codigo:
- app/mac/adiabatic_validator.py
  - AdiabaticValidator.validate(plan) -> ValidationResult
  - validate_derivative_limits(phases) (max 0.20/day)
  - validate_domain_constraints(phases, domain_config)
  - validate_rollback_executable(rollback)
  - validate_monotonicity(phases, domain)

Testes:
- test_validate_valid_plan_passes
- test_validate_derivative_exceeded_fails
- test_validate_domain_constraint_violated
- test_validate_rollback_invalid_version
- test_validate_monotonicity_violation
- test_validate_10_valid_plans
- test_validate_10_invalid_plans
(minimo 15 testes)
```

### P3-F003: Plan Simulator

**Descricao:** Simular execucao do plano por fases.

**Inclui:**

```
Codigo:
- app/mac/adiabatic_simulator.py
  - AdiabaticSimulator.simulate_plan(plan, dataset) -> PlanSimulation
  - AdiabaticSimulator.simulate_phase(phase, state) -> PhaseResult
  - AdiabaticSimulator.simulate_rollback(plan, phase_id) -> RollbackPreview

Testes:
- test_simulate_plan_generates_timeline
- test_simulate_phase_calculates_metrics
- test_simulate_rollback_preview
- test_simulate_identifies_high_risk_phases
- test_simulate_sensitivity_by_domain
(minimo 10 testes)
```

### P3-F004: Adiabatic Endpoints

**Descricao:** APIs de plano adiabatico.

**Inclui:**

```
Endpoints:
- POST /api/v1/mac/adiabatic-plans
- GET /api/v1/mac/adiabatic-plans
- GET /api/v1/mac/adiabatic-plans/{id}
- POST /api/v1/mac/adiabatic-plans/{id}/validate
- POST /api/v1/mac/adiabatic-plans/{id}/simulate
- POST /api/v1/mac/adiabatic-plans/{id}/rollback-preview

Testes:
- Contract tests para todos endpoints
- E2E: create -> validate -> simulate -> review
(minimo 15 testes)
```

**Gate G32 Checklist:**
- [ ] P3-F001 completo (DoD)
- [ ] P3-F002 completo (DoD)
- [ ] P3-F003 completo (DoD)
- [ ] P3-F004 completo (DoD)
- [ ] Validation catches all invalid plans
- [ ] Scorecard G32 gerado

---

## PHASE 4: MI/EXPERIENCES EXPOSURE

**Objetivo:** Feature completa de exposicao MI governada
**Gate:** G33

### P4-F001: MI Models

**Descricao:** Modelos para exposicao parcial.

**Inclui (DoD completo):**

```
Codigo:
- app/mi/models.py
  - AntibodySummary dataclass
  - ImmunityPatternSummary dataclass
  - ExperienceSummary dataclass (com anonimizacao)

Testes:
- test_antibody_summary_fields
- test_experience_summary_anonymized
- test_experience_source_derived_marked
(minimo 8 testes)
```

### P4-F002: RBAC Implementation

**Descricao:** 3 roles com niveis de acesso.

**Inclui:**

```
Codigo:
- app/mi/rbac.py
  - RBACService.check_access(user, resource, action) -> AccessResult
  - Roles: ops (ids+types), reviewer (partial), council (full redacted)
  - Decorador @require_role(role)

Testes:
- test_rbac_ops_sees_ids_only
- test_rbac_reviewer_sees_partial
- test_rbac_council_sees_full_redacted
- test_rbac_denies_unauthorized
- test_rbac_logs_access
- test_rbac_edge_token_expired
- test_rbac_edge_role_revoked
(minimo 15 testes)
```

### P4-F003: Redaction Service

**Descricao:** Redacao de PII e dados sensiveis.

**Inclui:**

```
Codigo:
- app/mi/redaction.py
  - RedactionService.redact(data, level) -> RedactedData
  - Redact: PII (names, emails, IPs), claim_text raw, source_urls

Testes:
- test_redact_removes_pii
- test_redact_removes_claim_text
- test_redact_removes_source_urls
- test_redact_preserves_aggregated
- test_redact_by_level
- test_redact_edge_bypass_attempt_fails
(minimo 10 testes)
```

### P4-F004: Audit Logger

**Descricao:** Audit trail completo.

**Inclui:**

```
Codigo:
- app/mi/audit.py
  - AuditLogger.log(event)
  - Event: user_id, role, resource, action, timestamp, ip, request_id
  - Encryption at rest
  - Rotation policy

Testes:
- test_audit_logs_access
- test_audit_logs_denial
- test_audit_includes_all_fields
- test_audit_encrypted
- test_audit_tamper_detection
(minimo 8 testes)
```

### P4-F005: MI Endpoints

**Descricao:** APIs MI com RBAC.

**Inclui:**

```
Endpoints:
- GET /api/v1/mi/patterns
- GET /api/v1/mi/patterns/{id}
- GET /api/v1/mi/antibodies
- GET /api/v1/mi/antibodies/{id}
- GET /api/v1/mi/analytics/health

Testes:
- Contract tests
- RBAC tests para cada endpoint x role
- Redaction verification
(minimo 20 testes)
```

### P4-F006: Experience Derivation

**Descricao:** Derivar experiencias quando store nao existe.

**Inclui:**

```
Codigo:
- app/mi/experience_deriver.py
  - ExperienceDeriver.derive(history) -> ExperienceSummary
  - Mark experience_source: derived

Testes:
- test_derive_from_history
- test_derive_marks_source
- test_derive_anonymizes
(minimo 5 testes)
```

**Gate G33 Checklist:**
- [ ] P4-F001 completo (DoD)
- [ ] P4-F002 completo (DoD)
- [ ] P4-F003 completo (DoD)
- [ ] P4-F004 completo (DoD)
- [ ] P4-F005 completo (DoD)
- [ ] P4-F006 completo (DoD)
- [ ] RBAC 100% tested
- [ ] PII never leaks (15+ tests)
- [ ] Audit trail complete
- [ ] Scorecard G33 gerado

---

## PHASE 5: FRONTEND INTEGRATION

**Objetivo:** UI completa com UX de producao
**Gate:** G34

### P5-F001: SimulationLab Page

**Descricao:** Pagina principal de simulacao.

**Inclui (DoD completo):**

```
Codigo:
- frontend/.../pages/SimulationLabPage.tsx
- Formulario com validacao
- Resultado com todos campos
- Disclaimer sempre visivel

Testes (Vitest):
- test_form_validation
- test_disclaimer_visible
- test_result_all_fields
- test_loading_state
- test_error_state
- test_a11y_keyboard_navigation
- test_a11y_screen_reader
(minimo 10 testes)

E2E (Playwright):
- test_e2e_simulate_happy_path
- test_e2e_simulate_error
- test_e2e_disclaimer_always_visible
```

### P5-F002: BatchPage

**Descricao:** Lista e detalhe de batches.

**Inclui:**

```
Codigo:
- frontend/.../pages/BatchSimulationsPage.tsx
- frontend/.../pages/BatchDetailPage.tsx
- Progress streaming
- Cancel/retry actions
- Scorecard view
- FlipSet with virtualization

Testes:
- test_list_pagination
- test_progress_updates
- test_cancel_action
- test_scorecard_colors
- test_flipset_virtualization
- test_a11y
(minimo 15 testes)
```

### P5-F003: MI States Component

**Descricao:** 4 estados visuais para MI.

**Inclui:**

```
Codigo:
- frontend/.../components/MIExposureState.tsx
- Estados: available (verde), redacted (cinza), not_authorized (laranja), not_available (vermelho)
- Copy PT-BR especifico para cada estado

Testes:
- test_state_available_green
- test_state_redacted_gray
- test_state_not_authorized_orange
- test_state_not_available_red
- test_copy_correct_per_state
(minimo 8 testes)
```

### P5-F004: Accessibility

**Descricao:** A11y em todos componentes.

**Inclui:**

```
Requisitos:
- WCAG 2.1 AA compliance
- Keyboard navigation complete
- Screen reader friendly
- Color contrast adequate
- Focus management

Testes:
- Axe accessibility audit (0 violations)
- Manual screen reader test
- Keyboard-only navigation test
```

**Gate G34 Checklist:**
- [ ] P5-F001 completo (DoD)
- [ ] P5-F002 completo (DoD)
- [ ] P5-F003 completo (DoD)
- [ ] P5-F004 completo (DoD)
- [ ] All Playwright E2E pass
- [ ] A11y audit pass
- [ ] Scorecard G34 gerado

---

## PHASE 6: HARDENING & PRODUCTION

**Objetivo:** Chaos testing, load testing, security audit
**Nao tem gate proprio - prepara G35**

### P6-CHAOS: Chaos Engineering

| Test | Scenario | Expected Behavior |
|------|----------|-------------------|
| CHAOS-001 | DB connection lost mid-batch | Batch fails gracefully, can retry |
| CHAOS-002 | Policy file corrupted | Clear error, fallback if configured |
| CHAOS-003 | Memory pressure | Graceful degradation, no OOM |
| CHAOS-004 | Network partition | Timeout handling, circuit breaker |
| CHAOS-005 | High latency (5s) | Timeout triggers, no hang |

### P6-LOAD: Load Testing

| Test | Config | Target |
|------|--------|--------|
| LOAD-001 | 100 req/s, 1h | p95 < 500ms, 0 errors |
| STRESS-001 | 500 req/s, 10min | < 1% errors, graceful degradation |
| SOAK-001 | 50 req/s, 24h | No memory leak, stable latency |
| SPIKE-001 | 1000 req/s, 1min | Recovery < 30s after spike |

### P6-SECURITY: Security Audit

- [ ] OWASP Top 10 checklist
- [ ] ZAP scan - 0 HIGH/CRITICAL
- [ ] Dependency scan - 0 known vulns
- [ ] Secret scan - 0 exposed secrets
- [ ] Penetration test (se budget)

### P6-RUNBOOK: Runbook Validation

- [ ] Runbook drills executed
- [ ] Each runbook tested with real scenario
- [ ] On-call rotation configured
- [ ] Escalation paths tested

---

## PHASE 7: ORR & BUNDLE

**Objetivo:** Evidencias finais e bundle
**Gate:** G35

### P7-ORR: ORR Checklist

| Category | Check | Status |
|----------|-------|--------|
| **Infra** | Endpoints documented/versioned | |
| **Infra** | Rollback procedure tested | |
| **Obs** | Logs structured + correlation | |
| **Obs** | Metrics per gate | |
| **Obs** | Alerts configured | |
| **Ops** | Runbooks complete | |
| **Ops** | Retention policy defined | |
| **Security** | AuthN/AuthZ working | |
| **Security** | RBAC tested | |
| **Security** | Audit log active | |
| **Security** | Evidence redacted | |
| **Capacity** | Load test passed | |
| **Capacity** | p95/p99 within targets | |

### P7-BUNDLE: Evidence Bundle

```
out/bundles/inspectah_s42_evidence_bundle.zip
├── scorecards/
│   ├── S42_G30_mac_simulate.json
│   ├── S42_G31_mac_batch.json
│   ├── S42_G32_adiabatic_plan.json
│   ├── S42_G33_mi_exposure.json
│   ├── S42_G34_ui.json
│   └── S42_G35_orr.json
├── evidence/
│   ├── S42_G30_mac_simulate/
│   │   ├── manifest.json
│   │   ├── requests.jsonl
│   │   ├── responses.jsonl
│   │   └── summary.md
│   ├── S42_G31_mac_batch/
│   ├── S42_G32_adiabatic_plan/
│   ├── S42_G33_mi_exposure/
│   │   ├── redaction_report.json
│   │   └── rbac_matrix.json
│   └── S42_G34_ui/
│       ├── screenshots/
│       └── routes_covered.json
├── configs/
│   ├── policies/
│   └── params/
├── datasets/
│   └── manifest.json
├── index.json (with hashes)
└── README.md
```

**Gate G35 Checklist:**
- [ ] All gates G30-G34 PASS
- [ ] ORR checklist complete
- [ ] Bundle generated with hashes
- [ ] Bundle integrity verified
- [ ] Ready for S43

---

## RESUMO v5.0 SENIOR

| Phase | Items | Foco |
|-------|-------|------|
| Phase 0 | 8 ADRs, 3 Spikes, Contracts, Threat Model | Design first |
| Phase 1 | 5 Features completas | MAC Simulate |
| Phase 2 | 5 Features completas | MAC Batch |
| Phase 3 | 4 Features completas | Adiabatic Plan |
| Phase 4 | 6 Features completas | MI Exposure |
| Phase 5 | 4 Features completas | Frontend |
| Phase 6 | Chaos, Load, Security, Runbooks | Hardening |
| Phase 7 | ORR, Bundle | Evidencias |

**Diferencas chave vs v4.0:**
- Phase 0 obrigatoria (design before code)
- Features, nao layers
- DoD completo em cada item
- Observabilidade built-in
- Security built-in
- Testes junto com codigo
- Chaos engineering
- Capacity planning real

---

## ASSINATURA v5.0

```
Sprint: S42
Versao: 5.0 SENIOR ENTERPRISE
Phases: 8 (0-7)
Gates: G30-G35
ADRs: 6
Spikes: 3
OpenAPI: Contract-first
Threat Model: Completo
Chaos Tests: 5
Load Tests: 4
DoD: 6 niveis obrigatorios
Metodologia: Feature-based, Design-first, Test-driven
Status: SENIOR ENTERPRISE READY
```

*Plano gerado por Tech Lead Senior*
*15 problemas estruturais corrigidos*
*Metodologia de engenharia enterprise*
