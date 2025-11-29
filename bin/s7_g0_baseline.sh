#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
PYTHON_BIN="$REPO_ROOT/.venv/bin/python3"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="$(command -v python3)"
fi

SCORECARD="$REPO_ROOT/out/scorecards/S7_G0_baseline.json"
EVIDENCE_DIR="$REPO_ROOT/out/evidence/S7_G0_baseline"
SUMMARY_JSON="$EVIDENCE_DIR/summary.json"
mkdir -p "$(dirname "$SCORECARD")" "$EVIDENCE_DIR"

DOC_PATHS=(
  "docs/sprint_7/sprint_7_capitulo_1.md"
  "docs/sprint_7/sprint_7_capitulo_2.md"
  "docs/sprint_7/sprint_7_capitulo_3.md"
  "docs/sprint_7/sprint_7_capitulo_4.md"
  "docs/sprint_7/sprint_7_resultados.md"
)
S6_SCORECARD="$REPO_ROOT/out/scorecards/S6_G8_sprint_go_no_go.json"

"$PYTHON_BIN" - "$SCORECARD" "$SUMMARY_JSON" "$S6_SCORECARD" "${DOC_PATHS[@]}" <<'PY'
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import List

scorecard_path = Path(sys.argv[1])
summary_path = Path(sys.argv[2])
s6_scorecard_path = Path(sys.argv[3])
doc_paths: List[Path] = [Path(p) for p in sys.argv[4:]]

def describe(path: Path) -> dict:
    info = {"path": str(path), "exists": path.exists(), "sha256": None}
    if path.exists():
        data = path.read_bytes()
        info["sha256"] = hashlib.sha256(data).hexdigest()
    return info

docs_info = [describe(path) for path in doc_paths]
missing_docs = [d["path"] for d in docs_info if not d["exists"]]

s6_status = None
if s6_scorecard_path.exists():
    try:
        with s6_scorecard_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
            s6_status = payload.get("status")
    except json.JSONDecodeError:
        s6_status = "INVALID_JSON"
else:
    s6_status = "MISSING"

status = "PASS"
notes = []
if missing_docs:
    status = "FAIL"
    notes.append(f"Documentos ausentes: {', '.join(missing_docs)}")
if s6_status != "GO":
    status = "FAIL"
    if s6_status is None:
        notes.append("Scorecard da S6_G8 não pôde ser lido.")
    else:
        notes.append(f"S6_G8 indica status '{s6_status}', esperado 'GO'.")

summary = {
    "checked_documents": docs_info,
    "s6_g8_status": s6_status,
    "notes": notes,
}
summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

scorecard = {
    "gate": "S7_G0",
    "name": "baseline",
    "status": status,
    "details": summary,
}
scorecard_path.write_text(json.dumps(scorecard, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

if status != "PASS":
    sys.exit(1)
PY
