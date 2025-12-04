#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT_DIR/out"
EVIDENCE_DIR="$OUT_DIR/evidence/S31_metrics"
SUMMARY_PATH="$EVIDENCE_DIR/metrics_summary.json"

mkdir -p "$EVIDENCE_DIR"

cd "$ROOT_DIR"
PYTHONPATH=. python - <<'PY' "$SUMMARY_PATH"
import json
import sys
from pathlib import Path

from app.ingestion.content_repo import ContentRepository
from app.providers.run_store import RunStore
from app.providers.service import ProviderService

out_path = Path(sys.argv[1])
svc = ProviderService()
store = RunStore()
repo = ContentRepository()

providers = svc.list_providers()
profiles = svc.list_profiles()
runs = store.list_runs(profile_id=None, limit=500)

summary = {
    "providers": len(providers),
    "profiles": len(profiles),
    "runs_recorded": len(runs),
    "last_run_at": (runs[-1]["finished_at"] if runs else None),
    "content_items": len(repo.list_items(limit=1000)),
}
out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(summary, indent=2, ensure_ascii=False))
PY
