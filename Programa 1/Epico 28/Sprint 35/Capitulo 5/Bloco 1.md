# Bloco 1 — Mapa de jornadas
- J1 Iniciar canary/teste (actor obrigatório, hash conferido) → estado e auditoria em tempo real.
- J2 Promoção/rollback governado com bloqueio se SLO/alerta negativo → timeline + bundle.
- J3 Drift de catálogo detectado → bloqueio, alerta `catalog_hash_drift`, runbook de sync.
- J4 Integração OracleOps/Truth: eventos com `flow_id/flow_version_id/mode/operation_id/actor/catalog_hash`, incluindo `slo_breach`.
- J5 Pilotos reais (news_v2, contestacao_v0) + simulação de breach/alerta com evidências reais (API/UI/metrics).
