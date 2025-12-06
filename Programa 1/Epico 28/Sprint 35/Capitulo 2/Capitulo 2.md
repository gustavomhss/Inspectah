# Inspectah — Sprint 35 — Capítulo 2
## Objetivos, Gates, Métricas & DoD (Governança avançada de fluxo)

### 2.1 Objetivos ↔ Gates (ver Matriz de Cobertura)
- O1 — Rollout governado com promoção/rollback auditável → **G1**, **G2**.
- O2 — Catálogo versionado/assinado com CLI/CI e uso em runtime → **G0**, **G1**, **G3**.
- O3 — Contratos expostos (`flow_version_id` + políticas) para lógica/Truth e OracleOps → **G2**, **G4**.
- O4 — Observabilidade/alertas por modo (teste/canary/ativo) e bundle de evidências → **G3**, **G4**, **G5**.

### 2.2 Gates G0–G5 (testáveis)
- **G0 — Escopo & Catálogo pronto:** 24 arquivos 6×4 completos; catálogo inicial `config/flow_catalog/*.yaml` (news_v2, contestacao_v0) com hash/assinatura; `bin/s35_g0_scope.sh` PASS.
- **G1 — Modelo/rollout habilitado:** migração `0036_s35_flow_governance_advanced.py` aplicada; modos teste/canary/ativo suportados; limites/flags ativos; políticas carregadas do catálogo sem erro; rollback/promoção bloqueiam violações; `bin/s35_g1_model.sh` PASS.
- **G2 — Console/API rollout:** rotas e UI para iniciar canary/teste, promover e rollback com RBAC; estado/diffs visíveis; auditoria completa (`flow_id`, `flow_version_id`, `mode`, `operation_id`, `actor`); `bin/s35_g2_console.sh` PASS.
- **G3 — Observabilidade rollout:** métricas/logs/alertas por fluxo/versão/mode; painel `s35_flow_rollout_overview` não vazio; alertas disparam; `bin/s35_g3_obs.sh` PASS.
- **G4 — Pilotos rollout:** fluxos de notícias e contestação v0 executam canary/teste → promoção/rollback evidenciados; catálogo publicado e consumido; bundle multi-fluxo gerado; `bin/s35_g4_pilotos.sh` PASS.
- **G5 — ORR/DoD:** review G0–G4 + `S35_metrics_summary.json`; GO/NO-GO com riscos/flags; runbooks ensaiados; bundle `inspectah_s35_evidence_bundle.zip` gerado.

### 2.3 Métricas e alertas chave
- Métricas de rollout: `flow_rollout_requests_total{flow_id,flow_version_id,mode}`, `flow_rollout_success_total`, `flow_rollout_rollback_total`, `flow_rollout_duration_seconds`, `flow_policy_violations_total`.
- Métricas de execução: `flow_exec_total{flow_id,flow_version_id,mode}`, `flow_exec_latency_p95`, `flow_exec_error_total`.
- Alertas: `rollbacks_rate_gt_threshold` (canary), `slo_breach_mode` (teste/ativo), `catalog_hash_drift`, `policy_violation_canary`, `canary_stuck_duration`.

### 2.4 Invariantes & DoD
- Toda operação de rollout/promoção/rollback é auditada com `flow_id`, `flow_version_id`, `mode`, `operation_id`, `actor`, `catalog_hash`.
- Catálogo publicado (hash/assinatura) é o mesmo carregado em runtime; divergência falha **G1/G3**.
- Canary/teste percentual respeitam limites (`max_test_percentual`, `max_rollbacks_per_hour`, `max_canary_duration_minutes`) e bloqueiam promoção se SLO/alertas negativos.
- **DoD:** G0–G5 PASS; catálogo versionado e publicado; rollout governado nos dois pilotos com evidências (logs, métricas, timeline, screenshots, bundle); OracleOps exibe estado de rollout e SLO/alertas por modo; contratos com `flow_version_id` expostos.
