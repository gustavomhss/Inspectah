# Inspectah — Sprint 30 — Capítulo 6
## Tasks da Sprint 30, Checklist de Execução e Backlog Imediato

O Capítulo 6 transforma tudo que foi definido nos Capítulos 1–5 em **lista de tasks concreta**, com dono, eixo e relação direta com gates e evidências.

Objetivos deste capítulo:
- traduzir objetivos, arquitetura, execução, governança e riscos em **tarefas executáveis**;
- oferecer um **checklist único** para acompanhar o progresso da S30;
- separar o que é **obrigatório para GO** do que vira **backlog explícito** pós‑sprint.

---

## 6.1 Estrutura de Tasks da Sprint 30

As tasks da S30 são organizadas em quatro grandes grupos:

1. Tasks de **fundação e domínio de fluxos** (backend, modelos, engine, roteamento);
2. Tasks de **Console de Fluxos** (APIs + frontend);
3. Tasks de **observabilidade, testes e gates** (telemetria, E2E, scripts de gates, CI, bundle);
4. Tasks de **governança e continuidade** (docs, ORR, riscos, handover para S31+).

Cada task a seguir pode (e deve) ser mapeada em cards de sprint (Jira/Linear/etc.), mantendo o texto daqui como descrição de referência.

---

## 6.2 Tasks de Fundação — Domínio de Fluxos v1.5

### T1 — Consolidar modelos de fluxo v1.5

**Descrição:**
Implementar/ajustar os modelos de fluxo em `app/flows/models.py` para refletir a versão v1.5 (Flow, FlowStep, FlowExecution, FlowStepExecution, FlowTemplate, FlowOperationLog), conforme Cap. 3 e 5.

**Inclui:**
- adicionar/ajustar campos de estado, tipo_entrada, percentual_teste, template_origem_id, metadata;
- definir relacionamentos e índices críticos;
- garantir que modelos suportam o fluxo‑pivô de notícias e fluxos futuros.

**Depende de:** Cap. 3 fechado; decisões do Cap. 5.2.1/5.2.2 consolidadas.
**Relaciona com gate:** G1 (modelo e templates).

---

### T2 — Criar migration principal de fluxos v1.5

**Descrição:**
Criar `migrations/versions/0030_s30_flow_model_v15.py` para aplicar o modelo v1.5 em banco vazio e banco pós‑S29.

**Inclui:**
- criação/alteraçao de tabelas de fluxos e execuções;
- ajustes em colunas legadas para comportar v1.5;
- criação de índices mínimos e FKs.

**Depende de:** T1.
**Relaciona com gate:** G1.

---

### T3 — Seed/ajuste do template de fluxo de notícias

**Descrição:**
Garantir que `FlowTemplate` inclui um template canônico para o fluxo de notícias (`Fluxo_Noticias_Geral_v1`, por exemplo) com topologia válida.

**Inclui:**
- migration opcional `0031_s30_flow_templates_seed.py` ou script idempotente de seed;
- estrutura de etapas em ordem (intérprete → classificador → analistas → debunkers → decision maker);
- validação de topologia via função/CLI interna.

**Depende de:** T1, T2.
**Relaciona com gate:** G1.

---

### T4 — Implementar serviço de fluxos (`app/flows/service.py`)

**Descrição:**
Implementar as operações principais sobre fluxos:
- `create_flow_from_template`;
- `set_flow_state` (com regras de transição formais);
- `replace_agent_for_step`;
- `route_event_to_flow`;
- `reprocess_items` com limites seguros.

**Inclui:**
- validações de domínio para estados e bindings de agentes;
- registro de operações em `FlowOperationLog`;
- tratamento de erros com mensagens claras.

**Depende de:** T1–T3.
**Relaciona com gates:** G1 (modelo), G2 (console), G3 (operações seguras).

---

### T5 — Implementar política de roteamento (`app/flows/routing_policy.py`)

**Descrição:**
Implementar função principal de roteamento de eventos de ingestão para fluxos, principalmente para `tipo_entrada = noticia_texto`.

**Inclui:**
- seleção de fluxo ativo para notícias;
- injeção opcional de tráfego em fluxo `em_teste` segundo `percentual_teste`;
- fallback definido para ausência de fluxo ativo;
- contrato claro com `IngestionEvent`.

**Depende de:** T1–T4.
**Relaciona com gates:** G2 (E2E console+API), G5 (E2E ingestão→fluxo).

---

### T6 — Implementar engine de execução de fluxo (`app/flows/execution_engine.py`)

**Descrição:**
Implementar a engine que percorre `FlowStep`s em ordem, chamando agentes e registrando execuções.

**Inclui:**
- criação de `FlowExecution` e `FlowStepExecution` com status e tempos;
- chamadas à camada de agentes para cada etapa;
- manuseio de erros (stop‑on‑first‑error vs degradação controlada), conforme Cap. 1/2;
- hooks para instrumentação.

**Depende de:** T1–T5.
**Relaciona com gates:** G3, G4, G5.

