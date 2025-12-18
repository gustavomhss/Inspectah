# S41 — Matriz de Rastreabilidade 100%
## Sprint Planner Tecnico v7 — Ciclo 1/3

> **Data:** 2025-12-16
> **Nivel:** State of the Art + Lapidacao Exaustiva
> **Objetivo:** 100% coverage de todos os requisitos

---

# PARTE 1: EXTRAÇÃO EXAUSTIVA DE REQUISITOS

## Cap.1 — Contexto, Escopo, Invariantes (62 requisitos)

### Bloco 1 — Packs R0 + Missao (20 requisitos)

| ID | Requisito | Fonte | Tipo |
|----|-----------|-------|------|
| REQ-C1B1-01 | Auditabilidade como requisito de primeira classe | B1§Pack Programa | MUST |
| REQ-C1B1-02 | Provenance como requisito de primeira classe | B1§Pack Programa | MUST |
| REQ-C1B1-03 | Anti-captura como requisito de primeira classe | B1§Pack Programa | MUST |
| REQ-C1B1-04 | P4 deve declarar origem (guia/tabela/dominio/gate) | B1§Pack Programa | MUST |
| REQ-C1B1-05 | Governanca (P5) com metricas, trilhas e limites | B1§Pack Programa | MUST |
| REQ-C1B1-06 | CVI v1 materializa incentivos em formato auditavel | B1§Pack Epico | MUST |
| REQ-C1B1-07 | Reputacao como classe de incentivo (rep) | B1§Pack Epico | MUST |
| REQ-C1B1-08 | Explicabilidade v2 = passos + contexto + conflitos + incerteza | B1§Pack Epico | MUST |
| REQ-C1B1-09 | Anti-captura = papeis/poderes/limites + trilhas + metricas | B1§Pack Epico | MUST |
| REQ-C1B1-10 | Filemap explicito no plano tecnico | B1§Licoes | MUST |
| REQ-C1B1-11 | Nomes canonicos de scripts gates/ORR | B1§Licoes | MUST |
| REQ-C1B1-12 | Modo degradado para dependencias externas | B1§Licoes | MUST |
| REQ-C1B1-13 | Scores com provenance (versao, origem, incerteza) | B1§Licoes | MUST |
| REQ-C1B1-14 | UI painel "Quem ganha com isso?" por tema/caso | B1§Pack UI | MUST |
| REQ-C1B1-15 | UI overlay CVI dentro da explicacao | B1§Pack UI | MUST |
| REQ-C1B1-16 | UI auditoria (calculado quando, com quais parametros) | B1§Pack UI | MUST |
| REQ-C1B1-17 | Estados criticos UI: dados insuficientes, hipoteses, alto risco, sem permissao, stale | B1§Pack UI | MUST |
| REQ-C1B1-18 | Progressive disclosure | B1§Pack UI | SHOULD |
| REQ-C1B1-19 | Evitar falsa autoridade | B1§Pack UI | MUST |
| REQ-C1B1-20 | Mostrar "porque" e "limites" no mesmo plano visual | B1§Pack UI | SHOULD |

### Bloco 2 — Escopo IN/OUT (24 requisitos)

