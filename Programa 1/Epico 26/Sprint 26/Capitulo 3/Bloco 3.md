# Inspectah — Sprint 26 (S26)
## Capítulo 3 — Bloco 3.3
### Filemap do Console de Fontes v2 & APIs de Fontes

Este bloco descreve o **filemap concreto** do Console de Fontes v2 (frontend) e das **APIs de fontes** (backend) que o console consome. Ele também amarra a relação entre esses arquivos e os gates G2 e G4 da S26.

A ideia central:
- o Console de Fontes v2 vive em uma **feature isolada** no frontend, dependente do Design System Admin v1;
- as APIs de fontes vivem na camada de backend de domínio, com rotas e testes explícitos;
- a comunicação entre os dois passa por uma camada clara de `sourcesApi` e tipos `Source`.

---

## 1. Frontend — Filemap do Console de Fontes v2

O Console de Fontes v2 é organizado como uma **feature** do frontend admin.

Localização base sugerida:

```text
frontend/inspectah-ui/src/features/sources/
```

Estrutura macro da pasta:

```text
frontend/inspectah-ui/src/features/sources/
  pages/
    SourcesListPage.tsx
    SourceEditPage.tsx
  components/
    SourcesTable.tsx
    SourceForm.tsx
    SourceStatusBadge.tsx
  api/
    sourcesApi.ts
  types/
    Source.ts
  index.ts
```

### 1.1. Pasta `pages/`

Responsável por expor as **páginas de roteamento** do Console de Fontes v2.

- `SourcesListPage.tsx`
  - Página principal de listagem de fontes.  
  - Usa `AdminShell`, `AdminHeader` e `AdminContent` do Design System Admin v1.  
  - Renderiza `SourcesTable` para mostrar as fontes; aciona filtros básicos; expõe ações de criar/editar/alterar status.

- `SourceEditPage.tsx`
  - Página de criação/edição de fonte.  
  - Usa layout admin (`AdminShell`, `AdminHeader`, `AdminContent`).  
  - Renderiza `SourceForm`, preenchido com dados atuais (edição) ou vazio (criação).  
  - Integra com `sourcesApi` para salvar alterações.

Invariantes:

1. Nenhuma página do Console de Fontes implementa layout próprio; usa sempre componentes de layout do design system.  
2. As páginas delegam a lógica de apresentação de dados a componentes de `components/` e a comunicação com backend a `api/sourcesApi.ts`.

### 1.2. Pasta `components/`

Contém componentes **específicos do domínio** de fontes.

- `SourcesTable.tsx`
  - Tabela de listagem de fontes.  
  - Usa o componente `Table` do design system para renderizar colunas como nome, tipo, status e ações.  
  - Exibe estados de vazio, loading e erro usando `Banner`/`Skeleton` do design system, conforme definido em Cap.3.2.

- `SourceForm.tsx`
  - Formulário para criação/edição de fonte.  
  - Composto por `FormField`, `Input`, `Select` e outros componentes admin genéricos.  
  - Implementa regras básicas de validação de UI (campos obrigatórios, formatos esperados) alinhadas aos schemas do backend.

- `SourceStatusBadge.tsx`
  - Componente pequeno para exibir o status da fonte (`ATIVA`, `INATIVA`, `ARQUIVADA`, etc.).  
  - Usa `Badge` do design system com esquemas de cor derivados de tokens.

Invariantes:

1. Esses componentes **conhecem o domínio** (sabem o que é `Source`, quais campos existem, quais status são possíveis).  
2. Nenhum componente aqui reimplementa botões, inputs ou tabelas do zero; tudo vem de `@/ui/admin`.  
3. Mudanças de contrato de API devem ser refletidas nos tipos de `types/Source.ts` e, a partir daí, nos componentes.

### 1.3. Pasta `api/`

Responsável por encapsular a comunicação com as APIs de fontes.

- `sourcesApi.ts`
  - Expõe funções como:

```ts
export async function listSources(params: ListSourcesParams): Promise<Source[]>;
export async function getSourceById(id: string): Promise<Source>;
export async function createSource(payload: CreateSourcePayload): Promise<Source>;
export async function updateSource(id: string, payload: UpdateSourcePayload): Promise<Source>;
export async function activateSource(id: string): Promise<Source>;
export async function deactivateSource(id: string): Promise<Source>;
export async function archiveSource(id: string): Promise<Source>;
```

  - Usa tipos definidos em `types/Source.ts`.  
  - Centraliza URLs de endpoints, métodos HTTP e tratamento básico de erros (por exemplo, mapeando erros de validação para mensagens amigáveis quando apropriado).

Invariantes:

1. Páginas e componentes do Console de Fontes v2 **não** fazem `fetch`/`axios` diretamente; sempre usam funções de `sourcesApi.ts`.  
2. Ajustes de endpoint ou contrato de API são concentrados em `sourcesApi.ts`.

### 1.4. Pasta `types/`

Define tipos TypeScript para o domínio de fontes no frontend.

- `Source.ts`
  - Define a interface principal, algo como:

```ts
export interface Source {
  id: string;
  name: string;
  type: "RSS" | "API" | "CSV" | string; // conforme modelo real
  status: "ACTIVE" | "INACTIVE" | "ARCHIVED"; // ou enum equivalente
  createdAt: string;
  updatedAt: string;
  // outros campos relevantes de configuração
}
```

  - Pode incluir tipos auxiliares (ex.: `SourceStatus`, `SourceType`).

