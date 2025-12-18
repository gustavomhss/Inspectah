# Sprint 42 — Cap.4 Bloco 4 — Tasks e Waves (v3.0 MATURE)

> **Programa:** P2 + P3 + P4 (+ P5/P6)
> **Missao:** Simulacoes MAC + Plano Adiabatico + Exposicao MI (parcial)
> **Gates:** G30–G35
> **Predecessora:** S41 (Governanca v1)
> **Sucessora:** S43 (GO/NO-GO Fase 2)
> **Versao:** 3.0 (18 rodadas de refinamento aplicadas)

---

## Changelog de Refinamento v3.0

| Rodada | Foco | Melhorias Aplicadas |
|--------|------|---------------------|
| R1-R10 | Inicial | 111 tasks base |
| R11 | Datasets | Estrutura canonica (~1100 casos) por dominio |
| R12 | Manifest/Lineage | Task especifica para lineage completo |
| R13 | Endpoints | +decisions, +evaluate, +stream |
| R14 | Estados de Run | cancel, streaming, retry |
| R15 | Testes | batch determinism, payloads grandes, mocks honestos |
| R16 | Observabilidade | Correlacao, metricas por gate, tracing |
| R17 | Runbooks/ORR | Runbooks operacionais completos |
| R18 | Polish | Campos de scorecard, copy detalhado, virtualization |

---

## Visao Geral das Waves

| Wave | Nome | Objetivo | Gates | Tasks | Dependencias |
|------|------|----------|-------|-------|--------------|
| W0 | Fundacao MAC | Schemas, contratos, migrations, configs, datasets canonicos | Pre-req | 24 | - |
| W1 | MAC Simulate | Endpoint dry-run deterministico com manifest completo | G30 | 22 | W0 |
| W2 | MAC Batch | Simulacao em lote + scorecards + streaming + cancel | G31 | 18 | W0, W1 |
| W3 | Plano Adiabatico | Validador + simulador por fases + rollback | G32 | 16 | W0, W1 |
| W4 | MI/Exp Exposure | Exposicao parcial + RBAC + redaction + derivation | G33 | 20 | W0, W1 |
| W5 | Frontend P4 | UI simulacoes + virtualization + disclaimers + states | G34 | 32 | W1, W2, W3, W4 |
| W6 | ORR/Bundle | Scripts + runbooks + teste carga + bundle + redaction | G35 | 26 | W0-W5 |

**Total: 158 tasks**

---

## W0 — Fundacao MAC (24 tasks)

**Objetivo:** Criar estrutura base completa conforme spec canonica.

**Spec refs:** Cap.3/Bloco2, Cap.3/Bloco3, Cap.6/Bloco2

### Tasks W0 — Backend Core

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-BE-001 | Criar modulo `app/mac/` com `__init__.py`, `models.py`, `service.py`, `exceptions.py`, `manifest.py` | `app/mac/__init__.py`, `app/mac/models.py`, `app/mac/service.py`, `app/mac/exceptions.py`, `app/mac/manifest.py` | `from app.mac import models, manifest` funciona; 0 erros |
| S42-BE-002 | Implementar `MacDecision` dataclass com TODOS campos (decision_id, allegation_id, source_state, target_state, action, confidence, mode, costs{type_i,type_ii,change,context,total}, hard_cap_triggered{reason}, hysteresis_applied{factor}, temperature_applied, policy_ref{name,version,hash}, params_ref{mode,version,hash}, mi_refs[], experience_refs[], timestamp, replay_token) | `app/mac/models.py` | Todos os 20+ campos presentes; to_dict() preserva todos |
| S42-BE-003 | Implementar `MacSimulation` dataclass com campos canonicos (simulation_id, basis{allegation_id,candidate_transition}, simulation_options{override_mode,override_signals,temperature,override_params}, recommended_action, action_probabilities, cost_breakdown{}, signals_used[], notes[], mi_refs[], experience_refs[], exposure_state, created_at, commit_ref, dataset_ref, replay_token, manifest_ref) | `app/mac/models.py` | Todos os 16+ campos presentes |
| S42-BE-004 | Implementar `MacBatchRun` dataclass com campos (batch_run_id, dataset_id, scenario_matrix_id, inputs{policy,params,mode,plan versions}, status{queued,running,succeeded,failed,canceled}, progress_percent, estimated_remaining_seconds, outputs{metrics,divergencias,paths}, created_at, started_at, completed_at, canceled_at, cancel_reason) | `app/mac/models.py` | Estados de lifecycle completos |
| S42-BE-005 | Implementar `RunManifest` dataclass com lineage completo (simulation_run_id, mode, policy_id, policy_version, policy_bundle_id, mac_version{commit,tag}, mi_version, dataset_id, dataset_version, params_efetivos, override_reason, seed, rng_state, temperature, timestamps{created,started,completed}, git_commit, server_id) | `app/mac/manifest.py` | Manifest gera hash deterministic |
| S42-BE-006 | Implementar error codes estaveis: `MacError(code,message_human,details)`, `PolicyNotFoundError`, `PolicyVersionMismatchError`, `SignalSnapshotInvalidError`, `SignalSnapshotExpiredError`, `SimulationTimeoutError`, `BatchCanceledError`, `ReplayMismatchError`, `DeterminismViolationError`, `RBACForbiddenError`, `DatasetNotFoundError`, `DatasetInvalidError`, `ManifestIncompleteError` | `app/mac/exceptions.py` | 13 classes de erro com codes estaveis |

