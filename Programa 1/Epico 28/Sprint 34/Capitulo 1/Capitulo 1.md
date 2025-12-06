# Inspectah — Sprint 34 — Capítulo 1
## Contexto, Problema e Objetivos (E28 — Fluxos de Agentes Configurável v1)

### 1.1 Identidade da Sprint
- **S34 — Fluxos Governáveis Multi-Domínio + OracleOps v2** (6ª/7 do Épico E28).  
- Programa 1 (Consolidação & Consoles Full); Squad: Fluxos & Operação 24/7.  
- Missão: escalar o modelo de fluxo governável (versionamento + políticas + console) para múltiplos fluxos e acoplar operação/SLO/incident ao nível de versão de fluxo.

### 1.2 Dores que a S34 ataca
- Hoje apenas um fluxo (notícias) está governado; novos fluxos (contestação/temas oficiais) carecem de templates, SLO e políticas.
- OracleOps (S33) não enxerga versão de fluxo nem políticas; incidentes/SLOs não apontam para `flow_id`/`flow_version_id`.
- Observabilidade de fluxo é parcial: não há painel multi-fluxo, nem alertas por versão/percentual de teste.
- Operação 24/7 precisa de runbooks unificados por fluxo, com evidência de rollback/teste e coleta de métricas/logs por versão.

### 1.3 Objetivos e estados-alvo
- Multi-fluxo governável: dois fluxos mínimos (notícias e contestação piloto) configurados via templates versionados, com políticas e rollback seguro.
- OracleOps v2: cockpit, incidentes e SLOs referenciam `flow_id/flow_version_id`; mapa de componentes/SLO atualizado.
- Observabilidade multi-fluxo: métricas/logs/alertas por fluxo/versão; painel `s34_flow_ops_overview` publicado e não vazio.
- Operação 24/7: runbooks e scripts por gate/fluxo; evidências completas (dataset, ingest_log, exec_dump, metrics/logs, screenshots) para ambos os fluxos.

### 1.4 Escopo IN / OUT
- **IN:** templates de fluxo (YAML/JSON) versionados; políticas mínimas por domínio; console multi-fluxo com histórico/diffs/rollback; SLOs/alertas por fluxo; integração OracleOps (incidentes/SLOs/ci-gates) com IDs de fluxo; dois pilotos (notícias, contestação v0); bundle único multi-fluxo.
- **OUT:** canary/rollout progressivo automático; editor visual avançado; lógica interna de agentes (Programa 2); Truth-DB avançado/Contestação completa; multi-tenant/quotas.
