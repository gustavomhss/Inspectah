# Inspectah — Sprint 3 Plan (Codex)

> **Modo atual:** PLAN. Sem aplicar diffs grandes até que o plano esteja validado.  
> **Fonte de verdade:** Capítulos 1–4 + Gates T0–T8 + filemap do Cap.3.

## 1. Objetivos da Sprint 3 ↔ Gates

| Objetivo de Sprint | Gates diretamente impactados | Observações práticas |
| --- | --- | --- |
| Ancorar o repositório nas specs vFinal (Cap.1–4 + blueprint) | **T0**, T7 | Criar `docs/inspectah_cap_1_produto.md` … `cap_4_playbook.md`, apontar `bin/orr_t0_spec_lock.sh` para eles, garantir evidência em `out/evidence/T0_spec_lock/`. |
| Normalizar schema + migrações + Field Designer scaffold | **T1**, T2, T3 | Migrar `db/` → `schema/` + `schema/migrations/`, alinhar scripts `bin/orr_t1_schema_check.sh`, atualizar tests. |
| Tornar Field Designer + watchers puramente configuráveis | **T2**, **T3**, T4 | Mover configs para `configs/sources/`, separar `src/field_designer/`, `src/watchers/`, `src/evidence_vault/`, garantir scorecards `T2_field_designer.json`, `T3_pipeline_invariants.json`. |
| Evidence Vault completo e auditável | **T4**, T5 | Formalizar `out/evidence/T4_evidence_vault/`, criar auditoria determinística `bin/orr_t4_evidence_audit.sh`, revisar `src/evidence_vault/*`. |
| Performance, latência e sucesso de resolução | **T5** | Preparar `bin/orr_t5_performance_gate.sh`, métricas em `ops/prometheus/*`, snapshots em `out/evidence/T5_performance/`. |
| Confidence Engine (HIGH RISK) e plano T5.2 | **T5.1**, T5.2 (base) | Criar `src/confidence_engine/*`, `configs/profiles/confidence_profiles.yaml`, `bin/orr_t5_1_confidence_gate.sh`, mapear onde ficam dados de calibração. |
| Observabilidade ponta-a-ponta | **T6**, T4/T5 dependentes | Estruturar `ops/otel/`, `ops/prometheus/`, `ops/grafana/`, `src/observability/`, script `bin/orr_t6_observability_smoke.sh`. |
| ORR/CI unificado e simultâneo | **T7** | Adicionar `.ci/orr_pipeline.yml`, scripts `bin/orr_t7_orr_pipeline.sh`, garantir bundle único + PASS simultâneo T0–T7. |
| Go/No-Go com dados reais | **T8** | `bin/orr_t8_go_nogo_helper.sh`, `out/scorecards/T8_go_nogo.json`, materializando uso real / ready logs. |

## 2. Estado atual vs. desejado (por Gate)

