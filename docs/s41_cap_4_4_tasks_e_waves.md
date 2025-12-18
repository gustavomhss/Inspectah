# S41 — Capitulo 4.4 — Tasks e Waves
## Governanca v1: CVI reputacao + Explicabilidade v2 + Anti-captura

> **Versao:** 3.0 (Refinado)
> **Data:** 2025-12-15
> **Planner:** Sprint Planner Tecnico v7
> **Fonte:** `docs/s41_tasks_execucao.yml`
> **Changelog v3.0:** +35 tasks de gap analysis (schemas, contratos, observabilidade)

---

## RESUMO EXECUTIVO

| Metrica | Valor | Nota |
|---------|-------|------|
| Total de tasks | 247 | +35 vs v2.1 |
| Total de waves | 14 (W0, W0.5, W1-W12) | +1 wave (W0.5) |
| Gates | 5 (G25-G29) | |
| Jornadas | 4 (J1-J4) | |
| Invariantes | 8 | |
| SLAs | 6 | |
| GO/NO-GO | 7/7 | |
| Gaps Addressed | 35/48 | 73% coverage |

---

## WAVES DE EXECUCAO

### W0 — Baseline & Preparacao (14 tasks)

**Objetivo:** Validar pre-condicoes e criar scaffolds.

| ID | Descricao | Tipo | Gate |
|----|-----------|------|------|
| W0.01 | Validar S40 DONE (testes passando, Truth-DB estavel) | CHECK | G29 |
| W0.02 | Verificar IDs estaveis (case_id, theme_id, actor_id) | CHECK | G26 |
| W0.03 | Definir conjunto piloto (2+ temas, 2+ casos) | DESIGN | G26 |
| W0.04 | Criar scaffold app/cvi/__init__.py | CODE | G26 |
| W0.05 | Criar scaffold app/cvi/models.py | CODE | G26 |
| W0.06 | Criar scaffold app/cvi/schemas.py | CODE | G26 |
| W0.07 | Criar scaffold app/governance/__init__.py | CODE | G28 |
| W0.08 | Criar scaffold app/governance/models.py | CODE | G28 |
| W0.09-13 | Criar estruturas out/evidence/S41_G*/ | CONFIG | G25-G29 |
| W0.14 | Criar migracao db/migrations/027_s41_cvi_tables.sql | CODE | G26 |

**Criterio de saida:** Scaffolds criados, piloto definido, S40 validado.

---

### W0.5 — Specifications & Contracts (18 tasks) [NEW]

**Objetivo:** Definir todas as especificacoes e contratos ANTES de implementar.

| ID | Descricao | Tipo | Gate |
|----|-----------|------|------|
| W0.5.01 | JSON Schema CVISnapshot (incluindo confidence) | DESIGN | G26 |
| W0.5.02 | JSON Schema ParamChangeProposal (TTL, estados) | DESIGN | G28 |
| W0.5.03 | Taxonomia AuditEvent (todos event_types) | DESIGN | G28 |
| W0.5.04 | JSON Schema Bundle auditavel | DESIGN | G28 |
| W0.5.05 | JSON Schema /api/cvi/metrics response | DESIGN | G25 |
| W0.5.06 | Modelo RBAC completo (roles, hierarchy) | DESIGN | G28 |
| W0.5.07 | Contrato P1 (Data Hub) -> CVI | DESIGN | G26 |
| W0.5.08 | Contrato P2 (Claims) <-> CVI | DESIGN | G27 |
| W0.5.09 | Contrato E40.5 <-> CVI | DESIGN | G29 |
| W0.5.10 | Criterios selecao piloto | DESIGN | G26 |
| W0.5.11 | Contract test matrix | DESIGN | G25 |
| W0.5.12 | RBAC test matrix | DESIGN | G28 |
| W0.5.13 | CVI pipeline test data specs | DESIGN | G26 |
| W0.5.14 | JSON Schema MANIFEST.json | DESIGN | G29 |
| W0.5.15 | JSON Schema coherence_review.json | DESIGN | G26 |
| W0.5.16 | JSON Schema sla_report.json | DESIGN | G29 |
| W0.5.17 | JSON Schema go_no_go_7of7.json | DESIGN | G29 |
| W0.5.18 | Wave dependency DAG | DESIGN | G29 |

