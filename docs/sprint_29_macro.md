# Inspectah — Sprint 29 (Macro) — Domain Agent Flow Config v1 (E28.1 + base E28.2)

## 1. Nome, squad e propósito

**Sprint 29 — Domain Agent Flow Config v1 (Fluxo de Agentes Configurável por Domínio)**  
Épico associado: **E28 — Fluxo de Agentes Configurável v1** (Programa 1).  
S29 foca em **E28.1 (Modelo & API de fluxo)** + a **primeira camada da E28.2 (UI linear mínima + validação)**.

**Squad responsável**: **Squad Agent Flow Config v1**  
Lideranças centrais:
- **Percy Liang** — arquitetura de agentes LLM, critérios de confiança e fallback.
- **Martin Kleppmann** — modelo de dados, versionamento interno, consistência e audit trail.
- **Gregor Hohpe** — integração com pipelines de ingestão e runtime de agentes.
- **Emily Bender** — sanidade linguística, limites e transparência na configuração de agentes.
- **Kent Beck** — design de API e testes, TDD da camada de fluxo.

**Propósito da S29**  
Tirar os fluxos de agentes "de dentro do código" e transformá‑los em **configuração de domínio, linear, validada e operável via UI**, garantindo que:
- o operador consiga **ver, editar e salvar** o fluxo de agentes de um domínio sem deploy,
- o runtime de ingestão/agentes **consuma esses fluxos configurados** de forma segura,
- existam **invariantes fortes** que impeçam fluxos inválidos (sem Interpreter, sem Classifier, etc.),
- haja **rastro mínimo de auditoria** das mudanças (quem mudou, quando, de que para que).

S29 é a sprint que abre o E28 e entrega a **v1 operável** do fluxo de agentes configurável, deixando o terreno pronto para:
- S30 fechar a **UI avançada + versionamento/histórico completo (E28.2 + E28.3)**.

---

## 2. North Star da Sprint 29

Ao final da S29, em ambiente dev, queremos o seguinte quadro:

1. Para qualquer domínio suportado (ex.: "Notícia — Política BR", "Dados econômicos — Brasil", "Saúde pública BR") existe **exatamente um fluxo de agentes ativo** definido em uma entidade de configuração (`AgentFlowConfig`), com:
   - uma lista **linear e ordenada** de passos,
   - cada passo associado a um **papel de agente** permitido (`INTERPRETER`, `CLASSIFIER`, `ORGANIZER`, `DEBUNKER`, `DECISION_MAKER`, etc.),
   - parâmetros básicos por passo (ex.: qual comitê, thresholds de confiança, flags de modo estrito/relaxado).

2. A **UI de admin** possui uma tela simples de "Fluxo de agentes por domínio" que permite:
   - selecionar um domínio e ver o fluxo atual em forma de lista ordenada,
   - reordenar passos (drag & drop ou controles de posição),
   - adicionar/remover passos a partir de um catálogo de papéis de agente suportados,
   - salvar somente se o fluxo respeitar **todas as regras de integridade**.

3. O **runtime de ingestão/agentes** já consulta essa configuração em tempo de execução, de forma que:
   - ao processar um item de um domínio X, o pipeline use a sequência de agentes definida em `AgentFlowConfig` para X,
   - em caso de ausência de configuração explícita, exista um **fallback controlado** (ex.: fluxo padrão global + flag de alerta).

4. Toda tentativa de salvar um fluxo passa por um **validador de invariantes**, que rejeita fluxos que:
   - não começam com um papel permitido como primeiro passo (`INTERPRETER` ou equivalente),
   - pulam etapas obrigatórias (ex.: fluxo com `DEBUNKER` sem `CLASSIFIER` prévio, se a política exigir),
   - criam combinações explicitamente proibidas (ex.: dois `DECISION_MAKER` em sequência, ou `DECISION_MAKER` no meio do fluxo).

5. As principais mudanças de fluxo de agentes são **rastreadas no banco e nos logs**, permitindo responder perguntas como:
   - "Quem alterou o fluxo de agentes do domínio X ontem?",
   - "Qual era o fluxo antes da mudança?" (mesmo que o histórico detalhado fique para S30, S29 já guarda um snapshot básico).

6. Os **gates da S29** cobrem:
   - modelo de dados e migrations,
   - API e contrato de domínio,
   - UI mínima,
   - integração com runtime,
   - testes de invariantes e logging,
   - evidências em bundle único de sprint.

