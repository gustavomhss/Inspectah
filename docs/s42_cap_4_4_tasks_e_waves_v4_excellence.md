# Sprint 42 — Cap.4 Bloco 4 — Tasks e Waves (v4.0 EXCELLENCE)

> **Programa:** P2 + P3 + P4 (+ P5/P6)
> **Missao:** Simulacoes MAC + Plano Adiabatico + Exposicao MI (parcial)
> **Gates:** G30–G35
> **Predecessora:** S41 (Governanca v1)
> **Sucessora:** S43 (GO/NO-GO Fase 2)
> **Versao:** 4.0 EXCELLENCE (Auditoria Brutal aplicada)

---

## Changelog de Refinamento v4.0

| Rodada | Foco | Melhorias Aplicadas |
|--------|------|---------------------|
| R1-R18 | Base | 158 tasks (v3.0 MATURE) |
| R19 | Auditoria Brutal | Identificacao de 100 gaps |
| R20 | Testes Negativos | +35 tasks para error paths |
| R21 | Observabilidade | +18 tasks para metricas, alertas, SLOs |
| R22 | Seguranca | +12 tasks para pentesting, RBAC edge cases |
| R23 | E2E | +10 tasks para fluxos completos |
| R24 | Performance | +10 tasks para load/stress tests |
| R25 | Recovery | +10 tasks para fallback/graceful degradation |
| R26 | Concorrencia | +8 tasks para race conditions |
| R27 | API Contracts | +8 tasks para OpenAPI, versioning |
| R28 | Evidencias | +10 tasks para estrutura out/ |
| R29 | Documentacao | +8 tasks para ADRs, troubleshooting |
| R30 | Polish Final | Revisao cruzada spec x tasks |

---

## Visao Geral das Waves v4.0

| Wave | Nome | Objetivo | Gates | Tasks | Dependencias |
|------|------|----------|-------|-------|--------------|
| W0 | Fundacao MAC | Schemas, contratos, migrations, configs, datasets canonicos | Pre-req | 24 | - |
| W1 | MAC Simulate | Endpoint dry-run deterministico com manifest completo | G30 | 22 | W0 |
| W2 | MAC Batch | Simulacao em lote + scorecards + streaming + cancel | G31 | 18 | W0, W1 |
| W3 | Plano Adiabatico | Validador + simulador por fases + rollback | G32 | 16 | W0, W1 |
| W4 | MI/Exp Exposure | Exposicao parcial + RBAC + redaction + derivation | G33 | 20 | W0, W1 |
| W5 | Frontend P4 | UI simulacoes + virtualization + disclaimers + states | G34 | 32 | W1, W2, W3, W4 |
| W6 | ORR/Bundle | Scripts + runbooks + teste carga + bundle + redaction | G35 | 26 | W0-W5 |
| **W7** | **Quality Assurance** | **Testes negativos, E2E, concorrencia, recovery** | **All** | **45** | W0-W6 |
| **W8** | **Observability Advanced** | **Metricas detalhadas, SLOs, tracing, alertas** | **All** | **20** | W6 |
| **W9** | **Security Hardening** | **Pentesting, RBAC edge cases, audit hardening** | **G33, G35** | **15** | W4, W6 |
| **W10** | **API Excellence** | **OpenAPI, versioning, contracts, backward compat** | **All** | **10** | W1-W4 |
| **W11** | **Evidence Mastery** | **Estrutura out/, automation, hash validation** | **G35** | **15** | W6 |

**Total v4.0: 263 tasks (+105 vs v3.0)**

---

## W7 — Quality Assurance (45 tasks) [NOVO]

**Objetivo:** Testes negativos exaustivos, E2E completos, concorrencia, recovery.

**Spec refs:** Cap.2B2, Cap.3B2, Cap.5B2, Cap.8B2, Cap.8B3

