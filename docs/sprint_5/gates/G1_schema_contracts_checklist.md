# G1 Schema Contracts Checklist

- [ ] `schemas/inspectah_item_v0_1.json` e `schemas/inspectah_claim_v0_1.json` atualizados com enums S0–S4 e polarity local verdicts.
- [ ] `docs/sprint_5/s5_contracts_overview.md` revisado e alinhado com schemas publicados.
- [ ] `inspectah/equivalence_key.py` sincronizado com contratos (hashes e categorias).
- [ ] `tests/test_schema_item.py`, `tests/test_schema_claim.py` e `tests/test_equivalence_key.py` passando localmente.
- [ ] Rodar `bin/s5_gate_g1_schema_contracts.sh` e anexar scorecard em `out/s5_gates/G1_schema_contracts/`.
