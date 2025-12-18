# Sprint 40 — Capítulo 4.4: Tasks e Waves
## Truth-DB Estável (Fase 2: Truth-DB Core)

> **Fonte de verdade** para execução da S40.
> O YAML `docs/s40_tasks_execucao.yml` é derivado deste documento.

---

## 1. Visão Geral das Waves

| Wave | Nome | Objetivo | Gates | Dependências |
|------|------|----------|-------|--------------|
| W0 | Groundwork | Schemas, migrations, contratos base | G20 | — |
| W1 | P3 Core | DecisionBlock válido + E40.5 enforcement + Experiências | G23 | W0 |
| W2 | P2 Export & Signals | ClaimGraph export v1 + NO-GO signals operáveis | G22 | W0 |
| W3 | P1 Hardening | Social/oficiais estáveis + SLA P1 | G21 | W0 |
| W4 | P4 Exposure | Truth Twin + Decision Inspector + provenance | G24 | W1, W2 |
| W5 | Quality & ORR | Testes, observabilidade, scorecards, bundle | G20-G24 | W0-W4 |

---

## 2. Wave 0 — Groundwork (Schemas, Migrations, Contratos)

**Objetivo:** Estabelecer fundação técnica para todas as waves subsequentes.

**Critério de saída:** Schemas validáveis, migration aplicada, contratos documentados.

| ID | Área | Descrição | Arquivos/Módulos | Gates | DONE | Evidências |
|----|------|-----------|------------------|-------|------|------------|
| S40-INF-001 | infra | Criar schema JSON `decision_block_v1.json` com campos obrigatórios (claim_id, domain, gate, state_transition, references.guias[], references.pilares[], references.e40_5, policy_version) | `schemas/decision_block_v1.json` | G20 | Schema passa validação JSON Schema Draft-07; campos obrigatórios marcados como required | `out/evidence/S40_G20_schema_validation.json` |
| S40-INF-002 | infra | Criar schema JSON `claimgraph_export_v1.json` para export P2→P3 (nodes[], edges[], prior, evidence_trail[]) | `schemas/claimgraph_export_v1.json` | G20, G22 | Schema válido; campos prior e evidence_trail[] obrigatórios | `out/evidence/S40_G20_export_schema.json` |
| S40-INF-003 | infra | Criar schema JSON `truth_twin_v1.json` para resposta Truth Twin (claim_id, current_state, timeline[], provenance) | `schemas/truth_twin_v1.json` | G20, G24 | Schema válido; provenance obrigatória | `out/evidence/S40_G20_twin_schema.json` |
| S40-DB-001 | dados | Criar migration `033_sprint40_decision_blocks.sql` com tabela decision_blocks (id, claim_id, domain, gate, initial_state, final_state, references JSONB, policy_name, policy_version, committee_summary, evidence_refs, experience_ref, latency_ms, created_at) | `db/migrations/033_sprint40_decision_blocks.sql` | G20, G23 | Migration aplica sem erro; rollback funciona | `out/evidence/S40_G20_migration.log` |
| S40-DB-002 | dados | Criar índices otimizados para decision_blocks (claim_id, domain, gate, created_at DESC) | `db/migrations/033_sprint40_decision_blocks.sql` | G20 | Query de timeline por claim_id < 50ms | Benchmark em scorecard |
| S40-DB-003 | dados | Criar tabela `experiences` na migration (experience_id, claim_id, decision_id, embedding VECTOR, metadata JSONB, created_at) | `db/migrations/033_sprint40_decision_blocks.sql` | G23 | Tabela criada com índice para embedding similarity | `out/evidence/S40_G20_migration.log` |
| S40-BE-001 | backend | Implementar validador fail-closed para DecisionBlock em `app/truth/validators.py` | `app/truth/validators.py` | G20 | DecisionBlock sem references.guias[], references.pilares[] ou references.e40_5 retorna ValidationError; transição bloqueada | Teste unitário passa |
| S40-BE-002 | backend | Implementar validador fail-closed para Claim (requer prior + evidence_trail[]) | `app/claims/validators.py` | G20, G22 | Claim sem prior ou evidence_trail[] retorna ValidationError | Teste unitário passa |
| S40-CI-001 | ci | Criar script `bin/s40_g20_contracts.sh` que valida schemas e roda testes de contrato | `bin/s40_g20_contracts.sh` | G20 | Exit 0 com schemas válidos; exit 1 se inválido | `out/scorecards/S40_G20_contracts.json` |

