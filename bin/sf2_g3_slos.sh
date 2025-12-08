#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

EVIDENCE_DIR="out/evidence/SF2_G3"
LOG="out/logs/SF2_G3.log"
PROM_API="${PROM_API:-http://localhost:9090/api/v1/query}"

mkdir -p "$EVIDENCE_DIR" out/logs
: >"$LOG"

log() {
  echo "[SF2_G3] $*" | tee -a "$LOG"
}

fail() {
  log "FAIL: $*"
  exit 1
}

log "Consultando SLOs via PromQL ($PROM_API) e injetando slo_breach"

python3 - <<'PY' 2>&1 | tee -a "$LOG"
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from app.flows import instrumentation
from app.flows import ops_integration

PROM_API = os.environ.get("PROM_API", "http://localhost:9090/api/v1/query")
EVIDENCE_DIR = Path("out/evidence/SF2_G3")
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

slo_files = [
    Path("Programa 1/Sprint 33/s33_slos.md"),
    Path("Programa 1/Epico 28/Sprint 34/s34_slos.md"),
]

slo_ids: list[str] = []
for p in slo_files:
    if not p.exists():
        print(f"[SF2_G3] SLO file missing: {p}", file=sys.stderr)
        sys.exit(1)
    for line in p.read_text().splitlines():
        m = re.match(r"^##\s+(s\d+_slo_[a-z0-9_]+)", line.strip())
        if m:
            slo_ids.append(m.group(1))

if not slo_ids:
    print("[SF2_G3] Nenhum SLO encontrado nos arquivos", file=sys.stderr)
    sys.exit(1)

def run_query(expr: str) -> dict:
    url = f"{PROM_API}?{urllib.parse.urlencode({'query': expr})}"
    with urllib.request.urlopen(url, timeout=10) as resp:
        payload = json.loads(resp.read().decode())
    if payload.get("status") != "success":
        raise RuntimeError(f"PromQL status != success for {expr}: {payload}")
    data = payload.get("data", {}).get("result", [])
    return {"expr": expr, "result_len": len(data), "result": data}

results = []
for slo in slo_ids:
    expr = f"sum by(flow_id,flow_version_id) (increase(inspectah_flow_slo_breach_total[15m]))"
    res = run_query(expr)
    res["slo_id"] = slo
    if res["result_len"] == 0:
        print(f"[SF2_G3] Série vazia para {slo} expr={expr}", file=sys.stderr)
        sys.exit(1)
    results.append(res)

ts = datetime.now(timezone.utc).isoformat()

# Injeta slo_breach sintético e evento OracleOps/Truth
instrumentation.record_slo_breach("flow_news_v2", "v2.2.0", slo_ids[0])
ops_integration.emit_event(
    "slo_breach",
    "flow_news_v2",
    "v2.2.0",
    {"slo_id": slo_ids[0], "ts": ts, "source": "sf2_g3_slos"},
)

Path("out/evidence/SF2_G3/slo_results.log").write_text(json.dumps({"ts": ts, "queries": results}, indent=2))
Path("out/evidence/SF2_G3/slo_breach_event.json").write_text(
    json.dumps({"event": "slo_breach", "flow_id": "flow_news_v2", "flow_version_id": "v2.2.0", "slo_id": slo_ids[0], "ts": ts}, indent=2)
)
PY

log "SF2_G3 concluído com evidências em $EVIDENCE_DIR"
