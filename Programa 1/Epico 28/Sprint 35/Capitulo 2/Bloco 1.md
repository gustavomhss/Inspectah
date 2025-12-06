# Bloco 1 — Gates G0 e G1
- **G0 — Escopo/catalogo:** 24 arquivos 6×4 sem TODO/FIXME; catálogo inicial `config/flow_catalog/*.yaml` (news_v2, contestacao_v0) versionado e assinado; script `bin/s35_g0_scope.sh` PASS.
- **G1 — Modelo/rollout:** migração `migrations/versions/0036_s35_flow_governance_advanced.py` aplicada (DB limpo + pós-S34); entidades suportam canary/teste percentual; limites/flags em `config/flows_limits.yaml` e `config/feature_flags.yaml` aplicados; políticas carregadas do catálogo sem erro; script `bin/s35_g1_model.sh` PASS.
