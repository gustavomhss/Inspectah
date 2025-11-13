#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="${ORR_OUTDIR:-$ROOT/out}"
EVID_DIR="$OUT_DIR/evidence/T8_orr"
SCORECARD="$OUT_DIR/scorecards/T8_orr.json"
mkdir -p "$EVID_DIR" "$OUT_DIR/scorecards"
REPORT="$EVID_DIR/orr_report.json"
python3 - <<'PY' "$ROOT" "$REPORT" "$SCORECARD"
import hashlib
import json
import os
import sys
from pathlib import Path
root = Path(sys.argv[1])
report_path = Path(sys.argv[2])
scorecard_path = Path(sys.argv[3])
scorecards = [
    ("T0", root / "out/scorecards/T0_sanity.json"),
    ("T2", root / "out/scorecards/T2_unit.json"),
    ("T3", root / "out/scorecards/T3_property.json"),
    ("T4", root / "out/scorecards/T4_golden.json"),
    ("T5", root / "out/scorecards/T5_bench.json"),
    ("T6_T7", root / "out/scorecards/T6_T7.json"),
    ("T7_CI", root / "out/scorecards/T7_ci_full.json"),
]
scorecard_results = []
passed = True
for gate, path in scorecards:
    item = {"gate": gate, "path": str(path.relative_to(root)), "exists": path.exists(), "passed": False}
    if path.exists():
        try:
            data = json.loads(path.read_text())
            item["passed"] = bool(data.get("passed"))
        except json.JSONDecodeError as exc:
            item["error"] = str(exc)
            passed = False
        else:
            if not item["passed"]:
                passed = False
    else:
        passed = False
    scorecard_results.append(item)
checksum_files = sorted(root.glob('out/CHECKSUMS_D*.sha256'))
checksum_results = []
for chk in checksum_files:
    entries = []
    with chk.open() as fh:
        for line in fh:
            parts = line.strip().split(maxsplit=1)
            if len(parts) != 2:
                continue
            expected, rel = parts
            target = root / rel
            if not target.exists():
                entries.append({"file": rel, "status": "missing"})
                passed = False
                continue
            actual = hashlib.sha256(target.read_bytes()).hexdigest()
            status = "passed" if actual == expected else "failed"
            if status == "failed":
                passed = False
            entries.append({"file": rel, "expected": expected, "actual": actual, "status": status})
    checksum_results.append({"file": str(chk.relative_to(root)), "entries": entries})
manifest_files = sorted((root / 'out/evidence').glob('D*/MANIFEST*.json'))
manifest_results = []
for manifest in manifest_files:
    try:
        json.loads(manifest.read_text())
        manifest_results.append({"path": str(manifest.relative_to(root)), "valid": True})
    except json.JSONDecodeError as exc:
        manifest_results.append({"path": str(manifest.relative_to(root)), "valid": False, "error": str(exc)})
        passed = False
runner_paths = sorted((root / 'bin').glob('orr_*.sh'))
runner_results = []
for runner in runner_paths:
    exec_ok = os.access(runner, os.X_OK)
    runner_results.append({"path": str(runner.relative_to(root)), "executable": exec_ok})
    if not exec_ok:
        passed = False
report = {
    "scorecards": scorecard_results,
    "checksums": checksum_results,
    "manifests": manifest_results,
    "runners": runner_results
}
report_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
scorecard = {
    "gate": "T8_ORR",
    "version": "1.0",
    "passed": passed,
    "artifacts": [
        {"path": str(report_path.relative_to(root))}
    ],
    "notes": "Operational Readiness Review"
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding='utf-8')
if not passed:
    sys.exit(1)
PY
echo "ORR final checks completed."