| ID | Requisito | Fonte | Tipo |
|----|-----------|-------|------|
| REQ-C1B2-01 | IncentiveExtractor componente | B2§1.1 | MUST |
| REQ-C1B2-02 | ActorProfiler componente | B2§1.1 | MUST |
| REQ-C1B2-03 | FieldAssembler componente | B2§1.1 | MUST |
| REQ-C1B2-04 | ImpactAnalyzer componente | B2§1.1 | MUST |
| REQ-C1B2-05 | CVIQueryService componente | B2§1.1 | MUST |
| REQ-C1B2-06 | CVIAdminService componente | B2§1.1 | MUST |
| REQ-C1B2-07 | CVIMetricsEmitter componente | B2§1.1 | MUST |
| REQ-C1B2-08 | Ingestao minima de sinais (dados existentes + input manual governado) | B2§1.1 | MUST |
| REQ-C1B2-09 | Vetores/campos por tema/caso | B2§1.1 | MUST |
| REQ-C1B2-10 | Snapshots versionados | B2§1.1 | MUST |
| REQ-C1B2-11 | Metricas Anexo D | B2§1.1 | MUST |
| REQ-C1B2-12 | Componente rep deve existir com provenance | B2§1.1 | MUST |
| REQ-C1B2-13 | Superficie decisao → passos → evidencias → CVI → limites/hipoteses | B2§1.2 | MUST |
| REQ-C1B2-14 | Export/auditoria por ID (snapshot/versao CVI) | B2§1.2 | MUST |
| REQ-C1B2-15 | RBAC/roles tecnico | B2§1.3 | MUST |
| REQ-C1B2-16 | Trilha de mudancas (audit log) | B2§1.3 | MUST |
| REQ-C1B2-17 | Metricas P5-7 e alertas basicos | B2§1.3 | MUST |
| REQ-C1B2-18 | Contratos APIs para P4 | B2§1.4 | MUST |
| REQ-C1B2-19 | Estrategia versionamento compativel | B2§1.4 | MUST |
| REQ-C1B2-20 | source_id/provider_id associaveis a actor_id | B2§1.5 | MUST |
| REQ-C1B2-21 | Metadados para rastreabilidade de incentivos | B2§1.5 | MUST |
| REQ-C1B2-22 | Logs de agentes/fluxos para reconstrucao | B2§1.6 | MUST |
| REQ-C1B2-23 | SLAs de consulta P2-E6 | B2§1.6 | MUST |
| REQ-C1B2-24 | Alimentar metricas P5 (suspeita/concentracao) | B2§1.6 | MUST |

### Bloco 3 — Cenarios (8 requisitos)

| ID | Requisito | Fonte | Tipo |
|----|-----------|-------|------|
| REQ-C1B3-01 | Cenario A: abrir explicacao, ver CVI, inspecionar atores | B3§CenA | MUST |
| REQ-C1B3-02 | Cenario A: registrar evidencia vs hipotese | B3§CenA | MUST |
| REQ-C1B3-03 | Cenario B: trilhas + metricas concentracao | B3§CenB | MUST |
| REQ-C1B3-04 | Cenario B: bundle reprodutivel por decisao | B3§CenB | MUST |
| REQ-C1B3-05 | Cenario C: justificar mudanca, versionar | B3§CenC | MUST |
| REQ-C1B3-06 | Cenario C: recomputar snapshots, manter historico | B3§CenC | MUST |
| REQ-C1B3-07 | Cenario D: exibir "dados insuficientes" com cobertura | B3§CenD | MUST |
| REQ-C1B3-08 | Cenario D: sugerir proximos passos (coleta/annotation) | B3§CenD | SHOULD |

### Bloco 4 — Invariantes (10 requisitos)

| ID | Requisito | Fonte | Tipo |
|----|-----------|-------|------|
| REQ-C1B4-01 | S41_INV_PROVENANCE_01: cvi_version_id, model_version, computed_at, sha256, metricas | B4§1 | MUST |
| REQ-C1B4-02 | S41_INV_ANTI_BOTECO_01: incentivo sem lastro = hipotese marcada | B4§1 | MUST |
| REQ-C1B4-03 | S41_INV_AUDIT_01: alteracao = audit_event com autor, motivo, diff, timestamp | B4§1 | MUST |
| REQ-C1B4-04 | S41_INV_ANTI_CAPTURA_01: papeis incompativeis bloqueados e auditados | B4§1 | MUST |
| REQ-C1B4-05 | S41_INV_RBAC_01: allowlist explicita, fail-closed | B4§1 | MUST |
| REQ-C1B4-06 | S41_INV_PRIVACY_01: dados sensiveis internos apenas | B4§1 | MUST |
| REQ-C1B4-07 | S41_INV_GATES_01: objetivos mapeiam para G25-G29 | B4§1 | MUST |
| REQ-C1B4-08 | S41_INV_FILEMAP_01: plano tecnico com filemap explicito | B4§1 | MUST |
| REQ-C1B4-09 | Gates S41 sao G25-G29 (nomes fixos) | B4§2 | MUST |
| REQ-C1B4-10 | Scorecards em out/scorecards/, evidencias em out/evidence/ | B4§2 | MUST |

---

## Cap.2 — Gates, Metricas, DoD (48 requisitos)

### Bloco 1 — Objetivos e KPIs (18 requisitos)

