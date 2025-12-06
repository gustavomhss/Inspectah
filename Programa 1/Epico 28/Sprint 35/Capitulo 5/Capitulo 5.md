# Inspectah — Sprint 35 — Capítulo 5
## Fluxos & Jornadas (Operadores, Fluxos, OracleOps, Lógica/Truth)

### 5.1 Jornada 1 — Iniciar canary/teste percentual
1) Operador abre OracleOps (lista multi-fluxo) → vê fluxo `fluxo_noticias_v2` com status `ativo`, hash de catálogo OK.  
2) Clica em “Iniciar canary/teste” → dialog (`FlowRolloutDialog`) preenche defaults do catálogo (percentual, critérios, duração).  
3) Operador ajusta percentuais/critério e confirma (RBAC) → API cria `operation_id`, grava auditoria e liga alertas.  
4) OracleOps mostra estado `canary`, percentuais, progresso e SLO/alertas ao vivo. Logs/metrics começam a marcar mode=canary.

### 5.2 Jornada 2 — Promoção ou rollback governado
1) Com canary em andamento, painel exibe SLO/alertas/diffs; operador vê timeline de execuções e violações.  
2a) **Promoção:** critério atende; botão “Promover” habilita; operação grava auditoria, atualiza `mode=ativo`, encerra canary e anexa timeline ao bundle.  
2b) **Rollback:** alerta/SLO breach; botão “Rollback” exige razão; operação marca `rollback` com `operation_id` e retorna fluxo ao modo anterior; bundle registra evento.  
3) OracleOps exibe badges de sucesso/rollback, atualiza hash de catálogo e timeline.

### 5.3 Jornada 3 — Catálogo e drift
1) Arquiteto publica novo catálogo via CLI/CI (`bin/s35_catalog_publish.sh`) → hash/assinatura salvos.  
2) Operador vê na lista badge “Drift detectado” se runtime != publicado; promoção fica bloqueada e alerta dispara.  
3) Operador aciona “Sincronizar catálogo” (quando permitido) ou abre runbook para corrigir; gates G1/G3 falham se drift persistir.

### 5.4 Jornada 4 — Integração com lógica/Truth (E40.5)
1) Execução de fluxo inclui `flow_version_id` e políticas; lógica/Truth consome dados e pode contestar.  
2) OracleOps e incidentes mostram labels por `flow_version_id/mode`; operador correlaciona incidentes de lógica com experimentos de rollout.  
3) Em caso de incidente, operador segue runbook de rollback/flags; evidências (exec_dump, timeline) são anexadas para Truth/Conselho.

### 5.5 Jornada 5 — Pilotos obrigatórios
- **Notícias:** canary 10–20% com critérios de latência e violação de política; promoção/rollback registrados; dataset e logs guardados.  
- **Contestação v0:** modo controlado, percentuais menores; exige confirmação dupla; rollback padrão; integração com Truth apenas via IDs.
