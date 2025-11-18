# Inspectah – Sprint 8 (Capítulo 3)
## Arquitetura, Filemap e Contratos Técnicos orientados aos Gates (v2)

---

### 0. One‑liner oficial do Capítulo 3

> **“O Capítulo 3 da Sprint 8 define a arquitetura, o filemap e os contratos técnicos – entre módulos, handlers e storage – que o Codex deve seguir para que todos os gates T0–T8 (Cap. 2) sejam atingíveis sem gambiarras, garantindo Admin v0, Usuário v0 e o fluxo Inspectah → Evidências → GPT → Resposta como um sistema coeso e extensível para Truth‑DB e blockchain.”**

Este capítulo não é sobre execução (Cap. 4), e sim sobre **forma e contratos**:

- como o código deve ser organizado (camadas, pastas, módulos)
- quais interfaces cada módulo expõe (pré/pós‑condições)
- como a UI conversa com o core e com o GPT
- onde os dados vivem (storage lógico) e como isso prepara o terreno para S10–S12

---

### 1. Papel do Capítulo 3 na Sprint 8

O Cap. 3 é o elo entre:

- **Cap. 1** – visão de produto, objetivos, DoD
- **Cap. 2** – gates T0–T8, evidências, scorecards

Ele responde, tecnicamente:

- onde cada parte da visão mora no código
- quais arquivos e módulos o Codex deve criar ou alterar
- como cada gate enxerga o sistema (quais módulos e artefatos toca)

Sem esse capítulo, os gates poderiam virar scripts soltos em cima de um código amorfo. Com ele, a Sprint 8 tem uma arquitetura mínima, explícita, **orientada a gates**.

---

### 2. Visão geral da arquitetura da Sprint 8

A arquitetura da S8 se organiza em quatro camadas principais, mais duas camadas transversais:

1. **Camada Admin (`app/admin/`)**
   - Cadastro e manutenção de fontes (Source)
   - Seleção de campos relevantes (SourceConfig.selected_fields)
   - Visualização básica de status de ingestão (SourceStatus)

2. **Camada Usuário (`app/user/`)**
   - Input de pergunta em linguagem natural
   - Chamada ao pipeline core
   - Exibição de resposta do GPT (texto + resumo estruturado)
   - Link para evidências (bundle + itens)

3. **Camada Core (`app/core/`)**
   - Parsing de perguntas (sem LLM)
   - Busca interna em fontes/itens
   - Montagem de evidence bundles
   - Orquestração do fluxo Inspectah → Evidências → GPT → Resposta
   - Logging de queries e evidências

4. **Camada GPT Client (`app/gpt_client/`)**
   - Wrapper único para chamadas ao modelo
   - Aplicação dos templates rígidos de prompt (verdade local, anti‑alucinação)

Camadas transversais:

- **Gates e CI (`bin/`, `.github/workflows/`)**
  - scripts `bin/s8_t*.sh`, `bin/s8_ci.sh`
- **Testes, fixtures e goldens (`tests/`)**
  - suites por gate, dados de exemplo, goldens dos 3 roteiros
- **Evidências e logs (`out/`)**
  - pastas por gate, bundles, queries, scorecards

Cada gate do Cap. 2 enxerga um recorte dessa arquitetura; o Cap. 3 explicita essas relações seção a seção.

---

### 3. Filemap macro da Sprint 8

Estrutura proposta em alto nível:

- `docs/`
  - `sprint_8_capitulo_1.md`  
  - `sprint_8_capitulo_2_gates.md`  
  - `sprint_8_capitulo_3_arquitetura.md`  
  - `sprint_8_cenarios_demo.md`
- `app/`
  - `admin/`
    - `__init__.py`
    - `routes.py`            (handlers/rotas Admin)
    - `schemas.py`           (DTOs Admin)
    - `service.py`           (lógica de fontes)
  - `user/`
    - `__init__.py`
    - `routes.py`            (handlers/rotas Usuário)
    - `schemas.py`           (DTOs de input/output)
    - `view_models.py`       (modelos para UI/resumo)
  - `core/`
    - `__init__.py`
    - `models.py`            (Source, Item, EvidenceBundle, QueryLog)
    - `query_parser.py`      (classificação e extração de sinais)
    - `search_internal.py`   (busca em fontes/itens)
    - `evidence_bundle_builder.py` (montagem de bundles)
    - `pipeline.py`          (orquestração pergunta→resposta)
    - `storage.py`           (abstrações de persistência S8)
  - `gpt_client/`
    - `__init__.py`
    - `client.py`           (função única para chamar GPT)
    - `prompts.py`          (templates de prompt da Sprint 8)
