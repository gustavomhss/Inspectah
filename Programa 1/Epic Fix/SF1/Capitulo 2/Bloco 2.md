# Bloco 2 — Gates G2–G3
- **G2:** API/Console rollout exigem `actor`; 4xx em ausência; auditoria inclui flow/mode/version/operation_id/actor/catalog_hash; UI mostra hash/estado; casos negativos (hash drift, limite violado) evidenciados.
- **G3:** observabilidade real: `curl /metrics` + promtool; alertas simulados (rollback/policy_violation/slo_breach) disparam e resolvem; painel `s35_flow_rollout_overview` export JSON/PNG com séries não vazias.
