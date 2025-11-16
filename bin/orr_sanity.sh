#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REQUIRED_DIRS=(
  bin docs contracts services db tests scripts configs ".github/workflows" out
)
REQUIRED_FILES=(
  README.md Makefile docs/EVIDENCE_SCHEMA.json docs/SPEC.md docs/SLOs.md \
  docs/PLAYBOOKS.md docs/LEGAL_TOS_ALLOWLIST.md bin/orr_all.sh
)
REQUIRED_RUNNERS=(bin/orr_all.sh bin/orr_sanity.sh bin/orr_t2.sh bin/orr_t3.sh bin/orr_t4.sh bin/orr_t5.sh bin/orr_t6.sh bin/orr_t7.sh bin/orr_t8.sh)
FAILURES=()
for dir in "${REQUIRED_DIRS[@]}"; do
  if [[ ! -d "$ROOT/$dir" ]]; then
    FAILURES+=("missing_dir:$dir")
  fi
done
for file in "${REQUIRED_FILES[@]}"; do
  if [[ ! -f "$ROOT/$file" ]]; then
    FAILURES+=("missing_file:$file")
  fi
done
for runner in "${REQUIRED_RUNNERS[@]}"; do
  if [[ ! -x "$ROOT/$runner" ]]; then
    FAILURES+=("not_executable:$runner")
  fi
done
OUT_DIR="$ROOT/out"
SCORECARD="$OUT_DIR/scorecards/T0_sanity.json"
EVID_DIR="$OUT_DIR/evidence/T0_sanity"
mkdir -p "$EVID_DIR" "$OUT_DIR/scorecards"
CHECKS_FILE="$EVID_DIR/checks.json"
if [[ ${#FAILURES[@]} -gt 0 ]]; then
  printf '{"status":"failed","issues":["%s"]}' "$(IFS=","; echo "${FAILURES[*]}")" > "$CHECKS_FILE"
  cat <<EOFMSG
Sanity checks failed:
$(printf ' - %s\n' "${FAILURES[@]}")
EOFMSG
  printf '{"gate":"T0","version":"1.0","passed":false,"failures":["scaffold-incomplete"],"notes":"see evidence"}' > "$SCORECARD"
  exit 1
fi
cat <<'JSON' > "$CHECKS_FILE"
{
  "status": "passed",
  "checks": {
    "directories": "ok",
    "files": "ok",
    "runners": "ok"
  }
}
JSON
MANIFEST="$EVID_DIR/MANIFEST.json"
python3 - "$CHECKS_FILE" "$MANIFEST" <<'PY'
import hashlib, json, os, sys
checks_path = sys.argv[1]
manifest_path = sys.argv[2]
files = []
for path in [checks_path]:
    with open(path, 'rb') as fh:
        data = fh.read()
    sha = hashlib.sha256(data).hexdigest()
    files.append({
        "path": os.path.relpath(path, os.path.dirname(os.path.dirname(checks_path))),
        "sha256": sha,
        "bytes": len(data)
    })
with open(manifest_path, 'w') as fh:
    json.dump({"files": files}, fh, indent=2)
PY
python3 - "$SCORECARD" <<'PY'
import json, sys, datetime
scorecard = {
  "gate": "T0",
  "version": "1.0",
  "started_at": datetime.datetime.utcnow().isoformat() + 'Z',
  "finished_at": datetime.datetime.utcnow().isoformat() + 'Z',
  "passed": True,
  "failures": [],
  "metrics": {},
  "artifacts": [
    {"path": "out/evidence/T0_sanity/checks.json"},
    {"path": "out/evidence/T0_sanity/MANIFEST.json"}
  ],
  "notes": "sanity ok"
}
with open(sys.argv[1], 'w') as fh:
  json.dump(scorecard, fh, indent=2)
PY
printf 'Sanity checks passed. Scorecard written to %s\n' "$SCORECARD"