Invariantes:

1. As respostas esperadas de API são tipadas aqui;  
2. Componentes de UI de fontes dependem desses tipos, não de `any`.

### 1.5. Arquivo `index.ts`

Opcional, mas recomendado para facilitar imports:

```ts
export * from "./pages/SourcesListPage";
export * from "./pages/SourceEditPage";
export * from "./types/Source";
```

Isso permite que outras partes do frontend importem elementos do Console de Fontes v2 a partir de um ponto único.

---

## 2. Backend — Filemap das APIs de Fontes

No backend, o domínio de fontes vive em um módulo específico (nomes exatos podem variar, mas a estrutura lógica é esta).

Localização base sugerida:

```text
app/sources/
  models.py
  schemas.py
  routes.py       # ou routers/sources.py, conforme padrão
  service.py      # opcional, para regras de negócio

tests/api/
  test_sources_console.py
```

### 2.1. `models.py`

- Define o modelo de dados de `Source` (ORM ou equivalente), com campos como:
  - `id`
  - `name`
  - `type`
  - `status`
  - `config` (JSON ou estruturado, dependendo da implementação)
  - timestamps (`created_at`, `updated_at`)

### 2.2. `schemas.py`

- Define schemas de entrada e saída para as APIs de fontes (Pydantic ou equivalente):
  - `SourceCreate`
  - `SourceUpdate`
  - `SourceOut`

- Garante que campos obrigatórios e restrições básicas estejam codificados nos tipos.

### 2.3. `routes.py` (ou `routers/sources.py`)

- Define as rotas consumidas pelo Console de Fontes v2, por exemplo:
  - `GET /api/sources` — listar fontes;  
  - `GET /api/sources/{id}` — obter uma fonte específica;  
  - `POST /api/sources` — criar fonte;  
  - `PUT/PATCH /api/sources/{id}` — atualizar fonte;  
  - `POST /api/sources/{id}/activate` — ativar;  
  - `POST /api/sources/{id}/deactivate` — desativar;  
  - `POST /api/sources/{id}/archive` — arquivar.

### 2.4. `tests/api/test_sources_console.py`

- Agrupa os testes de API focados nos fluxos que o Console de Fontes v2 usa.  
- Casos típicos:
  - listar fontes com e sem filtros;  
  - criar fonte válida;  
  - rejeitar criação inválida (campos obrigatórios ausentes ou inválidos);  
  - atualizar dados de fonte existente;  
  - ativar/desativar/arquivar fonte respeitando invariantes (ex.: não arquivar fonte inexistente, não ativar fonte já ativa, etc.).

Esses testes são fundamentais para o gate **G4 — API & Modelo de Dados de Fontes (Contratos)**.

---

## 3. Conexão Frontend ↔ Backend (Console de Fontes v2)

A ligação entre Console de Fontes v2 e APIs de fontes ocorre via `sourcesApi.ts`.

Fluxo típico:

1. Página `SourcesListPage.tsx` chama `listSources()` de `sourcesApi.ts`.  
2. `sourcesApi.ts` faz uma requisição `GET /api/sources` para o backend.  
3. O backend responde com uma lista de `SourceOut`.  
4. `sourcesApi.ts` converte (se necessário) para o tipo `Source` do frontend.  
5. `SourcesTable.tsx` renderiza os dados usando `Table` do design system e `SourceStatusBadge`.

Caminho semelhante se aplica a criação, edição e mudança de status (ativar/desativar/arquivar), sempre passando por funções de `sourcesApi.ts`.

---

## 4. Relação do Filemap com os Gates G2 e G4

- **G2 — Console de Fontes v2 (Fluxos Básicos)**
  - Depende diretamente de:
    - `frontend/inspectah-ui/src/features/sources/pages/*`  
    - `frontend/inspectah-ui/src/features/sources/components/*`  
    - `frontend/inspectah-ui/src/features/sources/api/sourcesApi.ts`  
    - `frontend/inspectah-ui/src/features/sources/types/Source.ts`
  - Os testes de G2 navegam por esses caminhos para validar os fluxos principais.

- **G4 — API & Modelo de Dados de Fontes (Contratos)**
  - Depende diretamente de:
    - `app/sources/models.py`  
    - `app/sources/schemas.py`  
    - `app/sources/routes.py` (ou `routers/sources.py`)  
    - `tests/api/test_sources_console.py`
  - Os testes de G4 garantem que o backend cumpre os contratos assumidos pelo Console de Fontes v2.

---

## 5. Síntese do Bloco 3.3

O Bloco 3.3 fixa, em termos de **filemap**, onde o Console de Fontes v2 vive e como ele fala com o backend:

- no frontend, a feature `features/sources` organiza páginas, componentes, API client e tipos;  
- no backend, o módulo `app/sources` organiza modelos, schemas e rotas, com testes em `tests/api/test_sources_console.py`;  
- a cola entre os dois é `sourcesApi.ts`, que implementa funções tipadas para consumo das rotas;  
- os gates G2 e G4 fiscalizam que essa ligação está saudável.

Com isso, qualquer pessoa consegue partir do Capítulo 1 (objetivo da sprint), passar pelos gates do Capítulo 2 e chegar até os arquivos específicos que implementam o Console de Fontes v2 e suas APIs.