### Tasks W0 — Plano Adiabatico

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-BE-007 | Implementar `AdiabaticPlan` dataclass com campos canonicos (plan_id, plan_version, baseline_policy_version, target_policy_version, scope{global,domain}, phases[], constraints{derivative_limits{max_per_day:0.20},hard_caps_by_domain}, rationale, provenance{commit,datasets[],author,timestamp,justification}) | `app/mac/adiabatic.py` | Todos campos conforme Cap.6B3 |
| S42-BE-008 | Implementar `AdiabaticPhase` dataclass (phase_id, order, delta{params_changes[]}, duration_days, constraints{derivative_cap,domain_overrides}, success_criteria{metrics_targets[]}, rollback_strategy{target_version,trigger_conditions[],auto_trigger:bool}) | `app/mac/adiabatic.py` | Rollback como primeira classe |

### Tasks W0 — Migrations

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-DB-001 | Criar migration `034_s42_mac_simulations.sql`: tabelas mac_simulations(id,allegation_id,mode,policy_ref_json,params_ref_json,costs_json,signals_json,result_json,manifest_json,replay_token,created_at), indices em (id), (created_at), (allegation_id) | `db/migrations/034_s42_mac_simulations.sql` | Migration up/down; indices criados |
| S42-DB-002 | Criar migration `035_s42_mac_batch_runs.sql`: tabela mac_batch_runs(id,dataset_id,scenario_matrix_json,status,progress_percent,inputs_json,outputs_json,manifest_json,created_at,started_at,completed_at,canceled_at,cancel_reason), indices em (id), (status), (created_at) | `db/migrations/035_s42_mac_batch_runs.sql` | Migration up/down |
| S42-DB-003 | Criar migration `036_s42_adiabatic_plans.sql`: tabela adiabatic_plans(id,version,baseline_policy_version,target_policy_version,scope,phases_json,constraints_json,rationale,provenance_json,status,created_at,updated_at), indices | `db/migrations/036_s42_adiabatic_plans.sql` | Migration up/down |
| S42-DB-004 | Criar migration `037_s42_run_manifests.sql`: tabela run_manifests(id,simulation_run_id,manifest_json,manifest_hash,created_at), indice unique em manifest_hash | `db/migrations/037_s42_run_manifests.sql` | Manifest persistido para replay |

### Tasks W0 — Configs

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-CFG-001 | Criar `configs/mac/policies/default.yaml` com campos: name, version, thresholds{promote,demote,suspend,revoke}, costs_weights{type_i,type_ii,change,context}, hard_caps[{domain,action,reason}], hysteresis{factor,window_hours} | `configs/mac/policies/default.yaml` | yamllint pass; schema valido |
| S42-CFG-002 | Criar `configs/mac/policies/candidate.yaml` (policy alternativa para comparacao) | `configs/mac/policies/candidate.yaml` | Diff significativo vs default |
| S42-CFG-003 | Criar `configs/mac/params/default.yaml` com: mode_defaults{NORMAL,ENDURECIDO,EMERGENCIA}, derivative_limits{max_per_day:0.20,max_per_phase:0.50}, hysteresis_factor, temperature_range{min,max,default}, seed_strategy | `configs/mac/params/default.yaml` | Derivative default 0.20 |
| S42-CFG-004 | Criar `configs/mac/domains/politics.yaml` com constraints especificos, hard_caps, derivative_overrides{max_per_day:0.10} | `configs/mac/domains/politics.yaml` | Override mais restritivo |
| S42-CFG-005 | Criar `configs/mac/domains/health.yaml` com constraints especificos | `configs/mac/domains/health.yaml` | yamllint pass |

### Tasks W0 — Datasets Canonicos

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-DAT-001 | Criar `datasets/mac/gold_standard/health_crises/` com ~150 casos (case_id, allegation_id, signals{mqv,tds,cvi,ethical}, expected_action, expected_confidence_range, justification, domain:health, tags[]) | `datasets/mac/gold_standard/health_crises/*.json` | jq length >= 150 |
| S42-DAT-002 | Criar `datasets/mac/gold_standard/political_scandals/` com ~200 casos | `datasets/mac/gold_standard/political_scandals/*.json` | jq length >= 200 |
| S42-DAT-003 | Criar `datasets/mac/gold_standard/historical_claims/` com ~100 casos | `datasets/mac/gold_standard/historical_claims/*.json` | jq length >= 100 |
| S42-DAT-004 | Criar `datasets/mac/adversarial/coordinated_attacks/` com ~80 casos (attack_type:coordinated, expected_detection:true, detection_target:>=95%) | `datasets/mac/adversarial/coordinated_attacks/*.json` | jq length >= 80 |
| S42-DAT-005 | Criar `datasets/mac/adversarial/temporal_attacks/` com ~30 casos (detection_target:>=98%) | `datasets/mac/adversarial/temporal_attacks/*.json` | jq length >= 30 |
| S42-DAT-006 | Criar `datasets/mac/adversarial/reversal_attacks/` com ~20 casos (detection_target:>=99%) | `datasets/mac/adversarial/reversal_attacks/*.json` | jq length >= 20 |
| S42-DAT-007 | Criar `datasets/mac/edge_cases/threshold_boundary/` com ~50 casos (valores exatamente no limiar) | `datasets/mac/edge_cases/threshold_boundary/*.json` | jq length >= 50 |
| S42-DAT-008 | Criar `datasets/mac/dataset_manifest.json` com: version, created_at, datasets[]{id,path,case_count,domain,type,detection_target,origin,license,hash} | `datasets/mac/dataset_manifest.json` | Manifest versionado |

