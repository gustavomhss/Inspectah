#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

OUT_DIR="out/scorecards"
EVIDENCE_DIR="out/evidence/S35_metrics_summary"
SCORECARD_PATH="$OUT_DIR/S35_metrics_summary.json"
LOG="$EVIDENCE_DIR/run.log"
OUT_LOG="out/logs/SF1_bin_s35_metrics_summary.log"

mkdir -p "$OUT_DIR" "$EVIDENCE_DIR" out/logs

echo "[S35_metrics_summary] Gerando resumo de métricas de rollout" | tee "$LOG" "$OUT_LOG"

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
if [ ! -x "$PYTHON_BIN" ]; then
  PYTHON_BIN="python3"
fi

$PYTHON_BIN - <<'PY' 2>&1 | tee -a "$LOG" "$OUT_LOG"
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from app.flows.service import FlowService

SCORECARD_PATH = os.environ.get("SCORECARD_PATH", "out/scorecards/S35_metrics_summary.json")
svc = FlowService()
targets = ["flow_news_v2", "flow_contestacao_v0"]
flows = {f.slug: f for f in svc.list_flows() if f.slug in targets}

warnings = []
for slug in targets:
    if slug not in flows:
        warnings.append(f"Flow {slug} não encontrado para métricas.")

def _count_ops(slug: str, name: str) -> int:
    if slug not in flows:
        return 0
    ops = svc.list_operations(flows[slug].id, limit=100)
    return sum(1 for op in ops if op.operacao == name)

summary = {
    "flow_rollout_requests_total": sum(_count_ops(slug, "start_rollout") for slug in targets),
    "flow_rollout_success_total": sum(_count_ops(slug, "promote") for slug in targets),
    "flow_rollout_rollback_total": sum(_count_ops(slug, "rollback") for slug in targets),
    "flow_policy_violations_total": sum(_count_ops(slug, "policy_violation") for slug in targets),
}

Path(SCORECARD_PATH).write_text(json.dumps({
    "status": "PASS" if summary["flow_rollout_requests_total"] > 0 else "WARN",
    "summary": summary,
    "warnings": warnings,
    "timestamp": datetime.now(timezone.utc).isoformat()
}, indent=2))
PY

echo "[S35_metrics_summary] Resumo salvo em $SCORECARD_PATH" | tee -a "$LOG" "$OUT_LOG"
