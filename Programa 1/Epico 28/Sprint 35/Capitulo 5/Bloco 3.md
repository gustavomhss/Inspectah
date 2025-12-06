# Bloco 3 — Exemplos, bordas e anti-casos
- **Exemplo J1:** canary 10% notícias com critério `p95_ms <= 2500`, duração 45min; promoção automática bloqueada se alertas > 0.
- **Exemplo J2 (rollback):** alerta `policy_violation` dispara; operador confirma rollback com razão; timeline registra evento + catalog_hash; SLO volta a `ativo`.
- **Exemplo J3 (drift):** catálogo publicado hash `abc`; runtime `def`; alerta `catalog_hash_drift` abre; botão “Promover” fica desabilitado até sync.
- **Borda:** canary expira por tempo (`max_canary_duration_minutes`) → rollback automático e alerta; operação tenta usar percentual > limite → erro 400 com mensagem clara.
- **Anti-caso:** iniciar canary sem catálogo assinado ou sem `flow_version_id` válido; iniciar promoção sem SLO/alertas coletados; ocultar labels em logs/metrics.
