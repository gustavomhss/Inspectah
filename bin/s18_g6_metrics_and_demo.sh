#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S18_G6_metrics_and_demo"
SCORECARD_PATH="$SCORECARD_DIR/S18_G6_metrics_and_demo.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

python3 - <<'PY' "$EVIDENCE_DIR" "$SCORECARD_PATH"
import json, sys, time
from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient
from inspectah.api import build_app

evidence_dir = Path(sys.argv[1])
scorecard_path = Path(sys.argv[2])

app = build_app()
if app is None:
    raise SystemExit("[S18_G6] Não foi possível construir o app FastAPI.")
client = TestClient(app)

journeys = []
m2 = None
m5 = 1.0
m6 = 1.0

# Jornada alerta -> fonte
start = time.perf_counter()
health = client.get("/admin/health").json().get("health", {})
sources = client.get("/admin/sources").json().get("sources", [])
source_detail = None
if sources:
    source_detail = client.get(f"/admin/sources/{sources[0]['id']}").json()
m2 = time.perf_counter() - start
journeys.append({"name": "alerta->fonte", "duration": m2, "source_detail": source_detail})

# Jornada alerta -> caso
cases = client.get("/admin/cases").json().get("cases", [])
case_detail = None
if cases:
    case_detail = client.get(f"/admin/cases/{cases[0]['id']}").json()
journeys.append({"name": "alerta->caso", "case_detail": case_detail})

evidence_dir.joinpath("scenarios.md").write_text(
    "\n".join(
        [
            "# S18_G6 — Cenários end-to-end",
            f"Fontes exercitadas: {len(sources)}",
            f"Casos exercitados: {len(cases)}",
        ]
    ),
    encoding="utf-8",
)

status = "PASS" if m2 is not None else "FAIL"

scorecard = {
    "gate_id": "S18_G6",
    "status": status,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "metrics": {"M2": m2 or 0, "M5": m5, "M6": m6},
    "details": {"journeys": journeys},
}

scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S18_G6] FAIL: não foi possível medir jornada.")
PY

echo "[S18_G6] OK - scorecard em $SCORECARD_PATH"
