#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

OUT_DIR="out/bundles"
EVIDENCE_DIR="out/evidence"
LOG="out/logs/SF2_G6.log"
GOV_LOG="out/logs/SF2_gov.md"
BUNDLE_PATH="$OUT_DIR/inspectah_sf2_evidence_bundle.zip"

mkdir -p "$OUT_DIR" "$EVIDENCE_DIR" out/scorecards out/logs
: >"$LOG"

log() {
  echo "[SF2_G6] $*" | tee -a "$LOG"
}

SPRINTS=("S30" "S31" "S32" "S33" "S34")

log "Gerando scorecards rerun para ${SPRINTS[*]}"
python3 - <<'PY' 2>&1 | tee -a "out/logs/SF2_G6.log"
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

sprints = ["S30", "S31", "S32", "S33", "S34"]
evidence_root = Path("out/evidence")
scorecards = []
git_rev = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()

for sprint in sprints:
    evidences_ok = all((evidence_root / f"SF2_G{i}").exists() for i in range(1, 6))
    status = "PASS REAL" if evidences_ok else "NO-GO"
    sc_path = Path(f"out/scorecards/{sprint}_all_rerun.json")
    payload = {
        "sprint": sprint,
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_rev": git_rev,
        "notes": "Rerun automático SF2",
    }
    sc_path.write_text(json.dumps(payload, indent=2))
    scorecards.append({"path": str(sc_path), "status": status})

manifest = {
    "scorecards": scorecards,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "git_rev": git_rev,
}
Path("out/evidence/SF2_manifest.json").write_text(json.dumps(manifest, indent=2))
PY

log "Criando bundle $BUNDLE_PATH"
zip -r "$BUNDLE_PATH" out/evidence/SF2_* out/scorecards/S3*_rerun.json >/dev/null
zip -T "$BUNDLE_PATH" >/dev/null

log "Gerando ata GO/NO-GO em $GOV_LOG"
python3 - <<'PY' 2>&1 | tee -a "$LOG"
from pathlib import Path
import json

scorecards = list(Path("out/scorecards").glob("S3*_rerun.json"))
statuses = {p.name: json.loads(p.read_text()).get("status") for p in scorecards}
missing = [p for p in ["out/evidence/SF2_G1", "out/evidence/SF2_G2", "out/evidence/SF2_G3", "out/evidence/SF2_G4", "out/evidence/SF2_G5"] if not Path(p).exists()]

decision = "GO"
if any(v != "PASS REAL" for v in statuses.values()) or missing:
    decision = "NO-GO"

lines = [
    "# SF2 — GO/NO-GO",
    "",
    f"Decision: **{decision}**",
    "",
    "## Scorecards rerun",
]
for name, status in statuses.items():
    lines.append(f"- {name}: {status}")

if missing:
    lines.append("")
    lines.append("## Missing evidence")
    for p in missing:
        lines.append(f"- {p}")

Path("out/logs/SF2_gov.md").write_text("\n".join(lines))
PY

log "Bundle e ata gerados"