### Tasks W0 — Schemas

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-SCH-001 | Criar JSON Schema `schemas/mac_simulation_v1.json` validando MacSimulation com todos campos required | `schemas/mac_simulation_v1.json` | jsonschema validation pass |
| S42-SCH-002 | Criar JSON Schema `schemas/mac_scorecard_v1.json` com campos: sprint, gate, status{PASS,NO_GO,GO_COM_RESSALVA}, commit, timestamp_utc, inputs{}, metrics{}, targets{}, violations[], evidence_paths[], limitations[] | `schemas/mac_scorecard_v1.json` | Schema completo conforme Cap.2B3 |
| S42-SCH-003 | Criar JSON Schema `schemas/run_manifest_v1.json` validando RunManifest | `schemas/run_manifest_v1.json` | Todos campos lineage |

**Total W0:** 24 tasks

---

## W1 — MAC Simulate (22 tasks)

**Objetivo:** Implementar endpoint dry-run com determinismo 100% e manifest completo.

**Spec refs:** Cap.3/Bloco1, Cap.2/Bloco2 (G30), Cap.6/Bloco2

### Tasks W1 — Engine Core

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-BE-010 | Implementar `MacEngine.__init__()` com carregamento de policy, params, mode configs | `app/mac/engine.py` | Engine inicializa sem erros |
| S42-BE-011 | Implementar `MacEngine.evaluate()` com calculo de costs (type_i, type_ii, change, context, total) usando weights da policy | `app/mac/engine.py` | Costs calculados corretamente |
| S42-BE-012 | Implementar `MacEngine.apply_hard_caps()` retornando {blocked:bool, reason:str, cap_id:str, domain:str} | `app/mac/engine.py` | Hard caps bloqueiam acoes proibidas |
| S42-BE-013 | Implementar `MacEngine.apply_hysteresis()` com fator configuravel e window temporal | `app/mac/engine.py` | Hysteresis ajusta thresholds |
| S42-BE-014 | Implementar `MacEngine.calculate_action_probabilities()` para temperature > 0 | `app/mac/engine.py` | Distribuicao soma 1.0 |

### Tasks W1 — Simulation Core

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-BE-015 | Implementar `simulate()` dry-run que NUNCA muta TruthState; assertion explícita | `app/mac/simulation.py` | Teste com mock TruthState; antes == depois |
| S42-BE-016 | Implementar determinismo com seed quando T=0: `random.seed(seed)`, ordenacao deterministica de todas operacoes | `app/mac/simulation.py` | 100 execucoes identicas byte-a-byte |
| S42-BE-017 | Implementar `simulate()` gerando RunManifest completo automaticamente | `app/mac/simulation.py` | Manifest com todos campos preenchidos |
| S42-BE-018 | Implementar override de modo (NORMAL/ENDURECIDO/EMERGENCIA) com registro em notes[] | `app/mac/simulation.py` | notes[] contem mode_override |
| S42-BE-019 | Implementar override de sinais com provenance registrada | `app/mac/simulation.py` | provenance contem signal_override |
| S42-BE-020 | Implementar `replay_token` generation (hash deterministico de inputs) | `app/mac/simulation.py` | replay_token reproduzivel |

### Tasks W1 — Signals Snapshot

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-BE-021 | Implementar `SignalsSnapshot.capture()` capturando mqv, tds, cvi, ethical, mi com timestamp | `app/mac/signals_snapshot.py` | Snapshot timestampado |
| S42-BE-022 | Implementar `SignalsSnapshot.replay()` retornando exatamente mesmos sinais | `app/mac/signals_snapshot.py` | Round-trip identico |
| S42-BE-023 | Implementar `SignalsSnapshot.validate()` verificando freshness e integridade | `app/mac/signals_snapshot.py` | Rejeita snapshots expirados |

### Tasks W1 — APIs

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-API-001 | Criar rota `POST /api/v1/mac/simulate` com request{allegation_id,candidate_transition,options{mode,signals,temperature,params}} e response completa | `app/api/mac_routes.py` | Response com todos campos MacSimulation |
| S42-API-002 | Criar rota `GET /api/v1/mac/simulations/{id}` incluindo manifest e exposure_state | `app/api/mac_routes.py` | Manifest presente |
| S42-API-003 | Criar rota `GET /api/v1/mac/simulations` com paginacao, filtros (domain,policy_version,created_after,created_before,status) | `app/api/mac_routes.py` | Filtros funcionais |
| S42-API-004 | Criar rota `GET /api/v1/mac/parameters` retornando params vigentes com version e hash | `app/api/mac_routes.py` | Version e hash presentes |
| S42-API-005 | Criar rota `GET /api/v1/mac/mode` retornando {mode, since, reason, can_override} | `app/api/mac_routes.py` | Modo atual |
| S42-API-006 | Criar rota `GET /api/v1/mac/decisions/{id}` para buscar decisao real (producao) | `app/api/mac_routes.py` | Decisao com lineage |
| S42-API-007 | Criar rota `GET /api/v1/mac/decisions` listagem paginada com filtros | `app/api/mac_routes.py` | Filtros por domain, mode, action |

### Tasks W1 — Testes

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-TST-001 | Criar testes de performance: p50<200ms, p95<500ms, p99<2s com T=0 | `tests/mac/test_simulate_perf.py` | pytest-benchmark pass |
| S42-TST-002 | Criar testes de replay deterministico: 100 replays, diff outputs = 0 | `tests/mac/test_replay_determinism.py` | 100/100 identicos |

**Total W1:** 22 tasks

---

## W2 — MAC Batch (18 tasks)

