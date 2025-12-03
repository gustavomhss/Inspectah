# Inspectah — Sprint 28
## Capítulo 3 — Arquitetura, Filemap e Pontos de Acoplamento
### E27.1 — CRUD & ON/OFF de Fonte

---

## 3.1 Visão geral da arquitetura da Sprint 28

A Sprint 28 atua sobre um conjunto bem definido de camadas do Inspectah:

1. **Domínio & Persistência (Backend)**  
   - Modelos de fonte e tipos relacionados (`Source`, `SourceType`, enums).  
   - Migrations de banco para consolidar o schema.  
   - Regras de domínio para ciclo de vida de estados (ACTIVE/DISABLED/DEPRECATED) e validações por tipo de fonte.

2. **API de Administração de Fontes**  
   - Endpoints `/admin/sources` responsáveis por CRUD & ON/OFF, filtragem e detalhes de fonte.  
   - Schemas (DTOs) usados para entrada/saída da API.

3. **Ingestão 2.0 & Scheduler**  
   - Lógica que decide **quais fontes** são elegíveis para ingestão automática em cada ciclo.  
   - Criação de registros de `IngestionRun` e interação com o modelo `Source`.

4. **Console de Fontes v2 (Frontend)**  
   - Tela de lista de fontes com filtros e ações.  
   - Tela de criação/edição de fonte com formulários guiados.  
   - Componentes visuais de estado, criticidade e menu de ações.

5. **Testes & Gates**  
   - Testes de domínio, API, integração e UI.  
   - Scripts `bin/s28_gX_*.sh` que orquestram validações e geram evidências/scorecards.

6. **Evidências & Observabilidade**  
   - Estrutura de arquivos em `out/evidence/S28_G*/**`.  
   - Integração com logs/observabilidade já existente em S21/S22 (sem refactors pesados).

A arquitetura da Sprint 28 é deliberadamente **evolutiva**: ela parte da base construída em S21/S22 e encaixa o CRUD & ON/OFF de fonte, sem introduzir novas tecnologias infra nem romper com o modelo de sprints anterior.

---

## 3.2 Backend — Domínio de Fontes & Persistência

### 3.2.1 Módulos e responsabilidades

**Módulo principal de fontes**  
- Caminho: `app/sources/models.py`
- Conteúdo esperado:
  - `class Source(Base)`: entidade central que representa uma fonte de dados.  
  - `class SourceType(Base)`: catálogo de tipos de fontes (`news_rss`, `http_json`, `price_feed`, etc.).  
  - Enums:
    - `class SourceState(Enum)`: `ACTIVE`, `DISABLED`, `DEPRECATED`.  
    - `class SourceMode(Enum)`: `AUTO`, `MANUAL`.  
    - `class SourceCriticality(Enum)`: `LOW`, `MEDIUM`, `HIGH` (ou equivalente).

**Campos esperados de `Source` (vista consolidada)**
- Identidade & descrição:  
  - `id` (PK),  
  - `name`,  
  - `slug` (opcional, se já existir no sistema),  
  - `description`.

- Classificação & contexto:  
  - `type` (FK para `SourceType` ou enum análogo),  
  - `category` (string ou enum: `news`, `data_official`, `market`, etc.),  
  - `domain` (string ou enum que liga a áreas como política, economia, mercado, etc.).

- Operação & configuração:  
  - `config` (JSON ou estrutura equivalente com detalhes por tipo),  
  - `credentials_ref` (referência a secreto, se existir),  
  - `mode` (`AUTO`/`MANUAL`),  
  - `schedule`/`cadence` (freq. de ingestão quando `AUTO`).

- Risco & criticidade:  
  - `criticality` (`LOW`/`MEDIUM`/`HIGH`).

- Ciclo de vida & estado:  
  - `state` (`ACTIVE`/`DISABLED`/`DEPRECATED`),  
  - `state_changed_at` (timestamp da última mudança de estado),  
  - `state_reason` (texto curto explicando o porquê da última mudança de estado).

