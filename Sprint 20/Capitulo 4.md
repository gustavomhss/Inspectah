Inspectah — Sprint 20
Capítulo 4 — Plano de Execução, Runbook e Ordem de Ataque (Frontend — UX, Auth básica e Observabilidade) — Versão 2

0. One-liner do Capítulo 4
Este capítulo traduz os Capítulos 1–3 em um plano executável e auditável: quais passos o squad deve seguir, em que ordem, quais arquivos tocar, quais comandos rodar e como amarrar tudo nos gates S20-G0…S20-G7, até chegar a uma decisão clara de GO/NO_GO para a Sprint 20, sem quebrar o backend, o Truth-DB ou a disciplina de evidências do Inspectah.

0.1 Mapa rápido da S20 (fases → gates → métricas)

– Fase 0: Preparação, branch e baseline → G0, visibilidade de M1.
– Fase 1: Filemap e casca do app → prepara terreno para G1, G2.
– Fase 2: Auth mínima → G4, impacto em G2, G6.
– Fase 3: Logging & Observabilidade de UI → G5, impacto em G2, G6.
– Fase 4: UX unificada + estados de verdade/navegação → G2, M2, M7.
– Fase 5: Responsividade & acessibilidade básica → G3, M3.
– Fase 6: Demo, uso interno + estados de verdade → G6, M6, M7.
– Fase 7: Build final e GO/NO_GO → G1, G7, consolidação de M1–M7.

1. Estratégia geral de execução da S20

A Sprint 20 é uma sprint de acabamento, unificação e endurecimento do frontend, não de criação de funcionalidades gigantes novas. A estratégia aprovada pela equipe é:

1) Estabilizar a base e a arquitetura antes de mexer em UX:
   – garantir que o frontend compila, testa e está minimamente organizado conforme o Capítulo 3;
   – não iniciar refatorações profundas sem um filemap estável.

2) Ativar pilares transversais (Auth e Observabilidade) logo no início:
   – colocar de pé login/logout e proteção de rotas;
   – estabelecer logger central e eventos mínimos;
   – sem se preocupar ainda em “embelezar” a UI.

3) Só então polir UX, responsividade e demo end-to-end:
   – aplicar design system mínimo e unificar vocabulário;
   – garantir responsividade aceitável e acessibilidade básica;
   – montar e ensaiar um roteiro de demo confiável;
   – rodar todos os gates até G7.

Princípios operacionais para o squad:
– Commits pequenos e temáticos por fase (por exemplo, um PR para filemap, outro para Auth, outro para observabilidade, etc.).
– Nunca misturar mudanças estruturais (ex.: mexer em `core/api`) com ajustes cosméticos de CSS no mesmo PR.
– Sempre reexecutar pelo menos build/tests de front antes de rodar gates relacionados.

2. Fase 0 — Preparação, branch e baseline (G0)

Objetivo: estabelecer um ponto de partida claro, rastreável e minimamente saudável para a S20.

Passos:

2.1 Criar ou confirmar branch da Sprint 20
– Na raiz do repositório do Inspectah, sincronizar com a branch base (tipicamente `main`).
– Criar branch específica da sprint, por exemplo: `s20_frontend_ux_auth_obs`.
– Registrar o SHA da base em um lugar fácil (será usado no G0).

2.2 Materializar Capítulos 1–3 em `docs/`
– Copiar os conteúdos aprovados dos canvases para:
  – `docs/sprint_20_capitulo_1_contexto_objetivos.md`;
  – `docs/sprint_20_capitulo_2_gates_validacao.md`;
  – `docs/sprint_20_capitulo_3_arquitetura_filemap.md`;
– Garantir que esses arquivos não contêm TODOs ou placeholders vagos.

2.3 Verificar build atual do frontend
– Entrar em `frontend/`;
– Rodar `npm install` (ou o gerenciador padrão do repo);
– Rodar `npm run build` e `npm run test` (ou comandos equivalentes definidos no `package.json`).
– Se falhar, abrir issues técnicas e corrigir o mínimo possível para estabilizar, sem mudar escopo.

2.4 Implementar e rodar S20-G0
– Criar `bin/s20_g0_scope_and_baseline.sh` que:
  – registra commit base (via `git rev-parse HEAD`);
  – executa build/test rápido do frontend;
  – gera `out/scorecards/S20_G0_scope_and_baseline.json` com campos: commit_base, M1 inicial, pendências não bloqueadoras, PASS/FAIL;
  – cria `out/evidence/S20_G0_scope_and_baseline/` com logs relevantes.
