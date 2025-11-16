# S2-G4 — Ingest v0 + Observabilidade básica

**Responsável:** Codex (Sprint 2)  
**Última atualização:** 2025-11-14T04:25:00Z

## Ingest pipelines
- [x] `inspectah/ingest/pipeline.py` e `inspectah/watchers/rss.py` consomem schemas do Field Designer e registries oficiais (nenhum schema inline).
- [x] CLI `python -m inspectah.ingest.cli run --source-id rss_news_minimal --use-fixture --fixture-path tests/fixtures/rss_sample.xml` executa ingest determinística.
- [x] Script `./scripts/ingest_source_demo.sh` encapsula o fluxo end-to-end usando `.venv`.

## Dados visíveis no Explore
- [x] `tests/integration/test_ingest_explore_roundtrip.py::test_ingest_fixture_and_query` ingere fixture e valida que `/explore/items` retorna registros com `fields`.

## Logs estruturados
- [x] `inspectah/watchers/rss.py` registra eventos `ingest_started`/`ingest_completed`/`ingest_failed` via `logging` com metadados (source, fixture, itens).
- [x] `inspectah/explore/api.py` registra `explore_query`, `explore_get_item` e `explore_list_sources` com parâmetros e duração (sem payload).

## Métricas e observabilidade
- [x] `inspectah/metrics.py` agora expõe `inspectah_ingest_items_total`, `inspectah_ingest_errors_total`, `inspectah_explore_queries_total`.
- [x] `tests/integration/test_ingest_explore_roundtrip.py` cobre ingest+explore e checa métricas.
- [x] Comando de observação documentado: `PYTHONPATH=$PWD ./.venv/bin/python - <<'PY'\nfrom inspectah.metrics import get_snapshot\nprint(get_snapshot())\nPY`.

## Testes e scripts
- [x] `PYTHONPATH=$PWD ./.venv/bin/pytest tests/unit/test_ingest_pipeline.py tests/integration/test_ingest_explore_roundtrip.py` verdes.
- [x] `./scripts/ingest_source_demo.sh` roda sem erro e produz itens visíveis via Explore.
- [x] `PYTHONPATH=$PWD ./.venv/bin/pytest` (suite completa) reexecutado após ajustes finais de T7/T8.

## Status do Gate
- [x] Checklist completo.
- [x] `evidence_s2/s2_summary_gate_matrix.json` atualizado para S2-G4 = PASS (apenas quando todos os itens acima estiverem `[x]`).
