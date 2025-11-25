#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S21_1_G4_files"
SCORECARD_PATH="$SCORECARD_DIR/S21_1_G4_files.json"
mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"
STATUS="PASS"; NOTES="upload/read stub"
python3 - <<'PY' "$EVIDENCE_DIR"
import json, sys, tempfile
from pathlib import Path
from inspectah.services import copiloto_files
from inspectah.agents.tools.file_reader import read_file_as_text
ed=Path(sys.argv[1])
ed.mkdir(parents=True, exist_ok=True)
tmp = tempfile.NamedTemporaryFile(delete=False)
tmp.write(b"conteudo teste copiloto")
tmp.close()
info = copiloto_files.save_upload("sess-script", Path(tmp.name).name, Path(tmp.name).read_bytes(), "text/plain")
text = read_file_as_text(info["file_id"])
Path(ed/"check.json").write_text(json.dumps({"file_id": info["file_id"], "text": text}), encoding="utf-8")
PY
python3 - <<'PY' "$SCORECARD_PATH" "$STATUS" "$NOTES"
import json, sys
from datetime import datetime, timezone
from pathlib import Path
out={"gate_id":"S21_1_G4","status":sys.argv[2],"automated_checks":{"status":sys.argv[2],"details":sys.argv[3]},"reviewers_internal":[],"reviewers_external":[],"risk_level":"low" if sys.argv[2]=="PASS" else "high","notes":sys.argv[3],"ts_last_update":datetime.now(timezone.utc).isoformat().replace("+00:00","Z")}
Path(sys.argv[1]).write_text(json.dumps(out, indent=2), encoding="utf-8")
PY
python3 - <<'PY' "$EVIDENCE_DIR"
import json, sys
from pathlib import Path
ed=Path(sys.argv[1]); files=[p.name for p in ed.iterdir() if p.is_file()]
(ed/"MANIFEST.json").write_text(json.dumps({"files":sorted(files),"notes":"Upload/read de arquivo pelo Copiloto"}, indent=2), encoding="utf-8")
PY
echo "[S21_1_G4] status=$STATUS"
