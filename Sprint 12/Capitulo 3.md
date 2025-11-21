# Inspectah – Sprint 12
## Capítulo 3 — Arquitetura & Filemap (Ingestão Contínua & Comunidade v0)

---

## 0. TL;DR — o que este capítulo garante

Este Capítulo 3 crava, sem ambiguidade:

- **Quais componentes** existem na S12 (serviços, scripts, módulos, UI);
- **Como eles se encaixam** na Truth‑DB + Guardião da S10 (sem duplicar papel de ninguém);
- **Onde cada coisa mora no repositório** (filemap estável e Codex‑friendly);
- **Que arquivos/scripts implementam cada gate** S12‑G0…S12‑G8 do Cap. 2.

Se alguém abrir o repo, ler Cap. 1–3 e ainda tiver dúvida de “onde codar o quê”, este capítulo falhou. A meta aqui é: **zero ambiguidade, zero gordura**.

---

## 1. Papel do Capítulo 3 na Sprint 12

Recap rápido:

- **Cap. 1 – Visão**: qual é a promessa da S12 (serviço 24/7, Debunker v0 em tudo, casos/temas com timeline, Explorer v0, feedback mínimo).
- **Cap. 2 – Gates**: como medimos essa promessa (SLIs/SLOs, G0…G8, DoD).
- **Cap. 3 – Arquitetura & Filemap (este)**: como **desenhar e localizar** tudo isso dentro do Inspectah.

Objetivos concretos do Cap. 3:

1. Definir **arquitetura lógica** da S12 (camadas e componentes, com responsabilidades claras).
2. Fixar **filemap exato** (nomes de pastas/arquivos/scripts) que o Codex deve usar.
3. Mapear **gate → scripts → módulos → evidências** (para execução e auditoria).
4. Reforçar as restrições da fase atual: **sem blockchain, sem reputação pesada, sem Sistema de Blocos completo, sem comunidade avançada**.

---

## 2. Princípios arquiteturais da S12

A equipe fixa alguns princípios que devem guiar toda decisão técnica nesta sprint:

1. **Uma única fonte de verdade**  
   Toda verdade materializada continua saindo da **Truth‑DB da S10**, via Guardião. A S12 só adiciona ingestão contínua, views de caso/timeline e UX/feedback em cima disso.

2. **Adapters, não atalhos**  
   Nenhum componente da S12 fala diretamente com tabelas internas da Truth‑DB. Toda mutação passa por um **adaptador S10**, que:
   - expõe operações de alto nível para S12; e
   - delega ao Guardião as ações reais sobre blocos/fatos/versões.

3. **Camadas separadas, contratos simples**  
   Ingestão, decisão, views de caso/timeline, experiência de usuário e observabilidade são camadas distintas, com contratos bem definidos.

4. **Idempotência como regra, logs como caixa‑preta**  
   Reprocessar eventos não pode criar caos. Logs devem permitir reconstruir o “filme” ingestão → Debunker → Truth‑DB → Explorer → feedback.

5. **Simplicidade operacional (Pavel)**  
   Poucas fontes, poucos scripts, poucas rotas. Tudo tem que caber na cabeça de uma pessoa de operação, sem precisar abrir 10 diagramas.

6. **Zero vazamento da Fase 2**  
   Nada de blockchain, reputação numérica, Sistema de Blocos completo ou features de comunidade avançada no código da S12. Se surgir a necessidade, vai para ADR e backlog da Fase 2.

---

## 3. Visão em camadas

Sem desenhar figuras, a S12 fica assim:

1. **Camada de fontes externas**  
   Diários oficiais, portais de transparência, feeds de clima, APIs especializadas etc.

2. **Camada de ingestão S12**  
   - registry de fontes + scheduler;
   - conectores específicos para cada fonte;
   - pipeline de ingestão e normalização.

3. **Camada de decisão (Debunker + Truth‑DB S10)**  
   - Debunker v0 classifica eventos (`aceito/incerto/suspeito`) com racional;
   - adaptador Truth‑DB traduz decisões em ações do Guardião;
   - Truth‑DB persiste blocos/fatos/versões/estados.

