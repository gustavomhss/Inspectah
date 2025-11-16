#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

PY_BIN="$ROOT/.venv/bin/python"
if [[ ! -x "$PY_BIN" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    PY_BIN="python3"
  else
    PY_BIN="python"
  fi
fi

cleanup() {
  bin/dev_down.sh >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "[e2e] starting dev environment"
bin/dev_up.sh >/dev/null

FIXTURE_PATH="${E2E_FIXTURE_PATH:-tests/fixtures/rss_sample.xml}"
export E2E_FIXTURE_PATH_VALUE="$FIXTURE_PATH"

echo "[e2e] running Inspectah v0 flow"
"$PY_BIN" - <<'PY'
import json
import os
from inspectah.explore.api import query_items
from inspectah.ingest.pipeline import run_ingest_pipeline
from inspectah.metrics import get_snapshot

fixture_path = os.environ["E2E_FIXTURE_PATH_VALUE"]
result = run_ingest_pipeline('rss_news_minimal', use_fixture=True, fixture_path=fixture_path)
print({"stage": "ingest", "items_ingested": result.items_ingested})

items = query_items()["items"]
if not items:
    raise SystemExit("Explore API returned no items")
first = items[0]
print({"stage": "explore", "items_count": len(items), "first_item_id": first["item_id"]})

snapshot = get_snapshot()
print({
    "stage": "metrics",
    "ingest_items_total": snapshot["inspectah_ingest_items_total"],
    "explore_queries_total": snapshot["inspectah_explore_queries_total"],
})

manifest_path = first["manifest_path"]
with open(manifest_path, 'r', encoding='utf-8') as handle:
    manifest = json.load(handle)
print({"stage": "manifest", "manifest_path": manifest_path, "source_id": manifest['source_id'], "content_hash": manifest['content_hash']})
PY

echo "[e2e] run complete"
