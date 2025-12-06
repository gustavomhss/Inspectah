# Bloco 2 — Estrutura dos riscos/trade-offs
- **Riscos operacionais:** canary sem limites, rollback lento, drift de catálogo, métricas sem labels.
- **Riscos de integração:** ausência de `flow_version_id`/políticas nos contratos de lógica/Truth; labels faltantes em incidentes.
- **Riscos de governança:** promoção sem dados reais, bloqueios relaxados por flags, auditoria incompleta.
- **Trade-offs chave:** simplicidade do rollout vs automação; bloqueios agressivos vs throughput de releases; assinatura CLI/CI vs editor visual; verbosidade de observabilidade vs custo.
- **Gatilhos de mitigação:** limites/flags configurados, hash/assinatura obrigatórios, SLO/alertas por modo, runbooks ensaiados, bundle obrigatório.