- `tests/`
  - `s8_t2_unit_contracts/`
  - `s8_t3_property/`
  - `s8_t4_golden_flows/`
  - `fixtures/`
    - `s8_preco_medio/…`
    - `s8_comparacao/…`
    - `s8_checagem_factual/…`
  - `goldens/`
    - `s8_preco_medio.json`
    - `s8_comparacao_simples.json`
    - `s8_checagem_factual.json`
- `bin/`
  - `s8_t0_scope_and_alignment.sh`
  - `s8_t1_static_quality.sh`
  - `s8_t2_unit_and_contracts.sh`
  - `s8_t3_property_and_edge_cases.sh`
  - `s8_t4_golden_flows.sh`
  - `s8_t5_perf_and_limits.sh`
  - `s8_t6_logs_and_evidence.sh`
  - `s8_t7_ci_pipeline.sh`
  - `s8_t8_go_no_go.sh`
  - `s8_ci.sh`               (agregador T1–T6)
  - `s8_demo.sh`             (script auxiliar de demo manual)
- `out/`
  - `evidence/`
    - `S8_T0_scope/…`
    - `S8_T1_static/…`
    - `S8_T2_unit_contracts/…`
    - `S8_T3_property/…`
    - `S8_T4_golden_flows/…`
    - `S8_T5_perf/…`
    - `S8_T6_logs_evidence/…`
    - `S8_T7_ci/…`
    - `S8_T8_go_no_go/…`
    - `s8_queries/…`
    - `s8_bundles/…`
    - `s8_responses/…`
  - `scorecards/`
    - `S8_T0_scope.json`
    - …
    - `S8_T8_go_no_go.json`

Esse filemap é o esqueleto que o Cap. 4 materializa com código concreto.

---

### 4. Modelos de domínio mínimos (app/core/models.py)

A S8 não implementa a Truth‑DB completa, mas já precisa de modelos compatíveis com o futuro (S10–S12). Os modelos abaixo são projetados como **subconjunto natural** dos modelos de Truth‑DB:

1. `Source`
   - `id: str`
   - `name: str`
   - `type: Literal["precos_api_simples", "noticias_rss_simplificado", ...]`
   - `config: SourceConfig`
   - `status: SourceStatus`

2. `SourceConfig`
   - `url_base: str`
   - `auth_token: Optional[str]`
   - `params: dict[str, Any]`
   - `selected_fields: list[str]`

3. `SourceStatus`
   - `last_fetch_at: Optional[datetime]`
   - `last_fetch_status: Literal["ok", "erro"]`
   - `last_fetch_error: Optional[str]`
   - `recent_items_count: int`

4. `Item`
   - `id: str`
   - `source_id: str`
   - `payload: dict[str, Any]`
   - `created_at: datetime`

5. `EvidenceItemRef`
   - `item_id: str`
   - `source_id: str`
   - `key_fields: dict[str, Any]`

6. `EvidenceBundle`
   - `id: str`  
   - `query_type: str`
   - `query_filters: dict[str, Any]`
   - `items_by_source: dict[str, list[EvidenceItemRef]]`
   - `manifest_paths: dict[str, str]`

7. `QueryLog`
   - `query_id: str`
   - `user_query: str`
   - `query_type: str`
   - `evidence_bundle_id: str`
   - `sources: list[str]`
   - `items_used: list[str]`
   - `gpt_response_ref: str`
   - `timestamp: datetime`
   - `status: Literal["ok", "dados_insuficientes", "erro", "fora_de_escopo"]`
   - `error_code: Optional[str]`

**Compatibilidade futura (S10–S12)**

- `Item` é candidato natural a virar **evento bruto** que alimenta blocos/fatos.
- `EvidenceBundle` será a "janela" de evidências usada pelo **Guardião de Blocos** na S10.
- `QueryLog` já nasce preparado para referenciar, futuramente, IDs de bloco/fato/versão, sem refatoração destrutiva (basta adicionar campos como `block_id`, `fact_id`).

---

### 5. Contratos de módulo – Core (Design by Contract)

#### 5.1. `query_parser.py`

Função principal sugerida:

```python
def parse_query(user_query: str) -> ParsedQuery: ...
```

Pré‑condições

- `user_query` não é vazio
- idioma é suportado (PT/EN) ou há fallback claro

Pós‑condições

- `ParsedQuery.query_type` ∈ {`"agregacao_simples"`, `"comparacao_simples"`, `"checagem_factual_simples"`, `"fora_de_escopo"`}
- se `query_type != "fora_de_escopo"`, então pelo menos uma entidade chave foi extraída (ex.: `produto` ou `pessoa`)

#### 5.2. `search_internal.py`

Função principal:

```python
def search_internal(parsed: ParsedQuery) -> list[Item]: ...
```

Pré‑condições

- `parsed.query_type` ∈ tipos suportados

Pós‑condições

- retorno é lista de `Item` (possivelmente vazia)
- todos os `Item.source_id` retornados existem em `Source`

