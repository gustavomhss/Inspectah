# Inspectah — Sprint 3 ORR Summary

## 1. Visão geral
Sprint 3 consolidou o Inspectah como um hub auditável de fontes. Implementamos o filemap completo dos Gates T0–T7, com scorecards e evidências em `out/scorecards/` e `out/evidence/` que provam desde o Spec Lock até a observabilidade. Este documento serve como wrap oficial para o comitê de GO/NO_GO.

## 2. Status dos Gates
| Gate | Pergunta | Status | Scorecard |
| --- | --- | --- | --- |
| T0 | Spec Lock | PASS | `out/scorecards/T0_spec_lock.json` |
| T1 | Modelo/Schema | PASS | `out/scorecards/T1_schema.json` |
| T2 | Field Designer | PASS | `out/scorecards/T2_field_designer.json` |
| T3 | Pipeline invariants | PASS | `out/scorecards/T3_pipeline_invariants.json` |
| T4 | Evidence Vault | PASS | `out/scorecards/T4_evidence_vault.json` |
| T5 | Performance | PASS | `out/scorecards/T5_performance.json` |
| T5.1 | Confidence Engine | PASS | `out/scorecards/T5_1_confidence.json` |
| T6 | Observabilidade | PASS | `out/scorecards/T6_observability.json` |
| T7 | ORR/CI | PASS | `out/scorecards/T7_orr_pipeline.json` |

## 3. Entregas principais
- **Modelo & schema canônico (T1):** `schema/inspectah_ddl.sql` + `schema/migrations/V001__bootstrap_schema.sql` traduzem o capítulo 1 (Sources, Observations, Items, Versions, Evidence) e são validados por `bin/orr_t1_schema_check.sh`.
- **Field Designer & fontes (T2):** `configs/sources/*.yaml`, `src/field_designer/*` e `bin/orr_t2_field_designer_smoke.sh` permitem cadastrar/validar fontes RSS/API/HTML com dry-run e scorecard `T2_field_designer.json`.
- **Pipeline invariants (T3):** `src/watchers/pipeline_runner.py` executa ingestões sintéticas e garante dedup, imutabilidade e lineage (`T3_pipeline_invariants.json`).
- **Evidence Vault (T4):** `src/evidence_vault/bundle_builder.py` + `audit_runner.py` criam bundles raw/manifest com hashes e LGPD tags; `bin/orr_t4_evidence_audit.sh` garante completude/hashes/órfãos (`T4_evidence_vault.json`).
- **Performance (T5):** `src/observability/perf_runner.py` mede ingestão e consultas (p95/p99) e `bin/orr_t5_performance_gate.sh` gera `T5_performance.json` + `out/evidence/T5_performance/perf_report.json`.
- **Confidence Engine (T5.1, HIGH RISK):** `src/confidence_engine/core.py`, `profiles.py`, `audit_runner.py` e `configs/profiles/confidence_profiles.json` calculam scores 0–100 explicáveis e guardam dataset para T5.2 (`out/evidence/T5_1_confidence/audit_report.json` + `calibration_dataset.json`).
- **Observabilidade (T6):** `src/observability/metrics.py` agrega scorecards T2–T5.1 e `bin/orr_t6_observability_smoke.sh` garante presença/sanidade das métricas (`T6_observability.json`).
- **ORR/CI (T7):** `bin/orr_all.sh` orquestra T0–T6 localmente e `.ci/orr_pipeline.yml` roda o mesmo fluxo em CI; evidências consolidadas em `out/evidence/T7_orr_pipeline/` e scorecard `T7_orr_pipeline.json`.

## 4. Riscos e débitos remanescentes
1. **Fontes reais:** pipeline ainda usa fixtures sintéticas. Próxima sprint deve on-board fontes reais e manter T2–T5 verdes com dados vivos.
2. **Observabilidade externa:** métricas estão em snapshot local; precisamos exportar para Prometheus/Grafana e ter alertas reais.
3. **Calibração T5.2:** dataset pronto, mas falta experimento de calibração e governança de confiança em produção.
4. **UI/Explore:** as APIs de consulta ainda são básicas; próxima sprint deve priorizar UX e filtros avançados.
5. **Automação multi-ambiente:** ORR roda em CI, mas precisamos conectar T8 ao processo de release/staging/prod oficialmente.

## 5. Próximos passos sugeridos
1. **Onboarding de fontes reais** (RSS oficiais, APIs públicas) mantendo T2–T5 saudáveis.
2. **Stack observabilidade externa** (Prometheus/Grafana + alertas) alimentada pelo snapshot local.
3. **Confidence T5.2:** usar `calibration_dataset.json` para calibrar heurísticas e registrar thresholds dinâmicos.
4. **Evolução de Explore/UI:** construir consultas com filtros, ordenação e visualização de evidências direto na interface.
5. **Automação de release:** amarrar T8 + ORR nos fluxos de aprovação/governança da equipe.

Evidências completas ficam em `out/evidence/` (T0–T7) e `out/evidence/T8_go_no_go/` após a execução do Gate T8.
