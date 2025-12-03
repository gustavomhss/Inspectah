# Inspectah — Sprint 30 — Capítulo 3 — Bloco 3
## Frontend da S30 em Detalhe: Console de Fluxos, UX de Operação e Integração com APIs

Este bloco detalha o lado frontend da Sprint 30: como o Console de Fluxos se materializa na UI, quais componentes existem, como a experiência de operação de fluxo é orquestrada e como tudo isso conversa com as APIs definidas no backend.

A pergunta aqui é: **o que o operador realmente vê, clica e entende quando vai operar o fluxo de notícias‑pivô?**

---

### 3.3.1 Princípios de UX para o Console de Fluxos

O Console de Fluxos de S30 segue a gramática visual e de interação do Console/Admin já estabelecida em E26, com alguns princípios específicos:

1. "Fluxos" são objetos de primeira classe, não detalhes de infra  
   O operador enxerga fluxos como entidades nomeadas (ex.: "Fluxo Notícias Geral — Produção"), com estados, saúde e ações claras.

2. Operações de alto impacto devem ser óbvias e reversíveis  
   Pausar, retomar, promover e trocar agentes são ações centrais. Elas precisam ser fáceis de encontrar, ter feedback claro e, quando possível, oferecer trilha de auditoria visível.

3. Rastreabilidade tem que caber numa tela  
   O operador precisa conseguir reconstruir a jornada de uma notícia (ou de uma execução de fluxo) sem abrir 7 telas diferentes. A estrutura "lista de execuções → detalhe com timeline" é padrão.

4. Console não é IDE  
   A UI expõe poder operacional, não ferramentas de desenvolvimento avançadas. Edição de topologia de fluxo continua sendo responsabilidade de time técnico via templates/versões, não de drag‑and‑drop irrestrito em produção.

---

### 3.3.2 Módulo de Fluxos no frontend (`frontend/inspectah-ui/src/features/flows/`)

O frontend da S30 organiza o Console de Fluxos como um módulo dedicado em `src/features/flows/`, com os seguintes componentes principais (nomes ilustrativos, finais em Cap. 4):

- `FlowsListPage.tsx`  
  - Página de listagem de fluxos.
  - Responsabilidades:
    - consumir `GET /api/flows` via hooks de API;
    - exibir tabela com colunas: Nome, Tipo de entrada, Estado, Template de origem, Saúde (ícone), Última execução;
    - fornecer filtros por tipo de entrada (ex.: `noticia_texto`), estado e template;
    - linkar para `FlowDetailPage` ao clicar em um fluxo.

- `FlowDetailPage.tsx`  
  - Página de detalhe de um fluxo.
  - Responsabilidades:
    - consumir `GET /api/flows/{flow_id}`;
    - exibir metadados: nome, tipo_entrada, estado, template_origem, data de criação, último operador;
    - mostrar diagrama textual estrutural das etapas em ordem (ex.: lista vertical ou timeline), com tipo de etapa, papel de agente e agente concreto;
    - exibir ações principais (botões) agrupadas em "Operações":
      - `Pausar fluxo` / `Retomar fluxo`;
      - `Marcar como em teste` / `Marcar como ativo`;
      - `Trocar agente de etapa` (abre diálogo dedicado);
      - `Reprocessar items` (abre diálogo com limites);
    - seção "Execuções recentes": tabela com execuções (id, item_id, status, início, fim, duração, link para detalhe).

- `FlowExecutionDetailDrawer.tsx`  
  - Drawer/modal lateral para exibir detalhe de uma execução específica de fluxo.
  - Responsabilidades:
    - consumir `GET /api/flows/{flow_id}/executions/{execution_id}`;
    - mostrar timeline de etapas: ordem, tipo, status, duração, resumo de output/erro;
    - exibir tags com links para observabilidade (por exemplo, "Ver logs" e "Ver métricas" abrindo nova aba com URL pré‑montada para o stack de observabilidade, usando `exec_fluxo_id`);
    - dar contexto rápido: qual item foi processado (link para caso/notícia se aplicável).

- `FlowCreateFromTemplateDialog.tsx`  
  - Diálogo/wizard para criação de novo fluxo a partir de template.
  - Responsabilidades:
    - consumir lista de templates (por endpoint específico ou via `GET /api/flows/templates` se existir);
    - permitir seleção de `FlowTemplate` (ex.: `Fluxo_Noticias_Geral_v1`);
    - exibir campos necessários para parametrização: nome do fluxo, tipo de ambiente (sandbox/produção), bindings de agentes para cada papel;
    - ao confirmar, chamar `POST /api/flows/from_template`;
    - exibir toasts de sucesso/erro e redirecionar para `FlowDetailPage` do novo fluxo.

- `FlowStateBadge.tsx`  
  - Componente pequeno que exibe o estado do fluxo como badge (cores/estilos conforme design system):
    - `draft`, `em_teste`, `ativo`, `pausado`, `deprecado`.

- `FlowOperationsBar.tsx` (opcional, para organização)  
  - Componente que agrega os botões de operações principais com estados desativados/ativos conforme o estado atual do fluxo.

- `flows/api.ts`  
  - Hooks de acesso a API usando React Query ou equivalente:
    - `useFlowsList(query)`;
    - `useFlowDetail(flowId)`;
    - `useFlowExecutions(flowId, filters)`;
    - `useCreateFlowFromTemplate()`;
    - `useUpdateFlowState(flowId)`;
    - `useReplaceFlowAgent(flowId)`;
    - `useReprocessFlowItems(flowId)`.

---

### 3.3.3 Fluxos de interação principais no Console

