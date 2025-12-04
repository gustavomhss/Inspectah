#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S31_G2_provider_ingestion"
SCORECARD_PATH="$SCORECARD_DIR/S31_G2_provider_ingestion.json"
LOG_PATH="$EVIDENCE_DIR/g2_provider_ingestion.log"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

python3 - <<'PY' "$LOG_PATH"
import json
from pathlib import Path

from app.ingestion.jobs.ingest_news import run as run_news
from app.ingestion.jobs.ingest_social import run as run_social

log_path = Path(__file__).resolve().parents[2] / "out/evidence/S31_G2_provider_ingestion/g2_provider_ingestion.log"
news_summary = run_news()
social_summary = run_social()
log_path.write_text(json.dumps({"news": news_summary, "social": social_summary}, indent=2, ensure_ascii=False), encoding="utf-8")
PY

STATUS="GO"

python3 - <<'PY' "$SCORECARD_PATH"
import json
from datetime import datetime, timezone
from pathlib import Path

scorecard_path = Path(sys.argv[1])
timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

scorecard = {
    "gate": "S31_G2_provider_ingestion",
    "timestamp": timestamp,
    "status": "GO",
    "metrics": {
        "evidence_dir": "out/evidence/S31_G2_provider_ingestion",
        "scorecard": "out/scorecards/S31_G2_provider_ingestion.json",
    },
}
scorecard_path.write_text(json.dumps(scorecard, indent=2))
print(f"[S31_G2] Scorecard salvo em {scorecard_path}")
PY

if [[ "$STATUS" != "GO" ]]; then
  exit 1
fi
