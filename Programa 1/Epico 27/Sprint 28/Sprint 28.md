# Inspectah — Sprint 28 (Macro) — E27.1 CRUD & ON/OFF de Fonte — Versão v2

## 1. Identidade da Sprint e Encaixe no Programa 1

**Nome oficial da sprint**  
Sprint 28 — E27.1 CRUD & ON/OFF de Fonte (Sources & Ingestion Ops v2.0, Sprint 1)

**Épico / Programa**  
- Programa 1 — Consolidação & Consoles Full (E26–E32)  
- Épico: **E27 — Fontes & Ingestão 2.0 em Modo Operação**  
- Sub-épico: **E27.1 — CRUD & ON/OFF de fonte**

**Squad responsável — Squad Sources & Ingestion Ops**  
- **Jay Kreps** — ingestão contínua, contratos de fonte, cadência e fluxo operacional.  
- **Michael Stonebraker** — modelo de dados, schema, normalização e invariantes fortes de banco.  
- **Charity Majors** — operabilidade, observabilidade, sanidade e comportamento em produção.  
- **Kent Beck** — incrementalismo, TDD, refino de workflow e simplicidade do design.  
- **Bruce Schneier (apoio)** — segurança de cadastro, acesso e operação de fontes (auth, segredos, abuso).

**Propósito da Sprint 28 (frase única)**  
Transformar o módulo de fontes em um **objeto de operação de verdade**, onde criar, editar, ativar e desativar qualquer fonte é trivial, seguro e totalmente operável via console, conversando de forma determinística com a Ingestão 2.0.

**Encaixe com o Programa 1 (E26–E32)**  
- E26 fornece o **Design System Admin v1**, que o Console de Fontes v2 deve consumir rigidamente.  
- E27 é o épico que leva fontes + ingestão para **modo operação 24/7**, com visibilidade e controle.  
- A Sprint 28 é o primeiro passo do E27: ela consolida o **modelo de fonte + API + console + ON/OFF**.  
- O que S28 entrega é pré-requisito direto para:  
  - E27.2 (histórico & métricas por fonte),  
  - E27.3 (saúde de fonte & logs administrativos),  
  - E31/E32 (Evidence Vault & Case Cockpit) conseguirem responder “quem são as fontes deste caso?” e “como elas estavam se comportando?”.

---

## 2. Contexto Atual, Problema e Limites de Escopo

### 2.1 Estado de mundo pós-S21/S22/S25

Hoje, após S21/S22/S25, o Inspectah já tem:

- **Domínio de fontes (S21)**:  
  - Entidades como `SourceType` (ex.: `news_rss`, `http_json`, `price_feed`, `custom_api`), com campos obrigatórios e regras mínimas de validação.  
  - Entidade `Source` com pelo menos: `id`, `name`, `type`, `config`, timestamps e um estado básico (`ACTIVE` / `DISABLED` / `DEPRECATED`).  
  - API interna de admin `/admin/sources` criada na S21, mas ainda com cicatrizes de evolução do produto.

- **Ingestão 2.0 (S22)**:  
  - Scheduler/engine que roda ingestões por fonte, com `IngestionRun` registrando o que aconteceu.  
  - Telemetria mínima por fonte, com informações sobre sucessos, falhas e última ingestão.  
  - Um painel inicial de ingestão, mais voltado a evidência técnica do que a operação.

- **Estado pós-S25**:  
  - Repositório consolidado, com sanidade global S1–S25 já possível (mesmo que sofrida).  
  - Lessons Learned fortes sobre:  
    - necessidade de **sanidade contínua**,  
    - perigos de acumular dívidas técnicas em sprints estruturais,  
    - importância de **gates vivos** e scorecards claros.

### 2.2 Problemas que a Sprint 28 precisa atacar