| ID | Requisito | Fonte | Tipo |
|----|-----------|-------|------|
| REQ-C2B1-01 | O1: cov_alta_infl >= 0.60 (min aceitavel) | B1§1 | MUST |
| REQ-C2B1-02 | O1: pct_atualizado >= 0.70 (min aceitavel) | B1§1 | MUST |
| REQ-C2B1-03 | O1: cvi_inexplicable_rate <= 0.35 (min aceitavel) | B1§1 | MUST |
| REQ-C2B1-04 | O2: explain_p95_ms < 900ms (min aceitavel) | B1§1 | MUST |
| REQ-C2B1-05 | O2: drill_levels >= 3 (min aceitavel) | B1§1 | MUST |
| REQ-C2B1-06 | O3: p5_capture_suspect_index operacional | B1§1 | MUST |
| REQ-C2B1-07 | O3: regras de papel bloqueando | B1§1 | MUST |
| REQ-C2B1-08 | O4: cobertura OpenAPI >= 95% endpoints novos | B1§1 | MUST |
| REQ-C2B1-09 | CVI Query Latency P95 < 300ms | B1§2 | SHOULD |
| REQ-C2B1-10 | CVI Snapshot Freshness por dominio | B1§2 | MUST |
| REQ-C2B1-11 | Explain Cache Hit Rate >= 0.80 | B1§2 | SHOULD |
| REQ-C2B1-12 | Audit Coverage 100% mudancas CVI | B1§2 | MUST |
| REQ-C2B1-13 | SLA P1 Latencia <= 1 min | B1§2.1 | MUST |
| REQ-C2B1-14 | SLA P2 Precisao >= 92% | B1§2.1 | MUST |
| REQ-C2B1-15 | SLA P3 Decisao <= 10s | B1§2.1 | MUST |
| REQ-C2B1-16 | SLA P4 API <= 100ms | B1§2.1 | MUST |
| REQ-C2B1-17 | SLA Reversao <= 4% | B1§2.1 | MUST |
| REQ-C2B1-18 | SLA Abuso <= 1% | B1§2.1 | MUST |

### Bloco 2 — Gates G25-G29 (20 requisitos)

| ID | Requisito | Fonte | Tipo |
|----|-----------|-------|------|
| REQ-C2B2-01 | G25: OpenAPI/contratos completos e versionados | B2§G25 | MUST |
| REQ-C2B2-02 | G25: Contract tests happy + erro (4xx/5xx) | B2§G25 | MUST |
| REQ-C2B2-03 | G25: Mudancas breaking bloqueadas | B2§G25 | MUST |
| REQ-C2B2-04 | G25: Evidencia S41_G25_contracts.json | B2§G25 | MUST |
| REQ-C2B2-05 | G26: Snapshots com rep presente | B2§G26 | MUST |
| REQ-C2B2-06 | G26: Provenance completo (INV_PROVENANCE_01) | B2§G26 | MUST |
| REQ-C2B2-07 | G26: cov_alta_infl e pct_atualizado >= minimo | B2§G26 | MUST |
| REQ-C2B2-08 | G26: 6+ decisoes em coherence_review | B2§G26 | MUST |
| REQ-C2B2-09 | G26: cvi_coherence_label e reason_code por decisao | B2§G26 | MUST |
| REQ-C2B2-10 | G27: UI navega decisao → steps → CVI → atores | B2§G27 | MUST |
| REQ-C2B2-11 | G27: Estados explicitos no_data, hypothesis, stale | B2§G27 | MUST |
| REQ-C2B2-12 | G27: Screenshot/HTML export com provenance visivel | B2§G27 | MUST |
| REQ-C2B2-13 | G28: RBAC fail-closed testado (403) | B2§G28 | MUST |
| REQ-C2B2-14 | G28: Audit log registra mudancas | B2§G28 | MUST |
| REQ-C2B2-15 | G28: 2-person rule validado | B2§G28 | MUST |
| REQ-C2B2-16 | G28: p5_decision_concentration_hhi_norm calculavel | B2§G28 | MUST |
| REQ-C2B2-17 | G28: p5_capture_suspect_index >= 0.70 aciona alerta | B2§G28 | MUST |
| REQ-C2B2-18 | G28: Bundle auditavel extraivel | B2§G28 | MUST |
| REQ-C2B2-19 | G29: G25-G28 PASS | B2§G29 | MUST |
| REQ-C2B2-20 | G29: GO/NO-GO 7/7 PASS com evidencia | B2§G29 | MUST |

