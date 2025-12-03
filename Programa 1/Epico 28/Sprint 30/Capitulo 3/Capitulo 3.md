# Inspectah — Sprint 30 — Capítulo 3
## Arquitetura, Filemap e Pontos de Integração

Este capítulo fixa **como** a Sprint 30 será materializada no código, nos dados, na UI e na observabilidade. A ideia é evitar “arquitetura de PowerPoint”: tudo aqui precisa bater com:
- o contrato conceitual do Capítulo 1;
- a malha de gates e métricas do Capítulo 2;
- o estado atual do repositório após S29.

---

### 3.1 Visão Geral de Arquitetura da S30

A S30 adiciona uma camada de poder operacional sobre o que S29 já entregou. Em termos de arquitetura, o escopo da sprint toca quatro eixos principais:

1. **Domínio de Fluxos & Templates (backend)**  
   - Refinar o modelo de Fluxo de Agentes v1 → v1.5, incluindo suporte explícito a:
     - templates versionados de fluxo (com destaque para `Fluxo_Noticias_Geral_v1`);
     - estados operacionais (`draft`, `em_teste`, `ativo`, `pausado`, `deprecado`);
     - política de roteamento por tipo de entrada + estado.
   - Consolidar entidades de execução (Execução de Fluxo, Execução de Etapa) e logs de operação.

2. **Camada de Orquestração & Operações de Fluxo**  
   - Serviço responsável por:
     - criação de fluxos a partir de templates;
     - mudança de estados (test/ativo/pausado);
     - aplicação de política de roteamento;
     - operações de reprocessamento com limites.

3. **Console de Fluxos (frontend + APIs)**  
   - Tela(s) em `inspectah-ui` para listar, inspecionar e operar fluxos.
   - APIs REST/HTTP no backend para suportar todas as ações de console.

4. **Observabilidade de Fluxos (telemetria & logs)**  
   - Instrumentação de execuções de fluxo/etapa com IDs de correlação.
   - Métricas por fluxo e por etapa, alinhadas ao plano de observabilidade global.

A S30 se apoia em três grandes subsistemas já existentes:
- **Ingestão 2.0** (Programa anterior/E27): responsável por coletar notícias de fontes e tipificá-las como eventos do tipo `noticia_texto` (com possíveis subtipos). A S30 não reimplementa ingestão; ela consome o que ingestão entrega.
- **Console/Admin E26**: gramática visual, padrões de UX, autenticação e autorização básicas.
- **Infra de Observabilidade / OTel**: já usada para outros serviços da plataforma.

---

### 3.2 Arquitetura de Backend — Domínio de Fluxos

#### 3.2.1 Módulos principais

Domínio de fluxos fica concentrado em `app/flows/` (seguindo padrão já utilizado em outros domínios como `app/sources/`, `app/cases/`):

- `app/flows/models.py`  
  - Define entidades de persistência:
    - `Flow` — definição de fluxo (id, nome, versão, tipo_entrada, estado, template_origem_id, metadata);
    - `FlowStep` — etapas ordenadas do fluxo (id, flow_id, ordem, tipo_etapa, agent_role, config, flags);
    - `FlowExecution` — execução de fluxo para um item específico (id, flow_id, item_id, status, started_at, finished_at, metadata);
    - `FlowStepExecution` — execução de etapa (id, flow_execution_id, step_id, status, started_at, finished_at, output_resumo, erro_resumo);
    - `FlowTemplate` — template canônico (id, slug, versão, tipo_entrada, estrutura de etapas, constraints);
    - `FlowOperationLog` — trilha de auditoria de operações (id, flow_id, user_id, operação, payload, created_at, resultado).

- `app/flows/schemas.py`  
  - Schemas Pydantic para entrada/saída de APIs:
    - `FlowRead`, `FlowCreateFromTemplate`, `FlowUpdateState`, `FlowReplaceAgent`, etc.;
    - `FlowExecutionRead`, `FlowExecutionDetail`, `FlowStepExecutionRead`.

- `app/flows/repository.py`  
  - Abstrações de acesso a dados para fluxos, templates e execuções.

