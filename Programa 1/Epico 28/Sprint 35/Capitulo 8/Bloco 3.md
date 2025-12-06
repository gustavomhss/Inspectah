# Bloco 3 — Exemplos e estados críticos
- **Estado canary ativo:** badge “canary 10% — 32m restantes”; card mostra SLO pass/alerta; botão “Promover” desabilitado até critérios OK.
- **Drift de catálogo:** badge vermelho “drift”; CTA “Sincronizar” ou abrir runbook; botão de promoção desabilitado; alerta em destaque.
- **Rollback em execução:** toast + spinner; timeline adiciona entrada; tabela marca modo retornando ao ativo; botão repetir rollback desabilitado.
- **Promoção bem-sucedida:** banner “versão v2.1 promovida” com operation_id; cards de SLO limpam; timeline atualizado.
- **Erro de limites:** tentativa de canary > `max_test_percentual` mostra erro inline; campos ressaltados com texto explicativo.
