# Inspectah — Sprint 23 — Capítulo 4 (Plano de Execução v2)

## 0. Premissas e ponto de partida

- Branch de trabalho: `feature/s23_agent_committees` (nome exato pode variar, mas toda a execução da S23 deve acontecer em uma branch dedicada da Sprint 23).
- Documento de referência obrigatório antes de qualquer código:
  - `docs/sprint_23_capitulo_1_contexto.md` (visão geral, squads, limites da S23).
  - `docs/sprint_23_capitulo_2_gates.md` (G0–G8, critérios de GO/NO_GO).
  - `docs/sprint_23_capitulo_3_filemap.md` (mapa de arquivos, pastas e contratos).
- Escopo da S23: camada de AGENTES (interpretação, classificação e debunk) com:
  - Console de administração de agentes (estilo “criar GPT”) para admins.
  - Modelo de comitês com redundância tripla por camada (dois debunkers + mediador).
  - Diretivas e perfis versionados, auditáveis, voltados apenas a produção de relatórios (bundles de informação), nunca “conversa solta”.
  - Chave global de controle de modelos (update imediato vs buffer de X dias) + override por agente.
  - Hooks claros para integrar com pipeline de consulta/Truth-DB nas Sprints futuras, sem tentar entregar “tudo” agora.

## 1. Trilha A — Modelo de domínio, persistência e API de agentes

### A1. Modelos e schema de agentes e comitês

Objetivo: criar a espinha dorsal de dados para Agents e Committees, com versionamento de instruções e histórico de execuções.

Arquivos principais (conforme Capítulo 3):
- `app/agents/models.py`
- `app/agents/schemas.py`
- `app/agents/repository.py`
- `app/agents/service.py`
- `migrations/versions/00xx_s23_agents_schema.py`

Entregas:
- Entidades mínimas:
  - `AgentProfile`:
    - id (UUID), name, description, layer (ex.: `"classification"`, `"interpretation"`, `"debunk"`), role (ex.: `"debunker_1"`, `"debunker_2"`, `"mediator"`), status (active/inactive), default_model, allowed_models, kb_refs (lista de caminhos/ids), created_at, updated_at.
  - `AgentInstructionVersion`:
    - id, agent_id (FK), version (semântico ou incremental), instructions_text (markdown), metadata (JSON: labels, tags), created_at, created_by.
  - `AgentCommittee`:
    - id, name, layer (classification / interpretation / debunk / aggregator), description, members (lista de agent_ids com papel), min_quorum (default 3, mas flexível), created_at.
  - `AgentRun`:
    - id, committee_id, input_ref (id da consulta / fato / evento), payload_snapshot (JSON com o que foi enviado para os LLMs), result_bundle_ref (hash ou caminho no evidence vault), status (PENDING/RUNNING/SUCCESS/FAIL), error (texto opcional), started_at, finished_at.

Critérios:
- Migrations idempotentes e com downgrade definido.
- Regras básicas de integridade (FKs, NOT NULL onde faz sentido, enums consistentes com Capítulo 2).

### A2. Serviços e contratos de domínio

Objetivo: encapsular lógica de negócio de Agents e Committees em serviços limpos, testáveis, sem acoplamento direto com cliente GPT ainda.

Arquivos:
- `app/agents/service.py`
- `app/agents/contracts.py` (separar DTOs internos, se necessário).

Operações mínimas:
- `create_agent_profile`, `update_agent_profile`, `archive_agent_profile`.
- `create_instruction_version`, `list_instruction_versions(agent_id)`, `get_current_instruction(agent_id)`.
- `create_committee`, `update_committee_members`, `list_committees`, `get_committee`.
- `start_committee_run` (cria AgentRun em PENDING/RUNNING e registra input_ref + payload_snapshot).
- `finalize_committee_run_success` / `finalize_committee_run_fail` (status final + result_bundle_ref ou erro).

Critérios:
- Nenhuma dependência direta com cliente de LLM; em S23 o comitê só gerencia metadados e execução “lógica” (quem entra, quem decide, como persistir o resultado).
- Todos os métodos com docstring descrevendo claramente qual camada do sistema vai chamá-los (UI admin, pipelines de consulta, tarefas futuras de worker, etc.).

### A3. API admin para Agents e Committees

Objetivo: expor endpoints ADMIN REST (ou HTTP JSON) para o console de agentes.

Arquivos:
- `app/api/agents/routes_admin.py`
- `app/api/agents/schemas.py` (payloads HTTP)
- `app/api/__init__.py` (registro de rotas se necessário)

