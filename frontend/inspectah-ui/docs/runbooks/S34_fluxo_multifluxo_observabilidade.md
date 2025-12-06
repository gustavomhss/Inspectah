# Runbook — Observabilidade Multi-fluxo (S34)

## Objetivo
Monitorar fluxos notícias v2 e contestação v0 com métricas, alertas e painel versionados (`flow_id`, `flow_version_id`).

## Métricas-chave
- `inspectah_flow_executions_total{flow_id,flow_version_id,status}`
- `inspectah_flow_latency_seconds{flow_id,flow_version_id}`
- `inspectah_flow_policy_violations_total{flow_id,flow_version_id}`
- `inspectah_flow_rollbacks_total{flow_id,flow_version_id}`
- `inspectah_flow_slo_breach_total{flow_id,flow_version_id,slo_id}`

## Painel
- `observability/dashboards/s34_flow_ops_overview.json`
  - Execuções por status
  - Latência p95 por versão
  - Violações de política
  - Rollbacks
  - SLO breaches

## Alertas (Prometheus)
- `observability/alerts/s34/policy_violations.yaml`
- `observability/alerts/s34/rollbacks.yaml`
- `observability/alerts/s34/slo_breach.yaml`
Forçar brecha: simule `record_policy_violation` ou `record_slo_breach` em dev.

## Cockpit
- `/api/ops/cockpit/flows` → retorna fluxos com SLOs/status.
- UI: painel Ops no detalhe do fluxo (FlowOpsPanel) exibe SLOs e versão ativa.

## Operação
1) Validar métricas expostas (`/metrics` se Prometheus ativo).
2) Painel não vazio → export/screenshot para evidência G3/G4.
3) Alertas firing → abrir incidente (ver runbook de incidentes).

## Evidências
- `bin/s34_g3_obs.sh` e `bin/s34_g4_pilotos.sh` produzem snapshots em `out/evidence/S34_G3_observabilidade_multifluxo` e `S34_G4_pilotos_multifluxo`.