### Bloco 4 — DoD (10 requisitos)

| ID | Requisito | Fonte | Tipo |
|----|-----------|-------|------|
| REQ-C2B4-01 | DoD: Nao viola invariantes S41_INV_* | B4§Codigo | MUST |
| REQ-C2B4-02 | DoD: Erros tratados (4xx vs 5xx) e observaveis | B4§Codigo | MUST |
| REQ-C2B4-03 | DoD: Unit tests cobrindo logica CVI e roles | B4§Testes | MUST |
| REQ-C2B4-04 | DoD: Contract tests endpoints CVI/governanca | B4§Testes | MUST |
| REQ-C2B4-05 | DoD: E2E cobrindo J1 e J2 | B4§Testes | MUST |
| REQ-C2B4-06 | DoD: Metricas CVI (Anexo D) emitidas | B4§Obs | MUST |
| REQ-C2B4-07 | DoD: Metricas P5 minimas emitidas | B4§Obs | MUST |
| REQ-C2B4-08 | DoD: Dashboards/alertas minimos | B4§Obs | MUST |
| REQ-C2B4-09 | DoD: APIs documentadas | B4§Doc | MUST |
| REQ-C2B4-10 | DoD: Acessibilidade basica (teclado, estados erro) | B4§UX | SHOULD |

---

## Cap.3 — Arquitetura, Contratos (32 requisitos)

### Bloco 1 — Arquitetura (8 requisitos)

| ID | Requisito | Fonte | Tipo |
|----|-----------|-------|------|
| REQ-C3B1-01 | IDs estaveis: case_id, theme_id, actor_id de P2/P3 | B1§2.1 | MUST |
| REQ-C3B1-02 | Sinais internos + inputs governados | B1§2.1 | MUST |
| REQ-C3B1-03 | field_snapshot com vetores, top atores, provenance | B1§2.2 | MUST |
| REQ-C3B1-04 | impact_summary para UI | B1§2.2 | MUST |
| REQ-C3B1-05 | Explicacao referencia cvi_snapshot_id + cvi_version_id | B1§2.3 | MUST |
| REQ-C3B1-06 | CVI contextualiza, nao decide | B1§2.3 | MUST |
| REQ-C3B1-07 | CVIQuery somente leitura | B1§3 | MUST |
| REQ-C3B1-08 | Lacuna = mostra, nao preenche | B1§3 | MUST |

### Bloco 2 — Filemap (6 requisitos)

