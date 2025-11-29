#!/usr/bin/env bash
set -euo pipefail

API_BASE_URL="${API_BASE_URL:-http://127.0.0.1:8000}"

echo ">> Checking console endpoints on ${API_BASE_URL}"

set -x
curl -f -s -o /dev/null -w "STATUS:%{http_code}\n" "${API_BASE_URL}/api/console/agents"
curl -f -s -o /dev/null -w "STATUS:%{http_code}\n" "${API_BASE_URL}/api/console/agents/flow"
set +x