---

## 3. Wave 1 — P3 Core (DecisionBlock + E40.5 + Experiências)

**Objetivo:** Tornar DecisionBlock a unidade de verdade com E40.5 obrigatório e Experiências mínimo.

**Critério de saída:** Toda transição crítica produz DecisionBlock válido; E40.5 FAIL bloqueia; Experiências append-only funciona.

| ID | Área | Descrição | Arquivos/Módulos | Gates | DONE | Evidências |
|----|------|-----------|------------------|-------|------|------------|
| S40-BE-003 | backend | Estender modelo DecisionBlock em `app/guardian/models.py` com campos references (guias[], pilares[], e40_5), experience_ref, latency_ms | `app/guardian/models.py` | G23 | Modelo tem todos os campos; migration aplicada | Teste unitário passa |
| S40-BE-004 | backend | Implementar `build_references()` em `app/truth/references.py` que monta objeto references com guias, pilares, policy, e40_5 a partir do contexto de decisão | `app/truth/references.py` | G23 | Função retorna dict com guias[], pilares[], policy{}, e40_5{}; campos não vazios | Teste unitário passa |
| S40-BE-005 | backend | Integrar E40.5 check obrigatório em `app/guardian/flow.py` (FlowContext) antes de AUTO_APPROVE | `app/guardian/flow.py` | G23 | Transição crítica sem E40.5 PASS fica em estado BLOCKED; DecisionBlock registra violations | Teste E2E passa |
| S40-BE-006 | backend | Implementar `record_decision_block()` em `app/truth/repository.py` que persiste DecisionBlock válido (append-only) | `app/truth/repository.py` | G23 | DecisionBlock gravado; histórico preservado; sem UPDATE in-place | Teste unitário passa |
| S40-BE-007 | backend | Implementar Experiências mínimo: modelo `Experience` em `app/truth/experiences.py` com campos (experience_id, claim_id, decision_id, embedding, metadata, created_at) | `app/truth/experiences.py` | G23 | Modelo criado; append-only (sem delete/update) | Teste unitário passa |
| S40-BE-008 | backend | Implementar `ExperienceRepository` com métodos `add()` e `find_similar(claim_embedding, top_n=5)` | `app/truth/experiences.py` | G23 | Retrieval por similaridade funciona; top-N retornado | Teste unitário passa |
| S40-BE-009 | backend | Integrar experience_ref em DecisionBlock: ao criar decisão, buscar experiências similares e anexar IDs | `app/guardian/service.py` | G23 | DecisionBlock.experience_ref[] populado quando experiências existem | Teste E2E passa |
| S40-BE-010 | backend | Implementar endpoint POST `/api/truth/experiences` para adicionar experiência manualmente (piloto) | `app/api/truth_routes.py` | G23 | Endpoint funciona; experiência persistida | Teste API passa |
| S40-BE-029 | backend | Implementar modo degradado em `app/guardian/flow.py`: se E40.5 indisponível, bloquear transições e marcar estado como `DEGRADED` | `app/guardian/flow.py` | G23 | E40.5 timeout → estado DEGRADED; transições bloqueadas; log registrado | Teste de resiliência passa |
| S40-BE-030 | backend | Criar script de seed `scripts/seed_experiences.py` para popular experiências iniciais do piloto | `scripts/seed_experiences.py` | G23 | Script popula 10-20 experiências de referência para domínios piloto | Experiências existem no DB |
| S40-CI-002 | ci | Criar script `bin/s40_g23_truthdb.sh` que valida DecisionBlocks, E40.5 enforcement e Experiências | `bin/s40_g23_truthdb.sh` | G23 | Exit 0 com casos A/B/C passando | `out/scorecards/S40_G23_truthdb.json` |

---

## 4. Wave 2 — P2 Export & Signals (ClaimGraph + NO-GO)

**Objetivo:** Export v1 do ClaimGraph ingerível por P3; NO-GO signals bloqueiam transições.