**Criterio de saida:** Todos schemas e contratos documentados e validados.
**IMPORTANTE:** Esta wave DEVE ser completada antes de W1.

---

### W1 — Models & Repository (18 tasks)

**Objetivo:** Implementar modelos de dados canonicos.

| ID | Descricao | Tipo | Gate |
|----|-----------|------|------|
| W1.01-02 | CVISnapshot model + schema | CODE | G26 |
| W1.03-04 | Coverage + Field embedded models | CODE | G26 |
| W1.05-06 | ActorProfile model + schema | CODE | G26 |
| W1.07 | IncentiveSignal model | CODE | G26 |
| W1.08 | Hypothesis embedded model | CODE | G26 |
| W1.09-11 | AuditEvent + ParamChangeProposal models | CODE | G28 |
| W1.12 | CVIRepository (CRUD) | CODE | G26 |
| W1.13 | AuditRepository (append-only) | CODE | G28 |
| W1.14-18 | Testes unitarios modelos e repositorios | TEST | G26/G28 |

**Criterio de saida:** Todos os modelos implementados com testes passando.

---

### W2 — CVI Pipeline (20 tasks)

**Objetivo:** Implementar pipeline de processamento CVI.

| ID | Descricao | Tipo | Gate |
|----|-----------|------|------|
| W2.01 | Criar app/cvi/pipeline/__init__.py | CODE | G26 |
| W2.02-04 | IncentiveExtractor (internal/manual/external) | CODE | G26 |
| W2.05-06 | ActorProfiler (profile + aggregate) | CODE | G26 |
| W2.07-08 | CVIAssembler (field + magnitudes) | CODE | G26 |
| W2.09-11 | CVIAnalyzer (coverage/gaps/hypotheses) | CODE | G26 |
| W2.12-13 | ProvenanceCollector (manifest/version) | CODE | G26 |
| W2.14 | Validar rep sempre presente | CODE | G26 |
| W2.15 | Validar hypotheses[] quando proxy | CODE | G26 |
| W2.16-20 | Testes unitarios + integracao pipeline | TEST | G26 |

**Criterio de saida:** Pipeline completo, invariantes validadas.

---

### W3 — CVI Services & APIs (22 tasks)

**Objetivo:** Implementar servicos e rotas CVI.

| ID | Descricao | Tipo | Gate |
|----|-----------|------|------|
| W3.01 | Criar app/cvi/services/__init__.py | CODE | G26 |
| W3.02-06 | CVIQueryService (snapshot/history/actors/provenance) | CODE | G26 |
| W3.07-11 | CVIAdminService (propose/approve/reject/signal/recompute) | CODE | G26 |
| W3.12-15 | CVIMetricsEmitter (cov_atores/cov_alta_infl/pct_atualizado/inexplicable) | CODE | G26 |
| W3.16-17 | Rotas CVI Query + Admin | CODE | G25 |
| W3.18 | RBAC nas rotas CVI | CODE | G28 |
| W3.19-22 | Testes services + contract tests | TEST | G25/G26 |

**Criterio de saida:** APIs funcionando, RBAC aplicado, contract tests passando.

---

### W4 — Governance & Anti-captura (24 tasks)

**Objetivo:** Implementar governanca e anti-captura P5.

| ID | Descricao | Tipo | Gate |
|----|-----------|------|------|
| W4.01-03 | AuditService (append-only + trail) | CODE | G28 |
| W4.04-05 | RBACService (fail-closed + allowlist) | CODE | G28 |
| W4.06-08 | RoleValidator (P5-5 incompatibilidades) | CODE | G28 |
| W4.09-11 | P5MetricsCalculator (HHI/capture_suspect/alert) | CODE | G28 |
| W4.12-13 | BundleService (generate/export) | CODE | G28 |
| W4.14-19 | Rotas Governance + RBAC | CODE | G25/G28 |
| W4.20-24 | Testes audit/rbac/roles/p5/routes | TEST | G25/G28 |

