# Sprint 20 — ORR Summary (Frontend — UX, Auth básica, Observabilidade)

## Objetivo da Sprint
Transformar as UIs de consulta, admin e diagnóstico em um produto único, com auth básica protegendo rotas sensíveis, observabilidade mínima de frontend, UX unificada, estados de verdade/incerteza explícitos, responsividade básica e disciplina de gates/scorecards.

## Gates S20 (estado atual)
- G0 Escopo & baseline: PASS (`out/scorecards/S20_G0_scope_and_baseline.json`)
- G1 Build & sanidade de frontend: PASS (`out/scorecards/S20_G1_frontend_build_and_sanity.json`)
- G2 UX & navegação coerente: PASS (`out/scorecards/S20_G2_ux_and_navigation.json`)
- G3 Responsividade & acessibilidade básica: PASS (`out/scorecards/S20_G3_responsiveness_and_basic_accessibility.json`)
- G4 Auth & rotas protegidas: PASS (`out/scorecards/S20_G4_auth_and_protected_routes.json`)
- G5 Observabilidade de UI: PASS (`out/scorecards/S20_G5_frontend_observability.json`)
- G6 Demo, uso interno & truth-states: FAIL (aguardando `out/evidence/S20_G6_demo_internal_use_and_truth_states/demo_scores.json` com M6/M7)
- G7 GO/NO_GO: NO_GO (`out/scorecards/S20_G7_go_no_go.json`) — bloqueado por G6.

## Métricas M1–M7 (última leitura)
- M1 Build/test: 1 (G1)
- M2 Navegação coerente: 1.0 (G2)
- M3 Responsividade/acessibilidade: 1.0 (G3)
- M4 Proteção de rotas sensíveis: 1.0 (G4)
- M5 Observabilidade de UI: 1.0 (G5)
- M6 Fluidez de demo: 0.0 (não medido — falta demo_scores.json)
- M7 Exposição correta de estados de verdade/incerteza: 0.0 (não medido — falta demo_scores.json)

## Entregas principais do frontend na S20
- Arquitetura organizada em `app/core/shared/modules` com App shell, providers e rotas centralizadas.
- Auth básica real (login/logout/sessão persistente), AuthGuard protegendo admin/timeline/xray, MainLayout com usuário/log out.
- Observabilidade de UI central (logger, LoggerProvider, ErrorBoundary) com eventos em consulta, admin e casos/timeline/xray.
- UX unificada com PageHeader/PageContainer, navegação clara entre consulta → admin → casos → timeline/raio-X.
- Camada de truth-states e `StatusPill` exibindo estados de verdade/incerteza em consulta, lista/detalhe de casos e timeline/raio-X, sem promover incerteza a fato.
- Responsividade/acessibilidade básica aplicada às telas principais.
- Scripts de gates S20 (G0–G7) e roteiro de demo em `docs/sprint_20_demo_script.md`.

## Riscos e pendências
- G6 depende da execução da demo real contra o backend e preenchimento de `out/evidence/S20_G6_demo_internal_use_and_truth_states/demo_scores.json` com M6/M7 (metas: M6 ≥ 0.8, M7 ≥ 0.9). Até lá, G7 permanece NO_GO.
- Após registrar os scores reais, reexecutar `bin/s20_g6_demo_internal_use_and_truth_states.sh`, `bin/s20_g7_go_no_go.sh` e `bin/s20_all_gates.sh`.

## Próximos passos
- Rodar demo interna seguindo `docs/sprint_20_demo_script.md`, capturar evidências e preencher demo_scores.json.
- Reexecutar G6 e G7; se todos os gates ficarem PASS, decisão final deverá ser GO.
