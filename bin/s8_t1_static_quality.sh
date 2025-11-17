#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S8_T1_static"
SCORECARDS_DIR="$ROOT_DIR/out/scorecards"
SUMMARY_FILE="$EVIDENCE_DIR/summary.json"
MANIFEST_FILE="$EVIDENCE_DIR/MANIFEST.json"
SCORECARD_FILE="$SCORECARDS_DIR/S8_T1_static.json"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

mkdir -p "$EVIDENCE_DIR" "$SCORECARDS_DIR"

STATUS="PASS"
TOOLS_INFO=""
export STATUS TIMESTAMP ROOT_DIR

run_step() {
  local name="$1"
  shift
  local log_file="$EVIDENCE_DIR/${name// /_}.log"
  if "$@" >"$log_file" 2>&1; then
    TOOLS_INFO+="${name}::PASS::${log_file};;"
  else
    STATUS="FAIL"
    TOOLS_INFO+="${name}::FAIL::${log_file};;"
  fi
}

run_step "compile_app" python3 -m compileall "$ROOT_DIR/app"
run_step "compile_tests_s8" python3 -m compileall "$ROOT_DIR/tests/s8_t2_unit_contracts" "$ROOT_DIR/tests/s8_t3_property"

secret_log="$EVIDENCE_DIR/secret_scan.log"
if ROOT_DIR="$ROOT_DIR" python3 - "$ROOT_DIR" >"$secret_log" 2>&1 <<'PY'
import os
import re
from pathlib import Path

root = Path(os.environ["ROOT_DIR"])
targets = [root / "app"]
patterns = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "aws_access_key"),
    (re.compile(r"-----BEGIN (?:RSA|EC|DSA) PRIVATE KEY-----"), "private_key"),
    (re.compile(r"api[_-]?key\s*=\s*['\"][A-Za-z0-9]{20,}"), "api_key_literal"),
]
issues = []
for target in targets:
    for path in target.rglob("*"):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern, label in patterns:
            if pattern.search(text):
                issues.append({"file": str(path.relative_to(root)), "label": label})
if issues:
    print("Potential secrets found:", issues)
    raise SystemExit(1)
print("Secret scan completed with no findings.")
PY
then
  TOOLS_INFO+="secret_scan::PASS::${secret_log};;"
else
  STATUS="FAIL"
  TOOLS_INFO+="secret_scan::FAIL::${secret_log};;"
fi

export TOOLS_INFO SUMMARY_FILE MANIFEST_FILE SCORECARD_FILE
python3 - <<'PY'
import json
import os
from pathlib import Path

summary_path = Path(os.environ["SUMMARY_FILE"])
manifest_path = Path(os.environ["MANIFEST_FILE"])
scorecard_path = Path(os.environ["SCORECARD_FILE"])
status = os.environ["STATUS"]
timestamp = os.environ["TIMESTAMP"]
tools_info = os.environ.get("TOOLS_INFO", "")
tools = []
for chunk in tools_info.split(";;"):
    if not chunk.strip():
        continue
    name, tool_status, log = chunk.split("::", 2)
    log_path = Path(log)
    output = log_path.read_text() if log_path.exists() else ""
    tools.append({
        "name": name,
        "status": tool_status,
        "log": str(log_path),
        "output_tail": output[-4000:],
    })

summary = {
    "gate": "S8_T1_static",
    "status": status,
    "timestamp": timestamp,
    "tools": tools,
}
summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

manifest = {
    "gate": "S8_T1_static",
    "artifacts": [str(summary_path), str(manifest_path)],
}
manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

scorecard = {
    "gate_id": "S8_T1_static",
    "status": status,
    "timestamp": timestamp,
    "outputs": {"summary_file": str(summary_path)},
}
scorecard_path.write_text(json.dumps(scorecard, indent=2, ensure_ascii=False), encoding="utf-8")
PY

if [[ "$STATUS" != "PASS" ]]; then
  exit 1
fi

echo "S8_T1_static PASS. Evidências em $EVIDENCE_DIR"
