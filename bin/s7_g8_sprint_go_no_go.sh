#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
PYTHON_BIN="$REPO_ROOT/.venv/bin/python3"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="$(command -v python3)"
fi

REPO_ROOT="$REPO_ROOT" "$PYTHON_BIN" - <<'PY'
from __future__ import annotations

import json
import os
from pathlib import Path

slug = "S7_G8_sprint_go_no_go"
repo_root = Path(os.environ["REPO_ROOT"])
scorecard_path = repo_root / "out" / "scorecards" / f"{slug}.json"
evidence_dir = repo_root / "out" / "evidence" / slug
scorecard_path.parent.mkdir(parents=True, exist_ok=True)
evidence_dir.mkdir(parents=True, exist_ok=True)

gates = [
    "S7_G0_baseline",
    "S7_G1_ui_boot_health",
    "S7_G2_ui_sources_admin",
    "S7_G3_ui_fields_preview",
    "S7_G4_ui_query_consolidation",
    "S7_G5_ui_evidence_trace",
    "S7_G6_ui_only_flows",
    "S7_G7_metrics_and_demo",
]

results = {}
failed = []
for name in gates:
    path = repo_root / "out" / "scorecards" / f"{name}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    results[name] = data
    if data.get("status") != "PASS":
        failed.append(name)

g7_flags = results["S7_G7_metrics_and_demo"].get("flags", {})
metrics_ok = all(g7_flags.values())

decision = "GO" if not failed and metrics_ok else "NO_GO"
details = {
    "failed_gates": failed,
    "flags": g7_flags,
}
scorecard = {
    "gate": "S7_G8",
    "name": "sprint_go_no_go",
    "status": decision,
    "decision": decision,
    "all_gates_pass": not failed,
    "all_metrics_pass": metrics_ok,
    "details": details,
}
scorecard_path.write_text(json.dumps(scorecard, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(evidence_dir / "summary.json").write_text(json.dumps(details, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

if decision != "GO":
    raise SystemExit("Sprint 7 NO_GO")
PY