A S29 é considerada **GO** somente se o conselho enxergar o fluxo de agentes como uma **peça de produto real**, e não como um experimento solto.

---

## 3. Problema que a S29 resolve

Hoje, o fluxo de agentes por domínio sofre com:

- **Acoplamento ao código**: a ordem e o conjunto de agentes vivem em código (config hardcoded, dicionários, enums, ifs), exigindo deploy para qualquer ajuste fino.
- **Ausência de visibilidade**: não há tela única que responda "qual é o fluxo de agentes para esse domínio?".
- **Zero versionamento explícito**: ajustes de fluxo não têm histórico acessível; o máximo que existe são diffs de código, difíceis de mapear para domínios/casos.
- **Risco de incoerências**: mudanças em um domínio podem quebrar invariantes não escritas (ex.: tirar o Classifier sem perceber o efeito sobre o Debunker).
- **Operação lenta**: product/ops não têm alavancas para afinar a análise de um domínio em resposta a crises (ex.: eleições, desinformação massiva) sem rodar todo um ciclo de desenvolvimento.

S29 ataca esse problema ao criar um **ponto único de verdade** para fluxos de agentes por domínio, com **modelo, API, UI e runtime integrados**, inaugurando o E28.

---

## 4. Estado-alvo da Sprint 29 (DONE S29)

Ao declarar S29 como concluída, todas as afirmações abaixo devem ser verdade em dev:

1. **Modelo & storage**
   - Existe um modelo de domínio para fluxos de agentes (`AgentFlowConfig`, `AgentFlowStep`) com:
     - referência ao domínio (ex.: `domain_key` estável usado em ingestão e no console),
     - lista ordenada de passos (`position`),
     - tipo de papel de agente (`agent_role`),
     - parâmetros básicos (ex.: `committee_id`, `strict_mode`, `max_depth`, etc.),
     - metadados de auditoria (`created_at`, `created_by`, `updated_at`, `updated_by`, `change_reason`).
   - Migrations criadas e aplicadas (`migrations/versions/00xx_s29_agent_flows.py`), idempotentes e alinhadas com os modelos.

2. **API de admin & contrato de domínio**
   - Endpoints REST (FastAPI) disponíveis sob `/admin/agent-flows`:
     - `GET /admin/agent-flows` — lista fluxos por domínio (com filtros por domínio e paginação).
     - `GET /admin/agent-flows/{flow_id}` — detalhes do fluxo (incluindo passos).
     - `GET /admin/agent-flows/by-domain/{domain_key}` — fluxo ativo para um domínio.
     - `POST /admin/agent-flows` — cria fluxo para domínio ainda não configurado.
     - `PUT /admin/agent-flows/{flow_id}` — atualiza fluxo existente, respeitando invariantes.
   - O contrato de API é descrito em schemas Pydantic (`AgentFlowConfigIn`, `AgentFlowConfigOut`, etc.), com tipos claros e exemplos.

3. **Validador de invariantes de fluxo**
   - Existe um módulo de validação (`app/agents/flows/validator.py`) com regras explícitas, por exemplo:
     - fluxo não pode ser vazio,
     - primeiro passo deve ser papel de entrada permitido (ex.: `INTERPRETER`),
     - papéis obrigatórios por domínio (ex.: `CLASSIFIER` antes de `DECISION_MAKER` quando o domínio exige),
     - nenhum passo `DECISION_MAKER` antes de todos os passos analíticos definidos para o domínio,
     - lista sem posições repetidas, sem buracos críticos, sem duplicações proibidas.
   - Esses invariantes são cobertos por **testes automatizados** em `tests/agents/test_agent_flow_validator.py`.

4. **UI de configuração linear mínima (v1)**
   - Nova seção no console admin, ex.: **"Agentes & Fluxos" → "Fluxo por domínio"**.
   - Tela `/admin/agent-flows` contendo:
     - tabela/listagem de domínios com status "configurado / não configurado" e link de edição,
     - visualização do fluxo atual como lista enumerada de passos.
   - Tela de edição de fluxo (`AgentFlowEditor`):
     - seletor de domínio,
     - lista ordenada de passos com controles para mover para cima/baixo,
     - botão para adicionar novo passo selecionando o papel de um catálogo controlado,
     - mensagens de erro claras se o fluxo violar invariantes na tentativa de salvar.
   - Para pelo menos **um domínio canônico**, o fluxo é configurado via UI e usado em um demo da S29.

