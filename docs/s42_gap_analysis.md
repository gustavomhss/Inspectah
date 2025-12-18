# Análise de Gaps — Sprint 42 (v3.0)

> Análise crítica profunda após releitura da spec completa (9×4 capítulos)

---

## GAPS CRÍTICOS IDENTIFICADOS

### 1. DATASETS (Severidade: CRÍTICA)

**Spec exige (Cap.6B2):**
```
datasets/
├── gold_standard/       # ~700 casos total
│   ├── health_crises/       ~150 casos
│   ├── political_scandals/  ~200 casos
│   ├── historical_claims/   ~100 casos
│   ├── scientific_disputes/ ~120 casos
│   └── economic_events/     ~130 casos
├── adversarial/         # ~255 casos total
│   ├── coordinated_attacks/ ~80 casos (≥95%)
│   ├── astroturfing/        ~60 casos (≥90%)
│   ├── semantic_drift/      ~40 casos (≥85%)
│   ├── temporal_attacks/    ~30 casos (≥98%)
│   ├── source_washing/      ~25 casos (≥80%)
│   └── reversal_attacks/    ~20 casos (≥99%)
├── edge_cases/          # ~145 casos total
│   ├── threshold_boundary/  ~50 casos
│   ├── multi_domain/        ~30 casos
│   ├── rapid_evolution/     ~40 casos
│   └── contradictory/       ~25 casos
└── regression/
    ├── fixed_bugs/
    └── known_failures/
```

**Plano atual:** 50+20+10 = 80 casos apenas
**Gap:** Falta ~1020 casos e estrutura canônica de domínios

---

### 2. MANIFEST/LINEAGE (Severidade: CRÍTICA)

**Spec exige (Cap.6B2):**
- `simulation_run_id`
- `mode` (dry-run; domínio; perfil)
- `policy_id` + `policy_version` (ou `policy_bundle_id`)
- `mac_version` (commit/tag)
- `mi_version` quando aplicável
- `dataset_id` + `dataset_version`
- `params` efetivos (incluindo overrides, com `override_reason`)
- `seed`/`rng` e `temperature`
- `timestamps` + `git_commit` do servidor
- `replay_token`

**Gap:** Não há task específica para implementar manifest completo

---

### 3. CONTRATOS DE ERRO (Severidade: ALTA)

**Spec exige (Cap.3B2):**
- `error_code` estável (ex: `POLICY_NOT_FOUND`, `SIGNAL_SNAPSHOT_INVALID`, `RBAC_FORBIDDEN`)
- `message_human` (PT-BR curto)
- `details` (quando apropriado)

**Gap:** Task S42-BE-004 menciona mas não lista todos os códigos

---

### 4. ESTADOS DE RUN PARA BATCH (Severidade: ALTA)

**Spec exige (Cap.8B2):**
- Estados: `queued` | `running` | `succeeded` | `failed` | `canceled`
- Polling ou stream para progresso
- Logs resumidos (sem dados sensíveis)
- Cancelamento e retry como ação visível

**Gap:** Task S42-BE-025 menciona parcialmente mas falta cancelamento e streaming

---

### 5. ENDPOINTS FALTANTES (Severidade: ALTA)

**Spec exige (Cap.3B2):**
- `POST /api/v1/mac/evaluate` — avaliação real (produção)
- `GET /api/v1/mac/decisions/{id}` — buscar decisão
- `GET /api/v1/mac/decisions` — listagem paginada

**Gap:** Esses endpoints não estão no plano

---

### 6. EXPERIENCE DERIVATION (Severidade: MÉDIA)

**Spec exige (Cap.3B2):**
> "Caso ExperienceStore ainda não exista: derivar a 'experiência' como trajetória resumida a partir de históricos disponíveis, marcando explicitamente `experience_source: derived`"

**Gap:** Task S42-BE-043 não cobre derivação

---

### 7. VIRTUALIZATION/WINDOWING (Severidade: MÉDIA)

**Spec exige (Cap.8B3):**
- Virtualização (windowing) por padrão para listas grandes
- Filtros e busca com debounce
- Ordenação determinística

**Gap:** Não há task específica

---

### 8. COPY/DISCLAIMERS DETALHADOS (Severidade: ALTA)

