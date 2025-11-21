# Inspectah — Sprint 14 ORR Summary

## Objetivo da Sprint 14
Endurecer o truth kernel v0, consolidar o Debunker v0 como serviço lógico único, garantir contratos do Explorer/feedback, executar migrações/cleanup leves e entregar gates S14_G0…S14_G8 com observabilidade e decisão formal, em linha com os Capítulos 1–3.

## Entregáveis principais
- Truth kernel v0 documentado e checado (G1).
- Debunker v0 com regras explícitas e consistência aferida (G2).
- Contratos Explorer/feedback preservados (G3) e migrações leves idempotentes (G4).
- Backlog fase 2 estruturado e validado (G5), snapshot de métricas S14 (G6), observabilidade consolidada (G7) e decisão GO/NO_GO (G8).

## Gates e artefatos S14
| Gate | Comando | Scorecard | Evidências |
| --- | --- | --- | --- |
| S14_G0 | `bash bin/s14_g0_env_repo.sh` | `out/scorecards/S14_G0_env_repo.json` | `out/evidence/S14_G0/` |
| S14_G1 | `bash bin/s14_g1_truth_kernel.sh` | `out/scorecards/S14_G1_truth_kernel.json` | `out/evidence/S14_G1/` |
| S14_G2 | `bash bin/s14_g2_debunker_consistency.sh` | `out/scorecards/S14_G2_debunker_consistency.json` | `out/evidence/S14_G2/` |
| S14_G3 | `bash bin/s14_g3_explorer_contracts.sh` | `out/scorecards/S14_G3_explorer_contracts.json` | `out/evidence/S14_G3/` |
| S14_G4 | `bash bin/s14_g4_migrations_and_cleanup.sh` | `out/scorecards/S14_G4_migrations_and_cleanup.json` | `out/evidence/S14_G4/` |
| S14_G5 | `bash bin/s14_g5_regression_smoke.sh` | `out/scorecards/S14_G5_regression_smoke.json` | `out/evidence/S14_G5/` |
| S14_G6 | `bash bin/s14_g6_docs_dna_alignment.sh` | `out/scorecards/S14_G6_docs_dna_alignment.json` | `out/evidence/S14_G6/` |
| S14_G7 | `bash bin/s14_g7_observabilidade.sh` | `out/scorecards/S14_G7_observabilidade.json` | `out/evidence/S14_G7/` |
| S14_G8 | `bash bin/s14_g8_decision.sh` | `out/scorecards/S14_G8_decision.json` | `out/evidence/S14_G8/` |

Status atual: todos os gates S14_G0…S14_G8 em PASS com decisão = GO.

## Execução local e CI
- Execução local prevista: `bash bin/s14_gates_all.sh` seguido de `bash bin/s14_g8_decision.sh` após todos os gates estarem implementados.
- Workflow GitHub Actions: `.github/workflows/_s14-gates.yml` (rodará os gates e publicará evidências).

## Riscos, débitos e próximos passos
- Itens de Fase 2 (Sistema de Blocos completo, blockchain, reputação, contestação avançada, TLA+) permanecem em `docs/sprint_14_backlog_fase2.md`.
- Riscos e débitos atuais documentados em `out/evidence/S14_G6/risks_and_debts.md` (referência replicada em G7).
