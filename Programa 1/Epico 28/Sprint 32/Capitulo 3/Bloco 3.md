# Inspectah — Sprint 32
## Capítulo 3 — Bloco 3
### Serviços & Fluxos — PromotionService, ContestationService & Caminhos End‑to‑End

> Este bloco especifica **como os fluxos centrais da S32 são implementados em serviços**: promoção de claims a verdade e contestação de estados. É o passo intermediário entre os modelos (Bloco 2) e os gates/testes (Capítulo 4).

---

#### 3.3.1 Objetivos dos serviços da S32

1. **Encapsular a lógica de negócio de verdade/contestação em serviços coesos**  
   – nada de espalhar regras em rotas, handlers ou scripts.

2. **Fornecer pontos de entrada claros para jobs, APIs e testes**  
   – funções de serviço com assinaturas estáveis, fáceis de chamar em gates e testes.

3. **Centralizar a emissão de métricas e logs de fluxo**  
   – PromotionService e ContestationService são “pontos quentes” de observabilidade do Truth‑DB.

4. **Respeitar invariantes estruturais e de domínio**  
   – qualquer violação deve falhar de forma ruidosa (erro óbvio, teste quebrado, gate vermelho).

---

#### 3.3.2 Módulo de serviços — `app/truthdb/services.py`

Arquivo sugerido: `app/truthdb/services.py`

Conteúdo principal:
- Classe ou conjunto de funções para **Promoção de Claims**.  
- Classe ou conjunto de funções para **Contestação de Estados de Verdade**.  
- Opcionalmente, pequenas abstrações de repositório (se não estiverem em `repositories.py`).

---

#### 3.3.3 PromotionService — fluxo claim → blocos → estado de verdade (SA32_1)

**Responsabilidade:** pegar uma claim do tipo prioritário e:
- traduzi‑la em um ou mais `FactBlock` + `EvidenceBlock`;  
- criar/atualizar um `TruthState` coerente;  
- gerar `DecisionBlock` quando necessário;  
- emitir métricas e respeitar invariantes.

Interface sugerida:

```python
class PromotionService:
    def __init__(self, db_session, metrics_client):
        self.db = db_session
        self.metrics = metrics_client

    def promote_claim(self, claim_id: str) -> "TruthState":
        """Fluxo principal de promoção de uma claim do tipo prioritário.

        - Carrega claim do domínio Programa 2.
        - Verifica se é do tipo suportado pela S32.
        - Cria/atualiza FactBlock + EvidenceBlock.
        - Atualiza TruthState e, se necessário, cria DecisionBlock.
        - Emite métricas de tentativa, sucesso/erro e latência.
        """
        ...

    def _build_blocks_for_claim(self, claim) -> "FactBlock":
        """Extrai conteúdo factual da claim e cria/atualiza FactBlock (e, se for o caso, EvidenceBlocks)."""
        ...

    def _update_truth_state(self, fact_block, previous_state=None) -> "TruthState":
        """Calcula novo status de verdade, cria/atualiza TruthState e, se status final, gera DecisionBlock."""
        ...
```

Pontos importantes do fluxo `promote_claim`:

1. **Carga e validação de claim**  
   - `claim = claims_repository.get(claim_id)`  
   - Verificar se `claim.type` pertence ao conjunto suportado pela S32 (tipo prioritário).  
   - Em caso de tipo não suportado, falhar com erro explícito (e emitir métrica de erro).

2. **Construção/atualização de FactBlock/EvidenceBlock**  
   - `fact_block = self._build_blocks_for_claim(claim)`  
   - Pode usar helper em `claims/adapters_truthdb.py` para extrair conteúdo.

3. **Cálculo e persistência de TruthState**  
   - Buscar estado atual (se existir) para a claim/fato.  
   - Decidir novo `status` com base em regras definidas (p. ex., se há evidência mínima, se passou por comitês, etc. – versão v1 simples na S32).  
   - Criar ou atualizar `TruthState` respeitando invariantes (estado final exige DecisionBlock).

4. **Criação de DecisionBlock (quando aplicável)**  
   - Se o status for final (ex.: `true`, `rejected`), gerar `DecisionBlock` com `decision_type` apropriado.  
   - Preencher `reasoning_summary` de forma mínima (texto ou referência) e manter espaço para evolução futura.

5. **Emissão de métricas e logs**  
   - Antes de começar, registrar tentativa de promoção: `inc_promotion_attempt(claim_type, env, ...)`.  
   - Em caso de sucesso, `inc_promotion_success(...)`.  
   - Em caso de erro, `inc_flow_error(stage="promotion", ...)`.  
   - Medir latência total do fluxo (depois alimentar `truthdb_flow_latency_seconds` com `flow_type="promotion"`).

6. **Retorno**  
   - Retornar o `TruthState` final (ou relevante) para uso por chamadores e testes.

---

#### 3.3.4 ContestationService — fluxo contestação → novos blocos → novo estado (SA32_2)

**Responsabilidade:** registrar e processar contestações contra estados de verdade existentes, sem destruir histórico.

Interface sugerida:

```python
class ContestationService:
    def __init__(self, db_session, metrics_client):
        self.db = db_session
        self.metrics = metrics_client

    def register_contestation(self, truth_state_id: str, payload: "ContestationInput") -> "ContestRecord":
        """Cria um ContestRecord pendente para o TruthState especificado."""
        ...

    def process_contestation(self, contest_id: str) -> "DecisionBlock":
        """Processa uma contestação pendente e gera DecisionBlock (+ eventual atualização de TruthState)."""
        ...
```

