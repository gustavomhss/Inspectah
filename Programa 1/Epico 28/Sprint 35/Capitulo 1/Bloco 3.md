# Bloco 3 — Objetivos e estados-alvo (testáveis)
- **Rollout governado:** canary/teste percentual iniciados via API/Console, com limites/flags, critérios automáticos de promoção/rollback e auditoria completa (`flow_id`, `flow_version_id`, `operation_id`).
- **Catálogo versionado/assinado:** `config/flow_catalog/*.yaml` com hash/assinatura; CLI/CI para publicar/validar/sincronizar; divergência derruba gate.
- **Contratos expostos:** `flow_version_id` + políticas enviadas para lógica/Truth (E40.5) e usadas em OracleOps (labels/filters).
- **OracleOps v3:** painel e alertas por modo (teste/canary/ativo), diffs de versão, timeline de promoções/rollback, SLO/incident por experimento.