1. **CRUD desalinhado com o modelo atual de fonte**  
   - O modelo de `Source` evoluiu; a API e o console de fontes v1 ficaram com partes obsoletas ou inconsistentes.  
   - Campos como domínio, criticidade, modo de ingestão (`MANUAL`/`AUTO`), cadência e categoria não estão expostos ou não batem front/back.

2. **ON/OFF pouco previsível e com risco de “duas verdades”**  
   - Hoje, desativar uma fonte pode não causar o efeito esperado na Ingestão 2.0 (jobs ainda agendados, corridas zumbis, etc.).  
   - Falta um contrato explícito: o que significa uma fonte estar `DISABLED`? O que o scheduler deve fazer (ou deixar de fazer)?

3. **Console de fontes v1 não é “console de operação”**  
   - É mais um painel técnico do que uma ferramenta de operação.  
   - Não conversa de forma elegante com o modelo pós-S22 nem com o Design System E26.  
   - Falta clareza visual de: estado, modo, criticidade, domínio e ações possíveis.

### 2.3 Escopo IN — o que a Sprint 28 vai tornar verdade

1) **Modelo consolidado de fonte (domínio + DB)**  
- `Source` passa a ter, de forma clara e consistente:
  - Identidade e metadados:  
    - `id` (UUID/ID),  
    - `name`,  
    - `description`,  
    - `type` (ligado a `SourceType`),  
    - `category` (ex.: "news", "macro_data", "market_data"),  
    - `domain` (ligação lógica com domínios operacionais do Inspectah).
  - Config operacional:  
    - `config` (JSON ou estrutura tipada, validada por tipo de fonte),  
    - `auth`/`credentials_ref` (referência a segredos, **nunca** segredos crus),  
    - `schedule` / `cadence` (cron, intervalos, janela mínima),  
    - `mode` (`MANUAL`/`AUTO`).
  - Risco e criticidade:  
    - `criticality` (LOW / MEDIUM / HIGH) — para priorização em futuras sprints (health & Debunker).  
  - Ciclo de vida:  
    - `state` (`ACTIVE`, `DISABLED`, `DEPRECATED`),  
    - `state_changed_at`,  
    - `state_reason` (texto curto explicando por que a transição ocorreu).

- Migrations atualizam o banco para refletir esse modelo, mantendo compatibilidade com dados existentes e documentando qualquer migração destrutiva.

2) **API de admin /admin/sources consolidada (CRUD & ON/OFF)**  
- Contratos REST claros:
  - `GET /admin/sources`  
    - Filtros: `type`, `state`, `category`, `domain`, `mode`, `criticality`.  
    - Paginação (`page`, `page_size`).
  - `GET /admin/sources/{source_id}` — detalhe completo.  
  - `POST /admin/sources` — criar fonte:  
    - validação forte de campos,  
    - rejeição de configs inválidas por `SourceType`,  
    - definição de estado inicial (`ACTIVE` ou `DISABLED`) com regras claras.
  - `PUT /admin/sources/{source_id}` — editar campos permitidos:  
    - políticas de edição para fontes `DEPRECATED` (restritas).  
  - Endpoints de transição de estado explícitos:  
    - `POST /admin/sources/{source_id}/activate`  
    - `POST /admin/sources/{source_id}/disable`  
    - `POST /admin/sources/{source_id}/deprecate`

- Regras de erro claras:  
  - `400` para payload inválido,  
  - `404` para fonte inexistente,  
  - `409` para transições proibidas (ex.: `DEPRECATED → ACTIVE`).

3) **Console de Fontes v2 (CRUD & ON/OFF full via UI)**  
- Tela lista de fontes:
  - Tabela com: `name`, `type`, `domain`, `category`, `state`, `mode`, `criticality`, `last_ingestion_at` (campo apenas expositivo), ações.  
  - Filtros persistentes por cima (com busca textual simples por nome/ID).  
  - Uso exclusivo de componentes do Design System Admin v1.