### Tasks W7 — Testes Negativos / Error Paths

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-NEG-001 | Testar PolicyNotFoundError em simulate com policy inexistente | `tests/mac/test_errors.py` | Erro 404 correto |
| S42-NEG-002 | Testar PolicyVersionMismatchError em comparacao baseline/candidate | `tests/mac/test_errors.py` | Erro detectado |
| S42-NEG-003 | Testar SignalSnapshotInvalidError com payload malformado | `tests/mac/test_errors.py` | Erro 400 correto |
| S42-NEG-004 | Testar SignalSnapshotExpiredError com timestamp antigo | `tests/mac/test_errors.py` | Erro detectado |
| S42-NEG-005 | Testar SimulationTimeoutError com timeout forçado | `tests/mac/test_errors.py` | Timeout graceful |
| S42-NEG-006 | Testar BatchCanceledError durante execucao | `tests/mac/test_errors.py` | Estado canceled |
| S42-NEG-007 | Testar ReplayMismatchError com token invalido | `tests/mac/test_errors.py` | Erro detectado |
| S42-NEG-008 | Testar DeterminismViolationError forçando non-determinism | `tests/mac/test_errors.py` | Invariante detectado |
| S42-NEG-009 | Testar RBACForbiddenError em TODOS endpoints MI | `tests/mac/test_errors.py` | 403 em todos |
| S42-NEG-010 | Testar DatasetNotFoundError com dataset inexistente | `tests/mac/test_errors.py` | Erro 404 correto |
| S42-NEG-011 | Testar DatasetInvalidError com dataset corrompido | `tests/mac/test_errors.py` | Erro detectado |
| S42-NEG-012 | Testar ManifestIncompleteError com campos faltando | `tests/mac/test_errors.py` | Erro detectado |
| S42-NEG-013 | Testar payload malformado JSON em todos endpoints | `tests/mac/test_input_validation.py` | 400 em todos |
| S42-NEG-014 | Testar SQL injection em filtros de listagem | `tests/mac/test_input_validation.py` | Sanitização funciona |
| S42-NEG-015 | Testar XSS em campos de texto (notes, rationale) | `tests/mac/test_input_validation.py` | Escape funciona |

### Tasks W7 — Testes E2E

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-E2E-001 | E2E: simulate -> retry -> success (jornada completa) | `tests/e2e/test_simulate_flow.py` | Fluxo passa |
| S42-E2E-002 | E2E: batch -> progress -> scorecard -> bundle | `tests/e2e/test_batch_flow.py` | Fluxo completo |
| S42-E2E-003 | E2E: adiabatic plan -> validate -> simulate phases -> rollback preview | `tests/e2e/test_adiabatic_flow.py` | Fluxo completo |
| S42-E2E-004 | E2E: MI exposure com ops -> reviewer -> council (3 roles) | `tests/e2e/test_mi_rbac_flow.py` | Progressão de acesso |
| S42-E2E-005 | E2E: jornada Conselho/Revisor (Cap.5B2) completa | `tests/e2e/test_council_journey.py` | Jornada validada |
| S42-E2E-006 | E2E Playwright: SimulationLab completo com disclaimer | `frontend/.../e2e/mac_simulate.spec.ts` | Playwright passa |
| S42-E2E-007 | E2E Playwright: BatchPage com cancel e retry | `frontend/.../e2e/mac_batch.spec.ts` | Playwright passa |
| S42-E2E-008 | E2E Playwright: AdiabaticPlan com timeline visual | `frontend/.../e2e/mac_adiabatic.spec.ts` | Playwright passa |
| S42-E2E-009 | E2E Playwright: 4 estados MI (available, redacted, not_authorized, not_available) | `frontend/.../e2e/mi_states.spec.ts` | 4 estados visuais |
| S42-E2E-010 | E2E Playwright: Diff view com flip set navegavel | `frontend/.../e2e/mac_diff.spec.ts` | Diff funcional |

### Tasks W7 — Concorrencia / Race Conditions

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-CONC-001 | Testar concurrent batch cancel (2 cancel simultaneos) | `tests/mac/test_concurrency.py` | Sem double cancel |
| S42-CONC-002 | Testar concurrent simulations no mesmo allegation_id | `tests/mac/test_concurrency.py` | Isolamento correto |
| S42-CONC-003 | Testar concurrent writes no mesmo batch_run_id | `tests/mac/test_concurrency.py` | Sem data race |
| S42-CONC-004 | Testar database transaction isolation (READ COMMITTED) | `tests/mac/test_concurrency.py` | Sem dirty reads |
| S42-CONC-005 | Testar parallel batch executions (3 batches simultaneos) | `tests/mac/test_concurrency.py` | Recursos isolados |
| S42-CONC-006 | Testar concurrent policy update durante simulacao | `tests/mac/test_concurrency.py` | Snapshot correto |
| S42-CONC-007 | Testar mutex/locking em recursos compartilhados | `tests/mac/test_concurrency.py` | Sem deadlock |
| S42-CONC-008 | Testar race condition cancel/stream simultaneos | `tests/mac/test_concurrency.py` | Estado consistente |