| ID | Requisito | Fonte | Tipo |
|----|-----------|-------|------|
| REQ-C3B2-01 | CVI em app/cvi/** | B2§1 | MUST |
| REQ-C3B2-02 | Rotas em app/api/*cvi*_routes.py | B2§1 | MUST |
| REQ-C3B2-03 | RBAC em app/middlewares/**, app/auth/** | B2§1 | MUST |
| REQ-C3B2-04 | Observabilidade em observability/** | B2§1 | MUST |
| REQ-C3B2-05 | Frontend em frontend/inspectah-ui/src/features/cvi/** | B2§1 | MUST |
| REQ-C3B2-06 | Gate scripts em bin/s41_*.sh | B2§1 | MUST |

### Bloco 3 — Contratos/APIs (12 requisitos)

| ID | Requisito | Fonte | Tipo |
|----|-----------|-------|------|
| REQ-C3B3-01 | CVI Snapshot schema completo (cvi_snapshot_id, cvi_version_id, etc.) | B3§1 | MUST |
| REQ-C3B3-02 | Campo rep deve existir (mesmo magnitude 0) | B3§1 | MUST |
| REQ-C3B3-03 | hypotheses[] nunca vazio com proxy | B3§1 | MUST |
| REQ-C3B3-04 | get_cvi_snapshot(case_id|theme_id, window) | B3§2 | MUST |
| REQ-C3B3-05 | list_top_actors(case_id|theme_id, class, limit) | B3§2 | MUST |
| REQ-C3B3-06 | get_actor_profile(actor_id) | B3§2 | MUST |
| REQ-C3B3-07 | get_cvi_metrics(domain|theme, window) | B3§2 | MUST |
| REQ-C3B3-08 | propose_param_change(diff, reason) | B3§2 | MUST |
| REQ-C3B3-09 | approve_param_change(proposal_id, approver) | B3§2 | MUST |
| REQ-C3B3-10 | upsert_incentive_signal(...) | B3§2 | MUST |
| REQ-C3B3-11 | get_audit_bundle(decision_id) | B3§2 | MUST |
| REQ-C3B3-12 | DecisionExplanation com cvi_snapshot_id ou cvi_unavailable_reason | B3§3 | MUST |

### Bloco 4 — Trade-offs (6 requisitos)

| ID | Requisito | Fonte | Tipo |
|----|-----------|-------|------|
| REQ-C3B4-01 | Preferencia batch + cache (reprodutibilidade) | B4§1 | SHOULD |
| REQ-C3B4-02 | Acesso interno e governado | B4§2 | MUST |
| REQ-C3B4-03 | Logs de acesso | B4§2 | SHOULD |
| REQ-C3B4-04 | Export com redactions se necessario | B4§2 | SHOULD |
| REQ-C3B4-05 | Endpoints versionados, evitar breaking | B4§4 | MUST |
| REQ-C3B4-06 | Mudancas CVI append-only | B4§4 | MUST |

---

## Cap.4 — Execucao, Cenarios Falha (28 requisitos)

### Bloco 1 — Waves (6 requisitos)

| ID | Requisito | Fonte | Tipo |
|----|-----------|-------|------|
| REQ-C4B1-01 | W0: Verificar estabilidade S40, definir piloto | B1§W0 | MUST |
| REQ-C4B1-02 | W1: Pipeline minimo + CVIQuery + CVIAdmin + metricas | B1§W1 | MUST |
| REQ-C4B1-03 | W2: Explicacoes referenciam snapshot/versao | B1§W2 | MUST |
| REQ-C4B1-04 | W3: Enforcement papeis + trilha + metricas P5-7 | B1§W3 | MUST |
| REQ-C4B1-05 | W4: QA e hardening, testes e2e | B1§W4 | MUST |
| REQ-C4B1-06 | W5: ORR/GO-NO-GO com G25-G29 | B1§W5 | MUST |

### Bloco 2 — Runbook (8 requisitos)

| ID | Requisito | Fonte | Tipo |
|----|-----------|-------|------|
| REQ-C4B2-01 | Ordem: sanity → unit → FE → contract → gates → ORR | B2§1 | MUST |
| REQ-C4B2-02 | Script bin/s41_g25_contracts.sh existe | B2§3 | MUST |
| REQ-C4B2-03 | Script bin/s41_g26_cvi.sh existe | B2§3 | MUST |
| REQ-C4B2-04 | Script bin/s41_g27_explainability.sh existe | B2§3 | MUST |
| REQ-C4B2-05 | Script bin/s41_g28_governance_audit.sh existe | B2§3 | MUST |
| REQ-C4B2-06 | Script bin/s41_g29_orr.sh existe | B2§3 | MUST |
| REQ-C4B2-07 | Cada gate gera scorecard + evidencia | B2§3 | MUST |
| REQ-C4B2-08 | unverified_checks[] registrado se servico externo indisponivel | B2§4 | MUST |

### Bloco 3 — Cenarios Falha (10 requisitos)

| ID | Requisito | Fonte | Tipo |
|----|-----------|-------|------|
| REQ-C4B3-01 | Falha 1: CVI sem dados → UI "dados insuficientes" | B3§F1 | MUST |
| REQ-C4B3-02 | Falha 1: Sistema nao inventa incentivos | B3§F1 | MUST |
| REQ-C4B3-03 | Falha 1: Sugerir annotation governada | B3§F1 | SHOULD |
| REQ-C4B3-04 | Falha 2: P95 acima → usar snapshot cache | B3§F2 | MUST |
| REQ-C4B3-05 | Falha 2: Progressive disclosure sob demanda | B3§F2 | SHOULD |
| REQ-C4B3-06 | Falha 3: Burla governanca → bloquear + audit event + alerta | B3§F3 | MUST |
| REQ-C4B3-07 | Falha 4: Divergencia versao → bug P0, bloquear gate | B3§F4 | MUST |
| REQ-C4B3-08 | Falha 5: p5_capture_suspect_index alto → fluxo auditoria | B3§F5 | MUST |
| REQ-C4B3-09 | Falha 5: Exportar bundles | B3§F5 | MUST |
| REQ-C4B3-10 | Falha 5: Registrar decisao de mitigacao | B3§F5 | MUST |

### Bloco 4 — Evidencias (4 requisitos)

| ID | Requisito | Fonte | Tipo |
|----|-----------|-------|------|
| REQ-C4B4-01 | Estrutura out/scorecards/S41_G*.json | B4§1 | MUST |
| REQ-C4B4-02 | Estrutura out/evidence/S41_G*/ com checks.json, MANIFEST.json | B4§1 | MUST |
| REQ-C4B4-03 | sla_report.json e go_no_go_7of7.json em G29 | B4§2 | MUST |
| REQ-C4B4-04 | Rastreabilidade completa (inputs, versao, timestamp, artefatos) | B4§4 | MUST |

