# Inspectah — Sprint 22 — Capítulo 5 (v3)
## Console de Ingestão 2.0 (UI) — Especificação Final orientada por Bret Victor

> Documento de especificação **normativa** para o Console de Ingestão 2.0 no frontend `inspectah-ui`. Não é prompt. Tudo aqui é contrato de produto + engenharia.
> Revisão liderada por **Bret Victor** (interação, visualização, fluxo de trabalho), com apoio de todo o conselho.

---

## 1. Visão Geral

### 1.1. Objetivo

O Console de Ingestão 2.0 é a **superfície visual** do subsistema de ingestão da Sprint 22. Ele permite que operadores e engenheiros:

- vejam, em um único lugar, o estado de ingestão de todas as fontes;
- entendam rapidamente *onde* há problemas e *por quê*;
- disparem ingestões manuais com feedback imediato e confiável;
- inspecionem o histórico de ingestões de uma fonte com clareza temporal.

A UI deve tornar **visível** o que a S22 já faz no backend: configs, runs, NDJSON, métricas. A regra orientadora de Bret Victor aqui é: *o operador nunca deve "chutar" o que está acontecendo; o estado do sistema tem que estar sempre óbvio na interface*.

### 1.2. Escopo

Incluído neste capítulo:

- item de menu e rotas de ingestão no `inspectah-ui`;
- tela de lista de ingestão (todas as fontes + estado de ingestão);
- tela de detalhe de ingestão da fonte (config, histórico, ações);
- visualização de run individual (modal ou página);
- visão de tempo (timeline simples) dos runs de uma fonte;
- estados de loading, erro, vazio, conflito;
- microcopy (textos de UI) e feedbacks;
- requisitos não funcionais (UX, desempenho, acessibilidade, i18n);
- matriz de testes frontend e critérios finais para o gate S22-G5.

Fora de escopo:

- alterações no backend S22 (este console consome o que já existe);
- qualquer interação direta com banco, Truth-DB ou blockchain;
- criação de novos tipos de fonte.

---

## 2. Princípios de Design (Bret Victor)

A equipe alinha os seguintes princípios como norte:

1. **Estado à vista**  
   A interface deve mostrar, sem cliques desnecessários:
   - quais fontes estão saudáveis;
   - quais estão com problemas;
   - quais estão paradas.

2. **Ação → Feedback imediato**  
   Toda ação de ingestão (rodar, mudar modo) deve gerar resposta visual clara em menos de 1 segundo: mudança de estado, toast, rótulos atualizados.

3. **Explorabilidade segura**  
   O usuário deve poder clicar e navegar sem medo de "quebrar" o sistema. A UI não oferece ações perigosas; o backend protege invariantes; erros são explicados.

4. **Tempo como primeira classe**  
   Ingestão é um processo que acontece no tempo. A UI deve mostrar uma **linha do tempo** simples dos runs de cada fonte, para que o operador veja padrões (ex.: fonte falhando vários dias seguidos).

5. **3 cliques para resposta**  
   Da home de admin até a resposta para "esta fonte está saudável?" não podem haver mais do que 3 cliques.

---

## 3. Navegação e Rotas

### 3.1. Menu lateral

No menu admin do `inspectah-ui`:

- Item: **Ingestão**
- Ícone: símbolo simples de fluxo/processo (seguir design system).
- Comportamento: redireciona para `/admin/ingestion`.

### 3.2. Rotas front

- `/admin/ingestion`  
  → **IngestionListPage** (lista de ingestão por fonte)

- `/admin/ingestion/sources/:sourceId`  
  → **IngestionSourceDetailPage** (detalhe de ingestão para uma fonte)

- `/admin/ingestion/runs/:runId` (opcional se usar página; se modal, rota interna)  
  → **IngestionRunDetailView** (detalhe de um run)

As rotas devem integrar com o router atual, respeitando padrões de loading e fallback existentes no app.

---

## 4. Contratos de Dados (UI ↔ Backend S22)

> Os tipos aqui são *exemplos normalizados*. A implementação real deve alinhar com os schemas Pydantic em `app/ingestion/schemas.py`.