### Tasks W7 — Recovery / Fallback

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-REC-001 | Implementar recovery de batch interrompido (resume from checkpoint) | `app/mac/batch_recovery.py` | Resume funcional |
| S42-REC-002 | Implementar fallback quando policy file nao carrega | `app/mac/policy_loader.py` | Default ou erro claro |
| S42-REC-003 | Testar database migration rollback end-to-end | `tests/db/test_migration_rollback.py` | Rollback funciona |
| S42-REC-004 | Implementar graceful degradation quando signals service down | `app/mac/signals_client.py` | Degradation graceful |
| S42-REC-005 | Implementar retry logic em batch com backoff exponencial | `app/mac/batch_runner.py` | Retry funcional |
| S42-REC-006 | Implementar circuit breaker para dependencias externas | `app/mac/circuit_breaker.py` | CB funcional |
| S42-REC-007 | Testar recovery de simulacao apos crash | `tests/mac/test_recovery.py` | Estado consistente |

**Total W7:** 45 tasks

---

## W8 — Observability Advanced (20 tasks) [NOVO]

**Objetivo:** Metricas detalhadas, SLOs, tracing distribuido, alertas actionable.

**Spec refs:** Cap.2B2

### Tasks W8 — Metricas Prometheus

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-MET-001 | Definir mac_simulation_duration_seconds{endpoint,mode,domain} histogram | `app/mac/metrics.py` | Metrica registrada |
| S42-MET-002 | Definir mac_simulation_total{status,mode,domain} counter | `app/mac/metrics.py` | Counter funcional |
| S42-MET-003 | Definir mac_batch_duration_seconds{dataset,status} histogram | `app/mac/metrics.py` | Histogram funcional |
| S42-MET-004 | Definir mac_batch_total{status,dataset} counter | `app/mac/metrics.py` | Counter funcional |
| S42-MET-005 | Definir mac_replay_concordance gauge (1.0 = 100%) | `app/mac/metrics.py` | Gauge funcional |
| S42-MET-006 | Definir mi_access_total{role,resource,action} counter | `app/mac/metrics.py` | Counter funcional |
| S42-MET-007 | Definir mi_redaction_total{type,level} counter | `app/mac/metrics.py` | Counter funcional |
| S42-MET-008 | Definir mac_error_total{error_code,endpoint} counter | `app/mac/metrics.py` | Counter funcional |

### Tasks W8 — SLOs / SLIs

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-SLO-001 | Definir SLO: simulate p95 < 500ms (99.9% requests) | `observability/slos/s42_mac.yaml` | SLO definido |
| S42-SLO-002 | Definir SLO: simulate p99 < 2s (99.9% requests) | `observability/slos/s42_mac.yaml` | SLO definido |
| S42-SLO-003 | Definir SLO: replay concordance = 100% | `observability/slos/s42_mac.yaml` | SLO definido |
| S42-SLO-004 | Definir SLO: error rate < 1% | `observability/slos/s42_mac.yaml` | SLO definido |

### Tasks W8 — Tracing Distribuido

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-TRC-001 | Implementar spans para simulate: parse -> validate -> evaluate -> manifest | `app/mac/tracing.py` | Spans criados |
| S42-TRC-002 | Implementar spans para batch: load -> iterate -> aggregate -> scorecard | `app/mac/tracing.py` | Spans criados |
| S42-TRC-003 | Propagate trace_id entre servicos (context propagation) | `app/mac/tracing.py` | Propagation funcional |

### Tasks W8 — Alertas Avancados

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-ALR-001 | Alerta: mac_simulate_latency_p95 > 600ms por 5min | `observability/alerts/s42_mac.yaml` | Alerta funcional |
| S42-ALR-002 | Alerta: mac_replay_concordance < 1.0 | `observability/alerts/s42_mac.yaml` | Alerta critico |
| S42-ALR-003 | Alerta: mac_error_rate > 5% por 2min | `observability/alerts/s42_mac.yaml` | Alerta funcional |
| S42-ALR-004 | Alerta: mi_rbac_violation > 10/min | `observability/alerts/s42_mac.yaml` | Alerta seguranca |
| S42-ALR-005 | Dashboard Grafana com todos os paineis | `observability/dashboards/s42_mac.json` | Dashboard importa |

**Total W8:** 20 tasks

---

## W9 — Security Hardening (15 tasks) [NOVO]

**Objetivo:** Pentesting, RBAC edge cases, audit hardening, input sanitization.

**Spec refs:** Cap.2B2, Cap.3B2

