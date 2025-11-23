# Sprint 17.1 — Filemap e Arquitetura da Consultation API v1

## Backend (núcleo de consulta)
- `inspectah/ui/consultation_models.py`: contratos Pydantic (`ConsultationRequest/Response`, `RiskLevel`, `ConsultationEvidence`) e `ConsultationResult`.
- `inspectah/ui/consultation_service.py`: orquestra Debunker + Comitês + Âncoras; aplica políticas de risco/insuficiência e gera `ConsultationResult`.
- `inspectah/ui/consultation_observability.py`: logs estruturados (`consultation_started/succeeded/failed`).
- `inspectah/ui/consultation_api.py`: router FastAPI (`POST /consultation`) usado pelo app principal.
- `inspectah/api.py`: registra o router de consulta em `/api/consultation` e habilita CORS para `http://localhost:5173`.

## Gates e evidências
- Shell scripts: `bin/s17_1_t0_sanity.sh` … `bin/s17_1_t8_go_no_go.sh`, orquestrados por `bin/s17_1_all_gates.sh`.
- Scorecards: `out/scorecards/S17_1_T*.json`.
- Evidências: `out/evidence/S17_1_T*_*/*`.
- Wrappers compatíveis com nomenclatura S17A: `bin/s17a_t*_*.sh` e `bin/s17a_all_gates.sh`.

## Testes
- `tests/test_consultation_models.py`: valida invariantes dos modelos e serialização para a UI.
- `tests/test_consultation_service.py`: cobre orquestração básica e tratamento de domínios desconhecidos.
- `tests/test_consultation_api.py`: smoke HTTP em `/api/consultation`.

## CI / Nightly
- `.ci/sprint_17_1_gates.yml`: roda T0–T7 em PR/main.
- `.ci/sprint_17_1_nightly.yml`: roda `bin/s17_1_all_gates.sh` (T0–T8) em cron/dispatch.

## Fluxo de dados resumido
1. UI envia `ConsultationRequest` → `/api/consultation`.
2. `ConsultationService` detecta domínio, monta claim e chama `analyze_claim` (Debunker).
3. Comitês V1/V2/V3 validam consistência; flags influenciam risco final.
4. Evidências do Debunker são normalizadas para o contrato da UI.
5. Resultado é ancorado (Merkle + `ChainClient`) e devolvido como `ConsultationResponse`.

