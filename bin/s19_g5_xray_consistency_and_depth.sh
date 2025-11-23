#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${ROOT_DIR}/.venv/bin/python"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python3"
fi
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S19_G5_xray_consistency_and_depth"
SCORECARD_PATH="$SCORECARD_DIR/S19_G5_xray_consistency_and_depth.json"
FIXTURE_DIR="$ROOT_DIR/Sprint 19/fixtures"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

"$PYTHON_BIN" - <<'PY' "$FIXTURE_DIR" "$SCORECARD_PATH" "$EVIDENCE_DIR"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient
from inspectah.api import build_app

fixtures_dir = Path(sys.argv[1])
scorecard_path = Path(sys.argv[2])
evidence_dir = Path(sys.argv[3])

app = build_app()
if app is None:
    raise SystemExit("[S19_G5] app não criada")
client = TestClient(app)

required_sections = ["summary", "debunker", "committees", "anchors", "evidences"]
results = {}

for fixture_path in sorted(fixtures_dir.glob("xray_expected_*.json")):
    expected = json.loads(fixture_path.read_text(encoding="utf-8"))
    case_id = expected.get("case_id")
    resp = client.get(f"/admin/cases/{case_id}/xray")
    payload = resp.json() if resp.content else {}
    (evidence_dir / f"xray_{fixture_path.stem}.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    xray = payload.get("xray", {})
    sections_ok = [sec for sec in required_sections if xray.get(sec)]
    completeness = len(sections_ok) / len(required_sections)
    explanation_texts = [
        str(xray.get("debunker", {}).get("explanation", "")),
        str(xray.get("committees", {}).get("summary", "")),
        str(xray.get("anchors", {}).get("summary", "")),
    ]
    explanation_ok = all(len(text.strip()) >= 20 for text in explanation_texts)
    results[case_id] = {
        "M4_case": round(completeness, 3),
        "M5_case": 1.0 if explanation_ok else 0.0,
        "status_code": resp.status_code,
        "sections_ok": sections_ok,
    }

m4 = min((entry["M4_case"] for entry in results.values()), default=1.0)
m5 = min((entry["M5_case"] for entry in results.values()), default=1.0)
status = "PASS" if m4 >= 1.0 and m5 >= 1.0 else "FAIL"

scorecard = {
    "gate_id": "S19_G5",
    "status": status,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "metrics": {"M4": m4, "M5": m5},
    "details": {"cases": results},
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S19_G5] Falha em completude ou explicação do raio-x")
PY

echo "[S19_G5] OK - scorecard em $SCORECARD_PATH"
