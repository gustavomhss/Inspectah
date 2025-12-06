# Runbook — Incidentes Multi-fluxo (S34)

## Objetivo
Tratar incidentes relacionados aos fluxos governados (notícias v2, contestação v0) com rastreabilidade por `flow_id/flow_version_id`.

## Detecção
- Alertas Prometheus: `observability/alerts/s34/` (policy_violations, rollbacks, slo_breach).
- Cockpit: `/api/ops/cockpit/flows` retorna SLO/status por fluxo/versão.
- Logs estruturados: `flow_policy_violation`, `flow_rollback`, `flow_slo_breach` em app/flows/instrumentation.

## Abertura
1) Identificar componente no mapa: `s34_components_map.yaml` (ex.: `flow_news_v2`, `flow_contestacao_v0`).
2) Criar incidente via IncidentService (DB `out/databases/s34_ops.sqlite`) ou rota cockpit:
   - payload: id, title, severity, component_id, slo_ids, description, flow_id/flow_version_id no texto.

## Triage
- Confirmar SLO afetado (s34_slo_*), coletar métricas do painel `s34_flow_ops_overview`.
- Verificar execuções em `/api/flows/{id}/executions` com `flow_version_id` correto.
- Checar políticas/rollback recentes em `/api/flows/{id}/ops`.

## Mitigação
- Ajustar estado do fluxo (`em_teste` com percentual menor) ou executar rollback seguro (ver runbooks de cada fluxo).
- Se política violada, revisar template/policies antes de reativar.

## Resolução/Encerramento
- Documentar causa raiz, versão impactada e evidências (metrics/logs/screenshots).
- Atualizar incidente para RESOLVED/CLOSED em IncidentService.
- Gerar evidência em `out/evidence/S34_G4_pilotos_multifluxo/console_screenshots/` se UI usada.

## Escalonamento
- Severidade HIGH/CRITICAL → acionar squad Fluxos & Operação 24/7.
