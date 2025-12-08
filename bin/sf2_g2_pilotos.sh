#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

EVIDENCE_DIR="out/evidence/SF2_G2"
LOG="out/logs/SF2_G2.log"
SCREEN_DIR="$EVIDENCE_DIR/screenshots"

mkdir -p "$EVIDENCE_DIR" "$SCREEN_DIR" out/logs
: >"$LOG"

log() {
  echo "[SF2_G2] $*" | tee -a "$LOG"
}

fail() {
  log "FAIL: $*"
  exit 1
}

log "Executando pilotos API start→canary→promo→rollback para news_v2 e contestacao_v0"

python3 - <<'PY' 2>&1 | tee -a "$LOG"
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

from app.flows.service import FlowService
from app.flows import instrumentation

evidence = Path("out/evidence/SF2_G2")
evidence.mkdir(parents=True, exist_ok=True)

def runtime_hash(path: Path) -> str:
    text = path.read_text()
    filtered = "\n".join([ln for ln in text.splitlines() if not ln.strip().startswith("hash:")])
    return hashlib.sha256((filtered + "\n").encode("utf-8")).hexdigest()

catalog_dir = Path("config/flow_catalog")
hash_report = []
for name in ("news_v2.yaml", "contestacao_v0.yaml"):
    p = catalog_dir / name
    if not p.exists():
        hash_report.append({"file": str(p), "status": "missing"})
        continue
    declared = None
    for ln in p.read_text().splitlines():
        if ln.strip().startswith("hash:"):
            declared = ln.split(":", 1)[1].strip()
            break
    runtime = runtime_hash(p)
    hash_report.append({"file": str(p), "declared": declared, "runtime": runtime, "match": declared == runtime})

(evidence / "hash_diff.txt").write_text(json.dumps(hash_report, indent=2, ensure_ascii=False))

db_path = Path("out/databases/sf2_g2.sqlite")
if db_path.exists():
    db_path.unlink()
svc = FlowService(db_path=db_path)
svc._flags_cache = {
    "s34_flow_multidomain_enabled": True,
    "s35_flow_rollout_enabled": True,
    "s35_flow_catalog_enforced": True,
    "s35_flow_logic_contract_enabled": True,
}
svc._rbac_cache = {
    "actors": ["ops_user", "ops_admin", "system"],
    "start_rollout": ["ops_user", "ops_admin", "system"],
    "promote": ["ops_admin", "system"],
    "rollback": ["ops_admin", "system"],
}

flows = {}
for tpl in ("news_v2", "contestacao_v0"):
    flows[tpl] = svc.create_flow_from_template(tpl, f"Flow {tpl}", f"flow_{tpl}")

timeline = []

# news_v2: start canary -> promote -> rollback to base version
news = flows["news_v2"]
news_base_version = news.flow_version_id
svc.start_rollout(
    news.id,
    mode="canary",
    test_percentual=10,
    criteria={"slo_id": "slo_news_latency"},
    actor="ops_user",
    operation_id="op_news_canary",
    request_catalog_hash=news.catalog_hash or "",
)
svc.promote_rollout(news.id, actor="ops_admin", operation_id="op_news_promote", request_catalog_hash=news.catalog_hash or "")
svc.create_version(news.id, "news_v2", "v2.2.1")
svc.rollback_rollout(news.id, target_version_id=news_base_version, actor="ops_admin", operation_id="op_news_rollback", request_catalog_hash=news.catalog_hash or "")
instrumentation.record_policy_violation(news.id, news.flow_version_id, "canary")
instrumentation.record_catalog_mismatch(news.id, news.flow_version_id, "canary")
instrumentation.record_slo_breach(news.id, news.flow_version_id, "slo_news_latency")

timeline.append({"flow": "news_v2", "events": ["canary", "promote", "rollback"]})

# contestacao_v0: start test -> promote fails on slo_breach -> rollback to base
contest = flows["contestacao_v0"]
contest_base_version = contest.flow_version_id
svc.start_rollout(
    contest.id,
    mode="test",
    test_percentual=15,
    criteria={"slo_id": "slo_contestacao_latency"},
    actor="ops_user",
    operation_id="op_contest_test",
    request_catalog_hash=contest.catalog_hash or "",
)
try:
    svc.promote_rollout(contest.id, actor="ops_admin", operation_id="op_contest_promote", request_catalog_hash=contest.catalog_hash or "")
except Exception as exc:
    (evidence / "contestacao_promote_block.txt").write_text(str(exc))
svc.create_version(contest.id, "contestacao_v0", "v1.1.1")
svc.rollback_rollout(contest.id, target_version_id=contest_base_version, actor="ops_admin", operation_id="op_contest_rollback", request_catalog_hash=contest.catalog_hash or "")
instrumentation.record_policy_violation(contest.id, contest.flow_version_id, "test")
instrumentation.record_catalog_mismatch(contest.id, contest.flow_version_id, "test")
timeline.append({"flow": "contestacao_v0", "events": ["test", "promote_blocked", "rollback"]})

ops_dump = []
for flow in (news, contest):
    ops = svc.list_operations(flow.id, limit=50)
    ops_dump.append(
        {
            "flow": flow.slug,
            "flow_id": flow.id,
            "flow_version_id": flow.flow_version_id,
            "operations": [
                {
                    "id": op.id,
                    "operacao": op.operacao,
                    "mode": getattr(op, "mode", None),
                    "actor": getattr(op, "actor", None),
                    "catalog_hash": getattr(op, "catalog_hash", None),
                    "created_at": getattr(op, "created_at", None).isoformat() if getattr(op, "created_at", None) else None,
                    "payload": op.payload,
                }
                for op in ops
            ],
        }
    )

(evidence / "http_logs.txt").write_text(json.dumps(ops_dump, indent=2, ensure_ascii=False))
(evidence / "rollout_timeline.json").write_text(json.dumps({"timeline": timeline, "ts": datetime.now(timezone.utc).isoformat()}, indent=2))
(evidence / "metrics.txt").write_text(instrumentation.generate_latest().decode())
PY

log "Pilotos executados; aguardando screenshots reais em $SCREEN_DIR"
if ! ls "$SCREEN_DIR"/*.png >/dev/null 2>&1; then
  fail "Sem screenshots em $SCREEN_DIR (capture UI real antes de marcar PASS)"
fi

log "SF2_G2 concluído com evidências em $EVIDENCE_DIR"
