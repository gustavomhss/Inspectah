# Sprint 17 — ORR Summary

## Objetivo
UI de consulta do Inspectah (v1): pergunta em linguagem natural, resposta consolidada, nível de risco em destaque e evidências principais, com mensagens claras para vazio/erro/incerteza.

## Gate × Status
| Gate | Status | Observações |
| --- | --- | --- |
| S17_T0_sanity | TBD | Ambiente frontend, lint/test/build |
| S17_T1_contracts_and_states | TBD | Máquina de estados + tipos UI↔API |
| S17_T2_ux_and_accessibility | TBD | UX mínima, acessibilidade básica |
| S17_T3_api_integration | TBD | Sucesso/risco/erros integrados |
| S17_T4_golden_flows | TBD | Casos canônicos baixo/alto/incerto |
| S17_T5_performance_and_bundle | TBD | Build e tamanho de bundle |
| S17_T6_frontend_observability | TBD | Error boundary + logs |
| S17_T7_ci_and_repro | TBD | CI definida e reproducibilidade |
| S17_T8_go_no_go | TBD | GO/NO_GO final |

## Artefatos principais
- Código: `frontend/inspectah-ui/` (React+TS+Vite+Tailwind).
- Scripts de gate: `bin/s17_t0...s17_t8.sh`, orquestração `bin/s17_all_gates.sh`.
- Scorecards: `out/scorecards/S17_T*.json` (gerados pelos scripts).
- Evidências: `out/evidence/S17_T*_*/*` (logs de lint/test/build/checklists).
- CI: `.ci/sprint_17_gates.yml`, `.ci/sprint_17_nightly.yml`.
- Documentação: `docs/sprint_17_overview.md`, `docs/sprint_17_filemap_e_arquitetura.md`, este arquivo.

## Riscos e próximos passos
- Ajustar integração com backend real/stub conforme ambientes de S15/S16 (ver `VITE_INSPECTAH_API_BASE_URL`/`VITE_INSPECTAH_CONSULT_PATH`).
- Monitorar tamanho de bundle e performance percebida conforme casos canônicos evoluírem.
- S18–S20: adicionar console/admin, timeline/raio-X, auth básica e observabilidade avançada de UI.

## Para conclusão pós-pipeline
Após rodar `PYTHONPATH=. bin/s17_all_gates.sh` no commit final:
- Atualizar a tabela acima com PASS/FAIL.
- Preencher `commit_sha` e `decision` em `out/scorecards/S17_T8_go_no_go.json`.
- Registrar aqui o SHA final, decisão GO/GO_WITH_RESTRICTIONS/NO_GO e restrições aplicáveis.