Onde `ContestationInput` pode ser uma dataclass/objeto simples contendo:
- `contested_by`  
- `reason`  
- `metadata` (opcional)

Passos do fluxo `register_contestation`:

1. Carregar `TruthState` alvo.  
2. Validar que contestação é permitida para o status atual (ex.: pode não fazer sentido contestar algo já marcado como `rejected` por certa política).  
3. Criar `ContestRecord` com `status='pending'`.  
4. Emitir métrica `truthdb_contestation_rate` (contagem básica).  
5. Registrar logs mínimos (quem contestou, qual estado, motivo).  
6. Retornar `ContestRecord`.

Passos do fluxo `process_contestation`:

1. Carregar `ContestRecord` + `TruthState` + blocos relevantes (`FactBlock`, `DecisionBlock` atual, etc.).  
2. Verificar se ainda está `pending`; caso contrário, erro de uso.  
3. Aplicar lógica de decisão v1 (pode ser simples):  
   - e.g., manter ou alterar o estado de verdade com base em critérios fixos ou stub de comitê.  
4. Criar um novo `DecisionBlock` com `decision_type='update_after_contest'` (ou similar) e resumo da decisão.  
5. Atualizar `TruthState` se necessário:  
   - alterar `status` e `current_decision_block_id`;  
   - preservar histórico (nunca deletar blocos).  
6. Atualizar `ContestRecord.status` para `processed` e ligar `processed_decision_block_id`.  
7. Emitir métricas:  
   - `truthdb_contestation_rate` (se quiser segmentar outcomes);  
   - `truthdb_flow_error_rate` se algo falhar;  
   - latência de fluxo com `flow_type="contestation"`.  
8. Retornar o `DecisionBlock` criado.

A lógica v1 pode ser deliberadamente simples (ex.: sempre marcar estado como `contested` + logar para revisão humana), desde que todo o rastro em blocos/estados funcione.

---

#### 3.3.5 Fluxos end‑to‑end em texto

**Fluxo A — Promoção (claim → verdade)**

1. Claim chega pronta do Programa 2 (por job, endpoint interno ou tarefa assíncrona).  
2. Chamador invoca `PromotionService.promote_claim(claim_id)`.  
3. PromotionService:  
   - valida claim;  
   - cria/atualiza blocos;  
   - ajusta `TruthState` + `DecisionBlock` (se necessário);  
   - emite métricas;  
   - retorna `TruthState` final.
4. Tests + gate G2 verificam que:  
   - blocos estão consistentes;  
   - invariantes se mantêm;  
   - métricas foram emitidas;  
   - latência está em faixa aceitável.

**Fluxo B — Contestação (estado → contestação → novo estado)**

1. Alguém (usuário, comitê, job) decide contestar um estado de verdade.  
2. Chamador invoca `ContestationService.register_contestation(truth_state_id, payload)`.  
3. Service cria `ContestRecord` pendente, registra métrica e retorna.  
4. Em momento posterior (ou imediatamente), chamador invoca `ContestationService.process_contestation(contest_id)`.  
5. Service:  
   - carrega registro, estado e blocos;  
   - aplica lógica v1;  
   - cria `DecisionBlock`;  
   - atualiza `TruthState` (se for o caso);  
   - marca `ContestRecord` como processado;  
   - emite métricas e mede latência.  
6. Tests + gate G3 verificam consistência do fluxo: histórico monotônico, estados coerentes, métricas ativas.

---

#### 3.3.6 Integração dos serviços com métricas (`app/truthdb/metrics.py`)

Para não poluir serviços com detalhes de cliente de métricas, um módulo auxiliar expõe funções de alto nível, por exemplo:

```python
# app/truthdb/metrics.py

def inc_promotion_attempt(claim_type: str, env: str, source: str | None = None):
    ...

def inc_promotion_success(claim_type: str, env: str, source: str | None = None):
    ...


def inc_flow_error(stage: str, env: str, error_type: str | None = None):
    ...


def observe_flow_latency(flow_type: str, env: str, seconds: float):
    ...


def inc_contestation(claim_type: str, env: str, outcome: str | None = None):
    ...
```

PromotionService e ContestationService apenas chamam essas funções, mantendo o código de negócio limpo.

---

#### 3.3.7 Relação dos serviços com testes, gates e filemap

- **Testes:**  
  - `test_promotion_flows.py` foca em `PromotionService.promote_claim`.  
  - `test_contestation_flows.py` foca em `ContestationService.register_contestation` + `process_contestation`.

- **Gates:**  
  - `s32_g2_promotion_flows.sh` executa cenários reais em cima do `PromotionService`.  
  - `s32_g3_contestation_flows.sh` executa cenários reais em cima do `ContestationService`.

- **Filemap:**  
  - Serviços vivem em `app/truthdb/services.py`.  
  - Métricas em `app/truthdb/metrics.py`.  
  - Models & migrações em `app/truthdb/models.py` + `migrations/versions/XXXX_s32_truthdb_blocks.py`.

Este Bloco 3 amarra a camada de serviços da S32: especifica **como** o Truth‑DB é acionado para promover claims e processar contestações, com pontos claros para métricas, testes e gates. O próximo bloco do Capítulo 3 fecha o desenho com o filemap completo e notas finais de arquitetura.

