#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
PYTHON_BIN="$REPO_ROOT/.venv/bin/python3"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="$(command -v python3)"
fi

SCORECARD="$REPO_ROOT/out/scorecards/S6_G8_sprint_go_no_go.json"
EVIDENCE_DIR="$REPO_ROOT/out/evidence/S6_G8_sprint_go_no_go"
mkdir -p "$(dirname "$SCORECARD")" "$EVIDENCE_DIR"

CARD_PATHS=(
  "$REPO_ROOT/out/scorecards/S6_G0_domain_setup.json"
  "$REPO_ROOT/out/scorecards/S6_G1_sources_registry.json"
  "$REPO_ROOT/out/scorecards/S6_G2_field_designer.json"
  "$REPO_ROOT/out/scorecards/S6_G3_collect_evidence.json"
  "$REPO_ROOT/out/scorecards/S6_G4_explore_verify.json"
  "$REPO_ROOT/out/scorecards/S6_G5_metrics_obs.json"
  "$REPO_ROOT/out/scorecards/S6_G6_bundle_repro.json"
  "$REPO_ROOT/out/scorecards/S6_G7_guard_automation.json"
)

SUMMARY_MD="$EVIDENCE_DIR/summary.md"
FINAL_STATUS=$(
"$PYTHON_BIN" - "$SCORECARD" "$SUMMARY_MD" "${CARD_PATHS[@]}" <<'PY'
import json, sys
scorecard_path, summary_md, *paths = sys.argv[1:]
statuses = {}
with open(summary_md, 'w', encoding='utf-8') as summary:
    for path in paths:
        try:
            data = json.load(open(path, encoding='utf-8'))
            status = data.get('status', 'MISSING')
        except FileNotFoundError:
            status = 'MISSING'
        summary.write(f"{path}: {status}\n")
        statuses[path] = status
final = 'GO' if all(status == 'PASS' for status in statuses.values()) else 'NO_GO'
json.dump({
    "gate": "S6_G8",
    "name": "sprint_go_no_go",
    "status": final,
    "details": {
        "gates": statuses,
    },
}, open(scorecard_path, 'w', encoding='utf-8'), indent=2)
print(final)
PY
)

echo "Decision: $FINAL_STATUS" >> "$SUMMARY_MD"

if [[ "$FINAL_STATUS" != "GO" ]]; then
  exit 1
fi