Endpoints mínimos (prefixo sugerido `/admin/agents`):
- `GET /admin/agents` — lista de agentes (filtro por layer/role/status).
- `POST /admin/agents` — cria agente com nome, descrição, layer, role, modelo recomendado etc.
- `GET /admin/agents/{agent_id}` — detalhe do agente (incluindo modelo atual, allowed_models, últimas instruções).
- `PUT /admin/agents/{agent_id}` — atualização básica (descrição, modelos, status).
- `GET /admin/agents/{agent_id}/instructions` — lista versões de instrução.
- `POST /admin/agents/{agent_id}/instructions` — adiciona nova versão de instrução.
- `GET /admin/committees` — lista comitês.
- `POST /admin/committees` — cria comitê com triple redundancy (2 debunkers + 1 mediator por default) e configura camada.
- `GET /admin/committees/{committee_id}` — detalhe, incluindo membros.
- `PUT /admin/committees/{committee_id}` — atualiza descrição, membros, quorum.
- `GET /admin/committees/{committee_id}/runs` — histórico de execuções.
- `POST /admin/committees/{committee_id}/dry-run` — endpoint de teste (stub) que monta um `AgentRun` com bundle fake para debug (sem chamar modelo real ainda — só para testar wiring e evidência).

Critérios:
- Esquemas pydantic compatíveis com o que o frontend espera (Capítulo 3).
- Responses sempre com IDs estáveis e timestamps.
- Todos os endpoints de admin protegidos com escopo/admin (mesmo que a autenticação completa esteja fora da S23, deixar o hook pronto).

## 2. Trilha B — Console de agentes (frontend admin)

### B1. Rotas e layout do Console de Agentes

Objetivo: criar a navegação no admin para gerenciamento de Agents e Committees com UX inspirada em “criar GPT”.

Arquivos:
- `frontend/inspectah-ui/src/app/routes.tsx`
- `frontend/inspectah-ui/src/app/layout/MainLayout.tsx`
- `frontend/inspectah-ui/src/modules/admin/pages/AdminAgentsPage.tsx`
- `frontend/inspectah-ui/src/modules/admin/pages/AdminAgentDetailPage.tsx`
- `frontend/inspectah-ui/src/modules/admin/pages/AdminCommitteeDetailPage.tsx`

Tarefas:
- Adicionar entrada “Agentes & Comitês” no menu Admin.
- Página `AdminAgentsPage`:
  - Lista de agentes com colunas: Nome, Layer, Papel (debunker/mediator), Modelo atual, Status.
  - Botão “Criar agente”.
- Página `AdminAgentDetailPage`:
  - Seções espelhando a UI de criação de GPT:
    - Nome
    - Descrição
    - Instruções (texto longo markdown)
    - Conhecimento (arquivos/refs — por enquanto só mostrar e registrar refs, sem upload real se estiver fora da S23)
    - Modelo recomendado (dropdown com modelos disponíveis)
  - Aba “Histórico de versões” mostrando `AgentInstructionVersion`.
- Página `AdminCommitteeDetailPage`:
  - Nome do comitê, camada.
  - Cards para cada membro: Debunker A, Debunker B, Mediador.
  - Indicação clara de que a decisão final vem sempre do mediador.
  - Lista de runs recentes com status (PENDING/RUNNING/SUCCESS/FAIL).

Critérios:
- Reutilizar componentes e padrões de design existentes (cards, tabelas, breadcrumbs, etc.).
- Nenhum “console mágico”: tudo que for configurável deve ser explicitamente visível em tela.

### B2. API client e hooks de frontend

Objetivo: encapsular chamadas aos endpoints de agentes em hooks e clients bem tipados.

Arquivos:
- `frontend/inspectah-ui/src/core/api/api-types.ts`
- `frontend/inspectah-ui/src/core/api/endpoints.ts`
- `frontend/inspectah-ui/src/modules/admin/api/agentsClient.ts`
- `frontend/inspectah-ui/src/modules/admin/hooks/useAgentsAdmin.ts`

Tarefas:
- Tipar `AgentProfile`, `AgentInstructionVersion`, `AgentCommittee`, `AgentRun` com base nos schemas do backend.
- Implementar client:
  - `listAgents`, `getAgent`, `createAgent`, `updateAgent`.
  - `listInstructionVersions`, `createInstructionVersion`.
  - `listCommittees`, `getCommittee`, `createCommittee`, `updateCommittee`, `listCommitteeRuns`, `dryRunCommittee`.
- Hook `useAgentsAdmin` para gerenciar estado de lista, filtros, loading, erros.

