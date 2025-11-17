# Sprint 10 — Overview Geral — Truth-DB & Guardião de Blocos

## Objetivo
A Sprint 10 cristaliza o eixo Truth-DB do Inspectah: modelar blocos/fatos/complementos/versões, dar contrato operacional ao Guardião de Blocos (GPT), aplicar tudo por uma engine mecânica e provar os fluxos ponta a ponta em dois domínios (obras públicas e índices de preços). A definição de pronto é cada gate S10-G0…G7 em PASS com scorecards e G8 emitindo `decision="GO"`.

## Escopo entregue
- Núcleo Truth-DB completo (`inspectah/truthdb/*`, migration `0001_s10_truthdb_core.py`).
- Contrato de ações (`inspectah/truthdb/actions_contract.py`) + schema JSON (`schema/s10_guardian_actions.schema.json`).
- Engine mecânica (`inspectah/truthdb/engine.py`) e invariantes dedicados.
- Pipelines domínio A/B (`inspectah/pipelines/s10_domain_a_obras.py`, `s10_domain_b_precos.py`) + testes que fecham o fluxo via Guardião + engine.
- Layer de exports/audit (`inspectah/truthdb/exports.py`, `config/s10_exports.yml`, `scripts/truthdb_inspect.py`, `scripts/truthdb_export_demo.py`).
- Gates G0…G8 e orquestrador `bin/s10_all_gates.sh`, além do workflow CI `_s10-gates.yml`.

## Gates e scorecards
| Gate | Foco | Status | Scorecard |
|------|------|--------|-----------|
| S10-G0 | Sanidade do repo/branch/docs/out | PASS | `out/scorecards/S10_G0_sanity.json` |
| S10-G1 | Modelo Truth-DB & future-ready | PASS | `out/scorecards/S10_G1_truthdb_model.json` |
| S10-G2 | Máquina de estados de fatos | PASS | `out/scorecards/S10_G2_state_machine.json` |
| S10-G3 | Contrato de ações do Guardião | PASS | `out/scorecards/S10_G3_guardian_contract.json` |
| S10-G4 | Engine mecânica | PASS | `out/scorecards/S10_G4_mechanical_engine.json` |
| S10-G5 | E2E domínio A (obras) | PASS | `out/scorecards/S10_G5_e2e_domain_A.json` |
| S10-G6 | E2E domínio B (preços) | PASS | `out/scorecards/S10_G6_e2e_domain_B.json` |
| S10-G7 | Auditabilidade & futuro (exports) | PASS | `out/scorecards/S10_G7_audit_and_future.json` |
| S10-G8 | GO/NO-GO | decision = GO | `out/scorecards/S10_G8_go_no_go.json` |

## Destaques de SLIs
- `ratio_valid_actions_accepted = 1.0` e `ratio_invalid_actions_rejected = 1.0` em G3–G6, confirmando contrato + engine.
- `audit_trace_completeness = 1.0` e `future_ready_completeness = 1.0` para domínios A/B (G5–G7).
- `e2e_scenario_success_rate = 1.0` nos pipelines A/B.

## Artefatos principais
- **Truth-DB**: `inspectah/truthdb/{models,state_machine,invariants,actions_contract,engine,exports}.py`, migration `migrations/versions/0001_s10_truthdb_core.py`.
- **Pipelines**: `inspectah/pipelines/s10_domain_a_obras.py`, `s10_domain_b_precos.py` + testes em `tests/pipelines/`.
- **Exports/Audit**: `inspectah/truthdb/exports.py`, `config/s10_exports.yml`, `scripts/truthdb_inspect.py`, `scripts/truthdb_export_demo.py`.
- **Gates**: `bin/s10_g0_sanity.sh` … `bin/s10_g8_go_no_go.sh`, orquestrador `bin/s10_all_gates.sh`, workflow `.github/workflows/_s10-gates.yml`.
- **Evidências**: `out/scorecards/S10_G*.json`, `out/evidence/S10_G*/` (snapshot de testes, logs, exports, relatórios).

## Riscos e próximos passos
- **Dependência futura**: export format está pronto mas vai precisar versionamento formal ao conectar com S11 (blockchain) e S12 (Explorer). Documentar mudanças na camada `exports.py`.
- **Eventos adicionais**: pipelines atuais cobrem domínios pilotos; expansão para novos domínios exigirá novos cenários e possivelmente ações adicionais no contrato (abrir via ADR).
- **Próximas sprints**:
  - **S11**: acoplar Truth-DB com camada de ancoragem em blockchain tomando `inspectah/truthdb/exports.py` como base; aproveitar `scripts/truthdb_export_demo.py` para gerar pacotes de âncora.
  - **S12**: construir Explorer/experiências externas lendo `out/evidence/S10_G7/exports/*.json`, adicionando camadas de consulta e governança contínua.
