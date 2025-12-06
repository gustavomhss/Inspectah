# Bloco 1 — Backend (rollout, catálogo, políticas)
- **Migração `0036_s35_flow_governance_advanced.py`:** campos para canary/teste percentual (mode, test_percentual, rollout_state, rollout_started_at, rollout_criteria), relação com catálogo (hash/version).
- **Rollout (`app/flows/rollout.py`):** iniciar canary/teste, monitorar critérios (SLO/alerta), promover ou rollback; valida limites/flags; registra auditoria.
- **Catálogo (`app/flows/catalog.py`):** carrega `config/flow_catalog/*.yaml`, valida esquema, calcula hash/assinatura; fornece API para sync e comparação com runtime.
- **Políticas (`policy_engine.py`):** aplica políticas por domínio e modo (teste/canary/ativo); bloqueia promoções quando violações/alertas.
- **Invariantes:** toda operação inclui `flow_id`, `flow_version_id`, `mode`, `operation_id`; rollback/promoção só se critérios atendidos; catálogo carregado corresponde ao hash publicado.
