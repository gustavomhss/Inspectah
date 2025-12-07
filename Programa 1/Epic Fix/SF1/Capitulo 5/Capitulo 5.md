# SF1 — Capítulo 5 — Fluxos & Jornadas

## Jornadas chave
- J1 Iniciar canary/teste: actor obrigatório; hash conferido; alertas armados; auditoria e métricas registradas.
- J2 Promoção governada: SLO/alertas verdes, hash ok → promo; evento OracleOps/Truth; timeline atualizada.
- J3 Rollback: SLO breach/alerta/limite violado → rollback com razão; alerta firing; auditoria completa.
- J4 Drift catálogo: hash diverge → bloqueio, alerta `catalog_hash_drift`, runbook acionado.
- J5 Simulação SLO breach: script eleva rollback/policy_violation; alerta dispara; `slo_breach` logado; promoção bloqueada; rollback permitido.