---

## 6.3 Tasks de Console de Fluxos (APIs + Frontend)

### T7 — Definir schemas de fluxo (`app/flows/schemas.py`)

**Descrição:**
Criar schemas Pydantic (ou equivalentes) para leitura/criação/atualização de fluxos e execuções.

**Inclui:**
- `FlowRead`, `FlowListItem`, `FlowStepRead`;
- `FlowCreateFromTemplateRequest/Response`;
- `FlowUpdateStateRequest`, `FlowReplaceAgentRequest`;
- `FlowExecutionRead`, `FlowExecutionDetailRead`, `FlowStepExecutionRead`;
- `FlowReprocessRequest`.

**Depende de:** T1–T4.
**Relaciona com gates:** G2.

---

### T8 — Implementar rotas do Console de Fluxos (`app/api/flow_console_routes.py`)

**Descrição:**
Criar rotas HTTP para operar fluxos e execuções pelo console.

**Inclui:**
- `GET /api/flows` (lista + filtros);
- `GET /api/flows/{flow_id}` (detalhe + steps);
- `POST /api/flows/from_template`;
- `POST /api/flows/{flow_id}/state`;
- `POST /api/flows/{flow_id}/replace_agent`;
- `GET /api/flows/{flow_id}/executions`;
- `GET /api/flows/{flow_id}/executions/{execution_id}`;
- `POST /api/flows/{flow_id}/reprocess`.

**Depende de:** T4, T7.
**Relaciona com gates:** G2, G3.

---

### T9 — Criar módulo de frontend do Console de Fluxos

**Descrição:**
Criar estrutura de UI em `frontend/inspectah-ui/src/features/flows/`.

**Inclui:**
- `FlowsListPage.tsx` (lista de fluxos);
- `FlowDetailPage.tsx` (detalhe, etapas, execuções recentes);
- `FlowExecutionDetailDrawer.tsx` (timeline de execução);
- `FlowCreateFromTemplateDialog.tsx`;
- `FlowStateBadge.tsx`/`FlowOperationsBar.tsx`.

**Depende de:** T8 (contrato de API estável) em nível mínimo.
**Relaciona com gates:** G2.

---

### T10 — Implementar hooks de API de fluxos no frontend

**Descrição:**
Criar hooks em `features/flows/api.ts` para consumir as rotas de fluxo.

**Inclui:**
- `useFlowsList`, `useFlowDetail`, `useFlowExecutions`, `useFlowExecutionDetail`;
- `useCreateFlowFromTemplate`, `useUpdateFlowState`, `useReplaceFlowAgent`, `useReprocessFlowItems`;
- tratamento de loading/erro padrão.

**Depende de:** T8, T9.
**Relaciona com gates:** G2.

---

### T11 — Escrever testes de frontend do Console de Fluxos

**Descrição:**
Adicionar testes automatizados para as telas principais do console.

**Inclui:**
- testes de renderização e filtros em `FlowsListPage`;
- testes de ações em `FlowDetailPage`;
- testes de criação em `FlowCreateFromTemplateDialog`;
- testes de timeline e links em `FlowExecutionDetailDrawer`.

**Depende de:** T9, T10.
**Relaciona com gates:** G2.

---

## 6.4 Tasks de Observabilidade, E2E, Gates e CI

### T12 — Implementar instrumentação de fluxos (`app/flows/instrumentation.py`)

**Descrição:**
Criar helpers e chamadas de instrumentação para métricas e logs de fluxo.

**Inclui:**
- funções `record_flow_execution_started/finished`, `record_flow_step_execution`, `record_flow_error`;
- emissão das métricas `inspectah_flow_*`;
- logs estruturados com campos mínimos.

**Depende de:** T1–T6.
**Relaciona com gates:** G4, G5.

---

### T13 — Ligar instrumentação na engine de execução

**Descrição:**
Chamar helpers de instrumentação nos pontos chave da `FlowExecutionEngine`.

**Inclui:**
- início e fim de execução de fluxo;
- início e fim de execução de etapa;
- situações de erro/exceção.

**Depende de:** T6, T12.
**Relaciona com gates:** G4, G5.

---

### T14 — Preparar dataset de notícias sintéticas para E2E

**Descrição:**
Criar dataset representativo de notícias sintéticas para o cenário E2E da S30.

**Inclui:**
- casos de sucesso “limpos”;
- casos com problemas propositalmente introduzidos;
- formatação compatível com ingestão.

**Depende de:** Especificação de ingestão e fluxo‑pivô.
**Relaciona com gates:** G5.

---

### T15 — Implementar script E2E de fluxo de notícias (`bin/s30_g5_e2e_canonical_flow.sh`)

**Descrição:**
Escrever script que sobe ambiente, injeta dataset, espera processamento e coleta evidências.

**Inclui:**
- execução de ingestão de notícias sintéticas;
- verificação de criação de execuções de fluxo;
- coleta de métricas e logs;
- salvamento em `out/evidence/S30_G5_e2e_canonical_flow/`.

