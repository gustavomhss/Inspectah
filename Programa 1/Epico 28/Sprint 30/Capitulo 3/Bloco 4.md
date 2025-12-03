# Inspectah — Sprint 30 — Capítulo 3 — Bloco 4
## Filemap da S30, Pontos de Integração e Sanidade Arquitetural Final

Este bloco fecha o Capítulo 3 transformando a arquitetura da Sprint 30 em um **filemap concreto**, com caminhos, scripts, artefatos gerados e pontos de integração explícitos. A ideia é que qualquer pessoa consiga, a partir deste bloco, navegar o repo e entender onde a S30 vive.

---

### 3.4.1 Filemap de Documentação da Sprint 30

Documentos canônicos da S30, todos em `docs/`:

- `docs/sprint_30_cap_1_contexto_problemas_objetivos.md`  
  - Capítulo 1 completo (Blocos 1–4): contexto, problemas, objetivos, escopo negativo, riscos, cenários‑núcleo.

- `docs/sprint_30_cap_2_gates_metricas_dod.md`  
  - Capítulo 2 completo (Blocos 1–4): filosofia de gates, definição de G0–G5, métricas agregadas, DoD e CI/ORR.

- `docs/sprint_30_cap_3_arquitetura_filemap.md`  
  - Capítulo 3 completo (Blocos 1–4): arquitetura macro, backend, frontend, filemap, integrações.

- `docs/sprint_30_cap_4_execucao_evidencias.md`  
  - Capítulo 4: plano de execução, timeline da sprint, cenários de teste, checklist de evidências, notas de ORR.

Opcional, mas recomendado para reforçar E28:

- `docs/epics/e28_fluxo_de_agentes_configuravel_v1.md`  
  - Documento do épico E28 (já existente), que a S30 referencia como fonte de verdade.

---

### 3.4.2 Filemap de Backend — Domínio de Fluxos & Orquestração

#### Módulo de domínio de fluxos

- `app/flows/__init__.py`  
  - Inicialização do módulo.

- `app/flows/models.py`  
  - Definição das entidades v1.5: `Flow`, `FlowStep`, `FlowExecution`, `FlowStepExecution`, `FlowTemplate`, `FlowOperationLog`.

- `app/flows/schemas.py`  
  - Schemas Pydantic para APIs do console e serviços internos.

- `app/flows/repository.py`  
  - Repositórios para persitência e queries de fluxos, templates, execuções e logs de operação.

- `app/flows/service.py`  
  - Regras de negócio principais: criação de fluxo via template, mudança de estado, troca de agente, reprocessamento limitado, roteamento de eventos.

- `app/flows/routing_policy.py`  
  - Política centralizada de roteamento por `tipo_entrada` + estado de fluxo.

- `app/flows/execution_engine.py`  
  - Engine de execução de fluxo: cria execuções, percorre etapas, chama agentes, registra step executions.

- `app/flows/instrumentation.py`  
  - Helpers de métricas e logs estruturados para execuções de fluxo.

#### Integração com orquestração/ingestão

- `app/orchestration/dispatcher.py` (ou equivalente)  
  - Ponto em que eventos de ingestão são encaminhados a `route_event_to_flow`.

- `app/orchestration/__init__.py`  
  - Configuração geral de orquestração.

#### APIs para o Console de Fluxos

- `app/api/flow_console_routes.py`  
  - Endpoints do Console de Fluxos: lista, detalhe, criação a partir de template, mudança de estado, troca de agente, execuções, reprocessamento.

Conexões explícitas:

- `flow_console_routes.py` → `schemas.py` (para entrada/saída);
- `flow_console_routes.py` → `service.py` (para operações de domínio);
- `service.py` → `routing_policy.py` + `execution_engine.py` (roteamento + execução);
- `execution_engine.py` → `instrumentation.py` (telemetria).

---

### 3.4.3 Filemap de Backend — Migrations

Migrations específicas da S30, em `migrations/versions/`:

- `migrations/versions/0030_s30_flow_model_v15.py`  
  - Migration principal da sprint:
    - cria/tuneia tabelas de fluxos e execuções;
    - adiciona campos v1.5 (ex.: `percentual_teste`, `template_origem_id` etc.);
    - garante integridade referencial entre entidades.

Se necessário, migrations auxiliares (nomes ilustrativos, caso hajam):

- `migrations/versions/0031_s30_flow_templates_seed.py`  
  - Dados iniciais de `FlowTemplate` (ex.: inserção de `Fluxo_Noticias_Geral_v1`).

Regras de migração (relembrando):

- devem aplicar limpo em banco vazio e em banco pós‑S29;
- qualquer transformação de dados sensível deve ser idempotente e documentada.

---

### 3.4.4 Filemap de Frontend — Console de Fluxos

Módulo de UI para operação de fluxos, em `frontend/inspectah-ui/src/features/flows/`:

- `frontend/inspectah-ui/src/features/flows/FlowsListPage.tsx`  
  - Lista de fluxos com filtros e status.

- `frontend/inspectah-ui/src/features/flows/FlowDetailPage.tsx`  
  - Detalhe de um fluxo, diagrama textual, ações de operação e execuções recentes.

- `frontend/inspectah-ui/src/features/flows/FlowExecutionDetailDrawer.tsx`  
  - Drawer/modal para jornada de execução (timeline de etapas + links para observabilidade).

- `frontend/inspectah-ui/src/features/flows/FlowCreateFromTemplateDialog.tsx`  
  - Wizard de criação de fluxo a partir de template.

- `frontend/inspectah-ui/src/features/flows/FlowStateBadge.tsx`  
  - Badge de estado de fluxo (draft/em_teste/ativo/pausado/deprecado).

