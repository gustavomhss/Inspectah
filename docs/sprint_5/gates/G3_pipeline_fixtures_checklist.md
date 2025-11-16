# G3 Pipeline Fixtures Checklist

- [ ] Fixtures `fixtures/s5/rss_feed.xml`, `api_feed.json`, `html_page.html` atualizados.
- [ ] `inspectah/pipeline/pipeline_fixtures.py` gerando itens esperados para RSS/API/HTML.
- [ ] `tests/pipeline/test_pipeline_fixtures.py` executado com `tests/golden/s5_pipeline/expected_items_summary.json` alinhado.
- [ ] `bin/s5_check_invariants.sh` ok para watchers + pipeline de S5.
- [ ] Rodar `bin/s5_gate_g3_pipeline_fixtures.sh` e salvar scorecard/logs em `out/s5_gates/G3_pipeline_fixtures/`.
