# Sprint 33 — Capítulo 4 (execução & evidências)

Estado atual:
- G0 PASS: `out/scorecards/S33_G0_scope_and_baseline.json`, evidência `out/evidence/S33_G0_scope_and_baseline/run.log`.
- G1 PASS: `out/scorecards/S33_G1_incidents.json`, evidência `out/evidence/S33_G1_incidents/run.log` (pytest com venv).
- G2 PASS (API cockpit): `out/scorecards/S33_G2_cockpit.json`, evidência `out/evidence/S33_G2_cockpit/run.log`.
- G3 PASS: `out/scorecards/S33_G3_slos.json`, evidência `out/evidence/S33_G3_slos/run.log`.

Artefatos implementados:
- `Programa 1/Sprint 33/s33_scope_ops.md`, `s33_components_map.yaml`, `s33_slos.md`.
- Domínio Incident: `app/ops/incidents.py`, migração `migrations/versions/0035_s33_incidents.py`, API `app/api/ops_incidents_routes.py`.
- Cockpit API/UI: `app/api/ops_cockpit_routes.py`, `frontend/inspectah-ui/src/modules/ops/pages/OpsCockpitPage.tsx`, rota `/admin/ops/cockpit`.
- SLO evaluator: `app/ops/slo_evaluator.py`.

Próximos gates: G4 (runbooks/bundle incidente) e G5 (ORR operacional).
