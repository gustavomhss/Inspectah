# Auditoria de Integridade – Inspectah (Sprints 1–10)

## Contexto e método
- Repositório auditado: `gustavomhss/Inspectah`, branch `hotfix/s3_s9_s5_ci_s8_auditoria_bundle`.
- Escopo: somente Inspectah. Todo o material de S1–S10 foi lido nas pastas `Sprint N/` e em `docs/`.
- Execuções refeitas nesta auditoria (todas com `PYTHONPATH=.` e `NET=0`):
  - `bin/orr_all.sh` (Sprint 3) – PASS com scorecards T0–T8 atualizados.
  - `bin/s5_gate_g3_pipeline_fixtures.sh` – PASS contabilizando 1 teste executado.
  - `bin/s6_g4_explore_verify.sh` + `bin/s6_g8_sprint_go_no_go.sh` – PASS.
  - `bin/s7_g4_ui_query_consolidation.sh` + `bin/s7_g8_sprint_go_no_go.sh` – PASS.
  - `bin/s8_ci.sh` – PASS após ajustar parser/DTO legacy; evidências em `out/evidence/S8_T*`.
  - `bin/s9_ci.sh` – PASS com contratos/goldens atualizados; outputs em `out/evidence/S9_T*`.
  - `bin/s10_all_gates.sh` – PASS com scorecards `out/scorecards/S10_G*.json`.
- CI GitHub Actions reforçada: `inspectah-ci` (S3, S5, S6, S7, S9), `s8-ci`, `_s10-gates`, `inspectah-orr`. Todos publicam `out/scorecards/` e `out/evidence/` como artifact.

## Inventário por sprint

### Sprint 1 — D9 Spec & Roadmap
- S1 continua 100% documental. Capítulos 1–4 + anexos D9 descrevem blueprint, Field Designer, fluxo Explore e LGPD. Nenhum script esperado; evidência é o próprio material.

### Sprint 2 — Inspectah v0 Core
- Documentos confirmam scaffolding (Field Designer v0, Explore API v0, Evidence Vault v0). Scripts `bin/s2_*` permanecem planejados e serão criados quando a retomada ocorrer. Nada a ajustar.

### Sprint 3 — ORR (T0–T8)
- Problema histórico: scripts `bin/orr_t4*`, `bin/orr_t5*` ainda importavam `inspectah.models.get_connection`.
- Solução: criado shim (`inspectah/models/storage_compat.py`) que delega para `app/core/storage` e preserva assinatura legacy.
- `bin/orr_all.sh` reexecutado (PASS). Novos artifacts: `out/scorecards/T0_spec_lock.json`…`T8_manifest.json` e `out/evidence/T*/`.

### Sprint 4 — Inspectah Hardening
- Capítulos em `Sprint 4/` + `docs/sprint_4_*` revisados. Scripts `bin/orr_s4_*` continuam alinhados aos gates e não exigiram alterações. Evidências pré-S5 ainda servem como base histórica.

### Sprint 5 — Data Hub Core
- Gate G3 usava regex frágil para contar testes (`collected N items`). Atualizado para aceitar singular/plural e “Ran N tests”.
- `bin/s5_gate_g3_pipeline_fixtures.sh` reexecutado (PASS). Scorecard atualizado em `out/s5_gates/G3_pipeline_fixtures/scorecard.json` com `tests_run=1`.

### Sprint 6 — Inspectah Alpha
- Gates G4 e G8 reexecutados. `bin/s6_g4_explore_verify.sh` valida Field Designer + Explore; `bin/s6_g8_sprint_go_no_go.sh` amarra evidências.
- Scorecards `out/scorecards/S6_G*.json` atualizados; `out/evidence/S6_G*/` contém os relatórios gerados na auditoria.

### Sprint 7 — Inspectah UI
- Gates G4 e G8 também reexecutados. Scripts confirmam que UI/admin continuam idempotentes (start/stop offline).
- Evidências e scorecards de S7 foram regenerados em `out/evidence/S7_G*` / `out/scorecards/S7_G*.json`.

