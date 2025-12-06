# Bloco 4 — Decisões críticas e “como não errar”
- Runbooks obrigatórios: `S35_rollout_noticias`, `S35_rollout_contestacao`, `S35_catalogo_fluxos`, `S35_incidentes_rollout` — precisam de evidência de ensaio.
- Feature flags e limites são a rede de segurança; promoção/rollback sem respeitar `max_test_percentual`, `max_rollbacks_per_hour` ou sem SLO/alertas é FAIL de gate.
- Drift de catálogo bloqueia promoções; nunca ignorar alerta `catalog_hash_drift`.
- Integração lógica/Truth: toda requisição deve carregar `flow_version_id` e políticas; logs sem labels são bug de execução.
- GO/NO-GO depende de G4 com dados reais; “gambiarra” em ambiente sintético não substitui pilotos.
