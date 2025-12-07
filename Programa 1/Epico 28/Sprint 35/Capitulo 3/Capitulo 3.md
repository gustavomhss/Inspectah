# Inspectah — Sprint 35 — Capítulo 3
## Arquitetura & Domínios (Rollout governado + Catálogo real)

### 3.1 Visão macro
- Domínio **Fluxos** ganha governança aplicável em runtime: modos (teste/canary/ativo), limites, SLO/alertas, catálogo assinado, RBAC obrigatório e eventos para OracleOps/Truth.
- Camadas tocadas:
  - **Persistência:** migração 0036 adiciona rollout state, deadlines, hash de catálogo, auditoria (actor, operation_id), registros `slo_breach`.
  - **Serviços:** orquestração de rollout (`service.py`/`rollout.py`), política/limites (`policy_engine.py`), catálogo/hashes (`catalog.py`), versionamento (`versioning.py`), integração ops (`ops_integration.py` emitindo eventos e métricas).
  - **API/Console:** rotas seguras (actor obrigatório) para start/promo/rollback, status com diffs, UI de rollout/versões/painel.
  - **Observabilidade:** instrumentação Prometheus real + alertas + painel com dados; scripts de gates validam séries/alerts.
  - **Contratos externos:** eventos com `flow_id`, `flow_version_id`, `mode`, `operation_id`, `actor`, `catalog_hash` para OracleOps/Truth; SLOs de s35_slos.md aplicados.

### 3.2 Componentes e filemap essencial
- **Backend (Python):** `app/flows/models.py`, `service.py`, `versioning.py`, `policy_engine.py`, `rollout.py`, `catalog.py`, `ops_integration.py`, `logs.py`, `instrumentation.py`.
- **APIs/Schemas:** `app/api/flow_console_routes.py`, `app/flows/schemas.py` (actor obrigatório, hash, deadlines).
- **Catálogo/CLI:** `config/flow_catalog/news_v2.yaml`, `config/flow_catalog/contestacao_v0.yaml`, `config/flows_limits.yaml`, `config/feature_flags.yaml`, `bin/s35_catalog_publish.sh`, `bin/s35_catalog_validate.sh`, `bin/s35_bundle.sh`.
- **Migration:** `migrations/versions/0036_s35_flow_governance_advanced.py` com deadlines, hash, audit trail e logs de SLO.
- **Frontend (Console/OracleOps):** `frontend/inspectah-ui/src/features/flows/FlowRolloutPanel.tsx`, `FlowRolloutDialog.tsx`, `FlowListMulti.tsx`, `FlowDetailMulti.tsx`, `FlowVersionHistory.tsx`, componentes de auditoria e alert badges.
- **Observabilidade:** `observability/dashboards/s35_flow_rollout_overview.json`, `observability/alerts/s35/*.yaml`, scripts `bin/s35_g3_obs.sh`, `bin/s35_metrics_summary.sh`.
- **Scripts/CI:** gates `bin/s35_g0_scope.sh`, `bin/s35_g1_model.sh`, `bin/s35_g2_console.sh`, `bin/s35_g3_obs.sh`, `bin/s35_g4_pilotos.sh`; workflow `.github/workflows/s35-gates.yml` roda negativos/alertas; bundle final `inspectah_s35_evidence_bundle.zip`.
- **Evidências:** `out/evidence/S35_G*_*/`, `out/scorecards/S35_G*.json`, `out/bundles/inspectah_s35_evidence_bundle.zip`.

### 3.3 Invariantes e contratos de dados
- Toda operação de rollout grava `flow_id`, `flow_version_id`, `mode`, `operation_id`, `actor`, `catalog_hash`, timestamps e resultado.
- `flow_version_id` + políticas via API são repassados para lógica/Truth; OracleOps usa mesmas chaves em métricas/logs.
- Catálogo carregado em runtime deve corresponder ao hash/assinatura publicado; divergência gera alerta e bloqueio de promoção.
- Modos e limites (`config/flows_limits.yaml`) são validados em serviço e em scripts de gate; feature flags (`config/feature_flags.yaml`) controlam ativação.

### 3.4 Configs e limites (defaults)
- `config/flow_catalog/*.yaml` — catálogo versionado/assinado (news_v2, contestacao_v0).
- `config/flows_limits.yaml`: `max_rollbacks_per_hour: 2`, `max_test_percentual: 20`, `max_versions_to_keep: 10`, `operation_timeout_seconds: 30`, `alert_rollbacks_threshold: 2`, `alert_policy_violations_threshold: 1`, `max_canary_duration_minutes: 60`.
- `config/feature_flags.yaml`: `s35_flow_rollout_enabled`, `s35_flow_catalog_enforced`, `s35_flow_logic_contract_enabled`.
