# Bloco 3 — Cenários de teste (mínimo para PASS)
- G1 negativos: canary_duration estourado; test_percentual > limite; rollbacks/h > limite; actor ausente; hash divergente → erro e log + métrica `flow_policy_violations_total` incrementada.
- G2: chamadas sem actor/hash → 4xx; com actor válido → sucesso e auditoria; UI reflete estado em tempo quase real (polling curto).
- G3: métricas obrigatórias ausentes ou sem labels corretos → FAIL; promtool erro → FAIL; alerta não dispara/resolvem → FAIL; painel com série vazia → FAIL.
- G4: placeholder/screenshot fake → FAIL; dataset duplicado → FAIL; ausência de `slo_breach` simulado → FAIL; hash publish/runtime divergente → FAIL.
