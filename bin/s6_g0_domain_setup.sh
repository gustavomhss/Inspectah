#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
PYTHON_BIN="$REPO_ROOT/.venv/bin/python3"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="$(command -v python3)"
fi

SCORECARD="$REPO_ROOT/out/scorecards/S6_G0_domain_setup.json"
EVIDENCE_DIR="$REPO_ROOT/out/evidence/S6_G0_domain_setup"
mkdir -p "$(dirname "$SCORECARD")" "$EVIDENCE_DIR"

DOC_PATHS=(
  "docs/sprint_6/sprint_6_capitulo_1.md"
  "docs/sprint_6/sprint_6_capitulo_2.md"
  "docs/sprint_6/sprint_6_capitulo_3.md"
  "docs/sprint_6/sprint_6_capitulo_4.md"
  "docs/sprint_6/dominio_piloto.md"
  "docs/sprint_6/sprint_6_resultados.md"
  "config/fields/dominio_piloto.yaml"
  "config/sources/fonte_a.yaml"
  "config/sources/fonte_b.yaml"
  "config/sources/fonte_c.yaml"
)

> "$EVIDENCE_DIR/summary.md"
missing=()
for path in "${DOC_PATHS[@]}"; do
  echo "- $path" >> "$EVIDENCE_DIR/summary.md"
  if [[ -f "$REPO_ROOT/$path" ]]; then
    sha=$(shasum -a 256 "$REPO_ROOT/$path" | awk '{print $1}')
    echo "  - presente (sha256=$sha)" >> "$EVIDENCE_DIR/summary.md"
  else
    echo "  - MISSING" >> "$EVIDENCE_DIR/summary.md"
    missing+=("$path")
  fi
  echo >> "$EVIDENCE_DIR/summary.md"
done

status="PASS"
if (( ${#missing[@]} )); then
  status="FAIL"
fi

ARGS=("$SCORECARD" "$status" "${DOC_PATHS[@]}")
if (( ${#missing[@]} )); then
  ARGS+=("--" "${missing[@]}")
fi

"$PYTHON_BIN" - "${ARGS[@]}" <<'PY'
import json, sys
scorecard_path = sys.argv[1]
status = sys.argv[2]
args = sys.argv[3:]
if "--" in args:
    idx = args.index("--")
    checked = args[:idx]
    missing = args[idx + 1 :]
else:
    checked = args
    missing = []
json.dump({
    "gate": "S6_G0",
    "name": "domain_setup",
    "status": status,
    "details": {
        "checked_paths": checked,
        "missing": missing,
    },
}, open(scorecard_path, "w", encoding="utf-8"), indent=2)
PY

if [[ "$status" != "PASS" ]]; then
  exit 1
fi