– Rodar o script na branch da sprint.

Saída esperada da Fase 0:
– Branch da sprint criada e documentada;
– Capítulos 1–3 presentes e alinhados;
– Build de base passando (ou problemas pontuais documentados);
– G0 = PASS.

3. Fase 1 — Organização de filemap e casca do app

Objetivo: alinhar o esqueleto do frontend à arquitetura do Capítulo 3, minimizando risco de retrabalho e preparando o terreno para Auth, Observabilidade e UX.

Passos:

3.1 Criar/ajustar estrutura de pastas
– Dentro de `frontend/src/`, garantir a existência de:
  – `app/`, `core/`, `shared/`, `modules/`;
  – subpastas de `core/` (auth, api, config, logging);
  – subpastas de `shared/` (components, layout, hooks, lib);
  – subpastas de `modules/` (consult, admin, cases).

3.2 Consolidar App shell
– Garantir que `main.tsx` monta `<App />` único;
– Em `App.tsx`:
  – configurar router (React Router ou equivalente);
  – envolver a árvore com `AuthProvider` e `LoggerProvider` (mesmo que ainda tenham implementação parcial);
  – registrar `ErrorBoundary` raiz;
  – usar `MainLayout` para rotas privadas e `PublicLayout` para rotas públicas.

3.3 Centralizar definição de rotas
– Implementar `app/routes.tsx` com estrutura clara:
  – rotas públicas: `/`, `/consult`;
  – rotas privadas: `/admin`, `/admin/sources`, `/admin/cases`, `/admin/cases/:id/timeline`, `/admin/cases/:id/xray`;
– Usar `AuthGuard` (stub inicial) em todas as rotas privadas.

3.4 Migrar páginas existentes para módulos
– Pegar as telas legadas das S17–S19 e movê-las ou referenciá-las dentro de:
  – `modules/consult/pages/ConsultPage.tsx`;
  – `modules/admin/pages/LoginPage.tsx`, `AdminDashboardPage.tsx`, `SourcesPage.tsx`, `CasesPage.tsx`;
  – `modules/cases/pages/CaseTimelinePage.tsx`, `CaseXrayPage.tsx`;
– Ajustar imports para utilizar componentes de `shared/components` quando fizer sentido, sem mexer em comportamento ainda.

Observação: nesta fase o foco é organização, não polimento. Bugs de layout que já existiam podem permanecer, desde que não piorem.

4. Fase 2 — Implementação de Auth mínima (G4)

Objetivo: colocar de pé a autenticação básica e a proteção de rotas sensíveis, conforme Capítulos 1–3, sem transformar a sprint em um projeto de identidade complexo.

Passos:

4.1 Implementar serviço de auth em `core/auth`
– Em `core/auth/auth-types.ts`:
  – definir `AuthSession` (token + claims mínimas, ex.: `userId`, `email` ou similar).
– Em `core/auth/auth-service.ts`:
  – funções `login(credentials)`, `logout()`, `loadSession()`, `saveSession()`, `clearSession()`;
  – integração com endpoint de login do backend (ex.: `POST /auth/login`), respeitando contratos existentes;
  – armazenamento do token em `sessionStorage` ou `localStorage` com prefixo claro (`inspectah_auth_*`).

4.2 Implementar AuthProvider
– Em `app/providers/AuthProvider.tsx`:
  – contexto com `user`, `token`, `isAuthenticated`, `login`, `logout`;
  – leitura inicial de sessão via `loadSession()`;
  – tratamento de estados de carregando/erro em login.

4.3 Implementar rota de login
– Em `modules/admin/pages/LoginPage.tsx`:
  – formulário com campos mínimos (usuário/senha ou equivalente);
  – chamada a `login` do contexto em submit;
  – mensagens claras de erro em falha de autenticação;
  – redirecionamento para `/admin` em caso de sucesso.

4.4 Proteger rotas privadas com AuthGuard
– Em `core/auth/auth-guard.tsx`:
  – criar componente que lê `isAuthenticated`;
  – se `false`, redireciona para `/login` e opcionalmente guarda rota alvo;
  – se `true`, renderiza children.
– Em `app/routes.tsx`, envolver rotas privadas com `AuthGuard`.

