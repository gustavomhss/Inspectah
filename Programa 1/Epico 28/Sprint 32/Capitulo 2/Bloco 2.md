# Inspectah — Sprint 32
## Capítulo 2 — Bloco 2
### Gates da Sprint 32 (S32_Gx_*) e Scorecards

> Este bloco detalha os **gates oficiais da Sprint 32** – o que cada um faz, como roda, o que gera e como se conecta aos estados-alvo SA32_x.

---

#### Visão geral dos gates

A S32 terá, no mínimo, os seguintes gates formais:

- **S32_G0_scope_and_baseline** — preparação da sprint (docs, filemap, scripts e estrutura mínima).  
- **S32_G1_models_and_invariants** — sanidade de modelos, migrações e invariantes estruturais do Truth-DB/Blocos.  
- **S32_G2_promotion_flows** — fluxo claim → blocos → estado de verdade.  
- **S32_G3_contestation_flows** — fluxo de contestação end-to-end.  
- **S32_G4_orr_and_bundle** — consolidação de estado, bundle de evidências e visão final para ORR.

Todos os gates seguem o padrão:  
- script em `bin/s32_gX_*.sh`;  
- scorecard JSON em `out/scorecards/S32_GX_*.json`;  
- evidências em `out/evidence/S32_GX_*/` quando fizer sentido.

---

#### G0 — S32_G0_scope_and_baseline

**Objetivo:** garantir que a Sprint 32 começa com o mínimo de estrutura e documentação em ordem.

**Script recomendado:** `bin/s32_g0_scope_and_baseline.sh`

**Checks típicos:**
- Docs da S32 presentes em `docs/`, no mínimo:  
  - `sprint_32_capitulo_1_contexto.md`  
  - `sprint_32_capitulo_2_gates_e_metricas.md`  
  - `sprint_32_capitulo_3_arquitetura_e_filemap.md`  
  - `sprint_32_capitulo_4_execucao_e_evidencias.md`  
  - `sprint_32_capitulo_5_orr_operacao_pos_sprint.md`  
  - `sprint_32_capitulo_6_learnings_e_anti_gaps.md`  
  - `sprint_32_capitulo_7_tasks.md`
- Scripts `bin/s32_g1_models_and_invariants.sh` até `bin/s32_g4_orr_and_bundle.sh` presentes (mesmo que em versão inicial).  
- Diretórios base `out/evidence/` e `out/scorecards/` existem.  
- Opcional: verificação simples se arquivos de código/truthdb esperados existem (`app/truthdb/models.py`, etc.).

**Saída esperada:**  
Scorecard JSON em `out/scorecards/S32_G0_scope_and_baseline.json`, contendo campos como:
```json
{
  "gate": "S32_G0_scope_and_baseline",
  "status": "PASS" | "FAIL",
  "docs_present": true,
  "scripts_present": true,
  "structure_ok": true,
  "notes": ["..."]
}
```

**Ligação com estados-alvo:**  
- Dá suporte indireto a **todos** os SA32_x, garantindo que a sprint não comece no caos.

---

#### G1 — S32_G1_models_and_invariants

**Objetivo:** validar o núcleo de dados do Truth-DB/Blocos e suas invariantes estruturais/lógicas.

**Script recomendado:** `bin/s32_g1_models_and_invariants.sh`

**Ações típicas do script:**
- Aplicar migrações em um banco de teste (ex.: `alembic upgrade head` ou equivalente).  
- Rodar testes de modelos e invariantes:  
  - `pytest tests/truthdb/test_models_and_invariants.py`  
  - (opcional) outros testes focados em integridade de schema.
- Opcional: rodar pequenos sanity checks de queries básicas (ex.: criar blocos fake, checar relações).

**Saída esperada:**  
Scorecard `out/scorecards/S32_G1_models_and_invariants.json`, por exemplo:
```json
{
  "gate": "S32_G1_models_and_invariants",
  "status": "PASS" | "FAIL",
  "migrations_ok": true,
  "tests_ok": true,
  "checked_invariants": [
    "no_orphan_fact_blocks",
    "no_orphan_decision_blocks",
    "history_is_monotonic",
    "final_states_require_decision_block"
  ],
  "warnings": ["..."]
}
```

**Evidências:**  
- Logs de migração e teste em `out/evidence/S32_G1_models_and_invariants/` (opcional, mas recomendado).

**Ligação com estados-alvo:**  
- Suporta diretamente **SA32_3** (invariantes em código) e, indiretamente, SA32_1/SA32_2.

---

#### G2 — S32_G2_promotion_flows

**Objetivo:** validar na prática o fluxo claim → blocos → estado de verdade para o tipo de claim prioritário.

**Script recomendado:** `bin/s32_g2_promotion_flows.sh`

**Ações típicas do script:**
- Preparar ambiente de teste:  
  - subir banco com schema S32;  
  - semear uma ou mais claims do tipo prioritário (via fixtures ou integração com Programa 2).  
- Invocar o `PromotionService` (ou rotas internas) para promover essas claims.  
- Verificar blocos criados e estados de verdade resultantes:  
  - consultar Truth-DB;  
  - checar vínculos entre FactBlock/EvidenceBlock/DecisionBlock.  
