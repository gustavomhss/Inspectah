# Sprint 16 — ORR de Hardening

## Objetivo
Consolidar o estado de hardening do pacote S13–S16 (Truth-DB + Debunker v1 + Comitês V1/V2/V3 + Âncoras + Anti-canetada), alinhado ao Threat Model em `docs/sprint_16_threat_model.md`, decidindo GO/GO_WITH_RESTRICTIONS/NO_GO com base nos gates T0–T8.

## Gates e status
- T0 Sanity & S15 baseline: **PASS/GO** — `out/scorecards/S16_T0_sanity.json`.
- T1 Threat Model: **PASS/GO** — `out/scorecards/S16_T1_threat_model.json`.
- T2 Cenários de Ataque: **PASS/GO** — `out/scorecards/S16_T2_attack_scenarios.json`.
- T3 Debunker & Comitês: **PASS/GO** — `out/scorecards/S16_T3_debunker_and_committees_under_attack.json`.
- T4 Âncoras e Anti-canetada: **PASS/GO_WITH_RESTRICTIONS** — `out/scorecards/S16_T4_anchors_and_anti_canetada.json`.
- T5 Stress e Degradação: **PASS/GO** — `out/scorecards/S16_T5_stress_and_degradation.json`.
- T6 Observabilidade de Segurança: **PASS/GO** — `out/scorecards/S16_T6_security_observability.json`.
- T7 CI e Reprodutibilidade: **PASS/GO** — `out/scorecards/S16_T7_ci_and_repro.json`.
- T8 Go/No-Go consolidado: **PASS/GO_WITH_RESTRICTIONS** — `out/scorecards/S16_T8_go_no_go.json`.

## Evidências principais
- Pastas `out/evidence/S16_T*/` com `MANIFEST.json`, logs e relatórios de cenários de ataque/stress (T2–T5) e consolidação de T8.
- Threat Model: `docs/sprint_16_threat_model.md`.
- Scripts e gates executados: `bin/s16_t*.sh`, `scripts/s16_*.py`.
- Workflows de CI: `.ci/sprint_16_gates.yml`, `.ci/sprint_16_nightly.yml`.

## Riscos residuais
- Cliente de chain ainda simulado: T4 registrou falhas de chain como GO_WITH_RESTRICTIONS; reorg real e latências de rede precisam de validação adicional.
- Heurísticas determinísticas do Debunker podem subestimar conteúdo malicioso sofisticado.
- Stress local limitado por recursos; comportamento pode variar em ambientes maiores.
- Observabilidade depende de artefatos locais; integrações externas podem ficar indisponíveis (mitigado parcialmente pelo T6).

## Decisão final
- **GO_WITH_RESTRICTIONS** — consolidado no `out/scorecards/S16_T8_go_no_go.json`, condicionado à mitigação de riscos de chain/âncoras em ambientes reais e à continuidade da cobertura de CI (`.ci/sprint_16_gates.yml`, `.ci/sprint_16_nightly.yml`).