4. **Camada de casos/temas & timeline S12**  
   - monta casos/temas e timelines como views organizadas do que a Truth‑DB já sabe;
   - aplica invariantes (I1–I3 do Cap. 1).

5. **Camada de experiência (Explorer v0 + feedback)**  
   - backend com rotas de busca, lista de casos, página de caso e feedback;
   - frontend com busca, timeline, links de fontes e botão “reportar problema”;
   - painel interno de triagem de feedbacks.

6. **Camada de observabilidade & gates**  
   - métricas (SLI‑1…SLI‑5), logs e snapshots;
   - scripts `bin/s12_g*.sh` para G0…G8;
   - scorecards em `out/scorecards/` e evidências em `out/evidence/`.

---

## 4. Componentes e responsabilidades

### 4.1. Registry de fontes & Scheduler

**Responsabilidades principais**

- Manter catálogo de fontes: `id_fonte`, domínio, tipo, URL, cadência, autenticação, flags.
- Expor funções de consulta (`list_sources`, `get_source_config`).
- Rodar scheduler central que decide quais fontes rodar e quando.
- Registrar sucessos, falhas e retries de forma rastreável.

**Impacto em gates**: G1 (fontes & scheduler), G2 (pipeline), G7 (observabilidade).

---

### 4.2. Conectores & Pipeline de ingestão

**Conectores**

- Um conector por fonte prioritária (ex.: diário oficial, portal de transparência, feed climático), responsável por:
  - falar com a API/HTML/CSV;
  - produzir uma coleção de eventos brutos com metadados mínimos (timestamp, fonte, payload).

**Pipeline**

- Normalizar eventos brutos em eventos S12 com campos mínimos (caso/tema, datas, domínio, texto de apoio, id_fonte, etc.).
- Resolver `id_caso` via serviço de casos (criar ou localizar caso).
- Roteamento determinístico evento → caso.
- Garantir idempotência (mesmo input não gera múltiplos eventos lógicos sem motivo).

**Impacto em gates**: G1, G2, G4, G7.

---

### 4.3. Debunker v0 Runner

**Responsabilidades principais**

- Receber eventos normalizados elegíveis para Truth‑DB.
- Chamar Debunker v0 (módulo já existente ou ampliado para S12).
- Registrar estado (`aceito/incerto/suspeito`) + racional em armazenamento estruturado.
- Repassar decisão para adaptador Truth‑DB, que aciona o Guardião conforme S10.

**Meta dura**: `debunker_coverage = 1.0` para todos os eventos elegíveis (SLI‑2).

**Impacto em gates**: G3 (cobertura), G4 (integridade de casos), G7 (observabilidade).

---

### 4.4. Adaptador Truth‑DB (S10)

**Responsabilidades principais**

- Expor para S12 operações de alto nível, como:
  - `register_event_for_case(evento_normalizado, estado_debunker, racional)`;
  - `apply_debunker_decision(id_evento, decisao)`;
  - `get_case_snapshot(id_caso)`.
- Internamente, traduzir essas operações em actions/commands da Truth‑DB S10.
- Garantir que S12 **não** precise conhecer detalhes de schema interno da Truth‑DB.

**Impacto em gates**: G2, G3, G4, G7.

---

### 4.5. Casos/Temas & Timeline Service

**Responsabilidades principais**

- Manter entidade `Caso` (id, domínio, título, descrição, status geral derivado).
- Garantir invariantes do Cap. 1:
  - I1: todo evento normalizado pertence a exatamente um caso (ou dispara criação atômica de um novo caso);
  - I2: um caso pertence a um único domínio;
  - I3: timeline é append‑only; correções aparecem como novos eventos/versões.
- Expor consultas:
  - buscar casos por texto;
  - listar eventos em ordem cronológica;
  - gerar snapshots de timeline para evidência.

**Impacto em gates**: G2, G4, G5, G7.

---

### 4.6. Explorer v0 Backend

**Responsabilidades principais**

