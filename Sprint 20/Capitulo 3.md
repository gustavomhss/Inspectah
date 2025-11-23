Inspectah — Sprint 20
Capítulo 3 — Arquitetura, Filemap e Pontos de Integração (Frontend — UX, Auth básica e Observabilidade) — Versão 2

0. One-liner do Capítulo 3
Este capítulo descreve como o frontend do Inspectah fica organizado após a Sprint 20 — camadas, pastas, arquivos principais e pontos de integração — para entregar a experiência unificada de consulta/admin/diagnóstico, com autenticação básica e observabilidade de UI, de forma estável o bastante para sustentar as sprints de Fase 2 (Sistema de Blocos, Debunker, governança e comunidade) sem reescrita estrutural.

1. Visão geral da arquitetura de frontend pós-S20

1.1 Camadas lógicas
Depois da S20, o frontend do Inspectah é organizado em quatro camadas principais, com responsabilidades explícitas:

1) Camada de shell e navegação (app shell)
– Responsável por:
  – layout principal;
  – roteamento (rotas públicas e privadas);
  – barra de navegação, breadcrumbs e estrutura de página;
  – tratamento global de erros (error boundaries);
  – integração com Providers de Auth e Logging.

2) Camada de domínios de UI
– Módulo de Consulta (S17): telas e componentes para o usuário final perguntar sobre fatos/casos/temas.
– Módulo de Admin (S18): telas para operadores/admins gerirem fontes, casos e saúde do sistema.
– Módulo de Casos/Timeline/Raio-X (S19): telas para diagnóstico profundo de casos, timeline de eventos/blocos e visão de raio-X.

3) Camada de núcleo (core)
– Auth: sessão, login/logout, guarda de rotas, injeção de tokens.
– API/HTTP: clientes HTTP tipados e centralizados.
– Config: URLs base, flags de ambiente, feature flags.
– Logging & Observabilidade: wrapper único para logs de eventos/erros de UI, incluindo correlação com o backend.

4) Camada compartilhada (shared)
– Componentes reutilizáveis (botões, inputs, tabelas, cards, modais, toasts, status pills).
– Layouts (containers, grids, cabeçalhos padrão).
– Hooks e utilitários (fetch com estados, mapeamento de estados de verdade, formatação de dados, helpers de responsividade).

Regras importantes alinhadas com a equipe:
– Domínios (consult/admin/cases) não acessam diretamente detalhes de infra: conversam com `core/` e `shared/`.
– Auth e logging vivem em `core/` + `app/providers/`, nunca espalhados como "if (localStorage...)" em componentes.
– Qualquer novo domínio deve seguir a mesma estrutura, evitando “ilhas” de código.

1.2 Relação com S17–S19

– S17 (consulta) é consolidada em `modules/consult/`, reaproveitando lógica existente, mas usando:
  – componentes de `shared/`;
  – hooks de `core/api` e `core/logging`;
  – estados de verdade via `shared/hooks/useTruthStateLabel` e `shared/components/StatusPill`.

– S18 (admin) é consolidada em `modules/admin/`, com:
  – páginas de dashboard, fontes e casos;
  – uso obrigatório de rotas protegidas via `AuthGuard`;
  – navegação clara para módulos de casos/timeline/raio-X.

– S19 (timeline/raio-X) é consolidada em `modules/cases/`, garantindo:
  – pages específicas para timeline e raio-X;
  – uso consistente de componentes de evidência/blocos;
  – exibição dos estados de verdade/incerteza de forma uniforme.

A Sprint 20 não cria domínios novos; ela reorganiza S17–S19 dentro dessa arquitetura, adicionando Auth e Observabilidade como camadas de primeira classe.

2. Filemap macro da Sprint 20

2.1 Estrutura de raiz do frontend

Na raiz do repositório do Inspectah, o frontend após a S20 deve ter, no mínimo:

– `frontend/`
  – `package.json`  
    – dependências, scripts de build/test/lint (incluindo scripts de S20).
  – `vite.config.ts`  
    – bundler/build.
  – `tsconfig.json`  
    – TypeScript.
  – `index.html`  
    – entry da aplicação.
  – `README.md`  
    – instruções de setup/uso, incluindo como rodar gates S20-G1…S20-G6.
  – `src/`  
    – código-fonte organizado por camadas.
  – `tests/`  
    – testes de integração/e2e do frontend, quando não integrados a `src/`.

