# Sprint 15 — ORR Parcial

## Decisão
- Status: **GO** condicionado aos gates T0–T7 em PASS.
- Justificativa: Debunker, comitês, âncoras e anti-canetada operam com evidências arquivadas; pipelines locais e CI configurados.

## Riscos residuais
- Regras de risco simplificadas: calibrar pesos por domínio na S16.
- Cliente de chain simulado: trocar por provedor real/testnet configurável antes de produção.
- Observabilidade básica: ampliar painéis e alertas na S16.

## Evidências principais
- Scorecards `out/scorecards/S15_T*.json`.
- Relatórios do Debunker em `out/evidence/S15_T2_debunker_offline/`.
- Fluxo de comitês em `out/evidence/S15_T3_committees_flow/`.
- Registro de âncoras e log de anti-canetada em `out/evidence/S15_T1_contracts_and_states/`.

## Próximos passos para S16
- Hardening e threat model dos comitês e do anti-canetada.
- Substituir cliente de chain fake por integração configurável.
- Expandir testes de carga e observabilidade em produção.

## Adendo — Validação final Sprint 15
Adendo — Validação final Sprint 15
Commit de referência: 47dfa5bc4538f501b382be59a209231f117fde00 (branch main, remoto sincronizado).
Data/hora da validação: 2025-11-21T19:35:22Z.
Ambiente: execução local em /Users/gustavoschneiter/Documents/Inspectah com PYTHONPATH=.
Gates executados (via PYTHONPATH=. bin/s15_all_gates.sh):


T0 – Sanity: PASS


Scorecard: out/scorecards/S15_T0_sanity.json


Evidências: out/evidence/S15_T0_sanity/




T1 – Contratos e estados: PASS


Scorecard: out/scorecards/S15_T1_contracts_and_states.json


Evidências: out/evidence/S15_T1_contracts_and_states/




T2 – Debunker offline: PASS


Scorecard: out/scorecards/S15_T2_debunker_offline.json


Evidências: out/evidence/S15_T2_debunker_offline/




T3 – Fluxo de comitês V1/V2/V3: PASS


Scorecard: out/scorecards/S15_T3_committees_flow.json


Evidências: out/evidence/S15_T3_committees_flow/




T4 – Golden scenarios por domínio: PASS


Scorecard: out/scorecards/S15_T4_golden_scenarios.json


Evidências: out/evidence/S15_T4_golden_*/




T5 – Performance e custo: PASS


Scorecard: out/scorecards/S15_T5_performance_and_cost.json


Evidências: out/evidence/S15_T5_performance_and_cost/




T6 – Observabilidade: PASS


Scorecard: out/scorecards/S15_T6_observability.json


Evidências: out/evidence/S15_T6_observability/




T7 – CI e reprodutibilidade: PASS


Scorecard: out/scorecards/S15_T7_ci_and_repro.json


Evidências: out/evidence/S15_T7_ci_and_repro/


Workflows relevantes: .ci/sprint_15_gates.yml, .ci/sprint_15_nightly.yml




T8 – Go/No-Go Sprint 15: PASS (GO)


Scorecard: out/scorecards/S15_T8_go_no_go.json


Evidências consolidadas: out/evidence/S15_T8_go_no_go/




Escopo efetivamente entregue na Sprint 15:


Debunker v1 completo (inspectah/debunker/* + fixtures em múltiplos domínios), com classificação de risco por domínio e execução offline via scripts/s15_debunker_offline.py e bin/s15_t2_debunker_offline.sh.


Comitês V1/V2/V3 (inspectah/committees/*) integrados ao fluxo de disputas, com validação mecânica, multi-brain (incluindo Promotores do Diabo) e checagem de coerência global.


Módulo de âncoras (inspectah/anchors/*) com Merkle, batcher, cliente de chain e registry, integrado ao Sistema de Blocos em inspectah/blocks/__init__.py.


Anti-canetada no write path em inspectah/commands/__init__.py, impedindo overrides diretos e registrando pedidos como eventos/disputas com trilha de auditoria.


Gates T0–T8 específicos da S15 (bin/s15_t0_sanity.sh…bin/s15_t8_go_no_go.sh) e orquestrador bin/s15_all_gates.sh.


Workflows de CI da S15 (.ci/sprint_15_gates.yml, .ci/sprint_15_nightly.yml) e documentação de sprint (docs/sprint_15_overview.md, docs/sprint_15_filemap_e_arquitetura.md, docs/sprint_15_orr_summary.md).


Riscos residuais e próximos passos sugeridos (para Sprint 16):


Refinar limites de risco do Debunker e políticas dos comitês com base em dados reais.


Stressar custos de âncoras e caminhos de fallback em caso de indisponibilidade de chain.


Aprimorar Threat Model e testes de ataque sobre a camada de blindagem (Debunker + comitês + âncoras + anti-canetada).


Decisão final ORR Sprint 15: GO para seguir para a Sprint 16, focada em hardening e Threat Model do Sistema de Blocos apoiado na camada de inteligência e blindagem entregue na S15.