### 4.1. Fonte (Source)

A UI de ingestão reutiliza a estrutura de fonte da S21:

```ts
type Source = {
  id: string;          // "source_123"
  name: string;        // "RSS Valor Econômico Demo"
  type: string;        // "news_rss" | "data_api" | ...
  is_active: boolean;  // true = ativa, false = desativada
};
```

### 4.2. Configuração de ingestão (IngestionConfig)

```ts
type IngestionMode = "MANUAL_ONLY" | "AUTOMATIC";

type IngestionConfig = {
  source_id: string;
  mode: IngestionMode;
  created_at: string;  // ISO 8601 UTC
  updated_at: string;  // ISO 8601 UTC
};
```

### 4.3. Run de ingestão (IngestionRun)

```ts
type IngestionStatus =
  | "SUCCESS"
  | "FAIL"
  | "RUNNING"
  | "PARTIAL_SUCCESS"
  | "PENDING"; // usado para estados intermediários

type IngestionRun = {
  run_id: string;
  source_id: string;
  status: IngestionStatus;
  started_at: string;     // ISO 8601 UTC
  finished_at?: string;   // ausente se RUNNING ou PENDING
  items_processed?: number;
  payload_ref?: string;   // ex.: "ndjson://.../run_abc123.ndjson"
};
```

### 4.4. Endpoints

1. `POST /admin/ingestion/{source_id}/run`

- Request body (opcional, se existir):

```json
{ "trigger_origin": "manual_ui" }
```

- Resposta 200:

```json
{
  "run_id": "run_abc123",
  "source_id": "source_123",
  "status": "RUNNING",
  "started_at": "2025-11-24T15:23:00Z"
}
```

- Erros:
  - 404: fonte não existe.
  - 409: já existe run em andamento.
  - 500: erro interno.

2. `POST /admin/ingestion/{source_id}/toggle-mode`

- Request:

```json
{ "new_mode": "AUTOMATIC" }
```

- Resposta 200:

```json
{ "source_id": "source_123", "mode": "AUTOMATIC" }
```

3. `GET /admin/ingestion/{source_id}/runs?limit=&offset=`

- Resposta:

```json
{
  "runs": [ /* IngestionRun[] */ ],
  "total": 37
}
```

4. `GET /admin/ingestion/runs/{run_id}`

- Resposta: `IngestionRun`.

---

## 5. Tela 1 — Lista de Ingestão (IngestionListPage)

### 5.1. Objetivo

- Dar uma visão **de radar** de todas as fontes e seus estados de ingestão.
- Sinalizar onde há problemas (falhas, falta de ingestão recente).
- Permitir ações rápidas: ver detalhe, rodar ingestão, mudar modo (opcional).

### 5.2. Layout

Componentes principais:

1. **Cabeçalho da página**
   - Título: "Ingestão"
   - Subtexto curto: "Status de ingestão por fonte"

2. **Barra de filtros**
   - Filtro por tipo de fonte (dropdown com opções derivadas do backend: `news_rss`, `data_api`, ...).
   - Filtro por estado da última ingestão: `Todas`, `Saudáveis (SUCCESS)`, `Falhando (FAIL)`, `Em andamento (RUNNING)`, `Nunca rodou`.
   - Campo de busca por nome de fonte (texto).

3. **Tabela de fontes**
   Colunas obrigatórias:
   - Nome da fonte
   - Tipo
   - Modo (badge Manual/Automático)
   - Última ingestão (data/hora ou "Nunca rodou")
   - Estado da última ingestão (badge de status)
   - Saúde (badge "OK", "Falhando", "Parada", derivada de heurísticas simples)
   - Ações (botões Ver detalhes / Rodar)

### 5.3. Derivação de "Última ingestão" e "Saúde"

A lista consome, para cada fonte, os dados do **último IngestionRun conhecido**.

- Última ingestão:
  - se existir `finished_at` ou `started_at`, exibir data/hora formatada localmente;
  - se nunca existiu run, mostrar "Nunca rodou".

