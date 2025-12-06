# Bloco 2 — Dores, restrições e dependências
- **Governança fraca:** canary/teste percentual sem limites, alertas ou trilha; rollback manual → risco de incidente.
- **Catálogo ad hoc:** templates/políticas não versionados nem assinados; ambientes divergem.
- **Observabilidade cega:** OracleOps não separa modo (teste/canary/ativo) nem mostra diffs/rollbacks; Conselho não tem visibilidade para GO/NO-GO.
- **Contratos incompletos:** lógica/Truth (E40.5) exige `flow_version_id` e políticas expostas; hoje fluxos não entregam.
- **Dependências:** S34 (multi-fluxo base), E26 (Console/Admin gramática), E40.5 (lógica/verdade), Programa 7 (observabilidade). Restrições: não mexer em lógica interna dos agentes.
