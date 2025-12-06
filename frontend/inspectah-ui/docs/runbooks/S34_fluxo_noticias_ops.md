# Runbook — Fluxo Notícias (S34)

## Identidade
- flow_id: `flow_news_v2`
- flow_version_id: `2`
- template: `config/flow_templates/news_v2.yaml`
- políticas: pol_news_source_trust, pol_news_confidence_gate
- limites: max_rollbacks_per_hour=2, max_test_percentual=20

## Operar
1) Criar fluxo (se ainda não existir):
   - `python - <<'PY'` com FlowService: create_flow_from_template("news_v2", "Fluxo Notícias v2", "flow_news_v2")
2) Colocar em teste (até 20%):
   - `POST /api/flows/{id}/state` body `{"novo_estado":"em_teste","percentual_teste":10}`
3) Ativar:
   - `POST /api/flows/{id}/state` body `{"novo_estado":"ativo"}`

## Rollback seguro
1) Criar nova versão (se necessário) via `create_version` ou rota `/api/flows/{id}/versions/{version}/rollback`.
2) Verificar limites: rollbacks usados na última hora < 2.
3) Executar rollback: `POST /api/flows/{id}/versions/{version_id}/rollback`.

## Teste de operação
- Usar dataset de prova (notícia curta) e `FlowExecutionEngine.execute_event`.
- Verificar execuções: `/api/flows/{id}/executions`.
- Métricas esperadas: `inspectah_flow_executions_total{flow_id="flow_news_v2"}`, `inspectah_flow_latency_seconds`, `inspectah_flow_policy_violations_total`, `inspectah_flow_rollbacks_total`.

## SLO/observabilidade
- SLOs: `s34_slo_exec_latency_news_v2`, `s34_slo_policy_violations_news_v2`, `s34_slo_rollback_rate_news_v2`.
- Painel: `observability/dashboards/s34_flow_ops_overview.json`.
- Alertas: `observability/alerts/s34/policy_violations.yaml`, `rollbacks.yaml`, `slo_breach.yaml`.

## Evidências
- Executar `bin/s34_g4_pilotos.sh` para coletar:
  - `out/evidence/S34_G4_pilotos_multifluxo/dataset_noticias.json`
  - `exec_dump_news.json`, `metrics_logs_snapshot_news.txt`, `console_screenshots/`

## Incidentes
- Se violações persistirem: abrir incidente em `ops_cockpit` para componente `flow_news_v2`, vinculando SLOs.
