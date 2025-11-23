# Sprint 17.1 — Overview (Consulta v1)

## Objetivo
Fechar o gap entre a UI da Sprint 17 e o backend, entregando a **Inspectah Consultation API v1** real, documentada e integrada ao motor (Debunker + Comitês + Âncoras). A rota oficial `POST /api/consultation` agora:
- Usa o mesmo contrato de `frontend/inspectah-ui/src/types/inspectah.ts`;
- Orquestra Debunker, Comitês e âncoras em vez de mocks;
- Está protegida por gates T0–T8 específicos da Sprint 17.1.

## Principais entregas
- Módulo de consulta em `inspectah/ui/consultation_*` com modelos Pydantic, serviço de orquestração e observabilidade.
- Router FastAPI dedicado (`/api/consultation`) conectado no `inspectah.api:build_app` com CORS para `http://localhost:5173`.
- Testes de modelos, serviço e API (`tests/test_consultation_*.py`).
- Gates e scorecards da Sprint 17.1 (`bin/s17_1_t0...t8.sh`, `out/scorecards/S17_1_T*.json`).
- Workflows de CI `sprint_17_1_gates` e `sprint_17_1_nightly`.
- Documentação técnica e ORR em `docs/sprint_17_1_*`.

## Como exercitar rapidamente
1. Backend: `PYTHONPATH=. python -m uvicorn inspectah.api:build_app --factory --reload --port 8000`
2. Frontend (Sprint 17): `cd frontend/inspectah-ui && npm ci && npm run dev`
3. Consulta: `curl -X POST http://localhost:8000/api/consultation -H "Content-Type: application/json" -d '{"question": "Eleição municipal procede?"}'`
4. Gates locais: `PYTHONPATH=. bin/s17_1_all_gates.sh`

## Estado atual
- Implementação da API e dos gates concluída neste commit.
- Execução final dos gates deve ser feita antes do ORR: `bin/s17_1_all_gates.sh` (gera scorecards em `out/scorecards/`).

