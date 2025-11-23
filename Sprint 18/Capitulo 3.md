# Inspectah — Sprint 18
## Capítulo 3 — Filemap, arquitetura e pontos de entrada do Console de Admin

> Arquivo alvo no repositório: `Sprint 18/Capitulo 3.md`  
> Domínio: Frontend — Console de Admin (Fontes, Casos/Temas, Saúde Operacional)  
> Este capítulo descreve **onde** cada peça da S18 vive no repositório, **como** o código de admin se organiza e **quais** são os pontos de entrada oficiais para gates, CI e demos.

---

### 1. Objetivo do capítulo

Os capítulos anteriores responderam:

- **Cap. 1** — o que a S18 precisa ser (visão, contexto, escopo);  
- **Cap. 2** — como vamos provar que a S18 foi entregue (gates, métricas, evidências).

Este **Capítulo 3** responde:

- onde cada coisa da S18 mora no repositório (filemap);  
- como o **Console de Admin** se encaixa na SPA existente;  
- quais são os **scripts, fixtures e caminhos oficiais** usados pelos gates S18_G0…S18_G8;  
- como estruturar o repo para que o Cap. 4 possa simplesmente dizer: “rode `bin/...` e veja as evidências em `out/...`”, sem inventar caminhos.

Depois deste capítulo, não deve sobrar dúvida do tipo “onde coloco esse arquivo?”, “qual script roda tal gate?” ou “para onde esse gate escreve o scorecard?”.

---

### 2. Topologia da S18 no repositório

A S18 segue o padrão do Inspectah, com três eixos principais:

1. **Pasta de sprint (documentos e fixtures da S18)**
2. **Código de produto (frontend + backend)**
3. **Infra de gates/CI/evidências**

#### 2.1 Pasta da sprint

```text
/Sprint 18/
  Capitulo 1.md                  # Visão, contexto e escopo (S18_Cap1)
  Capitulo 2.md                  # Gates, métricas e evidências (S18_Cap2)
  Capitulo 3.md                  # Filemap, arquitetura e entrypoints (S18_Cap3, este arquivo)
  Capitulo 4.md                  # Runbooks de execução, prompts Codex, demos (S18_Cap4)
  fixtures/
    admin_sources_fixture.json   # Conjunto de fontes conhecido para testes de G4
    admin_cases_fixture.json     # Conjunto de casos/temas conhecido para testes de G4/G6
    admin_health_fixture.json    # Snapshot de health para cenários de G5
```

A pasta `Sprint 18/fixtures/` guarda datasets estáveis para gates que exigem cenários controlados (especialmente S18_G4, S18_G5, S18_G6). Esses fixtures são consumidos por scripts específicos e **não** devem ser alterados sem atualizar os scorecards de referência.

#### 2.2 Código de produto — visão macro

A S18 não cria um novo projeto: ela **estende** o Inspectah existente. A topologia macro esperada é:

```text
/                                # raiz do repositório Inspectah
  docs/
    sprint_18_overview.md        # Wrap executivo da sprint, citado em S18_G8

  frontend/                      # SPA React/Vite/Tailwind (S17 + S18 + futuras S19/S20)
    ...

  backend/                       # FastAPI + Truth-DB + Sistema de Blocos + Admin APIs
    ...

  bin/                           # Scripts de gates e orquestração (S7, S10, S18, ORR etc.)
    s18_g0_scope.sh
    s18_g1_arch_front_and_api.sh
    s18_g2_journeys_and_ux.sh
    s18_g3_front_quality.sh
    s18_g4_ui_vs_backend.sh
    s18_g5_health_mapping.sh
    s18_g6_metrics_and_demo.sh
    s18_g7_ci_and_observability.sh
    s18_g8_go_no_go.sh
    s18_all.sh                   # (Opcional) roda G0…G7 em sequência, usado em demos/CI local

  out/
    scorecards/
      S18_G0_scope.json
      S18_G1_arch_front_and_api.json
      S18_G2_journeys_and_ux.json
      S18_G3_front_quality.json
      S18_G4_ui_vs_backend.json
      S18_G5_health_mapping.json
      S18_G6_metrics_and_demo.json
      S18_G7_ci_and_observability.json
      S18_G8_go_no_go.json
    evidence/
      S18_G0_scope/
      S18_G1_arch_front_and_api/
      S18_G2_journeys_and_ux/
      S18_G3_front_quality/
      S18_G4_ui_vs_backend/
      S18_G5_health_mapping/
      S18_G6_metrics_and_demo/
      S18_G7_ci_and_observability/
      S18_G8_go_no_go/

  .github/
    workflows/
      _s18_admin_front.yml       # Workflow de CI focado em build/lint/test do Console de Admin
```

