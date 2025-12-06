# Inspectah — Sprint 35 — Capítulo 4
## Escopo Funcional & Requisitos por Área (Rollout governado + Catálogo)

### 4.1 Backend / Domínio de Fluxos
- Suportar modos `teste`, `canary`, `ativo` em entidades de fluxo/execução (campos rollout_state, test_percentual, criteria, operation_id).
- Serviço de rollout: iniciar/monitorar/promover/rollback, validando limites (`max_test_percentual`, `max_rollbacks_per_hour`, `max_canary_duration_minutes`) e políticas.
- Catálogo: carregar/validar `config/flow_catalog/*.yaml` (hash/assinatura), expor API interna para diff runtime vs publicado, bloquear promoção em caso de drift.
- Políticas: engine para aplicar políticas por domínio e modo; retornar violações para API/Console e para alertas.
- Integração ops: registrar auditoria, enviar eventos para métricas/logs e para lógica/Truth com `flow_version_id`.

### 4.2 APIs e Contratos
- Rotas REST:
  - `GET /api/flows/catalog` (lista entradas, hash/assinatura, versões).
  - `POST /api/flows/{id}/rollout` (inicia teste/canary com critérios/percentual).
  - `POST /api/flows/{id}/promote` (promove se critérios/SLO ok).
  - `POST /api/flows/{id}/rollback` (rollback com razão).
  - `GET /api/flows/{id}/rollout/status` (estado, métricas, alertas, drift de catálogo).
- Payloads sempre incluem `flow_id`, `flow_version_id`, `mode`, `operation_id`, `catalog_hash`, `actor`; RBAC aplicado; erros padronizados.
- Contratos expõem `flow_version_id` + políticas a lógica/Truth (E40.5) e OracleOps (labels em métricas/logs).

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