#### 5.3. `evidence_bundle_builder.py`

Função principal:

```python
def build_evidence_bundle(parsed: ParsedQuery, items: list[Item]) -> EvidenceBundle: ...
```

Pré‑condições

- `items` contém apenas itens de fontes conhecidas

Pós‑condições

- `EvidenceBundle.id` não é vazio
- `EvidenceBundle.query_type == parsed.query_type`
- `len(items_by_source[source_id]) <= N_max_por_fonte`
- bundle persistido em `out/evidence/s8_bundles/<id>.json`

#### 5.4. `pipeline.py`

Interface sugerida:

```python
def run_pipeline(user_query: str) -> UserResponse: ...
```

Pré‑condições

- `user_query` não é vazio

Pós‑condições de sucesso (`UserResponse.status == "ok"`)

- foi criado um `EvidenceBundle` com ID não vazio
- existe registro de `QueryLog` para essa query
- os dados de `UserResponse.summary` são coerentes com o bundle (contagem de fontes/itens)

Pós‑condições de falha controlada (`status != "ok"`)

- existe `QueryLog` com `status` consistente (ex.: `"dados_insuficientes"`, `"fora_de_escopo"`)
- o usuário recebe mensagem clara sobre o tipo de falha

Esses contratos são o que T2/T3 validam diretamente.

---

### 6. Contratos de API/Handler – Camada Admin (app/admin)

Sem fixar framework, os handlers devem seguir contratos lógicos claros.

1. `POST /admin/sources`

Entrada

- `name: str`
- `type: str`
- `url_base: str`
- `auth_token: Optional[str>`
- `params: dict`
- `selected_fields: list[str]`

Pré‑condições

- `type` é um dos tipos válidos da S8
- `selected_fields` não é vazio

Saída

- `source_id: str`
- eco dos campos principais

Pós‑condições

- existe um `Source` persistido com esse `source_id`

2. `POST /admin/sources/{source_id}/test`

Saída

- `ok: bool`
- `sample_items: list[dict]`
- `error: Optional[str]`

Pós‑condições

- se `ok == True`, então `sample_items` contém de 1 a 5 exemplos
- se `ok == False`, `error` contém ao menos uma mensagem mínima

3. `GET /admin/sources/{source_id}/status`

Saída

- `last_fetch_at`
- `last_fetch_status`
- `last_fetch_error`
- `recent_items_count`

Esses contratos são usados por T2/T3 (via fixtures) e por T4/T6 indiretamente pelos cenários de demo.

---

### 7. Contratos de API/Handler – Camada Usuário (app/user)

Endpoint principal: `POST /user/query`

Entrada

- `query: str`

Pré‑condições

- `query` não é vazio

Saída

- `query_id: str`
- `answer_text: str`
- `summary` com
  - `query_type: str`
  - `main_value: Any`
  - `range_or_details: Optional[dict]`
  - `time_window: Optional[str]`
  - `sources_count: int`
  - `items_count: int`
- `evidence` com
  - `evidence_bundle_id: str`
  - `sources: list[str]`
  - `items_preview: list[dict]`
- `status: str` (ex.: `"ok"`, `"dados_insuficientes"`, `"fora_de_escopo"`)

Pós‑condições

- há um registro de `QueryLog` cujo `query_id` coincide
- para `status == "ok"`, `sources_count` e `items_count` são coerentes com o bundle

Esse contrato é a base de T4/T5/T6 (demos, performance, rastreabilidade).

---

### 8. Experiência de UI & Demos ligada à arquitetura

Para reduzir atrito entre doc e experiência real, a S8 prevê três "telas" (podem ser páginas simples ou componentes):

1. **Admin – Lista de fontes**
   - lista `Source` com nome, tipo, `last_fetch_status`, `recent_items_count`
   - botão "Testar" chamando `/admin/sources/{id}/test`

2. **Admin – Detalhe de fonte**
   - formulário de edição de `SourceConfig`
   - seleção de `selected_fields`
   - área de preview dos últimos itens (usando `Item.payload`)

3. **Usuário – Console de pergunta**
   - input de `query`
   - área de `answer_text`
   - card de `summary`
   - link "Ver evidências" abrindo uma visão dos itens (pelo `evidence_bundle_id`)

Relação com gates

- T4 garante que os três cenários oficiais funcionam **mesmo se a UI for mínima** (via API).
- Cap. 4 pode implementar a UI como um front simples em cima das rotas definidas aqui; não há dependência de framework específico.

---

### 9. GPT Client e Prompts (app/gpt_client)

Ponto único de entrada:

```python
def run_query(bundle: EvidenceBundle, user_query: str, query_type: str) -> GptAnswer: ...
```

Contratos

- Pré
  - `bundle` contém ao menos a estrutura mínima exigida (ver Cap. 1/2)
