# Inspectah — Sprint 35 — Capítulo 5
## Fluxos & Jornadas (Operadores, Observabilidade, OracleOps/Truth)

### 5.1 Jornada 1 — Iniciar canary/teste percentual (com actor obrigatório)
1) Operador (autenticado) abre Console → lista multi-fluxo mostra `news_v2` ativo, hash de catálogo = publicado, sem alertas.  
2) Clica em “Iniciar canary/teste” → dialog pré-preenche percentuais/limites do catálogo; exige `actor` e `operation_id`.  
3) AO confirmar, API valida hash vs publish, limites e SLO iniciais; grava auditoria (`flow_id`, `flow_version_id`, `mode=canary`, `actor`, `catalog_hash`) e liga alertas.  
4) Painel muda para `canary`, mostra deadline, percentuais, SLO/alertas ao vivo; métricas `flow_rollout_*` começam a registrar mode=canary.

### 5.2 Jornada 2 — Promoção governada ou rollback
1) Com canary rodando, painel exibe SLO, alertas, policy violations e timeline de execuções.  
2a) **Promoção:** SLO/alertas verdes, limites ok → botão “Promover” habilita; API compara hash novamente, grava auditoria, envia evento OracleOps/Truth e muda para `ativo`; timeline e métricas atualizadas.  
2b) **Rollback:** alerta/SLO breach ou limite estourado → botão “Rollback” exige razão; API grava `operation_id`, `actor`, registra `slo_breach` e retorna a versão anterior; alerta de rollback dispara; timeline/bundle capturam evento.

### 5.3 Jornada 3 — Drift de catálogo detectado
1) Arquiteto publica catálogo via CLI/CI (hash/assinatura salvos).  
2) Operador vê badge “Drift detectado” se runtime hash ≠ publicado; painel bloqueia promoção/start; alerta `catalog_hash_drift` dispara.  
3) Operador segue runbook: sincroniza catálogo ou abre incidente; G1/G3 falham enquanto drift persistir; bundle registra hash publish/runtime.

### 5.4 Jornada 4 — Simulação de SLO breach (teste negativo obrigatório)
1) Operador executa script de simulação (G3/G4) que eleva `flow_policy_violations_total` ou `flow_rollout_rollback_total`.  
2) Alertas disparam; painel mostra badge “SLO breach”; `ops_integration` grava evento `slo_breach` com `flow_id/flow_version_id/mode`.  
3) Operador valida que promoção fica bloqueada; rollback é permitido; evidências incluem firing/resolution + log de `slo_breach`.

### 5.4 Jornada 4 — Integração com lógica/Truth (E40.5)
1) Execução de fluxo inclui `flow_version_id` e políticas; lógica/Truth consome dados e pode contestar.  
2) OracleOps e incidentes mostram labels por `flow_version_id/mode`; operador correlaciona incidentes de lógica com experimentos de rollout.  
3) Em caso de incidente, operador segue runbook de rollback/flags; evidências (exec_dump, timeline) são anexadas para Truth/Conselho.

### 5.5 Jornada 5 — Pilotos obrigatórios
- **Notícias:** canary 10–20% com critérios de latência e violação de política; promoção/rollback registrados; dataset e logs guardados.  
- **Contestação v0:** modo controlado, percentuais menores; exige confirmação dupla; rollback padrão; integração com Truth apenas via IDs.
