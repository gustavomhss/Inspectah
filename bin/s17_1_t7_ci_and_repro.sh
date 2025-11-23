#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S17_1_T7_ci_and_repro"
SCORECARD_PATH="$SCORECARD_DIR/S17_1_T7_ci_and_repro.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

WORKFLOWS=(
  "$ROOT_DIR/.ci/sprint_17_1_gates.yml"
  "$ROOT_DIR/.ci/sprint_17_1_nightly.yml"
)
GATES_SCRIPT="$ROOT_DIR/bin/s17_1_all_gates.sh"

missing=()
for file in "${WORKFLOWS[@]}"; do
  [[ -f "$file" ]] || missing+=("$file")
done
[[ -x "$GATES_SCRIPT" ]] || missing+=("$GATES_SCRIPT")

status="PASS"
if [[ ${#missing[@]} -gt 0 ]]; then
  status="FAIL"
  printf "%s\n" "${missing[@]}" >"$EVIDENCE_DIR/missing.txt"
fi

cat >"$SCORECARD_PATH" <<EOF
{
  "gate": "S17_1_T7_ci_and_repro",
  "status": "${status}",
  "ts": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF

if [[ "$status" != "PASS" ]]; then
  >&2 echo "[S17_1_T7] Artefatos ausentes: ${missing[*]}"
  exit 1
fi

echo "[S17_1_T7] OK. Scorecard em $SCORECARD_PATH"
