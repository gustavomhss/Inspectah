# Sprint 19 – Capítulo 3
## Filemap, Arquitetura e Encaixe com o Repositório Real

Este capítulo cristaliza a Sprint 19 (“Timeline e Raio‑X do Inspectah”) em um **mapa de arquivos e arquitetura** alinhado com o repositório real do Inspectah e com o DNA/Sprint Playbook. Ele é o contrato operacional que liga:

- a visão macro (Capítulo 1),
- os gates, métricas e jornadas (Capítulo 2),
- e o plano de execução detalhado para o Codex (Capítulo 4).

Aqui respondemos, de forma inequívoca, a três perguntas:

1. **Onde** cada peça da S19 mora no repo?
2. **Como** backend, frontend, fixtures e gates se encaixam para entregar Timeline + Raio‑X sem quebrar S17/S18?
3. **Quais invariantes estruturais** precisam se manter verdadeiros para a sprint ser sustentável e auditável?

Nada neste capítulo exige reescrever sprints anteriores. A S19 é um **módulo de diagnóstico profundo**, apoiado na infraestrutura já consolidada da Truth‑DB, Debunker e Console de Admin.

---
## 1. Princípios de Arquitetura da S19

1. **Um único backend de admin, extensível**  
   Não existe “segundo backend”. A S19 estende o módulo existente em `app/admin/` e o app FastAPI em `inspectah/api.py`, adicionando contratos para Timeline e Raio‑X sob o mesmo guarda‑chuva `/admin`.

2. **Uma única SPA de admin, com novas rotas e telas**  
   Toda a experiência visual vive em `frontend/inspectah-ui/`. A S19 adiciona páginas, componentes e rotas abaixo do namespace de admin, reaproveitando layout, estilos e padrões de interação da S18.

3. **Camada de serviço como tradutor oficial da Truth‑DB**  
   As rotas de admin não falam direto com storage cru. A leitura do Sistema de Blocos/Truth‑DB passa por funções de serviço em `app/admin/service.py`, que convertem o estado consolidado em DTOs de Timeline e Raio‑X.

4. **Fixtures dedicadas e reutilizáveis**  
   Casos, timelines e raios‑X usados em testes e gates da S19 vivem em `Sprint 19/fixtures/`, com naming estável e reaproveitado por backend, frontend (via MSW) e scripts de gates.

5. **Gates como “usuário de primeira classe”**  
   Os scripts `bin/s19_g*.sh` consomem exatamente as mesmas APIs e rotas que um operador real. Eles geram scorecards em `out/scorecards/` e evidências em `out/evidence/` sem atalhos ocultos.

6. **Compatibilidade estrita com S17 e S18**  
   S17 continua sendo a jornada do usuário final; S18, o Console de Admin geral. A S19 **apenas adiciona profundidade** (Timeline + Raio‑X) conectada às telas de casos de admin, sem alterar contratos existentes nem quebrar fluxos já aprovados.

---
## 2. Visão Geral de Filemap da Sprint 19

Repositório local (já existente):

- Raiz: `/Users/gustavoschneiter/Documents/Inspectah`

A S19 toca ou cria arquivos apenas em áreas específicas:

- Backend de admin: `app/admin/` + `inspectah/api.py`.
- SPA de admin: `frontend/inspectah-ui/src/...`.
- Fixtures e documentação da sprint: `Sprint 19/`.
- Gates/scorecards/evidências: `bin/`, `out/scorecards/`, `out/evidence/`.
- CI da sprint: `.github/workflows/`.

As seções seguintes detalham cada bloco.

---
## 3. Backend de Admin – Timeline e Raio‑X

### 3.1 Módulos existentes e extensão S19

A S19 assume a base já entregue em sprints anteriores (especialmente S18):

- `app/admin/routes.py` – rotas FastAPI de admin (`/admin/sources`, `/admin/cases`, `/admin/health` etc.).
- `app/admin/schemas.py` – modelos Pydantic para DTOs de admin.
- `app/admin/service.py` – funções de serviço que leem snapshots/armazenamento consolidado e expõem DTOs para o Console de Admin.
- `inspectah/api.py` – criação do app FastAPI (`build_app()` + `app = build_app()`) e registro do router de admin.

A S19 **não introduz um novo módulo paralelo**; ela estende esses arquivos, mantendo a mesma topologia e padrões de código.

### 3.2 Novos schemas para Timeline e Raio‑X

