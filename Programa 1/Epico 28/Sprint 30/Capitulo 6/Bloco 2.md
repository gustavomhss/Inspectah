# Inspectah — Sprint 30 — Capítulo 6 — Bloco 2
## Tasks da Fundação de Fluxos (Eixo F) e do Console de Fluxos (Eixo C)

Este bloco detalha as tasks dos dois primeiros eixos da Sprint 30:
- **Eixo F — Fundação e Domínio de Fluxos v1.5**;
- **Eixo C — Console de Fluxos (APIs + Frontend)**.

Cada task vem com descrição, principais arquivos envolvidos, dependências e relação direta com gates e evidências.

---

## 6.2 Tasks de Fundação — Domínio de Fluxos v1.5 (Eixo F)

Estas tasks constroem o alicerce do modelo de fluxos v1.5, migrations, serviço de domínio, engine e roteamento. Sem elas, não existe fluxo real para operar via console.

### F1 — Consolidar modelos de fluxo v1.5

**Descrição**  
Implementar/ajustar os modelos de fluxo em `app/flows/models.py` para refletir o modelo v1.5: 
`Flow`, `FlowStep`, `FlowExecution`, `FlowStepExecution`, `FlowTemplate`, `FlowOperationLog`.

**Inclui**
- adicionar/ajustar campos:
  - em `Flow`: tipo_entrada, estado, percentual_teste, template_origem_id, metadata;
  - em `FlowStep`: ordem, tipo_etapa, agente_id, parametros, ativo;
  - em `FlowExecution`: status, tempos (inicio/fim), origem (ingestão, reprocessamento), metadata;
  - em `FlowStepExecution`: status, tempos, payload de entrada/saída, error_class;
  - em `FlowTemplate`: nome, descricao, tipo_entrada, configuracao de etapas;
  - em `FlowOperationLog`: operacao, parametros, resultado, user_id/origem, created_at.
- definir relacionamentos (FKs) e índices básicos (por flow_id, tipo_entrada, estado, timestamps);
- garantir compatibilidade com dados existentes pós‑S29.

**Arquivos principais**
- `app/flows/models.py`

**Dependências**
- Cap. 3 consolidado (seção de arquitetura de fluxos);
- Decisões do Cap. 5.2.1/5.2.2 (entidade de primeira classe + estados canônicos).

**Relação com gates**
- Gate G1 — modelo e templates de fluxos.

---

### F2 — Criar migration principal de fluxos v1.5

**Descrição**  
Criar `migrations/versions/0030_s30_flow_model_v15.py` para aplicar o modelo v1.5 tanto em banco vazio quanto em banco representativo pós‑S29.

**Inclui**
- criar/alterar tabelas necessárias para fluxos v1.5;
- ajustar colunas legadas (renomear, expandir tipos, adicionar defaults);
- criar índices mínimos (por flow_id, estado, tipo_entrada, created_at);
- garantir idempotência da migration.

**Arquivos principais**
- `migrations/versions/0030_s30_flow_model_v15.py`

**Dependências**
- F1 concluída (modelo definido).

**Relação com gates**
- Gate G1 — migrations aplicando limpo em banco vazio e pós‑S29.

---

### F3 — Seed/ajuste do template de fluxo de notícias

**Descrição**  
Garantir que `FlowTemplate` inclui um template canônico para o fluxo‑pivô de notícias (por exemplo, `Fluxo_Noticias_Geral_v1`) com topologia válida e alinhada ao desenho da S30.

**Inclui**
- criar migration adicional de seed (ex.: `0031_s30_flow_templates_seed.py`) ou script idempotente;
- definir estrutura de etapas na ordem:
  - intérprete → classificador → analista 1 → analista 2 → analista 3 → debunker 1 → debunker 2 → decision maker (ou variante definida no Cap. 3);
- marcar template como ativo e adequado para `tipo_entrada = noticia_texto`;
- implementar validador de topologia (sem ciclos proibidos, com etapa final bem definida) e rodá‑lo sobre o template.

**Arquivos principais**
- `migrations/versions/0031_s30_flow_templates_seed.py` (ou similar);
- `app/flows/service.py` (função de validação de template, se aplicável).

**Dependências**
- F1 e F2 concluídas.

**Relação com gates**
- Gate G1 — existência e validade de template canônico de notícias.

---

### F4 — Implementar serviço de fluxos (`app/flows/service.py`)

**Descrição**  
Implementar operações principais sobre fluxos, expondo a lógica de domínio que será usada por APIs e console.

**Inclui**
- `create_flow_from_template(template_id, overrides)`;
- `set_flow_state(flow_id, novo_estado)` com regras de transição formais;
- `replace_agent_for_step(flow_id, step_id, novo_agente)` com validações;
- `route_event_to_flow(evento_ingestao)` (interface com roteamento);
- `reprocess_items(flow_id, filtros, limites)` com políticas de segurança;
- registro de operações em `FlowOperationLog` (quem fez, quando, com quais parâmetros, resultado);
- tratamento de erros de domínio: transição inválida, template inexistente, reprocessamento excessivo, etc.

