# Bloco 2 — Dores e Contexto
- Apenas o fluxo de notícias está governado; não há templates multi-domínio nem políticas por tipo de entrada (contestação, oficial).
- OracleOps (S33) não referencia `flow_id/flow_version_id` em SLOs/incident; cockpit não enxerga estado de versão/política.
- Observabilidade de fluxo é parcial: métricas/logs sem agregação multi-fluxo, alertas não discriminam versões/teste.
- Runbooks e evidências são monofluxo; rollback/teste e coleta de payloads não estão padronizados entre fluxos.