Arquivo a ser estendido: `app/admin/schemas.py`

A S19 adiciona os seguintes tipos (nomes ilustrativos, mas estáveis):

- `AdminTimelineEvent`
  - `id: str`
  - `case_id: str`
  - `timestamp: datetime`
  - `event_type: str` (ex.: `"block_created"`, `"anchor_ok"`, `"anchor_failed"`, `"committee_vote"`, `"contest_opened"`)
  - `severity: Optional[str]` (ex.: `"info"`, `"warning"`, `"critical"`)
  - `source: Optional[str]` (fonte/bloco relacionado)
  - `summary: str` (texto curto para exibição em card)

- `AdminTimelineResponse`
  - `case_id: str`
  - `events: List[AdminTimelineEvent]`

- `AdminCaseXRay`
  - `case_id: str`
  - `title: str`
  - `category: Optional[str]`
  - `status: str` (estado atual do caso/bloco principal)
  - `risk: Optional[str]` (baixo/médio/alto, alinhado com Debunker)
  - `summary: str` (resumo textual geral)
  - `debunker: AdminDebunkerSection`
  - `committees: AdminCommitteesSection`
  - `anchors: AdminAnchorsSection`
  - `evidences: AdminEvidenceSection`

- Seções internas (também em `schemas.py`):
  - `AdminDebunkerSection` – nível de risco, explicação curta, principais flags.
  - `AdminCommitteesSection` – visão agregada de V1/V2/V3, com vereditos e divergências.
  - `AdminAnchorsSection` – âncoras relevantes, estados e mensagens de erro.
  - `AdminEvidenceSection` – evidências principais e links para blocos/artefatos.

Regras de modelagem:

- Campos opcionais são explicitamente marcados como `Optional[...]`; nada de `Any` solto.
- Enums/status seguem naming já usado em S17/S18 para não fragmentar significados.
- As estruturas são pensadas para golden tests: forma estável, fácil de serializar e comparar.

### 3.3 Camada de serviço – leitura da Truth‑DB

Arquivo a ser estendido: `app/admin/service.py`

A S19 adiciona funções de alto nível, isolando a lógica de montagem de Timeline/Raio‑X:

- `list_case_timeline(case_id: str) -> AdminTimelineResponse`
- `get_case_xray(case_id: str) -> Optional[AdminCaseXRay]`

Fontes de dados (sem reiventar storage):

- Snapshots de casos/timelines gerados em S12/S10 (ingestão + Truth‑DB), ou estruturas equivalentes já utilizadas por `list_admin_cases()`.
- Evidências e blocos consolidados em `out/evidence/` e/ou storage interno do domínio.

Invariantes obrigatórios:

- A lista `events` de `AdminTimelineResponse` vem **ordenada por timestamp ascendente**.
- IDs de eventos são determinísticos, permitindo diffs/goldens (ex.: `"evento_climatico:inmet-2025-0901#anchor_ok@2025-09-01T12:00:00Z"`).
- `get_case_xray` não inventa dados: se a Truth‑DB não tem informação suficiente, campos ficam vazios/None, mas o modelo continua válido.

### 3.4 Rotas FastAPI – endpoints S19

Arquivo a ser estendido: `app/admin/routes.py`

Novas rotas `/admin`:

- `GET /admin/cases/{case_id}/timeline`
  - Usa `list_case_timeline(case_id)`.
  - Retorna `AdminTimelineResponse` em casos conhecidos.
  - Retorna `404` (HTTPException) quando o caso não existe ou não há timeline configurada.

- `GET /admin/cases/{case_id}/xray`
  - Usa `get_case_xray(case_id)`.
  - Retorna `AdminCaseXRay` quando há raio‑X disponível.
  - Retorna `404` quando não há raio‑X para o `case_id` solicitado.

As rotas entram no mesmo `APIRouter` de admin usado pela S18, preservando tags, prefix e dependências já existentes.

### 3.5 Integração no app principal

Arquivo já existente: `inspectah/api.py`

Requisito da S19:

- Garantir que o router de admin (já registrado) agora também expõe as novas rotas de Timeline/Raio‑X sem qualquer ajuste estrutural extra.
- Opcionalmente, incluir tags/descriptions adicionais na documentação OpenAPI para agrupar endpoints de diagnóstico (`"Admin – Timeline"`, `"Admin – XRay"`).

### 3.6 Testes de backend da S19

Diretório: `tests/admin/`

