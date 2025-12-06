# Sprint 33 — Capítulo 3

## Bloco 3 — Frontend OracleOps Cockpit v1: composição, rotas e UX operacional

Este bloco detalha a arquitetura de frontend da Sprint 33 para o OracleOps Cockpit v1. Se o Bloco 2 explicou como o backend organiza domínio, serviços e API, aqui o foco é **como o cockpit é estruturado na UI**, quais páginas e componentes existem, como eles consomem a API e quais princípios guiam a experiência do operador.

O objetivo é que, com este bloco, alguém consiga:
- localizar o código do cockpit no frontend;
- entender como o estado é carregado e atualizado a partir da API de OracleOps;
- evoluir telas e componentes sem quebrar contratos nem tornar a experiência de operação confusa.

---

### 3.3.1 Princípios de design do frontend OracleOps

A camada de frontend do OracleOps v1 segue alguns princípios explícitos:

1. **Feature isolada e opinativa.**  
   O cockpit é implementado como um "feature" isolado (por exemplo, `features/oracleops`), com rotas próprias e componentes dedicados. Ele não se mistura com telas de usuário final, nem tenta resolver casos de uso de produto externo — o foco é operação interna.

2. **Navegação pensada para perguntas reais.**  
   As telas são desenhadas para responder rapidamente a perguntas como:
   - "o recorte da S33 está saudável agora?";
   - "quais componentes estão com problema?";
   - "que incidentes estão abertos?";
   - "qual é o estado dos SLOs críticos?";
   - "que runbook eu devo seguir?".
   Layouts e componentes são avaliados com base em quão rápido ajudam a responder essas perguntas, não em estética abstrata.

3. **Dependência explícita da API de OracleOps.**  
   O cockpit consome exclusivamente as rotas `ops_cockpit` definidas no backend. Ele não faz consultas diretas a outras APIs do sistema nem acessa bancos de dados por atalhos, o que mantém o acoplamento sob controle.

4. **Estados claros e legíveis.**  
   Componentes evitam estados ambíguos. Para cada pedaço de informação sensível (estado de componente, SLO, incidente), a UI sempre tenta mostrar: valor, contexto, e, quando apropriado, link para mais detalhes (dashboard, runbook, bundle de evidência).

---

### 3.3.2 Organização do código e rotas

O cockpit é organizado como um módulo de feature no frontend, por exemplo:

- `frontend/inspectah-ui/src/features/oracleops/`
  - `pages/OverviewPage.tsx`
  - `pages/ComponentDetailsPage.tsx`
  - `pages/IncidentsListPage.tsx`
  - `pages/IncidentDetailsPage.tsx`
  - `components/SloSummaryPanel.tsx`
  - `components/ComponentHealthTable.tsx`
  - `components/IncidentBadge.tsx`
  - `components/RunbookLinks.tsx`
  - `api/opsCockpitClient.ts`
  - `routes.ts`

As rotas do cockpit se integram ao roteador principal via `routes.ts`, expondo caminhos como:

- `/ops/cockpit/overview` — visão geral de saúde;
- `/ops/cockpit/components/:componentId` — detalhe de componente;
- `/ops/cockpit/incidents` — lista de incidentes;
- `/ops/cockpit/incidents/:incidentId` — detalhe de incidente.

Todos esses caminhos se apoiam nos endpoints descritos no backend (`/api/ops/cockpit/overview`, `/components`, `/incidents`, `/slos`).

---

### 3.3.3 Cliente de API e modelo de dados no frontend

Para evitar espalhar chamadas HTTP por várias partes da UI, a S33 introduz um cliente dedicado para o OracleOps:

**Módulo sugerido:** `frontend/inspectah-ui/src/features/oracleops/api/opsCockpitClient.ts`

Esse cliente encapsula chamadas como:

- `fetchOverview()` — consome `GET /api/ops/cockpit/overview` e retorna um objeto tipado com:
  - `componentsByState` (contagens);
  - `problematicComponents` (lista resumida);
  - `slos` (lista de SLOs com estado);
  - `activeIncidents` (incidentes ativos agregados por severidade);
- `fetchComponents()` — consome `GET /api/ops/cockpit/components`;
- `fetchComponentDetails(componentId)` — consome `GET /api/ops/cockpit/components/{componentId}`;
- `fetchIncidents(filters)` — consome `GET /api/ops/cockpit/incidents` com filtros;
- `fetchIncidentDetails(incidentId)` — consome `GET /api/ops/cockpit/incidents/{incidentId}`;
- `createIncident(payload)` — consome `POST /api/ops/cockpit/incidents`;
- `updateIncident(incidentId, patch)` — consome `PATCH /api/ops/cockpit/incidents/{incidentId}`;
- `fetchSlos()` — consome `GET /api/ops/cockpit/slos`.

As respostas são tipadas com interfaces/Typescript types, por exemplo:

- `HealthOverviewDto`, `ComponentSummaryDto`, `IncidentSummaryDto`, `IncidentDetailsDto`, `SloStatusDto`.

Isso garante que mudanças no contrato da API sejam detectadas cedo pelo compilador do frontend.

---

### 3.3.4 OverviewPage: visão geral de operação

A `OverviewPage` é a porta de entrada do cockpit e precisa responder rapidamente à pergunta: "como está o recorte da S33 agora?".