4.5 Integrar token com API
– Em `core/api/http-client.ts`:
  – adicionar interceptor para incluir header `Authorization: Bearer <token>` quando houver sessão;
  – tratar respostas 401/403, acionando `logout()` ou fluxo de sessão expirada conforme política definida.

4.6 Testes manuais de auth
– Verificar pelo menos os cenários:
  – acessar `/admin` sem login → redireciona para `/login`;
  – login válido → usuário é levado ao Admin e consegue navegar;
  – logout → retorna à área pública, rotas privadas bloqueadas de novo;
  – token inválido/expirado → sessão é limpa e usuário é convidado a logar novamente.

4.7 Rodar S20-G4
– Implementar `bin/s20_g4_auth_and_protected_routes.sh` que:
  – executa cenários de teste (automatizados ou semi-manuais);
  – alimenta M4 (proporção de tentativas bloqueadas corretamente);
  – gera `S20_G4_auth_and_protected_routes.json` e `out/evidence/S20_G4_auth_and_protected_routes/`.

Saída esperada da Fase 2:
– Auth mínima funcional;
– Rotas sensíveis consistentemente protegidas;
– G4 = PASS.

5. Fase 3 — Logging & Observabilidade de UI (G5)

Objetivo: estabelecer camada central de observabilidade de UI, integrada aos fluxos principais, de forma a sustentar troubleshooting e métricas básicas.

Passos:

5.1 Implementar logger central
– Em `core/logging/logging-types.ts`:
  – definir tipos para eventos de consulta, admin, cases e erros.
– Em `core/logging/logger.ts`:
  – implementar `logEvent(name, payload?)`, `logError(error, context?)`, `logNavigation(from, to, context?)`;
  – incluir campos padrão (timestamp, rota atual, userId, traceId opcional).

5.2 Implementar LoggerProvider
– Em `app/providers/LoggerProvider.tsx`:
  – criar contexto que expõe funções de logging;
  – conectar com `logger.ts`;
  – envolver a aplicação em `App.tsx`.

5.3 Instrumentar fluxos críticos
– Em `modules/consult/hooks/useConsultQuery.ts`:
  – `logEvent('consult.query_submitted', ...)` ao enviar pergunta;
  – `logEvent('consult.query_success', ...)` ao receber resposta;
  – `logError` em falhas.

– Em `modules/admin/pages/AdminDashboardPage.tsx`, `SourcesPage.tsx`, `CasesPage.tsx`:
  – `logEvent('admin.page_open', { page: 'dashboard' | 'sources' | 'cases' })`.

– Em `modules/cases/hooks/useCaseTimeline.ts` e `useCaseXray.ts`:
  – `logEvent('cases.timeline_load', ...)` e `logError` em caso de erro.

5.4 Integrar ErrorBoundary
– Em `app/layout/ErrorBoundary.tsx`:
  – chamar `logError` com error + info/contexto;
  – renderizar `shared/components/ErrorMessage` ao usuário.

5.5 Destino de logs
– Em `logging-config.ts`:
  – configurar comportamento em dev (console, logs verbosos);
  – preparar função opcional para envio de eventos a endpoint de backend (sem forçar dependências externas ainda).

5.6 Rodar S20-G5
– Implementar `bin/s20_g5_frontend_observability.sh`:
  – executar cenários que disparem eventos/erros planejados;
  – verificar que logs existem e são coerentes;
  – calcular M5 (eventos instrumentados / eventos planejados);
  – gerar scorecard e evidências.

Saída esperada da Fase 3:
– Logging/observabilidade operacionais;
– Eventos/erros críticos instrumentados;
– G5 = PASS.

6. Fase 4 — UX unificada, estados de verdade e navegação (G2, parte de G6)

Objetivo: tornar a experiência coerente com o vocabulário do Inspectah e expor corretamente estados de verdade/incerteza ao longo dos fluxos principais.

Passos:

6.1 Consolidar componentes compartilhados
– Em `shared/components/` garantir:
  – componentes básicos coesos (Button, Input, Table, Card, Badge, Modal, Toast);
  – `StatusPill` implementado com base em `truth-states` e `useTruthStateLabel`;
  – `ErrorMessage` para casos de erro.

6.2 Ajustar telas de consulta (S17)
– Em `ConsultPage.tsx` e componentes:
  – utilizar `PageContainer` e `PageHeader` padronizados;
  – exibir `StatusPill` baseado no estado retornado pelo backend;
  – mensagens claras para estados: aceito, em disputa, em análise, sem evidência suficiente;
  – garantir caminhos visíveis para nova consulta e, se aplicável, links para detalhes (sem prometer o que o backend não tem).