**Arquivos principais**
- `app/flows/service.py`

**Dependências**
- F1–F3 concluídas (modelo, migrations, template seed);
- Decisões de estados e transições do Cap. 5.2.2.

**Relação com gates**
- G1 — operações de modelo e template;
- G2 — operações usadas pelas APIs do console;
- G3 — operações seguras (reprocessamento, mudanças de estado).

---

### F5 — Implementar política de roteamento (`app/flows/routing_policy.py`)

**Descrição**  
Implementar a política de roteamento de eventos de ingestão para fluxos, com foco inicial em notícias (`tipo_entrada = noticia_texto`).

**Inclui**
- função principal `select_flow_for_event(evento)` ou equivalente;
- seleção de fluxo ativo principal para `noticia_texto`;
- aplicação de `percentual_teste` para enviar parte do tráfego a um fluxo em estado `em_teste`;
- comportamento definido para:
  - caso sem fluxo ativo (erro controlado ou fallback);
  - múltiplos fluxos ativos para o mesmo tipo de entrada (regra de desambiguação);
- logar decisões de roteamento quando relevante.

**Arquivos principais**
- `app/flows/routing_policy.py`
- eventualmente, integração com `app/orchestration/dispatcher.py`

**Dependências**
- F1–F4 (modelo, service e template configurados);
- contrato de `IngestionEvent` definido pela sprint de ingestão.

**Relação com gates**
- G2 — validação de console + APIs operando sobre fluxos reais;
- G5 — cenário E2E ingestão → fluxo.

---

### F6 — Implementar engine de execução de fluxo (`app/flows/execution_engine.py`)

**Descrição**  
Criar a engine responsável por percorrer as etapas de um fluxo, acionar agentes e registrar execuções.

**Inclui**
- criação de `FlowExecution` ao iniciar processamento de um item;
- criação de `FlowStepExecution` para cada etapa executada;
- integração com a camada de agentes (interprete, classificador, analistas, debunkers, decision maker);
- políticas de erro: parar no primeiro erro crítico ou degradar para caminho alternativo, conforme definido no Cap. 1/2;
- hooks para instrumentação (métricas e logs);
- retorno claro de resultado da execução (sucesso, erro, parcial, etc.).

**Arquivos principais**
- `app/flows/execution_engine.py`
- eventuais integrações com `app/agents/*` ou camada equivalente.

**Dependências**
- F1–F5 (modelo consolidado, service, roteamento);
- definições de contrato com agentes (ou mocks se agentes ainda estiverem em outro épico/sprint).

**Relação com gates**
- G3 — operações seguras de fluxo;
- G4 — observabilidade (via hooks de instrumentação);
- G5 — cenário E2E do fluxo de notícias.

---

## 6.3 Tasks do Console de Fluxos (Eixo C)

Estas tasks constroem o cockpit de operação de fluxos: APIs de console no backend e UI no frontend.

### C1 — Definir schemas de fluxo (`app/flows/schemas.py`)

**Descrição**  
Criar schemas Pydantic (ou equivalentes) para expor fluxos e execuções via API.

**Inclui**
- `FlowListItem`, `FlowRead`, `FlowStepRead` para leitura;
- `FlowCreateFromTemplateRequest/Response` para criação;
- `FlowUpdateStateRequest`, `FlowReplaceAgentRequest` para operações administrativas;
- `FlowExecutionRead`, `FlowExecutionDetailRead`, `FlowStepExecutionRead` para execuções;
- `FlowReprocessRequest` para reprocessamento;
- consistência com regras de domínio definidas em `service.py`.

**Arquivos principais**
- `app/flows/schemas.py`

**Dependências**
- F1–F4 (modelo e service definidos).

**Relação com gates**
- G2 — API do console de fluxos.

---

### C2 — Implementar rotas do Console de Fluxos (`app/api/flow_console_routes.py`)

**Descrição**  
Criar rotas HTTP para o Console de Fluxos operar o fluxo‑pivô de notícias e outros fluxos no futuro.

**Inclui**
- `GET /api/flows` — lista de fluxos com filtros (`tipo_entrada`, `estado`, etc.);
- `GET /api/flows/{flow_id}` — detalhe do fluxo (metadados, steps, estado);
- `POST /api/flows/from_template` — criação a partir de template;
- `POST /api/flows/{flow_id}/state` — mudança de estado com validações;
- `POST /api/flows/{flow_id}/replace_agent` — troca controlada de agente;
- `GET /api/flows/{flow_id}/executions` — lista de execuções recentes;
- `GET /api/flows/{flow_id}/executions/{execution_id}` — detalhe de uma execução;
- `POST /api/flows/{flow_id}/reprocess` — reprocessamento com limites de segurança.

**Arquivos principais**
- `app/api/flow_console_routes.py`

**Dependências**
- F4 (service de fluxos);
- C1 (schemas prontos).