| Gate | Estado atual (11/2025) | Divergências vs. Cap.3 | Ação necessária |
| --- | --- | --- | --- |
| **T0** | Existe `docs/d8_spec.md` + script `bin/orr_t0.sh` apontando para esse arquivo. Não existem `docs/inspectah_cap_*.md` nem blueprint canônico. Scorecards `T0_spec.json` fora do padrão. | Filemap exige `docs/inspectah_cap_1_produto.md` … `cap_4_playbook_codex.md` + blueprint; evidências devem viver em `out/evidence/T0_spec_lock/`. | Copiar Capítulos 1–4 do diretório do usuário (`Documents/Sprint 3/`) para `docs/inspectah_cap_*.md`, criar blueprint em `docs/blueprint/`, ajustar script/scorecards para novo path e formato. |
| **T1** | Schema vive em `db/schema.sql` + `db/migrations/`. `bin/orr_t1.sh` faz checklist de arquivos Python. Não existe `schema/` dedicado. | Cap.3 exige `schema/inspectah_ddl.sql` + `schema/migrations/VNNN__*.sql`; Gate T1 precisa validar invariantes e constraints, não apenas existência de arquivos Python. | Migrar diretórios (`db/` → `schema/`), atualizar script para rodar `sqlfluff`/`sqlite3` dry-run + validar invariantes; gerar scorecards `T1_schema.json` e evidências `out/evidence/T1_schema/`. |
| **T2** | Field Designer configurado via `registry/fields` + `registry/sources`; script `bin/orr_t2.sh` roda `tests/unit`. Configs em YAML não seguem `configs/sources/`. | Cap.3 define `configs/sources/*.yaml`, `src/field_designer/*`, `bin/orr_t2_field_designer_smoke.sh`, scorecard `T2_field_designer.json`. | Criar `src/field_designer/`, mover lógica do `registry/` para código modular, normalizar configs, atualizar testes/scrips e evidências `out/evidence/T2_field_designer/`. |
| **T3** | `bin/orr_t3.sh` executa testes contract/integration, mas watchers vivem em `inspectah/watchers/` e pipeline se mistura com Evidence Vault. Scorecard `T3_contract.json`. | Gate T3 deve validar dedup, imutabilidade, backfill, com scripts `bin/orr_t3_pipeline_invariants.sh` e `out/evidence/T3_pipeline_invariants/`. | Introduzir suíte sintética (fixtures + property tests) e script dedicado, separar watchers para `src/watchers/`, `src/evidence_vault/`. |
| **T4** | `bin/orr_t4.sh` empacota resultados do script legado `bin/d8_ci.sh`. Evidence Vault vive em `services/evidence_vault/` + `inspectah/evidence/`. Scorecards `T4_golden.json`. | Necessário `bin/orr_t4_evidence_audit.sh` lendo `src/evidence_vault/*`, manifestos por Item, checksums, `out/evidence/T4_evidence_vault/`. | Refatorar Evidence Vault CLI + auditor, movimentar assets para `src/evidence_vault/`, gerar bundles e scorecards compatíveis. |
| **T5** | Scripts `bin/orr_t5.sh` focam em métricas locais `inspectah/metrics.py` + fixtures RSS; `out/evidence/T5_metrics/` existe mas thresholds não alinhados. Não há `ops/*`. | T5 precisa medir `detection_latency_p95`, `explore_query_p95/p99`, `field_resolution_success`, `run_success_rate` com thresholds do Cap.2; dados devem residir em `ops/prometheus/`, dashboards em `ops/grafana/`. | Adicionar pipelines de benchmark (`bin/orr_t5_performance_gate.sh`), instrumentar watchers/explore com Prometheus, mover dashboards para `ops/`. |
| **T5.1** | **Inexistente**: não há `confidence_engine`, `configs/profiles/` ou script `bin/orr_t5_1_confidence_gate.sh`. | Cap.2 exige heurística de `confidence_score`, cobertura ≥95%, e plano explícito para dados de calibração (T5.2 futuro). | Criar módulo `src/confidence_engine/`, perfis em `configs/profiles/confidence_profiles.yaml`, script de Gate que produz `out/scorecards/T5_1_confidence.json` + `out/evidence/T5_1_confidence/`, registrar onde métricas de calibração viverão. |
| **T6** | `bin/orr_t6.sh` apenas agrega scorecards e chama `bin/orr_t6_ci`. Não existe `ops/otel/`/`ops/prometheus/`/`ops/grafana/`; observabilidade dispersa. | Gate T6 precisa validar coletores, alertas, dashboards e exporters. | Criar `ops/` árvore, scripts de smoke checks para métricas/logs/traces, evidências `out/evidence/T6_observability/`, atualizar ORR. |
| **T7** | `.ci/` contém apenas shell scripts (`bench.sh`, `tests.sh`, etc.). Não há `.ci/orr_pipeline.yml`. `bin/orr_t7.sh` só lê bundle local. | Precisamos de pipeline replicável (local + CI) que execute todos os Gates T0–T7, gere bundle único e scorecard `T7_orr.json`. | Adicionar `.ci/orr_pipeline.yml`, `bin/orr_t7_orr_pipeline.sh`, CLI helper `bin/orr_all.sh` apontando para os novos scripts, atualizar evidências `out/evidence/T7_orr/`. |
| **T8** | `bin/orr_t8.sh` verifica scorecards legados (`T6_ci.json`, `T7_ready.json`, `D8_ci.json`) e `docs/d8_summary.md`. Não há integração com dados reais de uso/API. | Gate T8 precisa medir ready state com métricas reais + feedback de operadores, `out/evidence/T8_go_nogo/`, `out/scorecards/T8_go_nogo.json`. | Atualizar fontes de verdade (API telemetry, UI usage), ajustar script/go helper para os novos scorecards e garantir `GO` depende da simultaneidade ORR. |

