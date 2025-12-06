# Bloco 4 — Notas críticas e “como não errar”
- Não copiar complexidade de Argo/Flagger (experimentos pesados); manter UI/Admin simples e aderente a E26.
- Não pular assinatura/hash de catálogo: é a garantia de drift-zero.
- Não misturar rollout com lógica interna de agente (Programa 2); manter agente como caixa preta com ID.
- Evitar dashboards genéricos; painel precisa de labels `flow_id`, `flow_version_id`, `mode`, `operation_id`, `catalog_hash`.
- Referências servem para inspiração, não para importar dependências novas.
