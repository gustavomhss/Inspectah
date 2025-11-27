### 3.3 – Modelos de dados e contratos (v2)

Este subcapítulo amarra, de forma operacional, a arquitetura lógica (3.1) e o filemap (3.2) naquilo que é mais crítico para o Inspectah: **como os dados são representados, armazenados e expostos, e quais contratos garantem que tudo isso permanece consistente ao longo do tempo**.

A partir daqui, qualquer pessoa da equipe (backend, frontend, dados, infra ou produto) deve ser capaz de:

- Desenhar à mão o modelo de dados da sprint (ER simplificado) sem inventar campos.
- Escrever um request **válido e completo** para qualquer endpoint crítico descrito na sprint.
- Entender, apenas lendo este subcapítulo, **como um fato entra como dado cru, passa por ingestão, interpretação, classificação, comitê/debunker e termina como registro de verdade auditável**.

> Notação: os nomes de entidades abaixo são alinhados com a linha S21–S25 (Fontes → Ingestão 2.0 → Cérebro/Comitês → Debunker v0 → Governança/Truth-DB). Em cada sprint específica, o Capítulo 3 deve especializar ou restringir a lista conforme o escopo daquela sprint.

---

### 3.3.1 – Objetivos e princípios de modelagem

Os modelos de dados e contratos desta sprint seguem quatro princípios não negociáveis:

1. **Clareza semântica**: cada entidade tem responsabilidade única e campo nenhum existe “por conveniência”. Se um campo não tem definição clara aqui, ele não entra no código.
2. **Auditabilidade total**: qualquer mudança importante (no mínimo: estado de ingestão, decisões de comitê, decisões de debunker, promoção/demissão de verdade) gera um rastro explícito, versionado e imutável.
3. **Contratos antes de implementação**: modelos que aparecem em fronteiras (APIs, eventos, filas, arquivos) são tratados como contratos. Mudanças são versionadas, nunca “editadas no escuro”.
4. **Invariantes explícitos**: regras de integridade não ficam implícitas “no código”: são descritas aqui, de forma textual, e cada uma é mapeada a testes, migrações ou verificações automáticas em gates/Gs da sprint.

---

### 3.3.2 – Mapa de entidades centrais da pipeline Inspectah

Abaixo, o mapa das entidades nucleares para o fluxo ponta‑a‑ponta (do dado cru até o registro de verdade). Cada sprint usará um recorte deste mapa.

#### 3.3.2.1 – Fonte e configuração de ingestão

**Source**  
Responsabilidade: representar **uma origem de informação** configurada no Inspectah (por exemplo, um feed RSS de jornal, um endpoint de dados oficiais, uma API de preços, etc.).

Campos principais (visão conceitual):
- `id` (UUID) – identificador estável da fonte dentro do Inspectah.
- `kind` (enum) – tipo de fonte: `NEWS_RSS`, `OPEN_DATA_API`, `FINANCIAL_API`, `CSV_UPLOAD`, etc.
- `name` (string) – nome legível interno (por exemplo, “Valor – Economia RSS”).
- `uri` (string) – URL/endpoint principal ou identificador de acesso.
- `config` (JSON) – parâmetros específicos (chaves de API, headers, parâmetros de paginação, padrões de parsing, etc.).
- `status` (enum) – `ACTIVE`, `PAUSED`, `DEPRECATED`.
- `created_at`, `updated_at` (timestamp) – trilha temporal.

Invariantes-chave:
- `uri` + `kind` devem ser únicos no escopo do sistema (não cadastrar duas fontes idênticas com nomes diferentes).
- `status = ACTIVE` exige uma configuração mínima válida (p. ex., campos obrigatórios em `config`).

**SourceHealthCheck**  
Responsabilidade: registrar resultados de **health checks** de uma fonte (latência, disponibilidade, erros recorrentes).

Campos principais:
- `id` (UUID).
- `source_id` (FK → Source.id).
- `timestamp` (timestamp) – quando o check foi feito.
- `status` (enum) – `UP`, `DEGRADED`, `DOWN`.
- `latency_ms` (int) – tempo de resposta da operação de teste.
- `error_code` (string, opcional) – código de erro de infra/HTTP.
- `details` (JSON) – metadados adicionais.

