# Inspectah — Sprint 30 — Capítulo 4 — Bloco 2
## Plano Detalhado de Execução por Eixo (Backend, Frontend, Observabilidade, Gates)

Este bloco pega as fases macro da S30 e explode em **tarefas concretas por eixo de trabalho**. A ideia é evitar o clássico “cada um faz um pedaço” sem ninguém garantir que o conjunto fecha.

Eixos principais:
- Backend — Domínio de Fluxos & Orquestração;
- Backend — APIs do Console de Fluxos;
- Frontend — Console de Fluxos (UI/UX);
- Observabilidade & E2E;
- Gates, Métricas e Bundle.

Cada subtópico abaixo pode virar um checklist operacional para o squad.

---

## 4.2.1 Eixo Backend — Domínio de Fluxos & Orquestração

Este eixo garante que o **coração da S30** (fluxos v1.5) está sólido.

### A. Modelos e Migrations

Tarefas:
1. **Modelos v1.5** em `app/flows/models.py`:
   - Definir/ajustar:
     - `Flow` (estados, tipo_entrada, percentual_teste, template_origem_id, metadata);
     - `FlowStep` (ordem, tipo_etapa, agent_role, agent_binding, config, flags);
     - `FlowExecution` (status, tempos, item_id, tipo_entrada, metadata);
     - `FlowStepExecution` (status, tempos, outputs/erros resumidos);
     - `FlowTemplate` (slug, versão, tipo_entrada, estrutura JSON, ativo, metadata);
     - `FlowOperationLog` (operacao, user_id, payload, resultado, timestamps).

2. **Migration principal** `migrations/versions/0030_s30_flow_model_v15.py`:
   - Criar tabelas de fluxos, steps, execuções, templates e logs de operação se não existirem;
   - Alterar colunas antigas para o formato v1.5 (ex.: adicionar `percentual_teste`, `template_origem_id`);
   - Garantir chaves estrangeiras e índices mínimos.

3. **Seeds de templates** (se aplicável) em `0031_s30_flow_templates_seed.py`:
   - Inserir `FlowTemplate` para `Fluxo_Noticias_Geral_v1` com estrutura mínima válida;
   - Garantir idempotência (rodar 2x não duplica dados).

Saídas internas desta sub‑etapa:
- Migrations aplicam limpo em banco vazio;
- Migrations aplicam limpo em dump pós‑S29;
- `FlowTemplate` de notícias visível em queries simples.

### B. Serviço de Fluxos (`app/flows/service.py`)

Tarefas:
1. Implementar `create_flow_from_template(template_slug, params)`:
   - Carrega template por slug/versão;
   - Aplica parâmetros (nome, bindings de agentes, metadata);
   - Cria `Flow` + `FlowStep`s;
   - Retorna objeto criado.

2. Implementar `set_flow_state(flow_id, novo_estado, actor)`:
   - Validar transições permitidas (ex.: `draft → em_teste`, `em_teste → ativo`, `ativo → pausado`, `pausado → ativo`, `ativo → deprecado`);
   - Registrar `FlowOperationLog` com resultado;
   - Disparar eventuais hooks internos (ex.: invalidação de caches, se existirem).

3. Implementar `replace_agent_for_step(flow_id, step_id, novo_agent_binding, actor)`:
   - Validar compatibilidade com `agent_role` da etapa;
   - Atualizar `agent_binding` na etapa;
   - Registrar `FlowOperationLog` com diffs relevantes.

4. Implementar `route_event_to_flow(event)`:
   - Delegar escolha de fluxo a `routing_policy.select_flow(event)`;
   - Criar `FlowExecution` com status inicial;
   - Encaminhar para `FlowExecutionEngine`.

5. Implementar `reprocess_items(flow_id, criteria, actor)` com segurança:
   - Definir limites (ex.: máximo N items ou intervalo máximo de tempo);
   - Validar critérios (evitar reprocessamento massivo acidental);
   - Registrar `FlowOperationLog`;
   - Disparar execuções com marcação de reprocessamento.

### C. Política de Roteamento (`app/flows/routing_policy.py`)

