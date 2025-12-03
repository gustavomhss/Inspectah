# Inspectah — Sprint 30 — Capítulo 3 — Bloco 2
## Backend da S30 em Detalhe: Domínio de Fluxos, Orquestração e APIs

Este bloco desce o zoom na arquitetura de backend tocada pela Sprint 30. A pergunta aqui é: **quais módulos exatos fazem o fluxo de notícias‑pivô existir, ser operável e observável?**

---

### 3.2.1 Domínio de Fluxos (`app/flows/*`)

O domínio de fluxos é o coração da S30. Tudo o que a sprint promete — templates, estados fortes, execuções rastreáveis — precisa estar ancorado aqui.

#### Entidades principais (modelo lógico v1.5)

Representadas em `app/flows/models.py` e reflectidas em migrations da S30:

- `Flow`
  - Representa a definição de um fluxo específico (instância de um template).
  - Campos-chave (ilustrativo, nomes finais em Cap. 4):
    - `id` (UUID ou inteiro sequencial);
    - `nome` (ex.: "Fluxo Notícias Geral — Produção");
    - `slug` (para uso interno, ex.: `fluxo_noticias_geral_prod`);
    - `tipo_entrada` (ex.: `noticia_texto`);
    - `estado` (`draft`, `em_teste`, `ativo`, `pausado`, `deprecado`);
    - `template_origem_id` (FK para `FlowTemplate`);
    - `percentual_teste` (para fluxos em `em_teste`, quando aplicável);
    - `metadata` (JSONB/config, flags de domínio);
    - `created_at`, `updated_at`.

- `FlowStep`
  - Define a sequência de etapas que compõem um fluxo.
  - Campos-chave:
    - `id`;
    - `flow_id` (FK para `Flow`);
    - `ordem` (inteiro, define a ordem de execução);
    - `tipo_etapa` (ex.: `interprete`, `classificador`, `analista`, `debunker`, `decision_maker`);
    - `agent_role` (nome lógico do papel do agente, ex.: `news_interpreter_v1`);
    - `agent_binding` (identificador concreto do agente, ex.: ID de config externa);
    - `config` (JSON: parâmetros específicos da etapa);
    - `flags` (JSON: por exemplo, etapa opcional, etapa de debug etc.).

- `FlowExecution`
  - Representa a execução de um fluxo para um item de entrada (ex.: uma notícia).
  - Campos-chave:
    - `id`;
    - `flow_id`;
    - `item_id` (ID interno da notícia);
    - `tipo_entrada`;
    - `status` (`em_andamento`, `concluido`, `falhou`, `cancelado`);
    - `started_at`, `finished_at`;
    - `erro_resumo` (quando aplicável);
    - `metadata` (JSON: contexto adicional).

- `FlowStepExecution`
  - Representa a execução de uma etapa específica de um fluxo.
  - Campos-chave:
    - `id`;
    - `flow_execution_id` (FK);
    - `step_id` (FK para `FlowStep`);
    - `status` (`pendente`, `ok`, `erro`, `skipped`);
    - `started_at`, `finished_at`;
    - `output_resumo` (texto curto);
    - `erro_resumo`;
    - `raw_ref` (ponte para objeto bruto, se necessário).

- `FlowTemplate`
  - Define um template canônico para um tipo de fluxo.
  - Campos-chave:
    - `id`;
    - `slug` (ex.: `fluxo_noticias_geral`);
    - `versao` (ex.: `1`);
    - `tipo_entrada`;
    - `estrutura` (JSON com etapas padrão, papéis, restrições);
    - `ativo` (boolean, para habilitar/desabilitar template);
    - `metadata`;
    - `created_at`, `updated_at`.

- `FlowOperationLog`
  - Registra operações administrativas sobre fluxos.
  - Campos-chave:
    - `id`;
    - `flow_id`;
    - `user_id` (quem operou);
    - `operacao` (ex.: `set_state`, `replace_agent`, `reprocess`);
    - `payload` (JSON de detalhes);
    - `resultado` (`ok`, `erro` + mensagem);
    - `created_at`.

#### Camada de serviços (`app/flows/service.py`)

