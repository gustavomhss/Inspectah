# Bloco 1 — Mapa de escopo por área
- **Backend:** modos rollout com deadlines; engine de limites/políticas; catálogo assinado com hash comparado; `_derive_slo_status` real; eventos OracleOps/Truth; auditoria completa.
- **APIs:** catálogo/rollout/promote/rollback/status com actor obrigatório, hash requerido, erros padronizados; testes negativos para actor ausente, hash divergente, limite violado.
- **Observabilidade:** métricas/alertas por mode com labels `{flow_id,flow_version_id,mode}`; promtool + firing; painel rollout com dados reais.
- **Frontend (OracleOps v3):** lista multi-fluxo com badges de SLO/alertas/hash; dialogs com validação; timeline/diffs; bloqueio sem actor; screenshots reais.
- **CI/ORR & Evidências:** scripts `bin/s35_*`, workflow `s35-gates.yml` rodando negativos + promtool + pilotos; bundle com hashes comparados, logs, métricas, screenshots reais e scorecards.