Tarefas:
1. Definir estrutura `RoutingDecision` (flow_id, percent_teste, fallback_strategy).
2. Implementar função principal, por exemplo `select_flow(event)`:
   - Para `tipo_entrada = noticia_texto`:
     - Selecionar fluxo `ativo` único como destino padrão;
     - Injetar tráfego em fluxo `em_teste` segundo `percentual_teste`, se configurado;
     - Ignorar fluxos `draft`, `pausado`, `deprecado` como candidatos.
3. Definir comportamento de fallback em ausência de fluxo ativo:
   - Ex.: lançar erro controlado, registrar evento de atenção e seguir política definida no Cap. 2.

### D. Engine de Execução (`app/flows/execution_engine.py`)

Tarefas:
1. Implementar `start_flow_execution(flow_id, item)`:
   - Criar `FlowExecution` com status `em_andamento`;
   - Buscar `FlowStep`s em ordem;
   - Para cada etapa:
     - criar `FlowStepExecution` com status inicial;
     - chamar agente via camada de agentes existente;
     - atualizar status, tempos, outputs/erros;
     - emitir telemetria via `instrumentation`.
2. Definir estratégias de erro (stop‑on‑first‑error vs. degradação controlada) coerentes com Cap. 1/2.

### E. Integração com Orquestração/Ingressão (`app/orchestration/dispatcher.py`)

Tarefas:
1. Adaptar dispatcher para reconhecer `IngestionEvent` com `tipo_entrada = noticia_texto`.
2. Para esses eventos, chamar `route_event_to_flow(event)`;
3. Garantir que logs na fronteira ingestão→fluxos incluam:
   - `item_id`, `tipo_entrada`, `flow_id`, `exec_fluxo_id` (quando houver).

---

## 4.2.2 Eixo Backend — APIs do Console de Fluxos

Este eixo garante que o backend está **operável via HTTP**, não só via Python shell.

### A. Schemas (`app/flows/schemas.py`)

Tarefas:
1. Definir `FlowRead`, `FlowListItem`, `FlowStepRead`;
2. Definir `FlowCreateFromTemplateRequest` e `FlowCreateFromTemplateResponse`;
3. Definir `FlowUpdateStateRequest` e resposta associada;
4. Definir `FlowReplaceAgentRequest`;
5. Definir `FlowExecutionRead`, `FlowExecutionDetailRead`, `FlowStepExecutionRead`;
6. Definir `FlowReprocessRequest`.

### B. Rotas (`app/api/flow_console_routes.py`)

Tarefas:
1. Implementar `GET /api/flows`:
   - Filtros: `tipo_entrada`, `estado`, `template_origem`, paginação;
   - Uso de `FlowListItem` como resposta.

2. Implementar `GET /api/flows/{flow_id}`:
   - Agregar informações de `Flow`, `FlowStep`s, saúde básica;
   - Responder com `FlowRead` completo.

3. Implementar `POST /api/flows/from_template`:
   - Validar entrada com `FlowCreateFromTemplateRequest`;
   - Chamar `create_flow_from_template`;
   - Retornar dados do fluxo criado.

4. Implementar `POST /api/flows/{flow_id}/state`:
   - Validar transição com `set_flow_state`;
   - Propagar erros de transição proibida via mensagens claras.

5. Implementar `POST /api/flows/{flow_id}/replace_agent`:
   - Validar que etapa existe e pertence ao fluxo;
   - Chamar `replace_agent_for_step`.

6. Implementar `GET /api/flows/{flow_id}/executions`:
   - Filtros: tempo, status, item_id;
   - Paginação.

7. Implementar `GET /api/flows/{flow_id}/executions/{execution_id}`:
   - Consultar `FlowExecution` + `FlowStepExecution`s e montar resposta estruturada.

8. Implementar `POST /api/flows/{flow_id}/reprocess`:
   - Validar `FlowReprocessRequest`;
   - Chamar `reprocess_items`;
   - Retornar estado/resultado da operação.

### C. Testes de API

Tarefas:
1. Criar arquivo de testes, ex.: `tests/api/test_flow_console_routes.py`;
2. Testar:
   - caminhos felizes (happy path) das rotas principais;
   - erros de validação (ex.: transição proibida, reprocessamento exagerado);
   - autenticação/autorização (usuário sem permissão não opera fluxos).

---

## 4.2.3 Eixo Frontend — Console de Fluxos (UI/UX)