Os nomes de arquivos de scorecard seguem **exatamente** o padrão definido no Cap. 2. As pastas de evidência podem conter logs, capturas de tela, dumps de respostas de API, manifests e quaisquer artefatos adicionais referenciados pelos gates.

Caso o projeto use outro layout (por exemplo, `web/` em vez de `frontend/`), este capítulo deve ser ajustado para refletir a realidade, mas **sempre mantendo**:

- um diretório claro para o front da SPA;  
- um diretório claro para o backend;  
- scripts de gates em `bin/`;  
- scorecards em `out/scorecards/`;  
- evidências em `out/evidence/`.

---

### 3. Arquitetura de frontend para o Console de Admin

A S18 expande a SPA da S17, sem criar um front separado. O Console de Admin mora em um **namespace próprio** dentro do front, reaproveitando layout, tema e roteamento existentes.

#### 3.1 Organização de pastas de frontend

```text
/frontend/
  src/
    main.tsx                     # bootstrap da SPA, já existente (S17)
    router.tsx                   # definição de rotas, inclui agora rotas de admin

    pages/
      admin/
        AdminLayout.tsx          # layout base do console de admin (header, sidebar, etc.)
        AdminOverviewPage.tsx    # Visão Geral (Health)
        AdminSourcesPage.tsx     # Lista de fontes
        AdminSourceDetailPage.tsx
        AdminCasesPage.tsx       # Lista de casos/temas
        AdminCaseDetailPage.tsx

    components/
      admin/
        HealthSummaryCards.tsx   # cards de health (fontes, casos, integrações)
        SourcesTable.tsx         # tabela de fontes com filtros
        SourceStatusBadge.tsx
        CasesTable.tsx           # tabela de casos/temas com filtros
        CaseStatusBadge.tsx
        RiskBadge.tsx
        EmptyState.tsx           # estados vazios/sem dados em admin
        LoadingState.tsx         # estados de loading em admin
        ErrorState.tsx           # estados de erro amigáveis em admin

    api/
      admin/
        adminClient.ts           # cliente HTTP focal de admin (fetch/axios)
        sources.ts               # funções typed para /admin/sources e /admin/sources/{id}
        cases.ts                 # funções typed para /admin/cases e /admin/cases/{id}
        health.ts                # funções typed para /admin/health

    types/
      admin/
        Source.ts                # tipos para fontes (id, nome, tipo, status, timestamps, etc.)
        Case.ts                  # tipos para casos/temas
        Health.ts                # tipos para health agregada (contagens, flags principais)

    hooks/
      useAdminRouteGuard.ts      # gate simples para /admin (flag de env, modo interno etc.)
      useAdminSources.ts         # hook para carregar/listar fontes com cache básico
      useAdminCases.ts           # hook para carregar/listar casos/temas
      useAdminHealth.ts          # hook para Visão Geral (health)

    tests/
      admin/
        AdminOverviewPage.test.tsx
        AdminSourcesPage.test.tsx
        AdminCasesPage.test.tsx
        AdminRouting.test.tsx    # garante que /admin e subrotas renderizam sem explodir
```

A nomenclatura (`.tsx` vs `.jsx`, presença de `index.ts`, etc.) deve acompanhar a convenção já usada na S17, mas a **separação lógica `admin/`** precisa ser mantida para não misturar componentes de consulta com admin.

#### 3.2 Rotas de admin

O roteador principal (`frontend/src/router.tsx` ou equivalente) deve incluir, no mínimo:

- `/admin` → `AdminOverviewPage` dentro de `AdminLayout`;  
- `/admin/sources` → `AdminSourcesPage`;  
- `/admin/sources/:sourceId` → `AdminSourceDetailPage`;  
- `/admin/cases` → `AdminCasesPage`;  
- `/admin/cases/:caseId` → `AdminCaseDetailPage`.