## 3. Backlog de blocos de trabalho (Gate-first)

| ID | Gate(s) alvo | Tipo (Catálogo) | Descrição & Arquivos chave | Risco | Dependências |
| --- | --- | --- | --- | --- | --- |
| B1 | T0 | Especificação/Docs | Copiar Capítulos 1–4 + blueprint para `docs/inspectah_cap_*.md`, atualizar `bin/orr_t0_spec_lock.sh`, gerar scorecard `T0_spec_lock.json`. | Normal | Nenhuma |
| B2 | T1 | Mudança de schema/DDL | Renomear `db/` → `schema/`, converter `schema.sql` em `schema/inspectah_ddl.sql`, criar migrações versionadas, atualizar script `bin/orr_t1_schema_check.sh` para validar constraints reais e gerar evidências `T1_schema/`. | Normal | B1 |
| B3 | T2, T3 | Nova fonte + watcher / Refactor pipeline | Introduzir `configs/sources/`, `src/field_designer/`, `src/watchers/`, migrar `registry/*` para esses módulos, criar script `bin/orr_t2_field_designer_smoke.sh`, `bin/orr_t3_pipeline_invariants.sh`, atualizar scorecards `T2_field_designer.json`, `T3_pipeline_invariants.json`. | Normal | B2 |
| B4 | T4 | Evidence Vault hardening | Criar `src/evidence_vault/` módulo standalone, mover CLI/scripts de `scripts/` → `bin/orr_t4_evidence_audit.sh`, garantir bundles em `out/evidence/T4_evidence_vault/`, atualizar watchers para gravar manifests Cap.3. | Normal | B3 |
| B5 | T5 | Performance | Instrumentar `src/watchers/` e `src/explore/` com métricas Prometheus (`ops/prometheus/`, `ops/grafana/`), escrever `bin/orr_t5_performance_gate.sh`, `out/scorecards/T5_performance.json`. | Normal | B4 |
| B6 | T5.1, T5.2 base | Ajuste Confidence (HIGH RISK) | Criar `src/confidence_engine/` e `configs/profiles/confidence_profiles.yaml`, integrar a UI/API, script `bin/orr_t5_1_confidence_gate.sh`, evidências `out/evidence/T5_1_confidence/`, documentação sobre dados de calibração (T5.2). | **High Risk** | B3, B4, B5 |
| B7 | T6 | Observabilidade | Estruturar `ops/otel/`, `ops/prometheus/`, `ops/grafana/`, script `bin/orr_t6_observability_smoke.sh`, atualizar dashboards (migrar `docs/dashboards/*` para `ops/grafana/`). | Normal | B5 |
| B8 | T7 | ORR/CI | Criar `.ci/orr_pipeline.yml`, padronizar `bin/orr_tX_*.sh` (nomes completos), ajustar `bin/orr_all.sh`, `bin/orr_t7_orr_pipeline.sh`, garantir bundle único + upload em `out/evidence/T7_orr/` e scorecard `T7_orr.json`. | Normal | B1–B7 |
| B9 | T8 | Go/No-Go operacional | Atualizar `bin/orr_t8_go_nogo_helper.sh` para consumir métricas reais (API usage/outage logs), gerar `out/evidence/T8_go_nogo/` e `out/scorecards/T8_go_nogo.json`, amarrado à simultaneidade ORR. | Normal | B8 |

## 4. Ordem sugerida de execução (Gate-first)