Responsável por concentrar as operações de domínio:

- `create_flow_from_template(template_slug, params)`
  - Carrega `FlowTemplate`, aplica parâmetros, cria `Flow` + `FlowStep`s.

- `set_flow_state(flow_id, novo_estado, actor)`
  - Valida transições permitidas (ex.: `draft → em_teste`, `em_teste → ativo`, `ativo → pausado`).
  - Dispara logs de operação (`FlowOperationLog`).

- `replace_agent_for_step(flow_id, step_id, novo_agent_binding, actor)`
  - Garante que a alteração é compatível com o `agent_role` esperado.
  - Registra operação para auditoria.

- `route_event_to_flow(event)`
  - Usa política de roteamento (abaixo) para escolher o fluxo.
  - Cria `FlowExecution` e invoca `FlowExecutionEngine`.

- `reprocess_items(flow_id, criteria, actor)`
  - Implementa reprocessamento limitado com validações de segurança (tamanho máximo, janela de tempo etc.).

#### Política de roteamento (`app/flows/routing_policy.py`)

Concentra a lógica que transforma eventos em escolha de fluxo:

- Entrada típica: `(tipo_entrada, fonte_id, metadata, flags)`.
- Saída: `RoutingDecision(flow_id, percent_teste, fallback_strategy)`.

Regras mínimas para o caso de notícias:

- Sempre que existir **exatamente um** fluxo em estado `ativo` para `tipo_entrada = noticia_texto`, ele recebe 100% do tráfego base.
- Fluxos em `em_teste` só recebem tráfego se `percentual_teste > 0`, e apenas essa fração.
- Fluxos `pausado`, `draft` ou `deprecado` nunca são candidatos a receber tráfego novo.
- Em ausência de fluxo ativo, aplicar estratégia de fallback definida (erro controlado, fallback genérico ou circuito aberto, conforme Cap. 1/2).

#### Engine de execução (`app/flows/execution_engine.py`)

Responsável por transformar uma decisão de roteamento em execução concreta do fluxo:

- `start_flow_execution(flow_id, item)`
  - Cria `FlowExecution` com status `em_andamento`.
  - Percorre `FlowStep`s em ordem, chamando agentes conforme `agent_binding`.
  - Para cada etapa, cria `FlowStepExecution` e registra status, tempos, outputs.
  - Emite eventos de telemetria (`instrumentation`) em cada etapa.
  - Ao final, marca `FlowExecution` como `concluido` ou `falhou`.

- Tratamento de erro:
  - Estratégias configuráveis: stop‑on‑first‑error, degradar para estado parcial, enviar para fila de revisão manual etc.;
  - Mesmo em erro, garantir sempre registro consistente de `FlowStepExecution`.

---

### 3.2.2 Orquestração com Ingestão

A S30 não cria uma nova camada gigantesca de orquestração; ela encaixa o domínio de fluxos no fluxo de ingestão existente.

Ponto de integração típico:

- Módulo de orquestração (por exemplo, `app/orchestration/dispatcher.py`) recebe um `IngestionEvent`:
  - `item_id`;
  - `tipo_entrada` (ex.: `noticia_texto`);
  - `fonte_id`;
  - `payload_normalized`;
  - `metadata`.

- O dispatcher chama:
  - `route_event_to_flow(event)` em `app/flows/service.py`;
  - obtém `RoutingDecision`;
  - aciona `FlowExecutionEngine`.

Garantias que S30 precisa instalar:

- Eventos com `tipo_entrada = noticia_texto` **nunca** são processados por caminhos paralelos (gambiarras) bypassando fluxos.
- Logs de integração sempre incluem `flow_id` e `exec_fluxo_id` quando um evento é aceito por um fluxo.

---

### 3.2.3 APIs do Console de Fluxos (`app/api/flow_console_routes.py`)

As rotas de API expõem o domínio de fluxos para o Console/Admin.

Rotas mínimas para S30 (nomes ilustrativos):

- `GET /api/flows`
  - Lista fluxos com filtros por `tipo_entrada`, `estado`, `template_origem`.
  - Usa paginação padrão da API do Inspectah.

