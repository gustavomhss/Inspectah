# Core Gates S3–S10 — Checkpoint Operacional

## Visão rápida
Main está selado com todas as sprints de S3 a S10 em estado PASS/GO. Os scorecards atuais em `out/scorecards/` foram regenerados após os últimos fixes e não há entradas com `status: FAIL` nem decisões `NO_GO`. O workflow `inspectah-ci` (job *core-gates*) roda em cada push/PR para `main` e cobre os scripts críticos de S3, S5, S6, S7, S8, S9 e S10, funcionando como guarda automática contra regressões. Os agregadores completos continuam disponíveis para execuções dedicadas, mas o core-gates se concentra no smoke/health check que realmente cabe dentro do CI. Sempre que o core-gates passar e `out/scorecards/` permanecer verde, podemos considerar a branch como pronta para destravar novas sprints.

## Mapa de gates no core-gates (inspectah-ci)
- **S3**: `bin/orr_all.sh` — valida o ORR completo da sprint 3.
- **S4**: não roda no core-gates; os gates `bin/orr_s4_t7_pipeline.sh` e `bin/orr_s4_t8_go_no_go.sh` são executados manualmente quando precisamos validar o legado da sprint 4.
- **S5**: `bin/s5_gate_g3_pipeline_fixtures.sh` — garante a contagem correta de testes e fixtures da pipeline.
- **S6**: `python -m inspectah.sprint6.cli collect` seguido de `bin/s6_g4_explore_verify.sh`. O objetivo aqui é garantir que a coleta canônica gera dados e que o Explore continua íntegro; os demais gates (G0–G3, G5–G8) permanecem fora do fluxo para evitar falso negativo em ambientes limpos.
- **S7**: `bin/s7_g4_ui_query_consolidation.sh` — smoke da UI/consulta; o `bin/s7_g8_sprint_go_no_go.sh` continua disponível para ORR completo, mas não é parte do core-gates.
- **S8**: `bin/s8_ci.sh` — roda T0–T6, incluindo os goldens da demo GPT.
- **S9**: `bin/s9_ci.sh` (T1–T6). Quando precisamos consolidar T7/T8, usamos `bin/s9_t7_ci_pipeline.sh` e `bin/s9_t8_go_no_go.sh` manualmente; o core-gates fica com o T1–T6 para reduzir tempo de CI.
- **S10**: `bin/s10_all_gates.sh` via workflow dedicado `_s10-gates.yml`, mas o resultado é considerado parte do checkpoint operacional.

## Mapa de ORR completo por sprint
- **Sprint 3**: `bin/orr_all.sh` (T0–T8) é o único entrypoint.
- **Sprint 4**: `bin/orr_s4_t7_pipeline.sh` + `bin/orr_s4_t8_go_no_go.sh` consolidam o ORR, consumindo os scorecards T0–T6.
- **Sprint 5**: conjunto G0–G5 descrito em `Sprint 5/` (`bin/s5_gate_g*_*.sh`), com G3 como guardião crítico.
- **Sprint 6**: gates `bin/s6_g0_*` até `bin/s6_g8_*` descritos na pasta `Sprint 6/` e nos docs oficiais; o CLI `inspectah.sprint6.cli` oferece comandos auxiliares para coletar e inspecionar bundles.
- **Sprint 7**: o ORR completo usa `bin/s7_g0_*` até `bin/s7_g8_*`, incluindo o agregador `bin/s7_g8_sprint_go_no_go.sh` (fora do core-gates).
- **Sprint 8**: `bin/s8_ci.sh` cobre T0–T6; T7/T8 são validados por scripts adicionais em `docs/sprint_8*/` quando necessário.
- **Sprint 9**: `bin/s9_ci.sh` (T1–T6) + `bin/s9_t7_ci_pipeline.sh` + `bin/s9_t8_go_no_go.sh` para o conjunto completo.
- **Sprint 10**: `bin/s10_all_gates.sh` executa todos os G0–G8 em sequência.

## Pacote de sanity local
Antes de iniciar qualquer sprint nova ou mexer em gates sensíveis, execute o seguinte pacote em `main`:

```bash
cd /Users/gustavoschneiter/Documents/Inspectah
git checkout main
 git pull origin main
. .venv/bin/activate
export PYTHONPATH=.

bin/orr_all.sh
bin/s5_gate_g3_pipeline_fixtures.sh
python -m inspectah.sprint6.cli collect
bin/s6_g4_explore_verify.sh
bin/s7_g4_ui_query_consolidation.sh
bin/s8_ci.sh
bin/s9_ci.sh
bin/s10_all_gates.sh
```

Todos os comandos acima devem concluir com exit 0. Qualquer erro ou `status: FAIL/NO_GO` em `out/scorecards/` invalida o estado de “main selado” e precisa ser tratado antes de abrir uma nova frente de desenvolvimento.

## Cláusula inviolável
Main só é considerado pronto/estável se (1) todos os steps do `inspectah-ci`/core-gates passarem e (2) não existir nenhum scorecard com `status: FAIL` ou `decision: NO_GO` em `out/scorecards/`. Quebrar essa cláusula significa que regressões de sprints passadas podem estar passando despercebidas.

## Próximos passos
Este checkpoint serve como referência para novas sprints (S11+) e como conjunto mínimo de restore caso migrações futuras impactem S3–S10. Antes de abrir novas threads, rode o pacote de sanity e archive os scorecards verdes. Em incidentes, use este documento como checklist para decidir quais gates precisam ser rerodados e em qual ordem.
