# Bloco 2 — Estrutura e dados por componente
- **FlowListMulti:** colunas `flow`, `mode`, `% canary`, `health/SLO`, `alerts`, `catalog_hash badge`, `last operation`, ações (`start test/canary`, `open rollout`). Filtros por estado, domínio, health.
- **FlowRolloutPanel:** cards de status (modo/percentual/tempo), SLO status, alertas ativos, diffs de catálogo, badges de drift, timeline (operation_id, ação, ator, resultado, timestamps).
- **FlowRolloutDialog:** campos `percentual`, `criterio` (SLO id, p95, breach_tolerance), `duracao`, aviso de limites, resumo de políticas aplicadas.
- **FlowVersionHistory:** tabela de versões com `flow_version_id`, catalog_hash, políticas, datas, diffs; botões para ver evidências/timeline.
- **Download/Evidências:** botões para bundle e arquivos; estados de loading/erro; indicação de último refresh.