- Expor API para a UI do Explorer v0:
  - `GET /explorer/cases?query=...` – busca de casos;
  - `GET /explorer/cases/{id_caso}` – detalhes + timeline;
  - `POST /explorer/cases/{id_caso}/feedback` – feedback no nível de caso;
  - `POST /explorer/events/{id_evento}/feedback` – feedback no nível de evento.
- Orquestrar `s12_case_service`, `s12_timeline_service` e `s12_feedback_service`.

**Impacto em gates**: G5 (navegação), G6 (feedback), G7 (observabilidade).

---

### 4.7. Explorer v0 Frontend

**Responsabilidades principais**

- Implementar experiência mínima da S12:
  - tela de busca de casos;
  - lista de casos com status geral e última atualização;
  - página de caso com resumo + timeline + links de fontes;
  - botão “reportar problema”.

**Impacto em gates**: G5 (fluxos F1–F3), G6 (ponto de origem do feedback).

---

### 4.8. Feedback Service & Painel interno

**Responsabilidades principais**

- Persistir feedbacks com campos mínimos:
  - `id_feedback`, `id_caso`/`id_evento`, texto, autor (opcional), timestamps, status.
- Expor funções:
  - `create_feedback(...)`;
  - `list_feedbacks(status)`;
  - `update_feedback_status(id_feedback, status)`.
- Rotas internas para painel de triagem:
  - `GET /internal/feedbacks?status=...`;
  - `POST /internal/feedbacks/{id_feedback}/status`.

**Impacto em gates**: G6 (entrega de feedback), G7 (observabilidade do fluxo de feedback).

---

### 4.9. Observabilidade & Gates Runner

**Responsabilidades principais**

- Coletar métricas relevantes (SLI‑1…SLI‑5) a partir das camadas anteriores.
- Consolidar logs de ingestão, Debunker, Explorer e feedbacks.
- Implementar scripts de gate `bin/s12_g0…bin/s12_g8` que:
  - rodem checks específicos;
  - emitam scorecards;
  - gravem evidências.

**Impacto em gates**: todos (G0…G8), com foco em G7.

---

## 5. Filemap detalhado da Sprint 12

### 5.1. Documentos (Sprint 12/ e docs/)

**Pasta da sprint**

- `Sprint 12/Capitulo 1.md` – visão (Cap. 1)
- `Sprint 12/Capitulo 2.md` – gates (Cap. 2)
- `Sprint 12/Capitulo 3.md` – arquitetura & filemap (este)
- `Sprint 12/Capitulo 4.md` – execução & Codex (a gerar)

**Docs espelhados**

- `docs/sprint_12_cap_1_visao.md`
- `docs/sprint_12_cap_2_gates.md`
- `docs/sprint_12_cap_3_arquitetura_filemap.md`
- `docs/sprint_12_cap_4_exec_codex.md`

**ADRs da sprint** (nomes ilustrativos):

- `docs/adr/adr_s12_001_slis_slos.md`
- `docs/adr/adr_s12_002_gates_evolucao.md`
- `docs/adr/adr_s12_003_observabilidade_minima.md`

---

### 5.2. Scripts de gates (bin/)

Cada gate tem um entrypoint em `bin/`:

- `bin/s12_g0_env_repo.sh`
- `bin/s12_g1_sources_scheduler.sh`
- `bin/s12_g2_ingest_pipeline.sh`
- `bin/s12_g3_debunker_coverage.sh`
- `bin/s12_g4_cases_timeline.sh`
- `bin/s12_g5_explorer_e2e.sh`
- `bin/s12_g6_feedback_flow.sh`
- `bin/s12_g7_observabilidade.sh`
- `bin/s12_g8_decision.sh`

Orquestrador:

- `bin/s12_gates_all.sh` – roda G0…G7, aborta em FAIL, imprime resumo.

Todos seguem padrão DNA: `set -euo pipefail`, logs simples, caminhos determinísticos para scorecards/evidências.

---

### 5.3. Ingestão & Scheduler (scripts/)

