#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )/.." && pwd)"
if [[ ! -d "$ROOT_DIR/.git" ]]; then
  >&2 echo "[S13][G1] Script precisa rodar a partir da raiz do repo."
  exit 2
fi

SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S13_G1"
SCORECARD_PATH="$SCORECARD_DIR/S13_G1_pilotos_multi_dominio.json"
EVIDENCE_PATH="$EVIDENCE_DIR/pilotos_resolved.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

python3 - <<'PY' "$SCORECARD_PATH" "$EVIDENCE_PATH"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from scripts import s13_pilots_registry as registry

scorecard_path = Path(sys.argv[1])
evidence_path = Path(sys.argv[2])

try:
    data = registry.load_pilots_config()
except Exception as exc:
    ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    scorecard_path.write_text(
        json.dumps(
            {"gate": "S13_G1", "status": "FAIL", "error": f"Erro ao carregar config: {exc}", "ts": ts},
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    raise

expected = registry.EXPECTED_DOMAINS
covered = [domain for domain in expected if data.get(domain)]
missing = [domain for domain in expected if not data.get(domain)]
total_pilots = sum(len(data[domain]) for domain in expected)
coverage = len(covered) / len(expected)
status = "PASS" if coverage == 1.0 else "FAIL"

evidence = {domain: data[domain] for domain in expected}
evidence_path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")

ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
payload = {
    "gate": "S13_G1",
    "status": status,
    "ts": ts,
    "metrics": {
        "domain_pilot_coverage": round(coverage, 3),
        "total_pilots": total_pilots,
        "domains_covered": covered,
        "domains_missing": missing,
    },
}
scorecard_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

if status != "PASS":
    raise SystemExit("S13-G1 falhou. Corrija os pilotos ausentes.")
PY

printf '[S13][G1] Cobertura de pilotos validada. Scorecard em %s\n' "$SCORECARD_PATH"