- Fluxos de operação:
  - Criar fonte via wizard guiado (passo a passo se necessário) com validação inline.  
  - Editar fonte com distinção visual clara do estado atual e campos bloqueados quando necessário.  
  - ON/OFF com ações rápidas:  
    - Botão/menu de “Ativar”, “Desativar”, "Deprecar" respeitando as invariantes.  
  - Estados vazios, loading e erro padronizados (ex.: nenhum resultado, erro de API, etc.).

4) **Integração mínima com Ingestão 2.0**  
- Sem reescrever o motor, a S28 garante que:
  - Fontes `DISABLED` **não** são mais elegíveis para jobs de ingestão automática.  
  - Transições `ACTIVE → DISABLED` e `DISABLED → ACTIVE` atualizam de forma determinística as decisões do scheduler.  
  - Não existem "jobs zumbis" para fontes desativadas (validação via tests e logs).

5) **Sanidade de legado relevante (S21/S22)**  
- S28 inclui consultoria explícita com S21/S22:  
  - Rodar gates relevantes de `S21_G*` e `S22_G*` como parte do G5.  
  - Garantir que nenhuma mudança quebra contratos já assumidos por outras partes do sistema.

### 2.4 Escopo OUT — o que **não** será feito na Sprint 28

- Cálculo de **health score** por fonte (métrica numérica ou categórica de saúde) — isso é E27.3.  
- UI de **histórico completo de ingestão** (lista detalhada de `IngestionRun` por fonte) — isso entra em E27.2.  
- **Logs administrativos ricos** (quem fez qual ação, com detalhes) integrados ao Evidence Vault — S28 apenas prevê ganchos mínimos; a implementação completa fica em E27.3/E31.  
- Qualquer reforma grande na Ingestão 2.0 além do necessário para ON/OFF.  
- Ajustes profundos no Design System — E26 é o fornecedor de componentes; S28 é consumidor exigente.

---

## 3. Estados-Alvo (SA) da Sprint 28

Cada estado-alvo é binário (atingido ou não) e verificável por testes, gates e/ou demo.

**SA-28-01 — API de admin de fontes é sólida e estável**  
Há uma API `/admin/sources` capaz de:
- Criar, listar, detalhar e editar fontes com validação forte.  
- Realizar ON/OFF e deprecar fontes com invariantes explícitas de ciclo de vida.  
- Ser exercitada por testes automatizados cobrindo casos canônicos e edge.

**SA-28-02 — Console de fontes v2 permite operar sem terminal**  
Um operador consegue, usando apenas a UI:
- Cadastrar uma nova fonte (com config válida) do zero.  
- Ajustar uma fonte existente (campos permitidos).  
- Ativar e desativar fontes com feedback imediato e coerente.  
- Perceber facilmente o estado, modo, criticidade e domínio de cada fonte.

**SA-28-03 — ON/OFF conversa com Ingestão 2.0**  
- Desativar uma fonte impede novas ingestões automáticas daquela fonte.  
- Reativar a fonte faz com que ela volte a ser ingerida conforme suas configs.  
- Testes de integração comprovam esse comportamento em cenários simples.

**SA-28-04 — Modelo de fonte consolidado, documentado e saneado**  
- O modelo de `Source` (campos, tipos, enums) está documentado em capítulo de arquitetura da S28.  
- Migrations aplicadas no banco alinham o schema com esse modelo, sem inconsistências.  
- Testes de domínio garantem invariantes de estado e proíbem transições ilegais.

**SA-28-05 — Sanidade de legado S21/S22 preservada**  
- Gates relevantes de S21 e S22 que tocam fontes/ingestão passam em ambiente local/CI.  
- Não há regressões nas funcionalidades já entregues por essas sprints.

---

## 4. Gates da Sprint 28 (G0–G7)

### G0 — S28_G0_scope_and_baseline

**Objetivo**: provar que a sprint tem escopo, docs e baseline alinhados ao Programa 1 e ao E27.1 antes de escrever código.

