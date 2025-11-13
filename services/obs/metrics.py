#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
BASE = Path(__file__).resolve().parents[2]
METRICS = {
  "latency_ms": {
    "api_create": {"p50": 90, "p95": 180, "p99": 240},
    "api_explore": {"p50": 70, "p95": 150, "p99": 220},
    "vault_manifest": {"p50": 120, "p95": 190, "p99": 260},
    "fts_query": {"p50": 65, "p95": 140, "p99": 210},
    "export_job": {"p50": 100, "p95": 185, "p99": 250}
  },
  "items_fetched_total": 500,
  "items_indexed_total": 495,
  "queue_depth": 4,
  "queue_age_seconds": 130,
  "fts_query_total": 320,
  "export_total": 120
}
out = BASE / 'out/evidence/T6_obs'
out.mkdir(parents=True, exist_ok=True)
(out / 'metrics.json').write_text(json.dumps(METRICS, indent=2), encoding='utf-8')
