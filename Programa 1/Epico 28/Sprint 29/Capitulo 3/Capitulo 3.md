# Sprint 29 — Capítulo 3
# Arquitetura, Filemap e Integrações

## 1. Papel do Capítulo 3 na Sprint 29

O Capítulo 3 traduz o contexto, os objetivos e os gates da Sprint 29 em **arquitetura concreta e filemap detalhado**. Ele responde a perguntas como:

- "Onde exatamente mora o cérebro de fluxos de agentes no backend?";
- "Como a UI fala com esse cérebro?";
- "Como o runtime de ingestão passa a respeitar o fluxo configurado por domínio?";
- "Quais arquivos e módulos existem em cada camada (backend, frontend, scripts, testes)?".

A ideia é que, com este capítulo, qualquer pessoa consiga navegar no repositório e entender como a S29 está estruturada sem adivinhar.

---

## 2. Visão geral da arquitetura da S29

A arquitetura da S29 é organizada em quatro blocos principais:

1. **Camada de domínio de fluxo de agentes** (backend):
   - modelos de dados (`AgentFlowConfig`, `AgentFlowStep`),
   - schemas Pydantic,
   - validador de invariantes,
   - serviço de fluxo.

2. **Camada de API de admin de fluxos** (backend):
   - rotas REST para criar/ler/atualizar fluxos,
   - mapeamento entre o domínio e a superfície HTTP.

3. **Camada de UI de fluxo de agentes** (frontend):
   - página de listagem por domínio,
   - editor linear de fluxo,
   - cliente de API da feature.

4. **Camada de runtime & observabilidade**:
   - adapter que resolve `AgentFlowConfig` por domínio para consumo no pipeline,
   - ajustes no pipeline de ingestão/agentes para chamar o adapter,
   - logs e métricas mínimas.

A S29 respeita o princípio: **catálogo de papéis de agentes e semântica de verdade continuam responsabilidade das sprints de Verdade & Interpretação (S23–S25)**. A S29 consome esse catálogo para montar fluxos configuráveis, em vez de redefini-lo.

---

## 3. Arquitetura de backend — Fluxos de agentes

### 3.1. Overview de módulos

No backend, a S29 introduz (ou consolida) o namespace `app/agents/flows/` com os seguintes módulos principais:

- `app/agents/flows/models.py` — modelos ORM/SQLAlchemy para `AgentFlowConfig` e `AgentFlowStep`.
- `app/agents/flows/schemas.py` — schemas Pydantic para entrada e saída das APIs.
- `app/agents/flows/validator.py` — funções de validação de invariantes de fluxo.
- `app/agents/flows/service.py` — operações de alto nível sobre fluxos (criar, atualizar, carregar por domínio) encapsulando modelo + validação.
- `app/agents/flows/runtime_adapter.py` — ponte entre o domínio de fluxo e o pipeline de ingestão/agentes.

Essa organização separa claramente:

- persistência (models),
- contrato externo/APIs (schemas),
- regras de negócio (validator + service),
- consumo em tempo de execução (runtime_adapter).

### 3.2. `models.py` — modelos de domínio

`AgentFlowConfig` e `AgentFlowStep` são definidos aqui como entidades de banco.

- `AgentFlowConfig` inclui:
  - `id` (chave primária),
  - `domain_key` (string, indexada),
  - metadados de auditoria (`created_at`, `created_by`, `updated_at`, `updated_by`),
  - `change_reason` (texto curto),
  - relacionamentos para `steps`.

- `AgentFlowStep` inclui:
  - `id` (chave primária),
  - `flow_id` (FK para `AgentFlowConfig`),
  - `position` (inteiro, indexado, com unicidade em `(flow_id, position)`),
  - `agent_role` (string ou enum, alinhado ao catálogo de papéis),
  - `params` (JSON ou campo equivalente).

Esse módulo é onde o banco passa a reconhecer fluxos de agentes como estruturas estáveis.

### 3.3. `schemas.py` — contratos Pydantic

Os schemas alinham modelo e API.

- Entrada:
  - `AgentFlowStepIn` — `position`, `agent_role`, `params`.
  - `AgentFlowConfigIn` — `domain_key`, `steps: list[AgentFlowStepIn]`.

- Saída:
  - `AgentFlowStepOut` — `id`, `position`, `agent_role`, `params`.
  - `AgentFlowConfigOut` — `id`, `domain_key`, metadados de auditoria, `steps` (lista de `AgentFlowStepOut`).