Invariantes:
- Cada registro é **append-only** (sem updates destrutivos); alterações são sempre novos registros.

**IngestionConfig**  
Responsabilidade: descrever **como** e **com qual frequência** uma fonte deve ser ingerida.

Campos principais:
- `id` (UUID).
- `source_id` (FK → Source.id).
- `schedule` (string) – expressão de cron, janela, ou política (ex.: “a cada 5 minutos”).
- `batch_size` (int) – quantos itens buscar por execução.
- `max_retries` (int) – tentativas em caso de falha.
- `parser_profile` (string) – identificador do parser a ser usado (por ex.: `NEWS_GENERIC_V1`).
- `enabled` (bool).

Invariantes:
- Uma `Source` pode ter 0…N `IngestionConfig`; cada `IngestionConfig` é exclusiva para uma combinação [source, schedule, parser_profile].

#### 3.3.2.2 – Execução de ingestão & itens

**IngestionRun**  
Responsabilidade: representar **uma execução concreta** do agendador de ingestão para uma dada configuração.

Campos principais:
- `id` (UUID).
- `ingestion_config_id` (FK → IngestionConfig.id).
- `started_at`, `finished_at` (timestamp).
- `status` (enum) – `RUNNING`, `SUCCESS`, `PARTIAL_SUCCESS`, `FAILED`.
- `items_fetched` (int).
- `items_stored` (int).
- `error_summary` (string/JSON, opcional).

Invariantes:
- `finished_at` ≥ `started_at` sempre que `status` ∈ {`SUCCESS`, `PARTIAL_SUCCESS`, `FAILED`}.
- Uma `IngestionRun` não pode ser reaberta: qualquer reprocessamento gera uma nova run.

**IngestionItemRaw**  
Responsabilidade: armazenar **o conteúdo cru** vindo da fonte, da forma mais próxima possível do que foi recebido (para auditoria e reprocessamento).

Campos principais:
- `id` (UUID).
- `ingestion_run_id` (FK → IngestionRun.id).
- `source_item_id` (string) – identificador nativo da fonte (ex.: GUID de RSS, ID de API).
- `payload_raw` (JSON/text) – conteúdo original (ou o envelope relevante extraído da resposta).
- `collected_at` (timestamp).

Invariantes:
- (`source_id`, `source_item_id`) devem ser únicos no sistema, evitando duplicar o mesmo item cru.

**IngestionItemNormalized**  
Responsabilidade: representar a versão **normalizada** de um item cru, já mapeado para um schema comum interno.

Campos principais:
- `id` (UUID).
- `raw_item_id` (FK → IngestionItemRaw.id).
- `normalized_kind` (enum) – `NEWS_ARTICLE`, `STATISTICAL_SERIES_POINT`, `PRICE_TICK`, etc.
- `title`, `summary`, `body` (strings, dependendo do tipo).
- `published_at` (timestamp, opcional).
- `entities_detected` (JSON) – rascunho de entidades básicas extraídas (pessoas, organizações, locais, etc.).
- `normalized_at` (timestamp).

Invariantes:
- Cada `IngestionItemRaw` tem 0 ou 1 `IngestionItemNormalized` (normalização idempotente).

#### 3.3.2.3 – Interpretação, classificação e claims

**InterpretationUnit**  
Responsabilidade: encapsular **um trecho interpretável** (por exemplo, um artigo, um parágrafo importante, um recorte de estatísticas) pronto para ser processado por agentes.

Campos principais:
- `id` (UUID).
- `normalized_item_id` (FK → IngestionItemNormalized.id).
- `text` (string) – texto consolidado a ser interpretado.
- `context` (JSON) – metadados relevantes (idioma, país, tópico, fonte, etc.).
- `created_at` (timestamp).

Invariantes:
- `text` não deve exceder o limite de tamanho definido para o agente daquela sprint (documentado no Cap. 2/Gates).

**ClassificationResult**  
Responsabilidade: guardar **o resultado da classificação automática** de uma `InterpretationUnit`.

