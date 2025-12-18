# S40 Context Anchor - Truth-DB Estavel

**Created:** 2025-12-17
**Sprint:** S40 - Truth-DB Estavel
**Status:** Em teste manual - populando dados reais

---

## Resumo da Sprint 40

Sprint 40 implementa o **Truth-DB Estavel** com foco em:

1. **DecisionBlock** - Registros imutaveis de decisoes com proveniencia completa
2. **References (Guias/Pilares)** - Rastreabilidade de documentos de referencia
3. **E40.5 Enforcement** - Validacao automatica de invariantes
4. **NO-GO Signals** - Deteccao de INCONSISTENCY, SUSPICION, ABUSE
5. **P4 Exposure** - API com SLA P95<100ms, P99<200ms

---

## Entregas Completas (W0-W4)

### Backend (11 arquivos)
- `app/truth/repository.py` - TruthRepository + DecisionBlockRepository
- `app/truth/validators.py` - Validadores com INV-DB-01 a INV-DB-04
- `app/truth/references.py` - build_references()
- `app/truth/experiences.py` - Experience model para similaridade
- `app/claims/signals.py` - SignalRepository com deteccao NO-GO
- `app/claims/export.py` - ClaimGraph export/ingest
- `app/api/truth_routes.py` - Rotas P4 Truth Twin
- `app/api/truth_schemas.py` - Schemas Pydantic
- `app/api/metrics.py` - Metricas P4
- `app/api/middleware/provenance.py` - Middleware de proveniencia
- `app/guardian/flow.py` - NOGO_BLOCKED event

### Frontend (13 arquivos)
- `frontend/inspectah-ui/src/modules/truth/types/index.ts`
- `frontend/inspectah-ui/src/modules/truth/components/StatusBadges.tsx`
- `frontend/inspectah-ui/src/modules/truth/components/DecisionTimeline.tsx`
- `frontend/inspectah-ui/src/modules/truth/components/ProvenancePanel.tsx`
- `frontend/inspectah-ui/src/modules/truth/components/DecisionInspector.tsx`
- `frontend/inspectah-ui/src/modules/truth/components/index.ts`
- `frontend/inspectah-ui/src/modules/truth/hooks/useTruthTwin.ts`
- `frontend/inspectah-ui/src/modules/truth/hooks/index.ts`
- `frontend/inspectah-ui/src/modules/truth/api/truthApi.ts`
- `frontend/inspectah-ui/src/modules/truth/api/index.ts`
- `frontend/inspectah-ui/src/modules/truth/pages/SpTruthTwinPage.tsx`
- `frontend/inspectah-ui/src/modules/truth/pages/index.ts`
- `frontend/inspectah-ui/src/modules/truth/index.ts`

### Schemas (3 arquivos)
- `schemas/decision_block_v1.json`
- `schemas/claimgraph_export_v1.json`
- `schemas/truth_twin_v1.json`

### Migration
- `db/migrations/033_sprint40_decision_blocks.sql`

### Testes (16 arquivos)
- `tests/truth/test_validators.py` (65 testes)
- `tests/truth/test_references.py` (12 testes)
- `tests/truth/test_experiences.py` (15 testes)
- `tests/truth/test_repository_s40.py` (18 testes)
- `tests/truth/test_e40_5_enforcement.py` (15 testes)
- `tests/truth/test_canonical_cases.py` (9 testes)
- `tests/claims/test_export.py` (8 testes)
- `tests/claims/test_signals.py` (14 testes)
- `tests/claims/test_nogo_signals.py` (15 testes)
- `tests/api/test_truth_routes_p4.py` (12 testes)
- `tests/api/test_truth_twin_routes.py` (8 testes)
- `tests/api/test_p4_metrics.py` (6 testes)
- `tests/api/test_p4_latency.py` (5 testes)
- `tests/api/test_provenance_middleware.py` (7 testes)
- `tests/api/test_truth_schemas.py` (9 testes)
- `tests/benchmarks/test_p4_benchmark.py` (4 testes)

