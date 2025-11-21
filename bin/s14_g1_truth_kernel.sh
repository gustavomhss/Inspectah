#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ! -d "$ROOT_DIR/.git" ]]; then
  >&2 echo "[S14] Rode a partir da raiz do repo (faltou .git)."
  exit 2
fi

SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S14_G1"
SCORECARD_PATH="$SCORECARD_DIR/S14_G1_truth_kernel.json"
REPORT_PATH="$EVIDENCE_DIR/kernel_integrity_report.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

python3 -m scripts.s14_truth_kernel_checks

if [[ ! -f "$REPORT_PATH" ]]; then
  >&2 echo "[S14_G1] Report não encontrado em $REPORT_PATH"
  exit 1
fi

python3 - <<'PY' "$REPORT_PATH" "$SCORECARD_PATH"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

report_path = Path(sys.argv[1])
scorecard_path = Path(sys.argv[2])
report = json.loads(report_path.read_text(encoding="utf-8"))
metrics = report.get("metrics", {})

kernel_ratio = float(metrics.get("kernel_integrity_ratio", 0.0))
domain_cov = float(metrics.get("domain_coverage_ratio", 0.0))
MIN_KERNEL = 0.95
MIN_DOMAIN = 1.0

status = "PASS"
reasons = []
if kernel_ratio < MIN_KERNEL:
    status = "FAIL"
    reasons.append(f"kernel_integrity_ratio abaixo do SLO ({kernel_ratio} < {MIN_KERNEL})")
if domain_cov < MIN_DOMAIN:
    status = "FAIL"
    reasons.append(f"domain_coverage_ratio abaixo do esperado ({domain_cov} < {MIN_DOMAIN})")

scorecard = {
    "gate": "S14_G1",
    "status": status,
    "kernel_integrity_ratio": kernel_ratio,
    "domain_coverage_ratio": domain_cov,
    "cases_total": metrics.get("cases_total", 0),
    "timeline_events_total": metrics.get("timeline_events_total", 0),
    "notes": reasons,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("S14_G1 falhou; consulte scorecard para detalhes.")
PY

echo "[S14_G1] OK. Scorecard: $SCORECARD_PATH"
