# S41 — Plano Tecnico v4.0 (Ciclo 1/3)
## Sprint Planner Tecnico v7 — Cobertura 100%

> **Data:** 2025-12-16
> **Base:** v3.1 (260 tasks) + Matriz Rastreabilidade (246 reqs, 14 gaps)
> **Nivel:** State of the Art + Lapidacao Exaustiva Ciclo 1

---

# RESUMO EXECUTIVO

| Metrica | v3.1 | v4.0 C1 | Delta |
|---------|------|---------|-------|
| Requisitos mapeados | 232/246 | 246/246 | +14 |
| Cobertura | 94.3% | **100%** | +5.7% |
| Tasks totais | 260 | **289** | +29 |
| Waves | 14 | 14 | 0 |
| Invariantes | 11 | **14** | +3 |
| Gaps P0 | 9 | 0 | -9 |
| Gaps P1 | 5 | 0 | -5 |

---

# TASKS ADICIONADAS (v4.0 Ciclo 1)

## Wave W1 — CVI Core (+4 tasks)

```yaml
- id: W1.19
  description: "Implementar eventos IncentiveSignalAdded/Updated/Retracted"
  type: CODE
  gate: G26
  priority: P0
  spec_ref: "Anexo C §1.2 - REQ-DNA-C-01"
  done_criteria:
    - Evento publicado em cada mutacao de incentive_signal
    - Schema de evento documentado
    - Consumer de teste recebe eventos

- id: W1.20
  description: "Implementar FieldAssembler modo batch (rebuild)"
  type: CODE
  gate: G26
  priority: P0
  spec_ref: "Anexo C §1.4 - REQ-DNA-C-03"
  done_criteria:
    - Job batch recalcula campos para janela temporal
    - Compara com campos atuais e registra diff
    - Gera novos snapshots se necessario

- id: W1.21
  description: "Implementar cvi_incentive_signal schema completo"
  type: CODE
  gate: G26
  priority: P0
  spec_ref: "Anexo C §2.2 - REQ-DNA-C-05"
  fields:
    - signal_id, actor_id, theme_id, case_id
    - class: econ|pol|rep|inst|leg
    - source_type, source_ref, value_descriptor
    - timestamp, horizon_hint, quality_score, notes

- id: W1.22
  description: "Implementar cvi_actor_profile schema completo"
  type: CODE
  gate: G26
  priority: P0
  spec_ref: "Anexo C §2.3 - REQ-DNA-C-06"
  fields:
    - actor_id, actor_type, name, jurisdiction
    - influence_indicators (audience_reach, institutional_power, network_centrality_ref)
    - history_refs, tags, last_updated_ts
```

## Wave W3 — Services/APIs (+3 tasks)

```yaml
- id: W3.23
  description: "Implementar GetDecisionContextIncentives para MQV/MAC"
  type: CODE
  gate: G26
  priority: P0
  spec_ref: "Anexo C §4.5 - REQ-DNA-C-08"
  contract:
    input: "identificadores alegacao/caso/decisao"
    output: "snapshot campo, V_tk, I_atk, concentracao, model_version"

- id: W3.24
  description: "Implementar upsert_incentive_signal com governanca"
  type: CODE
  gate: G28
  priority: P0
  spec_ref: "Cap.3B3 §2 - REQ-C3B3-10"
  done_criteria:
    - Somente truth_admin pode criar/editar
    - Gera audit_event
    - Dispara IncentiveSignalAdded/Updated

- id: W3.25
  description: "Implementar cvi_unavailable_reason em DecisionExplanation"
  type: CODE
  gate: G27
  priority: P0
  spec_ref: "Cap.3B3 §3 - REQ-C3B3-12"
  done_criteria:
    - Se CVI indisponivel, flag explicito no response
    - Reason codes: no_data, error, timeout, unauthorized
```

## Wave W4 — Governance (+5 tasks)

