# SF1 — Capítulo 2 — Objetivos, Gates, Métricas & DoD

## 2.1 Objetivos ↔ Gates
- O1 Limites aplicados e bloqueio automático → G1.
- O2 Catálogo assinado/hashes comparados em runtime → G0, G1, G3, G4.
- O3 SLO/alertas vivos com evidência → G3.
- O4 RBAC/auditoria obrigatórios → G2, G4.
- O5 Pilotos reais API/UI/metrics → G4.
- O6 Bundle/scorecards fresh e auditáveis → G5.

## 2.2 Gates SF1 (proíbem placeholders)
- **G0 — Escopo & Catálogo blindado:** s35_slos.md fonte única; catálogo `config/flow_catalog/*.yaml` assinado + hash; `bin/s35_bundle.sh` gera manifest; fail se hash/assinatura ausente/divergente.
- **G1 — Limites aplicados:** migração 0036 com deadlines/hash/actor/slo_breach; testes negativos (tempo/percentual/rollbacks/actor ausente/hash divergente) falham; limites bloqueiam promo/rollback; log/auditoria registram razão e `policy_violation` quando aplica; métricas de violação incrementadas.
- **G2 — API/Console com RBAC:** chamadas sem actor → 4xx; auditoria completa; UI exibe hash/estado; erros padronizados.
- **G3 — Observabilidade real:** `curl /metrics` + promtool; alertas disparados/resolvidos; painel `s35_flow_rollout_overview` com dados reais; fail se série vazia.
- **G4 — Pilotos reais:** news_v2 (reapontado para newsdata.io) e contestacao_v0 (mesma fonte com políticas distintas) via API/UI; rollback/promo exercitados; hash publish/runtime comparado; screenshots reais; `slo_breach` simulado; fail se placeholder/dataset duplicado ou se não atingir métricas com dados reais.
- **G5 — ORR/DoD:** review G0–G4, `S35_metrics_summary.json`, bundle `inspectah_s35_evidence_bundle.zip`; GO/NO-GO explícito; mocks → NO-GO.

## 2.3 Métricas/alertas chave
- Métricas: `flow_rollout_requests_total`, `flow_rollout_success_total`, `flow_rollout_rollback_total`, `flow_rollout_duration_seconds`, `flow_policy_violations_total`, `flow_catalog_hash_mismatch_total`, `inspectah_flow_slo_breach_total` (labels `{flow_id,flow_version_id,mode}`).
- Alertas: `rollbacks_rate_gt_threshold`, `slo_breach_mode`, `catalog_hash_drift`, `policy_violation_canary`, `canary_stuck_duration`, `api_rollout_unavailable`.
- Evidência: PromQL não vazia + print de firing/resolution; export JSON/PNG do painel.

## 2.4 Invariantes & DoD (checagem cruzada)
- Actor obrigatório; falta → 4xx + log.
- Hash publish/runtime deve bater; drift bloqueia.
- Limites/SLO/alertas aplicados em runtime; promo/rollback só com verde.
- Eventos OracleOps/Truth incluem flow/mode/version/actor/operation_id/catalog_hash; `slo_breach` logado.
- Métricas/alertas obrigatórias aparecem em PromQL com labels corretos e são validadas com promtool + firing/resolution.
- DoD: G0–G5 PASS sem placeholders; pilotos reais; bundle com logs/metrics/screenshots/hashes; scorecards rerodados com data/commit/hash; carimbo “PASS REAL” vs “NO-GO” explícito em caso de ausência de ambiente; cada gate tem evidência associada (manifest/hash, testes negativos, HTTP logs, PromQL, screenshots reais).
