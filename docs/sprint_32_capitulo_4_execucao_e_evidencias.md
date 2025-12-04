# Sprint 32 — Capítulo 4 (execução & evidências)

Resumo factual do que foi executado na S32, alinhado ao Cap.4 oficial.

- **G0**: `out/scorecards/S32_G0_scope_and_baseline.json` (PASS) — estrutura, docs e scripts presentes.
- **G1**: `out/scorecards/S32_G1_models_and_invariants.json` (PASS) — migração `0034_s32_truthdb_blocks.py`, testes de invariantes `tests/truthdb/test_models_and_invariants.py`, log em `out/evidence/S32_G1_models_and_invariants/run.log`.
- **G2**: `out/scorecards/S32_G2_promotion_flows.json` (PASS) — `PromotionService`, adaptadores de claim, métricas; testes em `tests/truthdb/test_promotion_flows.py`, log em `out/evidence/S32_G2_promotion_flows/run.log`.
- **G3**: `out/scorecards/S32_G3_contestation_flows.json` (PASS) — `ContestationService`, contestação end-to-end; testes em `tests/truthdb/test_contestation_flows.py`, log em `out/evidence/S32_G3_contestation_flows/run.log`.
- **G4**: `out/scorecards/S32_G4_orr_and_bundle.json` (PASS) — bundle `out/bundles/inspectah_s32_evidence_bundle.zip` íntegro (`unzip -t` OK), log em `out/evidence/S32_G4_orr_and_bundle/run.log`.

Evidências principais:
- Scorecards: `out/scorecards/`.
- Logs por gate: `out/evidence/S32_G*_*/run.log`.
- Bundle final: `out/bundles/inspectah_s32_evidence_bundle.zip`.