Critérios:
- Nenhum `any` silencioso; uso de tipos fortes.
- Erros renderizados com mensagens amigáveis (padrão já usado no Admin).

### B3. Validadores de formulário e UX de segurança

Objetivo: evitar que um admin crie agentes mal configurados por engano.

Arquivos:
- `frontend/inspectah-ui/src/modules/admin/components/AgentForm.tsx`
- `frontend/inspectah-ui/src/modules/admin/components/CommitteeForm.tsx`

Tarefas:
- Validação de campos obrigatórios:
  - Nome, descrição, layer, papel, modelo recomendado.
- Guard-rails:
  - Se papel for `mediator` mas layer for `debunk`, exibir tooltip explicando função.
  - Impedir comitê sem 3 membros nas camadas críticas (classification, debunk, interpretation).
- Indicar visualmente quando um agente está usando “modelo default global” vs override local.

## 3. Trilha C — Controle de modelos e política de atualização

### C1. Configuração global de modelos

Objetivo: centralizar política de modelo recomendado e janelas de adoção.

Arquivos:
- `inspectah/config/models.py` (novo módulo)
- `docs/sprint_23_model_policy.md`

Tarefas:
- Definir estrutura de configuração:
  - `global_default_model` (ex.: `"gpt-5.1-mini"` ou equivalente da época).
  - `adoption_delay_days` (inteiro; 0 = adotar imediatamente, >0 = buffer).
  - `models_catalog` (lista de modelos suportados com flags: `stable`, `experimental`, `deprecated`).
- Interface (funções) para outros módulos:
  - `get_effective_model_for_agent(agent: AgentProfile, now: datetime) -> str`.
  - Respeitar override do agente; se o override não estiver no catálogo ou estiver `deprecated`, emitir warning/flag.

### C2. Console de controle global (admin)

Objetivo: dar ao admin uma tela simples para gerenciar políticas de modelo.

Arquivos:
- `frontend/inspectah-ui/src/modules/admin/pages/AdminModelPolicyPage.tsx`
- `frontend/inspectah-ui/src/modules/admin/api/modelPolicyClient.ts`

Tarefas:
- Exibir:
  - Modelo global atual.
  - Lista de modelos disponíveis com status (stable/experimental/deprecated).
  - Input `adoption_delay_days` com help-text.
- Ações:
  - Botão “Adotar novo modelo global agora” (zera buffer e aplica imediatamente).
  - Botão “Programar adoção em X dias” (atualiza delay).

Critérios:
- Todas as mudanças registradas em log de auditoria (hook na trilha D).
- Essa política ainda não precisa, em S23, acionar nenhum worker automático; basta estar pronta e ser usada pelos módulos que consultam `get_effective_model_for_agent`.

## 4. Trilha D — Observabilidade, auditoria e evidência

### D1. Logs estruturados e eventos de auditoria

Objetivo: registrar tudo que é crítico para reconstruir decisões dos agentes.

Arquivos:
- `inspectah/observability/metrics.py` (já existente)
- `inspectah/observability/audit_logs.py` (novo módulo se necessário)

Eventos mínimos:
- `agent.profile_created`, `agent.profile_updated`, `agent.instruction_version_created`.
- `committee.created`, `committee.updated`.
- `committee.run_started`, `committee.run_finished`.
- `model_policy.updated`.

Tarefas:
- Cada evento deve conter: actor (admin/id ou `system`), timestamp, ids relevantes, diff ou resumo da mudança.
- Integração com qualquer stack de logs/metrics já usada nas sprints anteriores (sem reinventar).

### D2. Evidências em disco (Truth-DB ready)

Objetivo: produzir bundles de evidência para AgentRuns, mesmo que o conteúdo ainda seja stub.

Arquivos:
- `inspectah/evidence/builder.py`
- `inspectah/evidence/vault.py`
- `inspectah/evidence/layouts/s23_agent_runs.json` (novo layout)

Tarefas:
- Para cada `AgentRun` finalizado em SUCCESS ou FAIL, produzir um bundle mínimo com:
  - metadados do comitê (ids, nomes, layer).
  - input_ref e payload_snapshot.
  - resultado consolidado (mesmo que seja stub: “não executado ainda, apenas wiring testado” em S23).
- Gravar em `out/evidence/S23_agent_runs/<committee_id>/<run_id>/` com `SUMMARY.json` e `MANIFEST.json`.

Critérios:
- Layout compatível com DNA de evidência (Merkle/truth-ready), mas sem precisar fazer anchor em blockchain na S23.

## 5. Trilha E — Integração mínima com pipeline de consulta (sem acoplamento rígido)