**Objetivo:** Simulacao em lote com streaming, cancel, retry e scorecards.

**Spec refs:** Cap.6/Bloco2, Cap.2/Bloco2 (G31), Cap.8/Bloco2

### Tasks W2 — Batch Runner

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-BE-030 | Implementar `BatchRunner.run()` executando N simulacoes com paralelismo configuravel | `app/mac/batch_runner.py` | Paralelismo funcional |
| S42-BE-031 | Implementar estados de lifecycle: queued -> running -> succeeded/failed/canceled | `app/mac/batch_runner.py` | Transicoes corretas |
| S42-BE-032 | Implementar `BatchRunner.cancel()` com graceful shutdown e registro de cancel_reason | `app/mac/batch_runner.py` | Cancel para execucao |
| S42-BE-033 | Implementar `BatchRunner.get_progress()` retornando {percent,current_phase,estimated_remaining_seconds,partial_metrics} | `app/mac/batch_runner.py` | Progress tracking |
| S42-BE-034 | Implementar streaming de logs resumidos (sem dados sensiveis) via SSE ou WebSocket | `app/mac/batch_runner.py` | Stream funcional |

### Tasks W2 — Dataset e Comparacao

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-BE-035 | Implementar `DatasetLoader` com validacao contra schema, verificacao de hash, suporte a slices | `app/mac/datasets.py` | Rejeita datasets invalidos |
| S42-BE-036 | Implementar `ScenarioComparator` identificando flip_set[], top_regressions[10], top_improvements[10], delta_metrics{} | `app/mac/comparator.py` | Delta views completos |
| S42-BE-037 | Implementar `ScorecardGenerator` com TODOS campos obrigatorios (Cap.2B3): sprint, gate, status, commit, timestamp_utc, inputs{}, metrics{}, targets{}, violations[], evidence_paths[], limitations[] | `app/mac/scorecard.py` | Scorecard completo |
| S42-BE-038 | Implementar verificacao de targets MAC Anexo D: accuracy_gold>=95%, attack_detection>=95% (global), >=98% (temporal), >=99% (reversal), replay=100% | `app/mac/scorecard.py` | Targets verificados |

### Tasks W2 — Persistencia

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-BE-039 | Implementar `MacBatchRepository.create()` persistindo batch run com manifest | `app/mac/repository.py` | Batch persistido |
| S42-BE-040 | Implementar `MacBatchRepository.update_status()` para transicoes de estado | `app/mac/repository.py` | Status atualizado |
| S42-BE-041 | Implementar `MacBatchRepository.get_results()` retornando scorecard e evidencias | `app/mac/repository.py` | Resultados completos |

### Tasks W2 — APIs

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-API-010 | Criar rota `POST /api/v1/mac/simulations/batch` iniciando batch async | `app/api/mac_routes.py` | Retorna batch_run_id |
| S42-API-011 | Criar rota `GET /api/v1/mac/simulations/batch/{id}` com status, progress, scorecard, flip_set | `app/api/mac_routes.py` | Todos campos |
| S42-API-012 | Criar rota `GET /api/v1/mac/simulations/batch` listagem paginada | `app/api/mac_routes.py` | Paginacao |
| S42-API-013 | Criar rota `POST /api/v1/mac/simulations/batch/{id}/cancel` para cancelamento | `app/api/mac_routes.py` | Cancel funcional |
| S42-API-014 | Criar rota `GET /api/v1/mac/simulations/batch/{id}/stream` para SSE de progress | `app/api/mac_routes.py` | SSE streaming |

### Tasks W2 — Testes

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-TST-010 | Criar testes de batch com gold dataset (accuracy>=95%) | `tests/mac/test_batch_gold.py` | Scorecard gerado |
| S42-TST-011 | Criar testes de batch determinismo (mesmo batch, mesmo resultado) | `tests/mac/test_batch_determinism.py` | Batch deterministic |

**Total W2:** 18 tasks

---

## W3 — Plano Adiabatico (16 tasks)

**Objetivo:** Validador + simulador por fases com derivative caps e rollback.

**Spec refs:** Cap.6/Bloco3, Cap.2/Bloco2 (G32)

### Tasks W3 — Validador

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-BE-050 | Implementar `AdiabaticValidator.validate()` verificando: derivative<=max_per_day (default 0.20), phases em ordem, durations>0, rollback definido | `app/mac/adiabatic.py` | Rejeita planos invalidos |
| S42-BE-051 | Implementar validacao de constraints por dominio carregando de configs/mac/domains/{domain}.yaml | `app/mac/adiabatic.py` | Domain overrides aplicados |
| S42-BE-052 | Implementar validacao de rollback executavel (versao referenciada existe, delta inverso valido) | `app/mac/adiabatic.py` | Rollback validado |
| S42-BE-053 | Implementar validacao de monotonicidade quando aplicavel (nao reduzir exigencias em dominios sensiveis sem fase intermediaria) | `app/mac/adiabatic.py` | Monotonicidade verificada |

### Tasks W3 — Simulador

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-BE-054 | Implementar `AdiabaticSimulator.simulate_phase()` retornando {promotions,demotions,reversions,metrics_delta,flip_set[]} | `app/mac/adiabatic.py` | Metricas por fase |
| S42-BE-055 | Implementar `AdiabaticSimulator.simulate_plan()` gerando timeline[{phase_id,metrics,cumulative_impact,flip_set}], stability_score, high_risk_phases[] | `app/mac/adiabatic.py` | Timeline completa |
| S42-BE-056 | Implementar calculo de reversion_risk por fase e sensitivity_by_domain | `app/mac/adiabatic.py` | Riscos calculados |
| S42-BE-057 | Implementar `AdiabaticSimulator.simulate_rollback()` para preview de rollback | `app/mac/adiabatic.py` | Rollback simulavel |

