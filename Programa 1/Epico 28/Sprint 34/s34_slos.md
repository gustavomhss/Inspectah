# S34 — SLOs priorizados (multi-fluxo governável)

IDs e métricas alinhados ao mapa de componentes S34. Todos referenciam `flow_id` e `flow_version_id`.

## s34_slo_exec_latency_news_v2
- descricao: Latência p95 das execuções do fluxo news_v2.
- metrica: `flow_exec_latency_seconds{flow_id="news_v2",flow_version_id="v2",quantile="0.95"}`
- limiar: `<= 45` segundos
- janela: 30m
- alerta: `alert_flow_exec_latency_news_v2_p95` (threshold 45s, canal #ops)
- componentes: [`flow_news_v2`]

## s34_slo_policy_violations_news_v2
- descricao: Violações de política por versão do fluxo news_v2.
- metrica: `flow_policy_violations_total{flow_id="news_v2",flow_version_id="v2"}`
- limiar: `== 0` violações na janela
- janela: 15m
- alerta: `alert_flow_policy_violations_news_v2` (threshold >0, canal #ops)
- componentes: [`flow_news_v2`]

## s34_slo_rollback_rate_news_v2
- descricao: Rollbacks acionados no fluxo news_v2.
- metrica: `flow_rollback_total{flow_id="news_v2",flow_version_id="v2"}`
- limiar: `<= 1` rollback/1h
- janela: 1h
- alerta: `alert_flow_rollback_news_v2` (threshold >1, canal #ops)
- componentes: [`flow_news_v2`]

## s34_slo_exec_latency_contestacao_v0
- descricao: Latência p95 do piloto contestacao_v0.
- metrica: `flow_exec_latency_seconds{flow_id="contestacao_v0",flow_version_id="v0",quantile="0.95"}`
- limiar: `<= 90` segundos
- janela: 30m
- alerta: `alert_flow_exec_latency_contestacao_v0_p95` (threshold 90s, canal #ops)
- componentes: [`flow_contestacao_v0`]

## s34_slo_policy_violations_contestacao_v0
- descricao: Violações de política no piloto contestacao_v0.
- metrica: `flow_policy_violations_total{flow_id="contestacao_v0",flow_version_id="v0"}`
- limiar: `== 0` violações na janela
- janela: 15m
- alerta: `alert_flow_policy_violations_contestacao_v0` (threshold >0, canal #ops)
- componentes: [`flow_contestacao_v0`]

## s34_slo_rollback_rate_contestacao_v0
- descricao: Rollbacks no piloto contestacao_v0.
- metrica: `flow_rollback_total{flow_id="contestacao_v0",flow_version_id="v0"}`
- limiar: `<= 1` rollback/1h
- janela: 1h
- alerta: `alert_flow_rollback_contestacao_v0` (threshold >1, canal #ops)
- componentes: [`flow_contestacao_v0`]

## s34_slo_disponibilidade_console
- descricao: Disponibilidade do console/API multi-fluxo.
- metrica: `http_request_success_rate{service="api_flow_console"}`
- limiar: `>= 0.995`
- janela: 1h
- alerta: `alert_disponibilidade_api_flow_console` (threshold <0.995, canal #ops)
- componentes: [`api_flow_console`]

## s34_slo_freshness_obs_panel
- descricao: Atualização do painel `s34_flow_ops_overview`.
- metrica: `dashboard_freshness_seconds{panel="s34_flow_ops_overview"}`
- limiar: `<= 300` segundos
- janela: 15m
- alerta: `alert_freshness_s34_flow_ops_overview` (threshold >300s, canal #ops)
- componentes: [`observabilidade_flow_ops`]
