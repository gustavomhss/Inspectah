# Inspectah — Sprint 35 — Capítulo 2
## Objetivos, Gates, Métricas & DoD (Governança avançada de rollout)

### 2.1 Objetivos ↔ Gates (Matriz)
- O1 — Rollout governado com limites aplicados e bloqueio automático → **G1**, **G2**.
- O2 — Catálogo versionado/assinado carregado em runtime com hash comparado → **G0**, **G1**, **G3**.
- O3 — SLO/alerta e OracleOps/Truth integrados (eventos e métricas reais) → **G3**, **G4**.
- O4 — Pilotos reais (API/UI/metrics) com promo/rollback e bundle auditável → **G4**, **G5**.
- O5 — RBAC/auditoria obrigatórios (actor + operação) → **G2**, **G4**, **G5**.

### 2.2 Gates G0–G5 (testáveis e proibem placeholder)
- **G0 — Escopo & Catálogo blindado**
  - 9×4 completo, s35_slos.md carregado como fonte única de SLO.
  - Catálogo inicial `config/flow_catalog/*.yaml` (news_v2, contestacao_v0) assinado + hash calculado; CLI/CI `bin/s35_bundle.sh` gera manifest e comparação.
  - Falha se qualquer entry sem assinatura/hash ou se hash runtime ≠ publicado.
- **G1 — Modelo/rollout com limites aplicados**
  - Migração `0036_s35_flow_governance_advanced.py` aplicada; modos teste/canary/ativo.
  - Limites `max_canary_duration_minutes`, `operation_timeout_seconds`, `max_rollbacks_per_hour`, `max_test_percentual` aplicados e testados com casos negativos.
  - Promo/rollback bloqueiam se SLO/alerta negativo ou se catálogo diverge; evidência em logs + métrica `flow_policy_violations_total`.
  - Script `bin/s35_g1_model.sh` roda unidades felizes + negativas (tempo, percentual, ausência de actor).
- **G2 — Console/API rollout com RBAC obrigatório**
  - Rotas e UI para start/promo/rollback exigem `actor`; chamadas sem actor retornam 4xx e logam tentativa.
  - Auditoria completa (`flow_id`, `flow_version_id`, `mode`, `operation_id`, `actor`, `catalog_hash`, `request_id`); diffs/estado visíveis no console.
  - `bin/s35_g2_console.sh` inclui testes HTTP de erro (sem actor, catálogo divergente) + sucesso com evidências de auditoria.
- **G3 — Observabilidade real (sem placeholders)**
  - Métricas `inspectah_flow_*` expostas e consultadas via `curl /metrics` + `promtool`.
  - Alertas definidos para SLO/limites e simulados (forçar `flow_rollout_rollback_total` e `flow_policy_violations_total`); evidência de firing/resolve.
  - Painel `s35_flow_rollout_overview` renderizado com dados reais; export JSON/PNG incluído.
  - `bin/s35_g3_obs.sh` falha se métricas não aparecem, se promtool quebra, ou se alerta não dispara.
- **G4 — Pilotos reais (API/UI/metrics)**
  - news_v2 e contestacao_v0 executados com canary/teste percentual via API/UI; rollback e promoção exercitados.
  - Uso de catálogo assinado publicado; script checa hash consumo vs publicação.
  - Evidências: logs de API, métricas coletadas, screenshots reais (Playwright ou grab) do console, alert firing em piloto, registro de `slo_breach` simulado.
  - `bin/s35_g4_pilotos.sh` falha se detectar fixtures duplicados/placeholders.
- **G5 — ORR/DoD + decisão**
  - Review G0–G4, `S35_metrics_summary.json`, `inspectah_s35_evidence_bundle.zip`.
  - GO/NO-GO explícito com riscos e flags; se qualquer gate teve mock/placeholder, resultado é NO-GO.
  - Runbooks ensaiados para rollback rápido e freeze de catálogo.

### 2.3 Métricas e alertas chave
- Métricas rollout: `flow_rollout_requests_total`, `flow_rollout_success_total`, `flow_rollout_rollback_total`, `flow_rollout_duration_seconds`, `flow_policy_violations_total`, `flow_catalog_hash_mismatch_total`, sempre com labels `{flow_id,flow_version_id,mode}`.
- SLOs (fonte: s35_slos.md) aplicados em código e alertas: duração canary/teste, violações de política, rollback_rate, disponibilidade API rollout, freshness do painel.
- Alertas mínimos: `rollbacks_rate_gt_threshold`, `slo_breach_mode`, `catalog_hash_drift`, `policy_violation_canary`, `canary_stuck_duration`, `api_rollout_unavailable`.
- Evidência obrigatória: print do firing/resolution, query PromQL com séries não vazias, hash comparado (publish vs runtime).

### 2.4 Invariantes & DoD
- `actor` obrigatório em toda operação; ausência = 4xx + log de tentativa.
- Catálogo publicado (assinatura + hash) = catálogo carregado; divergência bloqueia operação e marca `policy_violation`.
- Limites de tempo/percentual/rollbacks aplicados em runtime; promoção/rollback só ocorre se SLO/alertas verdes.
- `_derive_slo_status` grava `operacao='slo_breach'` em log/métrica quando simulado; eventos OracleOps/Truth recebem `flow_id/flow_version_id/mode`.
- **DoD:** G0–G5 PASS sem placeholders; pilotos reais completos; bundle com logs, métricas, hashes, screenshots reais; painel/alertas comprovados; OracleOps/Truth recebendo eventos; scorecard de gates não tem “PASS sintético”.