6.3 Ajustar telas de admin (S18)
– Em `AdminDashboardPage.tsx`, `SourcesPage.tsx`, `CasesPage.tsx`:
  – alinhar títulos, labels e ações ao vocabulário de casos, fontes, evidências;
  – usar `StatusPill` na lista de casos;
  – garantir navegação óbvia para timeline/raio-X a partir de um caso.

6.4 Ajustar telas de timeline/raio-X (S19)
– Em `CaseTimelinePage.tsx` e `CaseXrayPage.tsx`:
  – usar `PageHeader` e `PageContainer`;
  – exibir estados de verdade nos blocos/eventos de forma consistente;
  – garantir caminho de volta para lista de casos/admin sem dead-ends.

6.5 Ensaiar navegação ponta a ponta
– Executar manualmente os cenários de navegação descritos no Capítulo 2 (M2);
– Anotar qualquer ponto de confusão, dead-end ou label inconsistente;
– Corrigir antes de rodar o gate.

6.6 Rodar S20-G2
– Implementar `bin/s20_g2_ux_and_navigation.sh`:
  – guiar execução dos cenários de navegação;
  – calcular M2 (cenários ok / cenários totais);
  – gerar scorecard e evidências.

Saída esperada da Fase 4:
– UX coerente nas principais telas;
– estados de verdade/incerteza visíveis e consistentes;
– G2 = PASS (M2 ≥ 0,9).

7. Fase 5 — Responsividade & acessibilidade básica (G3)

Objetivo: garantir uso aceitável em desktops, tablets e mobile, com acessibilidade básica.

Passos:

7.1 Ajustar layout responsivo
– Usar utilitários (ex.: Tailwind) e helpers de `responsive.ts` para:
  – evitar overflow horizontal desnecessário;
  – transformar tabelas muito largas em layouts alternativos (cards, rolagem controlada);
  – garantir que botões principais sejam clicáveis em telas menores.

7.2 Acessibilidade mínima
– Revisar componentes críticos para:
  – foco visível na navegação por teclado;
  – `aria-label` em ícones sem texto;
  – contraste aceitável em textos principais.

7.3 Rodar S20-G3
– Implementar `bin/s20_g3_responsiveness_and_basic_accessibility.sh`:
  – testar combinações de tela×viewport definidas no Capítulo 2;
  – calcular M3 a partir dos scores discretos (1, 0,5, 0);
  – gerar scorecard e evidências.

Saída esperada da Fase 5:
– Telas-chave usáveis em resoluções-alvo;
– Acessibilidade básica atendida;
– G3 = PASS (M3 ≥ 0,85 e nenhuma quebra crítica).

8. Fase 6 — Demo, uso interno e validação de estados de verdade (G6)

Objetivo: validar que o produto resultante da S20 é usável e demonstrável, e que a UI respeita os estados de verdade/incerteza vindos do motor.

Passos:

8.1 Definir roteiro de demo oficial
– Criar `docs/sprint_20_demo_script.md` com:
  – cenário de consulta sobre caso real/sintético;
  – login em admin, navegação para fontes/casos;
  – abertura de caso, visualização de timeline e raio-X, retorno seguro;
  – casos onde o backend retorna estados diferentes de verdade/incerteza (aceito, em disputa, em análise, sem evidência suficiente).

8.2 Preparar dados de teste no backend
– Garantir em ambiente dev:
  – existência de casos com estados variados;
  – fontes cadastradas que tornem a história crível na UI.

8.3 Rodar demo interna
– Com squad + PO (e, se possível, 1 pessoa convidada interna):
  – executar o roteiro completo;
  – anotar pontos de confusão, problemas, fricções.

8.4 Coletar scores M6 e M7
– Cada participante dá score 0–1 para fluidez geral (M6);
– Squad registra resultado dos cenários de estados de verdade (M7), observando se a UI não promove incerteza a fato.

8.5 Rodar S20-G6
– Implementar `bin/s20_g6_demo_internal_use_and_truth_states.sh`:
  – consolidar M6 e M7;
  – gerar `S20_G6_demo_internal_use_and_truth_states.json` e evidências (gravações, screenshots, notas);
  – marcar PASS/FAIL conforme metas.

