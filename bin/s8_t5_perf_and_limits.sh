#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python3"
fi

EVIDENCE_DIR="$ROOT_DIR/out/evidence/S8_T5_perf"
SCORECARDS_DIR="$ROOT_DIR/out/scorecards"
SUMMARY_FILE="$EVIDENCE_DIR/summary.json"
SCORECARD_FILE="$SCORECARDS_DIR/S8_T5_perf.json"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
STATUS_CARRIER="$EVIDENCE_DIR/status.tmp"
export ROOT_DIR EVIDENCE_DIR SCORECARDS_DIR SUMMARY_FILE SCORECARD_FILE TIMESTAMP STATUS_CARRIER

mkdir -p "$EVIDENCE_DIR" "$SCORECARDS_DIR"

PYTHONPATH="$ROOT_DIR" "$PYTHON_BIN" - <<'PY'
import importlib
import json
import statistics
import time
from pathlib import Path
import os

admin_service = importlib.import_module("app.admin.service")
user_routes = importlib.import_module("app.user.routes")

admin_service.ensure_default_sources()
SCENARIOS = [
    ("s8_preco_medio", "Qual o preço médio do arroz em São Paulo?"),
    ("s8_comparacao_simples", "Onde o arroz está mais barato em São Paulo?"),
    ("s8_checagem_factual", "João Mendes foi condenado na Operação Horizonte?"),
]
ITERATIONS = 5
LIMIT_P95_MS = 2000  # 2 seconds baseline

metrics = []
status = "PASS"
for name, query in SCENARIOS:
    durations = []
    bundle_sizes = []
    for _ in range(ITERATIONS):
        start = time.perf_counter()
        payload = user_routes.post_query({"query": query})
        elapsed_ms = (time.perf_counter() - start) * 1000
        durations.append(elapsed_ms)
        dto = payload["dto"]
        summary = dto.get("summary", {})
        bundle_sizes.append(summary.get("num_items", 0))
    durations.sort()
    p50 = statistics.median(durations)
    p95 = durations[int(len(durations) * 0.95) - 1] if durations else 0
    entry = {
        "scenario": name,
        "query": query,
        "iterations": ITERATIONS,
        "p50_ms": round(p50, 2),
        "p95_ms": round(p95, 2),
        "avg_items": statistics.mean(bundle_sizes) if bundle_sizes else 0,
        "max_items": max(bundle_sizes) if bundle_sizes else 0,
    }
    if p95 > LIMIT_P95_MS:
        status = "FAIL"
        entry["limit_breach"] = f"p95 {p95:.2f}ms > {LIMIT_P95_MS}ms"
    metrics.append(entry)

summary = {
    "gate": "S8_T5_perf",
    "status": status,
    "timestamp": os.environ["TIMESTAMP"],
    "metrics": metrics,
    "notes": [f"p95 limite {LIMIT_P95_MS}ms"],
}
Path(os.environ["SUMMARY_FILE"]).write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

scorecard = {
    "gate_id": "S8_T5_perf",
    "status": status,
    "timestamp": os.environ["TIMESTAMP"],
    "outputs": {"summary_file": os.environ["SUMMARY_FILE"]},
}
Path(os.environ["SCORECARD_FILE"]).write_text(json.dumps(scorecard, indent=2, ensure_ascii=False), encoding="utf-8")

Path(os.environ["STATUS_CARRIER"]).write_text(status, encoding="utf-8")

if status != "PASS":
    raise SystemExit(1)
PY

STATUS=$(cat "$STATUS_CARRIER")
rm -f "$STATUS_CARRIER"
if [[ "$STATUS" == "PASS" ]]; then
  echo "S8_T5_perf PASS. Evidências em $EVIDENCE_DIR"
fi
