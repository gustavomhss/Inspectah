# Inspectah — Sprint 34 — Capítulo 4
## Execução, Waves, Testes e Evidências (Multi-fluxo + OracleOps v2)

### 4.1 Waves (D1–D7)
- **W0/W1 (D1–D2):** Cap.1–3 fechados; templates/migração criados; G0 verde.
- **W1 (D3):** Modelo/políticas multi-fluxo implementados; G1 verde em DB limpo + pós-S32.
- **W2 (D4):** Console/API multi-fluxo com histórico/diffs/rollback; cockpit OracleOps exibindo fluxos/versões/SLO; G2 PASS local.
- **W3 (D5):** Observabilidade/alertas por fluxo/versão/teste; painel `s34_flow_ops_overview`; SLOs versionados; G3 PASS.
- **W4 (D6):** Pilotos de notícias e contestação v0 executados (teste/ativo) com rollback; evidências coletadas; G4 PASS; CI `s34-gates.yml` verde.
- **ORR (D7):** ORR em cima do bundle multi-fluxo; decisão GO/NO-GO; docs/runbooks atualizados.

### 4.2 Plano por eixo
- **Backend:** migração + serviços/versionamento/políticas multi-fluxo; integração ops/SLO/incident.
- **APIs:** rotas multi-fluxo e histórico/diffs/rollback com RBAC; payloads com `flow_id/flow_version_id`.
- **Frontend:** lista/detalhe multi-fluxo; histórico/diffs/rollback; painel de ops/SLO/incident.
- **Observabilidade:** métricas/logs/alertas por fluxo/versão; painel `s34_flow_ops_overview`; SLOs versionados.
- **E2E pilotos:** notícias governado (ativo/teste + rollback); contestação v0 governado (modo teste controlado); evidências completas.
- **Gates/CI:** scripts `bin/s34_g0..g5.sh`, metrics_summary, bundle, workflow `s34-gates.yml`.

### 4.3 Cenários de teste por gate
- **G0:** 24 arquivos 6×4; templates/scope/SLO map presentes; script retorna 0.
- **G1:** migração aplica (DB limpo + pós-S32); templates carregam; políticas por domínio ativas; limites/flags aplicados.
- **G2:** console/API lista fluxos/versões/diffs; rollback/promoção/teste funcionam com autorização; cockpit exibe SLO/incident.
- **G3:** métricas/logs com labels de fluxo/versão; painel não vazio; alertas disparam em thresholds; SLOs ligados a métricas reais.
- **G4:** pilotos notícias + contestação v0 rodados em teste/ativo; rollback exercitado; evidências completas; bundle multi-fluxo gerado.

### 4.4 Evidências e bundle
- Scorecards: `out/scorecards/S34_G0..G5.json`, `S34_metrics_summary.json`.
- Evidências:
  - `out/evidence/S34_G0_scope_and_templates/`
  - `out/evidence/S34_G1_model_and_policies_multifluxo/`
  - `out/evidence/S34_G2_console_multifluxo/`
  - `out/evidence/S34_G3_observabilidade_multifluxo/`
  - `out/evidence/S34_G4_pilotos_multifluxo/` (contém: `dataset_noticias.json`, `dataset_contestacao.json`, `ingest_log.txt`, `exec_dump.json`, `metrics_logs_snapshot.*`, `console_screenshots/`)
  - `out/evidence/S34_ORR_summary.txt`
- Bundle: `out/bundles/inspectah_s34_evidence_bundle.zip` com scorecards + evidências.
