# Bloco 4 — Riscos, rollback e decisão
- Riscos: escopo de contestação v0 inflar (mitigar com piloto isolado e flag); SLO/incident sem dados reais (G3 bloqueia); rollback corromper estado (validar versões e snapshots).
- Plano de rollback: desabilitar `s34_flow_multidomain_enabled` para isolar multi-fluxo; reverter migração se necessário (backup pré-migração); preferir correções forward.
- Matriz: **GO** (gates PASS, painel/alertas ativos, runbooks testados), **GO_WITH_WARNINGS** (gaps menores com dívidas/flags claras), **NO_GO** (falha em G2/G3/G4 ou ausência de dados reais em SLO/alerta).
