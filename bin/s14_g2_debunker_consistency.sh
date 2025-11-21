#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ! -d "$ROOT_DIR/.git" ]]; then
  >&2 echo "[S14] Rode a partir da raiz do repo (faltou .git)."
  exit 2
fi

SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S14_G2"
SCORECARD_PATH="$SCORECARD_DIR/S14_G2_debunker_consistency.json"
REPORT_PATH="$EVIDENCE_DIR/debunker_consistency_report.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

python3 -m scripts.s14_debunker_consistency

if [[ ! -f "$REPORT_PATH" ]]; then
  >&2 echo "[S14_G2] Report não encontrado em $REPORT_PATH"
  exit 1
fi

python3 - <<'PY' "$REPORT_PATH" "$SCORECARD_PATH"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

report_path = Path(sys.argv[1])
scorecard_path = Path(sys.argv[2])
report = json.loads(report_path.read_text(encoding="utf-8"))

defaults = (report.get("config") or {}).get("defaults", {})
pass_thresh = float(defaults.get("coverage_pass", 0.95))
warn_thresh = float(defaults.get("coverage_warn", 0.9))

metrics = report.get("metrics", {})
global_metrics = metrics.get("global", {})
global_cov = float(global_metrics.get("explanation_coverage", 0.0))

per_domain = metrics.get("per_domain", {}) or {}
domain_cov = {
    dom: float(data.get("explanation_coverage", 0.0))
    for dom, data in per_domain.items()
}

status = "PASS"
reasons = []

if global_cov < warn_thresh:
    status = "FAIL"
    reasons.append(f"coverage global abaixo de WARN ({global_cov} < {warn_thresh})")
elif global_cov < pass_thresh:
    status = "WARN"
    reasons.append(f"coverage global em WARN ({global_cov} < {pass_thresh})")

for dom, cov in domain_cov.items():
    target = float((report.get("config", {}).get("domain_targets", {}).get(dom, {}) or {}).get("coverage_target", warn_thresh))
    if cov < warn_thresh:
        status = "FAIL"
        reasons.append(f"{dom}: coverage abaixo de WARN ({cov} < {warn_thresh})")
    elif status != "FAIL" and cov < target:
        status = "WARN"
        reasons.append(f"{dom}: coverage abaixo do alvo ({cov} < {target})")

scorecard = {
    "gate": "S14_G2",
    "status": status,
    "global_explanation_coverage": global_cov,
    "per_domain": domain_cov,
    "reasons": reasons,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status == "FAIL":
    raise SystemExit("S14_G2 falhou; veja scorecard para detalhes.")
PY

echo "[S14_G2] Status registrado em $SCORECARD_PATH"