A aplicação de `useAdminRouteGuard` garante que essas rotas fiquem protegidas em ambientes onde o console ainda não é público (por exemplo, só acessíveis em dev/homolog ou atrás de auth tratada em S20).

#### 3.3 Integração visual com a SPA existente

- O `AdminLayout` reaproveita o **mesmo sistema de layout** da S17 (header, tema, tipografia), para reforçar a sensação de produto único.  
- Componentes genéricos (botões, dropdowns, inputs, ícones) devem ser importados de bibliotecas/pastas compartilhadas (por exemplo, `components/ui/`), evitando forks visuais.

---

### 4. Arquitetura de backend para Admin

A S18 não redesenha o backend; ela explicita e organiza o espaço de admin dentro da estrutura existente (FastAPI).

#### 4.1 Módulo de admin no backend

```text
/backend/
  app/
    admin/
      __init__.py
      routes.py                # definição de endpoints de admin (fontes, casos, health)
      schemas.py               # Pydantic models para requests/responses de admin
      service.py               # lógica de agregação/leitura para admin
      dependencies.py          # dependências específicas de admin (ex.: acesso à Truth-DB)

    core/
      ...                      # núcleo de Truth-DB, Sistema de Blocos, Debunker etc.

  tests/
    admin/
      test_admin_sources.py
      test_admin_cases.py
      test_admin_health.py
```

Se o projeto já usar organização diferente (por exemplo, `app/api/admin/routes.py`), a S18 deve seguir o padrão, mas mantendo um **namespace claro de admin** (rotas, schemas, serviços, testes agrupados).

#### 4.2 Endpoints oficiais de admin

Os contratos do Cap. 2 aparecem aqui como rotas concretas:

- `GET /admin/sources`  
  Lista fontes com paginação simples e filtros básicos (status, tipo).

- `GET /admin/sources/{id}`  
  Traz detalhe de uma fonte, incluindo histórico curto de execuções/checagens.

- `GET /admin/cases`  
  Lista casos/temas monitorados, com estado atual, categoria e risco agregado (quando houver).

- `GET /admin/cases/{id}`  
  Traz detalhe de um caso/tema, com resumo, estado atual e principais fontes/evidências associadas.

- `GET /admin/health`  
  Agrega sinais de watchers/scorecards em um objeto simples de health (fontes saudáveis vs degradadas, casos estáveis vs em atenção/contestação, integrações críticas).

O **mapeamento entre Truth-DB/Sistema de Blocos e esses schemas de admin** mora em `service.py`, mantendo a regra: admin **só lê estados consolidados**, nunca estados intermediários.

---

### 5. Scripts de gates e arquivos de saída (S18_G0…S18_G8)

Cada gate do Cap. 2 tem um script de entrada em `bin/` e um conjunto padronizado de saídas em `out/`.

#### 5.1 Convenções gerais

- Todos os scripts de gate da S18:
  - assumem `PYTHONPATH=.` na raiz do repo;  
  - escrevem logs/evidências em `out/evidence/S18_G*/`;  
  - escrevem um scorecard único em `out/scorecards/S18_G*.json` com, no mínimo:  
    - `gate_id`, `status`, `timestamp`, `details` (objeto), `metrics` (quando houver).

- O script opcional `bin/s18_all.sh` executa G0…G7 em ordem e falha se qualquer gate falhar.

#### 5.2 Gate a gate

**S18_G0 — Intenção & escopo travados**

```text
bin/s18_g0_scope.sh
  ↳ Lê:    Sprint 18/Capitulo 1.md
           Sprint 18/Capitulo 2.md
           docs/inspectah_sprint_18_macro.md        (se existir)
  ↳ Escreve: out/scorecards/S18_G0_scope.json
             out/evidence/S18_G0_scope/README.md    (resumo humano opcional)
```

O script pode ser uma checagem semi‑manual (por exemplo, baseada em checklist), mas o **local de saída** é fixo.

---

**S18_G1 — Arquitetura de front & contratos de admin**

```text
bin/s18_g1_arch_front_and_api.sh
  ↳ Lê:    Sprint 18/Capitulo 3.md
           backend/app/admin/routes.py
           backend/app/admin/schemas.py
           backend/app/admin/service.py
           frontend/src/pages/admin/
           frontend/src/api/admin/
  ↳ Escreve: out/scorecards/S18_G1_arch_front_and_api.json
             out/evidence/S18_G1_arch_front_and_api/
               openapi_admin.json        (snapshot opcional da spec de admin)
               notes.md                  (observações sobre contratos)
```

