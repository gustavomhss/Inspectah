# Inspectah — Sprint 26 (S26)
## Capítulo 3 — Arquitetura & Filemap

Este capítulo descreve **como** a S26 se materializa na árvore de código e na arquitetura do Inspectah. Ele conecta o contexto e os gates (Cap.1 e Cap.2) com:

- módulos e camadas impactados;
- estrutura de diretórios e arquivos novos/alterados;
- organização do Design System Admin v1;
- organização do Console de Fontes v2;
- scripts de gates e testes que amarram tudo.

Cap.3 está organizado em quatro blocos:

- **Bloco 3.1** — Visão de arquitetura lógica da S26 (frontend, backend, gates).
- **Bloco 3.2** — Filemap do Design System Admin v1.
- **Bloco 3.3** — Filemap do Console de Fontes v2 e APIs relacionadas.
- **Bloco 3.4** — Mapa de dependências, invariantes estruturais e pontos de extensão.

---

## Bloco 3.1 — Visão de Arquitetura Lógica da S26

### 1. Papel da S26 na arquitetura atual

A S26 atua principalmente em duas frentes da arquitetura do Inspectah:

1. **Frontend admin** — introduzindo o **Design System Inspectah Admin v1** como camada transversal de UI para consoles internos.
2. **Console de Fontes** — reconstruindo o console em cima desse design system, conectando-o às APIs e modelos de dados já existentes para fontes.

Do ponto de vista de camadas, S26 não cria um novo domínio de negócio; ela reorganiza a forma como o domínio de "fontes" é apresentado e operado, e cria uma camada de UI reutilizável para futuras sprints (S27–S32).

### 2. Componentes principais na S26

A arquitetura lógica da S26 pode ser resumida em três componentes principais:

1. **Design System Admin v1 (UI/Admin Core)**  
   Biblioteca de componentes e tokens de design usada por todos os consoles admin. Ela fornece:
   - layout de página admin (estrutura com sidebar, header, área de conteúdo);
   - componentes básicos de navegação (links, itens de menu);
   - componentes de dados (tabelas, listas, badges);
   - componentes de formulário (inputs, selects, textareas, radio/checkbox, validação visual);
   - componentes de feedback (modais, toasts, banners de estado, skeleton/loading);
   - tokens centralizados (cores, tipografia, espaçamento, bordas, sombras, estados).

2. **Console de Fontes v2 (UI/Feature Sources)**  
   Implementação da interface de gestão de fontes, usando exclusivamente o Design System Admin v1. Inclui:
   - tela de lista de fontes com filtros básicos;
   - tela de criação/edição de fonte;
   - componentes específicos do domínio "fonte" (formulário de configuração, indicadores de status);
   - integrações com as rotas de API de fontes.

3. **APIs e modelo de dados de fontes (Backend/Domain Sources)**  
   Camada backend já existente para fontes (models, schemas, rotas). A S26 pode:
   - ajustar contratos e validações pontuais, se necessário;
   - adicionar testes de API focados nos fluxos usados pelo novo console;
   - garantir a coerência entre invariantes de dados e o que a UI expõe.

### 3. Interações entre componentes

A interação entre os três componentes segue o fluxo:

- O **operador** interage com o **Console de Fontes v2**, construído com componentes do **Design System Admin v1**.
- O console emite chamadas para as **APIs de fontes** (listar, criar, atualizar, ativar/desativar/arquivar).
- As respostas são renderizadas usando componentes do design system, respeitando estados de sucesso, erro e vazio.
- Os **gates de S26** (G1–G4) verificam, cada um em seu nível, se o design system está íntegro, se o console funciona, se o front como um todo permanece saudável e se os contratos de API estão corretos.

Do ponto de vista de arquitetura, S26 precisa manter uma separação clara entre:

- a **camada genérica de UI admin** (design system),
- a **camada de telas de funcionalidade** (console de fontes),
- a **camada de negócio/dados** (APIs de fontes).

---

## Bloco 3.2 — Filemap do Design System Admin v1 (Frontend)

