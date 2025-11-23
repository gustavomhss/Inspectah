# Sprint 17.1 — ORR Summary (Consulta v1)

## Visão geral
A Sprint 17.1 formaliza a Consultation API v1, conectando UI (S17) ao motor real (Debunker + Comitês + Âncoras). Os gates T0–T8 desta sprint garantem que a rota `/api/consultation` existe, está contratualmente alinhada à UI e responde de forma observável.

## Gate × Status
| Gate | Objetivo | Status atual |
| --- | --- | --- |
| S17_1_T0_sanity | App FastAPI sobe e expõe OpenAPI | PENDING (rodar `bin/s17_1_t0_sanity.sh`) |
| S17_1_T1_contracts_and_states | Contrato HTTP ↔ UI | PENDING |
| S17_1_T2_integration_core_flows | Fluxos canônicos Debunker+Comitês | PENDING |
| S17_1_T3_error_paths_and_resilience | Erros previsíveis tratados | PENDING |
| S17_1_T4_ui_wire_and_e2e_smoke | Smoke compatível com UI S17 | PENDING |
| S17_1_T5_performance_and_limits | Latência e limites locais | PENDING |
| S17_1_T6_observability_and_logs | Logs/âncoras e IDs de correlação | PENDING |
| S17_1_T7_ci_and_repro | Workflows/clone limpo | PENDING |
| S17_1_T8_go_no_go | Decisão final | PENDING |

## Riscos e observações
- Execução local dos gates ainda não rodada neste ciclo; necessário rodar `bin/s17_1_all_gates.sh` para materializar scorecards.
- Ambiente atual sem `pytest` instalado; rodadas locais podem requerer `pip install -e .` ou ativar `.venv`.
- CORS limitado a `http://localhost:5173`; expandir origens deve seguir Cap. 3/4 se surgir novo ambiente.

## Decisão preliminar
- **Proposta**: GO_WITH_RESTRICTIONS — sujeita à execução completa dos gates e captura do SHA final.

## Adendo de execução final da Sprint 17.1
- `commit_sha`: a registrar após a rodada final dos gates.
- Comandos de verificação previstos: `PYTHONPATH=. bin/s17_1_all_gates.sh`.
- Scorecard T8 esperado: `out/scorecards/S17_1_T8_go_no_go.json`.
- Decisão final: preencher após execução (GO/GO_WITH_RESTRICTIONS/NO_GO).

