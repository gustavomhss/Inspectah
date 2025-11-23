#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S17_1_T5_performance_and_limits"
SCORECARD_PATH="$SCORECARD_DIR/S17_1_T5_performance_and_limits.json"
PYTHON_BIN="${PYTHON_BIN:-python3}"
if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
fi

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

PYTHONPATH="$ROOT_DIR" "$PYTHON_BIN" - <<'PY' "$EVIDENCE_DIR" "$SCORECARD_PATH"
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from inspectah.api import build_app


evidence_dir = Path(sys.argv[1])
scorecard_path = Path(sys.argv[2])
client = TestClient(build_app())

durations = []
for _ in range(10):
    start = time.perf_counter()
    resp = client.post("/api/consultation", json={"question": "Teste rápido de performance no clima?"})
    resp.raise_for_status()
    durations.append((time.perf_counter() - start) * 1000.0)

metrics = {
    "count": len(durations),
    "max_ms": max(durations),
    "avg_ms": sum(durations) / len(durations),
}
(evidence_dir / "latency_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
status = "PASS" if metrics["max_ms"] < 1500 else "FAIL"
scorecard = {
    "gate": "S17_1_T5_performance_and_limits",
    "status": status,
    "metrics": metrics,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S17_1_T5] Latência acima do limite esperado.")
PY

echo "[S17_1_T5] OK. Scorecard em $SCORECARD_PATH"
