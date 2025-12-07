# Bloco 4 — Riscos imediatos e mitigação
- Risco: ambiente sem Prom/Alertmanager/IdP → sem evidência real. Mitigar: provisionar mínimo; se faltar, marcar NO-GO explícito.
- Risco: repetição de placeholders. Mitigar: scripts falham se detectarem fixtures duplicadas/screenshots sintéticas.
- Risco: drift não detectado. Mitigar: comparar hash publish/runtime em toda operação e em gates.
- Risco: tempo curto para pilots reais. Mitigar: executar smoke enxuto com evidências obrigatórias; nada de mock silencioso.
