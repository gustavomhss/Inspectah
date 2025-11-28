# Inspectah — Sprint 9 Summary

## Objetivo geral
A Sprint 9 implantou o “Inspectah Evidence OS” completo para os cenários C1–C3: o core consolidou o triplo QueryLog→EvidenceBundle→UserResponse com InfoTypes oficiais, o Admin ganhou orquestração multi-fonte com visibilidade de status/erros, o User v1 entrega respostas estruturadas e explicáveis com ponteiros de evidência, e o GPT Engine especializado opera em modo bundle-only com métricas/observabilidade prontas para auditorias e gates T4–T6.

## Status dos gates

| Gate | Status | Evidência |
|------|--------|-----------|
| S9_T0_scope | PASS | `out/scorecards/S9_T0_scope.json` |
| S9_T1_static_quality | PASS | `out/scorecards/S9_T1_static_quality.json` |
| S9_T2_unit_and_contracts | PASS | `out/scorecards/S9_T2_unit_and_contracts.json` |
| S9_T3_property_and_edge_cases | PASS | `out/scorecards/S9_T3_property_and_edge_cases.json` |
| S9_T4_golden_flows | PASS | `out/scorecards/S9_T4_golden_flows.json` |
| S9_T5_perf_and_limits | PASS | `out/scorecards/S9_T5_perf_and_limits.json` |
| S9_T6_logs_and_evidence | PASS | `out/scorecards/S9_T6_logs_and_evidence.json` |
| S9_T7_ci_pipeline | PASS | `out/scorecards/S9_T7_ci_pipeline.json` |
| S9_T8_go_no_go | PASS (decision: GO) | `out/scorecards/S9_T8_go_no_go.json` |

## Entregáveis principais

- **Core S9** — Contratos em `app/core/*` reforçam InfoTypes oficiais, `app/core/pipeline.py` cria o triplo QueryLog↔EvidenceBundle↔UserResponse e persiste em `out/evidence/s9_logs|s9_bundles|s9_responses`.
- **Admin v1** — Serviços/rotas em `app/admin/service.py` e `app/admin/routes.py` administram fontes multi-fonte, status/erros e helpers `prepare_scenario_sources` respaldados por fixtures realistas em `tests/fixtures/s9_*`.
- **User v1** — Schemas e view-models em `app/user/*` expõem resposta textual, resumo estruturado, confiança e links de evidência com métricas instrumentadas.
- **GPT Engine especializado** — `app/gpt_client/prompts.py` e `app/gpt_client/client.py` geram decisões determinísticas bundle-only, usados unicamente pelo pipeline (Inv3).
- **Observabilidade e métricas S9** — `app/observability/metrics_s9.py` + hooks em Admin/User/Core alimentam `get_metrics_snapshot`, permitindo medir p50/p95, erros e admin actions.
- **Fixtures e goldens oficiais** — `tests/fixtures/s9_*` alinham C1–C3 com casos reais e `tests/goldens/s9_*.json` são verificados via `tests/s9_t4_golden_flows`.
- **Gates automatizados T1–T6** — Scripts `bin/s9_t{1..6}_*.sh` produzem scorecards e summaries em `out/scorecards/` e `out/evidence/`, preparando o terreno para CI/T7.
- **CI & decisão** — `bin/s9_ci.sh`, `bin/s9_t7_ci_pipeline.sh`, `bin/s9_t8_go_no_go.sh` e `.github/workflows/s9-ci.yml` levam os gates para CI e consolidam o GO/NO_GO com `docs/sprint_9_summary.md`.

## Demo & checklist final

- Runbook e script: `docs/sprint_9_cenarios_demo.md` detalha o passo a passo dos cenários e `bin/s9_demo.sh` automatiza o mesmo fluxo (Admin → User → evidências → métricas) com `NET=0`.

| Cenário | Demo rodada? | Evidências principais | Observações |
|---------|--------------|----------------------|-------------|
| C1 — Preço médio (SP) | Sim (`bin/s9_demo.sh`) | `out/evidence/s9_logs/*.json`, `out/evidence/s9_bundles/*.json`, `out/evidence/s9_responses/*.json`, scorecards `S9_T4/S9_T5/S9_T6` | Valor médio ≈ 221,58 BRL, `num_sources=3`, confiança alta, p95 ≪ 1,5 s |
| C2 — Comparação GLP (RJ) | Sim | Mesmos diretórios + scorecards `S9_T4/S9_T5/S9_T6` | Ranking capital×Baixada com divergências explícitas >5 % quando ocorrem |
| C3 — Checagem factual (BH) | Sim | Mesmos diretórios + scorecards `S9_T4/S9_T5/S9_T6` | Veredito `negado`, limitações claras, trilha completa auditada |

- Invariantes comprovadas no encerramento:
  - **Inv1** — `out/evidence/S9_T6_logs_and_evidence/summary.json` + a demo (`bin/s9_demo.sh`) mostram QueryLog↔EvidenceBundle↔UserResponse acessíveis e coerentes.
  - **Inv2** — Bundles de C1–C3 mantêm `meta.num_sources >= 2` e isso está registrado nos bundles e nos scorecards T4/T6.
  - **Inv3** — Toda decisão passa por `app/gpt_client/client.py`, provado pelos testes T4–T6 e reforçado no runbook (pipeline usa apenas bundles).
  - **Inv4** — Métricas (`metrics_s9`) e scorecards T5/T6 documentam p95 < 1,5 s e ausência de erros silenciosos; a demo não introduziu falhas adicionais.

## Evidências e referências

- `out/evidence/S9_T4_golden_flows/summary.json` — Golden flows C1–C3 batendo com os goldens oficiais.
- `out/evidence/S9_T5_perf_and_limits/summary.json` — Métricas oficiais (p50/p95, erro, throughput) coletadas via `metrics_s9.get_metrics_snapshot()`.
- `out/evidence/S9_T6_logs_and_evidence/summary.json` — Auditoria da trilha QueryLog↔EvidenceBundle↔UserResponse provando Inv1–Inv4 na prática.
- `out/evidence/S9_T7_ci_pipeline/summary.json` — Execução CI com T1–T6 encadeados.
- `out/evidence/S9_T8_go_no_go/summary.json` — Consolidação dos scorecards S9_T0…S9_T7 e decisão final GO.

## Limitações e recomendações para S10–S12

1. **Hardening de fontes dinâmicas** — fixtures S9 são snapshots; precisamos integrar conectores online com fallback seguro antes da produção.
2. **Observabilidade persistente** — métricas vivem em memória; estabelecer backend Prometheus/exporter e dashboards oficiais nas próximas sprints.
3. **Cobertura adicional de UX/Admin** — UI Admin ainda não expõe todas as métricas de `metrics_s9`; incorporar health badges/dashboards.
4. **Automação de demo/checklist** — Fase 8 ainda depende de execução manual; sugerimos scripts/guias de demo reutilizando os goldens e métricas para evitar desvios.