- `scripts/s12_sources_registry.py`
  - operações de CRUD e listagem de fontes;
  - export de snapshot para evidência do G1 (`sources_config.json`).

- `scripts/s12_scheduler.py`
  - laço principal ou hooks para cron;
  - decide quais fontes rodar;
  - registra execuções e falhas.

- `scripts/s12_run_connector.py`
  - wrapper que recebe `id_fonte`;
  - carrega config do registry;
  - chama conector apropriado e entrega eventos brutos ao pipeline.

- `scripts/s12_connectors/`
  - `scripts/s12_connectors/obra_publica_diario_oficial.py`
  - `scripts/s12_connectors/obra_publica_portal_transparencia.py`
  - `scripts/s12_connectors/evento_climatico_feed_nacional.py`
  - (um arquivo por fonte crítica das duas famílias de domínio piloto)

---

### 5.4. Pipeline de ingestão e normalização (scripts/)

- `scripts/s12_ingest_pipeline.py`
  - orquestra a cadeia: eventos brutos → normalizados → casos → Debunker/Truth‑DB;
  - aplica normalizadores específicos por domínio;
  - garante idempotência e loga erros.

- `scripts/s12_normalizers/`
  - `scripts/s12_normalizers/obra_publica.py`
  - `scripts/s12_normalizers/evento_climatico.py`
  - podem existir outros, mas a S12 foca nas famílias piloto.

---

### 5.5. Debunker Runner & Adaptador Truth‑DB (scripts/)

- `scripts/s12_debunker_runner.py`
  - recebe eventos normalizados elegíveis;
  - chama Debunker v0;
  - grava decisão e racional;
  - chama `s12_truthdb_adapter`.

- `scripts/s12_truthdb_adapter.py`
  - implementa funções de alto nível para S12 conversar com a Truth‑DB;
  - interna e exclusivamente, usa primitives/actions definidas na S10.

---

### 5.6. Casos/Temas & Timeline (scripts/)

- `scripts/s12_case_service.py`
  - criação/atualização de casos;
  - busca por texto;
  - cálculo de status geral do caso a partir de eventos/estados.

- `scripts/s12_timeline_service.py`
  - manutenção da projeção de timeline por caso;
  - aplicação das invariantes I1–I3;
  - export de snapshots para evidência do G4.

---

### 5.7. Explorer v0 – Backend (app/)

Supondo app HTTP Python:

- `app/explorer/__init__.py`
- `app/explorer/routes.py`

Rotas mínimas:

- `GET /explorer/cases?query=...`
- `GET /explorer/cases/{id_caso}`
- `POST /explorer/cases/{id_caso}/feedback`
- `POST /explorer/events/{id_evento}/feedback`

Essas rotas chamam diretamente:

- `s12_case_service`
- `s12_timeline_service`
- `s12_feedback_service`

---

### 5.8. Explorer v0 – Frontend (ui/)

Se o repo já tem frontend (ex.: React), a S12 adiciona:

- `ui/explorer/SearchPage.tsx`
- `ui/explorer/CasePage.tsx`
- `ui/explorer/components/Timeline.tsx`
- `ui/explorer/components/FeedbackButton.tsx`

Cap. 4 detalha stack, mas o filemap fixa a estrutura lógica do Explorer v0.

---

### 5.9. Feedback Service & Painel interno

Backend:

- `scripts/s12_feedback_service.py`
  - `create_feedback(...)`, `list_feedbacks(status)`, `update_feedback_status(...)`.

Rotas internas:

- `app/feedback/routes.py`
  - `GET /internal/feedbacks?status=...`
  - `POST /internal/feedbacks/{id_feedback}/status`

Frontend interno (se existir UI administrativa):

- `ui/admin/FeedbackListPage.tsx`

---

### 5.10. Artefatos de validação (out/)

**Scorecards**

- `out/scorecards/S12_G0_env_repo.json`
- `out/scorecards/S12_G1_sources_scheduler.json`
- `out/scorecards/S12_G2_ingest_pipeline.json`
- `out/scorecards/S12_G3_debunker_coverage.json`
- `out/scorecards/S12_G4_cases_timeline.json`
- `out/scorecards/S12_G5_explorer_e2e.json`
- `out/scorecards/S12_G6_feedback_flow.json`
- `out/scorecards/S12_G7_observabilidade.json`
- `out/scorecards/S12_G8_decision.json`

