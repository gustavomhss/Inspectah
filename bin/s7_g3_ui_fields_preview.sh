#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
PYTHON_BIN="$REPO_ROOT/.venv/bin/python3"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="$(command -v python3)"
fi

$PYTHON_BIN - <<'PY'
from __future__ import annotations

import json
from pathlib import Path

from inspectah.sprint6 import config as sprint6_config
from inspectah.sprint7.gate_utils import get_client, prepare_gate_paths, write_json
from inspectah.ui import runtime_bridge

slug = "S7_G3_ui_fields_preview"
scorecard_path, evidence_dir = prepare_gate_paths(slug)

client = get_client()
resp = client.get("/model/fields")
status = "PASS" if resp.status_code == 200 else "FAIL"

cfg = sprint6_config.load_domain_config()
ui_fields = runtime_bridge.list_fields()
schema_matches = 0
for field in ui_fields:
    ref = next((f for f in cfg.fields if f.name == field.name), None)
    if not ref:
        continue
    if (
        ref.type == field.type
        and ref.required == field.required
        and (ref.description or "").strip() == (field.description or "").strip()
    ):
        schema_matches += 1

total_fields = len(cfg.fields) or 1
schema_ratio = round(schema_matches / total_fields, 3)

samples = runtime_bridge.get_samples_by_source()
filled = 0
total_slots = 0
for records in samples.values():
    for record in records:
        data = record.model_dump()
        for field in cfg.fields:
            total_slots += 1
            value = data.get(field.name)
            if value not in (None, "", []):
                filled += 1
coverage = round(filled / total_slots, 3) if total_slots else 0.0

if schema_ratio < 1.0:
    status = "FAIL"
if coverage <= 0:
    status = "FAIL"

details = {
    "status_code": resp.status_code,
    "schema_matches": schema_matches,
    "fields_total": total_fields,
    "sample_sources": {k: len(v) for k, v in samples.items()},
}
metrics = {
    "m4_field_schema_match_ratio": schema_ratio,
    "m4_preview_sample_coverage": coverage,
}

write_json(scorecard_path, {
    "gate": "S7_G3",
    "name": "ui_fields_preview",
    "status": status,
    "metrics": metrics,
    "details": details,
})
write_json(evidence_dir / "summary.json", details)

if status != "PASS":
    raise SystemExit("S7-G3 failed")
PY