### Tasks W3 — Persistencia

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-BE-058 | Implementar `AdiabaticPlanRepository` com CRUD e versionamento | `app/mac/adiabatic_repository.py` | CRUD funcional |

### Tasks W3 — APIs

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-API-020 | Criar rota `POST /api/v1/mac/adiabatic-plans` criando plano | `app/api/mac_routes.py` | Plano criado |
| S42-API-021 | Criar rota `GET /api/v1/mac/adiabatic-plans` listagem com filtros | `app/api/mac_routes.py` | Listagem |
| S42-API-022 | Criar rota `GET /api/v1/mac/adiabatic-plans/{id}` com plano completo | `app/api/mac_routes.py` | Plano detalhado |
| S42-API-023 | Criar rota `POST /api/v1/mac/adiabatic-plans/{id}/simulate` simulando plano | `app/api/mac_routes.py` | Timeline retornada |
| S42-API-024 | Criar rota `POST /api/v1/mac/adiabatic-plans/{id}/validate` validando plano | `app/api/mac_routes.py` | Validation result |
| S42-API-025 | Criar rota `POST /api/v1/mac/adiabatic-plans/{id}/rollback-preview` preview de rollback | `app/api/mac_routes.py` | Rollback preview |

### Tasks W3 — Testes

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-TST-030 | Criar testes de validacao: 10+ planos validos, 10+ invalidos | `tests/mac/test_adiabatic_validation.py` | Cobertura validacao |

**Total W3:** 16 tasks

---

## W4 — MI/Exp Exposure (20 tasks)

**Objetivo:** Exposicao parcial governada com RBAC, redaction e derivation.

**Spec refs:** Cap.6/Bloco4, Cap.2/Bloco2 (G33), Cap.3/Bloco2

### Tasks W4 — Modulo MI

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-BE-060 | Criar modulo `app/mi/` com estrutura base | `app/mi/__init__.py`, `app/mi/models.py`, `app/mi/service.py`, `app/mi/exceptions.py` | Modulo importavel |
| S42-BE-061 | Implementar `AntibodySummary` com campos: id, type, short_reason, effect, impact_tags[], provenance, status, redaction_level | `app/mi/models.py` | Sumario com redaction |
| S42-BE-062 | Implementar `ImmunityPatternSummary` com campos similares | `app/mi/models.py` | Pattern summary |
| S42-BE-063 | Implementar `ExperienceSummary` com anonimizacao: claim_id_hash (NAO raw), outcome, time_window, aggregated_signals, mode_changes[], lessons_summary, experience_source{derived,store} | `app/mi/models.py` | Anonimizacao aplicada |

### Tasks W4 — RBAC e Redaction

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-BE-064 | Implementar RBAC com 3 niveis: ops (ids+tipos), reviewer (detalhes parciais), council (completo, ainda redatado PII) | `app/mi/rbac.py` | 3 roles configuradas |
| S42-BE-065 | Implementar `RedactionService.redact()` removendo: PII (nomes, emails, IPs), claim_text raw, source_urls sensiveis | `app/mi/redaction.py` | PII removido |
| S42-BE-066 | Implementar estados de resposta: `redacted`, `not_authorized`, `not_available`, `available` | `app/mi/service.py` | 4 estados distintos |
| S42-BE-067 | Implementar `AuditLogger` registrando: user_id, role, resource_type, resource_id, action, timestamp, ip_address, request_id | `app/mi/audit.py` | Audit trail completo |

### Tasks W4 — Experience Derivation

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-BE-068 | Implementar `ExperienceDeriver` derivando experiencias de historico quando ExperienceStore nao existe, marcando experience_source:derived | `app/mi/experience_deriver.py` | Derivation funcional |
| S42-BE-069 | Integrar com `ExperienceRepository` existente (app.truth.experiences) | `app/mi/service.py` | Integracao funcionando |

### Tasks W4 — Integracao MAC

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-BE-070 | Integrar MI/Experiencias na resposta de simulacao: mi_refs[], experience_refs[], exposure_state, mi_used:bool | `app/mac/simulation.py` | Refs presentes |
| S42-BE-071 | Implementar logica de quando MI nao foi consultada: mi_used:false + reason | `app/mac/simulation.py` | Reason explicito |

### Tasks W4 — APIs

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-API-030 | Criar rota `GET /api/v1/mi/patterns` com RBAC, response varia por role | `app/api/mi_routes.py` | RBAC aplicado |
| S42-API-031 | Criar rota `GET /api/v1/mi/patterns/{id}` com RBAC | `app/api/mi_routes.py` | RBAC aplicado |
| S42-API-032 | Criar rota `GET /api/v1/mi/antibodies` com RBAC | `app/api/mi_routes.py` | RBAC aplicado |
| S42-API-033 | Criar rota `GET /api/v1/mi/antibodies/{id}` com RBAC | `app/api/mi_routes.py` | RBAC aplicado |
| S42-API-034 | Criar rota `GET /api/v1/mi/analytics/health` retornando {active,patterns_count,antibodies_count,last_update,coverage_domains[]} | `app/api/mi_routes.py` | Health endpoint |