O script pode validar, por exemplo, se as rotas esperadas existem na OpenAPI e se os campos essenciais aparecem.

---

**S18_G2 — Journeys & UX do Console de Admin**

```text
bin/s18_g2_journeys_and_ux.sh
  ↳ Lê:    frontend/src/pages/admin/
           frontend/src/router.tsx
           Sprint 18/Capitulo 1.md (seção de perfis e jornadas)
  ↳ Usa:   ambiente local/homolog rodando, acessando /admin, /admin/sources, /admin/cases
  ↳ Escreve: out/scorecards/S18_G2_journeys_and_ux.json
             out/evidence/S18_G2_journeys_and_ux/
               journeys.md      (descrição das jornadas executadas)
               screenshots/     (prints opcionais das telas)
```

G2 pode ser semi‑automatizado (por exemplo, Cypress/Playwright) ou check manual guiado, mas a saída **sempre** converge para esses paths.

---

**S18_G3 — Qualidade de implementação de frontend**

```text
bin/s18_g3_front_quality.sh
  ↳ Roda:   comandos de build/lint/test do front (npm/pnpm/yarn)
  ↳ Escreve: out/scorecards/S18_G3_front_quality.json
             out/evidence/S18_G3_front_quality/build.log
             out/evidence/S18_G3_front_quality/lint.log
             out/evidence/S18_G3_front_quality/tests.log
```

Esse gate não precisa conhecer detalhes de admin; ele apenas garante que o front, **incluindo** admin, passa no mínimo de qualidade.

---

**S18_G4 — Coerência UI ↔ Backend (Fontes & Casos)**

```text
bin/s18_g4_ui_vs_backend.sh
  ↳ Prepara:  carrega fixtures de admin em ambiente de teste (se aplicável)
              Sprint 18/fixtures/admin_sources_fixture.json
              Sprint 18/fixtures/admin_cases_fixture.json
  ↳ Compara:  respostas de backend (/admin/sources, /admin/cases)
              com dados visíveis na UI (via testes E2E ou API interna do front)
  ↳ Escreve:  out/scorecards/S18_G4_ui_vs_backend.json
              out/evidence/S18_G4_ui_vs_backend/
                backend_sources_snapshot.json
                backend_cases_snapshot.json
                ui_sources_snapshot.json
                ui_cases_snapshot.json
                diff_report.md
```

Aqui são calculadas M3 e M4 (cobertura de fontes e casos) e registradas no scorecard.

---

**S18_G5 — Saúde operacional refletida na UI**

```text
bin/s18_g5_health_mapping.sh
  ↳ Prepara:  Sprint 18/fixtures/admin_health_fixture.json   (opcional)
  ↳ Lê:       backend/app/admin/routes.py   (endpoint /admin/health)
              frontend/src/pages/admin/AdminOverviewPage.tsx
  ↳ Exercita: cenários de health (tudo ok, fontes degradadas, casos em atenção)
  ↳ Escreve:  out/scorecards/S18_G5_health_mapping.json
              out/evidence/S18_G5_health_mapping/
                backend_health_snapshots.json
                ui_health_snapshots.json
                scenarios.md
```

M1 (tempo de carregamento da Visão Geral) é medido aqui e salvo em `metrics` dentro do scorecard.

---

**S18_G6 — Experiência de operação end‑to‑end**

```text
bin/s18_g6_metrics_and_demo.sh
  ↳ Usa:    ambiente local/homolog com Console de Admin completo
  ↳ Roda:   cenários de ponta a ponta (scripts de teste ou automação E2E)
  ↳ Calcula: M2, M5, M6
  ↳ Escreve: out/scorecards/S18_G6_metrics_and_demo.json
             out/evidence/S18_G6_metrics_and_demo/
               scenarios.md
               demo_notes.md
               recordings/         (opcional, gravações de tela ou GIFs)
```

Esse gate é o ponto central de demonstração da S18.

---

**S18_G7 — Observabilidade + CI da S18**

