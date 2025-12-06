# Bloco 2 — APIs e Schemas
- **Rotas principais (`app/api/flow_console_routes.py`):**
  - `GET /api/flows` (filtros: domínio, estado, health, versão).
  - `GET /api/flows/{id}/versions` e `GET /api/flows/{id}/versions/{version_id}` (detalhe + diff + políticas aplicadas + SLO status).
  - `POST /api/flows/{id}/versions/{version_id}/rollback` (valida limites/flags/políticas).
  - `POST /api/flows/{id}/state` (muda estado/teste/percentual).
  - `GET /api/flows/{id}/ops` (histórico de operações + incident/SLO refs).
- **Schemas (`app/flows/schemas.py`):**
  - `FlowTemplate`, `FlowVersion`, `FlowPolicy`, `FlowOperation`, `FlowOpsStatus`.
  - Campos mínimos: `flow_id`, `flow_version_id`, `domain`, `state`, `policies`, `test_percentual`, `slo_status`, `incident_ids`.
- **Payload exemplo (template YAML)**
  ```yaml
  flow_id: fluxo_noticias_v2
  domain: noticias
  version: 2
  state: em_teste
  stages:
    - ordem: 1
      tipo: interpretacao
      agent_ref: agent_interpreter_v2
    - ordem: 2
      tipo: classificacao
      agent_ref: agent_classifier_v3
  policies:
    min_confidence: 0.72
    max_latency_ms: 8000
    block_on_missing_entities: true
  ops_profile:
    slo_id: slo_noticias_latency
    incident_severity_default: medium
    test_percentual: 15
  ```
- **Respostas** incluem `diff_summary`, `policy_checks`, `slo_status` e `ops_links` (alertas/incident IDs).
