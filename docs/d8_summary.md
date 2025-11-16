# D8 Summary — rss_news_minimal Vertical Slice

## 1. Overview
- Inspectah remains a Data Hub–first pipeline: registry ➜ watcher ➜ Evidence Vault ➜ Field Designer ➜ Explore, all running deterministically on SQLite + local filesystem.
- D8 delivers a single canonical RSS source (`rss_news_minimal`) wired end-to-end, including typed fields (`title`, `url`, `published_at`, `source_name`) and deterministic manifests + SHA-256 evidence bundles.
- Every gate (T0–T7) executes 100% offline using fixtures under `tests/fixtures/`, and all smoke/CI tooling (`bin/d8_ci.sh`) stays local.
- Metrics for watcher runs and explore queries are captured via `inspectah.metrics` and persisted with each smoke run for later gates.

## 2. Gates and Evidence
| Gate | Purpose | Key Evidence |
| --- | --- | --- |
| T0_spec | Slice spec + DNA alignment | `docs/d8_spec.md`, `out/evidence/T0_spec/`, `out/scorecards/T0_spec.json` |
| T1_structure | Package layout + static checks | `out/evidence/T1_structure/`, `out/scorecards/T1_structure.json` |
| T2_unit | Field transforms + registry loaders | `tests/unit/*`, `bin/orr_t2.sh`, `out/evidence/T2_unit/`, `out/scorecards/T2_unit.json` |
| T3_contract | Watcher + Explore contract (fixtures only) | `tests/contract/test_watcher_rss_news_minimal.py`, `tests/integration/test_explore_api.py`, `bin/orr_t3.sh`, `out/evidence/T3_contract/`, `out/scorecards/T3_contract.json` |
| T4_golden | D8 smoke bundle + manifest | `bin/d8_ci.sh`, `bin/orr_t4.sh`, `out/evidence/D8_latest_bundle.json`, `out/evidence/T4_golden/`, `out/scorecards/T4_golden.json` |
| T5_metrics | Metrics snapshot + validation | `tests/integration/test_metrics_d8.py`, `bin/orr_t5.sh`, `out/evidence/D8_latest_metrics.json`, `out/evidence/T5_metrics/`, `out/scorecards/T5_metrics.json` |
| T6_ci | Aggregated CI readiness | `bin/orr_t6.sh`, `out/evidence/T6_ci/`, `out/scorecards/T6_ci.json` |
| T7_ready | Demo readiness + bundle pointer | `bin/orr_t7.sh`, `out/evidence/T7_ready/`, `out/scorecards/T7_ready.json` |

Additional smoke artifacts:
- Latest bundle descriptor: `out/evidence/D8_latest_bundle.json` (points to `out/evidence/D8_smoke_bundle_<timestamp>.zip` and its SHA).
- Latest metrics snapshot: `out/evidence/D8_latest_metrics.json` (mirrors `out/evidence/T5_metrics/metrics.json`).

## 3. How to Run D8 End-to-End (Local)
1. Ensure Python 3.11+ env with dependencies from `pyproject.toml` installed.
2. From repo root, run `bin/d8_ci.sh`. The script runs gates T0–T3, reruns the watcher against the RSS fixture, executes a sample Explore query, captures metrics, and produces:
   - `out/scorecards/D8_ci.json`
   - `out/evidence/D8_smoke_run_<timestamp>/` + `D8_smoke_bundle_<timestamp>.zip`
3. Optional manual watcher run:
   - Fixture mode: `bin/run_watcher_once.sh rss_news_minimal tests/fixtures/rss_sample.xml`
   - Live HTTP mode: `bin/run_watcher_once.sh rss_news_minimal` (ensure the registry URL points to a reachable RSS feed before running).
4. Optional Explore inspection:
   - Start FastAPI app: `uvicorn inspectah.api:build_app --factory --reload`
   - Query endpoints: `GET /explore/items`, `GET /explore/items/{item_id}` to view typed fields and manifest links.
5. For gate-by-gate validation, invoke `bin/orr_tN.sh` scripts (T0–T8) individually; each writes evidence under `out/evidence/TN_*` and scorecards under `out/scorecards/`.

## 4. Artifacts and Paths
- Smoke scorecard: `out/scorecards/D8_ci.json`
- Latest bundle descriptor: `out/evidence/D8_latest_bundle.json`
- Latest bundle ZIP + manifest: `out/evidence/D8_smoke_bundle_<timestamp>.zip`, `out/evidence/D8_smoke_run_<timestamp>/MANIFEST.json`
- Metrics snapshot: `out/evidence/D8_latest_metrics.json` and `out/evidence/T5_metrics/metrics.json`
- Gate scorecards: `out/scorecards/T0_spec.json`, `T1_structure.json`, `T2_unit.json`, `T3_contract.json`, `T4_golden.json`, `T5_metrics.json`, `T6_ci.json`, `T7_ready.json`

## 5. Limitations and Next Steps
- D8 handles only one source (`rss_news_minimal`); multi-source orchestration, backpressure, and rule engines remain future work.
- Explore API is read-only JSON with basic filters; richer UI/FTS/search facets land in later waves.
- Metrics are kept as in-process JSON snapshots; a full Prometheus/OpenMetrics endpoint and alerting are slated for D9+.
- Evidence Vault stores HTML/text/manifest bundles locally; distribution, dedup across hosts, and retention policies are still TODO per Bloco 3.
- Next steps (per Sprint Macro + DNA): add more source types, automate scheduling/bridge layers, expand Field Designer and Explore UX, and integrate the slice into broader ORR/CI pipelines for D9–D12.