**Critério de saída:** Export funciona sem adaptador manual; sinais NO-GO bloqueiam de verdade.

| ID | Área | Descrição | Arquivos/Módulos | Gates | DONE | Evidências |
|----|------|-----------|------------------|-------|------|------------|
| S40-BE-011 | backend | Implementar `export_claimgraph_v1()` em `app/claims/export.py` que serializa ClaimGraph com prior + evidence_trail[] para cada claim | `app/claims/export.py` | G22 | Export gera JSON válido contra schema; 100% claims têm prior e evidence_trail[] | Teste unitário passa |
| S40-BE-012 | backend | Implementar endpoint GET `/api/claims/export?domain={domain}&format=v1` com paginação | `app/api/claims_routes.py` | G22 | Endpoint retorna export paginado; headers de paginação corretos | Teste API passa |
| S40-BE-013 | backend | Implementar `ingest_claimgraph_export()` em `app/truth/ingest.py` que consome export v1 e cria/atualiza claims no Truth-DB | `app/truth/ingest.py` | G22 | Ingest funciona sem adaptador manual; claims válidas persistidas | Teste E2E passa |
| S40-BE-014 | backend | Implementar sinais NO-GO em `app/claims/signals.py`: tipos INCONSISTENCY, SUSPICION, ABUSE com critérios explícitos | `app/claims/signals.py` | G22 | Sinais têm threshold e critério documentado | Teste unitário passa |
| S40-BE-015 | backend | Integrar NO-GO signals em `app/guardian/flow.py`: sinal ativo bloqueia transição (estado BLOCKED_NO_GO) | `app/guardian/flow.py` | G22 | Transição com sinal NO-GO ativo fica bloqueada; DecisionBlock registra signal_ref | Teste E2E passa |
| S40-BE-016 | backend | Implementar endpoint GET `/api/claims/{claim_id}/signals` que retorna sinais ativos | `app/api/claims_routes.py` | G22 | Endpoint funciona; sinais retornados com tipo e severity | Teste API passa |
| S40-BE-017 | backend | Implementar detecção automática de INCONSISTENCY via contradições no ClaimGraph | `app/claims/graph_service.py` | G22 | Contradições detectadas geram sinal INCONSISTENCY automaticamente | Teste unitário passa |
| S40-CI-003 | ci | Criar script `bin/s40_g22_claimgraph.sh` que valida export + ingest + NO-GO signals | `bin/s40_g22_claimgraph.sh` | G22 | Exit 0 com export/ingest sem cola manual; NO-GO bloqueia | `out/scorecards/S40_G22_claimgraph.json` |

---

## 5. Wave 3 — P1 Hardening (Social/Oficiais + SLA)

**Objetivo:** Ingestão social e oficiais estável no piloto; SLA P1 ≤1min evidenciado.

**Critério de saída:** Fontes do piloto operacionais; latência p95 ≤1min com evidência.

| ID | Área | Descrição | Arquivos/Módulos | Gates | DONE | Evidências |
|----|------|-----------|------------------|-------|------|------------|
| S40-BE-018 | backend | Expandir `social_provider_client.py` para domínios piloto (saude, politica) com rate limiting e retry | `app/ingestion/social_provider_client.py` | G21 | Provider funciona para domínios piloto; erros tratados | Teste integração passa |
| S40-BE-019 | backend | Expandir fontes oficiais `gov_br.py` e `dados_gov.py` para domínios piloto com health check | `app/ingestion/providers/gov_br.py`, `app/ingestion/providers/dados_gov.py` | G21 | Fontes retornam dados; health check operacional | Teste integração passa |
| S40-BE-020 | backend | Implementar métricas de latência P1 em `app/ingestion/observability.py`: `p1_latency_collected_to_ready` | `app/ingestion/observability.py` | G21 | Métrica exposta; histograma com buckets adequados | Prometheus query funciona |
| S40-BE-021 | backend | Implementar alerta para SLA P1 violado (>1min) em `observability/alerts/` | `observability/alerts/s40_p1_sla.yaml` | G21 | Alerta dispara quando p95 > 60s | Teste de alerta passa |
| S40-BE-022 | backend | Criar job de benchmark P1 que mede latência em janela definida e gera scorecard | `scripts/benchmarks/p1_latency_benchmark.py` | G21 | Script gera `out/scorecards/S40_G21_p1_latency.json` com p50, p95, p99 | Scorecard gerado |
| S40-CI-004 | ci | Criar script `bin/s40_g21_p1_hardening.sh` que roda health checks e valida SLA | `bin/s40_g21_p1_hardening.sh` | G21 | Exit 0 com fontes healthy e SLA dentro | `out/scorecards/S40_G21_p1.json` |

