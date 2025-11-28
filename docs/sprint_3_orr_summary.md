# Inspectah — Sprint 3 ORR Summary

## 1. Visão geral
Sprint 3 consolidou o Inspectah como um hub auditável de fontes. Implementamos o filemap completo dos Gates T0–T7, com scorecards e evidências em `out/scorecards/` e `out/evidence/` que provam desde o Spec Lock até a observabilidade. Esta seção resume o estado atual para PO/CTO/Comitê.

## 2. Status dos Gates
| Gate | Pergunta | Status | Scorecard |
| --- | --- | --- | --- |
| T0 | Spec Lock | PASS | `out/scorecards/T0_spec_lock.json` |
| T1 | Schema | PASS | `out/scorecards/T1_schema.json` |
| T2 | Field Designer | PASS | `out/scorecards/T2_field_designer.json` |
| T3 | Pipeline invariants | PASS | `out/scorecards/T3_pipeline_invariants.json` |
| T4 | Evidence Vault | PASS | `out/scorecards/T4_evidence_vault.json` |
| T5 | Performance | PASS | `out/scorecards/T5_performance.json` |
| T5.1 | Confidence Engine | PASS | `out/scorecards/T5_1_confidence.json` |
| T6 | Observabilidade | PASS | `out/scorecards/T6_observability.json` |
| T7 | ORR Pipeline | PASS | `out/scorecards/T7_orr_pipeline.json` |

## 3. Entregas principais
- **Modelo & Schema (T1):** `schema/inspectah_ddl.sql` + `schema/migrations/V001__bootstrap_schema.sql` representam Sources/Observations/Items/Versions/Evidence; `inspectah/models.py` espelha tudo em SQLite.
- **Field Designer (T2):** `configs/sources/*.yaml`, `src/field_designer/*` e `bin/orr_t2_field_designer_smoke.sh` permitem cadastrar/validar fontes RSS/API/HTML.
- **Pipeline invariants (T3):** `src/watchers/pipeline_runner.py` roda ingestões sintéticas e garante dedup, imutabilidade e lineage sem violações.
- **Evidence Vault (T4):** `src/evidence_vault/bundle_builder.py` + `audit_runner.py` criam bundles raw/manifest com hashes e LGPD tags, auditados via `bin/orr_t4_evidence_audit.sh`.
- **Performance (T5):** `src/observability/perf_runner.py` mede ingestão e consultas com p95/p99, registradas em `out/evidence/T5_performance/perf_report.json`.
- **Confidence Engine (T5.1, HIGH RISK):** `src/confidence_engine/core.py`, `profiles.py`, `audit_runner.py` e `configs/profiles/confidence_profiles.json` calculam scores de 0–100 com explicações e dataset de calibração (`out/evidence/T5_1_confidence/calibration_dataset.json`).
- **Observabilidade (T6):** `src/observability/metrics.py` agrega scorecards T2–T5.1 em `metrics_snapshot.json`; gate `bin/orr_t6_observability_smoke.sh`.
- **ORR/CI (T7):** `bin/orr_all.sh` orquestra T0–T6 localmente; `.ci/orr_pipeline.yml` roda o mesmo fluxo em CI com artifacts em `out/evidence/T7_orr_pipeline/`.

## 4. Riscos e débitos
1. **Fontes reais** ainda não foram plugadas (fixtures sintéticas). Próxima sprint deve conectar fontes vivas garantindo T2–T5 verdes.
2. **Observabilidade externa** limitada ao snapshot local; precisamos exportar métricas para Prometheus/Grafana produtivo e configurar alertas reais.
3. **Calibração T5.2** pendente: dataset pronto, mas falta experimento de calibração e guardrails adicionais.
4. **UI/API** de Explore é mínima; próxima sprint deve evoluir para consultas ricas e exposição amigável.
5. **Automação multi-ambiente**: ORR está em CI, mas falta pipeline para ambientes staging/prod com dados reais.

## 5. Próximos passos sugeridos
1. **Onboarding de fontes reais** (RSS oficiais, APIs públicas) e watchers correspondentes, validando T2–T4/T5 em produção.
2. **Stack observabilidade externa** (Prometheus/Grafana + alertas) alimentada pelo snapshot local e métricas runtime.
3. **Confidence T5.2**: usar `calibration_dataset.json` para calibrar/ajustar heurísticas com dados reais e preparar thresholds operacionais.
4. **UI/Exploração**: evoluir `inspectah/explore`/UI para permitir consulta, filtros, export, view de evidências e explicações.
5. **Automação de release**: integrar T8 e ORR ao processo de aprovação/gateway (CI/CD) e registrar histórico de decisões GO/NO_GO.

Evidências completas estão em `out/evidence/T7_orr_pipeline/` e, após T8, também em `out/evidence/T8_go_no_go/`. Este doc é referenciado pelo Gate T8 como wrap oficial da Sprint 3.
