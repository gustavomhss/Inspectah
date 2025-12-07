# Bloco 4 — Evidências e bundle
- Scorecards: `out/scorecards/S35_G0..G5.json`, `S35_metrics_summary.json`; cada PASS anota se houve simulação e se alerta disparou.
- Evidências mínimas por gate:
  - `out/evidence/S35_G0_scope_and_catalog/` → manifest do catálogo publicado, hash/assinatura, comparação publish/runtime.
  - `out/evidence/S35_G1_model_rollout/` → logs de testes negativos (limites/actor), dump de DB pós-migração, policies carregadas.
  - `out/evidence/S35_G2_console_rollout/` → requests/responses HTTP reais (erro e sucesso), trilhas de auditoria, prints do console com hash/actor.
  - `out/evidence/S35_G3_observabilidade_rollout/` → `curl /metrics`, saída do promtool, export JSON/PNG do painel, prints de alert firing/resolution.
  - `out/evidence/S35_G4_pilotos_rollout/` → datasets reais, ingest_log, exec_dump, rollout_timeline, métricas (PromQL), comparação de hash publish/runtime, screenshots reais (Playwright/headless), registro de `slo_breach`.
  - `out/evidence/S35_ORR_summary.txt` → decisão GO/NO-GO com flags.
- Bundle: `out/bundles/inspectah_s35_evidence_bundle.zip` contendo todos os itens acima e hashes verificados.