```yaml
- id: W4.34
  description: "Criar catalogo completo de papeis P5-5"
  type: CODE
  gate: G28
  priority: P0
  spec_ref: "P5-5 §4 - REQ-DNA-P55-01"
  roles:
    - GovernanceActor
    - Judge
    - PanelMember
    - Chair
    - Observer
    - ExternalAuditor
    - StakeholderRepresentative
    - SystemAdmin/Operator

- id: W4.35
  description: "Definir poderes permitidos/proibidos por papel"
  type: CODE
  gate: G28
  priority: P0
  spec_ref: "P5-5 §4 - REQ-DNA-P55-02"
  done_criteria:
    - Cada papel tem lista de poderes permitidos
    - Cada papel tem lista de poderes proibidos
    - Matriz de conflitos de interesse

- id: W4.36
  description: "Implementar validacao de acumulo de poderes incompativeis"
  type: CODE
  gate: G28
  priority: P0
  spec_ref: "P5-5 §5 - REQ-DNA-P55-03"
  rules:
    - Chair != SystemAdmin
    - Judge != Stakeholder em mesmo caso
    - Auditor != Operator
    - Bloquear + audit_event se violacao

- id: W4.37
  description: "Implementar monitoramento de indicadores de concentracao"
  type: CODE
  gate: G28
  priority: P0
  spec_ref: "P5-5 §5 - REQ-DNA-P55-04"
  metrics:
    - Decisoes por papel/ator
    - HHI de concentracao
    - Incidencia de reversals por ator

- id: W4.38
  description: "Criar estrutura de scorecards anti-captura"
  type: CODE
  gate: G28
  priority: P1
  spec_ref: "P5-7 §5 - REQ-DNA-P57-04"
  scorecards:
    - Contestabilidade
    - Transparencia
    - Anti-captura
```

## Wave W6 — Frontend CVI (+4 tasks)

```yaml
- id: W6.21
  description: "Implementar maquina de estados completa CVIOverlay"
  type: CODE
  gate: G27
  priority: P0
  spec_ref: "Cap.8B2 §2 - REQ-C8B2-07"
  states:
    - idle
    - loading
    - ready
    - no_data
    - unauthorized
    - error
    - stale
    - pending_recompute

- id: W6.22
  description: "Implementar acao 'Solicitar annotation governada'"
  type: CODE
  gate: G27
  priority: P1
  spec_ref: "Cap.5B2 - REQ-C5B2-05"
  flow:
    - Botao visivel quando dados insuficientes
    - Modal com formulario de solicitacao
    - Envia para fila de triagem
    - Gera audit_event

- id: W6.23
  description: "Implementar CTA 'Sugerir proximos passos'"
  type: CODE
  gate: G27
  priority: P1
  spec_ref: "Cap.4B3 - REQ-C4B3-03"
  ctas:
    - "Coletar mais dados"
    - "Solicitar annotation especializada"
    - "Ver criterios de cobertura"

- id: W6.24
  description: "Garantir manifest acessivel em <= 3 interacoes"
  type: CODE
  gate: G27
  priority: P1
  spec_ref: "Cap.9B4 - REQ-C9B4-02"
  path: "CVIOverlay -> Provenance button -> Drawer com manifest"
```

## Wave W11 — Gates/QA (+8 tasks)