---

## Resultados dos Testes

| Suite | Resultado |
|-------|-----------|
| Backend (pytest) | 4,446 passed |
| Frontend (vitest) | 210 passed |
| Cobertura | 88% |

### Gates S40
- G20 (Contracts): PASS 18/18
- G22 (ClaimGraph): PASS 21/21
- G23 (Truth-DB): PASS 21/21
- G24 (P4 Exposure): PASS 29/29

---

## Problema Atual

O historico esta vazio - nao da pra testar a UI Truth Twin sem dados.

**Solucao:** Popular o sistema com casos reais complexos:
- Cada caso deve ter 10+ noticias
- Casos exemplo: Lava Jato, Pandemia COVID, etc.
- Dados devem incluir DecisionBlocks com referencias completas

---

## Estrutura de Dados

### Claims (JSONL)
```json
{
  "claim_id": "cl_xxx",
  "content_id_ref": "xxx",
  "claim_text": "Texto da claim",
  "claim_type": "factual|normativo",
  "scope": {"who": null, "what": "...", "when": "...", "where": "BR"},
  "published_at_ref": "ISO datetime",
  "risk_level": "low|medium|high"
}
```

### Truth Records (SQLite)
- id, slug, claim_id, domain, current_state
- last_decision_id, metadata, created_at, updated_at

### Decision Blocks (SQLite)
- id, decision_id, claim_id, domain, gate
- initial_state, final_state, decision_type
- policy_name, policy_version, committee_summary
- invariants_checked, evidence_refs
- references_json (guias[], pilares[], e40_5)
- state_transition (from_state, to_state, reason)
- experience_refs, created_at, latency_ms

### TruthState Enum
- UNKNOWN, CLAIMED, UNDER_REVIEW, PROVISIONAL
- ESTABLISHED_FACT, UNDER_DISPUTE, RETRACTED

---

## Dados Populados

### Casos Reais Carregados

**Total: 478 claims com decisoes e proveniencia completa**

#### Caso 1: Pandemia COVID-19 Brasil (99 noticias)
Claims: `cl_covid19_brasil_000` ate `cl_covid19_brasil_098`
Fonte principal: Ministerio da Saude, Fiocruz, CONASS, Anvisa, Butantan, OMS, CNN Brasil, Agencia Brasil

Exemplos para testar:
- `cl_covid19_brasil_002` - Primeiro caso confirmado (ESTABLISHED_FACT)
- `cl_covid19_brasil_036` - Colapso Manaus oxigenio (ESTABLISHED_FACT)
- `cl_covid19_brasil_054` - CPI instalada no Senado (ESTABLISHED_FACT)
- `cl_covid19_brasil_076` - CPI pede indiciamento (ESTABLISHED_FACT)

#### Caso 2: Impeachment Dilma Rousseff (97 noticias)
Claims: `cl_impeachment_dilma_000` ate `cl_impeachment_dilma_096`
Fonte principal: Senado Federal, Camara dos Deputados, STF, TSE, Planalto, Agencia Brasil

Exemplos para testar:
- `cl_impeachment_dilma_012` - Cunha aceita pedido impeachment (ESTABLISHED_FACT)
- `cl_impeachment_dilma_039` - Camara aprova 367 a 137 (ESTABLISHED_FACT)
- `cl_impeachment_dilma_079` - Senado condena 61 a 20 (ESTABLISHED_FACT)
- `cl_impeachment_dilma_085` - MPF arquiva pedaladas (ESTABLISHED_FACT)

#### Caso 3: Operacao Lava Jato (96 noticias)
Claims: `cl_lava_jato_000` ate `cl_lava_jato_095`
Fonte principal: MPF, CNN Brasil, Agencia Brasil, Conjur, Poder360, STF, TRF4

