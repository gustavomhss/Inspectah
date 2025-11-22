# Sprint 16 — Filemap e Arquitetura

## Camadas
- **Truth-DB / Sistema de Blocos (S13–S15)**: estados, eventos, disputas e write path.
- **Blindagem (S15)**: Debunker v1, Comitês V1/V2/V3, Âncoras e Anti-canetada.
- **Hardening (S16)**: Threat Model, cenários de ataque/stress, ajustes defensivos e observabilidade de segurança.
- **Runbooks/CI/ORR (S16)**: docs, gates em `bin/`, scripts em `scripts/`, workflows em `.ci/`, evidências em `out/`.

## Documentação
- `/Sprint 16/Capitulo 1.md` … `Capitulo 4.md`: visão, gates, filemap e runbook oficiais.
- `docs/sprint_16_overview.md`: resumo executivo da S16.
- `docs/sprint_16_filemap_e_arquitetura.md`: este mapa operacional.
- `docs/sprint_16_threat_model.md`: Threat Model formal e mapeamento ameaça → cenários/gates.
- `docs/sprint_16_orr_summary.md`: ORR S16 com decisão GO/GO_WITH_RESTRICTIONS/NO_GO.

## Scripts e gates
- `bin/s16_t0_sanity.sh` … `bin/s16_t8_go_no_go.sh`: gates individuais.
- `bin/s16_all_gates.sh`: orquestração T0–T8 com paradas em falha.
- `scripts/s16_threat_model_checks.py`: validação estrutural do Threat Model.
- `scripts/s16_attack_scenarios.py`: registro/CLI dos cenários de ataque e stress.
- `scripts/s16_debunker_and_committees_under_attack.py`: foco em Debunker + Comitês.
- `scripts/s16_anchors_and_anti_canetada_tests.py`: falhas de chain e bypass de override.
- `scripts/s16_stress_and_degradation.py`: stress controlado de fluxos críticos.
- `scripts/s16_security_observability_checks.py`: consultas padrão de observabilidade de segurança.
- `scripts/s16_ci_and_repro_checks.py`: verificação de workflows CI S16 e convergência local.

## Módulos endurecidos
- `inspectah/debunker/`: flags de risco adicionais e meta explicativa.
- `inspectah/committees/`: limites para decisões automáticas arriscadas e logging estruturado.
- `inspectah/anchors/`: melhor tratamento de falhas da chain e persistência de batches.
- `inspectah/commands/__init__.py`: anti-canetada com trilha obrigatória e bloqueio de overrides silenciosos.

## Evidências e scorecards
- Scorecards: `out/scorecards/S16_T*.json` (um por gate).
- Evidências: `out/evidence/S16_T*/` com `MANIFEST.json`, logs, dumps e snapshots.
- Scorecards e evidências seguem o padrão da S15, mas com foco em cenários de ataque e investigações de segurança.

## CI
- `.ci/sprint_16_gates.yml`: gates críticos (T0–T4+) em PR/main.
- `.ci/sprint_16_nightly.yml`: cenários mais pesados (stress/ataque) em cadência diária.
- Artefatos publicados como uploads de scorecards/evidências para inspeção posterior.
