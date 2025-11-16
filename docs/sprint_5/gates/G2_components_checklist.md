# G2 Components Checklist

- [ ] `inspectah/watchers/*` sincronizados na raiz e com fontes dummy configuradas.
- [ ] `inspectah/evidence/builder.py` e `inspectah/evidence/verifier.py` usando schemas promovidos.
- [ ] `inspectah/normalizer/normalizer.py` + `client_ai.py` revisados (modo stub e AI) com fixtures.
- [ ] `inspectah/indexer/indexer.py` e `query_api.py` expostos para testes componentizados.
- [ ] Rodar `bin/s5_gate_g2_components.sh` garantindo PASS e scorecard em `out/s5_gates/G2_components/`.