Esses schemas são usados diretamente nas rotas de admin (S29_G2) e no runtime adapter (para construção de objetos em memória).

### 3.4. `validator.py` — invariantes de fluxo

O módulo de validação implementa as invariantes da S29, por exemplo:

- fluxo não vazio;
- primeiro passo com papel permitido como entrada;
- papéis obrigatórios para domínios sensíveis (por exemplo, `DEBUNKER` antes de `DECISION_MAKER`);
- `DECISION_MAKER` somente na última posição (quando presente);
- proibição de posições duplicadas;
- rejeição de papéis desconhecidos.

Funções típicas:

- `validate_agent_flow(domain_key: str, steps: list[AgentFlowStepIn]) -> None`;
- helpers específicos como `ensure_required_roles(...)`, `ensure_decision_maker_last(...)` etc.

O módulo também centraliza tipos de exceção (por exemplo, `AgentFlowValidationError`) com códigos/mensagens padronizados para a API.

### 3.5. `service.py` — operações de alto nível

O serviço de fluxo de agentes encapsula a lógica de:

- criar fluxos (aplicar validação → persistir config + steps);
- atualizar fluxos existentes (carregar → aplicar novas steps → validar → persistir);
- carregar fluxos por `domain_key` ou `flow_id`.

Funções típicas:

- `create_agent_flow(config_in: AgentFlowConfigIn, actor: Optional[str]) -> AgentFlowConfig`;
- `update_agent_flow(flow_id: UUID, config_in: AgentFlowConfigIn, actor: Optional[str]) -> AgentFlowConfig`;
- `get_agent_flow_by_domain(domain_key: str) -> Optional[AgentFlowConfig]`.

Essa camada é onde as decisões de auditoria são aplicadas (registrar `updated_by`, `change_reason`, etc.).

### 3.6. `runtime_adapter.py` — consumo em pipeline

O adapter oferece uma função pública simples para o runtime:

- `get_agent_flow_for_domain(domain_key: str) -> AgentFlowRuntimePlan`

`AgentFlowRuntimePlan` pode ser:

- uma estrutura leve com a lista ordenada de papéis para execução (por exemplo, `[{"role": "INTERPRETER"}, {"role": "CLASSIFIER"}, ...]`);
- mais metadados úteis para log/observabilidade (por exemplo, `flow_id`, `version_tag`).

O adapter lida com:

- caso com fluxo configurado (usa config de banco);
- caso sem fluxo configurado (aplica fallback padrão e registra log/flag de observabilidade);
- caching leve, se necessário, para evitar consultas repetidas a cada item (desde que sem comprometer a consistência desejada).

---

## 4. Arquitetura de backend — API de admin de fluxos

### 4.1. Módulo de rotas

As rotas de admin de fluxo ficam em um módulo dedicado, por exemplo:

- `app/api/admin_agent_flows_routes.py`

Esse módulo expõe endpoints sob um prefixo como `/admin/agent-flows`, usando os schemas do módulo `schemas.py` e o serviço do módulo `service.py`.

### 4.2. Organização interna

O módulo segue o padrão dos demais endpoints de admin:

- dependências de autenticação/autorização reaproveitadas (por exemplo, `get_current_admin_user`);
- injeção de sessão de banco/Unit of Work conforme padrão do projeto;
- mapeamento claro entre exceções de validação (`AgentFlowValidationError`) e respostas HTTP (status `400`/`422`, payload com `code` + `message`).

As rotas não implementam lógica de negócio pesada; delegam para o serviço e apenas convertem resultados em respostas HTTP.

---

## 5. Arquitetura de frontend — UI de fluxo de agentes

### 5.1. Overview de pastas

No frontend, a feature de fluxo de agentes mora em:

- `frontend/inspectah-ui/src/features/agent-flows/`

Estrutura inicial sugerida:

- `AgentFlowsPage.tsx` — página de listagem/entrada da feature (seleção de domínio, acesso ao editor).
- `AgentFlowEditor.tsx` — editor linear de fluxo (lista de passos, botões para adicionar/remover/reordenar).
- `agentFlowsApi.ts` — cliente de API da feature, encapsulando chamadas ao backend.
- `agentFlowsTypes.ts` — tipos TypeScript da feature, espelhando os schemas do backend.
- `agentFlowsHooks.ts` (opcional) — hooks como `useAgentFlow(domainKey)` e `useSaveAgentFlow()`.

### 5.2. Integração com o router e layout admin

A página principal é integrada ao router admin do Inspectah, algo como:

