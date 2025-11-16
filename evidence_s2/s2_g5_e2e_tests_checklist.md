# S2-G5 — Tests + E2E Script

**Responsável:** Codex (Sprint 2)
**Última atualização:** 2025-11-14T04:55:00Z

## Scripts
- [x] `./bin/run_inspectah_v0_e2e.sh` — executa dev_up → ingest demo (via pipeline) → Explore → métricas → manifest → dev_down. Saída recente:
  ```
  {'stage': 'ingest', 'items_ingested': 2}
  {'stage': 'explore', 'items_count': 2, 'first_item_id': 1}
  {'stage': 'metrics', 'ingest_items_total': {'count': 2.0, 'min': 0.0, 'max': 0.0, 'avg': 0.0}, 'explore_queries_total': {'count': 1.0, 'min': 0.0, 'max': 0.0, 'avg': 0.0}}
  {'stage': 'manifest', 'manifest_path': '.../manifest.json', 'source_id': 'rss_news_minimal', 'content_hash': 'd8c1ee4fd2ca639e59a2f2a44d707dace592d9d5f7e1cc85ae27d6b5fd3846b2'}
  ```

## Testes
- [x] `PYTHONPATH=$PWD ./.venv/bin/pytest tests/integration/test_e2e_inspectah_v0.py` (1/1 PASS).
- [x] `PYTHONPATH=$PWD ./.venv/bin/pytest` (37/37 PASS após T9).

## Observações
- [x] Checklist concluído e evidências anexadas.
- [x] `evidence_s2/s2_summary_gate_matrix.json` atualizado com S2-G5 = PASS.
