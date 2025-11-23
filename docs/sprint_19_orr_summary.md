# Sprint 19 – ORR (Timeline e Raio-X)

## Objetivo
Entregar diagnóstico profundo dos casos do Inspectah sobre o Console de Admin: timeline navegável e raio-X completo por caso, reaproveitando dados consolidados da Truth-DB/Sistema de Blocos sem quebrar contratos da S17/S18.

## Gates S19_G0…S19_G8
- Execução local recomendada:
  - `PYTHONPATH=. bash bin/s19_all.sh`
  - `PYTHONPATH=. bash bin/s19_g8_go_no_go.sh`
- Scorecards gerados em `out/scorecards/` e evidências em `out/evidence/S19_*`.
- Última execução local: todos os gates S19_G0…S19_G8 em `PASS`, decisão final `GO` (ver scorecards em `out/scorecards`).

## Métricas M1…M6 (consolidadas em S19_G6)
- Último snapshot (scorecard S19_G6): M1=0.003s, M2=0.003s, M3=1.0, M4=1.0, M5=1.0, M6=2.0.
- Thresholds: M1/M2 ≤ 0.8s, M3 ≥ 0.95, M4 = 1.0, M5 = 1.0, M6 ≤ 2.0.

## Principais entregas
- **Backend (app/admin)**: novos schemas de timeline/raio-X, serviços `list_case_timeline` e `get_case_xray`, rotas `/admin/cases/{id}/timeline` e `/admin/cases/{id}/xray`, testes em `tests/admin/test_admin_timeline_xray_endpoints.py`.
- **Frontend (frontend/inspectah-ui)**: tipos TS de timeline/raio-X, clients `getAdminCaseTimeline`/`getAdminCaseXRay`, páginas dedicadas, componentes de timeline e raio-X, rotas registradas no router e links a partir da lista/detalhe de casos, testes em `src/__tests__/admin/AdminTimelineXRay.test.tsx`.
- **Fixtures**: `Sprint 19/fixtures/` com timelines e raios-X canônicos usados por backend, MSW e gates S19_G4/S19_G5.
- **Gates e CI**: scripts `bin/s19_g*.sh`, orquestrador `bin/s19_all.sh`, workflow CI `_s19_timeline_xray.yml` rodando qualidade de front e checagens de timeline/raio-X.

## Riscos e débitos
- Warnings de Pydantic V2 permanecem em aberto (fora de escopo da S19).
- Caminho até evidência (M6) calculado de forma heurística; aprofundar em sprints futuras se necessário.

## Conclusão
Com todos os scorecards da S19 em `PASS` e decisão `GO`, a timeline e o raio-X passam a compor a camada de diagnóstico do Inspectah, permitindo reconstruir rapidamente a história de cada caso sem regressões nas entregas da S17/S18.