---

## Cap.5 — Jornadas J1-J4 (24 requisitos)

### Bloco 1 — Personas e Mapa (6 requisitos)

| ID | Requisito | Fonte | Tipo |
|----|-----------|-------|------|
| REQ-C5B1-01 | Operador Ops (P4): somente leitura CVI/explain | B1§Mapa | MUST |
| REQ-C5B1-02 | Auditor: role leitura/auditoria, externo segregado | B1§Mapa | MUST |
| REQ-C5B1-03 | Admin Governanca: role mutacao com 2-person rule | B1§Mapa | MUST |
| REQ-C5B1-04 | Chair/PanelMember: metadado + RBAC minimo | B1§Mapa | SHOULD |
| REQ-C5B1-05 | Endpoints com allowlist explicita (INV_RBAC_01) | B1§Mapa | MUST |
| REQ-C5B1-06 | 4 jornadas criticas: J1, J2, J3, J4 | B1§Jornadas | MUST |

### Bloco 2 — J1 (6 requisitos)

| ID | Requisito | Fonte | Tipo |
|----|-----------|-------|------|
| REQ-C5B2-01 | J1: Operador abre decisao | B2§Fluxo | MUST |
| REQ-C5B2-02 | J1: UI mostra steps + evidencias | B2§Fluxo | MUST |
| REQ-C5B2-03 | J1: CVI overlay com top atores, coverage, freshness | B2§Fluxo | MUST |
| REQ-C5B2-04 | J1: Provenance acessivel (versao, manifest, hypotheses) | B2§Fluxo | MUST |
| REQ-C5B2-05 | J1: Acoes: marcar suspeita, abrir bundle, solicitar annotation | B2§Fluxo | MUST |
| REQ-C5B2-06 | J1: Estados criticos obrigatorios em UX | B2§Estados | MUST |

### Bloco 3 — J2 (6 requisitos)

| ID | Requisito | Fonte | Tipo |
|----|-----------|-------|------|
| REQ-C5B3-01 | J2: Admin abre pagina parametros | B3§Fluxo | MUST |
| REQ-C5B3-02 | J2: Proposta com diff + motivo + referencia | B3§Fluxo | MUST |
| REQ-C5B3-03 | J2: Aprovacao 2-person rule | B3§Fluxo | MUST |
| REQ-C5B3-04 | J2: Aplicacao cria nova versao + audit event | B3§Fluxo | MUST |
| REQ-C5B3-05 | J2: UI mostra antes/depois e impacto | B3§Fluxo | MUST |
| REQ-C5B3-06 | J2: Versoes append-only | B3§Regras | MUST |

### Bloco 4 — J3 (6 requisitos)

| ID | Requisito | Fonte | Tipo |
|----|-----------|-------|------|
| REQ-C5B4-01 | J3: Auditor seleciona decisao | B4§Fluxo | MUST |
| REQ-C5B4-02 | J3: Solicita audit bundle | B4§Fluxo | MUST |
| REQ-C5B4-03 | J3: Bundle contem decisao, snapshot, manifest, versao, metricas P5 | B4§Fluxo | MUST |
| REQ-C5B4-04 | J3: Verificar reprodutibilidade | B4§Fluxo | MUST |
| REQ-C5B4-05 | J3: Estados: OK, Suspeita, Inconclusivo | B4§Estados | MUST |
| REQ-C5B4-06 | J3: Destacar concentracao, conflitos, reversals | B4§Regras | MUST |

---

## Cap.8-9 — Frontend/UX (30 requisitos)

### Cap.8 — FE (14 requisitos)