- Script: `bin/s28_g0_scope_and_baseline.sh`  
- Verifica:  
  - Existência e integridade dos docs macro:  
    - `docs/sprint_28_cap_1_contexto.md`  
    - `docs/sprint_28_cap_2_estados_gates.md`  
    - `docs/sprint_28_cap_3_arquitetura_filemap.md`  
    - `docs/sprint_28_cap_4_execucao_evidencias.md`  
  - Coerência mínima entre S28 e a descrição de E27.1 no Roadmap (via checks simples ou checklist textual).  
- Evidências:  
  - `out/evidence/S28_G0_scope_and_baseline/*`  
  - `out/scorecards/S28_G0_scope_and_baseline.json`

### G1 — S28_G1_sources_model_and_schema

**Objetivo**: consolidar o modelo de fonte e garantir que o banco o reflita corretamente.

- Script: `bin/s28_g1_sources_model_and_schema.sh`  
- Verifica:  
  - Migrations de S28 aplicadas (via `alembic upgrade head` ou equivalente).  
  - Schema resultante contém os campos e tipos esperados para `Source` e entidades relacionadas.  
  - Testes de domínio (`pytest tests/domain/test_sources_model_invariants.py`) passam, garantindo invariantes de estado e ciclo de vida.  
- Evidências:  
  - Dump de schema, logs de migration, relatório de testes de domínio.

### G2 — S28_G2_sources_admin_api

**Objetivo**: garantir que a API de admin `/admin/sources` é correta e estável.

- Script: `bin/s28_g2_sources_admin_api.sh`  
- Verifica:  
  - Execução de `pytest tests/api/test_admin_sources_crud_onoff.py`.  
  - Cobertura de casos: criação, listagem, detalhe, edição, transições de estado válidas e proibidas, erros 400/404/409 onde esperado.  
  - Opcional: snapshot da documentação OpenAPI atualizado.  
- Evidências:  
  - Logs de testes, snapshot de OpenAPI, exemplos de curl capturados.

### G3 — S28_G3_sources_console_front

**Objetivo**: garantir que o Console de Fontes v2 está funcional, alinhado ao Design System e passa pelos fluxos principais.

- Script: `bin/s28_g3_sources_console_front.sh`  
- Verifica:  
  - `npm test` e `npm run build` na pasta `frontend/inspectah-ui`.  
  - Testes de UI (ex.: Playwright/Vitest) em `frontend/inspectah-ui/tests/sources/sources_console_onoff.spec.ts` incluindo:  
    - Criar fonte,  
    - Editar fonte,  
    - Ativar/desativar fonte,  
    - Interação com estados vazios/erro.  
  - Opcional: checagem simples de que os componentes usados pertencem ao Design System Admin v1 (por convenção/imports).  
- Evidências:  
  - Logs de testes e build, prints/screenshots ou gravação de fluxo.

### G4 — S28_G4_sources_ingestion_integration

**Objetivo**: provar que ON/OFF de fonte conversa com a Ingestão 2.0.

- Script: `bin/s28_g4_sources_ingestion_integration.sh`  
- Verifica (via testes de integração + script):  
  - Cenário 1:  
    - Fonte criada em `ACTIVE` com `AUTO`.  
    - Ingestão roda ao menos 1 vez (com registro em `IngestionRun`).
  - Cenário 2:  
    - Fonte é desativada (`DISABLED`) via API/console.  
    - Novas ingestões automáticas dessa fonte deixam de ocorrer.  
  - Cenário 3:  
    - Fonte é reativada (`ACTIVE`).  
    - Ingestão automática volta a ocorrer.  
- Evidências:  
  - Logs de teste, prints de `IngestionRun`, timeline dos eventos.

### G5 — S28_G5_observability_and_legacy_sanity

**Objetivo**: preservar confiabilidade e sanidade de S21/S22.