Este eixo garante que existe um **cockpit de fluxos** digno do nome.

### A. Estrutura de módulo

Tarefas:
1. Criar pasta `frontend/inspectah-ui/src/features/flows/`;
2. Integrar rotas do app principal (ex.: `/admin/flows`, `/admin/flows/:id`).

### B. Páginas e componentes principais

Tarefas:
1. `FlowsListPage.tsx`:
   - Consumir hook `useFlowsList`;
   - Renderizar tabela com colunas principais;
   - Implementar filtros (tipo de entrada, estado, template);
   - Linkar para detalhe de fluxo.

2. `FlowDetailPage.tsx`:
   - Consumir hook `useFlowDetail`;
   - Exibir metadados (nome, estado, tipo_entrada, template);
   - Exibir estrutura de etapas em ordem (lista/timeline);
   - Renderizar `FlowOperationsBar` com ações principais;
   - Exibir seção de execuções recentes (tabela com link para detalhe).

3. `FlowExecutionDetailDrawer.tsx`:
   - Consumir hook `useFlowExecutionDetail` ou dados passados por props;
   - Mostrar timeline de etapas com status, duração e resumos;
   - Mostrar links para observabilidade (logs/métricas) usando IDs de correlação;
   - Ser aberto a partir da tabela de execuções.

4. `FlowCreateFromTemplateDialog.tsx`:
   - Mostrar seletor de template (inicialmente, pelo menos o de notícias);
   - Campos de nome, parâmetros essenciais, bindings de agente;
   - Chamar `useCreateFlowFromTemplate` ao confirmar;
   - Redirecionar para `FlowDetailPage` do novo fluxo em caso de sucesso.

5. `FlowStateBadge.tsx` (e opcional `FlowOperationsBar.tsx`):
   - Exibir estado como badge consistente (cores/estilos do design system);
   - Agregar botões de operação em layout previsível.

### C. Hooks de API (`frontend/inspectah-ui/src/features/flows/api.ts`)

Tarefas:
1. Implementar hooks, por exemplo:
   - `useFlowsList(filters)`;
   - `useFlowDetail(flowId)`;
   - `useFlowExecutions(flowId, filters)`;
   - `useFlowExecutionDetail(flowId, executionId)`;
   - `useCreateFlowFromTemplate()`;
   - `useUpdateFlowState(flowId)`;
   - `useReplaceFlowAgent(flowId)`;
   - `useReprocessFlowItems(flowId)`.

2. Garantir tratamento de loading/erro padrão (spinners, toasts, mensagens claras).

### D. Testes de frontend (`__tests__/flows_console.spec.tsx`)

Tarefas:
1. Testar renderização e comportamento básico de `FlowsListPage`:
   - renderiza tabela com dados mock;
   - aplica filtros corretamente.

2. Testar `FlowDetailPage`:
   - exibe metadados e etapas;
   - ações de estado disparam callbacks esperados.

3. Testar `FlowCreateFromTemplateDialog`:
   - fluxo de criação chama hook com payload correto;
   - UI reage adequadamente a sucesso/erro.

4. Testar `FlowExecutionDetailDrawer`:
   - timeline aparecendo com dados expected;
   - links de observabilidade montados corretamente.

---

## 4.2.4 Eixo Observabilidade & E2E

Aqui garantimos que fluxos **não são caixa‑preta**.

### A. Instrumentação (`app/flows/instrumentation.py`)

Tarefas:
1. Implementar helpers para eventos de execução:
   - `record_flow_execution_started`;
   - `record_flow_execution_finished`;
   - `record_flow_step_execution`;
   - `record_flow_error`.

2. Publicar métricas mínimas:
   - `inspectah_flow_executions_total{flow_id, tipo_entrada, status}`;
   - `inspectah_flow_executions_success_total{flow_id, tipo_entrada}`;
   - `inspectah_flow_executions_failure_total{flow_id, tipo_entrada, error_class}`;
   - `inspectah_flow_latency_seconds{flow_id, tipo_entrada}` (para p95 no backend de métricas);
   - opcional: `inspectah_flow_backlog_items{flow_id, step_id}`.

3. Padronizar logs estruturados com campos obrigatórios:
   - `flow_id`, `exec_fluxo_id`, `exec_etapa_id`, `item_id`, `tipo_entrada`, `status`.