### Tasks W4 — Testes

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-TST-040 | Criar testes RBAC exaustivos: 15+ testes (3 roles x 5 recursos) | `tests/mi/test_rbac.py` | Cobertura RBAC |
| S42-TST-041 | Criar testes de redaction: 15+ testes garantindo PII nunca vaza | `tests/mi/test_redaction.py` | PII protegido |
| S42-TST-042 | Criar testes de audit: todo acesso logado, log parseavel | `tests/mi/test_audit.py` | Audit funcional |

**Total W4:** 20 tasks

---

## W5 — Frontend P4 (32 tasks)

**Objetivo:** UI completa com virtualization, disclaimers, estados MI, diffs.

**Spec refs:** Cap.8/Blocos1-4, Cap.9/Blocos1-4

### Tasks W5 — Estrutura

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-FE-001 | Criar modulo `modules/mac/` com index.ts, routes.tsx, types.ts | `frontend/.../mac/` | Build passa |
| S42-FE-002 | Criar hooks `useMacSimulation` com loading, error, data, refetch, cancel | `frontend/.../mac/hooks/` | Hooks funcionais |
| S42-FE-003 | Criar hooks `useMacBatch` com streaming de progress | `frontend/.../mac/hooks/` | Streaming funcional |
| S42-FE-004 | Criar tipos TypeScript para todos contratos MAC/MI | `frontend/.../mac/types.ts` | Tipos completos |

### Tasks W5 — Paginas

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-FE-005 | Criar `SimulationLabPage` com selecao de dominio, alegacao, modo, overrides, temperature | `frontend/.../pages/SimulationLabPage.tsx` | Formulario funcional |
| S42-FE-006 | Criar `BatchSimulationsPage` com lista paginada, status badges, progress | `frontend/.../pages/BatchSimulationsPage.tsx` | Lista funcional |
| S42-FE-007 | Criar `BatchDetailPage` com scorecard, flip_set, timeline | `frontend/.../pages/BatchDetailPage.tsx` | Detalhe completo |
| S42-FE-008 | Criar `AdiabaticPlanPage` com timeline visual, phases, constraints | `frontend/.../pages/AdiabaticPlanPage.tsx` | Plano visual |

### Tasks W5 — Componentes Core

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-FE-009 | Criar `SimulationForm` com validacao, aviso de override, disable durante loading | `frontend/.../components/SimulationForm.tsx` | Form validado |
| S42-FE-010 | Criar `SimulationResult` exibindo recommended_action (badge), costs, signals, notes[], mi_refs[], experience_refs[] | `frontend/.../components/SimulationResult.tsx` | Resultado completo |
| S42-FE-011 | Criar `ScorecardView` com accuracy_gold, attack_detection (por tipo), replay_concordance, cores conforme target | `frontend/.../components/ScorecardView.tsx` | Cores por target |
| S42-FE-012 | Criar `FlipSetTable` com virtualizacao (windowing), paginacao, filtros, busca com debounce, ordenacao deterministica | `frontend/.../components/FlipSetTable.tsx` | Virtualizacao ativa |
| S42-FE-013 | Criar `TimelineChart` (recharts) com eixo X=fases, Y=metricas, tooltips, highlight high_risk | `frontend/.../components/TimelineChart.tsx` | Chart funcional |
| S42-FE-014 | Criar `PhaseStepper` visual com highlight em high_risk, click abre detalhe | `frontend/.../components/PhaseStepper.tsx` | Stepper funcional |

### Tasks W5 — Disclaimers e Estados

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-FE-015 | Criar `SimulationDisclaimer` banner amarelo: "SIMULACAO — nao altera producao. Resultados sao hipoteticos." sempre visivel | `frontend/.../components/SimulationDisclaimer.tsx` | Banner visivel |
| S42-FE-016 | Criar `MIExposureState` com 4 estados visuais distintos: available (verde), redacted (cinza), not_authorized (laranja), not_available (vermelho) | `frontend/.../components/MIExposureState.tsx` | 4 estados visuais |
| S42-FE-017 | Criar `LimitationsWarning` exibindo limitations[] do scorecard | `frontend/.../components/LimitationsWarning.tsx` | Limitacoes visiveis |

### Tasks W5 — Provenance e Diff

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-FE-018 | Criar `ProvenanceFooter` com policy_version, params_version, simulation_id, timestamp, commit, copy to clipboard | `frontend/.../shared/components/ProvenanceFooter.tsx` | Provenance visivel |
| S42-FE-019 | Criar `DiffView` side-by-side: baseline vs candidate, highlight diferencas, collapse sections | `frontend/.../components/DiffView.tsx` | Diff funcional |
| S42-FE-020 | Criar `ManifestViewer` exibindo lineage completo do run | `frontend/.../components/ManifestViewer.tsx` | Manifest visivel |

### Tasks W5 — Integracao

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-FE-021 | Integrar simulacao em `FactCard` com botao "Simular" abrindo drawer | `frontend/.../guardian/components/FactCard.tsx` | What-if funcional |
| S42-FE-022 | Implementar cancelamento e retry de batch na UI | `frontend/.../pages/BatchDetailPage.tsx` | Cancel/retry funcionais |

### Tasks W5 — Estados e Resiliencia

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-FE-023 | Criar `LoadingState` com skeleton e cancelamento quando aplicavel | `frontend/.../components/LoadingState.tsx` | Skeleton funcional |
| S42-FE-024 | Criar `ErrorState` com causa, run_id para debug, retry button | `frontend/.../components/ErrorState.tsx` | Retry funcional |
| S42-FE-025 | Criar `PartialState` para batch em andamento com scorecard parcial | `frontend/.../components/PartialState.tsx` | Partial visivel |

