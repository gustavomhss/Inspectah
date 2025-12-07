# Bloco 3 — Objetivos testáveis
- Limites aplicados: `max_canary_duration`, `max_test_percentual`, `max_rollbacks_per_hour`, `operation_timeout_seconds` bloqueiam operações; casos negativos cobertos.
- SLO/alerta vivo: métricas `inspectah_flow_*` expostas; alertas disparam; `slo_breach` registrado em log/métrica.
- Catálogo assinado: hash publish vs runtime comparado; drift = erro + alerta + bloqueio.
- RBAC/auditoria: actor obrigatório; logs incluem `flow_id/flow_version_id/mode/operation_id/actor/catalog_hash`.
- Pilotos reais: API/UI com rollback/promo; screenshots reais; bundle sem placeholders.
