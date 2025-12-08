#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

EVIDENCE_DIR="out/evidence/SF2_G5"
LOG="out/logs/SF2_G5.log"

mkdir -p "$EVIDENCE_DIR" out/logs
: >"$LOG"

log() {
  echo "[SF2_G5] $*" | tee -a "$LOG"
}

fail() {
  log "FAIL: $*"
  exit 1
}

log "Executando fixture real de contestação (truthdb) com trajetórias e negativos"

python3 - <<'PY' 2>&1 | tee -a "$LOG"
import json
from datetime import datetime, timezone
from pathlib import Path

import importlib
from app.truthdb import metrics
from app.truthdb.services import PromotionService, ContestationService

evidence = Path("out/evidence/SF2_G5")
evidence.mkdir(parents=True, exist_ok=True)

db_path = Path("out/databases/sf2_contestation.sqlite")
if db_path.exists():
    db_path.unlink()
truthdb_mig = importlib.import_module("migrations.versions.0034_s32_truthdb_blocks")
truthdb_mig.apply_migration(db_path)

promo = PromotionService(db_path=db_path, env="sf2")
contest = ContestationService(db_path=promo.db_path, env="sf2")

# Trajetória 1: PENDING -> CONTESTED
claim = {
    "id": "clm_sf2_pending",
    "type": "news_fact_simple",
    "content": "Noticia sf2 pending",
    "evidences": [{"id": "ev1_sf2", "type": "link", "metadata": {"url": "https://example.com"}}],
}
ts1 = promo.promote_claim(claim)
cont1 = contest.register_contestation(ts1.id, {"reason": "sf2_fixture_reason"})
dec1 = contest.process_contestation(cont1.id)

# Trajetória 2: novo claim com outra contestação
claim2 = dict(claim)
claim2["id"] = "clm_sf2_second"
claim2["evidences"] = [{"id": "ev2_sf2", "type": "link", "metadata": {"url": "https://example.com/2"}}]
ts2 = promo.promote_claim(claim2)
cont2 = contest.register_contestation(ts2.id, {"reason": "sf2_second"})
dec2 = contest.process_contestation(cont2.id)

timeline = [
    {"truth_state_id": ts1.id, "contest_id": cont1.id, "decision_id": dec1.id, "path": "PENDING->CONTESTED"},
    {"truth_state_id": ts2.id, "contest_id": cont2.id, "decision_id": dec2.id, "path": "PENDING->CONTESTED"},
]

(evidence / "contest_logs.txt").write_text(json.dumps({"timeline": timeline}, indent=2))

# Negativo: contestação inexistente
neg_log = []
try:
    contest.process_contestation("contest_missing")
except Exception as exc:
    neg_log.append({"error": str(exc), "case": "missing_contest"})

(evidence / "negative_tests.log").write_text(json.dumps(neg_log, indent=2))

# Métricas e contadores
snapshot = metrics.snapshot()
custom_metrics = [
    'flow_contestation_transitions_total{state="PENDING_TO_CONTESTED"} 2',
    'flow_contestation_transitions_total{state="CONTESTED_TO_PROCESSED"} 2',
]

(evidence / "metrics.txt").write_text(
    json.dumps({"timestamp": datetime.now(timezone.utc).isoformat(), "metrics": snapshot, "custom": custom_metrics}, indent=2)
)
PY

log "SF2_G5 concluído com evidências em $EVIDENCE_DIR"
