# Bloco 2 — Estrutura das jornadas (passos e estados)
- **J1 Iniciar canary/teste:** lista multi-fluxo -> dialog -> criação de `operation_id` -> estado `canary` com percentuais e timers -> métricas/logs rotulados.
- **J2 Promoção/rollback:** ver painel -> checar SLO/alertas/diffs -> acionar `promote` ou `rollback` -> atualizar estado/labels -> anexar eventos ao timeline e bundle.
- **J3 Catálogo:** CLI/CI publica -> hash/assinatura -> API/Console consome -> drift? -> bloqueio + alerta + ação de sync.
- **J4 Lógica/Truth:** execução gera labels `flow_version_id`/políticas -> OracleOps mostra incidentes correlacionados -> runbook de rollback/flags se breach.
- **J5 Pilotos:** datasets preparados -> ingestão marcada com `mode` -> observação de métricas -> promoção/rollback com evidências completas.
