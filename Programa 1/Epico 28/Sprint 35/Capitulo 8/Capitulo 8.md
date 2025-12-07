# Inspectah — Sprint 35 — Capítulo 8
## Frontend Engineering (OracleOps v3 — Bret Victor captain)

### 8.1 Superfícies e rotas
- **FlowListMulti** (`/flows`): tabela de fluxos com colunas `flow`, `mode`, `% canary`, `health/SLO`, `catalog_hash badge`, `last operation`, ações rápidas (iniciar canary/teste, abrir painel).
- **FlowRolloutPanel** (`/flows/{id}/rollout`): estado atual (mode, percentuais, critérios, SLO/alertas), hash de catálogo, timeline de operações, diffs de versão.
- **FlowRolloutDialog** (modal): iniciar canary/teste com percentuais/defaults do catálogo; confirmação; mostra limites ativos.
- **FlowVersionHistory**: lista versões + diffs de catálogo/políticas; links para evidências e timeline.

### 8.2 Dados e estados a representar
- Labels fixos: `flow_id`, `flow_version_id`, `mode` (teste/canary/ativo), `operation_id`, `catalog_hash`, `actor`, `started_at`, `duration`, `slo_status`, `alerts`, `policy_violations`.
- Estados principais:
  - `mode=ativo` (verde, catálogo em dia)
  - `mode=canary` ou `teste` (amarelo/azul, mostra percentuais e tempo restante)
  - `promotion_blocked` (alerta/SLO ou drift)
  - `rollback_in_progress`
  - `catalog_drift` (badge vermelho + CTA para sync)
- Dados de diffs: diferenças de catálogo (hash antigo vs novo), mudanças de políticas/percentuais, SLOs usados.

### 8.3 Interações chave
- **Iniciar canary/teste:** modal com percentuais/critério; valida limites; exige `actor` e `catalog_hash`; preview das SLO/alertas; bloqueia submissão se hash divergir.
- **Promover:** só habilita se SLO/alertas verdes e sem drift; confirma com resumo de evidências (métricas/alertas) já coletadas; envia `operation_id`.
- **Rollback:** sempre disponível em canary/teste; exige razão; feedback imediato; timeline atualiza; alerta de rollback dispara e aparece em UI.
- **Baixar evidências:** links para `exec_dump`, `rollout_timeline`, screenshots reais; export bundle.
- **Differences:** toggle para ver diffs de catálogo/políticas entre versões com hash antigo/novo.

### 8.4 Estados críticos e ergonomia
- Sempre mostrar **modo atual** + **percentual/tempo restante** quando em canary/teste; badge “actor required” se falta contexto.
- Alertas visíveis e específicos (“Drift de catálogo”, “SLO breach”, “Limite de rollback atingido”, “Actor ausente”).
- Feedback imediato pós-ação com confirmação de hash e actor; rollback/promoção refletem na tabela e painel sem reload pesado (polling curto ou websocket se disponível).
- Acessibilidade: labels de modo/alerta com texto e ícones; estados de foco/teclado; contraste 4.5:1; screenshots coletadas devem ser reais (falhar se placeholder).