**Spec exige (Cap.9B3):**
- Estados visuais: `redacted`, `not_authorized`, `not_available`, `available`
- Copy PT-BR específico para cada estado
- "Vazio nunca pode ser ambíguo"

**Gap:** Task S42-UX-001 não detalha os copies específicos

---

### 9. TESTES FALTANTES (Severidade: ALTA)

**Spec exige (Cap.8B3):**
- Testes de determinismo com batch (não só unitário)
- Testes de estados MI (4 estados) em FE
- Testes de diff view
- Testes de degradação com payloads grandes
- Mocks com lineage (manifest)

**Gap:** Cobertura insuficiente

---

### 10. OBSERVABILIDADE DETALHADA (Severidade: MÉDIA)

**Spec exige (Cap.2B2 — ORR):**
- Correlação por `simulation_id`/`run_id` nos logs
- Métricas por gate (determinismo, latency, coverage, redaction)

**Gap:** Tasks de observabilidade superficiais

---

### 11. ORR CHECKLIST (Severidade: CRÍTICA)

**Spec exige (Cap.2B2):**
- **Infra:** endpoints documentados e versionados; rollback não manual
- **Observabilidade:** logs estruturados + métricas por gate + correlação
- **Operações:** runbook mínimo + política de retenção
- **Segurança:** AuthN/AuthZ + RBAC testável + audit log + evidências redatadas
- **Capacidade:** teste de carga confirmando p95/p99 e degradação graciosa

**Gap:** Não há tasks para runbooks operacionais completos, teste de carga, política de retenção

---

### 12. EVIDÊNCIAS REDATADAS POR PADRÃO (Severidade: CRÍTICA)

**Spec exige (Cap.4B4 e Cap.6B4):**
> "Evidências em `out/` devem ser redatadas por padrão quando envolvem MI/Experiências"

**Gap:** Não há task para garantir redação automática em evidências

---

### 13. PLANO ADIABÁTICO — CAMPOS OBRIGATÓRIOS (Severidade: ALTA)

**Spec exige (Cap.6B3):**
- `plan_id` + `plan_version`
- `baseline_policy_version` + `target_policy_version`
- `phases[]` com:
  - `phase_id`
  - `delta`
  - `duration`
  - `constraints` (derivative caps)
  - `success_criteria`
  - `rollback_strategy`
- Provenance (commit, dataset(s), autor, timestamp, justificativa)

**Gap:** Task S42-BE-003 não cobre todos os campos

---

### 14. SCORECARD CAMPOS MÍNIMOS (Severidade: ALTA)

**Spec exige (Cap.2B3):**
- `sprint`, `gate`, `status` (PASS/NO_GO/GO_COM_RESSALVA)
- `commit`, `timestamp_utc`
- `inputs` (policy_version/params_version/plan_version/dataset_id)
- `metrics` (valores e targets)
- `targets` (thresholds mandatórios/desejáveis aplicados)
- `violations` (lista de violações e severidade)
- `evidence_paths`
- `limitations`

**Gap:** Tasks de bundle não detalham todos os campos

---

## RESUMO DE GAPS POR SEVERIDADE

| Severidade | Quantidade | Exemplos |
|------------|------------|----------|
| CRÍTICA | 5 | Datasets, Manifest, ORR checklist, Evidências redatadas, INV_S42_NOFAKE |
| ALTA | 8 | Endpoints, Estados de run, Plano adiabático, Scorecard, Testes |
| MÉDIA | 4 | Experience derivation, Virtualization, Observabilidade |

---

## AÇÕES NECESSÁRIAS

1. Expandir datasets para estrutura canônica (~1100 casos)
2. Criar task específica para Manifest/Lineage
3. Adicionar endpoints faltantes (decisions, evaluate)
4. Expandir estados de batch (cancel, stream)
5. Criar task para Experience derivation
6. Adicionar virtualization no FE
7. Detalhar copy/disclaimers
8. Expandir testes (batch determinism, payloads grandes, mocks com lineage)
9. Criar runbooks operacionais detalhados
10. Adicionar teste de carga
11. Garantir redação automática de evidências
12. Completar campos de scorecard
13. Adicionar política de retenção

---

*Análise gerada pelo Sprint Planner Técnico v7*
*Rodada: Análise Crítica Profunda*
