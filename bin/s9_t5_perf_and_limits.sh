#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
export NET=0
export PYTHONPATH="${PYTHONPATH:-.}"
export INSPECTAH_DATA_DIR="${INSPECTAH_DATA_DIR:-$ROOT/out/evidence}"

OUT_DIR="$ROOT/out/evidence/S9_T5_perf_and_limits"
SCORECARD="$ROOT/out/scorecards/S9_T5_perf_and_limits.json"
SUMMARY="$OUT_DIR/summary.json"
MANIFEST="$OUT_DIR/MANIFEST.json"
RUN_DATA_DIR="$OUT_DIR/run_data"

mkdir -p "$OUT_DIR" "$(dirname "$SCORECARD")"
export INSPECTAH_DATA_DIR="$RUN_DATA_DIR"

RESULT=$(SUMMARY_PATH="$SUMMARY" python3 - <<'PY'
import json
import os
import time
from pathlib import Path

from app.admin import service as admin_service
from app.observability import metrics_s9
from app.user import routes as user_routes

SUMMARY_PATH = Path(os.environ["SUMMARY_PATH"])
GOLDENS = {
    "C1": Path("tests/goldens/s9_preco_medio.json"),
    "C2": Path("tests/goldens/s9_comparacao_simples.json"),
    "C3": Path("tests/goldens/s9_checagem_factual.json"),
}
SCENARIOS = {
    "C1": "Qual é o preço médio atual da cesta básica padrão em São Paulo?",
    "C2": "Onde o botijão de gás 13kg está mais barato nesta semana, capital ou Baixada Fluminense?",
    "C3": "O preço médio do diesel caiu 12% em Belo Horizonte nos últimos 30 dias?",
}
TOTAL_QUERIES = 60
THROUGHPUT_QUERIES = 30
P95_TARGET = 1.5
MAX_ERROR_RATE = 0.02
TOLERANCE_REL = 0.05


def _percentile(values, ratio):
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = ratio * (len(ordered) - 1)
    lower = int(rank)
    upper = min(lower + 1, len(ordered) - 1)
    weight = rank - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def _within_tolerance(actual, expected):
    for key, expected_value in expected.items():
        if key not in actual:
            return False
        actual_value = actual[key]
        if isinstance(expected_value, (int, float)):
            denom = abs(expected_value) if expected_value else 1.0
            if abs(actual_value - expected_value) / denom > TOLERANCE_REL:
                return False
        elif isinstance(expected_value, dict):
            if not _within_tolerance(actual_value, expected_value):
                return False
        else:
            if actual_value != expected_value:
                return False
    return True


summary = {
    "gate": "S9_T5_perf_and_limits",
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "scenarios": {},
}
status = "PASS"
notes = []

for scenario_id, question in SCENARIOS.items():
    metrics_s9.reset()
    admin_service.prepare_scenario_sources(scenario_id)
    golden = json.loads(GOLDENS[scenario_id].read_text(encoding="utf-8"))
    payload = {"question": question, "scenario_id": scenario_id}
    durations = []
    errors = 0
    stability_failures = 0
    throughput_start = time.perf_counter()
    for idx in range(THROUGHPUT_QUERIES):
        t0 = time.perf_counter()
        try:
            response = user_routes.post_query(payload)["response"]
        except Exception:
            errors += 1
            continue
        durations.append(time.perf_counter() - t0)
        if idx < 30 and not _within_tolerance(response["summary_card"], golden["summary_card"]):
            stability_failures += 1
    throughput_duration = time.perf_counter() - throughput_start

    for _ in range(TOTAL_QUERIES - THROUGHPUT_QUERIES):
        t0 = time.perf_counter()
        try:
            response = user_routes.post_query(payload)["response"]
        except Exception:
            errors += 1
            continue
        durations.append(time.perf_counter() - t0)
        if not _within_tolerance(response["summary_card"], golden["summary_card"]):
            stability_failures += 1

    p50 = _percentile(durations, 0.5)
    p95 = _percentile(durations, 0.95)
    error_rate = errors / TOTAL_QUERIES
    scenario_data = {
        "total_queries": TOTAL_QUERIES,
        "p50_seconds": round(p50, 4),
        "p95_seconds": round(p95, 4),
        "error_rate": round(error_rate, 4),
        "stability_failures": stability_failures,
        "throughput_duration_seconds": round(throughput_duration, 2)
    }
    summary["scenarios"][scenario_id] = scenario_data

    if p95 > P95_TARGET:
        status = "FAIL"
        notes.append(f"{scenario_id} p95 acima de {P95_TARGET}s")
    if error_rate >= MAX_ERROR_RATE:
        status = "FAIL"
        notes.append(f"{scenario_id} erro >= {MAX_ERROR_RATE*100:.0f}%")
    if stability_failures > 0:
        status = "FAIL"
        notes.append(f"{scenario_id} detectou variação em {stability_failures} respostas")
    if throughput_duration > 120:
        status = "FAIL"
        notes.append(f"{scenario_id} throughput demorou {throughput_duration:.2f}s")

summary["status"] = status
summary["notes"] = notes
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
  "gate": "S9_T5",
  "name": "Performance & Limits",
  "status": "$RESULT",
  "summary_path": "out/evidence/S9_T5_perf_and_limits/summary.json"
}
JSON

if [[ "$RESULT" != "PASS" ]]; then
  exit 1
fi