- Saúde (heurística mínima):

  - `OK` (verde):
    - última ingestão com status SUCCESS;
    - e menos de X horas sem nova ingestão (X definido pela S22 doc, ex.: 24h).

  - `Falhando` (vermelho):
    - última ingestão com status FAIL ou PARTIAL_SUCCESS.

  - `Parada` (amarelo):
    - nunca rodou; ou
    - última ingestão SUCCESS mas há mais de X horas sem nova ingestão quando se espera ingestão recorrente (pode ser refinado em sprints futuras).

### 5.4. Ação "Rodar ingestão"

- Botão na coluna de ações, por linha.
- Comportamento:
  1. Ao clicar, dispara `POST /admin/ingestion/{source_id}/run`.
  2. Enquanto a request estiver pendente:
     - desabilitar botão;
     - mostrar spinner ou label "Rodando...".
  3. Em sucesso:
     - exibir toast: "Ingestão iniciada para [nome da fonte]";
     - refazer fetch da linha (ou da tabela) para refletir novo run (pode aparecer RUNNING como último status).
  4. Em erro 409:
     - toast: "Já existe uma ingestão em andamento para esta fonte.".
  5. Em erro 4xx/5xx genérico:
     - toast: "Não foi possível iniciar a ingestão. Tente novamente."

### 5.5. Modo de ingestão na lista

- A coluna "Modo" exibe um badge com texto:
  - `Manual` para `MANUAL_ONLY`;
  - `Automático` para `AUTOMATIC`.

- Opcional (recomendado):
  - clique no badge abre um pequeno menu com opções:
    - "Definir como Manual"
    - "Definir como Automático"
  - Em seleção, dispara `POST /admin/ingestion/{source_id}/toggle-mode`.
  - Em sucesso, atualiza badge;
  - Em erro, toast com mensagem clara.

### 5.6. Estados especiais

- **Sem fontes**:
  - mensagem: "Nenhuma fonte cadastrada. Use o Console de Fontes para criar fontes antes de configurar a ingestão.";
  - botão "Ir para Fontes" (link para tela de fontes).

- **Erro ao carregar**:
  - mensagem: "Erro ao carregar status de ingestão.";
  - botão "Tentar novamente".

- **Loading**:
  - skeleton de tabela ou spinner.

---

## 6. Tela 2 — Detalhe de Ingestão por Fonte (IngestionSourceDetailPage)

### 6.1. Objetivo

Dar visão completa da ingestão para **uma fonte específica**, incluindo:

- configuração atual de ingestão (modo);
- botão de ingestão manual, com feedback;
- histórico de runs organizados no tempo;
- visão de timeline (para Bret Victor: enxergar padrões ao longo do tempo).

### 6.2. Layout e seções

1. **Breadcrumb + cabeçalho**
   - Breadcrumb: `Ingestão / [Nome da Fonte]`.
   - Título grande: nome da fonte.
   - Subtítulo: tipo (ex.: `news_rss`) + badge de ativo/inativo.

2. **Cartão de status e configuração**
   - Campos:
     - Modo de ingestão (Manual/Automático) com seletor claro.
     - Estado atual (derivado do último run: badge SUCCESS/FAIL/RUNNING/NUNCA RODOU).
     - Última ingestão: data/hora.
     - Saúde: badge OK/Falhando/Parada.
   - Ações:
     - seletor de modo (drop-down ou toggle);
     - botão "Salvar" (se for formulário) ou atualização imediata (se for toggle inline);
     - tooltip explicando efeito do modo.

3. **Botão principal — "Rodar ingestão agora"**

- Botão destacado (primary), claramente visível.
- Mesmo comportamento da lista, com feedback extra:
  - ao clicar, mostrar estado "Rodando..." no botão;
  - exibir banner discreto dizendo "Ingestão iniciada. Atualizando histórico...".

4. **Histórico de ingestões (tabela)**

- Colunas mínimas:
  - `run_id` (link ou botão para detalhe);
  - Início (`started_at` formatado);
  - Fim (`finished_at` ou "Em andamento");
  - Duração (calculada na UI se ambos timestamps existirem);
  - Status (badge);
  - Items processed.

