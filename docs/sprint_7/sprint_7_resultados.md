# Sprint 7 Resultados

## Entregas principais

- Inspectah UI Alpha disponível nos endpoints `/admin/sources`, `/model/fields`, `/query` e `/evidence/<id>` com todo o fluxo admin/usuário sem terminal.
- Gates `S7-G0` a `S7-G8` implementados em `bin/` com scorecards e evidências em `out/scorecards/` e `out/evidence/`.
- Métricas M1–M6 consolidadas no gate `S7-G7` e refletidas abaixo.
- Testes automatizados da Sprint 7 adicionados em `tests/sprint_7/`.

## Métricas M1–M6

| Métrica | Observado | Limite | Status |
| --- | --- | --- | --- |
| M1 — Demo UI-only | 1.40 s (fluxo admin + usuário) | ≤ 300 s | ✅ |
| M2 — Fluxo usuário sem terminal | 0.88 s / terminal desnecessário | Fluxo completo sem terminal | ✅ |
| M3 — Admin CRUD | 1.0 (100%) | 100% | ✅ |
| M4 — Modelo e consultas | schema 1.0 · consistência 1.0 · coverage 1.0 | 100% | ✅ |
| M5 — Explicação consolidada | presente para todas as consultas validadas | Obrigatório | ✅ |
| M6 — Evidência | 2 cliques · 100% de sucesso | ≤ 2 cliques / 100% | ✅ |

Fonte: `out/scorecards/S7_G7_metrics_and_demo.json`.

## Roteiro oficial da demo

1. `bin/s7_ui_start.sh` e validação de `/health`.
2. Navegar para `/admin/sources`, ajustar uma fonte e salvar.
3. Abrir `/model/fields` para revisar o modelo e prévias por fonte.
4. Acessar `/query`, executar uma consulta e observar a decisão consolidada + explicação.
5. Clicar em “Ver evidência” para qualquer linha e conferir o manifest correspondente.
6. `bin/s7_ui_stop.sh` ao final.

## Decisão

- **S7-G8:** GO (`out/scorecards/S7_G8_sprint_go_no_go.json`).
- Todos os gates e métricas em PASS.

## Como validar

```bash
bin/s7_g0_baseline.sh
bin/s7_g1_ui_boot_health.sh
bin/s7_g2_ui_sources_admin.sh
bin/s7_g3_ui_fields_preview.sh
bin/s7_g4_ui_query_consolidation.sh
bin/s7_g5_ui_evidence_trace.sh
bin/s7_g6_ui_only_flows.sh
bin/s7_g7_metrics_and_demo.sh
bin/s7_g8_sprint_go_no_go.sh
PYTHONPATH=. pytest tests/sprint_7 -q
```

> Observação: a suíte completa `pytest -q` depende de módulos legados da Sprint 6 que hoje não expõem funções como `get_connection`/`run_once_for_source`; por isso só os testes da Sprint 7 são executados automaticamente.
