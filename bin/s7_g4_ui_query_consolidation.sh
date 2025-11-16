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
import math
import re

from inspectah.sprint7.gate_utils import get_client, prepare_gate_paths, write_json
from inspectah.ui import runtime_bridge
from inspectah.ui.views import query as query_view

slug = "S7_G4_ui_query_consolidation"
scorecard_path, evidence_dir = prepare_gate_paths(slug)

client = get_client()
test_queries = [
    {"categoria": "graos"},
    {"search": "Frango"},
]

consistency = 0
explanations_present = True
cases = []
for payload in test_queries:
    resp = client.post("/query", data=payload)
    text = resp.text
    value_match = re.search(r"Valor consolidado:\s*<strong>R\$ ([0-9.,]+)</strong>", text)
    ui_value = float(value_match.group(1).replace(",", ".")) if value_match else None
    filters = query_view._parse_filters(payload)  # type: ignore[attr-defined]
    records = runtime_bridge.run_query(filters)
    expected = runtime_bridge.consolidate(records)
    matches = ui_value is not None and expected.value is not None and math.isclose(ui_value, expected.value, rel_tol=1e-3)
    if matches:
        consistency += 1
    explanation_ok = "Mediana" in text or "mediana" in text
    explanations_present = explanations_present and explanation_ok
    cases.append(
        {
            "payload": payload,
            "ui_value": ui_value,
            "expected_value": expected.value,
            "records_returned": [item.item_id for item in records],
            "html_contains_ids": all(item.item_id in text for item in records),
        }
    )

ratio = consistency / len(test_queries)
metrics = {
    "m4_query_consistency_ratio": round(ratio, 2),
    "m5_explanation_present": explanations_present,
}
status = "PASS" if ratio == 1.0 and explanations_present else "FAIL"

details = {"cases": cases}
write_json(scorecard_path, {
    "gate": "S7_G4",
    "name": "ui_query_consolidation",
    "status": status,
    "metrics": metrics,
    "details": details,
})
write_json(evidence_dir / "summary.json", details)

if status != "PASS":
    raise SystemExit("S7-G4 failed")
PY