5. **Integração com runtime de ingestão/agentes**
   - Existe uma função única de resolução de fluxo, ex.: `get_agent_flow_for_domain(domain_key: str) -> AgentFlowRuntimeSpec` em `app/agents/flows/runtime_adapter.py`.
   - Os pipelines de ingestão ou orquestração de agentes chamam essa função para determinar a ordem dos agentes a serem executados.
   - Em caso de erro na leitura do fluxo ou ausência de configuração para o domínio:
     - o sistema usa um fallback explícito documentado (fluxo padrão global),
     - um log estruturado é emitido marcando o problema,
     - uma métrica/flag é incrementada para monitorar uso de fallback.

6. **Auditoria mínima e logs de mudanças**
   - Toda alteração de fluxo (`POST`/`PUT`) gera um registro de mudança com:
     - identificador do usuário/operador (quando disponível),
     - timestamp,
     - motivo (campo de texto obrigatório `change_reason`),
     - snapshot mínimo do fluxo antes/depois (mesmo que simplificado em S29).
   - Logs estruturados são emitidos em um logger dedicado (`agent_flows_audit`), incluídos nos bundles de evidência da sprint.

7. **Documentação e ORR**
   - Capítulos 1–4 da S29 estão criados em `docs/sprint_29_capitulo_*.md`, alinhados ao Sprint Playbook v3.
   - Existe um documento `docs/sprint_29_macro.md` (este), descrevendo o panorama geral da sprint.
   - O ORR da S29 (`docs/sprint_29_orr_summary.md`) referencia:
     - os gates executados,
     - os scorecards gerados,
     - o bundle de evidências correspondente.

---

## 5. Escopo detalhado por eixo

### 5.1 Backend — Modelo, API e validação

- Modelos de domínio em `app/agents/flows/models.py` ou módulo equivalente:
  - `AgentFlowConfig` — entidade principal, por domínio.
  - `AgentFlowStep` — passos do fluxo, com `position`, `agent_role`, `params`.
- Migrations em `migrations/versions/00xx_s29_agent_flows.py`:
  - criação de tabelas de configuração e steps,
  - índices por `domain_key` e `position`.
- Schemas Pydantic em `app/agents/flows/schemas.py`.
- Rotas FastAPI em `app/api/admin_agent_flows_routes.py` ou similar.
- Módulo de validação de fluxo (`validator.py`), desacoplado das rotas, com testes dedicados.

### 5.2 Frontend — UI linear mínima de fluxo por domínio

- Feature folder em `frontend/inspectah-ui/src/features/agent-flows/` contendo, por exemplo:
  - `AgentFlowsPage.tsx` — listagem de domínios + status + link para edição.
  - `AgentFlowEditor.tsx` — editor de fluxo linear.
  - `agentFlowsApi.ts` — client para os endpoints `/admin/agent-flows`.
  - `agentFlowsTypes.ts` — tipos TypeScript espelhando os schemas da API.
- Integração com o design system e layout existente de admin.
- Testes de UI em `frontend/inspectah-ui/src/features/agent-flows/__tests__/AgentFlowEditor.test.tsx` cobrindo:
  - criação de fluxo válido,
  - rejeição de fluxo inválido com mensagens claras,
  - reordenação de passos.

### 5.3 Runtime — Adapter único para pipelines

- `app/agents/flows/runtime_adapter.py` contendo:
  - função pública `get_agent_flow_for_domain` (única porta de entrada para resolução de fluxo),
  - conversão da configuração persistida para uma estrutura pronto‑para‑uso pelos pipelines,
  - tratamento de fallback e erros com logs estruturados.
- Ajustes mínimos em pipelines existentes para consumir esse adapter, sem reescrever toda a lógica de agentes (S29 foca na resolução de fluxo, não em todos os detalhes do pipeline S23/S24).

### 5.4 Observabilidade, testes e DX

- Métricas expostas para observabilidade (pelo menos em forma de contadores/gauges internos), como:
  - número de fluxos configurados por domínio,
  - contagem de saves/updates de fluxo,
  - contagem de usos de fallback.
- Testes automatizados cobrindo:
  - modelos e migrations (consistência básica),
  - validação de invariantes de fluxo,
  - API de admin (happy path + erros de validação),
  - integração mínima entre UI e API (ex.: teste e2e com Cypress ou teste integrado reduzido, se já existir infra).
