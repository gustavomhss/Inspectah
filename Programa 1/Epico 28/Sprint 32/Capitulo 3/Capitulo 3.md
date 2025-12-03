# Inspectah — Sprint 32  
## Capítulo 3 — Arquitetura & Filemap (Truth-DB, Sistema de Blocos & Contestação v1)

> Este capítulo traduz os estados‑alvo, gates, métricas e invariantes da S32 em **arquitetura concreta de código**: módulos, serviços, esquemas, testes, scripts e diretórios. É o mapa para o Codex trabalhar sem inventar moda.

---

### 3.1 Visão de alto nível da arquitetura na S32

A Sprint 32 atua principalmente em 4 frentes arquiteturais, todas encaixadas no monólito/backend já existente do Inspectah:

1. **Camada de Dados (Truth-DB & Blocos)**  
   - Modelos e migrações para `FactBlock`, `EvidenceBlock`, `DecisionBlock`, `TruthState` e vínculos com claims/casos.  
   - Invariantes estruturais garantidas por schema + lógica.

2. **Camada de Serviços & Fluxos (Promoção & Contestação)**  
   - Serviços responsáveis por:  
     - promover claims a blocos + estados de verdade (PromotionService);  
     - registrar e processar contestações (ContestationService).  
   - Orquestração dos fluxos `claim → blocos → estado` e `estado → contestação → novos blocos/estado`.

3. **Camada de Observabilidade & Métricas do Truth-DB**  
   - Emissão de métricas obrigatórias (`truthdb_promotion_success_rate`, `truthdb_contestation_rate`, `truthdb_flow_error_rate`, `truthdb_flow_latency_p95`).  
   - Logs de saúde dos fluxos, acoplados à stack do Programa 1.

4. **Camada de Validação & Evidências (Tests, Gates & Bundles)**  
   - Testes de modelos/invariantes/promoção/contestação.  
   - Scripts de gates S32_G0–G4.  
   - Estrutura de diretórios para evidências e bundles.

Arquiteturalmente, a S32 **não cria um subsistema isolado**; ela estende o backend existente com um núcleo de verdade/contestação que:
- conversa com o domínio de claims (Programa 2);  
- utiliza a infraestrutura de dados, logging e métricas do Programa 1;  
- prepara API/queries para futuros produtos do Programa 4.

---

### 3.2 Componentes principais da S32

#### 3.2.1 Modelos & Esquema (Truth-DB & Blocos)

Módulo central (exemplo): `app/truthdb/models.py`

Modelos mínimos esperados:

- **`FactBlock`**  
  - Representa uma afirmação factual derivada de uma claim.  
  - Campos essenciais (exemplos):  
    - `id` (PK);  
    - `claim_id` (FK para domínio de claims);  
    - `content_hash` (hash do conteúdo factual);  
    - `created_at`, `updated_at`.

- **`EvidenceBlock`**  
  - Representa evidências ligadas a uma claim/fato (links, documentos, trechos, etc.).  
  - Campos:  
    - `id`;  
    - `fact_block_id` (FK para `FactBlock`);  
    - `evidence_type` (ex.: `source_article`, `official_data`, etc.);  
    - `metadata` (JSON);  
    - `created_at`.

- **`DecisionBlock`**  
  - Representa a decisão tomada em relação a um fato/claim (promoção a verdade, rejeição, alteração após contestação).  
  - Campos:  
    - `id`;  
    - `fact_block_id` ou `truth_state_id`;  
    - `decision_type` (ex.: `promote_true`, `reject`, `update_after_contest`);  
    - `reasoning_summary` (texto resumido ou referência a artefato de reasoning);  
    - `created_at`.

- **`TruthState`**  
  - Estado de verdade atual para uma claim/fato.  
  - Campos:  
    - `id`;  
    - `claim_id` ou `fact_block_id`;  
    - `status` (ex.: `pending`, `provisionally_true`, `true`, `contested`, `rejected`);  
    - `current_decision_block_id` (FK obrigatória para estados finais);  
    - `created_at`, `updated_at`.

- **`ContestRecord`** (ou similar)  
  - Registro de uma contestação realizada.  
  - Campos:  
    - `id`;  
    - `truth_state_id` ou `claim_id`;  
    - `contested_by` (usuário/sistema);  
    - `reason` (texto resumido ou código de motivo);  
    - `processed_decision_block_id` (opcional, quando já houve decisão);  
    - `created_at`, `processed_at`.

Esses modelos suportam diretamente as invariantes da S32 (sem blocos órfãos, estados finais com DecisionBlock, histórico monotônico).

Migrações associadas: `migrations/versions/XXXX_s32_truthdb_blocks.py`.

---

#### 3.2.2 Serviços & Fluxos (PromotionService & ContestationService)

Módulo sugerido: `app/truthdb/services.py` (ou subdividido em múltiplos módulos, mantendo coesão).