1. **B1 – T0 Docs Alignment:** Garantir que Capítulos 1–4 e blueprint estejam versionados, permitindo Spec Lock sólido.
2. **B2 – T1 Schema Migration:** Reorganizar `schema/` + migrar script para validar invariantes reais.
3. **B3 – T2/T3 Config + Pipeline Refactor:** Normalizar Field Designer, watchers e configs, desbloqueando coletas reais.
4. **B4 – T4 Evidence Vault:** Reforçar bundling, auditoria e manifests, preparando terreno para performance/confidence.
5. **B5 – T5 Performance:** Instrumentar métricas e garantir limiares do Cap.2.
6. **B6 – T5.1 Confidence (High Risk):** Implementar engine, perfis e Gate, com plano explícito de calibração T5.2.
7. **B7 – T6 Observabilidade:** Ativar `ops/` e smoke tests para métricas, logs e alertas.
8. **B8 – T7 ORR Pipeline:** Conectar todos os Gates em `.ci/orr_pipeline.yml`, orquestrar bundle único e garantir PASS simultâneo.
9. **B9 – T8 Go/No-Go:** Consumar decisão baseada em uso real + métricas pós-ORR.

## 5. Notas adicionais

- **Filemap converge:** Toda alteração precisa apontar para caminhos do Cap.3 (`docs/`, `schema/`, `configs/`, `src/`, `ops/`, `bin/`, `.ci/`, `out/`). Pastas antigas (`services/`, `registry/`, `data/…`) serão migradas gradualmente ou marcadas como legado.
- **Scorecards e evidências:** Cada Gate passará a produzir `out/scorecards/TX_*.json` (formato comum com `gate`, `name`, `version`, `status`, `timestamp`, `metrics`, `thresholds`, `details`) e `out/evidence/TX_*/` sincronizados.
- **Confidence = alta criticidade:** Qualquer mudança em `confidence_score` ou `confidence_profile_id` deve seguir B6, com plano explícito para calibração T5.2 registrado no `docs/sprint_3_plan_codex.md`.
- **ORR simultâneo:** Nenhum bloco será encerrado sem rodar `bin/orr_tX_*` relevantes localmente **e** ter evidência na CI (`.ci/orr_pipeline.yml`) mostrando T0–T7 `PASS` simultâneos após a mudança.
- **T1 baseline migrado:** `schema/inspectah_ddl.sql` + `schema/migrations/V001__bootstrap_schema.sql` representam o modelo (Fontes, Observações, Items, Item Versions, Evidence) e `bin/orr_t1_schema_check.sh` já valida o Gate produzindo `T1_schema.json`.
- **T2 Field Designer em dry-run:** `configs/sources/*.yaml` definem três fontes (RSS/API/HTML), `src/field_designer/*` executa previews e `bin/orr_t2_field_designer_smoke.sh` gera `T2_field_designer.json` + evidências com amostras.
- **T3 Pipeline invariants:** `src/watchers/pipeline_runner.py` aplica as fixtures via Field Designer, escreve no schema canônico e `bin/orr_t3_pipeline_invariants.sh` assegura dedup/imutabilidade/lineage com `T3_pipeline_invariants.json` + `pipeline_report.json`.
- **T4 Evidence Vault:** `src/evidence_vault/bundle_builder.py` cria bundles (raw + manifest) após o pipeline, `src/evidence_vault/audit_runner.py` audita hashes/completude e `bin/orr_t4_evidence_audit.sh` gera `T4_evidence_vault.json` + `evidence_report.json`.
- **T5 Performance:** `src/observability/perf_runner.py` roda ingestão/consultas sintéticas, mede p95/p99 e `bin/orr_t5_performance_gate.sh` publica `T5_performance.json` + `perf_report.json`.
- **T5.1 Confidence:** `src/confidence_engine/*` (core/profiles/audit) calcula scores explicáveis, `configs/profiles/confidence_profiles.json` define pesos e `bin/orr_t5_1_confidence_gate.sh` gera `T5_1_confidence.json` + `audit_report.json`/`calibration_dataset.json`.
- **T6 Observabilidade:** `src/observability/metrics.py` agrega scorecards T2–T5.1, `bin/orr_t6_observability_smoke.sh` valida e produz `T6_observability.json` + `metrics_snapshot.json`.
- **T7 ORR/CI:** `bin/orr_all.sh` orquestra T0–T6 e `.ci/orr_pipeline.yml` executa em CI, gerando `T7_orr_pipeline.json` + `out/evidence/T7_orr_pipeline/orr_summary.json`.

Este plano será atualizado conforme blocos forem entregues e as lacunas do filemap forem fechadas.
