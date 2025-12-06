# Bloco 2 — Gate G2 (Console & APIs)
- UI/Console multi-fluxo lista fluxos/versões/estado/SLO/alertas; histórico e diffs por versão; rollback/promoção/teste com autorização.
- APIs em `app/api/flow_console_routes.py` (exemplos):  
  - `GET /api/flows` (filtros por estado/domínio/health)  
  - `GET /api/flows/{id}/versions`, `GET /api/flows/{id}/versions/{version_id}` (detalhe + diff)  
  - `POST /api/flows/{id}/versions/{version_id}/rollback`  
  - `POST /api/flows/{id}/state` (muda estado/teste)  
  - `GET /api/flows/{id}/ops` (histórico + SLO/incident links)
- G2 PASS: rotas protegidas por RBAC; UI consome APIs reais; auditoria grava `flow_id/flow_version_id/operation_id`; script `bin/s34_g2_console.sh` PASS.