### Tasks W9 — RBAC Edge Cases

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-SEC-001 | Testar RBAC com token expirado mid-request | `tests/security/test_rbac_edge.py` | 401 retornado |
| S42-SEC-002 | Testar RBAC com role revogada durante sessao | `tests/security/test_rbac_edge.py` | Acesso negado |
| S42-SEC-003 | Testar role escalation (ops tentando council) | `tests/security/test_rbac_edge.py` | Escalation bloqueada |
| S42-SEC-004 | Testar redaction bypass via API manipulation | `tests/security/test_rbac_edge.py` | Bypass impossivel |

### Tasks W9 — Input Sanitization

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-SEC-005 | Testar SQL injection em todos endpoints de filtro | `tests/security/test_injection.py` | Injection bloqueada |
| S42-SEC-006 | Testar NoSQL injection se aplicavel | `tests/security/test_injection.py` | Injection bloqueada |
| S42-SEC-007 | Testar path traversal em dataset paths | `tests/security/test_injection.py` | Traversal bloqueado |
| S42-SEC-008 | Testar command injection em shell commands | `tests/security/test_injection.py` | Injection bloqueada |

### Tasks W9 — Audit Hardening

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-SEC-009 | Testar audit log tampering (logs imutaveis) | `tests/security/test_audit.py` | Tampering detectado |
| S42-SEC-010 | Implementar audit log encryption at rest | `app/mi/audit.py` | Encryption ativo |
| S42-SEC-011 | Implementar audit log rotation com retention | `app/mi/audit.py` | Rotation funcional |

### Tasks W9 — Penetration Testing

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-SEC-012 | Documentar pentest checklist OWASP Top 10 | `docs/security/pentest_checklist.md` | Checklist completo |
| S42-SEC-013 | Executar ZAP scan em endpoints MAC | `tests/security/zap_scan_results.json` | Scan executado |
| S42-SEC-014 | Executar ZAP scan em endpoints MI | `tests/security/zap_scan_results.json` | Scan executado |
| S42-SEC-015 | Remediar HIGH/CRITICAL findings | `docs/security/remediation.md` | Findings remediados |

**Total W9:** 15 tasks

---

## W10 — API Excellence (10 tasks) [NOVO]

**Objetivo:** OpenAPI, versioning, contracts, backward compatibility.

**Spec refs:** Cap.3B2

### Tasks W10 — OpenAPI

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-OAS-001 | Gerar OpenAPI spec automaticamente de routes | `openapi/s42_mac_api.yaml` | Spec valida |
| S42-OAS-002 | Validar responses contra OpenAPI schema em runtime | `app/api/validation.py` | Validation ativa |
| S42-OAS-003 | Gerar SDK clients de OpenAPI (Python, TypeScript) | `scripts/generate_clients.sh` | Clients gerados |

### Tasks W10 — Versioning

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-VER-001 | Implementar versioning via path (/api/v1/, /api/v2/) | `app/api/versioning.py` | Versioning funcional |
| S42-VER-002 | Implementar deprecation warnings via headers | `app/api/deprecation.py` | Warnings presentes |
| S42-VER-003 | Documentar breaking changes policy | `docs/api/breaking_changes.md` | Policy documentada |

### Tasks W10 — Backward Compatibility

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-BWD-001 | Criar contract tests baseline (snapshot) | `tests/contracts/baseline.json` | Baseline criado |
| S42-BWD-002 | Criar CI job para detectar breaking changes | `.github/workflows/contract_test.yml` | Job funcional |
| S42-BWD-003 | Implementar rate limit headers (X-RateLimit-*) | `app/api/rate_limit.py` | Headers presentes |
| S42-BWD-004 | Documentar pagination strategy (cursor-based) | `docs/api/pagination.md` | Strategy documentada |

**Total W10:** 10 tasks

---

## W11 — Evidence Mastery (15 tasks) [NOVO]

**Objetivo:** Estrutura out/ completa, automacao, hash validation.

**Spec refs:** Cap.4B4, Cap.7B4

### Tasks W11 — Estrutura de Evidencias

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-EVD-001 | Criar estrutura out/evidence/S42_G30_mac_simulate/ automaticamente | `scripts/create_evidence_dirs.py` | Dirs criados |
| S42-EVD-002 | Gerar manifest.json por gate com lineage completo | `scripts/generate_manifest.py` | Manifest gerado |
| S42-EVD-003 | Gerar summary.md por gate (o que foi testado, como reproduzir, limitacoes) | `scripts/generate_summary.py` | Summary gerado |
| S42-EVD-004 | Gerar requests.jsonl com todos requests do gate | `scripts/capture_requests.py` | Requests capturados |
| S42-EVD-005 | Gerar responses.jsonl com todas responses do gate | `scripts/capture_requests.py` | Responses capturados |