- Metadados padrão:  
  - `created_at`, `updated_at`.

**Migrations**  
- Caminho: `migrations/versions/00xx_s28_sources_model_consolidation.py`
- Responsabilidades:
  - Criar/adicionar campos que faltavam para o modelo consolidado.  
  - Ajustar tipos/constraints quando necessário (ex.: tornar `state` obrigatório).  
  - Preservar dados existentes (migrações cuidadosas, sem perda silenciosa).

### 3.2.2 Invariantes de domínio importantes

- `Source.state` segue regras de transição definidas (ver Cap. 2):
  - Permitidas: `ACTIVE → DISABLED`, `DISABLED → ACTIVE`, `ACTIVE → DEPRECATED`.  
  - Proibidas: `DEPRECATED → ACTIVE` e qualquer outra transição que viole o fluxo de vida desenhado.

- Campos obrigatórios:
  - `name`, `type`, `mode`, `state` sempre presentes.  
  - Campos específicos por tipo (ex.: `config.url` obrigatório para `news_rss`).

- `criticality` deve sempre ter um valor válido (sem `NULL`/"sem classificação" em produção).  
- `state_changed_at` deve ser atualizado a cada transição de estado via API/admin.  
- `state_reason` deve ser preenchido para transições relevantes (ex.: desativação por problema ou manutenção).

### 3.2.3 Arquivos de teste relacionados ao domínio

- `tests/domain/test_sources_model_invariants.py`  
  - Cobre:
    - criação de `Source` válido,  
    - transições de estado válidas,  
    - tentativa de transições proibidas,  
    - validações por tipo (`news_rss`, `http_json`, etc.).

---

## 3.3 Backend — API de Admin `/admin/sources`

### 3.3.1 Rotas e handlers

**Arquivo principal de rotas**  
- Caminho: `app/api/admin_sources_routes.py`
- Responsável por expor endpoints REST para administração de fontes:
  - `GET /admin/sources` — listar fontes com filtros e paginação.  
  - `GET /admin/sources/{source_id}` — obter detalhes completos de uma fonte.  
  - `POST /admin/sources` — criar nova fonte.  
  - `PUT /admin/sources/{source_id}` — editar fonte existente (campos permitidos).  
  - `POST /admin/sources/{source_id}/activate` — ativar fonte.  
  - `POST /admin/sources/{source_id}/disable` — desativar fonte.  
  - `POST /admin/sources/{source_id}/deprecate` — marcar fonte como deprecada.

**Schemas (DTOs)**  
- Caminho: `app/sources/schemas.py`  
- Estruturas esperadas:
  - `SourceCreate` — payload de criação (campos obrigatórios + opcionais).  
  - `SourceUpdate` — payload de edição (apenas campos editáveis).  
  - `SourceDetail` — resposta detalhada de uma fonte.  
  - `SourceListItem` — item de lista.

### 3.3.2 Contratos principais

- Filtros suportados em `GET /admin/sources`:
  - `type`, `state`, `category`, `domain`, `mode`, `criticality`, além de paginação (`page`, `page_size`).

- Códigos de status esperados:
  - `200 OK` — operações de leitura/lista bem-sucedidas.  
  - `201 Created` — criação de fonte.  
  - `400 Bad Request` — payload inválido, campos faltando, combinações impossíveis.  
  - `404 Not Found` — `source_id` inexistente.  
  - `409 Conflict` — transições de estado proibidas.

- OpenAPI:  
  - Gerado automaticamente via FastAPI (ou framework equivalente).  
  - Deve refletir com precisão os campos e rotas acima.

### 3.3.3 Arquivos de teste da API

- `tests/api/test_admin_sources_crud_onoff.py`  
  - Cobre casos felizes, erros de validação e transições de estado.

---

## 3.4 Backend — Ingestão 2.0 & Scheduler (ON/OFF)

### 3.4.1 Módulos envolvidos

