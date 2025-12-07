# Bloco 2 — Estrutura de fluxo
- Entrada: operador autenticado + catálogo publish hash + s35_slos.md.
- Passos: valida hash/limites → inicia canary/teste → monitora métricas/alertas → decide promo/rollback → registra eventos/auditoria → atualiza painel/bundle.
- Saídas: estado atualizado (mode), logs/metrics com labels, alertas firing/resolution, evidências armazenadas.
