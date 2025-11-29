#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"
export NET=0
export ROOT_DIR

EVIDENCE_DIR="$ROOT_DIR/out/evidence/S9_T1_static"
SCORECARDS_DIR="$ROOT_DIR/out/scorecards"
SUMMARY_FILE="$EVIDENCE_DIR/summary.json"
MANIFEST_FILE="$EVIDENCE_DIR/MANIFEST.json"
SCORECARD_FILE="$SCORECARDS_DIR/S9_T1_static_quality.json"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

mkdir -p "$EVIDENCE_DIR" "$SCORECARDS_DIR"

STATUS="PASS"
TOOLS=()

run_step() {
  local name="$1"
  shift
  local log_file="$EVIDENCE_DIR/${name// /_}.log"
  if "$@" >"$log_file" 2>&1; then
    TOOLS+=("$name::PASS::$log_file")
  else
    STATUS="FAIL"
    TOOLS+=("$name::FAIL::$log_file")
  fi
}

run_step "compile_app" python3 -m compileall app
run_step "compile_tests_s9" python3 -m compileall tests/s9_t2_unit_contracts tests/s9_t3_property

TODO_LOG="$EVIDENCE_DIR/todo_scan.log"
if rg --no-ignore -n "TODO|FIXME" app/core app/user app/gpt_client tests/s9_t2_unit_contracts tests/s9_t3_property >"$TODO_LOG" 2>&1; then
  STATUS="FAIL"
  TOOLS+=("todo_scan::FAIL::$TODO_LOG")
else
  TOOLS+=("todo_scan::PASS::$TODO_LOG")
fi

SECRET_LOG="$EVIDENCE_DIR/secret_scan.log"
if python3 - "$ROOT_DIR" >"$SECRET_LOG" 2>&1 <<'PY'
import os
import re
from pathlib import Path

root = Path(os.environ["ROOT_DIR"])
patterns = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "aws_key"),
    (re.compile(r"-----BEGIN (?:RSA|EC|DSA) PRIVATE KEY-----"), "private_key"),
    (re.compile(r"api[_-]?key\s*=\s*['\"][A-Za-z0-9]{20,}"), "api_literal"),
]
issues = []
for path in (root / "app").rglob("*.py"):
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    for pattern, label in patterns:
        if pattern.search(text):
            issues.append({"file": str(path.relative_to(root)), "label": label})
if issues:
    print("Potential secrets found", issues)
    raise SystemExit(1)
print("Secret scan completed with no findings.")
PY
then
  TOOLS+=("secret_scan::PASS::$SECRET_LOG")
else
  STATUS="FAIL"
  TOOLS+=("secret_scan::FAIL::$SECRET_LOG")
fi

TOOLS_ENV="$(IFS=';;'; printf "%s" "${TOOLS[*]}")"

SUMMARY_FILE="$SUMMARY_FILE" \
SCORECARD_FILE="$SCORECARD_FILE" \
MANIFEST_FILE="$MANIFEST_FILE" \
STATUS="$STATUS" \
TIMESTAMP="$TIMESTAMP" \
TOOLS="$TOOLS_ENV" \
python3 - <<'PY'
import json
import os
from pathlib import Path

summary_path = Path(os.environ["SUMMARY_FILE"])
scorecard_path = Path(os.environ["SCORECARD_FILE"])
manifest_path = Path(os.environ["MANIFEST_FILE"])
status = os.environ["STATUS"]
timestamp = os.environ["TIMESTAMP"]

tools = []
for entry in os.environ.get("TOOLS", "").split(";;"):
    if not entry:
        continue
    name, tool_status, log = entry.split("::", 2)
    log_path = Path(log)
    output_tail = ""
    if log_path.exists():
        output_tail = log_path.read_text(encoding="utf-8")[-4000:]
    tools.append({"name": name, "status": tool_status, "log": str(log_path), "output_tail": output_tail})

summary = {
    "gate": "S9_T1_static_quality",
    "status": status,
    "timestamp": timestamp,
    "tools": tools,
    "invariants": ["Inv4"],
}
summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

manifest = {
    "gate": "S9_T1_static_quality",
    "artifacts": [str(summary_path)],
}
manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

scorecard = {
    "gate": "S9_T1_static_quality",
    "status": status,
    "timestamp": timestamp,
    "details": {
        "tools_run": len(tools),
        "notes": "Compile + scans executados",
    },
}
scorecard_path.write_text(json.dumps(scorecard, indent=2, ensure_ascii=False), encoding="utf-8")
PY

if [[ "$STATUS" != "PASS" ]]; then
  exit 1
fi

echo "S9_T1_static_quality $STATUS. Evidencias em $EVIDENCE_DIR"
