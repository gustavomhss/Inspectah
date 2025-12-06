# Bloco 3 — Exemplos e anti-casos UX
- **Exemplo promoção:** cartão mostra “SLO ok, alertas 0, catálogo ok” → botão “Promover” fica ativo; dialog mostra impacto e evidencia que timeline será atualizada.
- **Exemplo bloqueio:** badge de drift + tooltip “Hash publicado abc, runtime def. Rode sync”; promoção desabilitada.
- **Exemplo rollback:** toast “Rollback acionado (op-456)” + timeline; tabela marca fluxo em transição com spinner.
- **Anti-caso:** esconder operação em andamento; não mostrar motivo do bloqueio; usar apenas cor sem texto; não pedir confirmação para rollback/promoção.