Campos principais:
- `id` (UUID).
- `interpretation_unit_id` (FK → InterpretationUnit.id).
- `classifier_version` (string) – versão do agente/classificador.
- `labels` (JSON) – por exemplo: {"type":"NOTICIA", "topic":["ECONOMIA","INFLACAO"], ...}.
- `confidence_scores` (JSON) – probabilidades ou escores por label.
- `created_at` (timestamp).

Invariantes:
- Não pode existir mais de um `ClassificationResult` **ativo** por `InterpretationUnit` e `classifier_version`.

**Claim**  
Responsabilidade: representar **uma afirmação verificável** extraída da `InterpretationUnit` (por ex.: “A inflação em outubro foi de 4,5%”).

Campos principais:
- `id` (UUID).
- `interpretation_unit_id` (FK → InterpretationUnit.id).
- `text` (string) – frase da afirmação, de forma atômica e verificável.
- `context` (JSON) – informações estruturadas (datas, lugares, sujeitos, objetos, referência a entidades).
- `extracted_by_version` (string) – versão do agente de extração.
- `created_at` (timestamp).

Invariantes:
- Uma `Claim` deve ser sempre mapeável a pelo menos uma fonte original: via `interpretation_unit_id → normalized_item_id → raw_item_id → source_id`.

#### 3.3.2.4 – Evidências, comitês e debunker

**Evidence**  
Responsabilidade: representar **um pedaço de evidência** (por exemplo, link para documento oficial, trecho de dataset, imagem de gráfico) utilizado para corroborar ou refutar uma `Claim`.

Campos principais:
- `id` (UUID).
- `claim_id` (FK → Claim.id).
- `kind` (enum) – `OFFICIAL_DATASET`, `NEWS_ARTICLE`, `SCIENTIFIC_PAPER`, `GOVERNMENT_PORTAL`, etc.
- `uri` (string) – link ou identificador da evidência.
- `snippet` (string) – trecho relevante ou resumo.
- `metadata` (JSON) – detalhes adicionais (por exemplo, série temporal, país, unidade de medida).
- `collected_at` (timestamp).

Invariantes:
- `uri` deve ser resolvível ou replicável no vault interno (quando aplicável), para satisfazer o requisito de reprodutibilidade.

**CommitteeEvaluation**  
Responsabilidade: registrar **uma avaliação individual** de uma `Claim` por um membro (agente ou humano) do comitê.

Campos principais:
- `id` (UUID).
- `claim_id` (FK → Claim.id).
- `committee_member_id` (string) – identificador lógico do membro (ex.: `AGENT_INTERPRETER_V1`, `HUMAN_ANALYST_X`).
- `verdict` (enum) – `SUPPORTS`, `REFUTES`, `INCONCLUSIVE`, `OUT_OF_SCOPE`.
- `confidence` (float) – 0.0–1.0.
- `notes` (string) – justificativas.
- `created_at` (timestamp).

Invariantes:
- Um par (`claim_id`, `committee_member_id`) tem no máximo uma avaliação ativa por rodada de decisão.

**CommitteeDecision**  
Responsabilidade: consolidar **a decisão final de comitê** sobre uma `Claim`, após as avaliações individuais.

Campos principais:
- `id` (UUID).
- `claim_id` (FK → Claim.id).
- `version` (int) – versões da decisão ao longo do tempo.
- `final_verdict` (enum) – `TRUE`, `FALSE`, `UNDECIDED`, `CONTESTED`.
- `uncertainty_score` (float) – medida de incerteza agregada (por ex., baseada na dispersão de avaliações).
- `rationale` (string) – resumo estruturado da decisão.
- `created_at` (timestamp).

Invariantes:
- Para uma mesma `Claim`, a combinação (`version`, `created_at`) define uma linha do tempo de decisões; decisões antigas não são apagadas, apenas substituídas por versões novas.

**DebunkIssue**  
Responsabilidade: representar **uma contestação** aberta contra uma `Claim`, uma `CommitteeDecision` ou um `TruthRecord`.

Campos principais:
- `id` (UUID).
- `target_type` (enum) – `CLAIM`, `COMMITTEE_DECISION`, `TRUTH_RECORD`.
- `target_id` (UUID) – FK para o alvo correspondente.
- `status` (enum) – `OPEN`, `UNDER_REVIEW`, `RESOLVED`, `ESCALATED`.
- `opened_by` (string) – agente ou humano que abriu a contestação.
- `reason` (string) – descrição da contestação.
- `created_at`, `updated_at` (timestamp).