- `GET /api/flows/{flow_id}`
  - Retorna:
    - dados do `Flow`;
    - lista ordenada de `FlowStep`s;
    - resumo de saúde (status, últimos erros, métricas básicas agregadas, quando disponível).

- `POST /api/flows/from_template`
  - Corpo: `FlowCreateFromTemplate`.
  - Ação: cria fluxo a partir de `FlowTemplate` com parâmetros de agente/config.

- `POST /api/flows/{flow_id}/state`
  - Corpo: `FlowUpdateState`.
  - Ação: transição de estado (`draft` → `em_teste` → `ativo` → `pausado` → `deprecado`), com todas as validações de domínio.

- `POST /api/flows/{flow_id}/replace_agent`
  - Corpo: `FlowReplaceAgentRequest`.
  - Ação: substitui o binding de agente em `FlowStep` específico.

- `GET /api/flows/{flow_id}/executions`
  - Lista `FlowExecution`s recentes com filtros de tempo/status.

- `GET /api/flows/{flow_id}/executions/{execution_id}`
  - Detalhe da execução, incluindo a sequência de `FlowStepExecution`s.

- `POST /api/flows/{flow_id}/reprocess`
  - Corpo: critérios de reprocessamento (IDs, janela de tempo, limites de volume).
  - Ação: agenda ou dispara reprocessamento limitado sob regras de segurança.

Todas as rotas:

- usam schemas em `app/flows/schemas.py` para validação e serialização;
- respeitam autenticação/autorização (só Operador/Admin de fluxos pode operar);
- geram entradas em `FlowOperationLog` para ações críticas.

---

### 3.2.4 Instrumentação e Telemetria (`app/flows/instrumentation.py`)

Para que métricas e logs existam sem virar um carnaval, a S30 centraliza a instrumentação em um módulo dedicado.

Responsabilidades:

- Expor helpers para:
  - `record_flow_execution_started(flow_execution)`;
  - `record_flow_execution_finished(flow_execution)`;
  - `record_flow_step_execution(step_execution)`;
  - `record_flow_error(flow_execution, error)`.

- Mapear execuções em métricas:
  - `inspectah_flow_executions_total{flow_id, tipo_entrada, status}`;
  - `inspectah_flow_executions_success_total{flow_id, tipo_entrada}`;
  - `inspectah_flow_executions_failure_total{flow_id, tipo_entrada, error_class}`;
  - `inspectah_flow_latency_seconds{flow_id, tipo_entrada}` (com p95 calculado no backend de métricas);
  - `inspectah_flow_backlog_items{flow_id, step_id}` quando houver fila explícita.

- Garantir que todos os logs estruturados de fluxo contenham:
  - `flow_id`;
  - `exec_fluxo_id`;
  - `exec_etapa_id` (quando aplicável);
  - `item_id`;
  - `tipo_entrada`;
  - `status`.

Com isso, qualquer ferramenta de observabilidade consegue reconstruir jornadas de notícias e gerar dashboards baseados em fluxo.

---

### 3.2.5 Migrations da S30 (`migrations/versions/*.py`)

A Sprint 30 introduz ou ajusta tabelas relacionadas a fluxos. A migration principal recomendada:

- `migrations/versions/0030_s30_flow_model_v15.py`
  - Cria tabelas que ainda não existiam em S29;
  - Altera colunas necessárias para v1.5 (ex.: adiciona `percentual_teste`, `template_origem_id`);
  - Garante chaves estrangeiras consistentes entre `Flow`, `FlowStep`, `FlowExecution`, `FlowStepExecution`, `FlowTemplate`, `FlowOperationLog`.

Requisitos:

- Migration aplica limpo em banco vazio.
- Migration aplica limpo em banco com dados de S29.
- Qualquer transformação de dados (ex.: migrar estados antigos para novos) é feita com scripts idempotentes e seguros.

---

Com isso, o Bloco 2 do Capítulo 3 fixa o esqueleto de backend da S30: domínio de fluxos, orquestração com ingestão, APIs de console e instrumentação. O próximo bloco entra na parte de frontend (Console de Fluxos) e amarra tudo ao filemap final da sprint.

