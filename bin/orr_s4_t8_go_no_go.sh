#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}" )/.." && pwd)
export ROOT
EVIDENCE_DIR="$ROOT/out/evidence/S4_T8_go_no_go"
SUMMARY_PATH="$EVIDENCE_DIR/summary.json"
MANIFEST_PATH="$EVIDENCE_DIR/MANIFEST.json"
SCORECARD_PATH="$ROOT/out/scorecards/S4_T8_go_no_go.json"
WRAP="$ROOT/docs/sprint_4_orr_summary.md"
if [[ ! -f "$WRAP" ]]; then
  echo "Wrap humano docs/sprint_4_orr_summary.md não encontrado." >&2
  exit 1
fi
mkdir -p "$EVIDENCE_DIR"
python3 <<'PY'
import json, os, sys, hashlib
root = os.path.abspath(os.environ['ROOT'])
wrap_path = os.path.join(root, 'docs', 'sprint_4_orr_summary.md')
evidence_dir = os.path.join(root, 'out', 'evidence', 'S4_T8_go_no_go')
summary_path = os.path.join(evidence_dir, 'summary.json')
manifest_path = os.path.join(evidence_dir, 'MANIFEST.json')
scorecard_path = os.path.join(root, 'out', 'scorecards', 'S4_T8_go_no_go.json')

gates = [
    ("S4_T0", "Sprint 4 - T0 Discovery", "out/scorecards/S4_T0_discovery.json"),
    ("S4_T1", "Sprint 4 - T1 Specs", "out/scorecards/S4_T1_specs.json"),
    ("S4_T2", "Sprint 4 - T2 Sources", "out/scorecards/S4_T2_sources.json"),
    ("S4_T3", "Sprint 4 - T3 Fixtures", "out/scorecards/S4_T3_fixtures.json"),
    ("S4_T4", "Sprint 4 - T4 Goldens", "out/scorecards/S4_T4_goldens.json"),
    ("S4_T5", "Sprint 4 - T5 Vault", "out/scorecards/S4_T5_repetition.json"),
    ("S4_T6", "Sprint 4 - T6 Observability", "out/scorecards/S4_T6_observability.json"),
    ("S4_T7", "Sprint 4 - T7 ORR Pipeline", "out/scorecards/S4_T7_orr_pipeline.json"),
]
summary = {"sprint": "S4", "gates": []}
missing = []
decision = "GO"
reason = "Todos os gates S4_T0…S4_T7 em PASS"
for gate_id, gate_name, rel_path in gates:
    path = os.path.join(root, rel_path)
    if not os.path.exists(path):
        missing.append(rel_path)
        status = "MISSING"
    else:
        with open(path, encoding='utf-8') as handle:
            data = json.load(handle)
        status = data.get('status', 'UNKNOWN')
        if status != 'PASS' and decision == 'GO':
            decision = 'NO_GO'
            reason = f"{gate_id} status {status}"
    summary['gates'].append({
        'gate_id': gate_id,
        'name': gate_name,
        'status': status,
        'scorecard': rel_path
    })
if missing and decision == 'GO':
    decision = 'NO_GO'
    reason = f"Scorecards ausentes: {', '.join(missing)}"
summary['decision'] = decision
summary['reason'] = reason
with open(summary_path, 'w', encoding='utf-8') as handle:
    json.dump(summary, handle, indent=2, ensure_ascii=False)

def sha256(path):
    with open(path, 'rb') as handle:
        return hashlib.sha256(handle.read()).hexdigest()

artifacts = []
for rel in [os.path.relpath(wrap_path, root), os.path.relpath(summary_path, root)] + [rel for _, _, rel in gates]:
    path = os.path.join(root, rel)
    if not os.path.exists(path):
        continue
    artifacts.append({'path': rel, 'sha256': sha256(path)})
with open(manifest_path, 'w', encoding='utf-8') as handle:
    json.dump({'artifacts': artifacts}, handle, indent=2, ensure_ascii=False)
status_flag = 'PASS' if decision == 'GO' else 'FAIL'
scorecard = {
    'sprint_id': 'S4',
    'gate_id': 'S4_T8',
    'gate_name': 'Sprint 4 GO/NO_GO',
    'status': status_flag,
    'decision': decision,
    'summary': reason,
    'invariants_guarded': [
        'Não existe GO com gate FAIL',
        'Decisão T8 registrada em JSON + wrap',
        'Integridade dos scorecards via MANIFEST'
    ],
    'checks': [
        {'name': 'all_s4_gates_scorecards_present', 'status': 'PASS' if not missing else 'FAIL', 'details': 'Scorecards verificados'},
        {'name': 'all_s4_gates_passed', 'status': 'PASS' if decision == 'GO' else 'FAIL', 'details': reason},
        {'name': 'wrap_summary_present', 'status': 'PASS', 'details': 'docs/sprint_4_orr_summary.md'},
        {'name': 'decision_consistent_with_gates', 'status': 'PASS', 'details': decision}
    ],
    'metrics': {
        'gates_total': len(gates),
        'gates_passed': sum(1 for g in summary['gates'] if g['status'] == 'PASS'),
        'gates_failed': sum(1 for g in summary['gates'] if g['status'] != 'PASS')
    },
    'artifacts': [
        {'path': 'docs/sprint_4_orr_summary.md'},
        {'path': 'out/evidence/S4_T8_go_no_go/summary.json'},
        {'path': 'out/evidence/S4_T8_go_no_go/MANIFEST.json'}
    ],
    'errors': []
}
with open(scorecard_path, 'w', encoding='utf-8') as handle:
    json.dump(scorecard, handle, indent=2, ensure_ascii=False)
if decision != 'GO':
    sys.exit(1)
PY