**DebunkTask**  
Responsabilidade: granularizar **as ações de debunker** a serem realizadas para uma `DebunkIssue`.

Campos principais:
- `id` (UUID).
- `debunk_issue_id` (FK → DebunkIssue.id).
- `assigned_to` (string) – agente/humano.
- `status` (enum) – `PENDING`, `IN_PROGRESS`, `DONE`, `CANCELLED`.
- `instructions` (string) – o que deve ser verificado.
- `result` (string/JSON) – achados.
- `created_at`, `updated_at` (timestamp).

Invariantes:
- Uma `DebunkIssue` só pode ser marcada `RESOLVED` quando **todas** as `DebunkTask` associadas estiverem em estado terminal (`DONE` ou `CANCELLED`).

#### 3.3.2.5 – Registros de verdade e histórico

**TruthRecord**  
Responsabilidade: representar **o estado atual da “verdade oficial”** de uma `Claim` dentro do Inspectah.

Campos principais:
- `id` (UUID).
- `claim_id` (FK → Claim.id).
- `current_state` (enum) – `CANDIDATE`, `FACT`, `REJECTED`, `RETIRED`.
- `committee_decision_id` (FK → CommitteeDecision.id) – decisão que suportou o estado atual.
- `effective_from` (timestamp).
- `effective_until` (timestamp, opcional) – preenchido quando o estado é substituído.

Invariantes:
- Para uma dada `Claim`, **apenas um** `TruthRecord` pode estar com `effective_until = NULL` em qualquer momento (estado atual).

**TruthChangeEvent**  
Responsabilidade: registrar **eventos de mudança de estado** de uma `Claim` na Truth-DB.

Campos principais:
- `id` (UUID).
- `truth_record_id` (FK → TruthRecord.id).
- `old_state`, `new_state` (enum).
- `reason` (string) – justificativa textual.
- `trigger_source` (enum) – `COMMITTEE`, `DEBUNKER`, `GOVERNANCE_POLICY`, etc.
- `created_at` (timestamp).

Invariantes:
- `TruthChangeEvent` é **append-only**; serve como trilha de auditoria e base para ancoragem futura em blockchain/Sistema de Blocos.

---

### 3.3.3 – Modelos em código (Pydantic/ORM) e organização

Os modelos conceituais acima são concretizados em duas famílias principais de classes:

1. **Modelos de persistência** (ORM – ex.: SQLModel, SQLAlchemy): mapeiam entidades para tabelas/índices.
2. **Modelos de contrato** (Pydantic/DTOs): definem o formato dos dados em fronteiras (APIs, filas, CLI, etc.).

Regras gerais:
- Cada entidade conceitual central (ex.: `Source`, `IngestionRun`, `Claim`, `TruthRecord`) deve possuir **um modelo ORM** e **um modelo Pydantic** (ou mais, quando houver variações de payload: request vs response) claramente documentados.
- Os nomes de classes seguem convenção clara: `SourceModel` (persistência), `SourceCreate`, `SourceRead`, `SourceUpdate` (contratos de API).
- Diferenças entre o que é armazenado e o que é exposto são **explícitas** aqui:
  - Ex.: campos internos de auditoria (`internal_notes`, `raw_debug`) podem existir no modelo ORM, mas nunca aparecer em `SourceRead`.

Exemplo de organização de arquivos (ajustar nomes conforme sprint):
- `app/models/source.py` – modelos ORM para `Source`, `SourceHealthCheck`, `IngestionConfig`.
- `app/models/ingestion.py` – ORM para `IngestionRun`, `IngestionItemRaw`, `IngestionItemNormalized`.
- `app/models/claims.py` – ORM para `InterpretationUnit`, `ClassificationResult`, `Claim`.
- `app/models/truth.py` – ORM para `Evidence`, `CommitteeEvaluation`, `CommitteeDecision`, `TruthRecord`, `TruthChangeEvent`.
- `app/schemas/source.py` – Pydantic para `SourceCreate`, `SourceRead`, etc.
- `app/schemas/ingestion.py`, `app/schemas/claims.py`, `app/schemas/truth.py` – análogos para os demais domínios.

