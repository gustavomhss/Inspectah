#!/usr/bin/env python3
from __future__ import annotations
import json
import time
from pathlib import Path
BASE = Path(__file__).resolve().parents[2]
LEVELS = ["INFO", "WARN", "ERROR"]
logs = []
for idx in range(12):
    logs.append({
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "level": LEVELS[idx % len(LEVELS)],
        "service": "inspectah",
        "event": f"event-{idx}",
        "payload": {"request_id": f"req-{idx}", "status": "ok"}
    })
out = BASE / 'out/evidence/T6_obs'
out.mkdir(parents=True, exist_ok=True)
(out / 'logs.json').write_text(json.dumps(logs, indent=2), encoding='utf-8')
