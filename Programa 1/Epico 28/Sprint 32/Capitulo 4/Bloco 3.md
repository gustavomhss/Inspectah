# Inspectah — Sprint 32
## Capítulo 4 — Bloco 3
### Fase 2 & Fase 3 — Fluxos de Promoção (G2) e Contestação (G3)

> Este bloco desdobra as Fases 2 e 3 da S32 em **plano de execução detalhado**: o que implementar, em que ordem, como validar, quais comandos rodar e quais evidências precisam existir para deixar G2 e G3 verdes.

---

#### 4.3.1 Fase 2 — Fluxo de Promoção (PromotionService & G2, SA32_1)

**Objetivo da Fase 2:** tornar funcional, com testes e evidências, o fluxo **claim → blocos → estado de verdade** para o tipo de claim prioritário definido no Capítulo 1.

##### 4.3.1.1 Passos de implementação

1. **Escolher/confirmar o tipo de claim prioritário**  
   - Verificar no domínio do Programa 2 qual tipo de claim será usado na S32 (ex.: `news_fact_simple`).  
   - Documentar essa escolha no Capítulo 1 e referenciar aqui (para evitar ambiguidade em testes e gates).

2. **Implementar helpers de mapeamento em `app/claims/adapters_truthdb.py`**  
   - Criar funções do tipo:
     - `extract_fact_from_claim(claim) -> dict` (conteúdo factual mínimo).  
     - `extract_evidence_from_claim(claim) -> list[dict]` (lista de evidências básicas).
   - Garantir que o adaptador lida, pelo menos, com:
     - campos obrigatórios (texto, entidades, data, fonte);  
     - casos de claim incompleta (lançar erro ou retornar algo explicitamente inválido).

3. **Implementar o `PromotionService` em `app/truthdb/services.py`**  
   - Métodos mínimos:

   ```python
   class PromotionService:
       def __init__(self, db_session, metrics_client):
           self.db = db_session
           self.metrics = metrics_client

       def promote_claim(self, claim_id: str) -> "TruthState":
           ...

       def _build_blocks_for_claim(self, claim) -> "FactBlock":
           ...

       def _update_truth_state(self, fact_block, previous_state=None) -> "TruthState":
           ...
   ```

   - Regras mínimas de negócio:
     - Falhar de forma clara se a claim não for do tipo suportado.  
     - Criar `FactBlock` vinculado à claim (sem blocos órfãos).  
     - Criar `EvidenceBlock`(s) básicos quando houver dados suficientes.  
     - Criar ou atualizar `TruthState` com um `status` consistente (ex.: `pending` → `provisionally_true` → `true` ou similar).  
     - Gerar `DecisionBlock` sempre que um estado final for atingido ou alterado, atualizando `current_decision_block_id`.

4. **Integrar métricas de promoção (`app/truthdb/metrics.py`)**  
   - Em `promote_claim`:
     - antes de começar, chamar `inc_promotion_attempt(claim_type, env, source?)`;  
     - em caso de sucesso, chamar `inc_promotion_success(...)`;  
     - em caso de erro que invalide o fluxo, chamar `inc_flow_error(stage="promotion", ...)`;  
     - medir o tempo total do fluxo e chamar `observe_flow_latency(flow_type="promotion", ...)`.

5. **Implementar testes de fluxo em `tests/truthdb/test_promotion_flows.py`**  
   - Casos mínimos:
     - promoção bem-sucedida de claim válida (cria Fact/EvidenceBlocks, TruthState e, se aplicável, DecisionBlock);  
     - tentativa de promoção de claim inválida ou de tipo errado (esperar erro claro, métricas de erro);  
     - verificação de invariantes no contexto de promoção (states finais exigem DecisionBlock, sem blocos órfãos).  
   - Sempre que possível, checar efeitos colaterais relevantes (ex.: número de blocos antes/depois).

##### 4.3.1.2 Gate G2 — `s32_g2_promotion_flows.sh`