Arquivo novo dedicado à S19:

- `tests/admin/test_admin_timeline_xray_endpoints.py`

Cobertura mínima:

- `GET /admin/cases/{id}/timeline`
  - Cenário feliz com caso conhecido: status `200`, `case_id` correto, `events` não vazios, ordenados e com campos chave preenchidos.
  - Cenário `404` para caso inexistente.

- `GET /admin/cases/{id}/xray`
  - Cenário feliz com caso conhecido: status `200`, seções `debunker`, `committees`, `anchors` e `evidences` presentes.
  - Cenário `404` para caso inexistente.

Esses testes alimentam diretamente gates como S19_G1, S19_G4 e S19_G5.

---
## 4. Frontend de Admin – Timeline e Raio‑X

### 4.1 Organização geral

Base da SPA: `frontend/inspectah-ui/`

A S19 trabalha inteiramente dentro da SPA existente, sob o namespace de admin:

- Páginas: `frontend/inspectah-ui/src/pages/admin/`
- Componentes: `frontend/inspectah-ui/src/components/admin/`
- API client: `frontend/inspectah-ui/src/api/admin/`
- Tipos compartilhados: `frontend/inspectah-ui/src/types/admin.ts`
- Testes: `frontend/inspectah-ui/src/__tests__/admin/`

### 4.2 Rotas e páginas

Arquivos novos/estendidos:

- `frontend/inspectah-ui/src/pages/admin/AdminCaseTimelinePage.tsx`
  - Página dedicada à Timeline do caso.
  - Consome `/admin/cases/:caseId/timeline` via client de API.
  - Exibe a linha do tempo com filtros simples (período e tipo de evento).

- `frontend/inspectah-ui/src/pages/admin/AdminCaseXRayPage.tsx`
  - Página dedicada ao Raio‑X do caso.
  - Consome `/admin/cases/:caseId/xray`.
  - Renderiza seções Debunker, Comitês, Âncoras e Evidências de forma organizada.

- Ajustes em `frontend/inspectah-ui/src/pages/admin/AdminCasesPage.tsx` e/ou `AdminCaseDetailPage.tsx`
  - Adicionar ações “Ver timeline” e “Ver raio‑X” para cada caso, levando às rotas da S19.

- Ajustes em `frontend/inspectah-ui/src/App.tsx`
  - Registrar rotas novas:
    - `/admin/cases/:caseId/timeline` → `AdminCaseTimelinePage`.
    - `/admin/cases/:caseId/xray` → `AdminCaseXRayPage`.

### 4.3 Componentes de Timeline

Diretório sugerido: `frontend/inspectah-ui/src/components/admin/timeline/`

Componentes principais:

- `Timeline.tsx`
  - Recebe `events: AdminTimelineEvent[]` e estado de filtros.
  - É responsável por agrupar, ordenar e desenhar a linha do tempo.

- `TimelineEventCard.tsx`
  - Renderiza um evento individual com ícone, cor por severidade, resumo textual e timestamp.

- `TimelineFilters.tsx`
  - Controles para período (7 dias, 30 dias, tudo) e tipos de evento.

Esses componentes seguem o padrão visual do admin da S18 (Tailwind, espaçamentos consistentes, uso de cards e badges).

### 4.4 Componentes de Raio‑X

Diretório sugerido: `frontend/inspectah-ui/src/components/admin/xray/`

Componentes principais:

- `CaseXRayLayout.tsx`
  - Orquestra a página de Raio‑X, recebendo `AdminCaseXRay` e distribuindo para as sub‑seções.

- `DebunkerPanel.tsx`
  - Mostra risco, resumo do Debunker e flags principais.

- `CommitteesPanel.tsx`
  - Cards por comitê (V1, V2, V3) com veredito, confiança e divergências.

- `AnchorsPanel.tsx`
  - Lista as âncoras relevantes, estados, timestamps e mensagens de erro.

- `EvidenceSummaryPanel.tsx`
  - Mostra as evidências principais, tipos, fontes e links/ações.

Esses componentes podem (e devem) reutilizar badges, cards e tipografia genérica já definidos em `src/components/admin/`.

### 4.5 Tipos e API client

Arquivo a ser estendido: `frontend/inspectah-ui/src/types/admin.ts`

- Adicionar interfaces alinhadas aos schemas de backend:
  - `AdminTimelineEvent` e `AdminTimelineResponse`.
  - `AdminCaseXRay` e seções internas (Debunker, Comitês, Âncoras, Evidências).