---

## 6. Wave 4 — P4 Exposure (Truth Twin + Decision Inspector + Provenance)

**Objetivo:** Expor Truth Twin e Decision Inspector com provenance obrigatória; latência P4 ≤100ms.

**Critério de saída:** Endpoints funcionam; provenance completa; latência dentro do SLA.

| ID | Área | Descrição | Arquivos/Módulos | Gates | DONE | Evidências |
|----|------|-----------|------------------|-------|------|------------|
| S40-BE-023 | backend | Implementar endpoint GET `/api/truth/{claim_id}/twin` que retorna estado atual + timeline de DecisionBlocks + provenance | `app/api/truth_routes.py` | G24 | Endpoint retorna TruthTwinResponse válido contra schema; provenance não vazia | Teste API passa |
| S40-BE-024 | backend | Implementar endpoint GET `/api/truth/decision/{decision_id}/inspect` que retorna detalhes completos do DecisionBlock (guias, pilares, policy, E40.5, evidence_refs, experience_ref) | `app/api/truth_routes.py` | G24 | Endpoint retorna InspectResponse com todos os campos de provenance | Teste API passa |
| S40-BE-025 | backend | Implementar middleware de provenance em `app/api/middleware/provenance.py`: toda resposta de verdade inclui header `X-Provenance-Valid: true/false` | `app/api/middleware/provenance.py` | G24 | Middleware ativo; responses sem provenance marcadas como invalid | Teste middleware passa |
| S40-BE-026 | backend | Implementar DTO `TruthTwinResponse` e `DecisionInspectResponse` em `app/api/truth_schemas.py` | `app/api/truth_schemas.py` | G24 | DTOs validam contra schemas JSON | Teste unitário passa |
| S40-BE-027 | backend | Implementar métricas de latência P4 em `app/api/metrics.py`: `p4_endpoint_latency_ms` | `app/api/metrics.py` | G24 | Métrica exposta; histograma correto | Prometheus query funciona |
| S40-BE-028 | backend | Criar job de benchmark P4 que mede latência em janela definida | `scripts/benchmarks/p4_latency_benchmark.py` | G24 | Script gera `out/scorecards/S40_G24_p4_latency.json` com p50, p95, p99 | Scorecard gerado |
| S40-FE-001 | frontend | Criar página Truth Twin em `frontend/inspectah-ui/src/modules/spovest/pages/admin/SpTruthTwinPage.tsx` | `frontend/inspectah-ui/src/modules/spovest/pages/admin/SpTruthTwinPage.tsx` | G24 | Página carrega; busca claim; exibe estado + timeline | Teste Playwright passa |
| S40-FE-002 | frontend | Criar componente `DecisionTimeline` que exibe lista de DecisionBlocks com expand para detalhes | `frontend/inspectah-ui/src/modules/truth/components/DecisionTimeline.tsx` | G24 | Componente renderiza timeline; click expande detalhes | Teste componente passa |
| S40-FE-003 | frontend | Criar componente `ProvenancePanel` que exibe guias[], pilares[], policy, E40.5 de um DecisionBlock | `frontend/inspectah-ui/src/modules/truth/components/ProvenancePanel.tsx` | G24 | Componente renderiza provenance; links clicáveis para refs | Teste componente passa |
| S40-FE-004 | frontend | Criar componente `DecisionInspector` (modal ou página) com drill-down completo | `frontend/inspectah-ui/src/modules/truth/components/DecisionInspector.tsx` | G24 | Inspector mostra todos os campos; ≤3 cliques para rastreabilidade | Teste E2E passa |
| S40-FE-005 | frontend | Criar badges de status: `<ValidBadge />`, `<InvalidBadge />`, `<BlockedNoGoBadge />`, `<DegradedBadge />` | `frontend/inspectah-ui/src/modules/truth/components/StatusBadges.tsx` | G24 | Badges renderizam corretamente com cores distintas | Teste visual passa |
| S40-FE-006 | frontend | Integrar rota `/admin/truth-twin` no router e menu | `frontend/inspectah-ui/src/routes.tsx` | G24 | Rota acessível; menu linkado | Navegação funciona |
| S40-FE-007 | frontend | Criar types TypeScript para Truth Twin em `frontend/inspectah-ui/src/modules/truth/types.ts` (TruthTwinResponse, DecisionBlock, Provenance, etc.) | `frontend/inspectah-ui/src/modules/truth/types.ts` | G24 | Types correspondem aos schemas JSON; export funciona | Compilação TypeScript passa |
| S40-FE-008 | frontend | Criar hook `useTruthTwin(claimId)` para fetch de dados com loading/error states | `frontend/inspectah-ui/src/modules/truth/hooks/useTruthTwin.ts` | G24 | Hook retorna data/loading/error; cache funciona | Teste hook passa |
| S40-CI-005 | ci | Criar script `bin/s40_g24_p4_exposure.sh` que valida endpoints, provenance e latência | `bin/s40_g24_p4_exposure.sh` | G24 | Exit 0 com endpoints OK, provenance válida, latência ≤100ms | `out/scorecards/S40_G24_p4.json` |

