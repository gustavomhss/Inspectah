# Inspectah — Sprint 23
## Capítulo 3 — Arquitetura, Filemap e Fronteiras da Camada de Agentes

### 3.1 Visão geral da arquitetura da Sprint 23

A Sprint 23 introduz a **Camada de Agentes de Interpretação e Classificação** do Inspectah, com o seguinte objetivo estrutural:

- Criar uma **infraestrutura genérica de agentes GPT** (registry, configuração, política de modelos, KBs, comitês de redundância tripla) reutilizável em todas as camadas futuras (interpretação, classificação/organização, debunker, etc.).
- Entregar, nesta sprint, **dois comitês concretos** plugados no pipeline do Inspectah:
  - Comitê de **Interpretação** (Interpretation Committee) — transforma entrada bruta/normalizada em avaliações textuais estruturadas (ex.: "o que este bloco diz?", "quais claims existem aqui?").
  - Comitê de **Classificação & Organização** (Classification & Organization Committee) — classifica blocos/eventos em categorias, themes, info_types e outros eixos do modelo de fontes/Truth-DB.
- Expor um **Console de Agentes** (admin) onde o operador consegue:
  - Ver a lista de agentes e comitês ativos.
  - Abrir um agente individual, editar instruções, anexar KBs, escolher modelo, política de atualização de modelo e parâmetros básicos.
  - Ver histórico de versões do agente (versão de instrução + modelo + KB) para garantir auditabilidade.
- Implementar o padrão de **redundância tripla** como construção de alto nível:
  - Para cada camada crítica (interpretação, classificação): 2 agentes debunkers + 1 mediador (triad committees).
  - A orquestração dessa tríade é feita pela própria camada de agentes, não pelo pipeline de ingestão.
- Tornar as **diretrizes dos agentes auditáveis**:
  - Admin vê tudo e edita.
  - Usuário final, ao inspecionar uma decisão, consegue ver uma versão estável e legível das diretrizes (sem segredos operacionais) e saber qual comitê de agentes foi responsável por aquela decisão.

Do ponto de vista arquitetural, a Sprint 23 adiciona um novo "sub-sistema" ao Inspectah:

- **Sub-sistema Agents**: `inspectah/agents/*` + `app/agents/*` + páginas de admin em `frontend/inspectah-ui/src/modules/agents/*`.
- Integração com:
  - **Pipeline de classificação/organização** (já existente) via adaptadores bem definidos.
  - **Evidence Vault / Logs** para registrar decisões, inputs e outputs dos comitês.
  - **Modelo de fontes e casos** (S21/S22) para usar o mesmo vocabulário de themes, info_types, categories.

Tudo é desenhado para ser:

- Modular (camada Agents não “suga” lógica do pipeline e vice-versa).
- Auditável (cada decisão de agente produz trilha revisável).
- Troca-de-modelo-aware (política de upgrades de modelo de IA configurável pelo admin, com buffers e janelas de migração).

---

### 3.2 Backend — Domínio e serviços da camada de agentes

#### 3.2.1 Domínio: agentes, comitês e políticas

Novo módulo de domínio:

- `app/agents/models.py`
  - `AgentId` (alias / value object).
  - `AgentProfile` — representa um agente unitário, com campos alinhados à metáfora de "Custom GPT":
    - `id: AgentId`
    - `name: str`
    - `description: str`
    - `instructions: str` (texto longo, em markdown, versionável).
    - `role: Literal["interpreter", "classifier", "debunker", "mediator"]`.
    - `layer: Literal["interpretation", "classification", "debunk"]` (qual camada lógica do Inspectah).
    - `model_name: str` (modelo LLM efetivo em uso).
    - `recommended_model_name: str` (sugestão padrão para o admin, com base em política global).
    - `temperature: float`, `max_tokens: int`, `top_p: float` (parâmetros básicos).
    - `kb_sources: List[AgentKBRef]` (links para KBs/arquivos/coleções).
    - `status: Literal["active", "paused", "deprecated"]`.
    - `created_at`, `updated_at`, `created_by`, `last_modified_by`.
  - `AgentKBRef`
    - `id`, `kind` (arquivo, collection, external_ref), `label`, `path_or_uri`.
  - `AgentVersion`
    - Snap da versão (instructions + modelo + params + KB) para cada mudança relevante.
    - Contém `version_number`, `changelog`, `changed_by`, timestamps.
  - `AgentCommittee`
    - Representa um comitê de redundância tripla (2 debunkers + 1 mediador ou variações futuras).
    - Campos principais:
      - `id`
      - `name`
      - `layer: "interpretation" | "classification" | "debunk"`
      - `primary_agents: List[AgentId]` (ex.: `[debunker_a, debunker_b]`).
      - `mediator_agent: AgentId`.
      - `policy: CommitteePolicy` (como combinar, quorum, quando falhar).
  - `CommitteePolicy`
    - Parâmetros de consenso:
      - `required_agreement_ratio` (ex.: pelo menos 2 de 3).
      - `max_disagreement_tolerance`.
      - `resolve_ties_strategy` (ex.: "favor cautious", "favor debunk", "escalar para humano").