- Script: `bin/s28_g5_observability_and_legacy_sanity.sh`  
- Verifica:  
  - Logs e métricas de fontes e ingestão ainda fazem sentido após as mudanças.  
  - Execução de um subconjunto de gates antigos:  
    - Ex.: `bin/s21_g1_sources_domain.sh`, `bin/s21_g2_sources_api.sh`, `bin/s22_g1_ingestion_core.sh`, `bin/s22_g2_ingestion_metrics.sh` (nomes ilustrativos).  
  - Todos em PASS.  
- Evidências:  
  - Logs dos gates de S21/S22, scorecards reemitidos se necessário.

### G6 — S28_G6_demo_internal

**Objetivo**: validar, com olhos humanos, que a S28 entregou algo operável.

- Script: `bin/s28_g6_demo_internal.sh` (principalmente um wrapper para registrar artefatos)  
- Verifica:  
  - Execução de um roteiro de demo, por exemplo:  
    1. Criar uma nova fonte RSS de notícias,  
    2. Ver a fonte aparecer na lista e conferir campos,  
    3. Desativar a fonte,  
    4. Confirmar via logs/console de ingestão que ela parou de ser ingerida,  
    5. Reativar e ver ingestões voltarem.  
  - Registro dessa demo (vídeo curto ou screenshots) + notas rápidas de usabilidade da equipe.  
- Evidências:  
  - Pasta com mídia da demo e um mini-relato de feedback.

### G7 — S28_G7_go_no_go

**Objetivo**: consolidar a decisão final da sprint.

- Script: `bin/s28_g7_go_no_go.sh`  
- Verifica:  
  - Todos os gates G0–G6 com status `PASS`.  
  - Geração de `out/scorecards/S28_overall.json` com:  
    - resumo dos estados-alvo,  
    - breve análise de risco,  
    - decisão `GO` ou `NO_GO`.  
- Evidências:  
  - Scorecard consolidado e assinado pela liderança técnica do squad.

---

## 5. Arquitetura & Filemap da Sprint 28

### 5.1 Backend — domínio, DB, serviços e API

**Domínio / modelos**  
- `app/sources/models.py`  
  - `class Source(Base)`: campos, enums e invariantes de estado.  
  - `class SourceType(Base)`: tipos de fonte e metadados de validação.  
  - Enums: `SourceState`, `SourceMode`, `SourceCriticality`.

**Esquemas e validação**  
- `app/sources/schemas.py`  
  - `SourceCreate`, `SourceUpdate`, `SourceDetail`, `SourceListItem`.  
  - Validações específicas por `SourceType` (ex.: URL obrigatória para RSS).

**Serviços**  
- `app/sources/service.py`  
  - Funções de alto nível para criar/editar fontes,  
  - Funções para `activate_source`, `disable_source`, `deprecate_source`,  
  - Aplicação de invariantes e registros de `state_reason`.

**Migrations**  
- `migrations/versions/00xx_s28_sources_model_consolidation.py`  
  - Ajusta campos, cria novas colunas (ex.: `criticality`, `state_reason`), migra dados antigos se necessário.

**API de admin**  
- `app/api/admin_sources_routes.py`  
  - Rotas `/admin/sources` (GET/POST), `/admin/sources/{id}` (GET/PUT),  
  - Rotas de ON/OFF: `/admin/sources/{id}/activate` etc.  
  - Integração com schemas e serviços.

### 5.2 Integração com Ingestão 2.0

- `app/ingestion/scheduler.py`  
  - Lógica que decide quais fontes entram em cada ciclo de ingestão.  
  - Respeita `Source.state` e `Source.mode` (ex.: `AUTO` + `ACTIVE`).

- `tests/integration/test_sources_ingestion_onoff.py`  
  - Cenários básicos de ON/OFF × ingestão, usados pelo G4.

### 5.3 Frontend — Console de Fontes v2

