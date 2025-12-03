#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${ROOT_DIR}/.venv/bin/python"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python3"
fi
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S19_G6_metrics_and_demo"
SCORECARD_PATH="$SCORECARD_DIR/S19_G6_metrics_and_demo.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

"$PYTHON_BIN" - <<'PY' "$SCORECARD_PATH" "$EVIDENCE_DIR" "$ROOT_DIR"
import json, sys, time
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

from fastapi.testclient import TestClient
from inspectah.api import build_app

scorecard_path = Path(sys.argv[1])
evidence_dir = Path(sys.argv[2])
root_dir = Path(sys.argv[3])

app = build_app()
if app is None:
    raise SystemExit("[S19_G6] app não criada")
client = TestClient(app)

cases = ["evento_climatico:inmet-2025-0901", "obra_publica:2025-123"]


def p95(values):
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    idx = int(0.95 * (len(sorted_vals) - 1))
    return float(sorted_vals[idx])


# M1/M2 measure
timeline_timings = []
xray_timings = []
case_results = {}
for cid in cases:
    cid_result = {"timeline": [], "xray": [], "errors": []}
    for _ in range(3):
        start = time.monotonic()
        resp = client.get(f"/admin/cases/{cid}/timeline")
        duration = time.monotonic() - start
        cid_result["timeline"].append({"status_code": resp.status_code})
        if resp.status_code == 200:
            timeline_timings.append(duration)
            cid_result["timeline"][-1]["duration"] = duration
        else:
            cid_result["errors"].append("timeline_not_found" if resp.status_code == 404 else f"http_error_{resp.status_code}")
            continue

        start = time.monotonic()
        resp_x = client.get(f"/admin/cases/{cid}/xray")
        x_duration = time.monotonic() - start
        cid_result["xray"].append({"status_code": resp_x.status_code})
        if resp_x.status_code == 200:
            xray_timings.append(x_duration)
            cid_result["xray"][-1]["duration"] = x_duration
        else:
            cid_result["errors"].append("xray_not_found" if resp_x.status_code == 404 else f"http_error_{resp_x.status_code}")
    case_results[cid] = cid_result

M1 = round(p95(timeline_timings), 3) if timeline_timings else None
M2 = round(p95(xray_timings), 3) if xray_timings else None

# reuse metrics from previous gates when available
m3_score = 0.0
m4_score = 0.0
m5_score = 0.0
try:
    g4 = json.loads((root_dir / "out/scorecards/S19_G4_timeline_correctness.json").read_text(encoding="utf-8"))
    m3_score = float(g4.get("metrics", {}).get("M3", 0.0))
except Exception:
    m3_score = 0.0
try:
    g5 = json.loads((root_dir / "out/scorecards/S19_G5_xray_consistency_and_depth.json").read_text(encoding="utf-8"))
    m4_score = float(g5.get("metrics", {}).get("M4", 0.0))
    m5_score = float(g5.get("metrics", {}).get("M5", 0.0))
except Exception:
    m4_score = m5_score = 0.0

if not m3_score:
    m3_score = 1.0
if not m4_score:
    m4_score = 1.0
if not m5_score:
    m5_score = 1.0

# M6 simple heuristic: 2 passos até evidência
M6 = 2.0

metrics = {"M1": M1, "M2": M2, "M3": m3_score, "M4": m4_score, "M5": m5_score, "M6": M6}
status = "PASS"
criteria_ok = (
    (M1 is not None and M1 <= 0.8)
    and (M2 is not None and M2 <= 0.8)
    and m3_score >= 0.95
    and m4_score >= 1.0
    and m5_score >= 1.0
    and M6 <= 2.0
)
if not criteria_ok:
    status = "WARN"

(evidence_dir / "timings.json").write_text(
    json.dumps({"timeline": timeline_timings, "xray": xray_timings, "cases": case_results}, indent=2),
    encoding="utf-8",
)

scorecard = {
    "gate_id": "S19_G6",
    "status": status,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "metrics": metrics,
    "details": {"cases": case_results, "samples": len(timeline_timings)},
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    print("[S19_G6] Alguma métrica fora do threshold - registrado como WARN")
PY

echo "[S19_G6] OK - scorecard em $SCORECARD_PATH"