- rota `/admin/agent-flows` → `AgentFlowsPage`;
- parâmetros/estado para escolher um `domain_key` e abrir diretamente o editor.

O layout reaproveita o design system existente (S26):

- uso de componentes comuns (tabelas, forms, modais);
- consistência visual com o restante do console admin.

### 5.3. Comportamento do `AgentFlowEditor`

O editor linear implementa:

- renderização da lista de passos na ordem atual;
- mecanismos para:
  - adicionar passo (escolhendo papel de um dropdown alinhado ao catálogo de papéis);
  - remover passo;
  - reordenar (setas ou drag & drop simples);
- botão de "Salvar" que dispara `PUT` ou `POST` no backend.

Tratamento de erros:

- mensagens de validação vindas da API (`AgentFlowValidationError`) exibidas de forma clara (ex.: toast ou banner explicando qual invariantes foi violada);
- campos com erro destacados quando relevante.

### 5.4. Cliente de API da feature

`agentFlowsApi.ts` encapsula:

- `fetchAgentFlowByDomain(domainKey): Promise<AgentFlowConfigOut>`;
- `createAgentFlow(payload: AgentFlowConfigIn): Promise<AgentFlowConfigOut>`;
- `updateAgentFlow(flowId, payload): Promise<AgentFlowConfigOut>`.

Ele centraliza:

- URLs base;
- mapeamento de erros (por exemplo, traduzir códigos de erro específicos em mensagens de alto nível para UI);
- tipagem forte entre TS e Pydantic.

---

## 6. Arquitetura de runtime — Integração com pipeline

### 6.1. Ponto de integração no pipeline

O pipeline de ingestão/agentes (por exemplo, em `app/ingestion/pipeline.py` ou equivalente) passa a:

1. Determinar o `domain_key` do item (já definido pela camada de classificação/roteamento).
2. Chamar `get_agent_flow_for_domain(domain_key)` no `runtime_adapter`.
3. Receber um `AgentFlowRuntimePlan` com a sequência de papéis.
4. Orquestrar a execução dos agentes seguindo essa sequência.

Isso substitui (ou envolve) qualquer lógica anterior que tinha tabela fixa de papéis por domínio embutida no código.

### 6.2. Fallback controlado

Se `get_agent_flow_for_domain` não encontrar fluxo configurado:

- aplica-se um fluxo padrão global (por exemplo, `INTERPRETER → CLASSIFIER → DECISION_MAKER`), definido em configuração;
- registra-se log estruturado indicando que o domínio X está em fallback;
- incrementa-se métrica de fallback (quando a infra de métricas estiver disponível).

Esse comportamento garante que a ausência de fluxo configurado não quebra o pipeline, mas também não passa despercebida.

### 6.3. Observabilidade

O runtime registra logs em um logger específico, por exemplo `agent_flows_runtime`, contendo:

- `domain_key`;
- `item_id` (ou equivalente);
- `flow_id` (quando houver);
- lista de papéis executados;
- indicador de uso de fallback.

Esses logs são usados pelo gate S29_G4 e ajudam a depurar comportamentos estranhos (por exemplo, se um domínio aparentemente configurado está caindo em fallback).

---

## 7. Segurança, permissões e governança mínima

### 7.1. Permissões de API

As rotas de admin de fluxo (S29_G2) são protegidas por:

- autenticação padrão do console admin;
- autorização adicional, se existir conceito de "permissão de fluxo" (por ex., apenas certos perfis podem alterar fluxos de domínios sensíveis).

Na S29, é suficiente reaproveitar o guard de admin existente, mas a arquitetura já prevê a possibilidade de reforço futuro, especialmente para domínios de alto impacto.

### 7.2. Auditoria mínima

Ao criar/atualizar fluxos, o serviço (`service.py`) registra:

- `created_by` / `updated_by` a partir do usuário autenticado;
- `change_reason` vindo da UI (campo obrigatório na tela ao salvar alterações);
- `updated_at` com timestamp da operação.

Esse rastro mínimo alimenta tanto a auditoria futura quanto os bundles de evidência (S29_G5).

---

## 8. Estratégia de migração e compatibilidade

A S29 introduz o fluxo configurável, mas não migra todos os domínios de uma vez.

### 8.1. Domínio piloto

Um domínio piloto é escolhido (por exemplo, "Notícia — Política BR") e migrado integralmente para o modelo novo:

- fluxo configurado em banco;
- UI capaz de editar esse fluxo;
- pipeline usando o fluxo configurado para esse domínio.

Esse domínio piloto é o foco de evidência dos gates G3 e G4.