O Design System Admin v1 é introduzido como uma "mini-biblioteca" interna no frontend do Inspectah. O objetivo é que qualquer console admin futuro possa depender dessa árvore como fonte primária de componentes.

### 1. Localização base

Sugestão (a ser confirmada em Cap.4 com o time, mas tratada aqui como contrato preferencial):

- `frontend/inspectah-ui/src/ui/admin/`  
  Raiz do Design System Admin v1.

Dentro dessa pasta, a organização proposta é:

- `tokens/` — definição de tokens de design (cores, tipografia, espaçamentos, etc.).
- `components/` — componentes genéricos, independentes de domínio.
- `layout/` — componentes de layout de página admin.
- `hooks/` (opcional) — hooks utilitários ligados à UI admin.
- `index.ts` — ponto de entrada público do design system (re-exporta os componentes e tokens).

### 2. Estrutura detalhada de arquivos

Estrutura exemplificativa (nomes exatos podem ser refinados, mas a ideia estrutural é fixa):

- `frontend/inspectah-ui/src/ui/admin/`
  - `tokens/`
    - `colors.ts`
    - `typography.ts`
    - `spacing.ts`
    - `shadows.ts`
    - `radius.ts`
    - `index.ts` (re-exporta tokens principais)
  - `layout/`
    - `AdminShell.tsx` (layout com sidebar + header + conteúdo)
    - `AdminSidebar.tsx`
    - `AdminHeader.tsx`
    - `AdminContent.tsx`
    - `index.ts`
  - `components/`
    - `Button.tsx`
    - `Button.test.tsx`
    - `Input.tsx`
    - `Input.test.tsx`
    - `Select.tsx`
    - `Table.tsx`
    - `Badge.tsx`
    - `Modal.tsx`
    - `Toast.tsx`
    - `Banner.tsx`
    - `FormField.tsx`
    - `index.ts`
  - `hooks/` (se necessário)
    - `useToast.ts`
    - `index.ts`
  - `index.ts` (exporta tokens, layout e components)

Além disso, testes específicos do design system devem ficar próximos dos componentes ou em uma pasta `__tests__`, conforme padrão atual do frontend.

### 3. Princípios estruturais do design system

1. **Dependência unidirecional**: consoles admin podem depender do design system; o design system não depende de componentes específicos de consoles.
2. **Tokens como fonte única de verdade**: cores, tipografia e espaçamentos usados em componentes admin devem vir de `tokens/`, jamais de valores "hardcoded" em cada componente.
3. **Exports controlados**: o `index.ts` do design system define o que é API pública; componentes internos auxiliares podem permanecer não exportados.
4. **Isolamento de domínio**: nenhum componente do design system deve conhecer o conceito de "fonte", "caso", "debunker" etc. Ele é estritamente genérico.

---

## Bloco 3.3 — Filemap do Console de Fontes v2 e APIs (Frontend + Backend)

### 1. Frontend — Console de Fontes v2

O Console de Fontes v2 passa a ser um conjunto de telas e componentes de domínio que consomem o Design System Admin v1.

Sugestão de organização base:

- `frontend/inspectah-ui/src/features/sources/`
  - `pages/`
    - `SourcesListPage.tsx`
    - `SourceEditPage.tsx`
  - `components/`
    - `SourcesTable.tsx`
    - `SourceForm.tsx`
    - `SourceStatusBadge.tsx`
  - `api/`
    - `sourcesApi.ts` (funções de chamada às APIs de backend de fontes)
  - `types/`
    - `Source.ts` (tipagens TypeScript para fontes)
  - `index.ts`

As páginas `SourcesListPage.tsx` e `SourceEditPage.tsx` usam:

- layout do design system (`AdminShell`, `AdminHeader`, `AdminContent`);
- componentes genéricos (`Table`, `Button`, `Input`, `Select`, `Badge`, `Modal`, `Toast`, `Banner`, `FormField`);
- componentes de domínio (`SourcesTable`, `SourceForm`, `SourceStatusBadge`).

### 2. Backend — APIs de fontes