### B. Integração com a Engine de Execução

Tarefas:
1. Chamar helpers de instrumentação em pontos chave da `FlowExecutionEngine`:
   - início/fim de execução de fluxo;
   - início/fim de execução de etapa;
   - em casos de erro/exceção.

2. Garantir que execuções originadas do cenário E2E de notícias geram métricas/logs visíveis.

### C. Painel de Observabilidade

Tarefas (dependem da stack usada, mas conceitualmente):
1. Criar ou adaptar painel de métricas para o fluxo de notícias:
   - gráfico de execuções totais vs. falhas;
   - latência p95;
   - possivelmente gráfico de backlog.

2. Garantir que o painel consiga responder perguntas como:
   - “O fluxo está saudável?”;
   - “Qual a taxa de erro nos últimos X minutos?”;
   - “Há aumento de latência ou backlog?”

### D. Cenário E2E (`bin/s30_g5_e2e_canonical_flow.sh`)

Tarefas:
1. Definir dataset de notícias sintéticas (ex.: JSON/fixtures);
2. Escrever script que:
   - sobe ambiente mínimo (banco, backend, ingestão, etc.);
   - injeta notícias via mecanismo de ingestão;
   - espera processamento;
   - coleta execuções de fluxo de notícias;
   - coleta métricas e logs;
   - salva tudo em `out/evidence/S30_G5_e2e_canonical_flow/`.

3. Incluir pelo menos variantes de sucesso e erro simulados.

---

## 4.2.5 Eixo Gates, Métricas e Bundle

Este eixo costura tudo com o modelo de **“sprint com nota em ata”**.

### A. Scripts de Gates (`bin/s30_g*.sh`)

Tarefas:
1. Implementar todos os scripts de gate:
   - `s30_g0_scope_and_alignment.sh`;
   - `s30_g1_flow_model_and_templates.sh`;
   - `s30_g2_flow_console_ops.sh`;
   - `s30_g3_flow_operations_safety.sh`;
   - `s30_g4_flow_observability.sh`;
   - `s30_g5_e2e_canonical_flow.sh`.

2. Garantir características comuns:
   - idempotentes;
   - escrevem scorecard JSON em `out/scorecards/`;
   - escrevem evidências em `out/evidence/`;
   - retornam código de saída ≠ 0 em caso de falha.

### B. Métricas Agregadas (`bin/s30_metrics_summary.sh`)

Tarefas:
1. Implementar script que:
   - lê todos `S30_G*.json`;
   - extrai campos relevantes (status, métricas de eixo);
   - aplica regras de agregação do Bloco 3 do Cap. 2;
   - escreve `out/scorecards/S30_metrics_summary.json` com:
     - `epic`, `sprint`, `axes`, `status`, `reasons`.

2. Garantir que falhas em métricas críticas geram `status = "FAIL"`.

### C. Bundle de Evidências (`bin/s30_bundle.sh`)

Tarefas:
1. Implementar script que monta `out/bundles/inspectah_s30_evidence_bundle.zip` contendo:
   - todos `out/scorecards/S30_G*.json` + `S30_metrics_summary.json`;
   - todas as pastas `out/evidence/S30_G*`;
   - `out/evidence/S30_ORR_summary.txt` (preenchido ao final);
2. Confirmar que o bundle pode ser baixado de uma execução de CI e inspecionado localmente sem dependências extras.

### D. Workflow de CI (`.github/workflows/s30-gates.yml`)

Tarefas:
1. Criar/ajustar workflow com jobs:
   - `setup` (checkout, Python/Node, deps);
   - `gates-core` (G0–G4);
   - `gates-e2e` (G5);
   - `metrics-and-bundle` (metrics_summary + bundle);
2. Configurar o workflow para falhar em qualquer gate vermelho ou falha de script;
3. Publicar `inspectah_s30_evidence_bundle.zip` como artifact.

---

Com esse plano detalhado por eixo, o Bloco 2 do Capítulo 4 entrega o “como fazer” operacional da S30. Os blocos seguintes mergulham nos cenários de teste por gate, no ritual de ORR e no checklist de evidências que define quando a sprint pode ser declarada DONE sem gaguejar.