- Paginação: 20 runs por página, com indicadores de total.

5. **Timeline visual (faixa horizontal)**

- Abaixo ou acima da tabela, uma pequena timeline com marcadores para cada run, posicionados no tempo:
  - eixo X: tempo (ex.: últimos 7 dias);
  - cada run é um ponto colorido (verde = sucesso, vermelho = falha, amarelo = parcial/pendente);
  - hover em um ponto mostra tooltip com data, estado, items.

Essa timeline torna visível padrões como "falhou em sequência" ou "parou de rodar".

### 6.3. Detalhe de run (modal ou página)

Ao clicar em `run_id` ou em um ponto da timeline:

- abrir modal `IngestionRunDetailModal` ou página `IngestionRunDetailPage`.

Campos exibidos:

- Cabeçalho
  - Run: `run_id`
  - Fonte: nome (link de volta para detalhe)

- Métricas do run
  - Status
  - Início, fim, duração
  - Items processed

- Link técnico
  - `payload_ref` exibido em campo copyable (para devs);
  - texto de ajuda: "Este caminho aponta para o NDJSON bruto desta ingestão.".

- Estado de erro (se FAIL ou PARTIAL_SUCCESS)
  - mensagem curta amigável derivada de erro se o backend fornecer;
  - se não houver mensagem, texto padrão: "Esta ingestão terminou com falha. Consulte logs detalhados no backend.".

---

## 7. Estados, Erros e Microcopy

### 7.1. Status → texto e cor

Sugestão alinhada ao design system:

- SUCCESS → verde, label "Sucesso".
- FAIL → vermelho, label "Falhou".
- RUNNING → amarelo, label "Em andamento".
- PARTIAL_SUCCESS → laranja, label "Parcial".
- PENDING/NUNCA RODOU → cinza, label "Pendente" / "Nunca rodou".

### 7.2. Mensagens de erro (tabela)

- 400: "Requisição inválida para ingestão. Verifique os dados da fonte e tente novamente."
- 404: "Fonte ou ingestão não encontrada."
- 409: "Já existe uma ingestão em andamento para esta fonte."
- 500: "Erro interno ao processar a ingestão. Tente novamente. Se persistir, contate o responsável."

### 7.3. Mensagens de sucesso

- Ao rodar ingestão: "Ingestão iniciada para [nome da fonte].".
- Ao trocar modo: "Modo de ingestão atualizado para [Manual/Automático].".

---

## 8. Requisitos Não Funcionais

### 8.1. Desempenho

- IngestionListPage deve carregar em < 2s em ambiente de desenvolvimento razoável com ~200 fontes.
- Ações de run/toggle devem dar feedback visual em < 1s (mesmo que o backend finalize depois, o usuário vê que algo aconteceu).

### 8.2. Acessibilidade

- Todos os botões e links com `aria-label` adequado.
- Navegação por teclado suportada em:
  - tabela de fontes;
  - botões de rodar e ver detalhes;
  - modal de detalhe de run.

### 8.3. i18n

- Todas as strings de UI extraídas para o mecanismo de tradução existente.
- Chaves de exemplo:
  - `ingestion.title`
  - `ingestion.filters.type`
  - `ingestion.filters.status`
  - `ingestion.table.columns.name`
  - `ingestion.table.columns.mode`
  - `ingestion.actions.run_now`
  - `ingestion.actions.view_details`
  - `ingestion.messages.run_started`
  - `ingestion.messages.run_conflict`
  - etc.

---

## 9. Filemap Frontend (Refinado)

Dentro de `frontend/inspectah-ui` (ajustar nomes ao padrão real):

```text
src/
  features/
    ingestion/
      pages/
        IngestionListPage.tsx
        IngestionSourceDetailPage.tsx
      components/
        IngestionSourceTable.tsx
        IngestionFiltersBar.tsx
        IngestionModeBadge.tsx
        IngestionStatusBadge.tsx
        IngestionRunHistoryTable.tsx
        IngestionTimeline.tsx
        IngestionRunDetailModal.tsx
      api/
        ingestionApi.ts
      hooks/
        useIngestionSources.ts
        useIngestionRuns.ts
```