### Tasks W5 — UX e A11y

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-FE-026 | Implementar A11y: aria-labels, role=alert em disclaimers, focus management, contraste WCAG AA | `varios componentes` | npm run lint:a11y pass |
| S42-UX-001 | Criar `constants/copy.ts` com copy PT-BR para todos estados e disclaimers | `frontend/.../mac/constants/copy.ts` | Copy completo |
| S42-UX-002 | Criar `constants/colors.ts` com paleta: success=#22c55e, warning=#eab308, error=#ef4444, redacted=#6b7280 | `frontend/.../mac/constants/colors.ts` | Cores definidas |

### Tasks W5 — Testes

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-TST-050 | Criar testes de componente (Vitest): cobertura >= 80%, 60+ testes | `frontend/.../src/__tests__/mac/` | Cobertura >=80% |
| S42-TST-051 | Criar testes de estados MI (4 estados) em FE | `frontend/.../src/__tests__/mac/test_mi_states.tsx` | 4 estados testados |
| S42-TST-052 | Criar testes de diff view com payloads reais | `frontend/.../src/__tests__/mac/test_diff_view.tsx` | Diff testado |
| S42-TST-053 | Criar testes de degradacao com payloads grandes (smoke/perf) | `frontend/.../src/__tests__/mac/test_large_payloads.tsx` | Perf smoke pass |
| S42-TST-054 | Criar testes E2E (Playwright): fluxo completo SimulationLab, disclaimer visivel | `frontend/.../playwright/mac.spec.ts` | E2E pass |

**Total W5:** 32 tasks

---

## W6 — ORR/Bundle (26 tasks)

**Objetivo:** Scripts de gate, runbooks, teste de carga, bundle com redaction.

**Spec refs:** Cap.2/Bloco2 (G35), Cap.4/Bloco4, Cap.7/Bloco1

### Tasks W6 — Scripts de Gate

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-CI-001 | Criar `bin/s42_g30_mac_simulate.sh`: testes unitarios, integracao, performance, replay; gera scorecard | `bin/s42_g30_mac_simulate.sh` | Exit 0 |
| S42-CI-002 | Criar `bin/s42_g31_mac_batch.sh`: batch com gold/adversarial/edge; valida targets; gera scorecard | `bin/s42_g31_mac_batch.sh` | Exit 0 |
| S42-CI-003 | Criar `bin/s42_g32_adiabatic_plan.sh`: cria plano teste, valida, simula, gera evidencias | `bin/s42_g32_adiabatic_plan.sh` | Exit 0 |
| S42-CI-004 | Criar `bin/s42_g33_mi_exposure.sh`: testa RBAC (3 roles), redaction (15 casos), audit | `bin/s42_g33_mi_exposure.sh` | Exit 0 |
| S42-CI-005 | Criar `bin/s42_g34_ui_smoke.sh`: Playwright smoke, disclaimers, screenshots | `bin/s42_g34_ui_smoke.sh` | Exit 0 |
| S42-CI-006 | Criar `bin/s42_g35_orr.sh`: executa G30-G34, consolida, valida ORR checklist, gera bundle | `bin/s42_g35_orr.sh` | Exit 0 |

### Tasks W6 — Teste de Carga

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-PERF-001 | Criar teste de carga para simulate (T=0): 100 req/s, p95<500ms, p99<2s | `tests/load/test_simulate_load.py` | Targets atingidos |
| S42-PERF-002 | Criar teste de degradacao graciosa: 500 req/s, sem timeouts silenciosos | `tests/load/test_graceful_degradation.py` | Degradacao controlada |

### Tasks W6 — Observabilidade

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-OBS-001 | Criar alertas `s42_mac.yaml`: mac_simulate_latency_high, mac_batch_failure, mac_rbac_violation, mac_determinism_failure | `observability/alerts/s42_mac.yaml` | 4+ alertas |
| S42-OBS-002 | Criar dashboard `s42_mac.json`: simulations/hour, batch_runs/day, latency_p50/p95/p99, error_rate, mi_access_by_role, determinism_rate | `observability/dashboards/s42_mac.json` | Dashboard importavel |
| S42-OBS-003 | Implementar metricas Prometheus: mac_simulation_duration_seconds, mac_simulation_total, mac_batch_run_total, mac_batch_run_duration_seconds, mac_replay_concordance, mi_access_total | `app/mac/metrics.py` | 6+ metricas |
| S42-OBS-004 | Implementar correlacao por simulation_id/run_id em todos os logs | `app/mac/logging.py` | Correlacao funcional |

### Tasks W6 — Runbooks Operacionais

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-DOC-001 | Criar runbook `S42_simulation_timeout.md`: sintomas, diagnostico, resolucao | `docs/runbooks/S42_simulation_timeout.md` | Runbook completo |
| S42-DOC-002 | Criar runbook `S42_batch_failure.md` | `docs/runbooks/S42_batch_failure.md` | Runbook completo |
| S42-DOC-003 | Criar runbook `S42_rbac_violation.md` | `docs/runbooks/S42_rbac_violation.md` | Runbook completo |
| S42-DOC-004 | Criar runbook `S42_replay_mismatch.md` | `docs/runbooks/S42_replay_mismatch.md` | Runbook completo |
| S42-DOC-005 | Criar runbook `S42_determinism_failure.md` | `docs/runbooks/S42_determinism_failure.md` | Runbook completo |
| S42-DOC-006 | Criar politica de retencao `S42_retention_policy.md`: quanto tempo manter runs, como limpar | `docs/runbooks/S42_retention_policy.md` | Policy definida |

