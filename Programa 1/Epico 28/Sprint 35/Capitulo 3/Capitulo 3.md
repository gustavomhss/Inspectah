# Inspectah — Sprint 35 — Capítulo 3
## Arquitetura & Domínios (Rollout governado + Catálogo)

### 3.1 Visão macro
- Domínio **Fluxos** ganha camada de governança: modos (teste/canary/ativo), políticas/limites, catálogo versionado/assinado e auditoria.
- Camadas tocadas:
  - **Persistência:** novas colunas para rollout/políticas/estado (migração 0036).
  - **Serviços:** orquestração de rollout (`rollout.py`), catálogo (`catalog.py`), versionamento (`versioning.py`), políticas (`policy_engine.py`), integração com ops (`ops_integration.py`).
  - **API/Console:** rotas para catálogo/rollout/promo/rollback + UI em OracleOps v3.
  - **Observabilidade:** métricas, logs estruturados e alertas específicos de rollout.
  - **Contratos externos:** exposição de `flow_version_id` e políticas para lógica/Truth (E40.5) e ingestão de evidências no bundle.

### 3.2 Componentes e filemap essencial
- **Backend (Python):** `app/flows/models.py`, `service.py`, `versioning.py`, `policy_engine.py`, `rollout.py`, `catalog.py`, `ops_integration.py`.
- **APIs/Schemas:** `app/api/flow_console_routes.py`, `app/flows/schemas.py`.
- **Catálogo/CLI:** `config/flow_catalog/news_v2.yaml`, `config/flow_catalog/contestacao_v0.yaml`, `bin/s35_catalog_publish.sh`, `bin/s35_catalog_validate.sh`.
- **Migration:** `migrations/versions/0036_s35_flow_governance_advanced.py`.
- **Frontend (OracleOps v3):** `frontend/inspectah-ui/src/features/flows/FlowRolloutPanel.tsx`, `FlowRolloutDialog.tsx`, `FlowListMulti.tsx`, `FlowDetailMulti.tsx`, `FlowVersionHistory.tsx`.
- **Observabilidade:** `app/flows/instrumentation.py`, `observability/dashboards/s35_flow_rollout_overview.json`, `observability/alerts/s35/*.yaml`.
- **Scripts/CI:** `bin/s35_g0_scope.sh`, `bin/s35_g1_model.sh`, `bin/s35_g2_console.sh`, `bin/s35_g3_obs.sh`, `bin/s35_g4_pilotos.sh`, `bin/s35_metrics_summary.sh`, `bin/s35_bundle.sh`, `.github/workflows/s35-gates.yml`.
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