**Responsabilidade do gate:** provar que o fluxo de promoção funciona de ponta a ponta, em ambiente de teste, com métricas e invariantes respeitadas.

Passos típicos do script (conceituais):

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

source .venv/bin/activate  # se aplicável

# 1) Preparar banco de teste (migrações já cobertas em G1, mas pode rodar novamente por segurança)
# ex.: alembic upgrade head

# 2) Semear claims de teste do tipo prioritário (via fixtures, script Python ou factory)
# ex.: python -m scripts.seed_s32_promotion_claims

# 3) Rodar testes de fluxo de promoção
pytest tests/truthdb/test_promotion_flows.py

# 4) Opcional: rodar script Python que chama PromotionService diretamente
#    para registrar métricas adicionais e salvar dumps em out/evidence

# 5) Gerar scorecard S32_G2_promotion_flows.json
python - << 'PY'
# Script inline: ler resultados, montar JSON de scorecard e salvar em out/scorecards/
PY
```

Conteúdo esperado no scorecard G2 (conceitual):

```json
{
  "gate": "S32_G2_promotion_flows",
  "status": "PASS",
  "claims_tested": 10,
  "promotions_success": 10,
  "promotions_failed": 0,
  "metrics_sample": {
    "truthdb_promotion_success_rate": 1.0,
    "truthdb_flow_error_rate": 0.0
  },
  "notes": []
}
```

##### 4.3.1.3 Critérios de saída da Fase 2

A Fase 2 está concluída quando:

1. `PromotionService` está implementado e coberto por testes (em `test_promotion_flows.py`).  
2. As métricas de promoção são emitidas em ambiente de teste (ao menos uma execução observada).  
3. O gate G2 (`s32_g2_promotion_flows.sh`) roda de ponta a ponta e gera `S32_G2_promotion_flows.json` com `status = "PASS"`.  
4. Invariantes da S32 continuam verdes (G1 não foi quebrado pela implementação da Fase 2).

Evidências mínimas:
- Scorecard G2.  
- Pasta `out/evidence/S32_G2_promotion_flows/` com logs, dumps de blocos/estados antes/depois de pelo menos um cenário representativo.

---

#### 4.3.2 Fase 3 — Fluxo de Contestação (ContestationService & G3, SA32_2)

**Objetivo da Fase 3:** tornar funcional o fluxo de **contestar estados de verdade**, processar essas contestações e atualizar o estado quando necessário, sempre preservando histórico.

##### 4.3.2.1 Pré-requisitos da Fase 3

- Fase 2 concluída com G2 verde (é necessário ter estados de verdade criados via PromotionService).  
- Migrações e modelos de `ContestRecord`, `TruthState` e `DecisionBlock` estáveis.

##### 4.3.2.2 Passos de implementação

1. **Implementar/ajustar `ContestRecord` em `app/truthdb/models.py`**  
   - Confirmar campos: `truth_state_id`, `contested_by`, `reason`, `status`, `processed_decision_block_id`, timestamps, `metadata`.  
   - Garantir FKs obrigatórias e índices básicos.

2. **Implementar o `ContestationService` em `app/truthdb/services.py`**  
   - Métodos mínimos:

   ```python
   class ContestationService:
       def __init__(self, db_session, metrics_client):
           self.db = db_session
           self.metrics = metrics_client

       def register_contestation(self, truth_state_id: str, payload: "ContestationInput") -> "ContestRecord":
           ...

       def process_contestation(self, contest_id: str) -> "DecisionBlock":
           ...
   ```

   - Regras mínimas de negócio em `register_contestation`:
     - Verificar se `TruthState` existe e é contestável.  
     - Criar `ContestRecord` com `status='pending'`.  
     - Emitir `truthdb_contestation_rate` (contador básico).  
     - Registrar logs mínimos (quem contestou, qual estado, motivo).

   - Regras mínimas em `process_contestation`:
     - Carregar `ContestRecord` + `TruthState` + blocos relacionados.  
     - Validar que a contestação ainda está `pending`.  
     - Aplicar lógica v1 (pode ser simples, ex.: marcar estado como `contested` e criar um `DecisionBlock` de revisão).  
     - Preservar histórico (nunca deletar blocos);  
     - Atualizar `TruthState` se aplicável (novo status, novo `current_decision_block_id`).  
     - Atualizar `ContestRecord.status` para `processed` e setar `processed_decision_block_id`.  
     - Emitir métricas de latência e erros.

3. **Integrar métricas de contestação (`metrics.py`)**  
   - Em `register_contestation`:  
     - incrementar `truthdb_contestation_rate` com labels adequados.  
   - Em `process_contestation`:  
     - medir e registrar `truthdb_flow_latency_p95` (via histograma de latências);  
     - registrar erros em `truthdb_flow_error_rate` quando algo falhar.

4. **Implementar testes de fluxo em `tests/truthdb/test_contestation_flows.py`**  
   - Casos mínimos:
     - contestação simples:  
       - criar TruthState via PromotionService;  
       - registrar contestação;  
       - processar contestação;  
       - verificar criação de novo `DecisionBlock` e preservação de blocos anteriores.  
     - contestação em estado inválido (ex.: state que não aceita contestação): deve falhar claramente.  
     - verificação de que `ContestRecord.status` e `processed_decision_block_id` são atualizados corretamente.

##### 4.3.2.3 Gate G3 — `s32_g3_contestation_flows.sh`

**Responsabilidade do gate:** comprovar que a contestação funciona de ponta a ponta, do registro até a decisão, com histórico preservado.

Passos típicos do script (conceituais):

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

source .venv/bin/activate  # se aplicável

# 1) Preparar banco de teste (migrações +, se necessário, rodar G1/G2 antes)

# 2) Criar estados de verdade de teste (via PromotionService ou fixtures)

# 3) Rodar testes de fluxo de contestação
pytest tests/truthdb/test_contestation_flows.py

# 4) Opcional: rodar script Python para registrar e processar contestações
#    em lote e salvar evidências adicionais

# 5) Gerar scorecard S32_G3_contestation_flows.json
python - << 'PY'
# Script inline para consolidar resultados e gerar scorecard
PY
```

