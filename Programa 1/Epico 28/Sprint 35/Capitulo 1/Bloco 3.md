# Bloco 3 — Objetivos e estados-alvo (testáveis)
- **Rollout governado real:** canary/teste percentual iniciados via API/Console, limites aplicados (tempo/percentual/rollbacks), bloqueio automático se SLO/alerta negativo, rollback exercitado, auditoria completa (`flow_id`, `flow_version_id`, `mode`, `operation_id`, `actor`, `catalog_hash`).
- **Catálogo versionado/assinado:** `config/flow_catalog/*.yaml` com hash/assinatura; CLI/CI para publicar/validar/sincronizar; runtime compara hash e recusa drift; evidência de hash no bundle.
- **Contratos expostos:** eventos para OracleOps/Truth contendo flow/mode/version + `operation_id` e `actor`; `_derive_slo_status` consultando SLO real e registrando `slo_breach`.
- **Observabilidade viva:** métricas `inspectah_flow_*` expostas e consultadas; alertas Prometheus disparam com simulação controlada; painel `s35_flow_rollout_overview` populado com dados reais.
- **Pilotos reais:** news_v2 e contestacao_v0 executados via API/UI; promoção e rollback registrados; evidências (logs, métricas, screenshots reais, hashes) sem placeholders.