**Evidências por gate** (exemplos mínimos):

- `out/evidence/S12_G0/env_snapshot.json`, `files_present.json`
- `out/evidence/S12_G1/sources_config.json`, `scheduler_logs.txt`, `freshness_sample.json`
- `out/evidence/S12_G2/pipeline_fixtures_input.json`, `pipeline_normalized_output.json`, `idempotency_check.json`
- `out/evidence/S12_G3/debunker_decisions_sample.json`, `coverage_report.json`
- `out/evidence/S12_G4/cases_snapshot.json`, `timelines_sample.json`
- `out/evidence/S12_G5/explorer_flow_results.json` (+ prints/HAR opcionais)
- `out/evidence/S12_G6/feedback_flow_results.json`, `feedbacks_sample.json`
- `out/evidence/S12_G7/metrics_snapshot.json`, `logs_sample.txt`
- `out/evidence/S12_G8/summary.md`, `risks_and_debts.md` (opcional)

---

## 6. Mapa gate → scripts → componentes

Para o Codex não errar o alvo:

- **G0 – Env/Repo**  
  - script: `bin/s12_g0_env_repo.sh`  
  - usa: estrutura do repo + docs da S12.

- **G1 – Fontes & Scheduler**  
  - script: `bin/s12_g1_sources_scheduler.sh`  
  - usa: `scripts/s12_sources_registry.py`, `scripts/s12_scheduler.py`, `scripts/s12_connectors/*`.

- **G2 – Pipeline de ingestão/normalização**  
  - script: `bin/s12_g2_ingest_pipeline.sh`  
  - usa: `scripts/s12_ingest_pipeline.py`, `scripts/s12_normalizers/*`, `scripts/s12_case_service.py`, `scripts/s12_truthdb_adapter.py`.

- **G3 – Debunker v0**  
  - script: `bin/s12_g3_debunker_coverage.sh`  
  - usa: `scripts/s12_debunker_runner.py`, `scripts/s12_truthdb_adapter.py`.

- **G4 – Casos/temas & timeline**  
  - script: `bin/s12_g4_cases_timeline.sh`  
  - usa: `scripts/s12_case_service.py`, `scripts/s12_timeline_service.py`, `scripts/s12_truthdb_adapter.py`.

- **G5 – Explorer v0 E2E**  
  - script: `bin/s12_g5_explorer_e2e.sh`  
  - usa: `app/explorer/routes.py`, `ui/explorer/*`, serviços de caso/timeline.

- **G6 – Feedback E2E**  
  - script: `bin/s12_g6_feedback_flow.sh`  
  - usa: rotas `/explorer/*/feedback`, `scripts/s12_feedback_service.py`, rotas `/internal/feedbacks`.

- **G7 – Observabilidade**  
  - script: `bin/s12_g7_observabilidade.sh`  
  - usa: métricas (SLI‑1…SLI‑5) + logs de ingestão, Debunker, Explorer e feedbacks.

- **G8 – Decisão GO/NO‑GO**  
  - script: `bin/s12_g8_decision.sh`  
  - usa: todos os scorecards G0…G7, gera scorecard de decisão + resumo humano.

---

## 7. Fluxos principais (dinâmica da arquitetura)

### 7.1. Fluxo de ingestão contínua

1. `s12_scheduler` lê `s12_sources_registry` e decide quais fontes rodar.
2. Dispara `s12_run_connector` para cada `id_fonte`:
   - conector coleta dados da fonte;
   - produz eventos brutos.
3. `s12_ingest_pipeline` converte eventos brutos em eventos normalizados, resolve `id_caso` via `s12_case_service`.
4. Eventos elegíveis seguem para `s12_debunker_runner`:
   - Debunker v0 decide estado + racional;
   - `s12_truthdb_adapter` aplica decisão na Truth‑DB (via Guardião).
