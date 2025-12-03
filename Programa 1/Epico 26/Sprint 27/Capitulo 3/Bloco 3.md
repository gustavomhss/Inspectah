# Inspectah — Sprint 27 (S27)
## Capítulo 3 — Bloco 3
### Filemap detalhado de backend — APIs, modelos, schemas e testes de contrato

> Arquivo-alvo no repo: `docs/s27_cap_3_3_filemap_backend_apis.md`
>
> Função: detalhar a organização do **backend** da S27 — rotas de API, modelos, schemas e testes — que dão suporte direto aos consoles admin de Fontes, Ingestão 2.0 e Debunker. Este bloco conecta o mundo HTTP/modelos aos consoles admin e aos gates G2/G4.

---

## 1. Princípios de organização do backend na S27

A S27 adota alguns princípios explícitos para o backend exposto aos consoles admin:

1. **Separação clara por domínio**  
   - Fontes, Ingestão e Debunker têm rotas, modelos e schemas próprios, ainda que compartilhem algumas entidades base.

2. **Contratos explícitos**  
   - Toda rota usada por consoles admin tem um contrato (request/response) definido em schema ou modelo claro.

3. **Tests de contrato próximos ao código**  
   - Para cada grupo de rotas admin, há testes de API que validam comportamento e formato de resposta.

4. **Rastreabilidade com o frontend admin**  
   - É possível mapear, a partir de uma tela admin, quais rotas e modelos ela consome.

---

## 2. Filemap backend — Domínio Fontes

### 2.1 Rotas de API de Fontes

- Diretório típico de rotas:
  - `app/api/sources_routes.py`  
    - Exemplos de endpoints (nomes ilustrativos, ajustar à realidade):
      - `GET /api/sources` — listar fontes com filtros.  
      - `GET /api/sources/{source_id}` — detalhe de uma fonte.  
      - `POST /api/sources` — criar nova fonte.  
      - `PUT /api/sources/{source_id}` — atualizar uma fonte.  
      - `POST /api/sources/{source_id}/activate` — ativar.  
      - `POST /api/sources/{source_id}/deactivate` — desativar.

### 2.2 Modelos e schemas de Fontes

- Modelos de persistência:
  - `app/models/sources.py`
    - Exemplo: `Source` (id, nome, tipo, config, status, datas, etc.).

- Schemas (entrada/saída):
  - `app/schemas/sources.py`
    - `SourceCreate`, `SourceUpdate`, `SourceOut`, `SourceListFilters`.

Esses schemas são o contrato esperado pelo frontend em `features/sources`.

### 2.3 Tests de API / contrato de Fontes

- Diretório de testes de contrato:
  - `tests/api/test_admin_sources_contracts.py`

- Escopo:
  - Verificar que os endpoints usados pelos consoles admin de Fontes:
    - respondem com códigos HTTP esperados;  
    - retornam JSON com campos e tipos compatíveis com schemas;  
    - tratam erros básicos de forma previsível (404, 400, etc.).

G4, na parte de Fontes, deve apontar para esses arquivos.

---

## 3. Filemap backend — Domínio Ingestão 2.0

### 3.1 Rotas de API de Ingestão

- Diretório típico de rotas:
  - `app/api/ingestion_routes.py`

- Exemplos de endpoints (ajustar conforme projeto):
  - `GET /api/ingestion/overview` — visão agregada da saúde da ingestão por fonte.  
  - `GET /api/ingestion/sources/{source_id}` — estado de ingestão para uma fonte específica.  
  - `GET /api/ingestion/runs` — lista de runs de ingestão (com filtros).  
  - `POST /api/ingestion/runs/{run_id}/retry` — acionar reprocessamento ou ação similar.

### 3.2 Modelos e schemas de Ingestão

- Modelos:
  - `app/models/ingestion.py`
    - Exemplo: `IngestionRun`, `IngestionStatus`.

- Schemas:
  - `app/schemas/ingestion.py`
    - `IngestionOverview`, `IngestionSourceStatus`, `IngestionRunOut`, etc.

Esses schemas definem o contrato consumido por `features/ingestion`.

### 3.3 Tests de API / contrato de Ingestão

- Diretório de testes:
  - `tests/api/test_admin_ingestion_contracts.py`

