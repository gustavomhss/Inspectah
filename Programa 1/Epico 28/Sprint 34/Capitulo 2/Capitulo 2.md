# Inspectah — Sprint 34 — Capítulo 2
## Gates, Métricas e Invariantes (Fluxos Governáveis Multi-Domínio + OracleOps v2)

### 2.1 Gates G0–G5
- **G0 — Escopo e baseline:** 24 arquivos 6×4 fechados; templates de fluxo definidos; mapa de componentes/SLOs versão S34.
- **G1 — Modelo/Políticas multi-fluxo:** entidades/templates/migração `0034_s34_flow_multidomain_ops.py` aplicadas; políticas mínimas por domínio; limites/flags ativos.
- **G2 — Console multi-fluxo & APIs:** histórico/diffs/rollback por fluxo/versão; rotas protegidas; cockpit OracleOps exibe fluxos/versões/SLO.
- **G3 — Observabilidade & SLO:** métricas/logs/alertas por fluxo/versão/teste; painel `s34_flow_ops_overview` não vazio; SLOs versionados.
- **G4 — Pilotos notícias + contestação v0:** fluxos governados executados com rollback/teste; evidências (dataset, ingest_log, exec_dump, metrics/logs, screenshots); bundle multi-fluxo.
- **G5 — ORR:** avaliação G0–G4 + metrics_summary; GO/NO-GO com riscos/flags; documentação e runbooks testados.

### 2.2 Métricas principais
- `flow_exec_total{flow_id,flow_version_id,status}`; `flow_exec_latency_p95`; `flow_policy_violations_total`; `flow_rollback_total`.
- `flow_ops_slo_breach_total{flow_id,slo_id}`; `flow_incidents_total{flow_id,severity}`; `flow_incidents_mttr_hours`.
- Painel `s34_flow_ops_overview`: execuções por versão, violações/policy, rollbacks, SLO breaches, incident timeline.

### 2.3 Invariantes
- Toda execução registra `flow_id`, `flow_version_id`, `operation_id`.
- Rollback só permitido para versões válidas/testadas; limites/flags bloqueiam excesso.
- SLO/alerta sempre referenciam `flow_id` e componente monitorado; incidentes seguem lifecycle com trilha auditável.
