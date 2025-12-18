#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/SF4_G3"
LOG_DIR="$ROOT_DIR/out/logs"
LOG_PATH="$LOG_DIR/SF4_G3.log"
SCHEMA_APPLY_LOG="$EVIDENCE_DIR/schema_apply.log"
FIXTURE_MANIFEST="$EVIDENCE_DIR/fixtures_manifest.md"
SCRIPT_LOG="$EVIDENCE_DIR/sf4_g3_schema.log"
DB_PATH="${DB_PATH:-$ROOT_DIR/out/databases/sf4.sqlite}"

mkdir -p "$EVIDENCE_DIR" "$LOG_DIR" "$(dirname "$DB_PATH")"
: >"$SCRIPT_LOG"

log() { echo "$@" | tee -a "$LOG_PATH" "$SCRIPT_LOG"; }
fail() { echo "[SF4_G3][FAIL] $*" | tee -a "$LOG_PATH" "$SCRIPT_LOG"; exit 1; }

log "[SF4_G3] Aplicando migrations SQL em $DB_PATH"
mapfile -t migrations < <(find "$ROOT_DIR/db/migrations" -maxdepth 1 -name "*.sql" | sort)
if [[ ${#migrations[@]} -eq 0 ]]; then
  fail "Nenhuma migration encontrada em db/migrations"
fi

: >"$SCHEMA_APPLY_LOG"
for sql in "${migrations[@]}"; do
  log "- Applying $sql"
  python3 -m scripts.db.migrate "$sql" "$DB_PATH" 2>&1 | tee -a "$SCHEMA_APPLY_LOG"
done

log "[SF4_G3] Manifesto de fixtures (fixtures/ e tests/fixtures/)"
python3 - <<'PY' "$ROOT_DIR" "$FIXTURE_MANIFEST"
import hashlib
import os
from pathlib import Path
import sys

root = Path(sys.argv[1])
manifest_path = Path(sys.argv[2])
paths = [root / "fixtures", root / "tests" / "fixtures"]

def hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

entries = []
for base in paths:
    if not base.exists():
        continue
    for file in sorted(base.rglob("*")):
        if file.is_file():
            rel = file.relative_to(root)
            entries.append((str(rel), hash_file(file)))

commit = os.popen("git rev-parse HEAD").read().strip()
lines = [
    "# SF4 fixtures manifest",
    f"repo_commit: {commit}",
    "",
]
for rel, digest in entries:
    lines.append(f"- {rel}: {digest}")

if not entries:
    lines.append("- NO_FIXTURES_FOUND")

manifest_path.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote manifest with {len(entries)} entries")
PY

log "[SF4_G3] Concluído; evidências em $EVIDENCE_DIR"