**Criterio de saida:** Anti-captura operacional, 403 negativo testado.

---

### W5 — Integracao Explicabilidade (16 tasks)

**Objetivo:** Integrar CVI com ExplainService existente.

| ID | Descricao | Tipo | Gate |
|----|-----------|------|------|
| W5.01-02 | Modificar ExplainService para cvi_snapshot_id | CODE | G27 |
| W5.03-05 | Estados explicitos (no_data/stale/hypothesis) | CODE | G27 |
| W5.06-07 | Drill-down >= 3 + provenance chain | CODE | G27 |
| W5.08 | Caching com invalidacao | CODE | G27 |
| W5.09 | Garantir p95 < 900ms | PERF | G27 |
| W5.10-15 | Testes integracao + estados + p95 | TEST | G27 |
| W5.16 | Atualizar OpenAPI spec | CODE | G25 |

**Path real:** `app/explainability/service.py` (nao `app/explain/`)

**Criterio de saida:** Explain v2 integrado, p95 < 900ms.

---

### W6 — Frontend CVI (20 tasks)

**Objetivo:** Implementar componentes FE para CVI.

| ID | Descricao | Tipo | Gate |
|----|-----------|------|------|
| W6.01-02 | types.ts + api.ts | CODE | G27 |
| W6.03-04 | Hooks useCVISnapshot/useCVIActors | CODE | G27 |
| W6.05-12 | Componentes (Overlay/Header/ActorList/Card/Provenance/Filter/Badge/Disclaimer) | CODE | G27 |
| W6.13-15 | State machine + skeleton + error boundaries | CODE | G27 |
| W6.16 | Integrar no ExplainPanel | CODE | G27 |
| W6.17-20 | Testes FE unitarios | TEST | G27 |

**Path:** `frontend/inspectah-ui/src/features/cvi/`

**Criterio de saida:** Componentes funcionando, state machine implementada.

---

### W7 — Frontend Governance (12 tasks)

**Objetivo:** Implementar componentes FE para governanca.

| ID | Descricao | Tipo | Gate |
|----|-----------|------|------|
| W7.01-02 | types.ts + api.ts | CODE | G28 |
| W7.03-09 | Componentes (AuditTrail/EventCard/Proposal/Approval/P5Dashboard/Alert/Export) | CODE | G28 |
| W7.10-12 | Testes FE unitarios | TEST | G28 |

**Path:** `frontend/inspectah-ui/src/features/governance/`

**Criterio de saida:** Componentes funcionando.

---

### W8 — UX & Microcopy (10 tasks)

**Objetivo:** Definir UX e microcopy para estados criticos.

| ID | Descricao | Tipo | Gate |
|----|-----------|------|------|
| W8.01-05 | Microcopy estados CVI (loading/ready/stale/error/no_data) | UX | G27 |
| W8.06-08 | Tooltips + disclaimers + CTAs | UX | G27 |
| W8.09 | Feedback visual mutacoes | UX | G28 |
| W8.10 | Acessibilidade WCAG 2.1 AA | UX | G27 |

**Criterio de saida:** Microcopy definido, acessibilidade validada.

---

### W9 — E2E & Contract Tests (12 tasks)

**Objetivo:** Testes E2E por jornada + contract tests.

| ID | Descricao | Tipo | Gate |
|----|-----------|------|------|
| W9.01-04 | Playwright J1-J4 | TEST | G27/G28 |
| W9.05-06 | Contract tests OpenAPI + breaking changes | TEST | G25 |
| W9.07 | Testes regressao S40 | TEST | G29 |
| W9.08-09 | Testes 403 negativo + 2-person rule | TEST | G28 |
| W9.10-12 | Testes invariantes INV_PROVENANCE/ANTI_BOTECO/AUDIT | TEST | G26/G28 |

**Criterio de saida:** Todos os testes passando.

---

### W10 — Observabilidade (8 tasks)

**Objetivo:** Dashboards e alertas.