- `ingestionApi.ts`: funções puras para chamar os endpoints da S22.
- `useIngestionSources.ts`: hook para obter lista de fontes + estado de ingestão (pode compor dados de fontes e runs).
- `useIngestionRuns.ts`: hook para obter runs de uma fonte ou run individual.

---

## 10. Matriz de Testes Frontend

### 10.1. Unit

1. `IngestionModeBadge`
   - Renderiza corretamente "Manual" / "Automático".
   - Aplica classes/cores esperadas.

2. `IngestionStatusBadge`
   - Para cada status, renderiza label e estilo corretos.

3. `IngestionTimeline`
   - Dado um conjunto de runs, renderiza pontos consistentes.
   - Ordena pontos por tempo.

### 10.2. Integração

1. `IngestionListPage`
   - Com mocks de API, renderiza tabela com N fontes;
   - Filtro por tipo altera o conjunto mostrado;
   - Clique em "Rodar ingestão" chama API e dispara toast de sucesso/erro;
   - Clique em "Ver detalhes" navega para rota de detalhe.

2. `IngestionSourceDetailPage`
   - Renderiza dados de fonte + config + histórico;
   - Clique em "Rodar ingestão" atualiza histórico;
   - Clique em `run_id` abre modal/página de detalhe.

### 10.3. E2E (Cypress/Playwright)

**Cenário E2E 1 — Fonte RSS saudável**

- Abrir `/admin/ingestion`.
- Encontrar fonte RSS de teste.
- Ver colunas preenchidas (modo, última ingestão, estado).
- Rodar ingestão via botão.
- Ver toast de sucesso.
- Entrar no detalhe da fonte e ver novo run SUCCESS no histórico.

**Cenário E2E 2 — Fonte data_api saudável**

- Mesmo fluxo que RSS, com fonte `data_api`.

**Cenário E2E 3 — Fonte quebrada**

- Abrir `/admin/ingestion`.
- Encontrar fonte de teste quebrada.
- Clicar em "Rodar ingestão".
- UI mostra mensagem de erro apropriada.
- No detalhe, último run aparece como FAIL.

---

## 11. Gate S22-G5 (Admin UI) — Critérios Finais

O Console de Ingestão 2.0 será considerado **DONE** para a Sprint 22 quando todos os critérios abaixo forem verdadeiros:

1. **Funcionalidade**
   - Item "Ingestão" presente no menu e funcional.
   - IngestionListPage lista fontes com todas as colunas definidas.
   - IngestionSourceDetailPage exibe config, histórico e timeline da fonte.
   - É possível rodar ingestão manual a partir da lista e do detalhe.
   - Troca de modo funciona e reflete visualmente.

2. **Experiência**
   - A regra dos 3 cliques é satisfeita: a partir de `/admin`, o operador chega à resposta "esta fonte está saudável?" em até 3 cliques.
   - Estados de erro e loading são sempre tratados (nenhuma tela fica "morta").

3. **Testes**
   - Unit e integração de componentes/telas de ingestão passando.
   - Cenários E2E descritos na seção 10.3 passando em ambiente local/CI.

4. **Evidências**
   - `bin/s22_g5_admin_ui.sh` atualizado para rodar testes frontend relevantes (unit/integration/E2E, conforme capacidade do projeto).
   - `out/scorecards/S22_G5_admin_ui.json` com status PASS.
   - `out/evidence/S22_G5_admin_ui/` contendo:
     - prints das telas IngestionListPage e IngestionSourceDetailPage;
     - prints ou gravação dos fluxos E2E principais;
     - logs de execução dos testes.

5. **Integração CI**
   - Workflow `.github/workflows/s22-gates.yml` executa G5 (parte frontend) sem falhas.

Quando estes itens estiverem atendidos, o Console de Ingestão 2.0 da S22 passa a ser a **superfície oficial** para operar a ingestão, pronta para servir de base às próximas sprints (S23: classificação, S24: debunker, S25: governança/verdade) sem ambiguidades de comportamento ou lacunas de UX.

