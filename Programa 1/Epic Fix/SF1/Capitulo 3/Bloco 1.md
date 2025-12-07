# Bloco 1 — Backend
- Migração 0036: deadlines, catalog_hash, actor, operation_id, slo_status/slo_breach, contadores de rollback/violações.
- Service/rollout aplica limites; bloqueia promo/rollback em SLO/alerta negativo ou drift.
- Catalog carrega YAML assinado (incluindo `newsdata_br_v1.yaml`, `contestacao_newsdata_v1.yaml`), calcula hash, compara publish/runtime; recusa drift.
- Policy engine integra s35_slos.md; gera eventos/metrics de violação.