---

## 7. Wave 5 — Quality & ORR (Testes, Observabilidade, Bundle)

**Objetivo:** Garantir qualidade, observabilidade e bundle final para GO/NO-GO 7/7.

**Critério de saída:** Cobertura ≥97%; todos os gates PASS; bundle completo.

| ID | Área | Descrição | Arquivos/Módulos | Gates | DONE | Evidências |
|----|------|-----------|------------------|-------|------|------------|
| S40-TST-001 | testes | Criar testes unitários para validadores (DecisionBlock, Claim) | `tests/truth/test_validators.py` | G20 | Testes passam; cobrem casos válido/inválido | Coverage report |
| S40-TST-002 | testes | Criar testes E2E para E40.5 enforcement (PASS e FAIL) | `tests/truth/test_e40_5_enforcement.py` | G23 | Teste PASS cria DecisionBlock; teste FAIL bloqueia transição | Coverage report |
| S40-TST-003 | testes | Criar testes E2E para NO-GO signals (bloqueio real) | `tests/claims/test_nogo_signals.py` | G22 | Sinal NO-GO bloqueia transição; DecisionBlock registra | Coverage report |
| S40-TST-004 | testes | Criar testes de contrato para export ClaimGraph → ingest P3 | `tests/claims/test_claimgraph_export_contract.py` | G22 | Export gera JSON válido; ingest consome sem erro | Coverage report |
| S40-TST-005 | testes | Criar testes API para Truth Twin e Decision Inspector | `tests/api/test_truth_twin_routes.py` | G24 | Endpoints retornam responses válidas; provenance presente | Coverage report |
| S40-TST-006 | testes | Criar testes de latência P4 (benchmark) | `tests/api/test_p4_latency.py` | G24 | Latência p95 ≤100ms no ambiente de teste | Benchmark report |
| S40-TST-007 | testes | Criar testes frontend (Playwright) para Truth Twin page | `frontend/inspectah-ui/playwright/truth-twin.pw.ts` | G24 | Page carrega; timeline renderiza; inspector abre | Playwright report |
| S40-TST-008 | testes | Criar golden tests para casos canônicos A/B/C | `tests/truth/test_canonical_cases.py` | G23, G24 | Casos A (PASS), B (NO-GO), C (contestação) executam e geram evidência | Golden files em `out/evidence/` |
| S40-OBS-001 | observabilidade | Criar dashboard Grafana para S40 (P1 latency, P4 latency, DecisionBlocks válidos, NO-GO count) | `observability/dashboards/s40_truthdb.json` | G21, G24 | Dashboard importável; painéis funcionam | Screenshot |
| S40-OBS-002 | observabilidade | Criar alertas para invariantes S40 (DecisionBlock inválido, E40.5 bypass, SLA violado) | `observability/alerts/s40_invariants.yaml` | G20, G23 | Alertas configurados; disparam em violação | Teste de alerta |
| S40-CI-006 | ci | Criar script `bin/s40_all_gates.sh` que roda G20-G24 em sequência | `bin/s40_all_gates.sh` | G20-G24 | Exit 0 se todos passam; exit 1 se qualquer falha | Log completo |
| S40-CI-007 | ci | Criar script `bin/s40_orr.sh` que gera bundle final com scorecards e evidências | `bin/s40_orr.sh` | G20-G24 | Bundle `out/bundles/S40_bundle.zip` gerado com todos os artefatos | Bundle existe |
| S40-DOC-001 | docs | Atualizar `S40_ORR_Checklist.md` com paths reais de evidências | `docs/Agents/Planejamento/Programa 2/Sprint 40/S40_ORR_Checklist.md` | G24 | Checklist preenchível com paths concretos | Documento atualizado |
| S40-DOC-002 | docs | Preencher `S40_Handoff.md` (template → valores reais ao final) | `docs/Agents/Planejamento/Programa 2/Sprint 40/S40_Handoff.md` | G24 | Handoff completo para S41 | Documento preenchido |

