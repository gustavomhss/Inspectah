# Runbook — Fluxo Contestação v0 (S34)

## Identidade
- flow_id: `flow_contestacao_v0`
- flow_version_id: `0`
- template: `config/flow_templates/contestacao_v0.yaml`
- políticas: pol_contestacao_origem_obrigatoria, pol_contestacao_protecao_dados
- limites: max_rollbacks_per_hour=2, max_test_percentual=20

## Operar
1) Criar fluxo piloto:
   - FlowService: create_flow_from_template("contestacao_v0", "Contestação Piloto", "flow_contestacao_v0").
2) Rodar em modo teste (<=20%):
   - `POST /api/flows/{id}/state` body `{"novo_estado":"em_teste","percentual_teste":10}`.
3) Promover para ativo (após teste):
   - `POST /api/flows/{id}/state` body `{"novo_estado":"ativo"}`.

## Rollback seguro
1) Criar versão de teste com `create_version(..., version_id="1")`.
2) Se falha, rollback para `version_id=0` com `POST /api/flows/{id}/versions/0/rollback`.
3) Respeitar limite de 2 rollbacks/hora.

## Teste de operação
- Enviar payload estruturado (origem/cliente + texto de contestação) para `FlowExecutionEngine`.
- Conferir execuções em `/api/flows/{id}/executions`.
- Métricas: `inspectah_flow_executions_total`, `inspectah_flow_policy_violations_total`, `inspectah_flow_latency_seconds`, `inspectah_flow_rollbacks_total` com labels do fluxo.

## SLO/observabilidade
- SLOs: `s34_slo_exec_latency_contestacao_v0`, `s34_slo_policy_violations_contestacao_v0`, `s34_slo_rollback_rate_contestacao_v0`.
- Painel: `observability/dashboards/s34_flow_ops_overview.json`.
- Alertas: `observability/alerts/s34/*`.

## Evidências
- Rodar `bin/s34_g4_pilotos.sh` para coletar:
  - `out/evidence/S34_G4_pilotos_multifluxo/dataset_contestacao.json`
  - `exec_dump_contestacao.json`, `metrics_logs_snapshot_contestacao.txt`, `console_screenshots/`

## Incidentes
- Abrir incidente para componente `flow_contestacao_v0` se violações/latência extrapolarem SLO.