**Depende de:** T5, T6, T12–T14.
**Relaciona com gates:** G5.

---

### T16 — Implementar scripts de gates G0–G4 (`bin/s30_g*.sh`)

**Descrição:**
Implementar scripts de gate para:
- G0 — escopo e alinhamento;
- G1 — modelo e templates;
- G2 — console de fluxos (API + UI);
- G3 — operações seguras;
- G4 — observabilidade de fluxos.

**Inclui:**
- verificação de docs, migrations, templates, APIs, front, operações, métricas e logs;
- escrita de scorecards JSON em `out/scorecards/`;
- geração de arquivos de evidência em `out/evidence/`.

**Depende de:** tasks T1–T13 (e T11 para a parte de front em G2).
**Relaciona com gates:** G0–G4.

---

### T17 — Implementar script de métricas agregadas (`bin/s30_metrics_summary.sh`)

**Descrição:**
Criar script que consolida os scorecards `S30_G*` em `S30_metrics_summary.json`.

**Inclui:**
- leitura de JSONs de gates;
- agregação de status e métricas de eixo;
- regra de decisão (qualquer gate crítico vermelho → `status = "FAIL"`).

**Depende de:** T16.
**Relaciona com:** ORR, decisão GO/NO‑GO.

---

### T18 — Implementar script de bundle de evidências (`bin/s30_bundle.sh`)

**Descrição:**
Criar script que monta `out/bundles/inspectah_s30_evidence_bundle.zip` com scorecards, evidências e resumo de ORR.

**Inclui:**
- inclusão de todos `S30_G*.json` + `S30_metrics_summary.json`;
- inclusão de todas as pastas `out/evidence/S30_G*`;
- inclusão de `out/evidence/S30_ORR_summary.txt`.

**Depende de:** T16, T17.
**Relaciona com:** ORR, inspeção futura da sprint.

---

### T19 — Criar/ajustar workflow de CI da S30 (`.github/workflows/s30-gates.yml`)

**Descrição:**
Configurar workflow de CI que roda todos os gates, métricas e bundle.

**Inclui:**
- jobs de setup, G0–G5, métricas e bundle;
- upload de `inspectah_s30_evidence_bundle.zip` como artifact;
- falha da pipeline se qualquer gate ou script relevante falhar.

**Depende de:** T16–T18.
**Relaciona com:** todos os gates, ORR.

---

## 6.5 Tasks de Governança, ORR e Backlog Pós‑S30

### T20 — Consolidar docs finais de sprint (Cap. 1–5)

**Descrição:**
Garantir que todos os capítulos da S30 estão atualizados e livres de TODO/FIXME.

**Inclui:**
- revisão de Cap. 1–5;
- alinhamento entre docs, código e gates;
- atualização de qualquer decisão ou risco de última hora.

**Depende de:** tasks principais implementadas.
**Relaciona com gates:** G0, ORR.

---

### T21 — Conduzir ORR da S30 e preencher resumo

**Descrição:**
Executar o ritual de ORR descrito no Cap. 4 e 5.

**Inclui:**
- inspeção de CI, scorecards e evidências;
- navegação pelo console e métricas;
- discussão de riscos residuais;
- preenchimento de `out/evidence/S30_ORR_summary.txt`.

**Depende de:** T16–T19.
**Relaciona com:** decisão GO/NO‑GO.

---

### T22 — Registrar backlog imediato pós‑S30

**Descrição:**
Converter aprendizados da S30, limitações conscientes e ideias de evolução em backlog para S31–S35.

**Inclui:**
- registrar itens como:
  - generalização de fluxos para outros tipos de entrada;
  - melhorias de UX no Console de Fluxos;
  - refinamentos de limites de reprocessamento;
  - extensões de telemetria e dashboards.

**Depende de:** T21 (ORR) e insights de operação.
**Relaciona com:** planejamento de S31–S35.

---

## 6.6 Checklist Resumido de Tasks Críticas para GO

Para fins de acompanhamento rápido, a S30 só é considerada pronta para GO se, no mínimo, as seguintes tasks estiverem DONE com qualidade:

- [ ] T1–T6 (domínio de fluxos v1.5 implementado);
- [ ] T7–T11 (Console de Fluxos funcional, com testes básicos);
- [ ] T12–T15 (instrumentação, dataset e cenário E2E implementados);
- [ ] T16–T19 (gates, métricas, bundle e CI rodando verdes);
- [ ] T20–T21 (docs consolidados e ORR realizado com decisão GO documentada).

A T22 é obrigatória como **registro de continuidade**, mas não bloqueia o GO técnico — ela bloqueia, conceitualmente, o fechamento elegante da S30 como peça do Épico E28.

Com isso, o Capítulo 6 encerra a especificação da Sprint 30 em modo 100% operacional: qualquer pessoa que leia este capítulo deve conseguir, com os capítulos anteriores, **rodar, inspecionar e fechar a sprint sem depender de conhecimento oral ou memória seletiva.**