**Relação com gates**
- G2 — funcionalidade do console no backend;
- G3 — segurança de operações (estado e reprocessamento).

---

### C3 — Criar módulo de frontend para Console de Fluxos

**Descrição**  
Estruturar o módulo de UI de fluxos no frontend do Inspectah, fornecendo o cockpit visual descrito no Cap. 3.

**Inclui**
- criação do diretório base `frontend/inspectah-ui/src/features/flows/`;
- componentes principais:
  - `FlowsListPage.tsx` — lista de fluxos com filtros (tipo, estado, etc.);
  - `FlowDetailPage.tsx` — detalhe do fluxo, com estado, steps e execuções recentes;
  - `FlowExecutionDetailDrawer.tsx` — visualização de jornada de uma execução (timeline de etapas);
  - `FlowCreateFromTemplateDialog.tsx` — criação de fluxo a partir de template;
  - `FlowStateBadge.tsx` — visualização de estado;
  - `FlowOperationsBar.tsx` — ações disponíveis (ativar, pausar, deprecar, reprocessar).

**Arquivos principais**
- `frontend/inspectah-ui/src/features/flows/FlowsListPage.tsx`
- `frontend/inspectah-ui/src/features/flows/FlowDetailPage.tsx`
- `frontend/inspectah-ui/src/features/flows/FlowExecutionDetailDrawer.tsx`
- `frontend/inspectah-ui/src/features/flows/FlowCreateFromTemplateDialog.tsx`
- `frontend/inspectah-ui/src/features/flows/components/*`

**Dependências**
- C2 (contrato mínimo das APIs estável);
- design system e infra de navegação do frontend já existentes.

**Relação com gates**
- G2 — verificação de que o console funciona de ponta a ponta;
- G5 — parte visual do cenário E2E.

---

### C4 — Implementar hooks de API para fluxos no frontend

**Descrição**  
Criar hooks para consumo das APIs de fluxo pelo frontend, isolando detalhes de fetch e estados de loading/erro.

**Inclui**
- `useFlowsList` — busca paginada/filtrada de fluxos;
- `useFlowDetail` — detalhe de fluxo selecionado;
- `useFlowExecutions` — execuções recentes de um fluxo;
- `useFlowExecutionDetail` — detalhe de uma execução;
- `useCreateFlowFromTemplate` — criação de fluxo;
- `useUpdateFlowState` — mudança de estado;
- `useReplaceFlowAgent` — troca de agente;
- `useReprocessFlowItems` — reprocessamento.

**Arquivos principais**
- `frontend/inspectah-ui/src/features/flows/api.ts`

**Dependências**
- C2 (APIs);
- C3 (componentes de UI que usam os hooks).

**Relação with gates**
- G2 — funcionamento integrado de console (UI + API).

---

### C5 — Escrever testes de frontend do Console de Fluxos

**Descrição**  
Adicionar testes automatizados para garantir que o Console de Fluxos renderiza e opera as principais funcionalidades sem regressões óbvias.

**Inclui**
- testes de `FlowsListPage`:
  - renderização da lista;
  - aplicação de filtros;
  - navegação para detalhe ao clicar em um fluxo;
- testes de `FlowDetailPage`:
  - exibição correta de estado e etapas;
  - disparo de operações (ativar, pausar, etc.) e tratamento de erros;
- testes de `FlowCreateFromTemplateDialog`:
  - fluxo completo de criação de fluxo;
  - mensagens de erro em caso de falha de backend;
- testes de `FlowExecutionDetailDrawer`:
  - exibição de timeline de execução;
  - links para logs/métricas quando existirem.

**Arquivos principais**
- `frontend/inspectah-ui/src/features/flows/__tests__/*.test.tsx`

**Dependências**
- C3 (UI criada);
- C4 (hooks implementados);
- infraestrutura de testes do frontend (jest, testing-library, etc.) já configurada.

**Relação com gates**
- G2 — garantia de qualidade mínima do Console de Fluxos.

---

## 6.4 Amarração F + C com Gates da Sprint 30

- **G1 — Modelo e templates de fluxos**  
  Depende diretamente de: F1, F2, F3, F4.

- **G2 — Console de fluxos (APIs + UI)**  
  Depende diretamente de: F4, F5 (roteamento para dar sentido ao fluxo), F6 (engine em uso nos testes), C1–C5.

- **G3 — Operações seguras de fluxo**  
  Usa F4 (regras de estado e reprocessamento) e C2/C3/C4 (como essas operações aparecem no console).

- **G5 — Cenário E2E do fluxo de notícias**  
  Usa a combinação de F1–F6 + C1–C5; o fluxo não é E2E se backend e console não estiverem conectados.

Com o Bloco 2, o squad tem o mapa completo das tasks de fundação de fluxos (Eixo F) e do Console de Fluxos (Eixo C). O Bloco 3 entra nas tasks de observabilidade, E2E, gates, bundle e CI; o Bloco 4 fecha com governança, ORR, backlog e checklist de GO.