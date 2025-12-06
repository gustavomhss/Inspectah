# Inspectah — Sprint 35 — Capítulo 1
## Contexto & Problema (E28 — Fluxos de Agentes Configurável v1, fechamento)

### 1.1 Identidade e posição na cadeia
- **S35 — Governança Avançada de Fluxos (rollout progressivo + catálogo versionado + handoff lógica/verdade)** — 7ª/7 do Épico **E28** no **Programa 1 — Consolidação & Consoles Full**.
- Dono lógico: Squad Fluxos & Operação 24/7, em coordenação com Lógica/Truth (E40.5) e Observabilidade.
- Missão: fechar E28 tornando rollout de fluxos **governado, auditável e versionado**, com evidências para OracleOps e contratos prontos para lógica/Truth.

### 1.2 Problema a resolver (se S35 não existir)
- Multi-fluxo de S34 roda sem **rollout progressivo governado**: canary/teste percentual são manuais e sem limites, risco alto de incidente.
- Catálogo de fluxos/políticas é **manual e sem versionamento/assinatura**, gerando drift entre ambientes e perda de rastreabilidade.
- OracleOps não distingue **modo** (teste/canary/ativo) nem correlaciona eventos com `flow_version_id`; incidentes ficam opacos.
- Promoção/rollback não deixa trilha completa; Conselho não tem confiança para expandir fluxos a novos domínios.

### 1.3 Objetivos e estados-alvo (quando S35 termina)
- Rollout progressivo governado: canary/teste percentual com limites, políticas e alertas; promoção/rollback **auditável** por fluxo/versão/operation.
- Catálogo versionado/assinado de fluxos/políticas/templates (`config/flow_catalog/*.yaml`) com **CLI/CI** para publicar/validar/sincronizar ambientes.
- Contratos expõem `flow_version_id` + políticas para lógica/Truth (E40.5) e para OracleOps (SLO/incident por modo).
- OracleOps v3 exibe estado de rollout/canary, diffs por versão, timeline de promoções/rollback e SLO/alertas por experimento.

### 1.4 Escopo IN / OUT
- **IN:** rollout progressivo governado (canary/teste percentual) com limites/flags; catálogo versionado/assinado + CLI/CI; contratos com `flow_version_id` e políticas; observabilidade/alertas específicas; pilotos reais em **fluxo de notícias** e **contestação v0**; evidências/bundle completos.
- **OUT:** editor visual avançado de fluxo; lógica interna de agentes (Programa 2); Truth-DB/contestação avançada além de IDs/contratos mínimos; multi-tenant/quotas; roteamento condicional complexo; canary auto-adaptativo (fica como dívida).