### 8.2. Domínios antigos

Os demais domínios podem continuar temporariamente:

- no modelo antigo (fluxo definido em código),
- ou migrados de forma incremental ao longo de sprints futuras.

O adapter e o pipeline devem ser implementados de forma a:

- permitir coexistência dos dois modelos no curto prazo;
- favorecer uma migração incremental simples (por exemplo, regra "se tem fluxo configurado, usa; se não tem, usa lógica antiga").

---

## 9. Filemap detalhado da Sprint 29

Abaixo, o filemap sugerido/esperado para a S29, incluindo apenas os arquivos diretamente relevantes para o Épico E28 v1.

### 9.1. Backend — domínio, API, runtime

- `app/agents/flows/__init__.py`
- `app/agents/flows/models.py`
- `app/agents/flows/schemas.py`
- `app/agents/flows/validator.py`
- `app/agents/flows/service.py`
- `app/agents/flows/runtime_adapter.py`

- `app/api/admin_agent_flows_routes.py`

- `migrations/versions/00xx_s29_agent_flows.py` (nome com hash conforme padrão do projeto)

- `tests/agents/test_agent_flow_models.py`
- `tests/agents/test_agent_flow_validator.py`
- `tests/agents/test_agent_flow_api.py`
- (opcional) `tests/agents/test_agent_flow_runtime_adapter.py`

### 9.2. Frontend — UI de fluxo

- `frontend/inspectah-ui/src/features/agent-flows/AgentFlowsPage.tsx`
- `frontend/inspectah-ui/src/features/agent-flows/AgentFlowEditor.tsx`
- `frontend/inspectah-ui/src/features/agent-flows/agentFlowsApi.ts`
- `frontend/inspectah-ui/src/features/agent-flows/agentFlowsTypes.ts`
- (opcional) `frontend/inspectah-ui/src/features/agent-flows/agentFlowsHooks.ts`
- `frontend/inspectah-ui/src/features/agent-flows/__tests__/AgentFlowEditor.test.tsx`

### 9.3. Scripts de gates e evidências

- `bin/s29_g0_scope_and_baseline.sh`
- `bin/s29_g1_model_and_migrations.sh`
- `bin/s29_g2_api_and_validator.sh`
- `bin/s29_g3_ui_and_frontend_quality.sh`
- `bin/s29_g4_runtime_and_observability.sh`
- `bin/s29_g5_orr_and_bundle.sh`

- `out/evidence/S29_G0_scope_and_baseline/…`
- `out/evidence/S29_G1_model_and_migrations/…`
- `out/evidence/S29_G2_api_and_validator/…`
- `out/evidence/S29_G3_ui_and_frontend_quality/…`
- `out/evidence/S29_G4_runtime_and_observability/…`
- `out/evidence/S29_G5_orr_and_bundle/…`

- `out/scorecards/S29_G0_scope_and_baseline.json`
- `out/scorecards/S29_G1_model_and_migrations.json`
- `out/scorecards/S29_G2_api_and_validator.json`
- `out/scorecards/S29_G3_ui_and_frontend_quality.json`
- `out/scorecards/S29_G4_runtime_and_observability.json`
- `out/scorecards/S29_G5_orr_and_bundle.json`

### 9.4. Documentos da Sprint 29

- `docs/sprint_29_macro.md`
- `docs/sprint_29_capitulo_1.md`
- `docs/sprint_29_capitulo_2.md`
- `docs/sprint_29_capitulo_3.md` (este capítulo)
- `docs/sprint_29_capitulo_4.md` (Execução & Evidências)
- `docs/sprint_29_orr_summary.md`

---

## 10. Amarração final do Capítulo 3

O Capítulo 3 define onde cada peça da Sprint 29 mora e como elas se conectam:

- o domínio de fluxo de agentes vive em `app/agents/flows/`, com modelos, schemas, validação, serviço e runtime adapter bem separados;
- a API de admin expõe esse domínio de forma segura e testada;
- a UI oferece uma interface linear, simples e poderosa para operadores ajustarem o fluxo de um domínio;
- o runtime de ingestão passa a respeitar o fluxo configurado e a registrar sua execução de forma observável;
- o filemap garante que tudo isso é encontrável e auditável, alimentando os gates do Capítulo 2.

Com essa arquitetura estabelecida, o Capítulo 4 poderá descer para o nível de execução concreta:

- waves de implementação,
- sequência sugerida de tarefas,
- comandos de validação,
- e organização das evidências que irão preencher os diretórios e scorecards definidos aqui.

