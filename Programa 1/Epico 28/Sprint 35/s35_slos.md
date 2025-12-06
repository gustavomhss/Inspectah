# S35 — SLOs rollout governado (news_v2, contestacao_v0)

IDs e métricas alinhados a fluxo/versão/mode. Usar em painéis, alertas e scripts G3/G4/G5.

## s35_slo_rollout_duration_news_v2
- descricao: Duração de rollout/canary do fluxo news_v2.
- metrica: `flow_rollout_duration_seconds{flow_id="news_v2",flow_version_id="v2.1.0",mode="canary"}`
- limiar: `<= 2700` segundos (45m)
- janela: 1h
- alerta: `alert_rollout_duration_news_v2_canary` (threshold >2700s, canal #ops)
- componentes: [`flow_news_v2`]

## s35_slo_policy_violations_news_v2
- descricao: Violações de política durante rollout do fluxo news_v2.
- metrica: `flow_policy_violations_total{flow_id="news_v2",flow_version_id="v2.1.0",mode="canary"}`
- limiar: `== 0` violações na janela
- janela: 15m
- alerta: `alert_policy_violation_news_v2_canary` (threshold >0, canal #ops)
- componentes: [`flow_news_v2`]

## s35_slo_rollback_rate_news_v2
- descricao: Rollbacks no rollout governado do fluxo news_v2.
- metrica: `flow_rollout_rollback_total{flow_id="news_v2",flow_version_id="v2.1.0",mode="canary"}`
- limiar: `<= 2` rollbacks/1h
- janela: 1h
- alerta: `alert_rollout_rollback_news_v2` (threshold >2, canal #ops)
- componentes: [`flow_news_v2`]

## s35_slo_rollout_duration_contestacao_v0
- descricao: Duração de rollout/teste percentual no piloto contestacao_v0.
- metrica: `flow_rollout_duration_seconds{flow_id="contestacao_v0",flow_version_id="v0.1.0",mode="test"}`
- limiar: `<= 3600` segundos (60m)
- janela: 1h
- alerta: `alert_rollout_duration_contestacao_v0_test` (threshold >3600s, canal #ops)
- componentes: [`flow_contestacao_v0`]

## s35_slo_policy_violations_contestacao_v0
- descricao: Violações de política no piloto contestacao_v0 durante rollout/teste.
- metrica: `flow_policy_violations_total{flow_id="contestacao_v0",flow_version_id="v0.1.0",mode="test"}`
- limiar: `== 0` violações na janela
- janela: 15m
- alerta: `alert_policy_violation_contestacao_v0_test` (threshold >0, canal #ops)
- componentes: [`flow_contestacao_v0`]

## s35_slo_rollback_rate_contestacao_v0
- descricao: Rollbacks no piloto contestacao_v0 em rollout/teste.
- metrica: `flow_rollout_rollback_total{flow_id="contestacao_v0",flow_version_id="v0.1.0",mode="test"}`
- limiar: `<= 2` rollbacks/1h
- janela: 1h
- alerta: `alert_rollout_rollback_contestacao_v0` (threshold >2, canal #ops)
- componentes: [`flow_contestacao_v0`]

## s35_slo_disponibilidade_console_rollout
- descricao: Disponibilidade do console/API de rollout governado.
- metrica: `http_request_success_rate{service="api_flow_console_rollout"}`
- limiar: `>= 0.995`
- janela: 1h
- alerta: `alert_disponibilidade_api_flow_console_rollout` (threshold <0.995, canal #ops)
- componentes: [`api_flow_console`]

## s35_slo_freshness_rollout_panel
- descricao: Atualização do painel `s35_flow_rollout_overview`.
- metrica: `dashboard_freshness_seconds{panel="s35_flow_rollout_overview"}`
- limiar: `<= 300` segundos
- janela: 15m
- alerta: `alert_freshness_s35_flow_rollout_overview` (threshold >300s, canal #ops)
- componentes: [`observabilidade_flow_rollout`]