- `app/agents/policies.py`
  - `ModelUpgradePolicy`
    - Representa a política global e por agente para upgrades de modelo:
      - `auto_upgrade_enabled: bool`.
      - `delay_days: int` (ex.: 0, 7, 15).
      - `allowed_target_models: List[str]`.
      - `last_upgrade_at`, `next_upgrade_at`.
    - Lida com o conceito de **chave geral** que permite mudar o modelo padrão de todos os agentes, com buffer de tempo.
  - `AgentSafetyPolicy`
    - Limites de uso (para evitar comportamentos perigosos do LLM), ex.:
      - `allow_sensitive_topics: bool`.
      - `max_context_tokens`.
      - `red_team_mode: bool` para debunkers (mais agressivos na busca de inconsistências, ainda assim dentro da política de segurança).

#### 3.2.2 Repositório e persistência

- `app/agents/repository.py`
  - Responsável por persistir `AgentProfile`, `AgentVersion`, `AgentCommittee`, `ModelUpgradePolicy`.
  - Interface clara:
    - `get_agent(agent_id)`, `list_agents(filter)`, `create_agent(...)`, `update_agent(...)`, `soft_delete_agent(...)`.
    - `list_agent_versions(agent_id)`, `create_agent_version(...)`.
    - `get_committee(committee_id)`, `list_committees(layer)`, `create_committee(...)`, `update_committee(...)`.
    - `get_global_model_policy()`, `update_global_model_policy(...)`.
  - Implementação alinhada com SQLAlchemy e migrações da Sprint 23 (ver seção 3.4).

#### 3.2.3 Serviços e orquestração de comitês

- `app/agents/service.py`
  - Camada de aplicação que orquestra uso de LLMs via comitês.
  - Principais funções:
    - `run_interpretation_committee(input: InterpretationInput) -> InterpretationCommitteeResult`
    - `run_classification_committee(input: ClassificationInput) -> ClassificationCommitteeResult`
    - `run_generic_committee(committee_id, payload) -> CommitteeResult`
  - Internamente:
    - Resolve comitê e agentes envolvidos via `repository`.
    - Para cada agente da tríade, monta o prompt (instruções + input + contexto de KB) usando adaptadores.
    - Chama o LLM via client (`LLMClient`) de forma independente por agente.
    - Aplica `CommitteePolicy` para unir respostas, detectar divergências, decidir GO/NO-GO e quando escalar para humano.
    - Registra **logs de decisão** e **evidências** (ver 3.6) via Observability e Evidence Vault.

- `app/agents/llm_client.py`
  - Abstração para chamadas ao ChatGPT/OpenAI (ou outro provedor):
    - Garante que o **modelo mais atual** dentro do plano Plus seja usado por padrão, salvo override do admin.
    - Aplica `ModelUpgradePolicy` para decidir qual modelo concreto usar num dado momento.
    - Pode ter backends múltiplos (OpenAI, Azure, etc.) na mesma interface.

- `app/agents/kb_adapter.py`
  - Interface que converte `AgentKBRef` em contexto textual ou IDs para retrieval.
  - Integra com storage de KBs do Inspectah (arquivos, coleções, etc.).

#### 3.2.4 Integração com pipeline de casos/Truth-DB

- `inspectah/pipeline/agents_adapter.py`
  - Adapta o pipeline atual para chamar comitês de:
    - Interpretação na hora de criar/atualizar blocos e sub-blocos interpretativos.
    - Classificação/organização na hora de etiquetar blocos com themes, info_types, categorias, tags de risco, etc.
  - Expõe funções como:
    - `interpret_block(block) -> InterpretationBundle`
    - `classify_block(block) -> ClassificationBundle`
  - Esses bundles são guardados como parte da trilha de evidência e retornados como parte da resposta do Inspectah.

---

### 3.3 Backend — API de administração e consulta dos agentes

#### 3.3.1 Rotas de administração

Novo módulo de rotas admin:

- `app/agents/routes_admin.py`
  - Prefixo: `/admin/agents`
  - Operações principais:
    - `GET /admin/agents` — lista agentes, com filtros por camada/role/status.
    - `POST /admin/agents` — cria novo agente (nome, descrição, instruções, role, layer, modelo sugerido, KBs iniciais).
    - `GET /admin/agents/{agent_id}` — detalha agente e últimas versões.
    - `PUT /admin/agents/{agent_id}` — atualiza instruções, modelo, parâmetros, KBs.
    - `GET /admin/agents/{agent_id}/versions` — lista versões do agente.
    - `GET /admin/agents/{agent_id}/versions/{version}` — detalhe de uma versão específica.
    - `GET /admin/committees` — lista comitês existentes, por camada.
    - `POST /admin/committees` — cria comitê de agentes (2 debunkers + 1 mediador para cada camada crítica).
    - `PUT /admin/committees/{committee_id}` — ajusta composição ou política.
    - `GET /admin/agents/policies/model-upgrades` — lê política global de upgrades de modelo.
    - `PUT /admin/agents/policies/model-upgrades` — atualiza política (incluindo delay global de adoção de novos modelos).

- `app/agents/schemas.py`
  - Schemas Pydantic que espelham os modelos principais, com campos adequados para o Console Admin, inclusive metadados de audit trail (quem criou, quem editou, timestamps).

#### 3.3.2 Rotas de auditoria das decisões de agentes

- `app/agents/routes_audit.py`
  - Prefixo: `/admin/agents/audit`
  - Fornece endpoints para inspecionar decisões recentes de comitês:
    - `GET /admin/agents/audit/decisions` — lista decisões com filtros por camada, comitê, agente, caso, período.
    - `GET /admin/agents/audit/decisions/{decision_id}` — retorna input, outputs dos agentes, decisão final, committee policy aplicada e links para evidências no Evidence Vault.

Essas rotas alimentam tanto o Console de Agentes quanto futuras telas de auditoria fina.

---

### 3.4 Backend — Migrações e modelo de dados

Novas migrações (apenas esqueleto conceitual aqui; detalhes vão para os arquivos `migrations/versions/XXXX_s23_agents_*.py`):

- `ai_agents`
  - `id (PK)`
  - `name`
  - `description`
  - `instructions`
  - `role`
  - `layer`
  - `model_name`
  - `recommended_model_name`
  - `temperature`, `max_tokens`, `top_p`
  - `status`
  - `created_at`, `updated_at`, `created_by`, `last_modified_by`

- `ai_agent_versions`
  - `id (PK)`
  - `agent_id (FK ai_agents)`
  - `version_number`
  - `instructions`
  - `model_name`
  - `temperature`, `max_tokens`, `top_p`
  - `kb_snapshot` (JSON com lista de KBRefs)
  - `changelog`
  - `created_at`, `created_by`

- `ai_committees`
  - `id (PK)`
  - `name`
  - `layer`
  - `primary_agents` (array/JSON de AgentIds)
  - `mediator_agent` (FK ai_agents)
  - `policy` (JSON com parâmetros de consenso)
  - `status`
  - `created_at`, `updated_at`

- `ai_model_policy`
  - `id (PK, único)`
  - `auto_upgrade_enabled`
  - `delay_days`
  - `allowed_target_models` (JSON)
  - `last_upgrade_at`, `next_upgrade_at`
  - `created_at`, `updated_at`

- `ai_agent_decisions`
  - `id (PK)`
  - `committee_id`
  - `layer`
  - `input_kind` (ex.: `block`, `source_event`, `case_state`).
  - `input_ref` (ID do bloco/evento/caso).
  - `raw_input_snapshot` (JSON/texto com input usado pelo comitê).
  - `agent_outputs` (JSON por agente).
  - `final_decision` (JSON estruturado conforme o tipo de comitê: interpretação ou classificação).
  - `decision_status` (ex.: `accepted`, `escalated`, `rejected`).
  - `created_at`, `created_by` (se houver humano no loop).
  - `evidence_bundle_ref` (link para Evidence Vault).

Essas tabelas são o alicerce para:

- Configurar agentes e comitês.
- Versão dos agentes.
- Registrar decisões para auditoria e explicabilidade.

---

### 3.5 Frontend — Console de Agentes (Admin)

Novo módulo de frontend dedicado à administração dos agentes:

- Pasta base:
  - `frontend/inspectah-ui/src/modules/agents/`

Arquivos principais:

- `pages/AgentsListPage.tsx`
  - Lista de agentes com filtros por camada (interpretação, classificação, debunk), role (debunker, mediador, etc.) e status.
  - Ações rápidas:
    - Criar agente.
    - Abrir detalhe.

- `pages/AgentDetailPage.tsx`
  - Tela central do console, inspirada no fluxo de criação de Custom GPT:
    - Seções:
      - **Nome** — campo editável.
      - **Descrição** — resumo curto.
      - **Instruções** — editor de texto rico/markdown.
      - **Camada e função** — selects para layer (interpretation/classification/debunk) e role.
      - **Modelo recomendado e modelo atual** — dropdown com modelos suportados e indicação de qual é o default global.
      - **Parâmetros de geração** — temperatura, max_tokens, top_p.
      - **Knowledge** — cards de arquivos/coleções vinculadas ao agente, com ações de adicionar/remover.
      - **Política de upgrade de modelo** — exibe como o agente herda ou sobrescreve a política global.
      - **Histórico de versões** — tabela com versões; ao clicar, mostra diff básico (instruções e modelo) e metadados.