**Scheduler & ingestão**  
- Caminhos típicos (ajustar conforme repo real):
  - `app/ingestion/scheduler.py` — lógica de agendamento de ingestão.  
  - `app/ingestion/services.py` ou similar — seleção de fontes elegíveis e execução da ingestão.

**Modelo de IngestionRun**  
- Caminho: `app/ingestion/models.py` (ou equivalente).  
- Representa execuções de ingestão por fonte, contendo:
  - `id`, `source_id`, timestamps, `status` (SUCCESS/ERROR), possivelmente `error_reason`.

### 3.4.2 Regras de integração ON/OFF

- Fontes elegíveis para ingestão automática:
  - `mode = AUTO`  
  - `state = ACTIVE`  
  - demais critérios herdados de S22 (ex.: `enabled` geral, janelas de horário, etc., se existirem).

- Fontes não elegíveis:
  - `state = DISABLED` — deve ser excluída da lista de ingestão.  
  - `state = DEPRECATED` — não deve voltar a ingressar, salvo cenários muito específicos fora da S28 (neste momento, tratada como fora de fluxo).

### 3.4.3 Arquivos de teste de integração

- `tests/integration/test_sources_ingestion_onoff.py`  
  - Cobre os cenários descritos no Cap. 2 (criar, ingerir, desativar, parar, reativar, retomar).

---

## 3.5 Frontend — Console de Fontes v2

### 3.5.1 Páginas e componentes principais

**Estrutura de features**  
- Diretório raiz:  
  - `frontend/inspectah-ui/src/features/sources/`

**Páginas**
- `pages/SourcesListPage.tsx`  
  - Lista de fontes.  
  - Filtros (tipo, estado, domínio, criticidade, modo).  
  - Botão “Nova Fonte”.

- `pages/SourceFormPage.tsx`  
  - Formulário para criação/edição de fonte.  
  - Campos agrupados por seções (dados básicos, operação, risco, domínio).

**Componentes**
- `components/SourceListTable.tsx`  
  - Renderiza a tabela de fontes.  
  - Mostra colunas como: Nome, Tipo, Domínio, Modo, Estado, Criticidade, Ações.

- `components/SourceStateBadge.tsx`  
  - Badge visual para estado (`ACTIVE`, `DISABLED`, `DEPRECATED`).

- `components/SourceActionsMenu.tsx`  
  - Menu de ações de linha (Ver detalhes, Editar, Ativar, Desativar, Deprecar).

- Outros componentes auxiliares (ex.: filtros, formulário de config) conforme necessário.

### 3.5.2 API client

- Caminho: `src/features/sources/api/adminSourcesApi.ts`  
- Responsável por encapsular chamadas à API `/admin/sources`:
  - `listSources(filters)`,  
  - `getSource(id)`,  
  - `createSource(payload)`,  
  - `updateSource(id, payload)`,  
  - `activateSource(id)`, `disableSource(id)`, `deprecateSource(id)`.

### 3.5.3 Testes de UI / e2e

- Diretório de testes:  
  - `frontend/inspectah-ui/tests/sources/`
- Arquivo principal:  
  - `sources_console_onoff.spec.ts`
- Pode ser desdobrado em arquivos adicionais se os fluxos ficarem grandes, desde que mantida clareza de nomes.

---

## 3.6 Scripts de Gates, CI e Evidências

### 3.6.1 Scripts de gate da Sprint 28

Diretório: `bin/`

Scripts esperados:
- `bin/s28_g0_scope_and_baseline.sh`  
- `bin/s28_g1_sources_model_and_schema.sh`  
- `bin/s28_g2_sources_admin_api.sh`  
- `bin/s28_g3_sources_console_front.sh`  
- `bin/s28_g4_sources_ingestion_integration.sh`  
- `bin/s28_g5_observability_and_legacy_sanity.sh`  
- `bin/s28_g6_demo_internal.sh`  
- `bin/s28_g7_go_no_go.sh`