- **`PromotionService`**  
  Responsável por:
  - receber uma claim (ou ID de claim) do tipo prioritário;  
  - construir/ligar `FactBlock` + `EvidenceBlock` relevantes;  
  - criar/atualizar `TruthState` correspondente;  
  - gerar um `DecisionBlock` quando há mudança de estado final;  
  - emitir métricas de promoção (sucesso/erro/latência).

  Funções típicas:
  - `promote_claim(claim_id: str) -> TruthState`  
  - `build_blocks_for_claim(claim) -> FactBlock, List[EvidenceBlock]`

- **`ContestationService`**  
  Responsável por:
  - registrar uma nova contestação (`ContestRecord`);  
  - orquestrar o fluxo de análise (automatizado/stub);  
  - decidir se mantém ou altera o estado de verdade;  
  - gerar novos `DecisionBlock` + atualizar `TruthState`;  
  - emitir métricas de contestação e erros.

  Funções típicas:
  - `register_contestation(truth_state_id: str, payload: ContestationInput) -> ContestRecord`  
  - `process_contestation(contest_id: str) -> DecisionBlock`

Esses serviços centralizam a lógica de negócio da S32, evitam duplicação em rotas/API e concentraram pontos de emissão de métricas.

---

#### 3.2.3 Observabilidade & Métricas

Módulo sugerido: `app/truthdb/metrics.py`

Responsabilidades:

- Expor funções utilitárias para registrar:
  - `inc_promotion_attempt(claim_type, env, source?)`  
  - `inc_promotion_success(claim_type, env, source?)`  
  - `inc_flow_error(stage, env, error_type)`  
  - `observe_flow_latency(flow_type, env, seconds)`  
  - `inc_contestation(claim_type/case_type, env, outcome?)`

- Internamente, usar o client de métricas padrão do projeto (Prometheus/OpenTelemetry).  
- Garantir que o código de serviços (`PromotionService`, `ContestationService`) **não repita** lógica de métrica – apenas chama funções de `metrics.py`.

---

#### 3.2.4 Testes

Diretório: `tests/truthdb/`

Arquivos mínimos:

- `test_models_and_invariants.py`  
  - Testa integridade de FKs, blocos órfãos, estados finais com DecisionBlock, histórico monotônico.

- `test_promotion_flows.py`  
  - Testa o fluxo claim → blocos → estado;  
  - Garante respeito às invariantes no contexto de promoção;  
  - Pode checar latência/métricas de forma indireta.

- `test_contestation_flows.py`  
  - Testa fluxo de contestação end-to-end;  
  - Verifica criação de `ContestRecord`, `DecisionBlock`, atualização de `TruthState` e preservação de histórico.

---

#### 3.2.5 Scripts de Gates & Bundles

Diretório: `bin/`

Scripts mínimos:

- `s32_g0_scope_and_baseline.sh`  
- `s32_g1_models_and_invariants.sh`  
- `s32_g2_promotion_flows.sh`  
- `s32_g3_contestation_flows.sh`  
- `s32_g4_orr_and_bundle.sh`

Diretórios de saída:

- Scorecards: `out/scorecards/S32_*.json`  
- Evidências: `out/evidence/S32_GX_*/`  
- Bundle: `out/bundles/inspectah_s32_evidence_bundle.zip`

---

### 3.3 Filemap detalhado da S32

Abaixo, um filemap orientado à Sprint 32 (apenas novos arquivos ou arquivos impactados diretamente):

```text
Inspectah/
  app/
    truthdb/
      __init__.py
      models.py                 # Modelos Truth-DB (FactBlock, EvidenceBlock, DecisionBlock, TruthState, ContestRecord)
      services.py               # PromotionService, ContestationService
      metrics.py                # Funções utilitárias de métricas do Truth-DB
      repositories.py           # (Opcional) abstrações de acesso a dados para blocos/estados

    claims/
      models.py                 # Modelos de claim já existentes (Programa 2)
      adapters_truthdb.py       # (Opcional) helpers de mapeamento claim → blocos

  migrations/
    versions/
      XXXX_s32_truthdb_blocks.py  # Migração criando/alterando tabelas para Truth-DB & Blocos

  tests/
    truthdb/
      __init__.py
      test_models_and_invariants.py
      test_promotion_flows.py
      test_contestation_flows.py

  bin/
    s32_g0_scope_and_baseline.sh
    s32_g1_models_and_invariants.sh
    s32_g2_promotion_flows.sh
    s32_g3_contestation_flows.sh
    s32_g4_orr_and_bundle.sh

  docs/
    sprint_32_capitulo_1_contexto.md
    sprint_32_capitulo_2_gates_e_metricas.md
    sprint_32_capitulo_3_arquitetura_e_filemap.md
    sprint_32_capitulo_4_execucao_e_evidencias.md
    sprint_32_capitulo_5_orr_operacao_pos_sprint.md
    sprint_32_capitulo_6_learnings_e_anti_gaps.md
    sprint_32_capitulo_7_tasks.md

  out/
    scorecards/
      S32_G0_scope_and_baseline.json
      S32_G1_models_and_invariants.json
      S32_G2_promotion_flows.json
      S32_G3_contestation_flows.json
      S32_G4_orr_and_bundle.json

    evidence/
      S32_G1_models_and_invariants/
      S32_G2_promotion_flows/
      S32_G3_contestation_flows/

    bundles/
      inspectah_s32_evidence_bundle.zip
```