### Tasks W6 — Bundle e Evidencias

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-BND-001 | Gerar scorecard G30 com TODOS campos obrigatorios | `out/scorecards/S42_G30_mac_simulate.json` | Schema validation |
| S42-BND-002 | Gerar scorecard G31 com accuracy, attack_detection, replay_concordance | `out/scorecards/S42_G31_mac_batch.json` | Schema validation |
| S42-BND-003 | Gerar scorecard G32 | `out/scorecards/S42_G32_adiabatic_plan.json` | Schema validation |
| S42-BND-004 | Gerar scorecard G33 com rbac_tests, redaction_tests, pii_leaks=0 | `out/scorecards/S42_G33_mi_exposure.json` | Schema validation |
| S42-BND-005 | Gerar scorecard G34 | `out/scorecards/S42_G34_ui.json` | Schema validation |
| S42-BND-006 | Gerar scorecard G35 com ORR checklist completo | `out/scorecards/S42_G35_orr.json` | ORR checklist |
| S42-BND-007 | Implementar redaction automatica de evidencias MI em out/ | `scripts/redact_evidence.py` | Redaction aplicada |
| S42-BND-008 | Gerar bundle ZIP com scorecards/, evidence/, manifests/, logs/, screenshots/, REDACTED por default | `out/bundles/inspectah_s42_evidence_bundle.zip` | Bundle completo |

**Total W6:** 26 tasks

---

## Matriz de Cobertura Final

### Gates -> Tasks

| Gate | Tasks Core | Tasks Teste | Tasks CI | Tasks Bundle | Total |
|------|------------|-------------|----------|--------------|-------|
| G30 | S42-BE-010..023, S42-API-001..007 | S42-TST-001..002 | S42-CI-001 | S42-BND-001 | 28 |
| G31 | S42-BE-030..041, S42-API-010..014 | S42-TST-010..011 | S42-CI-002 | S42-BND-002 | 21 |
| G32 | S42-BE-050..058, S42-API-020..025 | S42-TST-030 | S42-CI-003 | S42-BND-003 | 17 |
| G33 | S42-BE-060..071, S42-API-030..034 | S42-TST-040..042 | S42-CI-004 | S42-BND-004 | 23 |
| G34 | S42-FE-001..026, S42-UX-001..002 | S42-TST-050..054 | S42-CI-005 | S42-BND-005 | 37 |
| G35 | S42-OBS-001..004, S42-DOC-001..006, S42-PERF-001..002 | - | S42-CI-006 | S42-BND-006..008 | 18 |

### Invariantes -> Tasks

| Invariante | Tasks que Verificam | Metodo |
|------------|---------------------|--------|
| INV_S42_SIM_01 | S42-BE-015, S42-TST-002 | Assertion TruthState antes == depois |
| INV_S42_DET_01 | S42-BE-016, S42-TST-002, S42-TST-011 | Loop 100 replays + batch determinism |
| INV_S42_TRAIL_01 | S42-BE-005, S42-BE-017, S42-FE-018 | Manifest completo em toda simulacao |
| INV_S42_PRIV_01 | S42-BE-064..067, S42-TST-040..042 | RBAC + redaction + audit |
| INV_S42_QUAL_01 | S42-BND-001..008, S42-CI-001..006 | Manifests com provenance; sem PASS sintetico |

### Riscos -> Mitigacoes

| Risco | Tasks de Mitigacao |
|-------|-------------------|
| R1 (confusao sim=prod) | S42-FE-015, S42-UX-001, S42-FE-026 |
| R2 (nao-determinismo) | S42-BE-016, S42-TST-002, S42-TST-011, S42-OBS-003 |
| R3 (vazamento MI) | S42-BE-064..067, S42-TST-040..042, S42-BND-007 |
| R4 (dataset bias) | S42-DAT-001..008, S42-TST-010..011 |
| R5 (plano inseguro) | S42-BE-050..057, S42-TST-030 |
| R6 (UX pesada) | S42-FE-012, S42-FE-023..025, S42-TST-053 |
| R7 (PASS sintetico) | S42-BND-001..008, S42-CI-001..006 |

---

## Totais Finais (v3.0)

| Categoria | Quantidade |
|-----------|------------|
| **Tasks totais** | **158** |
| Tasks W0 (Fundacao) | 24 |
| Tasks W1 (Simulate) | 22 |
| Tasks W2 (Batch) | 18 |
| Tasks W3 (Adiabatico) | 16 |
| Tasks W4 (MI Exposure) | 20 |
| Tasks W5 (Frontend) | 32 |
| Tasks W6 (ORR/Bundle) | 26 |
| | |
| Tasks Backend | 71 |
| Tasks Frontend | 28 |
| Tasks Testes | 17 |
| Tasks Infra/CI | 6 |
| Tasks Bundle | 8 |
| Tasks Observabilidade | 4 |
| Tasks Config/Dados | 13 |
| Tasks Schemas | 3 |
| Tasks UX | 2 |
| Tasks Docs/Runbooks | 6 |
| Tasks Performance | 2 |

---

## Assinatura do Planner

```
Sprint: S42
Versao: 3.0 (MATURE)
Rodadas de refinamento: 18
Gates cobertos: G30, G31, G32, G33, G34, G35
Invariantes verificados: 5/5
Riscos mitigados: 7/7
Tasks totais: 158
Datasets: ~1100 casos canonicos
Runbooks: 6 operacionais
Status: PRONTO PARA EXECUCAO
```

*Documento gerado pelo Sprint Planner Tecnico v7*
*18 rodadas de refinamento aplicadas*
*Analise de gaps resolvida*
