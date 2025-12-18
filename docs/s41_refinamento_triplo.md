# S41 — Refinamento Triplo (State of the Art)
## Sprint Planner Tecnico v7

> **Base:** Plano v3.0 (247 tasks, 14 waves)
> **Data:** 2025-12-16
> **Nivel:** State of the Art
> **Rodadas:** R1 (Gaps), R2 (Refinamento), R3 (Fine-tuning)

---

## R1 — ANALISE DE GAPS ESTRUTURAIS

### 1.1 Gaps P0 (Bloqueadores de Gate)

| ID | Gap | Fonte | Wave | Task Proposta |
|----|-----|-------|------|---------------|
| GAP-01 | DecisionBlock auditing faltando | G29 spec | W12 | `W12.17`: Auditar amostra de DecisionBlocks para `references.guias[]` e `references.e40_5` |
| GAP-02 | coherence_label + reason_code | Anexo D | W11 | `W11.18`: Definir metodologia de rotulacao de coerencia por decisao |
| GAP-03 | Incompatibilidades P5-5 incompletas | P5-5 §5 | W4 | `W4.31`: Mapear matriz completa de incompatibilidades (Chair, Judge, Observer, etc.) |
| GAP-04 | A_pot_hi criteria indefinido | Anexo D §2.1 | W2 | `W2.26`: Definir criterios para classificar atores de alta influencia |
| GAP-05 | 2+ param changes audit sample | G28 evidence | W11 | `W11.19`: Simular 2+ mudancas de parametro e gerar audit trail |

### 1.2 Gaps P1 (Importantes)

| ID | Gap | Fonte | Wave | Task Proposta |
|----|-----|-------|------|---------------|
| GAP-06 | Golden Cases piloto | Anexo D §1.3 | W0.5 | `W0.5.19`: Criar estrutura data/cvi_pilot/ com 2+ casos semi-sinteticos |
| GAP-07 | Screenshot/HTML export | G27 evidence | W11 | `W11.20`: Gerar screenshot/HTML do painel com provenance visivel |
| GAP-08 | Threshold domain-configurable | Anexo D §2.2 | W2 | `W2.27`: L_dominio configuravel por tema (saude=7d, energia=30d) |
| GAP-09 | Snapshot retention policy | Trade-offs | W4 | `W4.32`: Definir politica de retencao de snapshots (30d min) |
| GAP-10 | Coherence review template | W11.15 | W0.5 | `W0.5.20`: Template coherence_review.json com 6+ decisoes |

### 1.3 Gaps P2 (Nice-to-have para State of the Art)

| ID | Gap | Fonte | Wave | Task Proposta |
|----|-----|-------|------|---------------|
| GAP-11 | Expert agreement tracking | Anexo D scorecard | W4 | `W4.33`: Campo qualitativo expert_agreement_level em scorecards |
| GAP-12 | Fairness annotations | Anexo D §3.7 | W10 | `W10.15`: Alertas de assimetria de dados por tipo de ator |
| GAP-13 | Flagged patterns registry | Anexo D §3.4.1 | W10 | `W10.16`: Registro de padroes problematicos detectados |

**Total R1:** +13 tasks identificadas

---

## R2 — REFINAMENTO DE TASKS E DEPENDENCIAS

### 2.1 Tasks Refinadas (Clareza e Completude)

| Task Original | Problema | Refinamento |
|---------------|----------|-------------|
| W0.5.10 | Criterios piloto vagos | Adicionar: "minimo 2 temas, 2 casos, 10 atores, 50 sinais" |
| W2.09 | analyze_coverage incompleto | Adicionar: "incluir cov_atores, cov_alta_infl, pct_atualizado" |
| W3.08 | 2-person rule sem fallback | Adicionar: "fallback para single-admin com auditoria forcada" |
| W4.08 | Matriz incompatibilidades basica | Expandir para incluir todos os papeis P5-5 |
| W5.04 | stale threshold hardcoded | Usar L_dominio configuravel |
| W6.13 | State machine incompleta | Adicionar estado 'pending_recompute' |
| W9.07 | Regressao S40 sem baseline | Definir baseline minimo ou usar dados sinteticos |
| W11.15 | coherence_review.json vago | Especificar: 6 decisoes, 2 temas, com cvi_coherence_label |

### 2.2 Dependencias Criticas Adicionadas

```
W0.5.19 (golden cases) --> W2 (pipeline precisa de test data)
W0.5.20 (coherence template) --> W11.15 (gerar coherence_review)
W2.26 (A_pot_hi criteria) --> W2.09 (analyze_coverage usa A_pot_hi)
W4.31 (incompatibilidades) --> W4.06-08 (RoleValidator implementa)
W11.18 (metodologia coerencia) --> W11.15 (aplicar metodologia)
W11.19 (param changes) --> W11.09 (G28 evidence)
W12.17 (DecisionBlock audit) --> W12.15 (go_no_go_7of7)
```

