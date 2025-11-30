# Sprint 27 — Capítulo 4 (Execução e Evidências)

Documentação completa do Capítulo 4 da Sprint 27:
- Ver: `Programa 1/Epico 27/Sprint 27/Capitulo 4.md`
- Blocos: `Bloco 1.md` a `Bloco 4.md` na mesma pasta, se existirem.

Este arquivo serve como ponte para ferramentas e gates que esperam a documentação da S27 em `docs/`.

## Execução e Gates (S27)
- G0_scope_and_baseline → GO
- G1_models_and_invariants → GO
- G2_backend_ingestion_ops → GO
- G3_frontend_sources_console_ops → GO
- G4_audit_logs_evidence → GO
- G5_bundle_and_orr → GO
- Scorecards: `out/scorecards/S27_G*.json`
- Evidências: `out/evidence/S27_G*_*/`

## Bundle de evidências
- Arquivo: `out/bundles/inspectah_s27_evidence_bundle.zip`
- Conteúdo: scorecards S27, evidências dos gates G0–G5, `bundle_manifest.json`, logs de execução dos gates.

## Principais entregas operacionais
- Backend fontes/ingestão: modelo com saúde derivada de runs, ações admin logadas em audit (env `INSPECTAH_AUDIT_LOG_BASE`), endpoints de pause/resume/run manual.
- Frontend console de fontes: lista com filtros de estado/saúde, forms completos, ações de ingestão (pausa/retoma/run), painel de saúde e histórico resumido.
- Auditoria: registros de ações admin centralizados e validados pelo gate G4.