---

## 8. Matriz de Cobertura (Gates ↔ Tasks)

| Gate | Tasks Relacionadas | Estados-Alvo |
|------|--------------------|--------------|
| G20 | S40-INF-001..003, S40-DB-001..002, S40-BE-001..002, S40-CI-001, S40-TST-001 | SA-01, SA-07 |
| G21 | S40-BE-018..022, S40-CI-004 | SA-06 |
| G22 | S40-BE-011..017, S40-CI-003, S40-TST-003..004 | SA-02, SA-03 |
| G23 | S40-BE-003..010, S40-CI-002, S40-TST-002, S40-TST-008 | SA-01, SA-04 |
| G24 | S40-BE-023..028, S40-FE-001..006, S40-CI-005, S40-TST-005..007, S40-OBS-001..002 | SA-05, SA-06, SA-07 |

---

## 9. Resumo de Tasks por Área

| Área | Quantidade | IDs |
|------|------------|-----|
| infra | 3 | S40-INF-001..003 |
| dados | 3 | S40-DB-001..003 |
| backend | 30 | S40-BE-001..030 |
| frontend | 8 | S40-FE-001..008 |
| testes | 8 | S40-TST-001..008 |
| observabilidade | 2 | S40-OBS-001..002 |
| ci | 7 | S40-CI-001..007 |
| docs | 2 | S40-DOC-001..002 |
| **TOTAL** | **63** | — |

---

## 10. Dependências Críticas

```
W0 (Groundwork)
├── W1 (P3 Core) ─────────┐
├── W2 (P2 Export)────────┼── W4 (P4 Exposure)
└── W3 (P1 Hardening)─────┘         │
                                    └── W5 (Quality & ORR)
```

**Bloqueadores entre waves:**
- W1 requer schemas de W0 para validação
- W4 requer DecisionBlocks de W1 e export de W2
- W5 requer todas as waves anteriores

---

## 11. Ordem de Execução Interna por Wave

### W0 — Ordem recomendada
1. S40-INF-001..003 (schemas primeiro)
2. S40-DB-001..003 (migration com schemas prontos)
3. S40-BE-001..002 (validadores usando schemas)
4. S40-CI-001 (valida tudo)

### W1 — Ordem recomendada
1. S40-BE-003 (modelo DecisionBlock estendido)
2. S40-BE-004 (build_references)
3. S40-BE-007..008 (Experience model e repository)
4. S40-BE-005 (E40.5 enforcement) ← depende de 003 e 004
5. S40-BE-029 (modo degradado) ← depende de 005
6. S40-BE-006 (record_decision_block) ← depende de 003 e 004
7. S40-BE-009 (integrar experience_ref) ← depende de 006, 007, 008
8. S40-BE-010 (endpoint experiences)
9. S40-BE-030 (seed experiences) ← depende de 010
10. S40-CI-002 (valida tudo)

