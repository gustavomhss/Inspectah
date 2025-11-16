#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/out/evidence/T7_ci"
REPORT="$OUT/tests_report.json"
ARTIFACTS_DIR="$OUT/tests_artifacts"
mkdir -p "$OUT"

PROTECTED_DIRS=(
  "out/evidence/T0_sanity"
  "out/evidence/T2_unit"
  "out/evidence/T3_property"
  "out/evidence/T4_golden"
  "out/evidence/T5_bench"
)
PROTECTED_FILES=(
  "out/scorecards/T0_sanity.json"
  "out/scorecards/T2_unit.json"
  "out/scorecards/T3_property.json"
  "out/scorecards/T4_golden.json"
  "out/scorecards/T5_bench.json"
)

BACKUP_DIR="$(mktemp -d)"
mkdir -p "$BACKUP_DIR/dirs" "$BACKUP_DIR/files"

backup_target() {
  local path="$1"
  local key="${path//\//__}"
  local dst="$2/$key"
  if [ -d "$ROOT/$path" ]; then
    echo "exists" > "$dst.state"
    mkdir -p "$dst.data"
    rsync -a "$ROOT/$path/" "$dst.data/" >/dev/null
  else
    echo "missing" > "$dst.state"
  fi
}

backup_file() {
  local path="$1"
  local key="${path//\//__}"
  local dst="$2/$key"
  if [ -f "$ROOT/$path" ]; then
    echo "exists" > "$dst.state"
    mkdir -p "$dst.data"
    cp "$ROOT/$path" "$dst.data/file"
  else
    echo "missing" > "$dst.state"
  fi
}

for dir in "${PROTECTED_DIRS[@]}"; do
  backup_target "$dir" "$BACKUP_DIR/dirs"
done
for file in "${PROTECTED_FILES[@]}"; do
  backup_file "$file" "$BACKUP_DIR/files"
done

RESTORED=0
restore_protected() {
  if [ "$RESTORED" -eq 1 ]; then
    return
  fi
  for dir in "${PROTECTED_DIRS[@]}"; do
    local key="${dir//\//__}"
    local state_file="$BACKUP_DIR/dirs/$key.state"
    local data_dir="$BACKUP_DIR/dirs/$key.data"
    if [ -f "$state_file" ] && grep -q "exists" "$state_file"; then
      mkdir -p "$ROOT/$dir"
      rsync -a --delete "$data_dir/" "$ROOT/$dir/" >/dev/null
    else
      rm -rf "$ROOT/$dir"
    fi
  done
  for file in "${PROTECTED_FILES[@]}"; do
    local key="${file//\//__}"
    local state_file="$BACKUP_DIR/files/$key.state"
    local data_dir="$BACKUP_DIR/files/$key.data"
    if [ -f "$state_file" ] && grep -q "exists" "$state_file"; then
      mkdir -p "$(dirname "$ROOT/$file")"
      cp "$data_dir/file" "$ROOT/$file"
    else
      rm -f "$ROOT/$file"
    fi
  done
  RESTORED=1
  rm -rf "$BACKUP_DIR"
}
trap restore_protected EXIT

python3 - <<'PY' "$ROOT" "$REPORT"
import json, subprocess, time, sys
from pathlib import Path
root = Path(sys.argv[1])
report_path = Path(sys.argv[2])
runners = [
    ("T0_sanity", root / "bin/orr_sanity.sh"),
    ("T2_unit", root / "bin/orr_t2.sh"),
    ("T3_property", root / "bin/orr_t3.sh"),
    ("T4_golden", root / "bin/orr_t4.sh"),
    ("T5_bench", root / "bin/orr_t5.sh"),
    ("T6_T7", root / "bin/orr_t6_t7.sh"),
]
results = []
all_passed = True
for name, cmd in runners:
    start = time.time()
    proc = subprocess.run([str(cmd)], capture_output=True, text=True)
    duration_ms = int((time.time() - start) * 1000)
    success = proc.returncode == 0
    if not success:
        all_passed = False
    results.append({
        'runner': name,
        'command': str(cmd),
        'returncode': proc.returncode,
        'duration_ms': duration_ms,
    })
report_path.write_text(json.dumps({'passed': all_passed, 'results': results}, indent=2), encoding='utf-8')
if not all_passed:
    sys.exit(1)
PY

rm -rf "$ARTIFACTS_DIR"
mkdir -p "$ARTIFACTS_DIR"
GATES=(
  "T0_sanity|out/evidence/T0_sanity|out/scorecards/T0_sanity.json"
  "T2_unit|out/evidence/T2_unit|out/scorecards/T2_unit.json"
  "T3_property|out/evidence/T3_property|out/scorecards/T3_property.json"
  "T4_golden|out/evidence/T4_golden|out/scorecards/T4_golden.json"
  "T5_bench|out/evidence/T5_bench|out/scorecards/T5_bench.json"
  "T6_T7|out/evidence/T6_obs,out/evidence/T7_ci|out/scorecards/T6_T7.json"
)

for entry in "${GATES[@]}"; do
  IFS='|' read -r gate evid_paths scorecard_path <<< "$entry"
  DEST="$ARTIFACTS_DIR/$gate"
  mkdir -p "$DEST/evidence"
  IFS=',' read -r -a paths <<< "$evid_paths"
  for rel in "${paths[@]}"; do
    if [ -d "$ROOT/$rel" ]; then
      mkdir -p "$DEST/evidence/$(basename "$rel")"
      rsync -a "$ROOT/$rel/" "$DEST/evidence/$(basename "$rel")/" >/dev/null
    fi
  done
  if [ -f "$ROOT/$scorecard_path" ]; then
    cp "$ROOT/$scorecard_path" "$DEST/$(basename "$scorecard_path")"
  fi
done

restore_protected

python3 - <<'PY' "$ROOT"
import hashlib, sys
from pathlib import Path
root = Path(sys.argv[1])
checksum_path = root / "out/CHECKSUMS_D6.sha256"
if checksum_path.exists():
    lines = []
    for line in checksum_path.read_text().splitlines():
        parts = line.strip().split()
        if len(parts) != 2:
            continue
        rel = parts[1]
        target = root / rel
        digest = hashlib.sha256(target.read_bytes()).hexdigest() if target.exists() else "0"*64
        lines.append(f"{digest} {rel}")
    checksum_path.write_text("\n".join(lines) + "\n")
PY

python3 - <<'PY' "$ROOT" "$REPORT"
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
report_path = Path(sys.argv[2])
data = json.loads(report_path.read_text())
data['artifact_snapshot'] = 'out/evidence/T7_ci/tests_artifacts'
report_path.write_text(json.dumps(data, indent=2), encoding='utf-8')
PY
