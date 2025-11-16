#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
PYTHON_BIN="$REPO_ROOT/.venv/bin/python3"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="$(command -v python3)"
fi

REPO_ROOT="$REPO_ROOT" "$PYTHON_BIN" - <<'PY'
from __future__ import annotations

import json
import os
from pathlib import Path

slug = "S7_G7_metrics_and_demo"
repo_root = Path(os.environ["REPO_ROOT"])
scorecard_path = repo_root / "out" / "scorecards" / f"{slug}.json"
evidence_dir = repo_root / "out" / "evidence" / slug
scorecard_path.parent.mkdir(parents=True, exist_ok=True)
evidence_dir.mkdir(parents=True, exist_ok=True)

def load_gate(slug: str) -> dict:
    path = repo_root / "out" / "scorecards" / f"{slug}.json"
    return json.loads(path.read_text(encoding="utf-8"))

g1 = load_gate("S7_G1_ui_boot_health")
g2 = load_gate("S7_G2_ui_sources_admin")
g3 = load_gate("S7_G3_ui_fields_preview")
g4 = load_gate("S7_G4_ui_query_consolidation")
g5 = load_gate("S7_G5_ui_evidence_trace")
g6 = load_gate("S7_G6_ui_only_flows")

metrics = {
    "m1_end_to_end_seconds": g6["metrics"]["m1_end_to_end_boot_and_use_seconds"],
    "m2_user_flow_seconds": g6["metrics"]["m2_user_flow_seconds"],
    "m3_admin_crud_success_rate": g2["metrics"]["m3_admin_crud_success_rate"],
    "m4_field_schema_match_ratio": g3["metrics"]["m4_field_schema_match_ratio"],
    "m4_query_consistency_ratio": g4["metrics"]["m4_query_consistency_ratio"],
    "m4_preview_sample_coverage": g3["metrics"]["m4_preview_sample_coverage"],
    "m5_explanation_present": g4["metrics"]["m5_explanation_present"],
    "m6_max_clicks_to_evidence": g5["metrics"]["m6_max_clicks_to_evidence"],
    "m6_evidence_found_ratio": g5["metrics"]["m6_evidence_found_ratio"],
    "boot_seconds": g1["metrics"]["m1_boot_seconds"],
}

flags = {
    "m1_pass": metrics["m1_end_to_end_seconds"] <= 300,
    "m2_pass": metrics["m2_user_flow_seconds"] <= 180,
    "m3_pass": metrics["m3_admin_crud_success_rate"] >= 1.0,
    "m4_pass": metrics["m4_field_schema_match_ratio"] >= 1.0 and metrics["m4_query_consistency_ratio"] >= 1.0,
    "m5_pass": bool(metrics["m5_explanation_present"]),
    "m6_pass": metrics["m6_max_clicks_to_evidence"] <= 2 and metrics["m6_evidence_found_ratio"] >= 1.0,
}

status = "PASS" if all(flags.values()) else "FAIL"
details = {"notes": "Aggregated metrics from S7-G1 a S7-G6"}

scorecard = {
    "gate": "S7_G7",
    "name": "metrics_and_demo",
    "status": status,
    "metrics": metrics,
    "flags": flags,
    "details": details,
}
scorecard_path.write_text(json.dumps(scorecard, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(evidence_dir / "summary.json").write_text(json.dumps(scorecard, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

if status != "PASS":
    raise SystemExit("S7-G7 failed")
PY
