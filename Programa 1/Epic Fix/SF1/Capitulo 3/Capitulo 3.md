# SF1 — Capítulo 3 — Arquitetura & Domínios

## 3.1 Filemap principal
- Backend: `app/flows/{service.py,rollout.py,catalog.py,policy_engine.py,ops_integration.py,logs.py,instrumentation.py}`, `app/flows/models.py` (migração 0036).
- Config: `config/flow_catalog/*.yaml` (adicionar `newsdata_br_v1.yaml`, `contestacao_newsdata_v1.yaml`), `config/flows_limits.yaml`, `config/feature_flags.yaml`.
- APIs: `app/api/flow_console_routes.py`, schemas em `app/flows/schemas.py`.
- Observabilidade: `observability/dashboards/s35_flow_rollout_overview.json`, `observability/alerts/s35/*.yaml`, `bin/s35_g3_obs.sh`.
- Scripts gates: `bin/s35_g0_scope.sh`, `bin/s35_g1_model.sh`, `bin/s35_g2_console.sh`, `bin/s35_g3_obs.sh`, `bin/s35_g4_pilotos.sh`, `bin/s35_metrics_summary.sh`, `bin/s35_bundle.sh`.
- Frontend: `frontend/inspectah-ui/src/features/flows/{FlowRolloutPanel.tsx,FlowRolloutDialog.tsx,FlowListMulti.tsx,FlowDetailMulti.tsx,FlowVersionHistory.tsx}`.
- Bundles/evidência: `out/evidence/S35_*`, `out/scorecards/S35_*`, `inspectah_s35_evidence_bundle.zip`.

## 3.2 Invariantes arquiteturais
- Operações exigem `actor`, `operation_id`, `catalog_hash`; ausência falha cedo.
- Hash publish/runtime comparado em toda operação; drift bloqueia e gera métrica/alerta.
- Métricas com labels `{flow_id,flow_version_id,mode}`; alertas definidos e testados.
- Eventos OracleOps/Truth incluem flow/mode/version/actor/catalog_hash; `slo_breach` logado; rollback/promo com policy_violation mapeados.
- UI deve consumir estados de rollout sem dependência de mocks; renders devem refletir hash/alertas em tempo quase real (polling curto).
- Templates: usar/estender template HTTP/JSON se existir em `config/flow_templates`; senão, criar template para newsdata.io `latest` com mapeamento `results[*]`.
