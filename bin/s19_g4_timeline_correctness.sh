#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${ROOT_DIR}/.venv/bin/python"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python3"
fi
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S19_G4_timeline_correctness"
SCORECARD_PATH="$SCORECARD_DIR/S19_G4_timeline_correctness.json"
FIXTURE_DIR="$ROOT_DIR/Sprint 19/fixtures"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

"$PYTHON_BIN" - <<'PY' "$FIXTURE_DIR" "$SCORECARD_PATH" "$EVIDENCE_DIR"
import json, sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

from fastapi.testclient import TestClient
from inspectah.api import build_app

fixtures_dir = Path(sys.argv[1])
scorecard_path = Path(sys.argv[2])
evidence_dir = Path(sys.argv[3])

app = build_app()
if app is None:
    raise SystemExit("[S19_G4] app não criada")
client = TestClient(app)

results = {}
for fixture_path in sorted(fixtures_dir.glob("timeline_expected_*.json")):
    data = json.loads(fixture_path.read_text(encoding="utf-8"))
    case_id = data.get("case_id")
    expected_events = data.get("events") or []
    resp = client.get(f"/admin/cases/{case_id}/timeline")
    payload = resp.json() if resp.content else {}
    (evidence_dir / f"timeline_{fixture_path.stem}.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    actual_events = payload.get("timeline", {}).get("events", [])
    expected_ids = {ev.get("id") for ev in expected_events if ev.get("id")}
    actual_ids = {ev.get("id") for ev in actual_events if ev.get("id")}
    matched = expected_ids & actual_ids
    missing = sorted(expected_ids - actual_ids)
    extra = sorted(actual_ids - expected_ids)
    coverage = len(matched) / len(expected_ids) if expected_ids else 1.0
    results[case_id] = {
        "M3_case": round(coverage, 3),
        "missing_events": missing,
        "extra_events": extra,
        "status_code": resp.status_code,
    }

m3_values = [entry["M3_case"] for entry in results.values()]
M3_global = round(mean(m3_values), 3) if m3_values else 1.0
status = "PASS" if all(v >= 0.9 for v in m3_values) and M3_global >= 0.95 else "FAIL"

scorecard = {
    "gate_id": "S19_G4",
    "status": status,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "metrics": {"M3": M3_global},
    "details": {"cases": results},
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S19_G4] Cobertura da timeline abaixo do esperado")
PY

echo "[S19_G4] OK - scorecard em $SCORECARD_PATH"
