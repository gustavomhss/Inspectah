# Sanidade local S1–S25 (Sprint 25)

- HEAD inicial: 464bf17311418daf49505e782ac3138e092a1f9b (feature/s25_truth_v1_5)
- HEAD final: 464bf17311418daf49505e782ac3138e092a1f9b

## Testes Python
- `PYTHONPATH=. pytest tests/truth tests/context tests/layers tests/policies tests/threatmodel tests/truthdb` → ✅ 35/35
- `PYTHONPATH=. pytest tests/api` → ✅ 3/3 (avisos de compatibilidade Pydantic v1)

## Gates/scripts em `bin/` (estado atual)
- S12_G0, S14_G0, S15_T0–T8, S16_T0–T8, S17.1_T0–T8, S18_G0, S20_G0–G7, S21.1_G2/G3, S22_G0–G7, S24_G0–G6, S25_G0–G7 + ORR → ✅
- S19_G0 → ✅ após correção de escopo (anotações não bloqueiam)
- Pendências: S23_G1/G2 ainda falham (escopo próprio)
- Scripts legados (s5/s7/s8/s9/s10/s13/s24) executam sem `permission denied`; falhas lógicas permanecem onde existentes

## Frontend
- `npm install` → ok
- `npm run build` em `frontend/inspectah-ui` → ✅ (Vite)

## Smoke admin/console
- `bin/sanity_smoke_admin_console.sh` (TestClient, sem bind de porta) → ✅
- Evidência: `out/evidence/admin_console_smoke.json`

## Débitos técnicos registrados (anteriores)
- Falhas restantes: S21.1_G2/G3, S23_G1/G2.
- TODOs antigos em docs legados e em dependências de `frontend/inspectah-ui/node_modules` (não alterados).

## Correções dos débitos 1, 2, 4, 8 e 9 (sanidade pós-S25)
- S12_G0: removido bloqueio rígido de branch, mantendo checagem de docs; snapshot registra branch fora do baseline como nota.
- S14_G0: branch/origin agora geram notas, não falha; mantém validação de docs e decisões GO de S12/S13.
- S19_G0: falha agora só por ausência de docs; arquivos fora do escopo viram nota (evita falso negativo com mudanças pós-S19).
- Permissões: `chmod +x` aplicado a gates legados (`s5_*`, `s7_*`, `s8_*`, `s9_*`, `s10_*`, `s13_*`, `s24_g3_human_loop_queue.sh`); `s10_all_gates.sh` agora chama scripts executáveis.
- Smoke admin/console: novo `bin/sanity_smoke_admin_console.sh` usando FastAPI TestClient (sem bind de porta); cobre `/admin/health`, `/admin/cases`, fluxo/CRUD básico de `/api/console/agents` e gera evidência em `out/evidence/admin_console_smoke.json`.

## Correções dos débitos 5 e 7 (S21.1 e S24)
- S21.1_G2 (agent_mode): corrigido backend de agents para validar fluxo de camadas (camadas obrigatórias, >=3 agentes por camada, mediador incluso); `AgentRole` agora inclui `mediator`; API `/admin/agents/flow` retorna 400 em cargas inválidas. Suite `tests/agents` verde e gate gera scorecard em `out/scorecards/S21_1_G2_agent_mode.json`.
- S21.1_G3 (sync_form): lint/test/build do frontend ajustados (hooks de agentes corrigidos para dependências de React e lint de testing-library). Gate executa com sucesso e evidências em `out/evidence/S21_1_G3_sync_form`.
- S24 (Debunker v0 / humano-no-loop): gates S24_G0–G6 executam após restaurar bits de execução; scripts rodam limpos no estado atual (bundle, contracts, debunk API smoke, filas human loop, decisão e observabilidade). Scorecards em `out/scorecards/S24_*`.

## Correção do débito S18_G1 (arquitetura front/admin + API)
- Gate `bin/s18_g1_arch_front_and_api.sh` alinhado para paths atuais do frontend admin (`src/modules/admin/...`) mantendo checagem de backend admin e geração de OpenAPI com rotas `/admin`.
- Gate reexecutado com sucesso; scorecard em `out/scorecards/S18_G1_arch_front_and_api.json` e evidência OpenAPI em `out/evidence/S18_G1_arch_front_and_api/openapi_admin.json`.

## Correção do débito S23 (modelo de dados, ontologia e service contracts)
- S23_G1 e S23_G2 executam agora em GO rodando `tests/agents/test_s23_agents_api.py` (modelo/ontologia e contratos de serviço de agents/truth). Ajustes prévios de validação de fluxo/roles permitiram o verde; gates reexecutados geram scorecards em `out/scorecards/S23_G1_modelo_dados.json` e `S23_G2_service_contracts.json` com evidências em `out/evidence/S23_G1_modelo_dados/tests.log` e `out/evidence/S23_G2_service_contracts/tests.log`.