Cada script:
- é idempotente (pode rodar várias vezes),  
- usa `set -euo pipefail` para falhar de forma clara,  
- escreve logs/evidências em `out/evidence/S28_G*/**`,  
- gera scorecard JSON em `out/scorecards/S28_G*.json`.

### 3.6.2 Integração com CI

- Workflow esperado (exemplo):  
  - `.github/workflows/s28-gates.yml`

Esse workflow deve:
- ser acionado manualmente e/ou em eventos de PR para branch da S28,  
- rodar os scripts de gates em ordem lógica (G0→G7, com possibilidade de paralelização parcial quando seguro),  
- anexar logs como artefatos do CI,  
- falhar o job se qualquer gate retornar erro.

### 3.6.3 Estrutura de evidências e scorecards

**Evidências**  
- Raiz: `out/evidence/`
- Por gate:
  - `out/evidence/S28_G0_scope_and_baseline/`  
  - `out/evidence/S28_G1_sources_model_and_schema/`  
  - ...  
  - `out/evidence/S28_G6_demo_internal/`

Dentro de cada pasta, podem existir:
- logs de execução (`.log`),  
- dumps de schema,  
- capturas de tela (para G6),  
- qualquer arquivo auxiliar relevante.

**Scorecards**  
- Diretório: `out/scorecards/`
- Arquivos:
  - `S28_G0_scope_and_baseline.json`  
  - `S28_G1_sources_model_and_schema.json`  
  - ...  
  - `S28_G6_demo_internal.json`  
  - `S28_overall.json` (gate G7 consolidado)

---

## 3.7 Resumo do filemap da Sprint 28

**Backend**
- `app/sources/models.py`  
- `app/sources/schemas.py`  
- `app/api/admin_sources_routes.py`  
- `app/ingestion/scheduler.py`  
- `app/ingestion/models.py` (ou arquivo equivalente que contenha `IngestionRun`).

**Migrations**
- `migrations/versions/00xx_s28_sources_model_consolidation.py`

**Testes**
- `tests/domain/test_sources_model_invariants.py`  
- `tests/api/test_admin_sources_crud_onoff.py`  
- `tests/integration/test_sources_ingestion_onoff.py`

**Frontend**
- `frontend/inspectah-ui/src/features/sources/pages/SourcesListPage.tsx`  
- `frontend/inspectah-ui/src/features/sources/pages/SourceFormPage.tsx`  
- `frontend/inspectah-ui/src/features/sources/components/SourceListTable.tsx`  
- `frontend/inspectah-ui/src/features/sources/components/SourceStateBadge.tsx`  
- `frontend/inspectah-ui/src/features/sources/components/SourceActionsMenu.tsx`  
- `frontend/inspectah-ui/src/features/sources/api/adminSourcesApi.ts`  
- `frontend/inspectah-ui/tests/sources/sources_console_onoff.spec.ts`

**Scripts & CI**
- `bin/s28_g0_scope_and_baseline.sh`  
- `bin/s28_g1_sources_model_and_schema.sh`  
- `bin/s28_g2_sources_admin_api.sh`  
- `bin/s28_g3_sources_console_front.sh`  
- `bin/s28_g4_sources_ingestion_integration.sh`  
- `bin/s28_g5_observability_and_legacy_sanity.sh`  
- `bin/s28_g6_demo_internal.sh`  
- `bin/s28_g7_go_no_go.sh`  
- `.github/workflows/s28-gates.yml`

**Evidências & Scorecards**
- `out/evidence/S28_G*/**`  
- `out/scorecards/S28_G*.json`  
- `out/scorecards/S28_overall.json`

---

Este Capítulo 3 entrega a visão consolidada de **arquitetura e filemap** da Sprint 28, cobrindo backend (modelo, API, ingestão), frontend (console de fontes v2), scripts de gates, CI e organização de evidências. É o mapa que o Codex/implementadores devem seguir para materializar, em código, o que foi definido nos Capítulos 1 e 2.