### E1. Pontos de integração no backend

Objetivo: preparar o terreno para que consultas ao Inspectah possam acionar comitês na S24+ sem reescrever tudo.

Arquivos:
- `inspectah/pipeline/pipeline_fixtures.py`
- `inspectah/indexer/query_api.py`
- `inspectah/api/consultation/routes.py` (ou equivalente)

Tarefas:
- Definir interface (sem implementação pesada):
  - `select_committees_for_case(case_type: str) -> List[AgentCommittee]`.
  - `enqueue_committee_runs(input_ref: str, committees: List[AgentCommittee]) -> List[AgentRun]`.
- Adicionar comentários/docstrings explicando como, na S24+, esses pontos serão ligados a workers que realmente chamam LLM.

Critérios:
- Nenhuma chamada real à API de LLM em S23.
- Tudo coberto por testes de unidade que validam apenas a seleção e o wiring lógico.

## 6. Trilha F — Testes, gates e ORR da Sprint 23

### F1. Scripts de gates S23

Objetivo: padronizar execução da sprint com o mesmo nível das sprints anteriores.

Arquivos:
- `bin/s23_all_gates.sh`
- `bin/s23_g0_contexto.sh`
- `bin/s23_g1_modelos_e_invariantes.sh`
- `bin/s23_g2_contratos_servico_agents.sh`
- `bin/s23_g3_console_admin_front.sh`
- `bin/s23_g4_model_policy.sh`
- `bin/s23_g5_observability_e_evidencias.sh`
- `bin/s23_g6_integracao_pipeline.sh`
- `bin/s23_g7_scorecard.sh`
- `bin/s23_g8_orr.sh`

Tarefas:
- Cada gate deve:
  - Rodar testes específicos (unit/integration/frontend) conforme Capítulo 2.
  - Gerar scorecards em `out/scorecards/S23_G*.json`.
  - Gerar evidências em `out/evidence/S23_G*/` quando aplicável.
- `bin/s23_all_gates.sh` roda G0–G7 em sequência, falhando no primeiro erro.
- `bin/s23_g8_orr.sh` agrega scorecards e produz decisão GO/NO_GO.

### F2. Suite de testes

Objetivo: garantir que o núcleo da S23 não quebre nada anterior e esteja protegido contra regressões burbas.

Arquivos exemplos:
- `tests/agents/test_agent_domain_model.py`
- `tests/agents/test_committee_domain_logic.py`
- `tests/agents/test_model_policy.py`
- `tests/integration/test_admin_agents_api.py`
- `frontend/inspectah-ui/src/__tests__/admin/AdminAgentsPage.test.tsx`

Critérios:
- Cobrir cenários de criação/edição de agent, criação de versões de instrução, criação de comitês com triple redundancy, dry-run, mudança de política de modelo.
- Garantir que chamadas de admin inválidas retornem erros HTTP adequados.

## 7. Sequência recomendada de execução (passo a passo humano)

1. Preparação
   - Atualizar `main` local, criar branch da S23.
   - Ler Capítulos 1–3 da Sprint 23.
2. Trilha A (domínio + API backend)
   - Implementar modelos, migrations e serviços de Agents/Committees.
   - Expor endpoints admin básicos.
   - Escrever testes de domínio e API.
3. Trilha B (console admin)
   - Criar páginas e componentes do console de agentes.
   - Ligar ao backend via clients/hooks.
   - Escrever testes de frontend para rotas e forms.
4. Trilha C (política de modelos)
   - Implementar módulo de configuração global de modelos.
   - Integrar com AgentProfile/Committee onde necessário.
   - Criar página admin de política de modelos.
5. Trilha D (observabilidade + evidência)
   - Adicionar eventos de auditoria.
   - Implementar bundles de evidência para AgentRuns.
6. Trilha E (integração mínima pipeline)
   - Criar pontos de integração e stubs.
   - Garantir que nada acione LLM ainda, apenas wiring.
7. Trilha F (gates e ORR)
   - Implementar scripts binários de gates.
   - Rodar `bin/s23_all_gates.sh` e ajustar quaisquer falhas.
   - Rodar `bin/s23_g8_orr.sh` e registrar decisão GO/NO_GO com wrap humano em `docs/sprint_23_orr_summary.md`.

Com isso, a Sprint 23 entrega uma fundação sólida, auditável e extensível para toda a camada de agentes e comitês do Inspectah: admin consegue configurar perfis, instruções, comitês e política de modelos, tudo com logs, evidências e trilhas de auditoria prontas para serem plugadas no Truth-DB e no Debunker nas próximas sprints.