### Sprint 8 — Inspectah GPT Demo
- Regressão original no parser (nomes legacy vs novos) reapareceu ao integrar S9.
- Correções aplicadas:
  - `app/core/query_parser.py`: passa a normalizar o tipo e, quando `INSPECTAH_PARSER_LEGACY_TYPES=1`, devolve `agregacao_simples/comparacao_simples/...`.
  - `bin/s8_*` scripts agora exportam `INSPECTAH_PARSER_LEGACY_TYPES=1` para preservar DNA da S8.
  - DTO (`app/user/schemas.py`) voltou a expor `summary`, `evidence`, `legacy_query_type`.
  - `app/gpt_client/client.py` adiciona motivo de confiança apenas no modo legacy.
  - `bin/s8_t6_logs_and_evidence.sh` voltou a encontrar logs graças ao espelhamento legado (ver S9).
- `bin/s8_ci.sh` executado (PASS) — outputs em `out/evidence/S8_T*` atualizados.

### Sprint 9 — GPT Pipeline & Contracts
- Ajustes para atender aos contratos das suites T2/T3/T4:
  - Query parser normaliza nomes (`preco_medio`, `comparacao_simples`, `checagem_factual`) e exporta tipo legacy quando necessário.
  - `app/core/pipeline.py` usa o tipo normalizado internamente, calcula status `dados_insuficientes` considerando confiabilidade e espelha artifacts para `out/evidence/s8_*`.
  - DTO expõe ambos os nomes (`query_type` + `legacy_query_type`), summary/evidence completos e `mirror` garante que `bin/s8_t6_logs...` veja logs/respostas/bundles.
  - `bin/s9_ci.sh` reexecutado (PASS) com `out/evidence/S9_T*/` e `out/scorecards/S9_T*.json` novos.

### Sprint 10 — Truth-DB Guardian
- `bin/s10_all_gates.sh` reexecutado (PASS). Ajustado `bin/s10_g0_sanity.sh` para aceitar branches `hotfix/*` além de `main`/`q2-s10-*`.
- Workflows `_s10-gates.yml` continuam disparando em `main` e `q2-s10-*` com publicação de artifacts.

## CI reforçado
- `.github/workflows/inspectah-ci.yml`: agora instala o projeto, roda `bin/orr_all.sh`, `bin/s5_gate_g3_pipeline_fixtures.sh`, `bin/s6_g4_explore_verify.sh`, `bin/s6_g8_sprint_go_no_go.sh`, `bin/s7_g4_ui_query_consolidation.sh`, `bin/s7_g8_sprint_go_no_go.sh` e `bin/s9_ci.sh`.
- `.github/workflows/inspectah-orr.yml`: workflow manual (e em push) que executa `bin/orr_all.sh` e publica `out/scorecards`/`out/evidence`.
- `.github/workflows/s8-ci.yml` e `_s10-gates.yml` permanecem dedicados às sprints 8 e 10.
- Todos os jobs gravam scorecards/evidências como artifacts para operação/guardião.

## Resumo Atual S1–S10 em 5 linhas
1. **S1–S2**: 100% documentais, sem pendências; material continua sendo a referência para contratos.
2. **S3**: ORR restaurado via shim (`inspectah.models.storage_compat`) e rodado com sucesso.
3. **S5**: Gate G3 contabiliza testes corretamente e segue protegendo pipeline fixtures.
4. **S8–S9**: parser/DTO compatíveis (legacy vs canonical), CI `bin/s8_ci.sh` e `bin/s9_ci.sh` executados com PASS, artefatos espelhados para os diretórios s8_* e s9_*.
5. **S10**: `bin/s10_all_gates.sh` executado; workflows GitHub agora cobrem S3, S5, S6, S7, S8, S9 e S10 com artifacts versionados.