- `pages/CommitteesPage.tsx`
  - Lista e gestão dos comitês:
    - Exibe comitês por camada.
    - Mostra quais agentes compõem as tríades (2 debunkers + 1 mediador).
    - Botão para criar/editar comitê, escolhendo agentes via autocomplete.

- `components/AgentForm.tsx`
  - Form principal reutilizado por criação/edição.
  - Valida campos críticos (nome, layer, role, modelo).

- `components/AgentKBManager.tsx`
  - UI para anexar KBs ao agente (upload simples, escolha de coleções, etc., conforme features de KB da versão atual do Inspectah).

- `components/AgentVersionTimeline.tsx`
  - Visualiza histórico de versões de um agente como timeline.

- `hooks/useAgents.ts`
  - Hook para listar, criar, atualizar agentes via API.

- `hooks/useAgentDetail.ts`
  - Hook para carregar detalhe + versões de um agente.

- `hooks/useCommittees.ts`
  - Hook para listar/criar/editar comitês.

- `api/agentsApi.ts`
  - Client tipado para as rotas `/admin/agents` e `/admin/committees`.

Integrações de navegação:

- `src/app/routes.tsx`
  - Acrescenta rotas:
    - `/admin/agents` → `AgentsListPage`.
    - `/admin/agents/:agentId` → `AgentDetailPage`.
    - `/admin/agents/committees` → `CommitteesPage`.

- `src/app/layout/MainLayout.tsx`
  - Adiciona link de menu para "Agentes" dentro da área admin.

Testes de frontend:

- `src/__tests__/agents/AgentsPages.test.tsx`
  - Cobre fluxos principais do console de agentes:
    - Listar agentes.
    - Criar agente básico.
    - Editar instruções e salvar.
    - Visualizar histórico de versões.

- `src/modules/agents/components/__tests__/*.test.tsx`
  - Testes de unidade dos componentes-chave (AgentForm, AgentVersionTimeline, etc.).

---

### 3.6 Observabilidade, evidência e trilha de auditoria

Para garantir auditabilidade e transparência das decisões dos agentes, a Sprint 23 amarra a camada de agentes ao sistema de observabilidade e ao Evidence Vault.

- Logs estruturados:
  - `inspectah/watchers/api_watcher.py` (ou módulo equivalente) passa a registrar eventos do tipo `agent.committee_run` com:
    - `committee_id`, `layer`, `agent_ids`, `input_ref`, `decision_id`, `status`.

- Evidence Vault:
  - Ao final de `run_interpretation_committee` ou `run_classification_committee`, o serviço de agentes cria um **bundle de evidência** com:
    - Input textual.
    - Configuração relevante do comitê (IDs de agentes, versão de instruções, modelo em uso; apenas metadados, não segredos internos).
    - Outputs dos agentes e decisão final.
  - O ID desse bundle é armazenado em `ai_agent_decisions.evidence_bundle_ref`.

- Métricas:
  - Métricas básicas por comitê e por agente:
    - Latência média do comitê.
    - Taxa de desacordo entre agentes.
    - Taxa de escalonamento para humano.

Essas estruturas serão usadas pelos gates de validação da Sprint 23, mas também pelas sprints seguintes (Debunker v0, Governança de Verdade/Fato) para construir scorecards mais sofisticados.

---

### 3.7 Escopo, fronteiras e itens explícitos fora da Sprint 23

Para evitar ambiguidades e manter o foco, a Sprint 23 **não** implementa:

- Fluxos completos de Debunker v0 (camada debunker final, com contestação pública, bonds, etc.).
  - S23 prepara a **infraestrutura** de agentes e comitês que será usada pelo Debunker na Sprint 24.

- UI de auditoria avançada para usuários finais (painéis detalhados de decisões de agentes).
  - Nesta sprint expomos APIs e dados necessários; as UIs avançadas ficam para Sprints futuras.

- Editor avançado de KB (gestão completa de coleções, versionamento de KB, etc.).
  - S23 oferece apenas o mínimo para anexar KBs aos agentes, reutilizando a infra de arquivos existente.

- Integrações com múltiplos provedores de LLM além do já suportado (ChatGPT/Plus ou equivalente).
  - A arquitetura do `LLMClient` já prevê este cenário, mas a implementação inicial é focada no provedor atual.

Com este filemap e arquitetura, a Sprint 23 define uma base sólida para que o Inspectah passe a tomar decisões de interpretação e classificação com **tríades de agentes GPT auditáveis**, altamente configuráveis e fáceis de manter, preparando o terreno para o Debunker v0 e para a governança de Verdade/Fato nas próximas sprints.