### W2 — Ordem recomendada
1. S40-BE-014 (sinais NO-GO com critérios)
2. S40-BE-017 (detecção INCONSISTENCY)
3. S40-BE-011 (export_claimgraph_v1)
4. S40-BE-012 (endpoint export)
5. S40-BE-013 (ingest_claimgraph_export)
6. S40-BE-015 (integrar NO-GO em FlowContext)
7. S40-BE-016 (endpoint signals)
8. S40-CI-003 (valida tudo)

### W3 — Ordem recomendada
1. S40-BE-018 (social provider)
2. S40-BE-019 (fontes oficiais)
3. S40-BE-020 (métricas latência)
4. S40-BE-021 (alerta SLA)
5. S40-BE-022 (benchmark)
6. S40-CI-004 (valida tudo)

### W4 — Ordem recomendada
1. S40-BE-026 (DTOs)
2. S40-BE-025 (middleware provenance)
3. S40-BE-023 (endpoint twin)
4. S40-BE-024 (endpoint inspect)
5. S40-BE-027 (métricas P4)
6. S40-BE-028 (benchmark P4)
7. S40-FE-007 (TypeScript types) ← paralelo com backend
8. S40-FE-008 (hook useTruthTwin)
9. S40-FE-005 (StatusBadges)
10. S40-FE-002 (DecisionTimeline)
11. S40-FE-003 (ProvenancePanel)
12. S40-FE-004 (DecisionInspector)
13. S40-FE-001 (página Truth Twin)
14. S40-FE-006 (rota)
15. S40-CI-005 (valida tudo)

### W5 — Ordem recomendada
1. S40-TST-001..008 (todos os testes)
2. S40-OBS-001..002 (observabilidade)
3. S40-CI-006 (all_gates)
4. S40-DOC-001..002 (docs)
5. S40-CI-007 (bundle final)

---

## 12. Checklist de Pré-Requisitos

Antes de iniciar a S40, verificar:

- [ ] S39 = GO (ou equivalente)
- [ ] `.venv` configurado com dependências
- [ ] PostgreSQL rodando com extensão pgvector (para embeddings)
- [ ] Prometheus/Grafana acessíveis (para métricas)
- [ ] Acesso às fontes oficiais (gov.br, dados.gov.br)
- [ ] sentence-transformers ou similar instalado (para embeddings)

---

## 13. Notas de Implementação (para o ACE)

### Embedding para Experiências
- Usar `sentence-transformers/all-MiniLM-L6-v2` (384 dims) ou similar
- Armazenar em PostgreSQL com `pgvector` extension
- Índice: `CREATE INDEX ON experiences USING ivfflat (embedding vector_cosine_ops)`

### Build References
```python
def build_references(claim, policy_result, e40_5_result):
    return {
        "guias": [{"guia": "MQV", "documento": "01_Guia_3X", "tabela": "G2", "secao": "Cap.2", "dominio": claim.domain, "gate": claim.gate}],
        "pilares": [{"pilar": "P5", "documento": "P5-4", "secao": "§3.2"}],
        "policy": {"version": policy_result.version, "rules_applied": policy_result.rules},
        "e40_5": {"status": e40_5_result.status, "invariants_checked": e40_5_result.invariants, "violations": e40_5_result.violations}
    }
```

### NO-GO Signal Thresholds (defaults)
- `INCONSISTENCY`: contradictions ≥ 2 no ClaimGraph
- `SUSPICION`: anomaly_score > 0.8
- `ABUSE`: spam_score > 0.9 OR report_count ≥ 3

### TruthState Mapping
```python
# Roadmap → Repo
"uncertain" → TruthState.UNKNOWN
"claimed"   → TruthState.CLAIMED
"review"    → TruthState.UNDER_REVIEW
"provisional" → TruthState.PROVISIONAL
"true"      → TruthState.ESTABLISHED_FACT
"disputed"  → TruthState.UNDER_DISPUTE
"retracted" → TruthState.RETRACTED
```

### Latência P4 Optimization
- Cache: Redis com TTL 60s para Truth Twin responses
- Índices: decision_blocks(claim_id, created_at DESC)
- Query limit: máx 100 DecisionBlocks por timeline

---