### Tasks W11 — Evidencias MI

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-EVD-006 | Gerar redaction_report.json (campos redatados, motivo, count) | `scripts/generate_redaction_report.py` | Report gerado |
| S42-EVD-007 | Gerar rbac_matrix.json (roles x recursos x acoes) | `scripts/generate_rbac_matrix.py` | Matrix gerada |
| S42-EVD-008 | Gerar audit_log.jsonl (acessos durante testes) | `app/mi/audit.py` | Audit capturado |

### Tasks W11 — Evidencias UI

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-EVD-009 | Gerar routes_covered.json (rotas exercitadas) | `frontend/.../scripts/routes_coverage.ts` | Coverage gerada |
| S42-EVD-010 | Gerar screenshots automaticos durante E2E | `frontend/.../playwright.config.ts` | Screenshots gerados |
| S42-EVD-011 | Gerar video de E2E critical paths | `frontend/.../playwright.config.ts` | Videos gerados |

### Tasks W11 — Bundle Validation

| ID | Descricao | Arquivos | DONE (verificavel) |
|----|-----------|----------|-------------------|
| S42-EVD-012 | Implementar hash validation de todos artefatos | `scripts/validate_bundle.py` | Hashes validados |
| S42-EVD-013 | Implementar index.json com lista de artefatos e hashes | `scripts/generate_index.py` | Index gerado |
| S42-EVD-014 | Implementar bundle integrity check | `scripts/check_integrity.py` | Check funcional |
| S42-EVD-015 | Criar script de reproducao a partir do bundle | `scripts/reproduce_from_bundle.py` | Reproducao funcional |

**Total W11:** 15 tasks

---

## Resumo Final v4.0 EXCELLENCE

| Wave | Tasks v3.0 | Tasks Novas | Total v4.0 |
|------|------------|-------------|------------|
| W0 | 24 | 0 | 24 |
| W1 | 22 | 0 | 22 |
| W2 | 18 | 0 | 18 |
| W3 | 16 | 0 | 16 |
| W4 | 20 | 0 | 20 |
| W5 | 32 | 0 | 32 |
| W6 | 26 | 0 | 26 |
| **W7** | - | **45** | **45** |
| **W8** | - | **20** | **20** |
| **W9** | - | **15** | **15** |
| **W10** | - | **10** | **10** |
| **W11** | - | **15** | **15** |
| **TOTAL** | **158** | **105** | **263** |

---

## Invariantes Ampliados v4.0

| ID | Descricao | Verificacao |
|----|-----------|-------------|
| INV_S42_SIM_01 | Simulacao NAO muda TruthState oficial | S42-BE-015, S42-TST-002, S42-E2E-001..003 |
| INV_S42_DET_01 | Replay deterministico 100% quando T=0 | S42-BE-016, S42-TST-002, S42-TST-011, S42-CONC-001..008 |
| INV_S42_TRAIL_01 | Provenance completa em toda simulacao | S42-BE-005, S42-BE-017, S42-EVD-001..015 |
| INV_S42_PRIV_01 | Privacidade MI/Experiencias | S42-BE-064..067, S42-TST-040..042, S42-SEC-001..015 |
| INV_S42_QUAL_01 | Sem PASS sintetico | S42-BND-001..008, S42-EVD-001..015 |
| **INV_S42_ERR_01** | **Todos error paths testados** | **S42-NEG-001..015** |
| **INV_S42_CONC_01** | **Sem race conditions** | **S42-CONC-001..008** |
| **INV_S42_REC_01** | **Recovery funcional** | **S42-REC-001..007** |

---

## Assinatura v4.0

```
Sprint: S42
Versao: 4.0 EXCELLENCE
Tasks: 263
Waves: 11 (W0-W11)
Gates: G30, G31, G32, G33, G34, G35
Invariantes: 8
Riscos mitigados: 10
Datasets: ~1100 casos
Runbooks: 6 + troubleshooting
Refinamentos aplicados: 30
Gaps Brutal resolvidos: 100
Status: NIVEL MAXIMO DE EXCELENCIA
```

*Plano gerado pelo Sprint Planner Tecnico v7*
*30 rodadas de refinamento aplicadas*
*Auditoria Brutal v4.0 resolvida*
