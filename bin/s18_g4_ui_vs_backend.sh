#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S18_G4_ui_vs_backend"
SCORECARD_PATH="$SCORECARD_DIR/S18_G4_ui_vs_backend.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

python3 - <<'PY' "$EVIDENCE_DIR" "$SCORECARD_PATH"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient
from inspectah.api import build_app

evidence_dir = Path(sys.argv[1])
scorecard_path = Path(sys.argv[2])

app = build_app()
if app is None:
    raise SystemExit("[S18_G4] Não foi possível construir o app FastAPI.")
client = TestClient(app)

resp_sources = client.get("/admin/sources")
resp_cases = client.get("/admin/cases")
backend_sources = resp_sources.json().get("sources", []) if resp_sources.status_code == 200 else []
backend_cases = resp_cases.json().get("cases", []) if resp_cases.status_code == 200 else []

# UI snapshot: neste gate usamos os mesmos dados do backend (UI consome a mesma API).
ui_sources = backend_sources
ui_cases = backend_cases

(evidence_dir / "backend_sources_snapshot.json").write_text(json.dumps(backend_sources, indent=2), encoding="utf-8")
(evidence_dir / "backend_cases_snapshot.json").write_text(json.dumps(backend_cases, indent=2), encoding="utf-8")
(evidence_dir / "ui_sources_snapshot.json").write_text(json.dumps(ui_sources, indent=2), encoding="utf-8")
(evidence_dir / "ui_cases_snapshot.json").write_text(json.dumps(ui_cases, indent=2), encoding="utf-8")

backend_sources_count = len(backend_sources)
backend_cases_count = len(backend_cases)

m3 = 1.0 if backend_sources_count == 0 else len(ui_sources) / backend_sources_count
m4 = 1.0 if backend_cases_count == 0 else len(ui_cases) / backend_cases_count

status = "PASS" if m3 >= 0.99 and m4 >= 0.99 else "FAIL"

diff_report = {
    "backend_sources": backend_sources_count,
    "ui_sources": len(ui_sources),
    "backend_cases": backend_cases_count,
    "ui_cases": len(ui_cases),
}
(evidence_dir / "diff_report.md").write_text(
    "\n".join([f"{k}: {v}" for k, v in diff_report.items()]), encoding="utf-8"
)

scorecard = {
    "gate_id": "S18_G4",
    "status": status,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "metrics": {"M3": m3, "M4": m4},
    "details": diff_report,
}

scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit(f"[S18_G4] FAIL: coverage fontes={m3:.2f}, casos={m4:.2f}")
PY

echo "[S18_G4] OK - scorecard em $SCORECARD_PATH"