**Páginas e componentes**  
- `frontend/inspectah-ui/src/features/sources/pages/SourcesListPage.tsx`  
- `frontend/inspectah-ui/src/features/sources/pages/SourceFormPage.tsx`  
- `frontend/inspectah-ui/src/features/sources/components/SourceListTable.tsx`  
- `frontend/inspectah-ui/src/features/sources/components/SourceStateBadge.tsx`  
- `frontend/inspectah-ui/src/features/sources/components/SourceActionsMenu.tsx`

**Camada de API no front**  
- `frontend/inspectah-ui/src/features/sources/api/adminSourcesApi.ts`  
  - Funções para chamar os endpoints de admin, tratar erros e mapear DTOs.

**Testes de UI**  
- `frontend/inspectah-ui/tests/sources/sources_console_onoff.spec.ts`  
  - Fluxos de criação, edição, ON/OFF, e verificação de estados visuais.

### 5.4 Tests, gates, scorecards e evidências

**Tests**  
- `tests/domain/test_sources_model_invariants.py`  
- `tests/api/test_admin_sources_crud_onoff.py`  
- `tests/integration/test_sources_ingestion_onoff.py`

**Scripts de gates (bin/)**  
- `bin/s28_g0_scope_and_baseline.sh`  
- `bin/s28_g1_sources_model_and_schema.sh`  
- `bin/s28_g2_sources_admin_api.sh`  
- `bin/s28_g3_sources_console_front.sh`  
- `bin/s28_g4_sources_ingestion_integration.sh`  
- `bin/s28_g5_observability_and_legacy_sanity.sh`  
- `bin/s28_g6_demo_internal.sh`  
- `bin/s28_g7_go_no_go.sh`

**Evidências & scorecards**  
- `out/evidence/S28_G0_scope_and_baseline/**`  
- `out/evidence/S28_G1_sources_model_and_schema/**`  
- …  
- `out/evidence/S28_G7_go_no_go/**`  
- `out/scorecards/S28_G0_scope_and_baseline.json` … `S28_G7_go_no_go.json`  
- `out/scorecards/S28_overall.json`

---

## 6. Plano de Execução (Waves)

### Wave 0 — Alinhamento e preparação

- Revisar: Roadmap E27, Programa 1, S21/S22, Lessons Learned S25.  
- Confirmar filemap, nomes de scripts, padrão de scorecards.  
- Escrever e rodar G0, garantindo que a sprint começa com docs e escopo claros.

### Wave 1 — Modelo de fonte + migrations (G1)

- Ajustar `app/sources/models.py` e enums associados.  
- Implementar migration `00xx_s28_sources_model_consolidation.py`.  
- Criar testes de domínio para invariantes de estado.  
- Rodar G1 até PASS estável.

### Wave 2 — API `/admin/sources` (G2)

- Implementar/ajustar rotas em `admin_sources_routes.py`.  
- Escrever `tests/api/test_admin_sources_crud_onoff.py`.  
- Atualizar OpenAPI.  
- Rodar G2 com PASS.

### Wave 3 — Console de Fontes v2 (G3)

- Refatorar front para usar Design System Admin v1.  
- Implementar telas e fluxos principais.  
- Escrever testes de UI.  
- Rodar G3 com PASS.

### Wave 4 — Integração ON/OFF × Ingestão 2.0 (G4)

- Ajustar scheduler para respeitar `Source.state`+`Source.mode`.  
- Escrever testes de integração.  
- Rodar G4 com PASS.

### Wave 5 — Observabilidade + legado + demo (G5–G7)

- Rodar e ajustar gates relevantes de S21/S22 (G5).  
- Preparar e registrar demo interna (G6).  
- Consolidar scorecards e rodar G7 com decisão final.

---

Este documento v2 é o contrato refinado da Sprint 28. Ele liga explicitamente o S28 ao Programa 1 e ao épico E27, define estados-alvo testáveis, gates claros, filemap preciso e um plano de execução em waves. A partir dele, o time e o Codex conseguem executar a sprint com rigor, previsibilidade e rastreabilidade total.