| ID | Requisito | Fonte | Tipo |
|----|-----------|-------|------|
| REQ-C8B1-01 | UI nao pode ser lenta, confusa ou magica | B1§1 | MUST |
| REQ-C8B1-02 | Evitar payloads gigantes | B1§1 | MUST |
| REQ-C8B1-03 | Carregar detalhes sob demanda | B1§1 | MUST |
| REQ-C8B1-04 | Provenance no caminho curto | B1§1 | MUST |
| REQ-C8B1-05 | Primeiro paint: decisao + resumo | B1§2 | MUST |
| REQ-C8B1-06 | Progressive disclosure para CVI | B1§2 | MUST |
| REQ-C8B1-07 | Paginacao/virtualizacao para listas de atores | B1§2 | SHOULD |
| REQ-C8B1-08 | Cache por cvi_snapshot_id | B1§3 | MUST |
| REQ-C8B1-09 | Chave cache inclui cvi_version_id | B1§3 | MUST |
| REQ-C8B1-10 | FCP < 3s em maquina dev | B1§4 | SHOULD |
| REQ-C8B2-01 | Componente CVIOverlayPanel | B2§1 | MUST |
| REQ-C8B2-02 | Componente CVISnapshotHeader | B2§1 | MUST |
| REQ-C8B2-03 | Componente CVIActorList com filtro/busca/paginacao | B2§1 | MUST |
| REQ-C8B2-04 | Componente CVIActorCard com badges | B2§1 | MUST |
| REQ-C8B2-05 | Componente CVIProvenanceDrawer | B2§1 | MUST |
| REQ-C8B2-06 | Componente GovernanceAuditTrail | B2§1 | MUST |
| REQ-C8B2-07 | Maquina estados: idle → loading → ready/no_data/unauthorized/error/stale | B2§2 | MUST |
| REQ-C8B2-08 | no_data nunca parece erro 500 | B2§3 | MUST |
| REQ-C8B2-09 | hypothesis e rotulo visual obrigatorio (badge) | B2§3 | MUST |

### Cap.9 — UX (11 requisitos)

| ID | Requisito | Fonte | Tipo |
|----|-----------|-------|------|
| REQ-C9B1-01 | Transparencia radical: numero/ordem com origem | B1§1 | MUST |
| REQ-C9B1-02 | Incerteza explicita: UI propria | B1§1 | MUST |
| REQ-C9B1-03 | Nao moralizar atores | B1§1 | MUST |
| REQ-C9B1-04 | Evitar falsa autoridade | B1§1 | MUST |
| REQ-C9B3-01 | Microcopy "Dados insuficientes" com CTA | B3 | MUST |
| REQ-C9B3-02 | Badge "Hipotese (proxy)" com tooltip | B3 | MUST |
| REQ-C9B3-03 | Banner "Alto risco de captura" | B3 | MUST |
| REQ-C9B3-04 | Titulo "Acesso restrito" | B3 | MUST |
| REQ-C9B4-01 | Todo numero tem versao + data + link provenance | B4 | MUST |
| REQ-C9B4-02 | Usuario chega ao manifest em <= 3 interacoes | B4 | MUST |
| REQ-C9B4-03 | Sem jargao sem tooltips | B4 | SHOULD |

---

## DNA — Documentos Normativos (22 requisitos)

### Anexo C — Arquitetura CVI (8 requisitos)

| ID | Requisito | Fonte | Tipo |
|----|-----------|-------|------|
| REQ-DNA-C-01 | IncentiveSignalAdded/Updated/Retracted eventos | Anexo C§1.2 | MUST |
| REQ-DNA-C-02 | ActorProfiler sem atribuir vetores, so contexto | Anexo C§1.3 | MUST |
| REQ-DNA-C-03 | FieldAssembler modos online e batch | Anexo C§1.4 | MUST |
| REQ-DNA-C-04 | ImpactAnalyzer nao decide, contextualiza | Anexo C§1.5 | MUST |
| REQ-DNA-C-05 | cvi_incentive_signal schema | Anexo C§2.2 | MUST |
| REQ-DNA-C-06 | cvi_actor_profile schema | Anexo C§2.3 | MUST |
| REQ-DNA-C-07 | cvi_case_field schema | Anexo C§2.4 | MUST |
| REQ-DNA-C-08 | GetDecisionContextIncentives para MQV/MAC | Anexo C§4.5 | MUST |