5. `s12_timeline_service` atualiza projeção de timeline/caso conforme os dados da Truth‑DB.

---

### 7.2. Fluxo de leitura no Explorer v0

1. Usuário acessa `/explorer/cases?query=...`.
2. Backend chama `s12_case_service` (e, se preciso, adaptador S10) para listar casos.
3. Usuário abre `/explorer/cases/{id_caso}`.
4. Backend chama `s12_case_service` + `s12_timeline_service` para montar visão do caso.
5. Frontend exibe resumo, timeline, estados e links de fontes originais.

---

### 7.3. Fluxo de feedback “reportar problema”

1. Usuário clica em “reportar problema” (caso ou evento).
2. Frontend envia POST para rota `/explorer/.../feedback`.
3. Backend chama `s12_feedback_service.create_feedback(...)`.
4. Feedback é persistido em storage interno.
5. Operador abre `/internal/feedbacks` e vê lista por status.
6. Operador marca `em_analise` / `resolvido` e, se necessário, aciona reprocessamento (sempre via adaptador S10).

---

### 7.4. Fluxo de observabilidade & gates

1. Cada componente registra métricas e logs (eventos/hora, erros/hora, distribuição de estados, SLIs).
2. Scripts de gate (G1…G7) usam essas métricas/logs + fixtures para gerar scorecards e evidências.
3. `bin/s12_g7_observabilidade.sh` consolida SLIs ao longo de uma janela de operação.
4. `bin/s12_g8_decision.sh` lê todos os scorecards e produz decisão GO/NO‑GO da S12.

---

## 8. Restrições oficiais da S12 (para o Codex não viajar)

- **Proibido** implementar qualquer integração com blockchain, smart contracts ou anchors on‑chain na S12.
- **Proibido** criar mecanismos de reputação numérica (de fontes, usuários, feedbacks) nesta sprint.
- **Proibido** implementar Sistema de Blocos completo (blocos/sub‑blocos/componentes com regras de promoção/rebaixamento).
- **Proibido** implementar comunidade avançada (perfis públicos, followers, ranking, votação, threads públicas).

Qualquer necessidade nessa linha deve:

1. Ser registrada como ADR (ex.: `adr_s12_0xx_future_blockchain.md`);
2. Seguir para backlog da Fase 2.

---

## 9. Checklist de consistência da S12 (para dev/Codex)

Antes de declarar o Cap. 3 “cumprido” na implementação, a equipe pode usar este checklist rápido:

1. **Arquitetura**
   - [ ] Existe um registry de fontes + scheduler que roda sem depender de hacks locais.
   - [ ] Conectores estão isolados em `scripts/s12_connectors/` e não vazam lógica de normalização.
   - [ ] O Debunker v0 é acessado apenas via `s12_debunker_runner.py`.
   - [ ] Toda interação com a Truth‑DB passa por `s12_truthdb_adapter.py`.

2. **Casos/Timeline**
   - [ ] `s12_case_service.py` e `s12_timeline_service.py` existem e aplicam invariantes I1–I3.
   - [ ] É possível exportar snapshots de casos/timelines para evidência do G4.

3. **Explorer & Feedback**
   - [ ] Rotas `/explorer/*` e `/internal/feedbacks` existem e estão conectadas aos serviços corretos.
   - [ ] UI do Explorer v0 permite executar os fluxos F1–F3 do Cap. 2.
   - [ ] Feedbacks criados na UI aparecem na fila interna em tempo aceitável.

4. **Gates & Observabilidade**
   - [ ] Todos os scripts `bin/s12_g0…bin/s12_g8` existem e produzem scorecards.
   - [ ] `out/scorecards/` e `out/evidence/` seguem a estrutura descrita neste capítulo.
   - [ ] `bin/s12_gates_all.sh` roda localmente e falha rápido em qualquer gate crítico.

Se todas as caixas acima estiverem marcadas, a implementação da S12 está alinhada com Cap. 1–3 e pronta para ser refinada/automatizada no Cap. 4.

