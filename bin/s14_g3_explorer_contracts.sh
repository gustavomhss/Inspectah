#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ! -d "$ROOT_DIR/.git" ]]; then
  >&2 echo "[S14] Rode a partir da raiz do repo (faltou .git)."
  exit 2
fi

SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S14_G3"
SCORECARD_PATH="$SCORECARD_DIR/S14_G3_explorer_contracts.json"
REPORT_PATH="$EVIDENCE_DIR/explorer_contracts_report.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

export PYTHONPATH="$ROOT_DIR"
python3 -m scripts.s14_explorer_contracts

if [[ ! -f "$REPORT_PATH" ]]; then
  >&2 echo "[S14_G3] Report não encontrado em $REPORT_PATH"
  exit 1
fi

python3 - <<'PY' "$REPORT_PATH" "$SCORECARD_PATH"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

report_path = Path(sys.argv[1])
scorecard_path = Path(sys.argv[2])
report = json.loads(report_path.read_text(encoding="utf-8"))

metrics = report.get("metrics", {})
global_ratio = float(metrics.get("explorer_contract_success_ratio", 0.0))
per_domain = metrics.get("per_domain_explorer_contract_ratio", {}) or {}

PASS_THRESHOLD = 0.95
WARN_THRESHOLD = 0.9
status = "PASS"
reasons = []

if global_ratio < WARN_THRESHOLD:
    status = "FAIL"
    reasons.append(f"explorer_contract_success_ratio abaixo de {WARN_THRESHOLD}")
elif global_ratio < PASS_THRESHOLD:
    status = "WARN"
    reasons.append(f"explorer_contract_success_ratio em WARN ({global_ratio})")

for domain, ratio in per_domain.items():
    if ratio < WARN_THRESHOLD:
        status = "FAIL"
        reasons.append(f"Domain {domain} abaixo de {WARN_THRESHOLD} ({ratio})")
    elif status != "FAIL" and ratio < PASS_THRESHOLD:
        status = "WARN"
        reasons.append(f"Domain {domain} em WARN ({ratio})")

scorecard = {
    "gate": "S14_G3",
    "status": status,
    "explorer_contract_success_ratio": global_ratio,
    "per_domain_explorer_contract_ratio": per_domain,
    "reasons": reasons,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status == "FAIL":
    raise SystemExit("S14_G3 falhou; consulte scorecard.")
PY

echo "[S14_G3] Status registrado em $SCORECARD_PATH"
