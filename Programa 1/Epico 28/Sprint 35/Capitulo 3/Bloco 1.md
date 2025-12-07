# Bloco 1 — Backend (rollout, catálogo, políticas)
- **Migração `0036_s35_flow_governance_advanced.py`:** campos para mode/test_percentual, deadlines (`rollout_deadline_at`), `catalog_hash`, `operation_id`, `actor`, `slo_status`, registro `slo_breach`, contadores de rollback/violações.
- **Rollout (`app/flows/rollout.py`/`service.py`):** inicia canary/teste, aplica limites (tempo, percentual, rollbacks/h), bloqueia promoção se SLO/alerta negativo ou hash divergente; registra auditoria completa e métricas.
- **Catálogo (`app/flows/catalog.py`):** carrega `config/flow_catalog/*.yaml`, valida schema, calcula hash/assinatura, compara com publish; recusa drift e grava `flow_catalog_hash_mismatch_total`.
- **Políticas (`policy_engine.py`):** aplica políticas por modo e domínio; produz eventos de violação para logs/métricas; integra com SLO (s35_slos.md).
- **Invariantes:** toda operação inclui `flow_id`, `flow_version_id`, `mode`, `operation_id`, `actor`, `catalog_hash`; promoção/rollback só com critérios atendidos e SLO verde; drift de catálogo falha operação.
