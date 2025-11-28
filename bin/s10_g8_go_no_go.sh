#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S10_G8"
SCORECARD="$SCORECARD_DIR/S10_G8_go_no_go.json"
SUMMARY_FILE="$EVIDENCE_DIR/summary.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
git_commit="$(git -C "$ROOT_DIR" rev-parse HEAD 2>/dev/null || echo "unknown")"
git_branch="$(git -C "$ROOT_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")"

python3 - <<'PY' "$SCORECARD" "$SUMMARY_FILE" "$ts" "$git_commit" "$git_branch"
import json
import sys
from pathlib import Path

scorecard_path, summary_path, ts, commit, branch = sys.argv[1:]

gate_specs = [
    {"id": "S10_G0", "path": "out/scorecards/S10_G0_sanity.json", "allow_warn": False},
    {"id": "S10_G1", "path": "out/scorecards/S10_G1_truthdb_model.json", "allow_warn": True},
    {"id": "S10_G2", "path": "out/scorecards/S10_G2_state_machine.json", "allow_warn": False},
    {"id": "S10_G3", "path": "out/scorecards/S10_G3_guardian_contract.json", "allow_warn": False},
    {"id": "S10_G4", "path": "out/scorecards/S10_G4_mechanical_engine.json", "allow_warn": False},
    {"id": "S10_G5", "path": "out/scorecards/S10_G5_e2e_domain_A.json", "allow_warn": True},
    {"id": "S10_G6", "path": "out/scorecards/S10_G6_e2e_domain_B.json", "allow_warn": True},
    {"id": "S10_G7", "path": "out/scorecards/S10_G7_audit_and_future.json", "allow_warn": True},
]

issues = []
warnings = []
checks = []

for spec in gate_specs:
    gate_file = Path(spec["path"])
    if not gate_file.exists():
        issues.append(f"{spec['id']} sem scorecard ({spec['path']})")
        checks.append(
            {
                "gate_id": spec["id"],
                "status": "MISSING",
                "details": "Scorecard não encontrado",
            }
        )
        continue
    data = json.loads(gate_file.read_text())
    status = data.get("status")
    checks.append({"gate_id": spec["id"], "status": status, "details": spec["path"]})
    if status == "FAIL":
        issues.append(f"{spec['id']} está em FAIL")
    elif status == "WARN":
        if spec["allow_warn"]:
            warnings.append(f"{spec['id']} em WARN")
        else:
            issues.append(f"{spec['id']} não aceita WARN")

decision = "GO" if not issues else "NO_GO"
if decision == "NO_GO":
    exit_code = 1
else:
    exit_code = 0

summary = {
    "warnings": warnings,
    "issues": issues,
    "checks": checks,
}
Path(summary_path).write_text(json.dumps(summary, indent=2), encoding="utf-8")

scorecard = {
    "gate_id": "S10_G8",
    "name": "Sprint 10 GO/NO-GO",
    "decision": decision,
    "checks": checks,
    "warnings": warnings,
    "meta": {"ts": ts, "git_commit": commit, "branch": branch},
}
Path(scorecard_path).write_text(json.dumps(scorecard, indent=2), encoding="utf-8")

sys.exit(exit_code)
PY
