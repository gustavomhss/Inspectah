# Bloco 3 — Casos de uso e bordas
- Caso feliz: start canary → métricas ok → promo → timeline registrada.
- Borda: hash divergente → bloqueio imediato, alerta drift.
- Borda: actor ausente → 4xx + log de tentativa.
- Borda: SLO breach simulado → alert firing, promoção bloqueada, rollback permitido; registro de `slo_breach` e `policy_violation`.
- Borda: rollout duração excedida → erro e rollback recomendado.
