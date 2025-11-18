#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
export NET=0
export PYTHONPATH="${PYTHONPATH:-.}"
export INSPECTAH_DATA_DIR="${INSPECTAH_DATA_DIR:-$ROOT/out/evidence}"

OUT_DIR="$ROOT/out/evidence/S9_T6_logs_and_evidence"
SCORECARD="$ROOT/out/scorecards/S9_T6_logs_and_evidence.json"
SUMMARY="$OUT_DIR/summary.json"
MANIFEST="$OUT_DIR/MANIFEST.json"

mkdir -p "$OUT_DIR" "$(dirname "$SCORECARD")"

RESULT=$(SUMMARY_PATH="$SUMMARY" python3 - <<'PY'
import json
import os
import time
from pathlib import Path

from app.admin import service as admin_service
from app.core import storage
from app.user import routes as user_routes

SCENARIOS = {
    "C1": "Qual é o preço médio atual da cesta básica padrão em São Paulo?",
    "C2": "Onde o botijão de gás 13kg está mais barato nesta semana, capital ou Baixada Fluminense?",
    "C3": "O preço médio do diesel caiu 12% em Belo Horizonte nos últimos 30 dias?",
}
SUMMARY_PATH = Path(os.environ["SUMMARY_PATH"])

queries_summary = []
status = "PASS"
notes = []

for scenario_id, question in SCENARIOS.items():
    admin_service.prepare_scenario_sources(scenario_id)
    payload = {"question": question, "scenario_id": scenario_id}
    view = user_routes.post_query(payload)
    response_dto = view["response"]
    query_id = response_dto["query_id"]
    response_id = response_dto["response_id"]

    log = storage.load_query_log(query_id)
    bundle = storage.load_evidence_bundle(log.evidence_bundle_id) if log and log.evidence_bundle_id else None
    response_path = storage.responses_dir() / f"{response_id}.json"
    response_file = json.loads(response_path.read_text(encoding="utf-8")) if response_path.exists() else None

    checks = {
        "log_exists": log is not None,
        "bundle_exists": bundle is not None,
        "response_file_exists": response_file is not None,
        "num_sources_bundle": bool(bundle and bundle.meta.get("num_sources", 0) >= 2),
        "num_sources_response": bool(response_file and response_file.get("summary", {}).get("num_sources", 0) >= 2),
        "log_response_link": bool(log and log.user_response_id == response_id),
        "log_bundle_link": bool(log and bundle and log.evidence_bundle_id == bundle.id),
        "response_bundle_link": bool(bundle and response_file and response_file.get("evidence_bundle_id") == bundle.id),
        "status_match": bool(log and response_file and log.status == response_file.get("status")),
        "error_code_consistent": bool(log and ((log.status == "ok" and log.error_code is None) or (log.status != "ok"))),
        "scenario_tag_match": bool(bundle and bundle.meta.get("scenario_tag") == scenario_id)
    }

    if not all(checks.values()):
        status = "FAIL"
        notes.append(f"{scenario_id} falhou em {', '.join([k for k, v in checks.items() if not v])}")

    queries_summary.append(
        {
            "scenario": scenario_id,
            "query_id": query_id,
            "response_id": response_id,
            "bundle_id": bundle.id if bundle else None,
            "checks": checks,
        }
    )

summary = {
    "gate": "S9_T6_logs_and_evidence",
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "queries": queries_summary,
    "status": status,
    "notes": notes,
}
SUMMARY_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(status)
PY)

cat > "$MANIFEST" <<JSON
{
  "artifacts": [
    "$SUMMARY"
  ]
}
JSON

cat > "$SCORECARD" <<JSON
{
  "gate": "S9_T6",
  "name": "Logs & Evidence",
  "status": "$RESULT",
  "summary_path": "out/evidence/S9_T6_logs_and_evidence/summary.json"
}
JSON

if [[ "$RESULT" != "PASS" ]]; then
  exit 1
fi