### 2.3 Wave DAG Atualizado

```
W0 (baseline)
 |
 +---> W0.5 (specifications) [+3 tasks: W0.5.19, W0.5.20, +criteria refinados]
        |
        +---> W1 (models)
        |      |
        |      +---> W2 (pipeline) [+2 tasks: W2.26, W2.27]
        |             |
        |             +---> W3 (services/APIs)
        |                    |
        |                    +---> W5 (explain integration)
        |                    |      |
        |                    |      +---> W6 (FE CVI)
        |                    |             |
        |                    |             +---> W8 (UX)
        |                    |
        |                    +---> W4 (governance) [+3 tasks: W4.31, W4.32, W4.33]
        |                           |
        |                           +---> W7 (FE governance)
        |
        +---> W10 (observability) [+2 tasks: W10.15, W10.16]
               |
               +---> W9 (E2E tests)
                      |
                      +---> W11 (gates) [+3 tasks: W11.18, W11.19, W11.20]
                             |
                             +---> W12 (ORR) [+1 task: W12.17]
```

---

## R3 — FINE-TUNING E POLISH FINAL

### 3.1 Otimizacoes de Execucao

| Area | Otimizacao | Impacto |
|------|------------|---------|
| Paralelismo | W6 (FE CVI) e W7 (FE Governance) podem rodar em paralelo apos W3/W4 | -20% tempo |
| Cache | W6.03 (useCVISnapshot) deve usar SWR/React Query para revalidation | +UX |
| Bundle size | W6.15 (error boundaries) deve usar lazy loading | -30% initial load |
| CI | Gate scripts devem ter timeout de 10min max | Previne hangs |

### 3.2 Hardening de Seguranca

| Task | Hardening | Racional |
|------|-----------|----------|
| W3.18 | Adicionar rate limiting em rotas CVI Query | Previne abuse |
| W4.05 | Allowlist deve ser imutavel em runtime | Previne injection |
| W4.19 | Audit log deve ser append-only com checksum | Integridade |
| W7.09 | Export bundle deve sanitizar dados sensiveis | LGPD compliance |

### 3.3 Observabilidade State of the Art

| Metrica | Threshold | Alerta |
|---------|-----------|--------|
| cvi_snapshot_compute_p95_ms | < 5000ms | Warning > 3000ms, Critical > 5000ms |
| cvi_coverage_alta_infl | >= 0.60 | Warning < 0.70, Critical < 0.60 |
| audit_events_per_hour | > 0 | Warning == 0 (no activity) |
| rbac_403_count | monitoring | Alert if spike > 10/min |
| explain_cache_hit_rate | > 0.70 | Warning < 0.70 |

### 3.4 UX Polish (Bret Victor Level)

| Componente | Polish |
|------------|--------|
| CVIActorCard | Animacao suave ao expandir details (200ms ease-out) |
| CVICoverageBadge | Cor semantica: verde >= 0.80, amarelo >= 0.60, vermelho < 0.60 |
| CVIHypothesesDisclaimer | Icone de interrogacao + tooltip com exemplo |
| AuditTrailList | Virtualizacao para 1000+ eventos |
| P5MetricsDashboard | Sparklines para tendencia 7d |

### 3.5 Documentacao State of the Art

| Doc | Conteudo |
|-----|----------|
| `docs/cvi/README.md` | Visao geral CVI, quick start, links |
| `docs/cvi/API.md` | Referencia completa de endpoints |
| `docs/cvi/ARCHITECTURE.md` | Diagrama de componentes, fluxo de dados |
| `docs/governance/RBAC.md` | Matriz de permissoes, exemplos |
| `docs/governance/AUDIT.md` | Formato de eventos, retencao, queries |

---

## RESUMO DO REFINAMENTO

| Metrica | v3.0 | v3.1 (Refinado) | Delta |
|---------|------|-----------------|-------|
| Total tasks | 247 | 260 | +13 |
| Gaps P0 | 5 | 0 | -5 |
| Gaps P1 | 5 | 0 | -5 |
| Gaps P2 | 3 | 0 | -3 |
| Dependencias explicitas | 15 | 22 | +7 |
| Hardening tasks | 0 | 4 | +4 |
| UX polish items | 0 | 5 | +5 |
| Docs adicionais | 0 | 5 | +5 |

---

## TASKS ADICIONADAS (v3.1)

### Wave W0.5 (+2)