Invariantes de organização:
- **Nenhum endpoint** deve expor diretamente instâncias de ORM; sempre passar por modelos Pydantic.
- Qualquer novo campo num modelo Pydantic que mude um contrato público deve ser refletido neste subcapítulo **antes** de ir para produção.

---

### 3.3.4 – Contratos de API síncronos

Esta seção documenta, em alto nível, os contratos de API REST (ou HTTP) críticos. O detalhamento linha a linha (OpenAPI/Swagger) é gerado automaticamente a partir dos modelos Pydantic, mas **a semântica** vive aqui.

Abaixo, um recorte típico para sprints S21–S25.

#### 3.3.4.1 – Administração de fontes

**POST `/admin/sources`** – cria uma nova `Source` + `IngestionConfig` básica.

Request (modelo `SourceCreate`):
- `kind` (enum) – obrigatório.
- `name` (string) – obrigatório.
- `uri` (string) – obrigatório.
- `config` (objeto) – opcional, mas pode ter campos obrigatórios por `kind`.
- `schedule` (string) – expressão de agendamento.

Response (modelo `SourceRead`):
- Dados da fonte criada, incluindo `id`, `status` inicial e configuração de ingestão associada.

Erros esperados:
- `400 BAD_REQUEST` – campos inválidos, `uri` duplicada para mesmo `kind`.
- `409 CONFLICT` – já existe fonte com `uri` e `kind` informados.

**GET `/admin/sources`** – lista fontes com filtros por `kind`, `status` e paginação.

Contrato de paginação padrão:
- Query params: `page`, `page_size` (limite máximo documentado no Cap. 2).
- Response inclui `items`, `total`, `page`, `page_size`.

#### 3.3.4.2 – Controle de ingestão

**POST `/admin/ingestions/{config_id}/run`** – dispara manualmente uma `IngestionRun`.

Request: vazio (ou parâmetros opcionais específicos da fonte).

Response: modelo `IngestionRunRead` com `id`, `status = RUNNING` e timestamps iniciais.

#### 3.3.4.3 – Consulta de claims e verdades

**GET `/truth/claims/{claim_id}`** – retorna visão consolidada de uma `Claim`.

Response (modelo `ClaimDetail`):
- Dados da claim (`text`, `context`, fonte).
- Lista de `Evidence` associadas (com `kind`, `uri`, `snippet`).
- Última `CommitteeDecision` (quando houver), com `final_verdict` e `uncertainty_score`.
- Estado atual na Truth‑DB (`TruthRecord.current_state`).

**GET `/truth/facts`** – busca `TruthRecord` filtrando por tópico, período ou entidades.

Parâmetros típicos:
- `entity_id`, `topic`, `from`, `to`, `state`.

#### 3.3.4.4 – Abertura de contestação (Debunker v0)

**POST `/debunker/issues`** – abre uma `DebunkIssue`.

Request (modelo `DebunkIssueCreate`):
- `target_type` – `CLAIM`, `COMMITTEE_DECISION` ou `TRUTH_RECORD`.
- `target_id` – ID correspondente.
- `reason` – texto explicando o problema.

Response: `DebunkIssueRead` com `id`, `status = OPEN`.

Erros:
- `404 NOT_FOUND` – target inexistente.
- `409 CONFLICT` – issue já aberta para o mesmo alvo dentro de uma janela configurada.

---

### 3.3.5 – Contratos assíncronos e eventos

Além das APIs síncronas, a sprint define eventos e mensagens trafegados via filas ou streams (por ex.: Kafka, Redis Streams, SQS). Estes contratos são tão importantes quanto os endpoints HTTP.

Eventos típicos:

1. `ingestion.item.normalized`  
   Payload mínimo:
   - `normalized_item_id` (UUID), `source_id`, `normalized_kind`, `published_at`.
   - `trace_id` – identificador de rastreio ponta‑a‑ponta.

2. `interpretation.unit.created`  
   - `interpretation_unit_id`, `normalized_item_id`, `trace_id`.

3. `claim.created`  
   - `claim_id`, `interpretation_unit_id`, `trace_id`.