Para garantir que a UI expressa o contrato da sprint, a S30 modela explicitamente alguns fluxos de interação centrais.

#### Cenário A — Criar um fluxo de notícias a partir de template

1. Operador abre `FlowsListPage` e aplica filtro `tipo_entrada = noticia_texto`.
2. Clica em "Criar fluxo" → abre `FlowCreateFromTemplateDialog`.
3. Seleciona template `Fluxo_Noticias_Geral_v1`.
4. Preenche nome, parâmetros mínimos e liga cada papel de agente a um agente concreto;
5. Confirma → requisição `POST /api/flows/from_template` é enviada;
6. Em caso de sucesso, UI mostra toast de confirmação e redireciona para `FlowDetailPage` correspondente ao novo fluxo.

#### Cenário B — Colocar fluxo em teste e depois promover para ativo

1. Em `FlowDetailPage`, operador vê fluxo recém‑criado em estado `draft`.
2. Clica em "Marcar como em teste" → abre diálogo de confirmação (opcionalmente com campo para `percentual_teste`).
3. UI chama `POST /api/flows/{flow_id}/state` com `novo_estado = em_teste` e `percentual_teste`.
4. Badge de estado atualiza para `em_teste`; seção de execuções passa a registrar execuções experimentais; UI pode exibir tag "em teste".
5. Após período de observação, operador volta ao detalhe, clica em "Marcar como ativo";
6. Nova chamada a `POST /api/flows/{flow_id}/state`, agora com `novo_estado = ativo`;
7. Badge mostra `ativo`, e políticas de roteamento se atualizam (verificadas via métricas e testes de S30).

#### Cenário C — Pausar fluxo com problema

1. Operador nota, via painel de métricas, aumento de falhas no fluxo de notícias.
2. Abre `FlowDetailPage` correspondente e clica em "Pausar fluxo".
3. UI exibe alerta sobre o efeito (fluxo não receberá novos eventos) e pede confirmação.
4. Chama `POST /api/flows/{flow_id}/state` com `novo_estado = pausado`.
5. Estado visual muda para `pausado`, e o operador pode verificar, via execuções e métricas, que eventos novos não estão mais caindo nesse fluxo.

#### Cenário D — Investigar a jornada de uma notícia

1. A partir de uma notícia específica (por exemplo, em UI de Casos ou via ID interno), operador chega a uma lista de execuções do fluxo ou busca pelo `item_id`.
2. Em `FlowDetailPage`, seção de execuções, filtra por `item_id` e encontra a execução desejada.
3. Clica na execução → abre `FlowExecutionDetailDrawer`.
4. Vê timeline das etapas com status, duração e resumos de output;
5. Se necessário, clica em "Ver logs" para abrir painel externo com logs detalhados, usando `exec_fluxo_id`.

---

### 3.3.4 Integração com as APIs de backend

A camada de frontend se comunica com as APIs definidas em `app/api/flow_console_routes.py`. Os hooks em `flows/api.ts` encapsulam esta integração.

Requisitos mínimos de integração:

- Todos os componentes de lista/detalhe usam os hooks (e, portanto, as APIs oficiais), nunca acessam dados de fluxo por caminhos alternativos.
- Mensagens de erro exibidas na UI refletem respostas estruturadas da API (por exemplo, erros de transição de estado, tentativas de reprocessamento fora de limites, etc.).
- Operações de escrita (criar fluxo, mudar estado, trocar agente, reprocessar) são sempre acompanhadas de feedback para o usuário (toasts/sinais visuais) e refletem o novo estado após sucesso.

---

### 3.3.5 Testes de frontend e contratos visuais

Para que S30 seja robusta, o módulo de fluxos precisa vir acompanhado de uma bateria mínima de testes de frontend:

- Arquivo sugerido: `frontend/inspectah-ui/src/features/flows/__tests__/flows_console.spec.tsx`.

Tipos de teste principais:

- **Testes de renderização e interação básica**  
  - `FlowsListPage` renderiza lista com dados fake e responde a filtros.
  - `FlowDetailPage` exibe corretamente estados, etapas e ações.

- **Testes de fluxo de criação**  
  - Simular preenchimento de `FlowCreateFromTemplateDialog` e checar chamada correta à API.

- **Testes de mudança de estado**  
  - Dado um fluxo em `draft`, clicar em "Marcar como em teste" leva à chamada correta.
  - Estados e labels visuais atualizam conforme esperado.

- **Testes de execução/detail drawer**  
  - `FlowExecutionDetailDrawer` apresenta timeline de etapas a partir de dados mockados;
  - Botão "Ver logs" monta corretamente a URL de logs (se previsto).

Snapshots (ou equivalente) podem ser usados para garantir que a estrutura básica do Console de Fluxos não degrada silenciosamente.

---

### 3.3.6 Aderência ao Design System e às regras de segurança

O Console de Fluxos S30 deve:

- Reutilizar componentes de design system (botões, tabelas, badges, toasts) para manter consistência com o restante do Admin.
- Respeitar regras de autenticação/autorização: botões de operação (promover, pausar, reprocessar) só aparecem para perfis autorizados.
- Exibir warnings claros para ações de alto impacto (por exemplo, reprocessamento de lote, pausa de fluxo ativo).

---

Com isso, o Bloco 3 do Capítulo 3 fixa o lado frontend/UX da Sprint 30: o módulo de Console de Fluxos, os componentes, os fluxos de interação e a integração com as APIs. O próximo bloco fecha o capítulo amarrando arquitetura completa, filemap final e coerência com gates/DoD em nível de sprint.

