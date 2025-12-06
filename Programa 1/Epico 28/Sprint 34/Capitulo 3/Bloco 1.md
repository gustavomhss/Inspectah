# Bloco 1 — Backend (modelo, serviços, templates)
- **Modelos/migração:** `0034_s34_flow_multidomain_ops.py` adiciona tabela de template/versionamento multi-fluxo, ligações a políticas por domínio e campos para SLO/incident hooks (`flow_ops_profile_id`).
- **Templates:** `app/flows/templates/loader.py` carrega `config/flow_templates/*.yaml` (news_v2, contestacao_v0), valida esquema e versiona; persistência opcional em DB.
- **Serviços:** `versioning.py` (create_version, diff_version, rollback com validações/limites); `policy_engine.py` (políticas mínimas por domínio/etapa, bloqueio de estados inválidos); `ops_integration.py` (emite eventos para SLO/incident com `flow_id/flow_version_id`).
- **Invariantes:** toda execução registra `flow_id/flow_version_id/operation_id`; rollback só com versão testada; políticas aplicadas antes de `em_teste`/`ativo`; limites/flags respeitados.