```yaml
- id: W11.21
  description: "Criar template coherence_review.json com 6+ decisoes"
  type: EVIDENCE
  gate: G26
  priority: P0
  spec_ref: "Cap.2B2 - REQ-C2B2-08"
  schema:
    decisions:
      - decision_id
      - cvi_coherence_label: Alta|Media|Baixa|DadosInsuficientes
      - reason_code: data_gap|model_gap|mixed|unknown
      - expert_notes

- id: W11.22
  description: "Implementar calculo cvi_coherence_label por decisao"
  type: CODE
  gate: G26
  priority: P0
  spec_ref: "Cap.2B2 - REQ-C2B2-09"
  done_criteria:
    - Label atribuido por revisao humana ou heuristica inicial
    - reason_code obrigatorio se label == Baixa
    - Armazenado em evidencia/scorecard

- id: W11.23
  description: "Implementar unverified_checks[] em modo degradado"
  type: CODE
  gate: G29
  priority: P1
  spec_ref: "Cap.4B2 - REQ-C4B2-08"
  done_criteria:
    - Se servico externo indisponivel, registrar em evidencia
    - Gate pode passar com justificativa explicita
    - Governanca deve aceitar risco

- id: W11.24
  description: "Criar estrutura scorecards por dominio (D1-D4)"
  type: DESIGN
  gate: G26
  priority: P1
  spec_ref: "Anexo D §3 - REQ-DNA-D-06"
  domains:
    - D1: Saude regulatoria (C5/C13)
    - D2: Energia/clima (C2/C7/C14)
    - D3: Midia/tech (C1/C10/C15)
    - D4: Administracao/justica (C6/C9/C12)

- id: W11.25
  description: "Validar formula cov_atores implementada"
  type: CHECK
  gate: G26
  priority: P0
  spec_ref: "Anexo D §2.1 - REQ-DNA-D-01"
  formula: "cov_atores = |A_CVI| / |A_pot|"

- id: W11.26
  description: "Validar formula cov_alta_infl implementada"
  type: CHECK
  gate: G26
  priority: P0
  spec_ref: "Anexo D §2.1 - REQ-DNA-D-02"
  formula: "cov_alta_infl = |A_CVI ∩ A_pot_hi| / |A_pot_hi|"

- id: W11.27
  description: "Validar formula pct_atualizado implementada"
  type: CHECK
  gate: G26
  priority: P0
  spec_ref: "Anexo D §2.2 - REQ-DNA-D-03"
  formula: "pct_atualizado = count(Δt <= L_dominio) / count(avaliados)"

- id: W11.28
  description: "Validar formula cvi_inexplicable_rate implementada"
  type: CHECK
  gate: G26
  priority: P0
  spec_ref: "Anexo D §2.3 - REQ-DNA-D-05"
  formula: "count(Baixa AND reason_code!=data_gap) / count(revisadas)"
```

## Wave W12 — ORR (+5 tasks)

```yaml
- id: W12.18
  description: "Validar formula p5_decision_concentration_hhi_norm"
  type: CHECK
  gate: G28
  priority: P0
  spec_ref: "P5-7 §4 - REQ-DNA-P57-01"
  formula: "(Σ p_i^2 − 1/N) / (1 − 1/N)"

- id: W12.19
  description: "Validar formula p5_capture_suspect_index"
  type: CHECK
  gate: G28
  priority: P0
  spec_ref: "P5-7 §4 - REQ-DNA-P57-02"
  components:
    - Dominancia em acoes criticas
    - Recorrencia de reversals anormais
    - Incidencia de conflitos de interesse

- id: W12.20
  description: "Validar threshold 0.70 aciona alerta"
  type: CHECK
  gate: G28
  priority: P0
  spec_ref: "Cap.2B1 - REQ-DNA-P57-03"
  done_criteria:
    - Se max p5_capture_suspect_index >= 0.70
    - Banner/alerta exibido
    - Revisao humana obrigatoria

- id: W12.21
  description: "Gerar sla_report.json com SLAs S40-S43 medidos"
  type: EVIDENCE
  gate: G29
  priority: P0
  spec_ref: "Cap.4B4 - REQ-C4B4-03"
  slas:
    - P1_latency: measured_value, limit, status
    - P2_precision: measured_value, limit, status
    - P3_decision: measured_value, limit, status
    - P4_api: measured_value, limit, status
    - reversal_rate: measured_value, limit, status
    - abuse_rate: measured_value, limit, status

- id: W12.22
  description: "Gerar go_no_go_7of7.json com checklist completo"
  type: EVIDENCE
  gate: G29
  priority: P0
  spec_ref: "Cap.4B4 - REQ-C4B4-03"
  criteria:
    - checklist_complete: true/false, evidence_link
    - guias_referenced: true/false, sample_count
    - tests_passing: true/false, coverage_pct
    - slas_within_limits: true/false, sla_report_ref
    - docs_updated: true/false, changelog_link
    - e40_5_operating: true/false, validation_method
    - ethical_preconditions: true/false, mac_report_ref
```

