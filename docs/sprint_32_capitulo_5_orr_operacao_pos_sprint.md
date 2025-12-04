# Sprint 32 — Capítulo 5 (ORR & operação pós-sprint)

Checklist ORR concluído com base no Cap.5 oficial:

- Gates S32_G0–S32_G4: todos PASS (scorecards em `out/scorecards/`).
- Bundle: `out/bundles/inspectah_s32_evidence_bundle.zip` gerado e com integridade validada (`unzip -t`).
- Evidências principais:
  - `out/evidence/S32_G1_models_and_invariants/run.log`
  - `out/evidence/S32_G2_promotion_flows/run.log`
  - `out/evidence/S32_G3_contestation_flows/run.log`
  - `out/evidence/S32_G4_orr_and_bundle/run.log`
- Sanidade cruzada ingestão/claims:
  - S21: `bash bin/s21_all_gates.sh` → PASS (G0–G7).
  - S24: gate G1 rodado com fallback → WARN (dependências ausentes: pytest/fastapi). Scorecard `out/scorecards/S24_G1_debunk_tests.json`. Reexecutar em ambiente completo para GO (se necessário para ORR amplo).

Estado para operação:
- Migração S32 aplicada em `out/databases/s32_truth.sqlite` (fluxo de gates).
- Serviços centrais implementados: PromotionService e ContestationService em `app/truthdb/services.py`, métricas em `app/truthdb/metrics.py`.

Pendências/observações:
- pytest não instalado globalmente; gates S32 usam fallback python puro (OK para reexecução). S24_G1 precisa de pytest/fastapi reais para validar.
- Rerodar sanidade S24 em ambiente completo e registrar resultado/waiver conforme ORR.
