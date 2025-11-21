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