Arquivo a ser estendido: `frontend/inspectah-ui/src/api/admin/index.ts`

- Adicionar funções de client:
  - `getAdminCaseTimeline(caseId: string): Promise<AdminTimelineResponse>`.
  - `getAdminCaseXRay(caseId: string): Promise<AdminCaseXRay>`.

Essas funções encapsulam `fetch`/`axios` (conforme padrão do projeto), retornando tipos fortes e tratando erros básicos.

### 4.6 Testes de frontend

Diretório: `frontend/inspectah-ui/src/__tests__/admin/`

Arquivo novo para a S19:

- `AdminTimelineXRay.test.tsx`

Cobertura mínima:

- Montar `AdminCaseTimelinePage` com MSW servindo uma Timeline de fixture.
- Montar `AdminCaseXRayPage` com MSW servindo um Raio‑X de fixture.
- Verificar estados:
  - Loading, erro e “sem eventos/sem dados”.
  - Render das seções obrigatórias (Debunker, Comitês, Âncoras, Evidências).
  - Navegação a partir de AdminCasesPage/AdminCaseDetailPage para Timeline/Raio‑X.

Esses testes conversam diretamente com S19_G2, S19_G3 e S19_G6.

---
## 5. Fixtures e Dados da Sprint 19

Diretório base: `Sprint 19/`

A S19 adiciona fixtures reutilizáveis pelos três eixos (backend, gates e UI via MSW).

### 5.1 Estrutura de fixtures

Subdiretório:

- `Sprint 19/fixtures/`

Exemplos de arquivos:

- `timeline_expected_evento_climatico_inmet_2025_0901.json`
- `timeline_expected_fofoca_celebridade_x.json`
- `timeline_expected_mandato_politico_y.json`
- `timeline_expected_projeto_obra_publica_z.json`

(Usando `case_id` como base do nome para evitar ambiguidade.)

Opcionalmente, fixtures de Raio‑X para smoke/golden tests:

- `xray_expected_evento_climatico_inmet_2025_0901.json`
- etc.

### 5.2 Uso das fixtures

- **Backend (tests/admin)**
  - Carrega fixtures de timeline/raio‑X para validar endpoints de forma determinística.

- **Gates S19_G4 e S19_G5**
  - Comparam resposta da API com `timeline_expected_*.json` e `xray_expected_*.json` para garantir completude/correção.

- **Frontend (MSW)**
  - Usa as mesmas fixtures como resposta fake de backend, garantindo que UI e backend falem o mesmo idioma de dados.

---
## 6. Gates, Scorecards e Evidências da S19

### 6.1 Scripts de gates

Diretório: `bin/`

A S19 define (ou consolida, se já criados) os scripts:

- `bin/s19_g0_scope.sh`
- `bin/s19_g1_contracts_and_data.sh`
- `bin/s19_g2_journeys_and_ux.sh`
- `bin/s19_g3_front_quality.sh`
- `bin/s19_g4_timeline_correctness.sh`
- `bin/s19_g5_xray_consistency_and_depth.sh`
- `bin/s19_g6_metrics_and_demo.sh`
- `bin/s19_g7_ci_and_observability.sh`
- `bin/s19_g8_go_no_go.sh`
- Orquestrador: `bin/s19_all.sh`

Padrão obrigatório de implementação:

- Shebang `#!/usr/bin/env bash`.
- `set -euo pipefail`.
- Cálculo de `ROOT_DIR` relativo ao próprio script.
- Criação de pastas em `out/scorecards/` e `out/evidence/S19_G*/`.
- Execução dos comandos específicos do gate.
- Emissão de scorecard JSON via `python3 - <<'PY'` com campos `gate_id`, `status`, `timestamp`, `metrics`, `details`.

### 6.2 Scorecards

Diretório: `out/scorecards/`

A S19 gera os arquivos:

- `out/scorecards/S19_G0_scope.json`
- `out/scorecards/S19_G1_contracts_and_data.json`
- `out/scorecards/S19_G2_journeys_and_ux.json`
- `out/scorecards/S19_G3_front_quality.json`
- `out/scorecards/S19_G4_timeline_correctness.json`
- `out/scorecards/S19_G5_xray_consistency_and_depth.json`
- `out/scorecards/S19_G6_metrics_and_demo.json`
- `out/scorecards/S19_G7_ci_and_observability.json`
- `out/scorecards/S19_G8_go_no_go.json`

