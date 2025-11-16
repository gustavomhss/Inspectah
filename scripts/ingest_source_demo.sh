#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

PYTHON_BIN="$ROOT/.venv/bin/python"
if [[ ! -x "$PYTHON_BIN" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  else
    PYTHON_BIN="python"
  fi
fi

FIXTURE="${FIXTURE_PATH:-tests/fixtures/rss_sample.xml}"

"$PYTHON_BIN" -m inspectah.ingest.cli \
  --source-id rss_news_minimal \
  --use-fixture \
  --fixture-path "$FIXTURE"
