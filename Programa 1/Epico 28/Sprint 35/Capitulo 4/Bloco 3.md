# Bloco 3 — Cenários de teste por gate (G0–G4)
- **G0:** varredura 9×4 sem TODO/FIXME; catálogo assinado + hash calculado; `bin/s35_bundle.sh` gera manifest e comparação publish/runtime.
- **G1:** migração aplica em DB limpo e existente; limites aplicados; testes negativos: `max_canary_duration` estourado → erro; `max_test_percentual` > limite → erro; operação sem actor → erro; catálogo drift → erro.
- **G2:** console/API start/promo/rollback com actor obrigatório; casos negativos (sem actor, hash divergente, limite violado) retornam 4xx e logam auditoria; casos positivos gravam operação e evento OracleOps/Truth; UI exibe diffs/hash.
- **G3:** métricas expostas (curl + promtool) com labels corretos; painel não vazio; alertas disparam via simulação (rollback/policy_violation); evidência de firing/resolution salva.
- **G4:** pilotos reais news_v2/contestacao_v0 via API/UI; rollback + promoção; hash publish vs runtime conferido; alerta disparado e `slo_breach` registrado; placeholders/datasets duplicados causam FAIL explícito.