- Escopo:
  - Validar que endpoints chave de Ingestão atendem o contrato esperado pelos componentes como `IngestionStatusCard`, `IngestionIssuesTable`, `IngestionRunsPage`.

G4, na parte de Ingestão, usa esses testes como fonte principal.

---

## 4. Filemap backend — Domínio Debunker

### 4.1 Rotas de API do Debunker

- Diretório típico de rotas:
  - `app/api/debunker_routes.py`

- Exemplos de endpoints (ajustar conforme modelo real):
  - `GET /api/debunker/cases` — lista de casos de disputa.  
  - `GET /api/debunker/cases/{case_id}` — detalhe de um caso.  
  - `POST /api/debunker/cases/{case_id}/decision` — registrar decisão (aprovar, rejeitar, escalar).  
  - `POST /api/debunker/cases/{case_id}/comment` — adicionar comentário ou anotação.

### 4.2 Modelos e schemas do Debunker

- Modelos:
  - `app/models/debunker.py`
    - Ex.: `DebunkCase`, `Evidence`, `Decision`.

- Schemas:
  - `app/schemas/debunker.py`
    - `DebunkCaseOut`, `EvidenceOut`, `DecisionIn`, `DecisionOut`.

Esses schemas são a base de tipos para `features/debunker`.

### 4.3 Tests de API / contrato do Debunker

- Diretório de testes:
  - `tests/api/test_admin_debunker_contracts.py`

- Escopo:
  - Validar que endpoints do Debunker entregam dados consistentes para telas:
    - `DebunkerCasesListPage`,  
    - `DebunkerCaseDetailPage`,  
    - painéis de evidência e decisão.

G4, na parte de Debunker, extrai seu veredito a partir desses testes.

---

## 5. Relação entre backend e fluxos E2E (G2)

Os fluxos E2E verificados em G2 cruzam múltiplos domínios de backend:

- **Fluxo Fontes — ciclo de vida básico**  
  - Usuário admin interage com `features/sources/*`;  
  - backend respondendo via `app/api/sources_routes.py` e `app/models/sources.py`.

- **Fluxo Ingestão — acompanhar problema**  
  - UI em `features/ingestion/*` consome `app/api/ingestion_routes.py`.  
  - Problemas podem ser correlacionados com dados de fontes.

- **Fluxo Debunker — tratar disputa**  
  - UI em `features/debunker/*` consome `app/api/debunker_routes.py` e modelos associados.

- **Fluxo combinado — Fontes → Ingestão → Debunker**  
  - Pode atravessar:  
    - `GET /api/sources/{source_id}`  
    - `GET /api/ingestion/sources/{source_id}`  
    - `GET /api/debunker/cases?source_id=...`

Cap.2 (G2) deve referenciar explicitamente quais endpoints fazem parte de cada cenário de teste E2E.

---

## 6. Integração com ferramentas de schema (OpenAPI/JSON Schema)

Se o projeto usa OpenAPI/JSON Schema, a S27 recomenda:

- Arquivo de especificação (exemplo):  
  - `app/api/openapi.yaml` ou `app/api/openapi.json`.

- G4 pode incluir:
  - validação de consistência desse arquivo;  
  - geração de clients (se for o caso);  
  - validação de exemplos de resposta retornados pelas APIs de Fontes, Ingestão e Debunker contra o schema.

O filemap deve refletir onde vivem esses arquivos para que o Codex possa ajustá-los quando os contratos mudarem.

---

## 7. Relação deste backend filemap com gates e docs

- **G0**: garante que o backend é compilável/sadio em nível mínimo (sanity checks).  
- **G2**: usa os endpoints mapeados aqui para construir cenários E2E.  
- **G3**: ainda que focado em frontend, depende de APIs estáveis para testes E2E integrarem.  
- **G4**: é o gate que lê diretamente este filemap (rotas, modelos, schemas, tests) para validar contratos.  
- **G5/G6**: runbooks e ORR referenciam endpoints e comportamentos descritos aqui.

Este Bloco 3 é, portanto, o mapa físico do lado servidor da S27: ele diz aos squads e ao Codex **onde** mexer quando for preciso alterar comportamento ou contrato de Fontes, Ingestão e Debunker no escopo da sprint.

