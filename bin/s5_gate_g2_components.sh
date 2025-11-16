#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT_DIR/out/s5_gates/G2_components"
LOG_FILE="$OUT_DIR/tests.log"
SCORECARD="$OUT_DIR/scorecard.json"
mkdir -p "$OUT_DIR"

now_iso="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
status="PASS"
notes=()

require_file() {
  local label="$1"
  local path="$2"
  if [[ ! -f "$path" ]]; then
    notes+=("Falta ${label}: ${path}")
    status="FAIL"
  fi
}

# Verifica componentes centrais
require_file "Sources registry" "$ROOT_DIR/inspectah/config/sources_registry.yaml"
require_file "Watcher engine" "$ROOT_DIR/inspectah/watchers/engine.py"
require_file "Watcher RSS" "$ROOT_DIR/inspectah/watchers/rss_watcher.py"
require_file "Watcher API" "$ROOT_DIR/inspectah/watchers/api_watcher.py"
require_file "Watcher HTML" "$ROOT_DIR/inspectah/watchers/html_watcher.py"
require_file "Evidence builder" "$ROOT_DIR/inspectah/evidence/builder.py"
require_file "Evidence verifier" "$ROOT_DIR/inspectah/evidence/verifier.py"
require_file "Normalizer stub" "$ROOT_DIR/inspectah/normalizer/normalizer.py"
require_file "Client stub" "$ROOT_DIR/inspectah/normalizer/client_ai.py"
require_file "Indexer" "$ROOT_DIR/inspectah/indexer/indexer.py"

mapfile -t COMPONENT_TESTS < <(cd "$ROOT_DIR" && find tests/components -name 'test_*.py' -print | sort) || true
if [[ ${#COMPONENT_TESTS[@]} -eq 0 ]]; then
  notes+=("Nenhum teste em tests/components")
  status="FAIL"
fi

run_component_tests() {
  pushd "$ROOT_DIR" >/dev/null
  local pytest_available
  pytest_available=$(python3 - <<'PY'
try:
    import pytest  # noqa: F401
except Exception:
    print("no")
else:
    print("yes")
PY
)
  if [[ "$pytest_available" == "yes" ]]; then
    cmd=(python3 -m pytest tests/components)
  else
    cmd=(python3 "$ROOT_DIR/bin/s5_pytest_shim.py" "${COMPONENT_TESTS[@]}")
  fi
  if ! "${cmd[@]}" 2>&1 | tee "$LOG_FILE"; then
    notes+=("Testes de componentes falharam — ver $LOG_FILE")
    status="FAIL"
  fi
  popd >/dev/null
}

run_component_tests

extract_tests_run() {
  python3 - "$LOG_FILE" <<'PY'
import re
import sys
from pathlib import Path
text = Path(sys.argv[1]).read_text() if Path(sys.argv[1]).exists() else ""
match = re.search(r"collected (\d+) items", text)
if not match:
    match = re.search(r"Ran (\d+) tests?", text)
print(match.group(1) if match else "0")
PY
}

tests_run=$(extract_tests_run)
notes_text="PASS"
if [[ ${#notes[@]} -gt 0 ]]; then
  notes_text=$(printf '%s; ' "${notes[@]}")
  notes_text=${notes_text::-2}
fi

cat <<JSON > "$SCORECARD"
{
  "gate_id": "G2",
  "status": "${status}",
  "checked_at": "${now_iso}",
  "notes": "${notes_text}",
  "metrics": {"tests_run": ${tests_run}}
}
JSON

if [[ "$status" == "PASS" ]]; then
  echo "G2 Components -> PASS (${tests_run} testes)"
else
  echo "G2 Components -> FAIL"
  echo "Notas: ${notes_text}"
  exit 1
fi