### Anexo D — Metricas CVI (6 requisitos)

| ID | Requisito | Fonte | Tipo |
|----|-----------|-------|------|
| REQ-DNA-D-01 | cov_atores formula | Anexo D§2.1 | MUST |
| REQ-DNA-D-02 | cov_alta_infl formula | Anexo D§2.1 | MUST |
| REQ-DNA-D-03 | pct_atualizado formula | Anexo D§2.2 | MUST |
| REQ-DNA-D-04 | cvi_coherence_label por decisao | Anexo D§2.3 | MUST |
| REQ-DNA-D-05 | cvi_inexplicable_rate formula | Anexo D§2.3 | MUST |
| REQ-DNA-D-06 | Scorecards por dominio | Anexo D§3 | MUST |

### P5-5 — Anti-Captura (4 requisitos)

| ID | Requisito | Fonte | Tipo |
|----|-----------|-------|------|
| REQ-DNA-P55-01 | Catalogo papeis: GovernanceActor, Judge, Chair, Observer, Auditor | P5-5§4 | MUST |
| REQ-DNA-P55-02 | Poderes permitidos/proibidos por papel | P5-5§4 | MUST |
| REQ-DNA-P55-03 | Nenhum ator acumula poderes incompativeis | P5-5§5 | MUST |
| REQ-DNA-P55-04 | Indicadores de concentracao monitorados | P5-5§5 | MUST |

### P5-7 — Metricas P5 (4 requisitos)

| ID | Requisito | Fonte | Tipo |
|----|-----------|-------|------|
| REQ-DNA-P57-01 | p5_decision_concentration_hhi_norm formula | P5-7§4 | MUST |
| REQ-DNA-P57-02 | p5_capture_suspect_index formula | P5-7§4 | MUST |
| REQ-DNA-P57-03 | Threshold 0.70 para alerta | Cap.2B1§3 | MUST |
| REQ-DNA-P57-04 | Scorecards anti-captura | P5-7§5 | MUST |

---

# PARTE 2: CONTAGEM TOTAL DE REQUISITOS

| Capitulo | Requisitos |
|----------|------------|
| Cap.1 — Contexto, Escopo, Invariantes | 62 |
| Cap.2 — Gates, Metricas, DoD | 48 |
| Cap.3 — Arquitetura, Contratos | 32 |
| Cap.4 — Execucao, Cenarios Falha | 28 |
| Cap.5 — Jornadas J1-J4 | 24 |
| Cap.8-9 — Frontend/UX | 30 |
| DNA — Documentos Normativos | 22 |
| **TOTAL** | **246** |

---

# PARTE 3: GAPS vs PLANO v3.1

## Requisitos NAO cobertos no plano v3.1 (identificados)

| ID | Requisito | Wave proposta | Prioridade |
|----|-----------|---------------|------------|
| REQ-DNA-C-01 | Eventos IncentiveSignal* | W1 | P0 |
| REQ-DNA-C-03 | FieldAssembler modo batch | W1 | P0 |
| REQ-DNA-C-08 | GetDecisionContextIncentives | W3 | P0 |
| REQ-C3B3-10 | upsert_incentive_signal | W3 | P0 |
| REQ-C4B3-03 | Sugerir annotation governada | W6 | P1 |
| REQ-C5B2-05 | Acao: solicitar annotation | W6 | P1 |
| REQ-C8B2-07 | Maquina estados completa (5 estados) | W6 | P0 |
| REQ-C9B4-02 | <= 3 interacoes para manifest | W8 | P1 |
| REQ-DNA-P55-01 | Catalogo papeis completo | W4 | P0 |
| REQ-DNA-P55-02 | Poderes permitidos/proibidos | W4 | P0 |
| REQ-DNA-D-06 | Scorecards por dominio (estrutura) | W11 | P1 |
| REQ-C2B2-08 | 6+ decisoes coherence_review | W11 | P0 |
| REQ-C2B2-09 | cvi_coherence_label + reason_code | W11 | P0 |
| REQ-C4B2-08 | unverified_checks[] em modo degradado | W11 | P1 |

**Total gaps identificados:** 14

---

**Gerado por:** Sprint Planner Tecnico v7
**Ciclo:** 1/3
**Data:** 2025-12-16
