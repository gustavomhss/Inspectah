#!/usr/bin/env bash
set -euo pipefail

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
base_evidence = root / "out" / "evidence"
LEGACY_PREFIXES = ("s8", "s9")

def _dir_candidates(kind: str):
    return [base_evidence / f"{prefix}_{kind}" for prefix in LEGACY_PREFIXES]

def _find_artifact(kind: str, name: str) -> Path | None:
    for directory in _dir_candidates(kind):
        path = directory / name
        if path.exists():
            return path
    return None

admin_service = importlib.import_module("app.admin.service")
user_routes = importlib.import_module("app.user.routes")

admin_service.ensure_default_sources()
scenarios = [
    ("s8_preco_medio", "Qual o preço médio do arroz em São Paulo?"),
    ("s8_comparacao_simples", "Onde o arroz está mais barato em São Paulo?"),
    ("s8_checagem_factual", "João Mendes foi condenado na Operação Horizonte?"),
]

checks = []
issues = []
for scenario, query in scenarios:
    payload = user_routes.post_query({"query": query})
    dto = payload["dto"]
    query_id = dto["query_id"]

    log_path = _find_artifact("queries", f"{query_id}.json")
    if not log_path:
        issues.append(f"QueryLog ausente para {query_id}")
        continue
    log_data = json.loads(log_path.read_text())
    bundle_id = log_data.get("evidence_bundle_id")
    response_id = log_data.get("gpt_response_ref")

    if not bundle_id:
        issues.append(f"Log {query_id} não aponta bundle")
        continue
    if not response_id:
        issues.append(f"Log {query_id} não aponta resposta")
        continue

    bundle_path = _find_artifact("bundles", f"{bundle_id}.json")
    response_path = _find_artifact("responses", f"{response_id}.json")

    if not bundle_path:
        issues.append(f"Bundle ausente {bundle_id}")
        continue
    bundle_data = json.loads(bundle_path.read_text())
    if bundle_data.get("meta", {}).get("num_sources", 0) < 2:
        issues.append(f"Bundle {bundle_id} não possui 2+ fontes para {scenario}")

    if not response_path:
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