O scorecard de G6 concentra os valores medidos para M1…M6; G8 lê todos os demais para decidir GO/NO‑GO.

### 6.3 Evidências

Diretório: `out/evidence/`

Padrão: `out/evidence/<gate_id>/`

- `out/evidence/S19_G0_scope/` — lista de arquivos in/out of scope, notas de escopo.
- `out/evidence/S19_G1_contracts_and_data/` — exemplos de payloads, snapshots OpenAPI recortados.
- `out/evidence/S19_G2_journeys_and_ux/` — screenshots/logs de jornadas de Timeline/Raio‑X.
- `out/evidence/S19_G3_front_quality/` — logs de lint/test/build da SPA.
- `out/evidence/S19_G4_timeline_correctness/` — comparações expected vs actual de timeline.
- `out/evidence/S19_G5_xray_consistency_and_depth/` — relatórios de completude das seções do Raio‑X.
- `out/evidence/S19_G6_metrics_and_demo/` — tempos medidos, cliques até evidência, scripts de demo.
- `out/evidence/S19_G7_ci_and_observability/` — workflow YAML, logs/resumos de CI.
- `out/evidence/S19_G8_go_no_go/` — decisão consolidada e referências cruzadas a todos os outros scorecards.

Essas pastas são parte integrante do ORR da sprint.

---
## 7. CI e Encaixe com Sprints Anteriores

### 7.1 Workflow de CI da S19

Diretório: `.github/workflows/`

Workflow dedicado (nome sugerido):

- `.github/workflows/_s19_timeline_xray.yml`

Responsabilidades:

- Rodar, pelo menos:
  - `bin/s19_g3_front_quality.sh`.
  - Um recorte representativo de `s19_g4_timeline_correctness.sh`, `s19_g5_xray_consistency_and_depth.sh` e `s19_g6_metrics_and_demo.sh` (ou comandos equivalentes encapsulados).
- Publicar scorecards/evidências de S19 como artefatos de CI.
- Disparar em PRs que toquem arquivos da S19 e em push para `main`.

### 7.2 Corrente S17 → S18 → S19

- S17 continua sendo a jornada do usuário final (pergunta → resposta → risco/resumo).
- S18 oferece o Console de Admin com visão de saúde, fontes e casos.
- S19 adiciona a “camada forense”: a partir do detalhe de um caso em admin, o operador consegue abrir Timeline e Raio‑X para entender **como** o sistema chegou naquele estado.

Fluxo típico:

1. Usuário final faz consulta (S17) e recebe resposta + risco.
2. Operador abre o caso correspondente no Console de Admin (S18).
3. Investigador/curador aprofunda o caso via Timeline e Raio‑X (S19) para analisar blocos, comitês, âncoras e evidências.

---
## 8. Invariantes Estruturais da S19

Para manter o padrão de excelência da sprint, os seguintes invariantes são mandatórios:

1. **Nenhum atalho direto ao storage cru**  
   Toda leitura para Timeline/Raio‑X passa por `app/admin/service.py`. Nada de consultas ad‑hoc espalhadas em rotas ou scripts.

2. **Separação limpa entre backend e frontend**  
   Páginas de Timeline/Raio‑X conhecem apenas os tipos e clients de `src/types/admin.ts` e `src/api/admin/index.ts`. Detalhes internos de storage/domínio ficam encapsulados no backend.

3. **Gates idempotentes e reentrantes**  
   Rodar `bin/s19_all.sh` quantas vezes for preciso não deve quebrar o repo nem produzir scorecards divergentes, apenas atualizar timestamps/medidas.

4. **Evidências suficientes para “contar a história”**  
   Cada gate deve deixar rastro em `out/evidence/S19_G*/` que permita a qualquer pessoa reconstruir o que foi testado, com que dados e que decisão foi tomada.

5. **Zero regressão em S17/S18**  
   A introdução de Timeline/Raio‑X não pode quebrar rotas, contratos ou telas já validadas em S17/S18.

Com este capítulo, a Sprint 19 passa a ter um filemap sólido, explícito e compatível com o DNA do Inspectah. O próximo passo (Capítulo 4) é transformar este mapa em um plano de execução preciso para o Codex, garantindo que cada arquivo citado aqui seja criado/configurado exatamente como descrito, com gates e evidências amarrando a entrega fim‑a‑fim.