Saída esperada da Fase 6:
– Demo oficial registrada e reprodutível;
– M6 e M7 medidos e dentro das metas;
– G6 = PASS.

9. Fase 7 — Build final, GO/NO_GO e wrap (G1, G7)

Objetivo: consolidar o estado da S20, rodar todos os gates e registrar decisão única de GO/NO_GO com trilha de evidências.

Passos:

9.1 Build final e testes
– Na branch da S20:
  – rodar `npm run build` e `npm run test` (incluindo e2e relevante);
  – confirmar M1 = 1.

9.2 Implementar S20-G1 (se ainda não existir)
– `bin/s20_g1_frontend_build_and_sanity.sh` deve:
  – rodar build/test do frontend;
  – gerar `S20_G1_frontend_build_and_sanity.json` com M1 e decisão;
  – salvar logs em `out/evidence/S20_G1_frontend_build_and_sanity/`.

9.3 Rodar todos os gates em sequência
– Executar `bin/s20_all_gates.sh` (ou rodar gates individualmente em ordem G0→G7):
  – se qualquer gate falhar, interromper execução e corrigir antes de tentar novamente.

9.4 Implementar S20-G7
– `bin/s20_g7_go_no_go.sh` deve:
  – ler todos os scorecards S20-G0…S20-G6;
  – decidir GO/NO_GO (fail se qualquer gate for FAIL);
  – gerar `S20_G7_go_no_go.json` com estado de cada gate, M1–M7 e decisão final;
  – gerar `out/evidence/S20_G7_go_no_go/summary.json` + `MANIFEST.json` referenciando todos os scorecards/evidências.

9.5 Wrap humano da sprint
– Em `docs/sprint_20_orr_summary.md`, registrar:
  – objetivo da S20;
  – tabela de gates S20-G0…S20-G7 com status;
  – resumo das métricas M1–M7;
  – principais entregas do frontend (arquitetura, Auth, Observabilidade, UX, demo);
  – riscos/remanescentes e recomendações para sprints futuras;
  – decisão final GO/NO_GO.

Saída esperada da Fase 7:
– Scorecards S20-G0…S20-G7 presentes e consistentes;
– `docs/sprint_20_orr_summary.md` completo;
– decisão final da Sprint 20 registrada.

10. Checklist mínimo antes de pedir GO ao Conselho

Antes de levar a Sprint 20 para GO no Conselho, o squad deve confirmar que:

– Consulta (S17):
  – UI permite pergunta e mostra resposta com status de verdade claro;
  – há logging de eventos de consulta;
  – layout funciona em desktop e é aceitável em tablet/mobile.

– Admin (S18):
  – `/admin` e telas derivadas exigem login;
  – fontes, casos e health são acessíveis e navegáveis;
  – é possível partir de um caso para timeline/raio-X e voltar.

– Timeline/Raio-X (S19):
  – carregam dados de casos de teste sem erros;
  – exibem blocos/eventos com `StatusPill` consistente;
  – registram eventos de carregamento e erros no logger.

– Auth:
  – todas as rotas sensíveis estão protegidas;
  – sessão expirada/invalidada produz experiência previsível.

– Observabilidade:
  – eventos e erros críticos são registrados e correlacionáveis com backend.

– Gates e evidências:
  – S20-G0…S20-G6 = PASS;
  – S20-G7 = GO;
  – scorecards e evidências existem nos diretórios esperados.

11. Resumo operacional para o Codex e para o squad

Para o Codex (engenharia):
– Usar Capítulo 3 como mapa de arquivos e Capítulo 4 v2 como script de execução.
– Implementar fases na ordem sugerida, sempre mantendo build/test verdes entre uma fase e outra.
– Nunca alterar contratos de backend ou semântica de estados de verdade sem alinhamento explícito com as sprints de backend/Truth-DB.

Para o squad humano:
– Acompanhar o progresso por fase, cobrando evidências (scorecards + diretórios `out/evidence/`).
– Usar o roteiro de demo da Fase 6 como teste recorrente de sanidade.
– Só chamar o Conselho quando todos os gates estiverem verdes e a demo estiver estável.

Com isso, o Capítulo 4 v2 entrega um runbook detalhado, compatível com a disciplina do Inspectah (gates, scorecards, evidências, ORR) e alinhado com os objetivos da Sprint 20 de tornar o frontend um produto coeso, protegido e observável, pronto para a Fase 2.

