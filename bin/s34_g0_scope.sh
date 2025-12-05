#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

EVIDENCE_DIR="out/evidence/S34_G0_scope_and_templates"
SCORECARD_PATH="out/scorecards/S34_G0_scope.json"
LOG="$EVIDENCE_DIR/run.log"

mkdir -p "$EVIDENCE_DIR" out/scorecards

echo "[S34_G0] Validando escopo (24 arquivos), templates, limites, flags e mapa de SLOs" | tee "$LOG"

python3 - <<'PY' 2>&1 | tee -a "$LOG"
import datetime
import json
import os
import pathlib
import re
import sys

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None

root = pathlib.Path(".")
status = "PASS"
errors = []
warnings = []

def fail(msg: str) -> None:
    global status
    status = "FAIL"
    errors.append(msg)

# 1) Validar 24 blocos 6x4
missing_blocks = []
for cap in range(1, 7):
    for bloco in range(1, 5):
        path = root / f"Programa 1/Epico 28/Sprint 34/Capitulo {cap}/Bloco {bloco}.md"
        if not path.exists():
            missing_blocks.append(str(path))
if missing_blocks:
    fail(f"Blocos faltando: {missing_blocks}")

# 2) Templates esperados
templates = {
    "news_v2": root / "config/flow_templates/news_v2.yaml",
    "contestacao_v0": root / "config/flow_templates/contestacao_v0.yaml",
}
for slug, path in templates.items():
    if not path.exists():
        fail(f"Template ausente: {path}")
        continue
    content = path.read_text().strip()
    if not content:
        fail(f"Template vazio: {path}")
    if slug not in content:
        warnings.append(f"Slug {slug} não encontrado textualmente em {path}")
    if yaml:
        try:
            data = yaml.safe_load(content)
            for field in ["id", "slug", "version", "domain", "entry_type", "steps"]:
                if field not in data:
                    fail(f"Campo '{field}' ausente em {path}")
            if data.get("slug") != slug:
                warnings.append(f"Slug esperado {slug} difere do slug em {path}")
            steps = data.get("steps") or []
            if not steps:
                fail(f"Template sem steps em {path}")
        except Exception as exc:
            fail(f"Erro ao parsear {path}: {exc}")
    else:
        warnings.append("PyYAML não instalado; validação de conteúdo dos templates parcial.")

# 3) Limites e flags
limits_path = root / "config/flows_limits.yaml"
expected_limits = [
    "max_rollbacks_per_hour",
    "max_test_percentual",
    "max_versions_to_keep",
    "operation_timeout_seconds",
    "alert_rollbacks_threshold",
    "alert_policy_violations_threshold",
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
    "s34_flow_multidomain_enabled",
    "s34_flow_console_history_enabled",
    "s34_flow_rollout_test_enabled",
]
if not flags_path.exists():
    fail(f"Arquivo de flags ausente: {flags_path}")
else:
    text = flags_path.read_text()
    for flag in required_flags:
        if f"{flag}:" not in text:
            fail(f"Flag '{flag}' ausente em {flags_path}")

# 4) Mapa de componentes e SLOs
components_map = root / "Programa 1/Epico 28/Sprint 34/s34_components_map.yaml"
slos_doc = root / "Programa 1/Epico 28/Sprint 34/s34_slos.md"
component_ids = []
slo_ids = []
if not components_map.exists():
    fail(f"Mapa de componentes ausente: {components_map}")
else:
    text = components_map.read_text()
    if yaml:
        try:
            payload = yaml.safe_load(text) or {}
            for comp in payload.get("components", []) or []:
                cid = comp.get("id")
                if cid:
                    component_ids.append(cid)
                    for slo in comp.get("slos") or []:
                        if slo not in slo_ids:
                            slo_ids.append(slo)
        except Exception as exc:
            fail(f"Erro ao parsear {components_map}: {exc}")
    else:
        for line in text.splitlines():
            m = re.match(r"^\s*- id:\s*(\S+)", line)
            if m:
                component_ids.append(m.group(1))
        warnings.append("PyYAML não instalado; checagem parcial do mapa de componentes.")

if not slos_doc.exists():
    fail(f"SLO doc ausente: {slos_doc}")
else:
    current = None
    metrics_found = {}
    for line in slos_doc.read_text().splitlines():
        m_slo = re.match(r"^##\s+(s34_slo_[a-z0-9_]+)", line.strip())
        if m_slo:
            current = m_slo.group(1)
            slo_ids.append(current)
            metrics_found[current] = False
        if current and line.lower().strip().startswith("- metrica:"):
            metrics_found[current] = True
    missing_metrics = [s for s, ok in metrics_found.items() if not ok]
    if missing_metrics:
        fail(f"SLOs sem métrica declarada: {missing_metrics}")

if component_ids and slo_ids:
    missing_refs = []
    if yaml and components_map.exists():
        payload = yaml.safe_load(components_map.read_text()) or {}
        for comp in payload.get("components", []) or []:
            for slo in comp.get("slos") or []:
                if slo not in slo_ids:
                    missing_refs.append(slo)
    if missing_refs:
        fail(f"SLOs referenciados no mapa e não definidos: {missing_refs}")

scorecard = {
    "gate": "S34_G0_scope",
    "status": status,
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "errors": errors,
    "warnings": warnings,
    "counts": {
        "blocks_present": 24 - len(missing_blocks),
        "templates_present": sum(1 for p in templates.values() if p.exists()),
        "components": len(component_ids),
        "slos": len(set(slo_ids)),
    },
}
pathlib.Path("out/scorecards").mkdir(parents=True, exist_ok=True)
pathlib.Path("out/scorecards/S34_G0_scope.json").write_text(json.dumps(scorecard, indent=2))
print(json.dumps(scorecard, indent=2))
PY

exit 0