2.2 Filemap de `frontend/src/`

– `frontend/src/`
  – `main.tsx`  
    – ponto de entrada React (monta `<App />`, registra Providers principais).
  – `App.tsx`  
    – shell principal: router, tema, AuthProvider, LoggerProvider, ErrorBoundary raiz.

  – `app/`
    – `routes.tsx`  
      – definição central de rotas, separando claramente:
        – rotas públicas (ex.: `/`, `/consult`);
        – rotas privadas (ex.: `/admin`, `/admin/cases/:id/timeline`, `/admin/cases/:id/xray`).
    – `layout/`
      – `MainLayout.tsx`  
        – layout padrão para rotas autenticadas (admin, cases).
      – `PublicLayout.tsx`  
        – layout para rotas públicas (consulta).
      – `ErrorBoundary.tsx`  
        – componente de Error Boundary global.
    – `providers/`
      – `AuthProvider.tsx`  
        – contexto de autenticação.
      – `LoggerProvider.tsx`  
        – contexto de logging/observabilidade.

  – `core/`
    – `auth/`
      – `auth-service.ts`  
        – funções de login/logout, leitura/escrita de token, refresh opcional.
      – `auth-guard.tsx`  
        – componente de rota protegida (envolve rotas privadas).
      – `auth-types.ts`  
        – tipos relacionados a sessão/usuário.
    – `api/`
      – `http-client.ts`  
        – cliente HTTP com baseURL, interceptors, headers de auth e correlação.
      – `endpoints.ts`  
        – catálogo de endpoints (consulta, fontes, casos, timeline, raio-X).
      – `api-types.ts`  
        – tipos de request/response.
    – `config/`
      – `env.ts`  
        – leitura de variáveis de ambiente e base URLs.
      – `feature-flags.ts`  
        – feature flags simples para UI.
    – `logging/`
      – `logger.ts`  
        – `logEvent`, `logError`, `logNavigation`.
      – `logging-types.ts`  
        – tipos de eventos/erros de UI.
      – `logging-config.ts`  
        – configuração de destinos e níveis.

  – `shared/`
    – `components/`
      – `Button.tsx`, `Input.tsx`, `Table.tsx`, `Card.tsx`, `Badge.tsx`, `Modal.tsx`, `Toast.tsx`.
      – `StatusPill.tsx`  
        – componente para estados de verdade/incerteza.
      – `ErrorMessage.tsx`  
        – componente padronizado de erro amigável ao usuário.
    – `layout/`
      – `PageHeader.tsx`  
        – título/subtítulo/ações.
      – `PageContainer.tsx`  
        – container com largura máxima, padding e responsividade padrão.
    – `hooks/`
      – `useQueryWithStatus.ts`  
        – hook para chamadas a API com estados (loading/success/error) + logging automático.
      – `useTruthStateLabel.ts`  
        – hook para mapear estados de verdade em labels/cores.
    – `lib/`
      – `formatters.ts`  
        – formatação de datas/números.
      – `responsive.ts`  
        – helpers de breakpoints/responsividade.
      – `truth-states.ts`  
        – enum/tipos para estados de verdade/incerteza.

  – `modules/`
    – `consult/` (S17)
      – `pages/`
        – `ConsultPage.tsx`  
          – página principal de consulta.
      – `components/`
        – `QueryForm.tsx`  
          – formulário de pergunta.
        – `AnswerPanel.tsx`  
          – exibição de resposta, risco e evidências.
      – `hooks/`
        – `useConsultQuery.ts`  
          – orquestra envio da pergunta, logging e tratamento de erro.

    – `admin/` (S18)
      – `pages/`
        – `LoginPage.tsx`  
          – tela de login para admin.
        – `AdminDashboardPage.tsx`  
          – overview de fontes, casos e health.
        – `SourcesPage.tsx`  
          – listagem/detalhes de fontes.
        – `CasesPage.tsx`  
          – listagem de casos (ponto de entrada para timeline/raio-X).
      – `components/`
        – `SourcesTable.tsx`, `CasesTable.tsx`, `HealthSummary.tsx`.
      – `hooks/`
        – `useSources.ts`, `useCases.ts`, `useHealthSummary.ts`.

    – `cases/` (S19)
      – `pages/`
        – `CaseTimelinePage.tsx`  
          – timeline de eventos/blocos de um caso.
        – `CaseXrayPage.tsx`  
          – visão de raio-X de um caso/bloco.
      – `components/`
        – `TimelineEventsList.tsx`, `BlockDetailsCard.tsx`, `EvidenceList.tsx`.
      – `hooks/`
        – `useCaseTimeline.ts`, `useCaseXray.ts`.