- Pós
  - `GptAnswer.answer_text` nunca é vazio
  - `GptAnswer.summary_structured` contém
    - `query_type`
    - `main_value` quando aplicável
    - flags de confiança/limite de dados

`prompts.py` inclui templates com:

- instrução de que **apenas o evidence bundle é verdade**
- proibição explícita de buscar conhecimento externo
- como marcar "não sei", conflito, fora de escopo

T4/T5 exercitam esse módulo com dados realistas (fixtures) e T6 verifica se as respostas ficam devidamente logadas.

---

### 10. Organização de testes e fixtures (tests/)

A árvore de testes é pensada para bater diretamente nos gates:

- `tests/s8_t2_unit_contracts/`
  - testes unitários de `query_parser`, `search_internal`, `evidence_bundle_builder`
- `tests/s8_t3_property/`
  - cenários adversos (dados insuficientes, conflitos, fora de escopo)
- `tests/s8_t4_golden_flows/`
  - fluxos completos dos 3 cenários oficiais usando fixtures e, idealmente, GPT real/mocked
- `tests/fixtures/`
  - conjuntos de dados coerentes com cada cenário
- `tests/goldens/`
  - snapshots esperados para cada fluxo, em formato JSON

Essa organização permite que os scripts `bin/s8_t2*.sh`, `bin/s8_t3*.sh`, `bin/s8_t4*.sh` chamem `pytest` em diretórios específicos, como descrito no Cap. 2.

---

### 11. Camada de storage e persistência (app/core/storage.py)

A S8 não fixa tecnologia (arquivo vs DB), mas define um **modelo lógico** – qualquer implementação concreta em Cap. 4 deve respeitar essa visão.

Tabelas/coleções lógicas:

1. `sources`
   - espelha `Source`

2. `items`
   - espelha `Item`
   - indexado por `source_id` e campos chave (ex.: produto, cidade)

3. `evidence_bundles`
   - espelha `EvidenceBundle` (principalmente metadados + path do arquivo JSON)

4. `queries`
   - espelha `QueryLog`

5. `gpt_responses`
   - opcional nesta sprint, mas recomendado para armazenar `GptAnswer` bruto/estruturado

Requisitos para S8

- todas as queries dos 3 cenários oficiais devem ser persistidas de forma que T6 possa reconstruir `query ↔ bundle ↔ resposta`
- os caminhos em `out/evidence/s8_bundles/` e `out/evidence/s8_queries/` devem ser estáveis e utilizáveis pelos gates

Compatibilidade futura

- essas "tabelas" viram base direta para a Truth‑DB da S10, podendo ganhar campos adicionais (`block_id`, `fact_id`, `version_id`) sem quebrar S8.

---

### 12. Scripts de gates e CI (bin/) – visão arquitetural

Ligação entre scripts e arquitetura:

- `s8_t1_static_quality.sh`
  - roda lint/format/scan em `app/` e `bin/`
- `s8_t2_unit_and_contracts.sh`
  - roda `pytest tests/s8_t2_unit_contracts/`
- `s8_t3_property_and_edge_cases.sh`
  - roda `pytest tests/s8_t3_property/`
- `s8_t4_golden_flows.sh`
  - roda `pytest tests/s8_t4_golden_flows/`
  - garante geração de bundles e logs
- `s8_t5_perf_and_limits.sh`
  - executa os cenários de T4 em loop, medindo tempo e tamanho
- `s8_t6_logs_and_evidence.sh`
  - verifica consistência de registros e paths em `out/evidence/s8_*`
- `s8_t7_ci_pipeline.sh`
  - chama `bin/s8_ci.sh`, que encadeia T1–T6
- `s8_t8_go_no_go.sh`
  - lê scorecards T0–T7 e toma decisão

O conteúdo exato de cada script é tema do Cap. 4, mas a ligação arquitetural já está aqui.

---

### 13. Handshake entre Cap. 1, Cap. 2 e Cap. 3

- **Cap. 1** diz o que a S8 precisa entregar (Admin v0, Usuário v0, fluxo GPT ancorado, demos, DoD).
- **Cap. 2** diz como vamos provar que isso foi entregue (gates, evidências, scorecards, GO/NO‑GO).
- **Cap. 3** diz onde e em que forma isso existe no código (arquitetura, filemap, modelos, contratos de módulo, APIs, storage).

Quando o Cap. 4 for escrito, ele pegará este blueprint (Cap. 3) e o traduzirá em:

- arquivos concretos com conteúdo
- comandos de terminal e passos detalhados para o Codex
- ajustes finos necessários para fazer todos os gates PASS

Até lá, o Cap. 3 v2 funciona como **contrato técnico final** da Sprint 8, garantindo que a execução já nasce orientada pelos gates leoninos do Cap. 2 e preparada para Truth‑DB e blockchain nas próximas sprints.

