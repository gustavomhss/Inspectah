#!/usr/bin/env bash
set -euo pipefail
SOURCE_ID="${1:-rss_news_minimal}"
FIXTURE_PATH="${2:-}"
python3 - <<'PY' "$SOURCE_ID" "$FIXTURE_PATH"
import sys
from inspectah.models import init_db
from inspectah.watchers import run_once_for_source
source_id = sys.argv[1]
fixture = sys.argv[2]
init_db()
kwargs = {}
mode = 'live'
if fixture:
    kwargs['use_fixture'] = True
    kwargs['fixture_path'] = fixture
    mode = 'fixture'
created = run_once_for_source(source_id, **kwargs)
print(f"items_created={created} mode={mode} source={source_id}")
PY
echo "STATUS=OK"