- Checar métricas mínimas de promoção:  
  - `truthdb_promotion_success_rate`;  
  - erros de fluxo, se houver.  
- Salvar evidências (dumps, logs) em `out/evidence/S32_G2_promotion_flows/`.

**Saída esperada:**  
Scorecard `out/scorecards/S32_G2_promotion_flows.json`, com algo como:
```json
{
  "gate": "S32_G2_promotion_flows",
  "status": "PASS" | "FAIL",
  "claims_tested": 10,
  "promotions_success": 10,
  "promotions_failed": 0,
  "error_breakdown": {},
  "metrics_sample": {
    "truthdb_promotion_success_rate": 1.0,
    "truthdb_flow_error_rate": 0.0
  },
  "notes": ["..."]
}
```

**Ligação com estados-alvo:**  
- É o gate central para **SA32_1** (fluxo claim → verdade) e ajuda a validar **SA32_4** (métricas) e **SA32_3** (invariantes no fluxo).

---

#### G3 — S32_G3_contestation_flows

**Objetivo:** validar o fluxo de contestação end-to-end, com trilha de auditoria.

**Script recomendado:** `bin/s32_g3_contestation_flows.sh`

**Ações típicas do script:**
- Garantir que existam estados de verdade de teste (via G2 ou fixtures).  
- Registrar uma ou mais contestações contra esses estados, usando a API/serviço real de contestação.  
- Disparar o fluxo de processamento (automatizado/stub de comitê).  
- Verificar:  
  - novos blocos criados (especialmente `DecisionBlock`);  
  - atualização de estado de verdade;  
  - manutenção do histórico anterior.  
- Checar métricas de contestação:  
  - `truthdb_contestation_rate`;  
  - erros de fluxo relacionados.
- Salvar evidências em `out/evidence/S32_G3_contestation_flows/`.

**Saída esperada:**  
Scorecard `out/scorecards/S32_G3_contestation_flows.json`, ex.:
```json
{
  "gate": "S32_G3_contestation_flows",
  "status": "PASS" | "FAIL",
  "contests_tested": 5,
  "contests_success": 5,
  "results_distribution": {
    "state_unchanged": 3,
    "state_changed": 2
  },
  "metrics_sample": {
    "truthdb_contestation_rate": 5,
    "truthdb_flow_error_rate": 0.0
  },
  "notes": ["..."]
}
```

**Ligação com estados-alvo:**  
- Gate principal para **SA32_2** (contestação v1 funcional).  
- Ajuda a validar **SA32_4** (observabilidade) e, parcialmente, **SA32_3** (invariantes na presença de contestação).

---

#### G4 — S32_G4_orr_and_bundle

**Objetivo:** consolidar a visão final da sprint, garantindo que:
- todos os gates anteriores foram executados;  
- o bundle de evidências existe e está íntegro;  
- há material suficiente para ORR e operação pós-sprint.

**Script recomendado:** `bin/s32_g4_orr_and_bundle.sh`

**Ações típicas do script:**
- Verificar se scorecards `S32_G0`–`S32_G3` existem e estão com `status = "PASS"` (ou, se houver `"WARN"`, isso está documentado).  
- Validar a presença de diretórios de evidências relevantes em `out/evidence/`.  
- Empacotar tudo em `out/bundles/inspectah_s32_evidence_bundle.zip` (scorecards, logs, dumps, README).  
- Gerar um resumo textual para o ORR.

**Saída esperada:**  
Scorecard `out/scorecards/S32_G4_orr_and_bundle.json`, ex.:
```json
{
  "gate": "S32_G4_orr_and_bundle",
  "status": "PASS" | "FAIL",
  "gates_status": {
    "S32_G0": "PASS",
    "S32_G1": "PASS",
    "S32_G2": "PASS",
    "S32_G3": "PASS"
  },
  "bundle_path": "out/bundles/inspectah_s32_evidence_bundle.zip",
  "bundle_integrity_ok": true,
  "notes": ["..."]
}
```

**Ligação com estados-alvo:**  
- Gate decisivo para **SA32_5** (bundle reexecutável).  
- Ponto de convergência para todos os demais SA32_x, pois depende da saúde dos gates anteriores.

---

#### Padrão esperado dos scorecards S32

Para manter consistência com sprints anteriores, todos os scorecards S32_x devem seguir alguns princípios:

- **Formato JSON bem definido** (sem campos soltos ou estrutura arbitrária).  
- Campos mínimos:  
  - `gate` (string);  
  - `status` ("PASS" | "FAIL" | opcionalmente "WARN");  
  - `timestamp` ou `run_id`;  
  - `details` e/ou campos específicos do gate.  
- Os scorecards devem ser versionados junto com o código, ou pelo menos arquivados em bundles reprodutíveis.

---

Este Bloco 2 do Capítulo 2 transforma os estados-alvo SA32_x em **gates concretos**, com scripts, scorecards e diretórios de evidências associados. No próximo bloco, as métricas e invariantes serão detalhadas como complementos desse sistema de validação.

