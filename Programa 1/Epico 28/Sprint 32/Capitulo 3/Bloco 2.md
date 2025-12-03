# Inspectah — Sprint 32
## Capítulo 3 — Bloco 2
### Modelos & Esquema do Truth-DB (Blocos, Estados e Contestações)

> Este bloco detalha **como o Truth-DB é representado em modelos e migrações** na S32: quais tabelas existem, como se relacionam e como as invariantes do Capítulo 2 aparecem em nível de schema/ORM.

---

#### 3.2.1 Objetivos de design dos modelos S32

1. **Representar o Sistema de Blocos v2 de forma mínima, mas fiel**  
   - `FactBlock`, `EvidenceBlock`, `DecisionBlock`, `TruthState`, `ContestRecord` e relações necessárias.

2. **Permitir evolução futura sem refatoração destrutiva**  
   - Campos `metadata`/JSON em pontos estratégicos;  
   - separação entre núcleo estável (IDs, FKs, status) e anexos flexíveis.

3. **Embutir invariantes onde possível no próprio modelo**  
   - FKs obrigatórias;  
   - constraints simples (ex.: estados finais exigindo decisão);  
   - validações de domínio no nível ORM.

4. **Não conflitar com esquemas existentes de claims/casos**  
   - Usar FKs para tabelas de claims/casos definidas pelo Programa 2.  
   - Evitar redefinir entidades já existentes.

---

#### 3.2.2 Modelos principais

> Nomes de campos e tipos são ilustrativos; o Codex pode ajustar detalhes ao ORM/banco real (ex.: SQLAlchemy + Postgres) mantendo a estrutura lógica.

##### `FactBlock`

Representa um bloco factual, normalmente derivado de uma claim.

Campos sugeridos:
- `id` (PK, UUID ou bigint).  
- `claim_id` (FK → `claims.id`, obrigatório para evitar blocos órfãos).  
- `content_hash` (string) — hash canônico do conteúdo factual (para detectar duplicados).  
- `summary` (texto curto) — descrição humana do fato (opcional, mas útil).  
- `created_at`, `updated_at` (timestamps).  
- `metadata` (JSON) — para anexos leves.

Constraints / invariantes em nível de modelo:
- `claim_id` não nulo.  
- índice em (`claim_id`, `content_hash`) para consultas rápidas.

##### `EvidenceBlock`

Representa uma peça de evidência associada a um fato/claim.

Campos sugeridos:
- `id` (PK).  
- `fact_block_id` (FK → `fact_blocks.id`, obrigatório).  
- `evidence_type` (string curta; ex.: `source_article`, `official_data`, `expert_report`).  
- `uri` (string) — link ou identificador da evidência.  
- `metadata` (JSON) — detalhes (ex.: trecho citado, data da fonte, etc.).  
- `created_at`.

Constraints / invariantes:
- FK obrigatória em `fact_block_id` para evitar evidências órfãs.  
- índice em `fact_block_id`.

##### `TruthState`

Representa o estado de verdade atual (e histórico) associado a uma claim/fato.

Campos sugeridos:
- `id` (PK).  
- `claim_id` (FK → `claims.id`) **ou** `fact_block_id` (FK → `fact_blocks.id`) — o projeto pode escolher o vínculo primário; S32 assume uma das duas abordagens, documentada aqui.  
- `status` (enum/string limitada):  
  - `pending`, `provisionally_true`, `true`, `contested`, `rejected`, etc.  
- `current_decision_block_id` (FK → `decision_blocks.id`, **obrigatória para estados finais**).  
- `version` (int) — opcional, para controlar múltiplos registros de estado ao longo do tempo.  
- `created_at`, `updated_at`.  
- `metadata` (JSON).

Constraints / invariantes:
- Único em (`claim_id`, `version`) ou (`fact_block_id`, `version`).  
- Constraint (no código ou BD) garantindo que, se `status` ∈ {`true`, `rejected`, `debunked`}, então `current_decision_block_id` não é nulo.

##### `DecisionBlock`

Registra uma decisão tomada sobre um fato/estado (promoção, rejeição, reavaliação após contestação).

Campos sugeridos:
- `id` (PK).  
- `truth_state_id` (FK → `truth_states.id`, obrigatório).  
- `decision_type` (string curta):  
  - `promote_true`, `reject`, `update_after_contest`, etc.  
