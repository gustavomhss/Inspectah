#!/usr/bin/env bash
set -euo pipefail
OUT="${ORR_OUTDIR:-out}"
if [[ "$OUT" != /* ]]; then
  OUT="$(pwd)/$OUT"
fi
EVID_DIR="$OUT/evidence/T0_spec_lock"
SCORECARD="$OUT/scorecards/T0_spec_lock.json"
REPORT="$EVID_DIR/docs_hashes.json"
SUMMARY="$EVID_DIR/docs_hashes.md"
DOCS=(
  "docs/inspectah_cap_1_produto.md"
  "docs/inspectah_cap_2_gates_orr.md"
  "docs/inspectah_cap_3_filemap_evidencias.md"
  "docs/inspectah_cap_4_playbook_codex.md"
  "docs/blueprint/inspectah_oracle_ops_platform_blueprint_v_1_2.md"
  "docs/Leasson_Learned_so_far_v1.md"
  "docs/sprint_3_plan_codex.md"
)
mkdir -p "$EVID_DIR" "$OUT/scorecards"
GIT_HEAD="$(git rev-parse HEAD 2>/dev/null || echo 'unknown')"
python3 - "$SCORECARD" "$REPORT" "$SUMMARY" "$GIT_HEAD" "${DOCS[@]}" <<'PY'
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
scorecard_path = Path(sys.argv[1])
report_path = Path(sys.argv[2])
summary_path = Path(sys.argv[3])
git_head = sys.argv[4]
docs = sys.argv[5:]
info = {}
present = 0
missing = []
for doc in docs:
    path = Path(doc)
    entry = {"path": doc}
    if path.is_file() and path.stat().st_size > 0:
        data = path.read_bytes()
        entry.update({
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": path.stat().st_size,
            "status": "present"
        })
        present += 1
    else:
        entry.update({"sha256": None, "bytes": 0, "status": "missing"})
        missing.append(doc)
    info[doc] = entry
report = {"git_head": git_head, "docs": info}
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
lines = [
    "# T0 Spec Lock — Evidência",
    "",
    "| Doc | Status | SHA256 | Bytes |",
    "| --- | --- | --- | --- |",
]
for doc, entry in info.items():
    lines.append(f"| {doc} | {entry['status']} | {entry['sha256'] or '-'} | {entry['bytes']} |")
summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
status = "PASS" if not missing else "FAIL"
scorecard = {
    "gate": "T0",
    "name": "spec_lock",
    "version": "v1",
    "status": status,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "metrics": {"docs_present": present, "docs_expected": len(docs)},
    "details": {
        "git_head": git_head,
        "docs": info,
    },
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    sys.stderr.write(f"Missing docs: {missing}\n")
    sys.exit(1)
PY
python3 - <<'PY' "$EVID_DIR"
import hashlib
import json
import sys
from pathlib import Path
root = Path(sys.argv[1])
files = []
for path in sorted(root.rglob('*')):
    if path.is_file():
        files.append({
            "path": path.relative_to(root).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "bytes": path.stat().st_size,
        })
(root / 'MANIFEST.json').write_text(json.dumps({"files": files}, indent=2), encoding='utf-8')
PY
echo "[T0] Spec lock scorecard written to $SCORECARD"