```text
bin/s18_g7_ci_and_observability.sh
  ↳ Lê:     .github/workflows/_s18_admin_front.yml
            outros workflows relevantes de front
  ↳ Verifica: se build/lint/test de admin estão plugados na CI
               se falhas graves em /admin quebrariam a pipeline
  ↳ Escreve:  out/scorecards/S18_G7_ci_and_observability.json
              out/evidence/S18_G7_ci_and_observability/
                workflows_list.md
                ci_last_run_summary.log
```

Aqui não se roda a CI em si (isso é papel do GitHub Actions), mas registra‑se o estado da integração da S18 com a CI.

---

**S18_G8 — GO/NO‑GO da Sprint 18**

```text
bin/s18_g8_go_no_go.sh
  ↳ Lê:    out/scorecards/S18_G0_scope.json
           out/scorecards/S18_G1_arch_front_and_api.json
           out/scorecards/S18_G2_journeys_and_ux.json
           out/scorecards/S18_G3_front_quality.json
           out/scorecards/S18_G4_ui_vs_backend.json
           out/scorecards/S18_G5_health_mapping.json
           out/scorecards/S18_G6_metrics_and_demo.json
           out/scorecards/S18_G7_ci_and_observability.json
           docs/sprint_18_overview.md
  ↳ Escreve: out/scorecards/S18_G8_go_no_go.json
             out/evidence/S18_G8_go_no_go/summary.json
```

O script faz a agregação, aplica as regras de GO/NO‑GO do Cap. 2 e registra a decisão final.

---

### 6. Integração com CI (GitHub Actions)

A S18 introduz (ou estende) um workflow específico para o Console de Admin:

```text
/.github/workflows/_s18_admin_front.yml
```

Responsabilidades típicas desse workflow:

- Instalar dependências do frontend;  
- Rodar `bin/s18_g3_front_quality.sh` (build/lint/test de front);  
- Opcionalmente, rodar um subconjunto de S18_G2, S18_G4 ou S18_G6 em modo headless (por exemplo, testes E2E de admin);  
- Publicar artefatos relevantes (logs de build/lint/test, scorecards da S18) como artefatos da run de CI.

Workflows globais (por exemplo, CI geral do backend/ORR) podem **invocar `bin/s18_all.sh`** como parte de um job de validação mais amplo.

---

### 7. Extensibilidade para S19 e S20

O filemap da S18 foi pensado para não virar gargalo nas sprints seguintes:

- A pasta `frontend/src/pages/admin/` pode ganhar, na S19, páginas adicionais de timeline e raio‑X (por exemplo, `AdminCaseTimelinePage.tsx`), sem quebrar a organização atual.  
- A pasta `frontend/src/components/admin/` suporta novos componentes de visualização (gráficos de timeline, painéis detalhados) sem conflitar com os componentes atuais de cards e tabelas.  
- O namespace `backend/app/admin/` pode ser estendido com novos endpoints (por exemplo, detalhes de bloco/sub‑bloco por caso) mantendo contratos de S18 intactos.  
- O padrão de scripts `bin/s18_g*_*.sh` e de scorecards em `out/scorecards/` serve de base direta para futuros `bin/s19_g*_*.sh`, `bin/s20_g*_*.sh`, com a mesma semântica de gates por sprint.

---

### 8. Definição de pronto (Cap. 3)

Do ponto de vista deste capítulo, consideramos o Cap. 3 **concluído** quando:

1. A árvore de arquivos aqui descrita existe (ou tem equivalentes claros) no repositório;  
2. Todos os scripts `bin/s18_g*_*.sh` existem como arquivos e escrevem nos caminhos de `out/scorecards/` e `out/evidence/` especificados (mesmo que, inicialmente, com lógica mínima);  
3. As rotas e módulos de admin no frontend e backend estão posicionados conforme este filemap (ou com variações explícitas e documentadas no próprio Cap. 3);  
4. O workflow `_s18_admin_front.yml` (ou equivalente) está presente em `.github/workflows/` e referenciado em S18_G7;  
5. O Cap. 4 consegue, sem inventar paths, referenciar scripts e artefatos definidos aqui para descrever “como rodar” a Sprint 18.

Quando esses pontos estiverem atendidos, o Time consegue mover‑se do **planejamento estrutural** da S18 (Cap. 1–3) para a **execução guiada** (Cap. 4), com um único mapa de arquivos como fonte de verdade.