- `reasoning_summary` (texto) — descrição humana ou referência a reasoning mais detalhado.  
- `created_at`.  
- `metadata` (JSON) — possíveis anexos: ID de comitê, scores, etc.

Constraints / invariantes:
- FK obrigatória em `truth_state_id` (sem DecisionBlock órfão).  
- Índice em `truth_state_id`.

##### `ContestRecord`

Representa uma contestação registrada contra um estado de verdade.

Campos sugeridos:
- `id` (PK).  
- `truth_state_id` (FK → `truth_states.id`, obrigatório).  
- `contested_by` (string/UUID → usuário/sistema; pode ser FK para tabela de usuários).  
- `reason` (texto curto) — motivo da contestação.  
- `status` (enum/string): `pending`, `processed`, `dismissed`.  
- `processed_decision_block_id` (FK → `decision_blocks.id`, opcional, setado quando a contestação é processada).  
- `created_at`, `processed_at`.  
- `metadata` (JSON).

Constraints / invariantes:
- `truth_state_id` não nulo.  
- Se `status = 'processed'`, então `processed_decision_block_id` não nulo (verificado via validação de domínio/testes).

---

#### 3.2.3 Migrações associadas (S32)

Arquivo sugerido: `migrations/versions/XXXX_s32_truthdb_blocks.py`

Responsabilidades da migração:

1. Criar tabelas novas (se ainda não existirem):  
   - `fact_blocks`  
   - `evidence_blocks`  
   - `truth_states`  
   - `decision_blocks`  
   - `contest_records`

2. Adicionar índices e constraints relevantes:  
   - índices em FKs (`claim_id`, `fact_block_id`, `truth_state_id`);  
   - constraints únicas de versão (se aplicável);  
   - constraints simples para garantir integridade básica (sem FKs nulas onde não deveriam).

3. Garantir compatibilidade com dados existentes:  
   - se já houver tabelas de blocos em versão anterior, realizar migração incremental (rename/adicionar colunas) em vez de drop/recreate destrutivo;  
   - registrar em Capítulo 6 qualquer trade-off ou exceção.

A migração deve ser idempotente e testada via G1 (`s32_g1_models_and_invariants.sh`).

---

#### 3.2.4 Como os modelos reforçam as invariantes da S32

- **Invariante 1 — Nenhum bloco órfão**  
  - `FactBlock.claim_id` obrigatório;  
  - `EvidenceBlock.fact_block_id` obrigatório;  
  - `DecisionBlock.truth_state_id` obrigatório;  
  - `ContestRecord.truth_state_id` obrigatório.

- **Invariante 2 — Histórico monotônico**  
  - `TruthState` e `DecisionBlock` são apenas acrescidos; remoções/overwrites devem ser raras e, se existirem, controladas.  
  - Testes de fluxo (`test_contestation_flows.py`) garantem que contestações criam novos blocos em vez de apagar antigos.

- **Invariante 3 — Estados finais exigem DecisionBlock**  
  - Implementada como:  
    - validação em nível de modelo/serviço ao tentar persistir estado final sem `current_decision_block_id`;  
    - teste dedicado em `test_models_and_invariants.py`.

- **Invariante 4 — Referências cruzadas consistentes**  
  - Uso de FKs reais no banco;  
  - proibição de IDs “mágicos” sem constraint.

- **Invariante 5 — Migrações compatíveis**  
  - Migrações da S32 são escritas para subir do zero até schema atual sem quebrar dados pré-existentes, testadas em G1.

---

#### 3.2.5 Notas de implementação para o Codex

1. **ORM padrão do projeto**  
   - Seguir o mesmo padrão (ex.: SQLAlchemy + Alembic);  
   - manter naming conventions existentes (snake_case, pluralização, etc.).

2. **Enums vs strings**  
   - Se o projeto já usar enums concretos em banco para status, seguir o padrão;  
   - caso contrário, usar strings curtas mais validadas em código.

3. **Campos `metadata`**  
   - JSONB (se Postgres) é ideal para anexar extras sem migrar schema toda hora;  
   - usar com moderação, mantendo núcleo de domínio em colunas fortes.

4. **Documentação inline**  
   - Em `models.py`, comentários curtos explicando o papel de cada modelo/campo crítico ajudam a manter o design vivo.

Este Bloco 2 estabelece a espinha dorsal de dados do Truth-DB na S32. No próximo bloco, os serviços (Promotion/Contestation) vão usar esses modelos para implementar os fluxos SA32_1 e SA32_2 na prática.