2.3 Diretório de testes do frontend

– `frontend/tests/`
  – `e2e/`
    – cenários cobrindo os fluxos de S20 (consulta, admin, timeline/raio-X, login/logout, estados de verdade/incerteza).
  – `unit/`
    – testes unitários dos componentes/core críticos (auth, logging, hooks principais).
  – `utils/`
    – wrappers de Providers e helpers de teste.

3. Arquitetura de Auth

3.1 Fluxo de autenticação

– Tela de login (`modules/admin/pages/LoginPage.tsx`):
  – usa `auth-service.ts` para enviar credenciais ao backend;
  – recebe token/identidade (payload mínimo, alinhado com backend);
  – armazena token de forma controlada (ex.: `sessionStorage` ou `localStorage` com chave clara, ex. `inspectah_auth_token`).

– `AuthProvider` expõe:
  – `user` (dados mínimos do usuário autenticado);
  – `token`;
  – `isAuthenticated` (boolean);
  – métodos `login(credentials)` e `logout()`;
  – estados de carregando/erro de sessão se relevantes.

3.2 Rotas protegidas

– `auth-guard.tsx` ou componente equivalente deve:
  – envolver todas as rotas privadas (admin, timeline, raio-X);
  – verificar `isAuthenticated` antes de renderizar;
  – redirecionar para login (com mensagem adequada) em caso de sessão ausente/inválida.

3.3 Integração com API

– `http-client.ts` injeta token em headers de requests autenticadas (ex.: `Authorization: Bearer <token>`);
– interceptors tratam respostas 401/403:
  – limpam sessão se necessário;
  – disparam fluxo de logout ou forçam re-login.

3.4 Persistência e limpeza

– `logout` remove token e dados de usuário do storage/contexto;
– qualquer estado de sessão inválida deve resultar em experiência previsível:
  – UI volta para área pública;
  – mensagem de sessão expirada/necessidade de novo login.

4. Arquitetura de Observabilidade de UI

4.1 Logger central

– `core/logging/logger.ts` expõe funções principais:
  – `logEvent(name, payload?)`;
  – `logError(error, context?)`;
  – `logNavigation(from, to, context?)`.

– `logging-types.ts` define tipos para:
  – eventos de consulta (query enviada, sucesso, erro);
  – eventos de admin (página aberta, caso selecionado, etc.);
  – erros de carregamento de timeline/raio-X.

4.2 Integração com Providers, hooks e componentes

– `LoggerProvider` injeta logger via contexto para toda a árvore.
– Hooks como `useConsultQuery`, `useCases`, `useCaseTimeline`, etc., chamam `logEvent`/`logError` em pontos-chave.
– O ErrorBoundary global chama `logError` com contexto (rota atual, userId, traceId se existir).

4.3 Destino dos logs

– Em dev:
  – logs podem ir para console e, opcionalmente, para um endpoint de debug;
– Em uso interno/pilotos:
  – eventos críticos podem ser enviados a um endpoint de backend (ex.: `/metrics/ui-events`), se disponível.

A S20 garante a existência das funções/hooks; a infraestrutura de coleta/armazenamento mais robusta pode vir em sprints futuras de observabilidade/infra.

5. Representação de estados de verdade/incerteza na UI

5.1 Tipos centrais

– `shared/lib/truth-states.ts` define tipos/enums para estados, ex.:
  – `"ACCEPTED"`, `"DISPUTED"`, `"UNDER_REVIEW"`, `"INSUFFICIENT_EVIDENCE"`.

– Esses valores devem refletir a semântica do backend, sem inventar estados novos no front.

5.2 Hooks e componentes

– `useTruthStateLabel.ts`:
  – recebe estado bruto e devolve label, cor e ícone sugerido;
