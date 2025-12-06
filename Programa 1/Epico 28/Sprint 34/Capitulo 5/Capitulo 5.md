# Inspectah — Sprint 34 — Capítulo 5
## ORR, Runbooks, Flags e Rollback (Multi-fluxo governável)

### 5.1 ORR S34
- Avalia G0–G4 + `S34_metrics_summary.json` + bundle `inspectah_s34_evidence_bundle.zip`.
- GO: fluxos notícias + contestação v0 governados, com SLO/incident integrados e evidências completas.

### 5.2 Runbooks
- `docs/runbooks/S34_fluxo_noticias_ops.md` — operar/rollback/teste do fluxo de notícias.
- `docs/runbooks/S34_fluxo_contestacao_ops.md` — operar/rollback/teste do fluxo de contestação v0.
- `docs/runbooks/S34_fluxo_multifluxo_incidentes.md` — incidentes com `flow_id/flow_version_id`, severidade, escalonamento.
- `docs/runbooks/S34_fluxo_multifluxo_observabilidade.md` — métricas/logs/alertas/painel s34.

### 5.3 Flags e limites (defaults)
- `config/feature_flags.yaml`: `s34_flow_multidomain_enabled` (default true dev/test), `s34_flow_console_history_enabled`, `s34_flow_rollout_test_enabled`.
- `config/flows_limits.yaml`: `max_rollbacks_per_hour: 2`, `max_test_percentual: 20`, `max_versions_to_keep: 10`, `operation_timeout_seconds: 30`, `alert_rollbacks_threshold: 2`, `alert_policy_violations_threshold: 1`.

### 5.4 Riscos e rollback
- Risco: contestação v0 virar escopo de Truth-DB → manter piloto isolado, políticas mínimas, flag para desligar.
- Risco: SLO/incident sem dados reais → G3 não passa; tests obrigatórios com métricas/alertas disparando.
- Rollback: desabilitar `s34_flow_multidomain_enabled` para isolar multi-fluxo; preferir correções forward; backup pré-migração disponível.

### 5.5 Decisão GO/NO-GO
- **GO:** G0–G4 PASS, metrics_summary PASS, runbooks testados, flags configuradas, riscos mitigados.
- **GO_WITH_WARNINGS:** gaps menores com dívidas/flags claras; operação 24/7 sustentando fluxos governáveis.
- **NO_GO:** gates críticos FAIL; console multi-fluxo incompleto; alertas/SLO sem ligação real.