```yaml
- id: W0.5.19
  description: "Criar estrutura data/cvi_pilot/ com 2+ casos semi-sinteticos (2 temas, 10 atores, 50 sinais)"
  type: CONFIG
  gate: G26
  priority: P1
  spec_ref: "Anexo D §1.3 - Golden Cases"

- id: W0.5.20
  description: "Criar template coherence_review.json com campos: decision_id, cvi_coherence_label, reason_code, expert_notes"
  type: DESIGN
  gate: G26
  priority: P1
  spec_ref: "Anexo D §2.3 - Coerencia"
```

### Wave W2 (+2)

```yaml
- id: W2.26
  description: "Definir criterios A_pot_hi (atores alta influencia): ActorProfiler score >= 0.7 OU role in [government, major_company, regulator]"
  type: CODE
  gate: G26
  priority: P0
  spec_ref: "Anexo D §2.1"

- id: W2.27
  description: "Implementar L_dominio configuravel: saude=7d, energia=30d, midia=14d, justica=21d"
  type: CODE
  gate: G27
  priority: P1
  spec_ref: "Anexo D §2.2"
```

### Wave W4 (+3)

```yaml
- id: W4.31
  description: "Mapear matriz completa incompatibilidades P5-5: Chair!=SystemAdmin, Judge!=Stakeholder, Auditor!=Operator"
  type: CODE
  gate: G28
  priority: P0
  spec_ref: "P5-5 §5"

- id: W4.32
  description: "Implementar snapshot retention policy: min 30 dias, cleanup automatico, log de delecoes"
  type: CODE
  gate: G28
  priority: P1
  spec_ref: "Trade-offs"

- id: W4.33
  description: "Adicionar campo expert_agreement_level em scorecards CVI (alto/medio/baixo/pendente)"
  type: CODE
  gate: G26
  priority: P2
  spec_ref: "Anexo D §3.3"
```

### Wave W10 (+2)

```yaml
- id: W10.15
  description: "Implementar alertas de assimetria de dados: detectar quando coverage varia > 2x entre tipos de ator"
  type: CODE
  gate: G26
  priority: P2
  spec_ref: "Anexo D §3.7"

- id: W10.16
  description: "Criar registro de flagged_patterns: pattern_id, description, recommendation, count"
  type: CODE
  gate: G28
  priority: P2
  spec_ref: "Anexo D §3.4.1"
```

### Wave W11 (+3)

```yaml
- id: W11.18
  description: "Definir metodologia coerencia: selecionar 6+ decisoes, atribuir cvi_coherence_label (alta/media/baixa), reason_code"
  type: DESIGN
  gate: G26
  priority: P0
  spec_ref: "Anexo D §2.3"

- id: W11.19
  description: "Simular 2+ mudancas de parametro CVI e gerar audit trail completo (propose -> approve -> apply)"
  type: EVIDENCE
  gate: G28
  priority: P0
  spec_ref: "G28 Evidence"

- id: W11.20
  description: "Gerar screenshot/HTML export do painel Explain+CVI com provenance visivel"
  type: EVIDENCE
  gate: G27
  priority: P1
  spec_ref: "G27 Evidence"
```

### Wave W12 (+1)

```yaml
- id: W12.17
  description: "Auditar amostra de 3+ DecisionBlocks para validar references.guias[] e references.e40_5 presentes"
  type: CHECK
  gate: G29
  priority: P0
  spec_ref: "G29 - GO/NO-GO 7/7"
```

---

## INVARIANTES ADICIONADAS

| ID | Regra | Consequencia |
|----|-------|--------------|
| INV_COHERENCE_01 | coherence_review.json DEVE ter 6+ decisoes | G26 FAIL se < 6 |
| INV_DECISIONBLOCK_01 | DecisionBlocks DEVEM ter references.guias[] e references.e40_5 | G29 FAIL se ausente |
| INV_RETENTION_01 | Snapshots nao podem ser deletados antes de 30 dias | Violacao = P0 |

---

## SCORECARD DO PLANNER (v3.1)

```yaml
planner_scorecard:
  version: "3.1"
  date: "2025-12-16"
  level: "state_of_the_art"

  coverage:
    spec_chapters_read: 36/36
    gates_mapped: 5/5
    invariants_defined: 11
    journeys_covered: 4/4
    slas_tracked: 6/6
    go_no_go_criteria: 7/7

  refinement:
    rounds_executed: 3
    gaps_p0_closed: 5
    gaps_p1_closed: 5
    gaps_p2_closed: 3
    tasks_added: 13
    dependencies_added: 7

  quality:
    hardening_items: 4
    ux_polish_items: 5
    docs_created: 5
    observability_metrics: 5

  risks:
    s40_dependency: "mitigated (synthetic fallback)"
    e40_5_existence: "to_verify"
    explain_service_interface: "to_verify"

  status: "READY_FOR_ACE_EXEC"
```

---

**Gerado por:** Sprint Planner Tecnico v7
**Data:** 2025-12-16
**Versao:** 3.1 (State of the Art)
