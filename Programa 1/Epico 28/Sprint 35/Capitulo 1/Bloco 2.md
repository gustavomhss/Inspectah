# Bloco 2 — Dores, restrições e dependências
- **Governança frágil (audit F2/F3/F5):** limites não aplicados; `_derive_slo_status` sempre OK; RBAC/actor opcional; auditoria incompleta.
- **Catálogo sem garantia (F4):** cargas locais SQLite; hashes não comparados; catálogo pode divergir do runtime sem bloquear promoção.
- **Observabilidade superficial (F1):** G3 verifica arquivos/testes repetidos; alertas e painel não exercitados; métricas podem nem existir.
- **Pilotos falsos (F4):** dataset duplicado, screenshots placeholders; nenhum tráfego API/UI real; rollbacks não exercitados.
- **Contratos externos:** OracleOps/Truth precisam de eventos com `flow_id`, `flow_version_id`, `mode`, `operation_id`, `actor`, `catalog_hash`.
- **Dependências fortes:** S34 (multi-fluxo base), E26 (console gramática), s35_slos.md (fonte única de SLO), observabilidade/alerts (dash Prometheus), IdP para actor, OracleOps/Truth listeners. Restrições: não alterar lógica interna dos agentes (Programa 2); sem blockchain/blocos.