No backend, a S26 se apoia nas estruturas existentes de fontes, que podem estar, por exemplo, em:

- `app/sources/models.py`
- `app/sources/schemas.py`
- `app/sources/routes.py` (ou `routers/sources.py`, conforme padrão atual)
- `tests/api/test_sources_console.py` (arquivo de testes de API criado/ajustado na S26)

A S26 pode introduzir ou alterar:

- rotas específicas para ativar/desativar/arquivar fontes;
- validações adicionais em schemas (campos obrigatórios, estados válidos);
- testes que alinhem essas rotas com as necessidades do Console de Fontes v2.

### 3. Conexão entre frontend e backend

O arquivo `frontend/inspectah-ui/src/features/sources/api/sourcesApi.ts` é o ponto de ligação principal entre Console de Fontes v2 e backend. Ele deve expor funções como:

- `listSources(params)`
- `createSource(payload)`
- `updateSource(id, payload)`
- `activateSource(id)`
- `deactivateSource(id)`
- `archiveSource(id)`

Essas funções consomem as rotas definidas em `app/sources/routes.py` e utilizam os tipos definidos em `types/Source.ts`.

---

## Bloco 3.4 — Mapa de Dependências, Invariantes e Pontos de Extensão

### 1. Mapa de dependências principais

- **Design System Admin v1**
  - Depende da infra de frontend (React, TypeScript, tooling) e dos tokens declarados em sua própria pasta.
  - Não depende de nenhum módulo de domínio (sources, cases, debunker).

- **Console de Fontes v2**
  - Depende do Design System Admin v1 (para layout e componentes básicos);
  - Depende das funções de `sourcesApi.ts` para comunicação com backend;
  - Depende dos tipos de `types/Source.ts`.

- **APIs de fontes**
  - Dependem do modelo de dados de fontes e da infraestrutura de API (FastAPI ou equivalente);
  - Não dependem de componentes de UI.

- **Scripts de gates G0–G6**
  - Dependem da existência dos diretórios descritos aqui;
  - Dependem da capacidade de rodar linters, testes e build com a estrutura definida.

### 2. Invariantes estruturais da S26

1. Nenhum componente de console admin novo deve ser criado fora de `ui/admin` (para design system) ou das pastas específicas de features (como `features/sources`).
2. Nenhuma tela de fontes pode usar diretamente estilos "hardcoded" de layout, cores ou tipografia; tudo deve passar pelo Design System Admin v1.
3. As rotas de API de fontes usadas pelo Console de Fontes v2 devem estar cobertas por testes de API, garantindo contratos consistentes.
4. O filemap aqui descrito deve ser refletido nos scripts de G0 e G1 (checagens de existência de diretórios e arquivos principais).

### 3. Pontos de extensão para sprints futuras (S27–S32)

A arquitetura desenhada para S26 prepara pontos naturais de extensão:

- O **Design System Admin v1** poderá ser estendido com novos componentes para Ingestão, Debunker, Truth Console, Evidence Vault e Case Cockpit, sem quebrar o que foi feito para fontes.
- O **Console de Fontes v2** já nasce com estrutura para receber, em S27, módulos de histórico de ingestão, métricas e healthscore (ex.: novas seções na tela de detalhe, abas adicionais, widgets de status).
- As **APIs de fontes** podem ganhar novas rotas para relatórios e dados agregados sem mudar o contrato básico usado em S26.

### 4. Síntese do Capítulo 3

O Capítulo 3 fixa o "mapa físico" da S26 dentro do repositório:

- onde vive o Design System Admin v1;
- onde vive o Console de Fontes v2 e como se organiza;
- onde estão as APIs de fontes e seus testes;
- quais caminhos os scripts de gates devem conhecer.

Com isso, qualquer pessoa que abra o repositório consegue navegar da visão conceitual da sprint (Cap.1) e dos gates (Cap.2) para os arquivos reais que implementam a S26. É esse alinhamento entre **ideia, contrato e código** que permite ao Inspectah crescer sem se perder em dívidas invisíveis.

