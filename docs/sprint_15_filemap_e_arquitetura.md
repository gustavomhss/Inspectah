# Sprint 15 — Filemap e Arquitetura

## Código de domínio
- `inspectah/debunker/`: engine, regras, modelos de relatório e fixtures.
- `inspectah/committees/`: tipos comuns e camadas V1 (mecânico), V2 (multi-cérebro) e V3 (coerência global).
- `inspectah/anchors/`: Merkle, cliente de chain, batcher e registry de âncoras.
- `inspectah/commands/`: write path blindado contra canetada; registra tentativas e exige causa formal.
- `inspectah/blocks/`: snapshot auxiliar com âncoras acopladas ao estado da Truth-DB.

## Scripts e gates
- `bin/s15_t0_sanity.sh` … `bin/s15_t8_go_no_go.sh`: gates individuais.
- `bin/s15_all_gates.sh`: orquestra T0–T8.
- Evidências: `out/evidence/S15_T*/` seguindo o layout do Cap. 3.
- Scorecards: `out/scorecards/S15_T*.json`.

## Workflows CI
- `.ci/sprint_15_gates.yml`: executa T0–T7 em PR/main.
- `.ci/sprint_15_nightly.yml`: roda subconjunto T2–T6 diariamente.

## Integrações chave
- V1 usa `inspectah.truthdb.state_machine.StateMachine` para validar transições.
- Anti-canetada mantém trilha de tentativas em `inspectah.commands.audit_trail`.
- Registro de âncoras persistido em `out/evidence/S15_T1_contracts_and_states/anchors/registry_snapshot.json`.
