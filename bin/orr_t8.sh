#!/usr/bin/env bash
# Wrapper retained for backward compatibility. For Sprint 3 the official
# T8 (go/no-go) gate lives in bin/orr_t8_go_no_go.sh.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/orr_t8_go_no_go.sh" "$@"