| ID | Descricao | Tipo | Gate |
|----|-----------|------|------|
| W10.01-02 | Dashboards CVI + Governance (Grafana) | CONFIG | G26/G28 |
| W10.03-04 | Alertas Anexo D + P5-7 | CONFIG | G26/G28 |
| W10.05-07 | Logs + tracing spans | CODE | G26/G28 |
| W10.08 | Metrica explain_p95_ms no dashboard | CODE | G27 |

**Criterio de saida:** Observabilidade operacional.

---

### W11 — Gates & QA (15 tasks)

**Objetivo:** Executar gates G25-G28.

| ID | Descricao | Tipo | Gate |
|----|-----------|------|------|
| W11.01-05 | Criar scripts bin/s41_g*.sh | CODE | G25-G29 |
| W11.06-09 | Executar gates G25-G28 | GATE | G25-G28 |
| W11.10-14 | Validar metricas minimas (cov_alta_infl/pct_atualizado/inexplicable/p95/drill) | CHECK | G26/G27 |
| W11.15 | Gerar coherence_review.json (6+ decisoes) | EVIDENCE | G26 |

**Criterio de saida:** G25-G28 PASS.

---

### W12 — ORR & GO/NO-GO (16 tasks)

**Objetivo:** Consolidar ORR e validar GO/NO-GO 7/7.

| ID | Descricao | Tipo | Gate |
|----|-----------|------|------|
| W12.01-06 | Medir SLAs S40-S43 (P1/P2/P3/P4/Reversao/Abuso) | SLA | G29 |
| W12.07 | Gerar sla_report.json | EVIDENCE | G29 |
| W12.08-14 | Validar GO/NO-GO 7/7 | CHECK | G29 |
| W12.15 | Gerar go_no_go_7of7.json | GATE | G29 |
| W12.16 | Consolidar S41_ORR.json + summary | GATE | G29 |

**Criterio de saida:** G29 PASS, 7/7 GO.

---

## DEPENDENCIAS ENTRE WAVES

```
W0 (baseline)
 ├──> W1 (models)
 │     ├──> W2 (pipeline)
 │     │     └──> W3 (services/APIs)
 │     │           ├──> W5 (explain integration)
 │     │           │     └──> W6 (FE CVI)
 │     │           │           └──> W8 (UX)
 │     │           └──> W4 (governance)
 │     │                 └──> W7 (FE governance)
 │     └──> W10 (observability)
 └──> W9 (E2E tests) <── W6, W7, W8
       └──> W11 (gates)
             └──> W12 (ORR)
```

---

## JORNADAS MAPEADAS

| Jornada | Persona | Fluxo | Playwright | Validacao |
|---------|---------|-------|------------|-----------|
| J1 | Operador | decisao -> explain -> CVI -> provenance | s41_j1_decision_cvi.pw.ts | Cap5/B2 |
| J2 | Admin | proposta -> 2-person -> audit_event -> nova versao | s41_j2_param_change.pw.ts | Cap5/B3 |
| J3 | Auditor | selecionar -> bundle -> verificar | s41_j3_audit_bundle.pw.ts | Cap5/B4 |
| J4 | Operador/Auditor | cobertura baixa -> UX explicita -> CTA | s41_j4_insufficient_data.pw.ts | Cap4/B3 (inferido) |

**Nota:** J4 foi inferida do Cap4/B3 (cenarios de falha). Nao e jornada canonica da spec.

---

## INVARIANTES

| ID | Regra | Tasks | Consequencia |
|----|-------|-------|--------------|
| INV_PROVENANCE_01 | Toda resposta CVI inclui provenance | W2.12-13, W3.06, W9.10 | API sem = P0 |
| INV_ANTI_BOTECO_01 | Incentivo sem lastro = hipotese | W2.11, W5.05, W6.12, W8.07, W9.11 | UI sem badge = P0 |
| INV_AUDIT_01 | Toda alteracao gera audit_event | W4.02-03, W9.12 | Mutacao sem trilha = P0 |
| INV_ANTI_CAPTURA_01 | Papeis incompativeis bloqueados | W4.06-08 | Bypass = P0 |
| INV_RBAC_01 | Rota nova sem allowlist = bug | W3.18, W4.04-05, W4.19 | Deploy = BLOCK |
| INV_2PERSON_01 | Proponente != Aprovador | W3.08, W9.09 | Mesmo usuario = P0 |
| INV_REP_01 | Campo rep sempre presente | W2.14 | Ausencia = P0 |
| INV_HYPOTHESES_01 | hypotheses[] nunca vazio com proxy | W2.15 | Array vazio = P0 |