Responsabilidades da página:
- Chamar `fetchOverview()` ao carregar;
- Exibir:
  - um **resumo visual** (cards ou indicadores) de componentes por estado (OK, degradado, falhando);
  - uma tabela ou lista de **componentes problemáticos** com links para detalhe;
  - um painel de **SLOs selecionados** (`SloSummaryPanel`);
  - um resumo de **incidentes ativos** (por severidade), com link para a lista completa.

Estados importantes a serem tratados:
- carregando (spinner, skeletons);
- erro (mensagem clara, opção de retry);
- vazio (por exemplo, nenhum incidente ativo no momento).

A `OverviewPage` é também o lugar natural para expor links rápidos para runbooks genéricos ("como usar o cockpit", "como abrir incidente").

---

### 3.3.5 ComponentDetailsPage: foco em um componente

A `ComponentDetailsPage` serve para responder perguntas como:
- "o que está acontecendo com esta fonte específica?";
- "este pipeline está atrasado ou falhando?";
- "que incidentes já tivemos ligados a este componente?".

Responsabilidades da página:
- Chamar `fetchComponentDetails(componentId)` com base na rota;
- Exibir:
  - metadados do componente (nome, tipo, criticidade, descrições);
  - estado atual (OK/degradado/falhando) e, se relevante, razão (por exemplo, SLO violado, erros recentes);
  - SLOs associados e estado (listagem compacta, com link para visualização mais detalhada);
  - incidentes ativos/recentes relacionados ao componente, com links para `IncidentDetailsPage`;
  - seção de **RunbookLinks** com links para runbooks relevantes, mapeados a partir do tipo/criticidade do componente.

Além disso, pode oferecer links diretos para dashboards de observabilidade configurados no backend (URLs vindas do `components_map`).

---

### 3.3.6 IncidentsListPage e IncidentDetailsPage

A UI de incidentes precisa equilibrar duas coisas: visão geral e capacidade de aprofundar.

**IncidentsListPage**:
- Chama `fetchIncidents(filters)`;
- Permite filtrar por:
  - estado (aberto, em triagem, mitigado, resolvido, etc.);
  - severidade (LOW, MEDIUM, HIGH, CRITICAL);
  - componente;
  - período (últimas 24h, 7 dias etc., se disponível na API);
- Exibe uma tabela/lista com colunas como:
  - ID, título, estado, severidade, componente principal, timestamps relevantes.

**IncidentDetailsPage**:
- Chama `fetchIncidentDetails(incidentId)`;
- Exibe:
  - título, descrição, estado atual, severidade;
  - componentes e SLOs associados;
  - timeline de mudanças de estado (com timestamps e atores);
  - links para runbooks relevantes;
  - links para bundles de evidência (quando houver, mesmo que apenas como URLs/paths apontados pelo backend).
- Permite, quando apropriado, ações como:
  - transicionar o estado (por exemplo, de OPEN para TRIAGE, de MITIGATED para RESOLVED), chamando `updateIncident`;
  - adicionar comentários/observações (se a S33 incluir esse campo).

---

### 3.3.7 Componentes de apoio: SloSummaryPanel, ComponentHealthTable, RunbookLinks

Para evitar duplicação e manter a consistência da UI, a S33 sugere alguns componentes de apoio:

- **`SloSummaryPanel`**  
  Recebe uma lista de `SloStatusDto` e exibe:
  - nome/descrição curta do SLO;
  - estado atual (OK/VIOLATED/NO_DATA);
  - valor atual relevante (por exemplo, recência em segundos, percentual de disponibilidade);
  - indicativo visual simples (ícones ou badges).

- **`ComponentHealthTable`**  
  Exibe uma lista de `ComponentSummaryDto` com colunas para nome, tipo, criticidade, estado agregado e links para detalhe. É usada tanto na `OverviewPage` (em versão resumida) quanto em telas mais focadas, se necessário.

- **`RunbookLinks`**  
  Recebe uma lista de links de runbook (URLs ou caminhos resolvidos pelo backend) e os exibe de forma organizada, com ícones e descrições curtas. É usado em `ComponentDetailsPage` e `IncidentDetailsPage` para conectar a UI ao catálogo de runbooks.

Esses componentes ajudam a manter o cockpit visualmente coeso e reduzem a probabilidade de cada página implementar sua própria lógica de apresentação de SLOs, componentes e runbooks.

---

### 3.3.8 UX operacional e integração com ORR

Do ponto de vista de experiência, o cockpit precisa funcionar bem não apenas no dia a dia, mas também durante a ORR (G5):

- A `OverviewPage` é o ponto de partida natural para a etapa de "inspeção de saúde" da ORR;
- A `ComponentDetailsPage` e a `IncidentsListPage` são usadas para identificar e seguir um incidente do recorte;
- A `IncidentDetailsPage` é a ponte para bundles de evidência e runbooks;
- O `SloSummaryPanel` ajuda a responder rapidamente quais SLOs da S33 estão no alvo ou violados.

A arquitetura de frontend descrita aqui deve ser pensada para suportar esses roteiros de uso. Se, durante a ORR, o operador precisar recorrer sistematicamente a ferramentas ou telas fora do cockpit para responder às perguntas principais, isso é um sinal de que o desenho precisa ser revisto.

Este bloco deve ser tratado como referência direta para a implementação e revisão da feature `oracleops` no frontend. Mudanças significativas em rotas, componentes centrais ou na forma de consumir a API precisam ser refletidas aqui para manter a arquitetura viva e alinhada com o código.