Conteúdo esperado no scorecard G3 (conceitual):

```json
{
  "gate": "S32_G3_contestation_flows",
  "status": "PASS",
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
  "notes": []
}
```

##### 4.3.2.4 Critérios de saída da Fase 3

A Fase 3 está concluída quando:

1. `ContestationService` está implementado e coberto por testes (em `test_contestation_flows.py`).  
2. As métricas de contestação e de latência de fluxo são emitidas em ambiente de teste e podem ser visualizadas (ao menos via endpoint de métricas/logs).  
3. O gate G3 (`s32_g3_contestation_flows.sh`) roda de ponta a ponta e gera `S32_G3_contestation_flows.json` com `status = "PASS"`.  
4. Invariantes da S32 permanecem verdes (especialmente histórico monotônico e estados finais com DecisionBlock).

Evidências mínimas:
- Scorecard G3.  
- Pasta `out/evidence/S32_G3_contestation_flows/` com logs, dumps de estados antes/depois de contestações representativas.

---

#### 4.3.3 Amarração entre Fase 2 e Fase 3

- A Fase 2 produz **TruthStates saudáveis** e blocos associados, que servem de base para a Fase 3.  
- A Fase 3 prova que **nenhum estado de verdade é definitivo** sem a possibilidade de contestação, e que tal contestação é rastreável.  
- G2 e G3, verdes em conjunto, são a evidência de que a S32 entregou um Truth-DB não só capaz de promover verdades, mas também de revisá-las — sem quebrar o histórico.

Nos próximos blocos do Capítulo 4, a execução será concluída com a Fase 4 (sanidade cruzada, regressões, G4 e bundle) e o amarramento final de evidências para ORR e operação pós-sprint.