Obs.: caminhos exatos podem ser ajustados para aderir 100% ao padrão já existente no repositório – mas a **estrutura lógica** deve permanecer equivalente.

---

### 3.4 Fluxos principais (com sequência de componentes)

#### 3.4.1 Fluxo 1 — claim → blocos → estado de verdade (SA32_1)

1. **Origem:** claim do tipo prioritário disponível em `app/claims/models.py`.  
2. **Chamada:** `PromotionService.promote_claim(claim_id)` (por tarefa interna, job ou endpoint).  
3. **Dentro do serviço:**  
   - Busca claim e valida tipo.  
   - Mapeia claim → estrutura factual (helpers em `claims/adapters_truthdb.py`, se existir).  
   - Cria/atualiza `FactBlock` + `EvidenceBlock`.  
   - Calcula novo estado de verdade (`TruthState.status`).  
   - Se estado for final ou alterado de forma significativa, cria `DecisionBlock` e vincula em `TruthState.current_decision_block_id`.  
   - Emite métricas de tentativa, sucesso, erro e latência.
4. **Persistência:** modelos em `app/truthdb/models.py` usando o ORM padrão do projeto.  
5. **Validação:** testes + gate `s32_g2_promotion_flows.sh`.

#### 3.4.2 Fluxo 2 — contestação → novos blocos → novo estado (SA32_2)

1. **Origem:** usuário/comitê/sistema decide contestar um estado de verdade (via UI futura ou ferramenta interna).  
2. **Chamada:** `ContestationService.register_contestation(truth_state_id, payload)`  
   - Cria `ContestRecord` pendente.  
   - Emite métrica `truthdb_contestation_rate`.
3. **Processamento:** `ContestationService.process_contestation(contest_id)`  
   - Carrega `ContestRecord` + `TruthState` + blocos relevantes.  
   - Aplica lógica de decisão (stub/heurística da S32).  
   - Cria novo `DecisionBlock` e, se necessário, atualiza `TruthState.status` e `current_decision_block_id`.  
   - Garante preservação do histórico (nenhum bloco apagado).  
   - Emite métricas de latência e erros.
4. **Validação:** testes `test_contestation_flows.py` + gate `s32_g3_contestation_flows.sh`.

---

### 3.5 Integrações & dependências com outros Programas

- **Programa 1 (Data Hub & Operação 24/7)**  
  - Reutilização da stack de logs e métricas (bibliotecas, exporters).  
  - Possível criação de healthchecks mínimos específicos para Truth-DB (Capítulo 5).

- **Programa 2 (Claims & Entidades)**  
  - Dependência forte do schema de claims para o tipo prioritário.  
  - Adaptações em `claims/adapters_truthdb.py` para mapear campos de claim para Fact/EvidenceBlocks.

- **Programa 4 (Produtos & Exposição)**  
  - A S32 expõe o núcleo, não endpoints públicos sofisticados – mas deve prever consultas internas que Programas futuros vão consumir (por exemplo, funções utilitárias em `repositories.py`).

---

### 3.6 Decisões arquiteturais explícitas da S32

1. **Truth-DB como módulo interno do backend**  
   Não criaremos um serviço separado nesta sprint; o Truth-DB vive como módulo interno, o que facilita reuso de infra de DB, métricas e testes.

2. **Serviços finos, não um “God Service”**  
   `PromotionService` e `ContestationService` devem ser pequenos, focados em orquestrar modelos/metrics/repos, não em virar monstros de lógica embutida.

3. **Separação clara entre modelo e métrica**  
   O domínio de blocos/estados não depende de métricas; elas são apenas observação. Por isso, métricas ficam em `metrics.py`.

4. **Testes como parte da arquitetura**  
   Dado o peso das invariantes da S32, os arquivos de teste `tests/truthdb/*` são tratados quase como parte do design, não “apêndice”.

5. **Filemap como contrato**  
   O filemap aqui descrito é contrato para o Codex: se a implementação divergir, deve haver justificativa clara no Capítulo 6.

---

Com este Capítulo 3, a Sprint 32 ganha um blueprint arquitetural claro: sabemos **onde** cada peça mora, **quem** faz o quê e **como** os fluxos centrais são montados. Capítulo 4 vai pegar essa arquitetura e transformá-la em plano de execução, linha do tempo e evidências faseadas.