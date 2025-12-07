# Inspectah — Sprint 35 — Capítulo 1
## Contexto & Problema (P1 / E28 — Governança Avançada de Rollout de Fluxos)

### 1.1 Identidade e posição na cadeia
- **S35 — Governança Avançada de Fluxos (rollout progressivo + catálogo versionado + SLO/OracleOps/Truth)**; 7ª/7 do Épico **E28** no **Programa 1 — Consoles & Truth Ops Foundation**.
- Dono lógico: Squad Fluxos & Operação 24/7, em coordenação com Observabilidade, OracleOps e Truth/Contestação.
- Missão: fechar E28 tornando rollout de fluxos governado, auditável, com limites reais e sinais consumíveis por OracleOps/Truth — bloqueando GO falso.

### 1.2 Problema a resolver (se S35 não existir)
- GO atual é inválido: gates G3/G4 foram simulados (SQLite local, placeholders), sem API/UI/metrics reais.
- Limites críticos (`max_canary_duration`, `operation_timeout`, SLO/alert thresholds) não são aplicados; promoção/rollback pode passar mesmo com SLO quebrado.
- SLO/OracleOps ausentes: `_derive_slo_status` sempre “OK”; nenhum evento `slo_breach` registrado; Truth/OracleOps não recebem `flow_version_id/mode`.
- Observabilidade superficial: G3 só verifica arquivos/repetição de unit; alertas/painéis não são validados; métricas podem não existir.
- RBAC/auditoria opcionais: `actor` vazio permitido em operações críticas; logs incompletos.
- Pilotos G4 sintéticos: datasets duplicados, screenshots placeholders, nenhum fluxo real via API/UI/metrics.

### 1.3 Objetivos e estados-alvo (quando S35 termina)
- Rollout progressivo governado com limites aplicados (tempo, percentuais, rollbacks/h) e bloqueio automático se SLO/alerta negativo.
- Catálogo versionado/assinado carregado em runtime, com comparação de hash e rejeição de drift; CLI/CI oficial para publicar/validar.
- Contratos e eventos expõem `flow_id`, `flow_version_id`, `mode`, `operation_id`, `actor`, `catalog_hash`; OracleOps/Truth recebem eventos com `flow_id/flow_version_id/mode`.
- Observabilidade real: métricas expostas e consultadas, alertas disparados/testados, painel `s35_flow_rollout_overview` com dados reais.
- Pilotos reais (notícias v2, contestação v0) via API/UI com promo/rollback evidenciados e bundle completo (logs, métricas, screenshots reais, hashes).

### 1.4 Escopo IN / OUT
- **IN:** limites de rollout aplicados; SLO/alerta com fonte única; eventos OracleOps/Truth com flow/mode/version; RBAC obrigatório com auditoria; catálogo assinado + hash comparado; pilots reais (API/UI/metrics) para news_v2 e contestacao_v0; evidências de alerta firing e slo_breach gravado; testes negativos de limites/SLO/RBAC.
- **OUT:** editor visual avançado de fluxo; lógica interna dos agentes (Programa 2); contestação/Truth avançada além dos contratos de eventos; blockchain/blocos; multi-tenant/quotas; canary auto-adaptativo; roteamento condicional complexo.