- `frontend/inspectah-ui/src/features/flows/FlowOperationsBar.tsx` (opcional)  
  - Componente que concentra botões de operação.

- `frontend/inspectah-ui/src/features/flows/api.ts`  
  - Hooks de acesso às APIs de backend (lista, detalhe, execuções, operações).

- `frontend/inspectah-ui/src/features/flows/__tests__/flows_console.spec.tsx`  
  - Testes automatizados do Console de Fluxos (renderização, ações, integração básica).

Integrações externas:

- Uso de componentes do design system global (tabelas, botões, badges, toasts);
- Navegação integrada ao roteador principal do app (ex.: `/admin/flows`, `/admin/flows/:id`).

---

### 3.4.5 Filemap de Scripts de Gates, Métricas e Bundles

Scripts da S30 em `bin/` (todos executáveis no CI):

- `bin/s30_g0_scope_and_alignment.sh`  
  - Verifica docs da sprint, alinhamento com E28, ausência de TODO/FIXME.

- `bin/s30_g1_flow_model_and_templates.sh`  
  - Valida migrations, schemas e templates de fluxo.

- `bin/s30_g2_flow_console_ops.sh`  
  - Testa Console de Fluxos (front + APIs).

- `bin/s30_g3_flow_operations_safety.sh`  
  - Exercita operações críticas (pausar, retomar, reprocessar) com segurança e logs.

- `bin/s30_g4_flow_observability.sh`  
  - Verifica métricas e logs estruturados de fluxos.

- `bin/s30_g5_e2e_canonical_flow.sh`  
  - Roda cenário end‑to‑end do fluxo de notícias‑pivô.

- `bin/s30_metrics_summary.sh`  
  - Consolida métricas agregadas de sprint em `S30_metrics_summary.json`.

- `bin/s30_bundle.sh`  
  - Empacota evidências e scorecards em `inspectah_s30_evidence_bundle.zip`.

Workflow de CI correspondente:

- `.github/workflows/s30-gates.yml`  
  - Orquestra a execução de todos os scripts acima, publica artefatos e falha em caso de gate vermelho.

---

### 3.4.6 Filemap de Artefatos Gerados (Scorecards, Evidências, Bundles)

Todos os artefatos gerados pela S30 vivem em `out/`.

Scorecards de gates:

- `out/scorecards/S30_G0_scope_and_alignment.json`
- `out/scorecards/S30_G1_flow_model_and_templates.json`
- `out/scorecards/S30_G2_flow_console_ops.json`
- `out/scorecards/S30_G3_flow_operations_safety.json`
- `out/scorecards/S30_G4_flow_observability.json`
- `out/scorecards/S30_G5_e2e_canonical_flow.json`

Scorecard agregado de métricas da sprint:

- `out/scorecards/S30_metrics_summary.json`

Evidências por gate:

- `out/evidence/S30_G0_scope_and_alignment/*`
- `out/evidence/S30_G1_flow_model_and_templates/*`
- `out/evidence/S30_G2_flow_console_ops/*`
- `out/evidence/S30_G3_flow_operations_safety/*`
- `out/evidence/S30_G4_flow_observability/*`
- `out/evidence/S30_G5_e2e_canonical_flow/*`

Resumo textual da ORR:

- `out/evidence/S30_ORR_summary.txt`

Bundle de evidências da sprint:

- `out/bundles/inspectah_s30_evidence_bundle.zip`  
  - Contém tudo o que é necessário para auditar a sprint: scorecards, evidências, resumo de ORR.

---

### 3.4.7 Pontos de Integração Críticos e Sanidade Arquitetural

Para garantir que a S30 não se transforme em um conjunto de partes soltas, este bloco explicita os pontos de integração mais sensíveis:

1. **Ingestão → Fluxos**  
   - `app/orchestration/dispatcher.py` chama `route_event_to_flow` (em `app/flows/service.py`) para todos os eventos `tipo_entrada = noticia_texto`.
   - Logs nessa fronteira incluem `flow_id` e `exec_fluxo_id` quando o fluxo aceita o evento.

2. **Fluxos → Agentes**  
   - `FlowExecutionEngine` chama agentes usando a camada de agentes existente (não redesenhada na S30), respeitando `agent_role` e `agent_binding` definidos em `FlowStep`.
   - APIs/clients de agentes não são reinventados nesta sprint; apenas usados de forma mais disciplinada.

3. **Fluxos → Observabilidade**  
   - Todos os caminhos de execução passam por `app/flows/instrumentation.py`.
   - Métricas e logs gerados aqui alimentam os gates G4 e G5, além de painéis operacionais.

4. **Fluxos → Console/Admin**  
   - `flow_console_routes.py` é a única porta de entrada para o Console de Fluxos.
   - O frontend de fluxos (`features/flows/*`) consome **exclusivamente** essas rotas.

5. **Fluxos → Programas Futuros (Debunker, Truth‑DB, Casos)**  
   - Embora a S30 não implemente Debunker nem Truth‑DB, ela estabelece que execuções de fluxo tenham IDs estáveis (`FlowExecution.id`, `FlowStepExecution.id`) que poderão, no futuro, ser referenciados por casos e evidências.

Sanidade final:

- Tudo que o Capítulo 1 promete tem casa neste filemap.
- Tudo que o Capítulo 2 exige (gates, métricas, bundle) tem scripts e caminhos explícitos.
- Backend, frontend, ingestão e observabilidade se encontram em pontos bem definidos, sem "fios desencapados".

Com isso, o Bloco 4 conclui o Capítulo 3 da Sprint 30: a arquitetura deixou de ser um desenho abstrato e virou um mapa navegável, com arquivos, scripts e integrações claros, pronto para ser usado no Capítulo 4 (Execução & Evidências).

