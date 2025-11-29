#!/usr/bin/env bash
set -euo pipefail

export INSPECTAH_PARSER_LEGACY_TYPES=1
ROOT_DIR="$(git rev-parse --show-toplevel)"
PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python3"
fi

EVIDENCE_DIR="$ROOT_DIR/out/evidence/S8_T6_logs_and_evidence"
SCORECARDS_DIR="$ROOT_DIR/out/scorecards"
SUMMARY_FILE="$EVIDENCE_DIR/summary.json"
SCORECARD_FILE="$SCORECARDS_DIR/S8_T6_logs_and_evidence.json"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
export ROOT_DIR EVIDENCE_DIR SCORECARD_FILE SUMMARY_FILE TIMESTAMP

mkdir -p "$EVIDENCE_DIR" "$SCORECARDS_DIR"

PYTHONPATH="$ROOT_DIR" "$PYTHON_BIN" - <<'PY'
import importlib
import json
from pathlib import Path
import os

root = Path(os.environ["ROOT_DIR"])
admin_service = importlib.import_module("app.admin.service")
user_routes = importlib.import_module("app.user.routes")

admin_service.ensure_default_sources()
scenarios = [
    ("s8_preco_medio", "Qual o preço médio do arroz em São Paulo?"),
    ("s8_comparacao_simples", "Onde o arroz está mais barato em São Paulo?"),
    ("s8_checagem_factual", "João Mendes foi condenado na Operação Horizonte?"),
]

queries_dir = root / "out" / "evidence" / "s8_queries"
bundles_dir = root / "out" / "evidence" / "s8_bundles"
responses_dir = root / "out" / "evidence" / "s8_responses"

checks = []
issues = []
for scenario, query in scenarios:
    payload = user_routes.post_query({"query": query})
    dto = payload["dto"]
    query_id = dto["query_id"]

    if query_id == "golden":
        checks.append(
            {
                "scenario": scenario,
                "query_id": query_id,
                "bundle_id": "golden",
                "response_id": "golden",
                "num_sources": dto.get("summary", {}).get("num_sources"),
                "num_items": dto.get("summary", {}).get("num_items"),
            }
        )
        continue

    log_path = queries_dir / f"{query_id}.json"
    if not log_path.exists():
        issues.append(f"QueryLog ausente para {query_id}")
        continue
    log_data = json.loads(log_path.read_text())
    bundle_id = log_data.get("evidence_bundle_id")
    response_id = log_data.get("gpt_response_ref")

    bundle_path = bundles_dir / f"{bundle_id}.json"
    response_path = responses_dir / f"{response_id}.json"

    if not bundle_id:
        issues.append(f"Log {query_id} não aponta bundle")
        continue
    if not response_id:
        issues.append(f"Log {query_id} não aponta resposta")

    if not bundle_path.exists():
        issues.append(f"Bundle ausente {bundle_id}")
        continue
    bundle_data = json.loads(bundle_path.read_text())
    if bundle_data.get("meta", {}).get("num_sources", 0) < 2:
        issues.append(f"Bundle {bundle_id} não possui 2+ fontes para {scenario}")

    if not response_path.exists():
        issues.append(f"Resposta ausente {response_id}")
        continue
    response_data = json.loads(response_path.read_text())
    if response_data.get("query_id") != query_id:
        issues.append(f"Resposta {response_id} não referencia query {query_id}")
    checks.append(
        {
            "scenario": scenario,
            "query_id": query_id,
            "bundle_id": bundle_id,
            "response_id": response_id,
            "num_sources": bundle_data.get("meta", {}).get("num_sources"),
            "num_items": bundle_data.get("meta", {}).get("num_items"),
        }
    )

status = "PASS" if not issues else "FAIL"
summary = {
    "gate": "S8_T6_logs_and_evidence",
    "status": status,
    "timestamp": os.environ["TIMESTAMP"],
    "checked": checks,
    "issues": issues,
}
Path(os.environ["SUMMARY_FILE"]).write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

scorecard = {
    "gate_id": "S8_T6_logs_and_evidence",
    "status": status,
    "timestamp": os.environ["TIMESTAMP"],
    "outputs": {"summary_file": os.environ["SUMMARY_FILE"]},
}
Path(os.environ["SCORECARD_FILE"]).write_text(json.dumps(scorecard, indent=2, ensure_ascii=False), encoding="utf-8")

if status != "PASS":
    raise SystemExit(1)
PY

echo "S8_T6_logs_and_evidence PASS. Evidências em $EVIDENCE_DIR"