4. `committee.decision.made`  
   - `committee_decision_id`, `claim_id`, `final_verdict`, `uncertainty_score`, `trace_id`.

5. `debunk.issue.opened`  
   - `debunk_issue_id`, `target_type`, `target_id`, `trace_id`.

6. `truth.state.changed`  
   - `truth_record_id`, `claim_id`, `old_state`, `new_state`, `trigger_source`, `trace_id`.

Regras contratuais para mensagens:
- Toda mensagem carrega `trace_id` permitindo reconstruir a jornada completa de um item ou claim.
- Campos obrigatórios e opcionais são congelados neste subcapítulo; extensões devem seguir política de versionamento (seção seguinte).
- Idempotência: qualquer consumidor deve poder reprocessar a mesma mensagem sem efeitos colaterais inconsistentes (uso de chaves naturais como (`claim_id`, `version`), etc.).

---

### 3.3.6 – Invariantes de dados e mapeamento para gates

Este subcapítulo também funciona como **lista oficial de invariantes** que os gates da sprint devem verificar.

Exemplos (ajustar conforme sprint específica):

1. Para toda `IngestionRun` com `status ∈ {SUCCESS, PARTIAL_SUCCESS, FAILED}` deve existir `finished_at` ≥ `started_at`.
2. Para toda `Claim` deve existir uma cadeia completa `Claim → InterpretationUnit → IngestionItemNormalized → IngestionItemRaw → Source`.
3. Para toda `TruthRecord` em vigor (`effective_until = NULL`), o estado deve estar em {`CANDIDATE`, `FACT`, `REJECTED`}.
4. Não pode existir mais de um `TruthRecord` em vigor por `Claim`.
5. Toda `CommitteeDecision` referenciada por `TruthRecord` deve ter pelo menos N `CommitteeEvaluation` (N definido no Cap. 2, tipicamente ≥ 3).
6. Uma `DebunkIssue` só pode ser `RESOLVED` se todas as `DebunkTask` associadas estiverem em estado terminal.

Cada uma dessas invariantes deve ser ligada, no Capítulo 2, a:
- Um conjunto de testes automatizados (unitários/integrados ou verificação de migrações).
- Scripts de sanity check (ex.: comandos que rodam queries de integridade no banco e falham o gate se houver violação).

---

### 3.3.7 – Versionamento, compatibilidade e migrações

Como o Inspectah é um sistema vivo, os modelos precisam suportar evolução sem quebrar confiança.

Regras gerais:
- **Contratos de API**: versionamento por caminho ou prefixo (ex.: `/v1/truth/facts`); alterações breaking exigem nova versão explícita.
- **Eventos**: qualquer mudança breaking no payload gera um novo `event_type` (por ex.: `truth.state.changed.v2`).
- **Banco de dados**: migrações são versionadas e descrevem não apenas a mudança estrutural, mas também as suposições de dados (ex.: “assumimos que não há registros com `status` nulo antes desta migração”).

Este subcapítulo deve listar, para a sprint em questão:
- Quais entidades ganharam novos campos.
- Quais APIs foram estendidas ou versionadas.
- Quais eventos tiveram seu payload alterado.

---

### 3.3.8 – Quadro de coerência final

Por fim, o 3.3 se fecha com uma visão de coerência cruzada entre:
- Entidades de domínio.
- Tabelas/coleções.
- Modelos de código (ORM e Pydantic).
- Endpoints HTTP.
- Eventos assíncronos.

Um exemplo de linha (a ser detalhada na sprint concreta):

- **Claim**  
  - Tabela: `claims`  
  - ORM: `ClaimModel` (`app/models/claims.py`)  
  - Schemas: `ClaimCreate`, `ClaimRead`, `ClaimDetail` (`app/schemas/claims.py`)  
  - APIs: `GET /truth/claims/{claim_id}`, `GET /truth/claims?filters...`  
  - Eventos: `claim.created`  
  - Invariantes principais: cadeia de origem completa, decisão de comitê versionada, mapeamento único para `TruthRecord`.

A expectativa é que, ao final, qualquer mudança em um desses elementos possa ser rastreada e verificada contra este quadro, evitando divergências silenciosas entre código, dados e contratos.

