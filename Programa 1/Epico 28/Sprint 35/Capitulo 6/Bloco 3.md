# Bloco 3 — Exemplos de aplicação das referências
- **Argo Rollouts:** usar métricas + threshold como critério automático; timeline semelhante para promo/rollback.
- **Flagger:** alerta de rollbacks sucessivos → desliga canary; replicar via `max_rollbacks_per_hour`.
- **LaunchDarkly:** cada operação tem `operation_id` + hash de config; copiar para catálogo/rollout.
- **AdmissionControls:** toda promoção valida hash/assinatura; exemplo de bloqueio em drift.
- **SLO by mode:** separar painéis/alertas `mode=canary` vs `mode=ativo` para evitar ruído.