- `app/flows/service.py`  
  - Regras de negócio principais:
    - criação de fluxo a partir de `FlowTemplate`;
    - aplicação da política de estados (quem pode ir de `draft` → `em_teste` → `ativo` → `pausado`);
    - execução de operações `pause_flow`, `resume_flow`, `set_flow_state`, `replace_agent_for_step`;
    - API interna `route_event_to_flow` usada pela camada de ingestão/orquestração.

- `app/flows/routing_policy.py`  
  - Implementa a política única de roteamento:
    - dado (`tipo_entrada`, metadata de fonte, flags de teste), escolher:
      - qual `Flow` em estado `ativo` é responsável;
      - se algum fluxo `em_teste` deve receber fração do tráfego;
      - o que fazer em caso de ausência de fluxo ativo (fallback).

- `app/flows/execution_engine.py`  
  - Responsável por:
    - criar `FlowExecution` quando um evento entra no fluxo;
    - orquestrar a chamada a cada etapa (`FlowStep`) na ordem correta;
    - registrar `FlowStepExecution` com outputs e erros;
    - publicar eventos de telemetria (métricas + logs estruturados).

- `app/flows/instrumentation.py`  
  - Ponto único de integração com observabilidade:
    - funções helpers para emitir métricas (`fluxo_execucoes_total`, etc.);
    - wrappers para logs estruturados com IDs de correlação (`exec_fluxo_id`, `exec_etapa_id`).

#### 3.2.2 Migrations

Migrations da S30 vivem em `migrations/versions/` com nomes disciplinados, por exemplo:

- `migrations/versions/0030_s30_flow_model_v15.py`  
  - cria/tuneia tabelas:
    - `flow_flows`;
    - `flow_flow_steps`;
    - `flow_flow_executions`;
    - `flow_flow_step_executions`;
    - `flow_flow_templates`;
    - `flow_flow_operation_logs`.

Migrations devem ser:
- idempotentes em ambientes já migrados;
- compatíveis com dados gerados em S29 (upgrade suave de v1 → v1.5).

---

### 3.3 Arquitetura de Backend — APIs do Console de Fluxos

As APIs públicas para o Console de Fluxos ficam concentradas em `app/api/flow_console_routes.py`:

Principais endpoints (nomes ilustrativos, detalhamento final em Cap. 4):

- `GET /api/flows`  
  - Lista fluxos com filtros (tipo_entrada, estado, template_origem).

- `GET /api/flows/{flow_id}`  
  - Detalhe de um fluxo: metadados, etapas, estado atual, info de saúde básica.

- `POST /api/flows/from_template`  
  - Cria fluxo novo a partir de `FlowTemplate`, com parâmetros fornecidos.

- `POST /api/flows/{flow_id}/state`  
  - Atualiza estado (`draft`, `em_teste`, `ativo`, `pausado`, `deprecado`).

- `POST /api/flows/{flow_id}/replace_agent`  
  - Troca de agente de uma etapa específica.

- `GET /api/flows/{flow_id}/executions`  
  - Lista execuções recentes do fluxo, com paginação.

- `GET /api/flows/{flow_id}/executions/{execution_id}`  
  - Detalhe de execução (timeline de etapas, outputs, erros, links para logs/metrics).

- `POST /api/flows/{flow_id}/reprocess`  
  - Reprocessamento limitado de notícias (por ID, range de tempo, etc.) com uso de `FlowOperationLog`.

Todos os endpoints:
- usam schemas em `app/flows/schemas.py`;
- validam autorização (role de Operador/Admin);
- emitem logs estruturados de operação.

---

### 3.4 Arquitetura de Frontend — Console de Fluxos

O front da S30 vive em `frontend/inspectah-ui/src/features/flows/` (seguindo o padrão modular do UI):

Componentes principais:

- `FlowsListPage.tsx`  
  - Lista de fluxos com filtros, estados, tipo de entrada, health básico (ícones de erro/ok).

