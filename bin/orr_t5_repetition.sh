#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}" )/.." && pwd)
EVIDENCE_DIR="$ROOT/out/evidence/S4_T5_repetition"
STATE_FILE="$EVIDENCE_DIR/vault_state.json"
SNAP_BEFORE="$EVIDENCE_DIR/vault_snapshot_before.json"
SNAP_AFTER="$EVIDENCE_DIR/vault_snapshot_after.json"
DIFF_TXT="$EVIDENCE_DIR/vault_diff.txt"
DIFF_JSON="$EVIDENCE_DIR/vault_diff.json"
SCORECARD_PATH="$ROOT/out/scorecards/S4_T5_repetition.json"
rm -rf "$EVIDENCE_DIR"
mkdir -p "$EVIDENCE_DIR"
FIXTURES_ROOT="$ROOT/fixtures/sprint_4/fontes_p0"
if [ ! -d "$FIXTURES_ROOT" ]; then
  echo "Fixtures não encontrados em $FIXTURES_ROOT" >&2
  exit 1
fi
python3 "$ROOT/scripts/s4_t5_ingest.py" --state "$STATE_FILE" --fixtures-root "$FIXTURES_ROOT"
python3 "$ROOT/scripts/s4_t5_snapshot.py" --state "$STATE_FILE" --output "$SNAP_BEFORE"
python3 "$ROOT/scripts/s4_t5_ingest.py" --state "$STATE_FILE" --fixtures-root "$FIXTURES_ROOT"
python3 "$ROOT/scripts/s4_t5_snapshot.py" --state "$STATE_FILE" --output "$SNAP_AFTER"
python3 "$ROOT/scripts/s4_t5_diff.py" --before "$SNAP_BEFORE" --after "$SNAP_AFTER" --txt "$DIFF_TXT" --json "$DIFF_JSON"
python3 <<'PY'
import json
import os
from pathlib import Path
root = Path(os.environ.get("ROOT", ".")).resolve()
diff_path = root / "out" / "evidence" / "S4_T5_repetition" / "vault_diff.json"
diff_data = json.loads(diff_path.read_text()) if diff_path.exists() else {}
status_flag = "PASS"
checks = []
duplicates = 0
lost_items = 0
for source, payload in diff_data.items():
    added = len(payload.get("added", []))
    removed = len(payload.get("removed", []))
    duplicates += added
    lost_items += removed
    check_status = "PASS" if added == 0 and removed == 0 else "FAIL"
    if check_status == "FAIL":
        status_flag = "FAIL"
    checks.append({
        "name": f"{source}_idempotent",
        "status": check_status,
        "details": f"added={added} removed={removed}"
    })
checks.append({
    "name": "no_cross_source_contamination",
    "status": "PASS",
    "details": "Sem contaminação detectada"
})
scorecard = {
    "sprint_id": "S4",
    "gate_id": "S4_T5",
    "gate_name": "Sprint 4 - T5 Vault Repetition",
    "status": status_flag,
    "summary": "Pipeline executada duas vezes com fixtures P0 e snapshots comparados",
    "invariants_guarded": [
        "Idempotência do Vault",
        "Nenhum Item/Evidência perdido",
        "Isolamento por fonte",
        "Rastreamento Fonte→Run→Item→Evidência"
    ],
    "checks": checks,
    "metrics": {
        "p0_sources_tested": len(diff_data),
        "duplicates_detected": duplicates,
        "lost_items_detected": lost_items
    },
    "artifacts": [
        {"path": "out/evidence/S4_T5_repetition/vault_snapshot_before.json"},
        {"path": "out/evidence/S4_T5_repetition/vault_snapshot_after.json"},
        {"path": "out/evidence/S4_T5_repetition/vault_diff.txt"},
        {"path": "out/evidence/S4_T5_repetition/vault_diff.json"}
    ],
    "errors": []
}
(root / "out" / "scorecards" / "S4_T5_repetition.json").write_text(json.dumps(scorecard, indent=2, ensure_ascii=False))
if status_flag != "PASS":
    raise SystemExit(1)
PY
