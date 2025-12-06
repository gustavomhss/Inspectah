# Inspectah — Sprint 34 — Capítulo 3
## Arquitetura, Filemap e Contratos (Multi-fluxo governável + OracleOps v2)

### 3.1 Visão geral
- Estender o modelo de fluxo governável para múltiplos domínios com templates versionados, políticas mínimas e integrações de operação/SLO/incident.
- Console multi-fluxo oferece histórico, diffs, rollback e status de SLO/incident por versão.
- Observabilidade conecta métricas/logs/alertas a `flow_id/flow_version_id` e aos componentes/SLOs do OracleOps.

### 3.2 Filemap essencial
- `app/flows/models.py`, `service.py`, `versioning.py`, `policy_engine.py`
- `app/flows/templates/loader.py` — carrega `config/flow_templates/*.yaml`
- `app/flows/ops_integration.py` — integra com incidentes/SLOs (OracleOps)
- `migrations/versions/0034_s34_flow_multidomain_ops.py`
- `app/api/flow_console_routes.py`, `app/flows/schemas.py`
- `frontend/inspectah-ui/src/features/flows/` (FlowListMulti.tsx, FlowDetailMulti.tsx, FlowOpsPanel.tsx, FlowVersionHistory.tsx, FlowRollbackDialog.tsx)
- Observabilidade: `app/flows/instrumentation.py`, `observability/dashboards/s34_flow_ops_overview.json`, `observability/alerts/s34/*.yaml`
- Scripts/CI: `bin/s34_g0_scope.sh`, `bin/s34_g1_model.sh`, `bin/s34_g2_console.sh`, `bin/s34_g3_obs.sh`, `bin/s34_g4_pilotos.sh`, `bin/s34_metrics_summary.sh`, `bin/s34_bundle.sh`, `.github/workflows/s34-gates.yml`
- Evidências: `out/evidence/S34_G*_*/`, `out/scorecards/S34_G*.json`, `out/bundles/inspectah_s34_evidence_bundle.zip`

### 3.3 Configs e limites
- Templates em `config/flow_templates/news_v2.yaml`, `config/flow_templates/contestacao_v0.yaml`
- Limites em `config/flows_limits.yaml`:  
  `max_rollbacks_per_hour: 2`, `max_test_percentual: 20`, `max_versions_to_keep: 10`, `operation_timeout_seconds: 30`, `alert_rollbacks_threshold: 2`, `alert_policy_violations_threshold: 1`
- Flags em `config/feature_flags.yaml`: `s34_flow_multidomain_enabled`, `s34_flow_console_history_enabled`, `s34_flow_rollout_test_enabled`
