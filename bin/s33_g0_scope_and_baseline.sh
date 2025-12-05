#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

DOC_SCOPE="Programa 1/Sprint 33/s33_scope_ops.md"
DOC_SLOS="Programa 1/Sprint 33/s33_slos.md"
DOC_COMPONENTS="Programa 1/Sprint 33/s33_components_map.yaml"

mkdir -p out/scorecards out/evidence/S33_G0_scope_and_baseline
LOG="out/evidence/S33_G0_scope_and_baseline/run.log"

echo "[S33_G0] Validando escopo, SLOs e mapa de componentes" | tee "$LOG"

python3 - <<'PY' 2>&1 | tee -a "$LOG"
import json
import pathlib
import re
import sys

root = pathlib.Path(".")
doc_scope = root / "Programa 1/Sprint 33/s33_scope_ops.md"
doc_slos = root / "Programa 1/Sprint 33/s33_slos.md"
doc_components = root / "Programa 1/Sprint 33/s33_components_map.yaml"

status = "PASS"
errors = []
warnings = []

for path in (doc_scope, doc_slos, doc_components):
    if not path.exists():
        status = "FAIL"
        errors.append(f"arquivo ausente: {path}")

if status == "FAIL":
    print(json.dumps({"status": status, "errors": errors}, indent=2))
    sys.exit(0)

# parse components map (manual, sem PyYAML)
components = []
current = {}
for line in doc_components.read_text().splitlines():
    l = line.strip()
    if l.startswith("- id:"):
        if current:
            components.append(current)
            current = {}
        current["id"] = l.split(":", 1)[1].strip()
    elif l.startswith("tipo:"):
        current["tipo"] = l.split(":", 1)[1].strip()
    elif l.startswith("criticidade:"):
        current["criticidade"] = l.split(":", 1)[1].strip()
    elif l.startswith("- s33_slo_"):
        current.setdefault("slos", []).append(l.lstrip("- ").strip())
if current:
    components.append(current)

component_ids = [c.get("id") for c in components if c.get("id")]
if len(component_ids) != len(set(component_ids)):
    status = "FAIL"
    errors.append("component_ids duplicados no mapa")

# parse SLO IDs from s33_slos.md (lines starting with ## slo_id)
slo_ids = []
for line in doc_slos.read_text().splitlines():
    m = re.match(r"^##\s+(s33_slo_[a-z0-9_]+)", line.strip())
    if m:
        slo_ids.append(m.group(1))
if not slo_ids:
    status = "FAIL"
    errors.append("nenhum SLO definido em s33_slos.md")

# check metrics presence in SLO sections
slos_missing_metric = []
current_slo = None
metrics_found = {}
for line in doc_slos.read_text().splitlines():
    m = re.match(r"^##\s+(s33_slo_[a-z0-9_]+)", line.strip())
    if m:
        current_slo = m.group(1)
        metrics_found[current_slo] = False
    if current_slo and line.lower().strip().startswith("- metrica:"):
        metrics_found[current_slo] = True
for slo_id, has_metric in metrics_found.items():
    if not has_metric:
        slos_missing_metric.append(slo_id)
if slos_missing_metric:
    status = "FAIL"
    errors.append(f"SLOs sem métrica: {slos_missing_metric}")

# ensure SLO IDs referenced in components slos exist
for c in components:
    for slo in c.get("slos", []) or []:
        if slo not in slo_ids:
            status = "FAIL"
            errors.append(f"SLO '{slo}' referenciado em {c.get('id')} não existe em s33_slos.md")

# ensure scope lists reference existing components
scope_text = doc_scope.read_text()
scope_ids = []
for line in scope_text.splitlines():
    ls = line.strip()
    if re.match(r"^- `(?:fonte_|pipeline_|api_)[^`]+`", ls):
        token = ls.split("`")[1]
        scope_ids.append(token)
missing_in_map = [cid for cid in scope_ids if cid not in component_ids]
if missing_in_map:
    status = "FAIL"
    errors.append(f"IDs no escopo ausentes no mapa: {missing_in_map}")

# scorecard
scorecard = {
    "gate": "S33_G0_scope_and_baseline",
    "status": status,
    "components_total": len(component_ids),
    "slos_total": len(slo_ids),
    "errors": errors,
    "warnings": warnings,
}
path = pathlib.Path("out/scorecards/S33_G0_scope_and_baseline.json")
path.write_text(json.dumps(scorecard, indent=2))
print(json.dumps(scorecard, indent=2))
PY