## 14. Riscos e Mitigações

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| E40.5 timeout | Alto | Modo degradado implementado (S40-BE-029) |
| pgvector não instalado | Alto | Checklist de pré-requisitos; fallback para cosine similarity manual |
| SLA P4 não atingido | Médio | Cache Redis; índices otimizados; benchmark antecipado |
| Export ClaimGraph muito grande | Médio | Paginação obrigatória; stream para grafos > 10k claims |
| Experiências sem embedding | Baixo | Fallback para text similarity (TF-IDF) |

---

## 15. Definição de DONE da Sprint

A Sprint 40 está **DONE** quando:

1. [ ] Todos os gates (G20-G24) = PASS com evidências em `out/scorecards/`
2. [ ] Casos canônicos A/B/C executados e rastreáveis
3. [ ] SLAs no recorte piloto atingidos:
   - [ ] P1 ≤ 1 min (p95)
   - [ ] P4 ≤ 100 ms (p95)
   - [ ] Reversão ≤ 4%
   - [ ] Abuso ≤ 1%
4. [ ] GO/NO-GO 7/7 comprovado em `S40_ORR_Checklist.md`
5. [ ] Cobertura de testes ≥ 97%
6. [ ] Bundle `out/bundles/S40_bundle.zip` gerado
7. [ ] Handoff `S40_Handoff.md` preenchido

---

## 16. Mapeamento GO/NO-GO 7/7 (obrigatório)

| # | Critério GO/NO-GO | Tasks que Evidenciam | Evidência |
|---|-------------------|---------------------|-----------|
| 1 | Checklist 100% completo | S40-CI-006, S40-CI-007 | `out/evidence/S40_all_gates.log` |
| 2 | Quadros/Guias em todos os DecisionBlocks | S40-BE-001, S40-BE-004 | Teste de validação rejeita sem guias[] |
| 3 | Testes passando (regressão + novos) | S40-TST-001..008 | `out/evidence/S40_coverage.html` |
| 4 | SLAs no recorte piloto | S40-BE-020..022, S40-BE-027..028 | Scorecards P1/P4 latency |
| 5 | Documentação atualizada | S40-DOC-001, S40-DOC-002 | S40_ORR_Checklist.md, S40_Handoff.md |
| 6 | E40.5 operando em transições críticas | S40-BE-005, S40-BE-029, S40-TST-002 | `out/evidence/S40_e40_5_tests.log` |
| 7 | Pré-condições éticas (Guia 5/MAC) | S40-BE-004 (references.pilares[]) | DecisionBlock exige pilares[] |

---

## 17. Mapeamento Invariantes → Tasks

| Invariante | Descrição | Task | Teste |
|------------|-----------|------|-------|
| INV-DB-01 | DecisionBlock sem guias[] é inválido | S40-BE-001 | `tests/truth/test_validators.py` |
| INV-DB-02 | DecisionBlock sem e40_5 é inválido | S40-BE-001 | `tests/truth/test_validators.py` |
| INV-DB-03 | DecisionBlock sem state_transition é inválido | S40-BE-001 | `tests/truth/test_validators.py` |
| INV-DB-04 | DecisionBlock sem pilares[] é inválido | S40-BE-001 | `tests/truth/test_validators.py` |
| INV-E40.5-01 | Toda transição crítica passa por E40.5 | S40-BE-005, S40-BE-029 | `tests/guardian/test_flow_e40_5.py` |
| INV-CLAIM-01 | Claim sem prior/evidence_trail[] é inválida | S40-BE-002 | `tests/claims/test_validators.py` |
| INV-SLA-01 | SLAs não violados | S40-BE-020..022, S40-BE-027..028 | Benchmarks geram scorecards |

---

## 18. Formato de Evidências com Carimbo

Todas as evidências em `out/evidence/` e `out/scorecards/` devem conter:

```json
{
  "metadata": {
    "sprint": "S40",
    "gate": "G20",
    "timestamp": "2024-12-16T12:00:00Z",
    "commit": "abc1234",
    "policy_version": "v3.2.1",
    "domain": "pilot_saude"
  },
  "result": "PASS|FAIL",
  "details": { ... }
}
```

Scripts de gate DEVEM incluir este carimbo. Evidência sem carimbo é inválida.

---

*Documento gerado pelo Sprint Planner Técnico — S40 v1.4 (REFINE-4: GO/NO-GO explícito + invariantes + carimbo)*