– `StatusPill.tsx`:
  – recebe estado de verdade e renderiza badge consistente.

Uso esperado:
– Em consulta: ao lado da resposta consolidada.
– Em Admin: na lista de casos e detalhes de cada caso.
– Em Timeline/Raio-X: em cada bloco/evento relevante.

Isso sustenta a métrica M7 e os checks do gate S20-G6 sobre exposição correta de estados de verdade/incerteza.

6. Integração com os Gates da S20

6.1 Scripts de gates

Na raiz do repositório (ou em `bin/`), os scripts de gates da S20 seguem padrão das sprints anteriores:

– `bin/s20_g0_scope_and_baseline.sh`
– `bin/s20_g1_frontend_build_and_sanity.sh`
– `bin/s20_g2_ux_and_navigation.sh`
– `bin/s20_g3_responsiveness_and_basic_accessibility.sh`
– `bin/s20_g4_auth_and_protected_routes.sh`
– `bin/s20_g5_frontend_observability.sh`
– `bin/s20_g6_demo_internal_use_and_truth_states.sh`
– `bin/s20_g7_go_no_go.sh`

Wrapper:

– `bin/s20_all_gates.sh`  
  – executa G0…G7 em ordem, interrompendo na primeira falha.

6.2 Scorecards e evidências

– `out/scorecards/`
  – `S20_G0_scope_and_baseline.json`
  – `S20_G1_frontend_build_and_sanity.json`
  – `S20_G2_ux_and_navigation.json`
  – `S20_G3_responsiveness_and_basic_accessibility.json`
  – `S20_G4_auth_and_protected_routes.json`
  – `S20_G5_frontend_observability.json`
  – `S20_G6_demo_internal_use_and_truth_states.json`
  – `S20_G7_go_no_go.json`

– `out/evidence/`
  – `S20_G0_scope_and_baseline/`
  – `S20_G1_frontend_build_and_sanity/`
  – `S20_G2_ux_and_navigation/`
  – `S20_G3_responsiveness_and_basic_accessibility/`
  – `S20_G4_auth_and_protected_routes/`
  – `S20_G5_frontend_observability/`
  – `S20_G6_demo_internal_use_and_truth_states/`
  – `S20_G7_go_no_go/`

Cada diretório contém logs, capturas, gravações, dumps de logs de UI e manifests conforme Capítulo 2.

7. Documentação ligada à Sprint 20

– `docs/sprint_20_capitulo_1_contexto_objetivos.md`  
  – Capítulo 1 (contexto, objetivos, escopo).
– `docs/sprint_20_capitulo_2_gates_validacao.md`  
  – Capítulo 2 (gates, métricas, evidências).
– `docs/sprint_20_capitulo_3_arquitetura_filemap.md`  
  – Este capítulo (arquitetura, filemap, integrações).
– `docs/sprint_20_plan_codex.md`  
  – Plano de execução para Codex/engenharia, derivado de C3+C4.
– `docs/sprint_20_orr_summary.md`  
  – Wrap final com resultado dos gates e decisão GO/NO_GO.

8. Critérios de correção arquitetural

Do ponto de vista da S20, esta arquitetura é considerada correta quando:

– O frontend está fisicamente organizado em camadas e módulos conforme descrito (mesmo com pequenas diferenças nominais).
– Lógica de Auth e Observabilidade está concentrada em `core/` + `app/providers/`, não espalhada de forma oportunista em componentes.
– Telas de S17–S19 vivem em `modules/consult`, `modules/admin` e `modules/cases`, sem páginas soltas fora dessa estrutura.
– Estados de verdade/incerteza são tratados via tipos centrais (`truth-states`) e componentes dedicados (`StatusPill`), não com strings soltas em cada tela.
– Scripts de gates S20 estão presentes, apontam para comandos corretos e geram scorecards/evidências com nomes/diretórios padronizados.
– Extensões futuras (novos domínios, dashboards, integrações de logging) conseguem se encaixar nesta arquitetura sem exigir rearranjo global.

Com isso, o Capítulo 3 v2 entrega para o squad e para o Codex um mapa concreto e estável do frontend pós-S20, alinhado com os objetivos de UX/Auth/Observabilidade e pronto para sustentar a evolução do Inspectah nas próximas sprints.