- `FlowDetailPage.tsx`  
  - Exibe:
    - metadados do fluxo (nome, id, template origem, tipo_entrada, estado);
    - diagrama textual/estrutural de etapas em ordem;
    - ações principais (botões): `Pausar`, `Retomar`, `Marcar como em teste`, `Marcar como ativo`, `Trocar agente`;
    - seção de execuções recentes (tabela resumida com link para detalhe).

- `FlowExecutionDetailDrawer.tsx`  
  - Drawer/modal que mostra a jornada de uma notícia:
    - linha do tempo das etapas;
    - status por etapa (ok/erro);
    - resumo de output;
    - link "ver em logs/observabilidade" (URL pré-montada para painel).

- `FlowCreateFromTemplateDialog.tsx`  
  - Wizard simplificado para criar fluxo a partir de template:
    - escolha do template (ex.: `Fluxo_Noticias_Geral_v1`);
    - parametrização de agentes por papel;
    - confirmação e criação.

- `FlowStateBadge.tsx`  
  - Componente pequeno e reutilizável para exibir estado (`draft`, `em_teste`, `ativo`, `pausado`, `deprecado`) com visual consistente.

A camada de acesso à API usa hooks em `frontend/inspectah-ui/src/features/flows/api.ts` (React Query ou similar), encapsulando chamadas aos endpoints descritos na seção 3.3.

O Console de Fluxos reutiliza o design system global (botões, tabelas, badges, toasts) definido em Programas/Sprints de E26.

---

### 3.5 Integração com Ingestão (entrada de notícias)

A ponte entre ingestão de notícias e fluxos é feita por um contrato interno simples:

- Ingestão, ao processar uma notícia, gera um evento interno (por exemplo, `IngestionEvent`) com campos mínimos:
  - `item_id` (id interno da notícia);
  - `tipo_entrada` (ex.: `noticia_texto`);
  - `fonte_id` (qual feed ou API originou o item);
  - `payload_raw`/`payload_normalized` (conteúdo relevante da notícia);
  - `metadata` (tags, categoria sugerida, timestamps, etc.).

- Um componente de orquestração (por exemplo, `app/orchestration/dispatcher.py`) chama:
  - `route_event_to_flow(event)` em `app/flows/service.py`;
  - que:
    - consulta `FlowRoutingPolicy` para escolher o fluxo;
    - cria `FlowExecution` e aciona `FlowExecutionEngine`.

S30 não refaz ingestão; ela garante que, uma vez que um evento de notícia chegue com `tipo_entrada` adequado, o fluxo de notícias‑pivô será escolhido e executado de forma previsível.

---

### 3.6 Arquitetura de Observabilidade para Fluxos

A S30 amarra o domínio de fluxos à camada de observabilidade existente.

#### 3.6.1 Métricas

Exportadas via OTel/Prometheus a partir de `app/flows/instrumentation.py`:

- `inspectah_flow_executions_total{flow_id, tipo_entrada, status}`
- `inspectah_flow_executions_success_total{flow_id, tipo_entrada}`
- `inspectah_flow_executions_failure_total{flow_id, tipo_entrada, error_class}`
- `inspectah_flow_latency_seconds_p95{flow_id, tipo_entrada}`
- opcional: `inspectah_flow_backlog_items{flow_id, step_id}`

Essas métricas são usadas pelos gates (G4, G5) e pelo painel de operação de fluxo de notícias.

#### 3.6.2 Logs estruturados

Todos os pontos críticos de execução chamam helpers que garantem inclusão de:
- `exec_fluxo_id`;
- `exec_etapa_id`;
- `flow_id`;
- `item_id`;
- `tipo_entrada`;
- `status`.

Logs são enviados para o stack de logging existente (Loki/Elastic/etc.), mas a S30 garante um formato mínimo estável para suportar reconstrução de jornada.

---

### 3.7 Filemap detalhado da Sprint 30

Abaixo, o filemap específico da S30, em cima do repositório do Inspectah. Apenas caminhos relevantes à sprint são listados.

#### 3.7.1 Documentação da Sprint 30

- `docs/sprint_30_cap_1_contexto_problemas_objetivos.md`  
  - Capítulo 1 completo (Blocos 1–4).

