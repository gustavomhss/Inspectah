# Bloco 2 — APIs, Schemas e Catálogo
- **Rotas (`app/api/flow_console_routes.py`):**
  - `GET /api/flows/catalog` → lista entries com `hash`, `signature`, `published_at`.
  - `POST /api/flows/{id}/rollout|promote|rollback` → requer `actor`, `operation_id`, `catalog_hash`; falha se hash ≠ publicado ou limites violados; grava auditoria + evento OracleOps/Truth.
  - `GET /api/flows/{id}/rollout/status` → retorna estado, deadlines, métricas/alertas ativos, últimos eventos (inclui `flow_version_id`, `mode`, `catalog_hash`).
- **Schemas (`app/flows/schemas.py`):**
  - `FlowCatalogEntry` (`flow_id`, `domain`, `version`, `template_ref`, `policies`, `rollout_defaults`, `hash`, `signature`).
  - `FlowRolloutRequest` (`flow_version_id`, `mode`, `test_percentual`, `catalog_hash`, `actor`, `operation_id`).
  - `FlowRolloutStatus` (`state`, `slo_status`, `alerts`, `policy_violations`, `canary_progress`, `deadline_at`, `catalog_hash`).
- **Exemplo de entrada de catálogo (`config/flow_catalog/news_v2.yaml`):**
  ```yaml
  flow_id: news_v2
  domain: noticias
  version: v2.1.0
  template_ref: config/flow_templates/news_v2.yaml
  policies:
    min_confidence: 0.72
    max_latency_ms: 8000
    block_on_missing_entities: true
  rollout_defaults:
    test_percentual: 10
    max_canary_duration_minutes: 45
    promote_on_slo_pass: true
  hash: "<sha256-publicado>"
  signature: "<detalhe assinatura>"
  ```
- **Exemplo de payload rollout (com actor obrigatório):**
  ```json
  {
    "flow_version_id": "v2.1.0",
    "mode": "canary",
    "test_percentual": 10,
    "catalog_hash": "<sha256-publicado>",
    "actor": "ops_user_01",
    "operation_id": "op-2025-12-06-001"
  }
  ```