- Scripts de dev para facilitar experimentação, ex.: `bin/s29_dev_seed_agent_flows.sh` criando alguns fluxos exemplo.

### 5.5 Documentação

- Capítulo 1 — Contexto & Problemas: detalha por que fluxos configuráveis importam e como E28 se encaixa no Programa 1.
- Capítulo 2 — Gates & Métricas: define gates S29_G0…S29_G4 e seus critérios objetivos.
- Capítulo 3 — Arquitetura & Filemap: descreve as decisões de modelo, API, UI, runtime e onde mora cada arquivo.
- Capítulo 4 — Execução & Evidências: lista waves/tarefas, scripts de gates, caminhos de evidência e bundles.
- Capítulos 5 e 6 (quando aplicável no Playbook v3) seguem o mesmo padrão das sprints anteriores para consolidação e lições aprendidas.

---

## 6. Fora de escopo e cortes (reservado para S30+)

Para manter S29 finita e executável, ficam explicitamente fora de escopo:

- **Versionamento avançado e timeline rica de mudanças de fluxo** (E28.3):
  - UI de histórico detalhado,
  - rollback por clique para versões anteriores,
  - comparação visual de versões.
- **Regras complexas de fluxo por domínio**:
  - políticas avançadas específicas (ex.: fluxos sazonais, modos de crise, fluxos condicionais por tipo de item dentro do domínio),
  - branching/nós de decisão; S29 fica estritamente em **fluxo linear**.
- **Editor visual avançado com diagramações complexas** (drag&drop rico, zoom, minimapas etc.): S29 entrega um editor linear funcional; o resto é evolutivo.
- **Integração profunda com todos os agentes das S23/S24/S25**:
  - S29 integra apenas o suficiente para que pelo menos um pipeline real use o fluxo configurado,
  - ajustes amplos em todos os pipelines ficam para sprints futuras.
- **Qualquer relação direta com Sistema de Blocos / blockchain**: E28 é sobre fluxo de agentes; ancoragens on‑chain continuam reservadas para Fase 2.

---

## 7. Gates, scorecards e evidências da S29

A S29 segue o Sprint Playbook v3, com gates formais no estilo:

- `bin/s29_g0_scope_and_baseline.sh` — verifica presença e consistência mínima de docs (`sprint_29_macro`, Capítulos 1–3) e filemap.
- `bin/s29_g1_model_and_migrations.sh` — roda testes de modelos, migrations e validação de esquema.
- `bin/s29_g2_api_and_validator.sh` — roda testes de API e invariantes de fluxo.
- `bin/s29_g3_ui_and_frontend_quality.sh` — lint, testes e build do frontend relacionados à feature `agent-flows`.
- `bin/s29_g4_runtime_and_observability.sh` — smoke tests de runtime usando o adapter, verificação de logs/métricas mínimas.

Cada gate gera um scorecard JSON em `out/scorecards/S29_G*_*.json` e evidências em `out/evidence/S29_G*_*`.  
Um bundle único da sprint é gerado em `out/bundles/inspectah_s29_evidence_bundle.zip` para ORR.

A sprint só é considerada **GO** se:
- todos os gates obrigatórios estiverem verdes,
- o conselho (Jobs, Kleppmann, Percy, etc.) classificar a sprint como **≥ 9.5/10** em:
  - clareza do modelo de fluxo,
  - segurança das invariantes,
  - operabilidade via UI,
  - qualidade da integração com runtime e observabilidade.

---

## 8. Interações com outras sprints e próximos passos

**Dependências principais**:
- S21 — Console de Fontes: fornece os domínios e o console onde a nova seção "Agentes & Fluxos" será encaixada.
- S22 — Ingestão 2.0: pipelines de ingestão que vão consumir o fluxo configurado.
- S23–S25 — Agentes, Debunker, Governança: definem os papéis (`INTERPRETER`, `CLASSIFIER`, `DEBUNKER`, etc.) e expectativas de comportamento.

**Efeitos da S29 sobre o roadmap**:
- E28 passa de ideia para **infraestrutura real de configuração de fluxo por domínio**.
- S30 poderá focar em:
  - UI avançada e experiência completa de edição,
  - histórico/versionamento rico de fluxos,
  - regras por domínio mais sofisticadas.

Com S29 concluída, o Inspectah ganha sua **primeira versão de alavanca tática** sobre o cérebro de agentes: fluxos deixam de ser mágicos e passam a ser configuráveis, auditáveis e, o mais importante, governáveis.