---

## SLAs S40-S43

| Metrica | Limite | Task |
|---------|--------|------|
| P1 Latencia | <= 1 min | W12.01 |
| P2 Precisao | >= 92% | W12.02 |
| P3 Decisao | <= 10 s | W12.03 |
| P4 API | <= 100 ms | W12.04 |
| Reversao | <= 4% | W12.05 |
| Abuso | <= 1% | W12.06 |

---

## GO/NO-GO 7/7

| # | Criterio | Task |
|---|----------|------|
| 1 | Checklist 100% completo | W12.08 |
| 2 | Quadros de Guias referenciados | W12.09 |
| 3 | Testes passando | W12.10 |
| 4 | SLAs dentro dos limites | W12.11 |
| 5 | Documentacao atualizada | W12.12 |
| 6 | E40.5 operando | W12.13 |
| 7 | Pre-condicoes eticas verificadas | W12.14 |

### O que e E40.5?

**E40.5 (P3-E1 Logic Engines)** e o motor de logica do Inspectah:
- Epico ESTRUTURAL que valida claims
- Todo DecisionBlock DEVE passar por E40.5
- DecisionBlock sem `e40_5` = INVALIDO
- Referencia: `docs/DNA/README.md` §0.2, §0.3

**Validacao E40.5 (W12.13):**
- Verificar que DecisionBlocks gerados possuem campo `e40_5`
- Verificar que transicoes criticas passam pelo motor
- Referencia: P2-0 (Motor E40.5), MQV-01

---

## EVIDENCIAS OBRIGATORIAS

```
out/scorecards/
├── S41_G25_contracts.json
├── S41_G26_cvi.json
├── S41_G27_explainability.json
├── S41_G28_governance_audit.json
├── S41_G29_orr.json
└── S41_ORR.json

out/evidence/
├── S41_G25_contracts/
│   ├── checks.json
│   ├── MANIFEST.json
│   └── openapi_spec.yaml
├── S41_G26_cvi/
│   ├── checks.json
│   ├── MANIFEST.json
│   ├── snapshots_sample.json      <-- Gerar em W11.07
│   └── coherence_review.json      <-- Gerar em W11.15
├── S41_G27_explainability/
│   ├── checks.json
│   ├── MANIFEST.json
│   └── playwright_results/
├── S41_G28_governance_audit/
│   ├── checks.json
│   ├── MANIFEST.json
│   ├── audit_trail_sample.json    <-- Gerar em W11.09
│   └── rbac_403_test.log
├── S41_G29_orr/
│   ├── checks.json
│   ├── MANIFEST.json
│   ├── sla_report.json
│   └── go_no_go_7of7.json
└── S41_ORR_summary.txt
```

---

## NOTAS DE EXECUCAO

### Dependencia S40
- S40 nao tem spec escrita
- W0.01 deve validar baseline minimo (Truth-DB operacional)
- Se S40 indisponivel: usar dados sinteticos + scaffold minimo
- W9.07 (regressao S40) pode ser adaptado para baseline disponivel

### Paths de Codigo
- ExplainService: `app/explainability/service.py` (NAO `app/explain/`)
- CVI: `app/cvi/` (a criar)
- Governance: `app/governance/` (a criar)
- FE CVI: `frontend/inspectah-ui/src/features/cvi/`
- FE Governance: `frontend/inspectah-ui/src/features/governance/`

### Migracoes DB
- `db/migrations/027_s41_cvi_tables.sql` - tabelas CVI
- `db/migrations/028_s41_audit_tables.sql` - tabelas audit (adicionar se necessario)

---

**Gerado por:** Sprint Planner Tecnico v7
**Data:** 2025-12-15
**Versao:** 2.1
