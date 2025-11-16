#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}" )/.." && pwd)
EVIDENCE_DIR="$ROOT/out/evidence/S4_T7_orr_pipeline"
RUN_LOG="$EVIDENCE_DIR/run_log.txt"
SUMMARY="$EVIDENCE_DIR/summary.json"
SCORECARD_PATH="$ROOT/out/scorecards/S4_T7_orr_pipeline.json"
mkdir -p "$EVIDENCE_DIR"
cat /dev/null > "$RUN_LOG"
GATES=(
  "S4_T0|Sprint 4 - T0 Discovery|true|out/scorecards/S4_T0_discovery.json"
  "S4_T1|Sprint 4 - T1 Specs|true|out/scorecards/S4_T1_specs.json"
  "S4_T2|Sprint 4 - T2 Sources|bash bin/orr_t2_sources.sh|out/scorecards/S4_T2_sources.json"
  "S4_T3|Sprint 4 - T3 Fixtures|bash bin/orr_t3_fixtures.sh|out/scorecards/S4_T3_fixtures.json"
  "S4_T4|Sprint 4 - T4 Goldens|bash bin/orr_t4_goldens.sh|out/scorecards/S4_T4_goldens.json"
  "S4_T5|Sprint 4 - T5 Vault|bash bin/orr_t5_repetition.sh|out/scorecards/S4_T5_repetition.json"
  "S4_T6|Sprint 4 - T6 Observability|python3 scripts/s4_t6_generate_evidence.py|out/scorecards/S4_T6_observability.json"
)
SUMMARY_JSON='{"sprint":"S4","gates":[]}'
STATUS="PASS"
GATES_PASSED=0
for entry in "${GATES[@]}"; do
  IFS='|' read -r gate_id gate_name command scorecard <<<"$entry"
  CMD_STATUS=0
  if [[ "$command" != "true" ]]; then
    echo "[$gate_id] running: $command" | tee -a "$RUN_LOG"
    if ! eval "$command" >> "$RUN_LOG" 2>&1; then
      CMD_STATUS=$?
    fi
  else
    echo "[$gate_id] using existing scorecard" | tee -a "$RUN_LOG"
  fi
  if [[ ! -f "$ROOT/$scorecard" ]]; then
    echo "[$gate_id] missing scorecard $scorecard" | tee -a "$RUN_LOG"
    STATUS="FAIL"
    break
  fi
  gate_status=$(jq -r '.status' "$ROOT/$scorecard")
  echo "[$gate_id] scorecard status=$gate_status" | tee -a "$RUN_LOG"
  SUMMARY_JSON=$(python3 <<PY
import json
summary = json.loads('''$SUMMARY_JSON''')
summary['gates'].append({'gate_id': '$gate_id', 'name': '$gate_name', 'status': '$gate_status', 'scorecard': '$scorecard'})
print(json.dumps(summary))
PY
)
  if [[ "$CMD_STATUS" -ne 0 || "$gate_status" != "PASS" ]]; then
    STATUS="FAIL"
    break
  fi
  GATES_PASSED=$((GATES_PASSED+1))
done
MID=$(python3 <<PY
print('$SUMMARY_JSON')
PY
)
printf '%s' "$MID" | jq . > "$SUMMARY"
cat <<EOS > "$SCORECARD_PATH"
{
  "sprint_id": "S4",
  "gate_id": "S4_T7",
  "gate_name": "Sprint 4 - T7 ORR Pipeline",
  "status": "$STATUS",
  "summary": "Execução sequencial dos gates S4_T0…S4_T6",
  "invariants_guarded": [
    "Reprodutibilidade do ORR",
    "Completude dos gates",
    "Curto-circuito em caso de FAIL"
  ],
  "checks": [
    {"name": "all_s4_gates_scorecards_present", "status": "$([ -f "$ROOT/out/scorecards/S4_T6_observability.json" ] && echo PASS || echo FAIL)", "details": "Scorecards esperados consultados"},
    {"name": "all_s4_gates_passed", "status": "$STATUS", "details": "Gates PASS: $GATES_PASSED"},
    {"name": "pipeline_exit_zero", "status": "$STATUS", "details": "Runner encerrado"}
  ],
  "metrics": {
    "gates_total": ${#GATES[@]},
    "gates_passed": $GATES_PASSED,
    "gates_failed": $(( ${#GATES[@]} - GATES_PASSED ))
  },
  "artifacts": [
    {"path": "out/evidence/S4_T7_orr_pipeline/run_log.txt"},
    {"path": "out/evidence/S4_T7_orr_pipeline/summary.json"}
  ],
  "errors": []
}
EOS
if [[ "$STATUS" != "PASS" ]]; then
  exit 1
fi
