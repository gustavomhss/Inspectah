# Inspectah — Sprint 35 — Capítulo 4
## Escopo Funcional & Requisitos por Área (Rollout governado real)

### 4.1 Backend / Domínio de Fluxos
- Modos `teste`, `canary`, `ativo` persistidos com deadlines; `operation_id`, `actor`, `catalog_hash` obrigatórios.
- Serviço de rollout aplica limites (`max_test_percentual`, `max_rollbacks_per_hour`, `max_canary_duration_minutes`, `operation_timeout_seconds`) e bloqueia promoção se SLO/alerta negativo ou drift de catálogo.
- Catálogo: carregar/validar `config/flow_catalog/*.yaml` (hash/assinatura); comparar publish vs runtime; gravar `flow_catalog_hash_mismatch_total` e recusar operação se divergir.
- Políticas: engine retorna violações e alimenta métricas/alertas; integra SLOs de s35_slos.md.
- Integração ops/Truth: eventos com `flow_id`, `flow_version_id`, `mode`, `operation_id`, `actor`, `catalog_hash`, `slo_status`; registra `slo_breach` em log/métrica.

### 4.2 APIs e Contratos
- Rotas REST:
  - `GET /api/flows/catalog` (entries com hash/assinatura/published_at).
  - `POST /api/flows/{id}/rollout|promote|rollback` (actor obrigatório; recusa hash divergente; retorna estado + auditoria).
  - `GET /api/flows/{id}/rollout/status` (estado, métricas/alertas ativos, drift, deadlines).
- Payloads incluem `flow_id`, `flow_version_id`, `mode`, `operation_id`, `catalog_hash`, `actor`; erros padronizados e logados.
- Contratos expõem `flow_version_id` + políticas para Truth/OracleOps; labels de métricas/logs usam `{flow_id,flow_version_id,mode}`.

### 4.3 Observabilidade e SLO/alertas
- Métricas reais expostas: `flow_rollout_*`, `flow_exec_*`, `flow_policy_violations_total`, `flow_catalog_hash_mismatch_total`, `flow_rollout_duration_seconds`, `inspectah_flow_slo_breach_total`.
- Alertas de s35_slos.md implementados; promtool + firing simulado; painel `s35_flow_rollout_overview` com dados de news_v2 e contestacao_v0.
- `bin/s35_g3_obs.sh` roda smoke de métricas/alertas; falha se séries vazias ou alerta não dispara.

### 4.4 Pilotos, CI e evidências
- Pilotos via API/UI (sem SQLite local): news_v2 e contestacao_v0, com rollback e promoção; uso de catálogo publicado; comparação de hash; captura de métricas/alertas; screenshots reais.
- `bin/s35_g4_pilotos.sh` detecta placeholders/datasets duplicados; grava `slo_breach` simulado.
- CI `s35-gates.yml`: roda unit + negativos (limites, actor ausente), smoke HTTP, promtool, pilotos controlados (modo headless), geração de `inspectah_s35_evidence_bundle.zip`.
- Evidências: logs estruturados, JSONs de exec/status, prints de painel/alert firing, hash publish vs runtime, scorecards S35_G*_*.json.

### 4.3 Observabilidade, Dados e CI/ORR
- Métricas/logs/alertas específicos de rollout (ver Cap.2.3).
- Painel `s35_flow_rollout_overview` com execuções por modo, rollbacks, violações de política, SLO, diffs de catálogo, timeline de operações.
- Alertas em `observability/alerts/s35/*.yaml`; SLOs rollout em `Programa 1/Sprint 35/s35_slos.md`.
- Scripts de gates (`bin/s35_g0..g5.sh`), `metrics_summary`, `bundle`; workflow `.github/workflows/s35-gates.yml`.
- Evidências depositadas em `out/evidence/S35_*` + bundle com scorecards e dumps (`exec_dump.json`, `rollout_timeline.json`, screenshots).

### 4.4 Frontend / Console (OracleOps v3)
- Superfícies: lista multi-fluxo com estado de rollout e hash de catálogo; painel de rollout por fluxo (status, percentuais, critérios, SLO/alertas); timeline de promoções/rollback; modal para iniciar canary/teste; diffs de versão/catálogo.
- Estados: catálogo OK vs drift; modo ativo vs canary/teste; promoção bloqueada por SLO/alerta; rollback em andamento; operação concluída.
- Ações: iniciar canary/teste (com confirmação), promover (após checagens), rollback (com razão), baixar evidências (exec_dump, timeline).

### 4.5 Operação 24/7, Segurança e Perf
- Runbooks para canary/teste/promoção/rollback, catálogo, incidentes de rollout (ver Cap.5).
- Perf/perf percebida: operações de rollout respondem < 3s; UI com feedback imediato e polling curto; limites evitam degradação por retries.
- Segurança: RBAC por rota/ação; auditoria de todas as operações; feature flags para desativar rollout e catálogo enforcement em emergência.
