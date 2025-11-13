#!/usr/bin/env python3
from __future__ import annotations
import json
import time
from pathlib import Path
BASE = Path(__file__).resolve().parents[2]
trace = {
  "trace_id": "trace-1",
  "root": {
    "span": "api_call",
    "start": time.time(),
    "duration_ms": 60,
    "children": [
      {"span": "vault", "duration_ms": 25, "children": [{"span": "db_write", "duration_ms": 10, "children": []}]},
      {"span": "fts", "duration_ms": 18, "children": []},
      {"span": "export", "duration_ms": 22, "children": []}
    ]
  }
}
out = BASE / 'out/evidence/T6_obs'
out.mkdir(parents=True, exist_ok=True)
(out / 'traces.json').write_text(json.dumps([trace], indent=2), encoding='utf-8')
