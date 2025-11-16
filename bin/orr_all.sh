#!/usr/bin/env bash
set -euo pipefail

OUT=${ORR_OUTDIR:-out}
if [[ "$OUT" != /* ]]; then
  OUT="$(pwd)/$OUT"
fi
SUMMARY_DIR="$OUT/evidence/T7_orr_pipeline"
SUMMARY_JSON="$SUMMARY_DIR/orr_summary.json"
SCORECARD="$OUT/scorecards/T7_orr_pipeline.json"
rm -rf "$SUMMARY_DIR"
mkdir -p "$SUMMARY_DIR" "$OUT/scorecards"

declare -a GATES=(
  "T0:bin/orr_t0_spec_lock.sh:out/scorecards/T0_spec_lock.json"
  "T1:bin/orr_t1_schema_check.sh:out/scorecards/T1_schema.json"
  "T2:bin/orr_t2_field_designer_smoke.sh:out/scorecards/T2_field_designer.json"
  "T3:bin/orr_t3_pipeline_invariants.sh:out/scorecards/T3_pipeline_invariants.json"
  "T4:bin/orr_t4_evidence_audit.sh:out/scorecards/T4_evidence_vault.json"
  "T5:bin/orr_t5_performance_gate.sh:out/scorecards/T5_performance.json"
  "T5.1:bin/orr_t5_1_confidence_gate.sh:out/scorecards/T5_1_confidence.json"
  "T6:bin/orr_t6_observability_smoke.sh:out/scorecards/T6_observability.json"
)

SUMMARY_ENTRIES=()
FAILED=0

for entry in "${GATES[@]}"; do
  IFS=":" read -r gate script scorecard <<<"$entry"
  echo "[ORR] Running $gate via $script"
  status="UNKNOWN"
  if "$script"; then
    status="PASS"
  else
    echo "[ORR] Gate $gate returned failure"
    status="FAIL"
    FAILED=1
  fi
  if [[ -f "$scorecard" ]]; then
    status=$(python3 - "$scorecard" <<'PY'
import json, sys
path = sys.argv[1]
data = json.loads(open(path).read())
if data.get('status') == 'PASS' or data.get('passed') is True:
    print('PASS')
else:
    print('FAIL')
PY
)
  else
    status="MISSING"
  fi
  if [[ "$status" != "PASS" ]]; then
    FAILED=1
  fi
  SUMMARY_ENTRIES+=("${gate}|${status}|${scorecard}")
  echo "[ORR] Gate $gate ${status}"
  # small pause to avoid smashing logs simultaneously
  sleep 0.5
 done

python3 - <<'PY' "$SUMMARY_JSON" "$SCORECARD" "$FAILED" "${SUMMARY_ENTRIES[@]}"
import json, sys
summary_path, scorecard_path, failed_flag, *entries = sys.argv[1:]
info = []
for entry in entries:
    gate, status, scorecard = entry.split('|', 2)
    info.append({'gate': gate, 'status': status, 'scorecard': scorecard})
summary = {'gates': info}
with open(summary_path, 'w', encoding='utf-8') as handle:
    json.dump(summary, handle, indent=2)
failed = int(failed_flag)
scorecard = {
    'gate': 'T7',
    'name': 'orr_pipeline',
    'version': 'v1',
    'status': 'FAIL' if failed else 'PASS',
    'timestamp': __import__('datetime').datetime.utcnow().isoformat() + 'Z',
    'metrics': {
        'gates_total': len(info),
        'gates_passed': sum(1 for gate in info if gate['status'] == 'PASS'),
        'gates_failed': sum(1 for gate in info if gate['status'] != 'PASS'),
    },
    'thresholds': {
        'gates_failed': '== 0'
    },
    'details': summary,
}
with open(scorecard_path, 'w', encoding='utf-8') as handle:
    json.dump(scorecard, handle, indent=2)
PY

python3 - <<'PY' "$SUMMARY_DIR"
from pathlib import Path
import hashlib, json, sys
root = Path(sys.argv[1])
files = []
for path in sorted(root.rglob('*')):
    if path.is_file():
        files.append({
            'path': path.relative_to(root).as_posix(),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'bytes': path.stat().st_size,
        })
(root / 'MANIFEST.json').write_text(json.dumps({'files': files}, indent=2), encoding='utf-8')
PY

if [[ "$FAILED" -ne 0 ]]; then
  echo "[ORR] Pipeline FAILED"
  exit 1
fi

echo "[ORR] Pipeline PASS"