---

# INVARIANTES ADICIONADAS (v4.0)

| ID | Regra | Consequencia |
|----|-------|--------------|
| INV_SIGNAL_EVENTS_01 | Toda mutacao de incentive_signal DEVE gerar evento | Mutacao sem evento = bug P0 |
| INV_BATCH_MODE_01 | FieldAssembler DEVE suportar modo batch | Nao ter batch = G26 FAIL |
| INV_ROLE_CATALOG_01 | Catalogo P5-5 completo com poderes/proibicoes | Catalogo incompleto = G28 FAIL |

---

# MAPEAMENTO REQUISITOS -> TASKS (100%)

## Cobertura por Capitulo

| Capitulo | Requisitos | Tasks | Cobertura |
|----------|------------|-------|-----------|
| Cap.1 | 62 | 68 | 100% |
| Cap.2 | 48 | 52 | 100% |
| Cap.3 | 32 | 35 | 100% |
| Cap.4 | 28 | 31 | 100% |
| Cap.5 | 24 | 27 | 100% |
| Cap.8-9 | 30 | 34 | 100% |
| DNA | 22 | 28 | 100% |
| **TOTAL** | **246** | **289** | **100%** |

---

# WAVE DAG ATUALIZADO

```
W0 (baseline) ────────────────────────────────────────────────────────┐
 │                                                                     │
 └──> W0.5 (specifications) ─────────────────────────────────────────┐│
       │                                                              ││
       ├──> W1 (CVI core) [+4 tasks: eventos, batch, schemas]        ││
       │         │                                                    ││
       │         └──> W2 (pipeline)                                   ││
       │                   │                                          ││
       │                   └──> W3 (services) [+3 tasks: MQV, upsert] ││
       │                             │                                ││
       │                   ┌─────────┴──────────┐                     ││
       │                   │                    │                     ││
       │                   ▼                    ▼                     ││
       │            W4 (governance)       W5 (explain)                ││
       │            [+5 tasks: roles]          │                      ││
       │                   │                   │                      ││
       │                   ▼                   ▼                      ││
       │            W7 (FE gov)          W6 (FE CVI)                  ││
       │                   │             [+4 tasks: states]           ││
       │                   │                   │                      ││
       │                   └─────────┬─────────┘                      ││
       │                             │                                ││
       │                             ▼                                ││
       │                        W8 (UX)                               ││
       │                             │                                ││
       └──> W10 (observability) ─────┤                                ││
                                     │                                ││
                                     ▼                                ││
                              W9 (E2E tests)                          ││
                                     │                                ││
                                     ▼                                ││
                        W11 (gates) [+8 tasks: coherence, formulas]   ││
                                     │                                ││
                                     ▼                                ││
                        W12 (ORR) [+5 tasks: SLA, 7of7]  ─────────────┘│
                                                                       │
                                                           ────────────┘
```

---

# PROXIMOS PASSOS

## Ciclo 2/3: Segunda Rodada de Refinamento
- Revisar todas as 289 tasks para clareza e completude
- Adicionar criterios de DONE detalhados
- Refinar dependencias entre tasks
- Validar estimativas de complexidade

## Ciclo 3/3: Terceira Rodada de Polimento
- Polish final de nomenclatura
- Otimizacao de paralelismo
- Hardening de seguranca adicional
- UX polish items
- Documentacao final

---

**Gerado por:** Sprint Planner Tecnico v7
**Ciclo:** 1/3
**Data:** 2025-12-16
**Status:** COBERTURA 100% ATINGIDA
