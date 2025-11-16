#!/usr/bin/env bash
set -euo pipefail

# Smoke test for the Explore API rate limit (120/min burst 240).
# By default this script manages the dev server lifecycle via bin/dev_up.sh/bin/dev_down.sh.
# Set MANAGE_SERVER=0 to run against an already running instance.

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
IDENTITY_HEADER="${IDENTITY_HEADER:-X-Client-Id}"
CLIENT_ID="${CLIENT_ID:-rate-limit-smoke}"
TOTAL_REQUESTS="${TOTAL_REQUESTS:-300}"
MANAGE_SERVER="${MANAGE_SERVER:-1}"

wait_for_server() {
  local attempts=0
  while [[ $attempts -lt 30 ]]; do
    if curl -s -o /dev/null "${BASE_URL}/explore/items" >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
    attempts=$((attempts + 1))
  done
  echo "[rate_limit_smoke] API não respondeu em ${BASE_URL} após ${attempts}s" >&2
  return 1
}

cleanup() {
  if [[ "${MANAGE_SERVER}" == "1" ]]; then
    bin/dev_down.sh >/dev/null
  fi
}
trap cleanup EXIT

if [[ "${MANAGE_SERVER}" == "1" ]]; then
  bin/dev_up.sh >/dev/null
  # Give the server a brief moment to accept connections.
  if ! wait_for_server; then
    exit 1
  fi
else
  echo "[rate_limit_smoke] Assuming API already running at ${BASE_URL}"
fi

SUCCESS=0
THROTTLED=0

echo "[rate_limit_smoke] Exercising ${TOTAL_REQUESTS} requests against ${BASE_URL}/explore/items"

for attempt in $(seq 1 "${TOTAL_REQUESTS}"); do
  TMP_HEADERS="$(mktemp)"
  TMP_BODY="$(mktemp)"
  if ! STATUS="$(curl -s -D "${TMP_HEADERS}" -o "${TMP_BODY}" -w "%{http_code}" \
    -H "${IDENTITY_HEADER}: ${CLIENT_ID}" \
    "${BASE_URL}/explore/items?page_size=5")"; then
    echo "[rate_limit_smoke] Falha ao chamar /explore/items na tentativa ${attempt}" >&2
    cat "${TMP_BODY}" >&2 || true
    rm -f "${TMP_HEADERS}" "${TMP_BODY}"
    exit 1
  fi

  if [[ "${STATUS}" == "200" ]]; then
    ((SUCCESS+=1))
    if [[ "${attempt}" -le 3 ]]; then
      echo "--- 2xx sample headers (request ${attempt}) ---"
      grep -E 'X-RateLimit-' "${TMP_HEADERS}" || true
    fi
  elif [[ "${STATUS}" == "429" ]]; then
    ((THROTTLED+=1))
    echo "--- 429 rate limited on request ${attempt} ---"
    cat "${TMP_BODY}"
    grep -E 'X-RateLimit-' "${TMP_HEADERS}" || true
  else
    echo "[rate_limit_smoke] Unexpected status ${STATUS} on request ${attempt}"
    cat "${TMP_BODY}"
  fi

  rm -f "${TMP_HEADERS}" "${TMP_BODY}"
done

echo "[rate_limit_smoke] Success responses : ${SUCCESS}"
echo "[rate_limit_smoke] Rate limited      : ${THROTTLED}"
echo "[rate_limit_smoke] Headers captured above show X-RateLimit-* for evidence."