- `docs/sprint_30_cap_2_gates_metricas_dod.md`  
  - Capítulo 2 completo (Blocos 1–4).

- `docs/sprint_30_cap_3_arquitetura_filemap.md`  
  - Este capítulo.

- `docs/sprint_30_cap_4_execucao_evidencias.md`  
  - Plano de execução, cenários de teste, checklist de evidências (definido na própria S30).

#### 3.7.2 Backend — domínio de fluxos

- `app/flows/__init__.py`
- `app/flows/models.py`
- `app/flows/schemas.py`
- `app/flows/repository.py`
- `app/flows/service.py`
- `app/flows/routing_policy.py`
- `app/flows/execution_engine.py`
- `app/flows/instrumentation.py`

- `app/api/flow_console_routes.py`  
  - Rotas do Console de Fluxos.

#### 3.7.3 Backend — migrations

- `migrations/versions/0030_s30_flow_model_v15.py`  
  - Migration principal da Sprint 30.

#### 3.7.4 Frontend — Console de Fluxos

- `frontend/inspectah-ui/src/features/flows/FlowsListPage.tsx`
- `frontend/inspectah-ui/src/features/flows/FlowDetailPage.tsx`
- `frontend/inspectah-ui/src/features/flows/FlowExecutionDetailDrawer.tsx`
- `frontend/inspectah-ui/src/features/flows/FlowCreateFromTemplateDialog.tsx`
- `frontend/inspectah-ui/src/features/flows/FlowStateBadge.tsx`
- `frontend/inspectah-ui/src/features/flows/api.ts`
- `frontend/inspectah-ui/src/features/flows/__tests__/flows_console.spec.tsx` (testes principais).

#### 3.7.5 Scripts de gates e métricas

- `bin/s30_g0_scope_and_alignment.sh`
- `bin/s30_g1_flow_model_and_templates.sh`
- `bin/s30_g2_flow_console_ops.sh`
- `bin/s30_g3_flow_operations_safety.sh`
- `bin/s30_g4_flow_observability.sh`
- `bin/s30_g5_e2e_canonical_flow.sh`
- `bin/s30_metrics_summary.sh`
- `bin/s30_bundle.sh`

#### 3.7.6 Artefatos gerados por S30

- `out/scorecards/S30_G0_scope_and_alignment.json`
- `out/scorecards/S30_G1_flow_model_and_templates.json`
- `out/scorecards/S30_G2_flow_console_ops.json`
- `out/scorecards/S30_G3_flow_operations_safety.json`
- `out/scorecards/S30_G4_flow_observability.json`
- `out/scorecards/S30_G5_e2e_canonical_flow.json`
- `out/scorecards/S30_metrics_summary.json`

- `out/evidence/S30_G0_scope_and_alignment/*`
- `out/evidence/S30_G1_flow_model_and_templates/*`
- `out/evidence/S30_G2_flow_console_ops/*`
- `out/evidence/S30_G3_flow_operations_safety/*`
- `out/evidence/S30_G4_flow_observability/*`
- `out/evidence/S30_G5_e2e_canonical_flow/*`
- `out/evidence/S30_ORR_summary.txt`

- `out/bundles/inspectah_s30_evidence_bundle.zip`

---

### 3.8 Coerência entre Arquitetura, Gates e Objetivos

Por fim, o sanity check:

- O que o Capítulo 1 promete (fluxo‑pivô operável, estados fortes, rastreabilidade, observabilidade) está refletido em **componentes concretos** (`service`, `routing_policy`, `execution_engine`, `instrumentation`).
- O que o Capítulo 2 exige (gates G0–G5, métricas de sprint, bundle de evidências) tem caminhos e scripts explicitamente previstos no filemap.
- O Console de Fluxos está ancorado em componentes front e back bem localizados, evitando "UI fantasma" sem API correspondente.

Com isso, o Capítulo 3 entrega o mapa de terreno para a implementação da S30: qualquer pessoa que leia este documento sabe onde tocar no código, onde escrever scripts, onde cairão evidências — e como tudo isso se conecta ao contrato de E28.