Exemplos para testar:
- `cl_lava_jato_000` - 1a fase Lava Jato deflagracao (ESTABLISHED_FACT)
- `cl_lava_jato_050` - Delacao JBS atinge politicos (ESTABLISHED_FACT)
- `cl_lava_jato_078` - STF anula condenacoes Lula (ESTABLISHED_FACT)

#### Caso 4: Fraude INSS (94 noticias)
Claims: `cl_inss_fraude_000` ate `cl_inss_fraude_093`
Fonte principal: CGU, Policia Federal, MPF, Camara, Senado, TCU, Ministerio da Previdencia

Exemplos para testar:
- `cl_inss_fraude_030` - R$ 6,3 bilhoes desviados estimativa (ESTABLISHED_FACT)
- `cl_inss_fraude_057` - Operacao Sem Desconto deflagrada (ESTABLISHED_FACT)
- `cl_inss_fraude_075` - Ex-presidente INSS preso (ESTABLISHED_FACT)

#### Caso 5: Governo Bolsonaro (92 noticias)
Claims: `cl_bolsonaro_governo_000` ate `cl_bolsonaro_governo_091`
Fonte principal: Planalto, Agencia Brasil, STF, TSE, PF, Senado, Camara, CNN Brasil

Exemplos para testar:
- `cl_bolsonaro_governo_029` - Moro demissao interferencia PF (ESTABLISHED_FACT)
- `cl_bolsonaro_governo_074` - Minutas decreto golpista (ESTABLISHED_FACT)
- `cl_bolsonaro_governo_091` - Braga Netto preso (ESTABLISHED_FACT)

### Arquivos JSON Gerados
- `/data/s40_cases/covid19_brasil.json` (99 items)
- `/data/s40_cases/impeachment_dilma.json` (97 items)
- `/data/s40_cases/lava_jato.json` (96 items)
- `/data/s40_cases/inss_fraude.json` (94 items)
- `/data/s40_cases/bolsonaro_governo.json` (92 items)

### Bancos Populados
- `/out/databases/s25_truth.sqlite` - 478 truth records
- `/out/databases/decision_blocks.sqlite` - 478 decision blocks
- `/out/databases/s21_sources.sqlite` - 34 fontes registradas:
  - 6 government (CGU, Câmara, INSS, Planalto, Senado, TCU)
  - 6 health (Anvisa, CONASS, Fiocruz, Butantan, MS, OMS)
  - 9 legal (Conjur, MPF, PGR, PF, STF, STJ, TRF-1, TRF-4, TSE)
  - 10 news (Agência Brasil, BBC, CNN, Estadão, Folha, G1, Poder360, Reuters, UOL, newsdata.io)
  - 3 official (IBGE API, IBGE Portal, Valor Econômico)
- Evidence refs ancorados às fontes cadastradas

### Script de Ingestao
- `scripts/s40_ingest_json_cases.py` - Ingere todos os JSON de casos

---

## Como Testar

1. Acesse http://localhost:5173/admin/truth-twin
2. Digite um claim ID no campo de busca (ex: `cl_lava_jato_000`)
3. Clique em "Buscar"
4. Verifique:
   - Estado atual (TruthStateBadge)
   - Timeline de decisoes (Gate badges)
   - Painel de Proveniencia (Guias, Pilares, E40.5)
5. Clique em uma decisao para abrir o Inspector Modal

---

## Servicos em Execucao

```bash
# Backend (porta 8000)
INSPECTAH_ENV=development INSPECTAH_AUTH_DISABLED=true PYTHONPATH=. .venv/bin/python -m uvicorn inspectah.api:build_app --factory --host 0.0.0.0 --port 8000 --reload

# Frontend (porta 5173)
cd frontend/inspectah-ui && npm run dev
```

**Navegacao:** Menu Truth Twin adicionado em MainLayout.tsx

---

*Este documento serve como ancora de contexto para continuidade do trabalho.*
