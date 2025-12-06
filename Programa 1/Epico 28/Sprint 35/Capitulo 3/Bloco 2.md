# Bloco 2 — APIs, Schemas e Catálogo
- **Rotas (`app/api/flow_console_routes.py`):**
  - `GET /api/flows/catalog` (lista templates/políticas, hash, versão).
  - `POST /api/flows/{id}/rollout` (inicia canary/teste; payload inclui critérios, percentuais).
  - `POST /api/flows/{id}/promote` (promove se critérios atendidos).
  - `POST /api/flows/{id}/rollback` (rollback de rollout em curso).
  - `GET /api/flows/{id}/rollout/status` (estado, métricas, alertas).
- **Schemas (`app/flows/schemas.py`):**
  - `FlowCatalogEntry` (`flow_id`, `domain`, `version`, `policies`, `hash`, `signature?`).
  - `FlowRolloutRequest` (`flow_version_id`, `mode`, `test_percentual`, `criteria`).
  - `FlowRolloutStatus` (`state`, `slo_status`, `alerts`, `policy_violations`, `canary_progress`).
- **Exemplo de entrada de catálogo (`config/flow_catalog/news_v2.yaml`):**
  ```yaml
  flow_id: fluxo_noticias_v2
  domain: noticias
  version: 2.1.0
  template_ref: config/flow_templates/news_v2.yaml
  policies:
    min_confidence: 0.72
    max_latency_ms: 8000
    block_on_missing_entities: true
  rollout_defaults:
    test_percentual: 10
    max_canary_duration_minutes: 45
    promote_on_slo_pass: true
  hash: "<sha256>"
  ```
- **Exemplo de payload rollout:**
  ```json
  {
    "flow_version_id": "v2.1.0",
    "mode": "canary",
    "test_percentual": 10,
    "criteria": {"slo_id": "slo_noticias_latency", "p95_ms_max": 2500, "breach_tolerance": 0}
  }
  ```
