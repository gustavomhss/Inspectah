#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

EVIDENCE_DIR="out/evidence/S35_G0_scope_and_catalog"
SCORECARD_PATH="out/scorecards/S35_G0_scope.json"
LOG="$EVIDENCE_DIR/run.log"
OUT_LOG="out/logs/SF1_bin_s35_g0_scope.log"
PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
if [ ! -x "$PYTHON_BIN" ]; then
  PYTHON_BIN="python3"
fi

mkdir -p "$EVIDENCE_DIR" out/scorecards out/logs

echo "[S35_G0] Validando escopo (24 arquivos), catálogo/limites/flags e mapa de SLOs" | tee "$LOG" "$OUT_LOG"

$PYTHON_BIN - <<'PY' 2>&1 | tee -a "$LOG" "$OUT_LOG"
import datetime
import json
import pathlib
import re
import sys

try:
    import yaml  # type: ignore
except Exception:
    yaml = None

root = pathlib.Path(".")
status = "PASS"
errors: list[str] = []
warnings: list[str] = []

def fail(msg: str) -> None:
    global status
    status = "FAIL"
    errors.append(msg)

# 1) Validar 24 blocos 6x4 e ausência de TODO/FIXME
missing_blocks: list[str] = []
todo_hits: list[str] = []
for cap in range(1, 7):
    for bloco in range(1, 5):
        path = root / f"Programa 1/Epico 28/Sprint 35/Capitulo {cap}/Bloco {bloco}.md"
        if not path.exists():
            missing_blocks.append(str(path))
            continue
        for line in path.read_text().splitlines():
            if "sem TODO/FIXME" in line:
                continue
            if re.search(r"\b(TODO|FIXME)\b", line):
                todo_hits.append(str(path))
                break

if missing_blocks:
    fail(f"Blocos faltando: {missing_blocks}")
if todo_hits:
    fail(f"Encontrado TODO/FIXME nos blocos: {todo_hits}")

# 2) Catálogo de fluxos
catalog_dir = root / "config/flow_catalog"
expected_catalogs = {
    "news_v2": catalog_dir / "news_v2.yaml",
    "contestacao_v0": catalog_dir / "contestacao_v0.yaml",
}

if not catalog_dir.exists():
    fail(f"Diretório de catálogo ausente: {catalog_dir}")
catalog_entries = 0
for slug, path in expected_catalogs.items():
    if not path.exists():
        fail(f"Entrada de catálogo ausente: {path}")
        continue
    text = path.read_text().strip()
    if not text:
        fail(f"Entrada de catálogo vazia: {path}")
        continue
    catalog_entries += 1
    if yaml:
        try:
            data = yaml.safe_load(text) or {}
            required_fields = [
                "flow_id",
                "domain",
                "version",
                "template_ref",
                "policies",
                "rollout_defaults",
                "hash",
                "signature",
            ]
            for field in required_fields:
                if not data.get(field):
                    fail(f"Campo '{field}' ausente ou vazio em {path}")
            tmpl = data.get("template_ref")
            if tmpl:
                tmpl_path = root / str(tmpl)
                if not tmpl_path.exists():
                    warnings.append(f"Template referenciado não existe: {tmpl_path}")
            catalog_hash = str(data.get("hash", ""))
            if len(catalog_hash) < 16:
                warnings.append(f"Hash curto em {path}")
        except Exception as exc:
            fail(f"Erro ao parsear {path}: {exc}")
    else:
        # Fallback mínimo sem PyYAML: checa presença dos campos top-level
        required_fields = [
            "flow_id:",
            "domain:",
            "version:",
            "template_ref:",
            "policies:",
            "rollout_defaults:",
            "hash:",
            "signature:",
        ]
        for field in required_fields:
            if field not in text:
                fail(f"Campo '{field}' ausente em {path} (checagem fallback)")

# 3) Limites e flags
limits_path = root / "config/flows_limits.yaml"
expected_limits = [
    "max_rollbacks_per_hour",
    "max_test_percentual",
    "max_versions_to_keep",
    "operation_timeout_seconds",
    "alert_rollbacks_threshold",
    "alert_policy_violations_threshold",
    "max_canary_duration_minutes",
]
if not limits_path.exists():
    fail(f"Arquivo de limites ausente: {limits_path}")
else:
    text = limits_path.read_text()
    for key in expected_limits:
        if f"{key}:" not in text:
            fail(f"Limite '{key}' ausente em {limits_path}")

flags_path = root / "config/feature_flags.yaml"
required_flags = [
    "s35_flow_rollout_enabled",
    "s35_flow_catalog_enforced",
    "s35_flow_logic_contract_enabled",
]
if not flags_path.exists():
    fail(f"Arquivo de flags ausente: {flags_path}")
else:
    text = flags_path.read_text()
    for flag in required_flags:
        if f"{flag}:" not in text:
            fail(f"Flag '{flag}' ausente em {flags_path}")

# 4) Mapa de SLOs rollout
slos_doc = root / "Programa 1/Epico 28/Sprint 35/s35_slos.md"
found_slos: dict[str, bool] = {}
if not slos_doc.exists():
    fail(f"SLO doc ausente: {slos_doc}")
else:
    current = None
    for line in slos_doc.read_text().splitlines():
        m_slo = re.match(r"^##\s+(s35_slo_[a-z0-9_]+)", line.strip())
        if m_slo:
            current = m_slo.group(1)
            found_slos[current] = False
        if current and line.lower().strip().startswith("- metrica:"):
            found_slos[current] = True
    missing_metrics = [s for s, ok in found_slos.items() if not ok]
    if missing_metrics:
        fail(f"SLOs sem métrica declarada: {missing_metrics}")

scorecard = {
    "gate": "S35_G0_scope",
    "status": status,
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "errors": errors,
    "warnings": warnings,
    "counts": {
        "blocks_present": 24 - len(missing_blocks),
        "catalog_entries": catalog_entries,
        "slos": len(found_slos),
    },
}
pathlib.Path("out/scorecards").mkdir(parents=True, exist_ok=True)
pathlib.Path("out/scorecards/S35_G0_scope.json").write_text(json.dumps(scorecard, indent=2))
print(json.dumps(scorecard, indent=2))
PY

exit 0
