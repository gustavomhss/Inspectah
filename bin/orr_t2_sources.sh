#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}" )/.." && pwd)
export ROOT
EVIDENCE_DIR="$ROOT/out/evidence/S4_T2_sources"
SCORECARD_DIR="$ROOT/out/scorecards"
mkdir -p "$EVIDENCE_DIR" "$SCORECARD_DIR"
python3 <<'PY'
import json, os, glob, sys, hashlib
root = os.environ["ROOT"]
config_dir = os.path.join(root, "config", "sources", "sprint_4", "fontes_p0")
fd_dir = os.path.join(root, "config", "field_designer", "sprint_4")
evidence_dir = os.path.join(root, "out", "evidence", "S4_T2_sources")
scorecard_path = os.path.join(root, "out", "scorecards", "S4_T2_sources.json")
log_path = os.path.join(evidence_dir, "validation.log")
summary_path = os.path.join(evidence_dir, "sources_summary.json")
expected_sources = {
    "api_market_prices",
    "html_market_watch",
    "rss_news_minimal"
}
for needed in (config_dir, fd_dir):
    if not os.path.isdir(needed):
        print(f"Missing directory: {needed}", file=sys.stderr)
        sys.exit(1)
config_files = sorted(glob.glob(os.path.join(config_dir, "*.yaml")))
if not config_files:
    print("No fonte configs found", file=sys.stderr)
    sys.exit(1)
def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)
def detect_secret(obj):
    secret_tokens = ("password", "secret", "token", "key")
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(k, str) and any(tok in k.lower() for tok in secret_tokens):
                if isinstance(v, str) and not v.startswith("vault://"):
                    return True
            if detect_secret(v):
                return True
    elif isinstance(obj, list):
        for item in obj:
            if detect_secret(item):
                return True
    return False
log_lines = []
summary = {"sources": []}
failures = 0
warnings = 0
secret_flag = False
fd_cache = {}
def get_fd(schema_id):
    path = os.path.join(fd_dir, f"{schema_id}.yaml")
    if not os.path.exists(path):
        return None, path
    if schema_id not in fd_cache:
        fd_cache[schema_id] = load_json(path)
    return fd_cache[schema_id], path
seen_sources = set()
for cfg_path in config_files:
    cfg = load_json(cfg_path)
    metadata = cfg.get("metadata", {})
    source_id = metadata.get("id")
    if not source_id:
        log_lines.append(f"[ERROR] {os.path.basename(cfg_path)}: metadata.id ausente")
        failures += 1
        continue
    seen_sources.add(source_id)
    messages = []
    status = "PASS"
    required_meta_keys = {"name", "description", "type", "priority", "risk_level", "owners"}
    missing_meta = [k for k in required_meta_keys if k not in metadata]
    if missing_meta:
        status = "FAIL"
        failures += 1
        messages.append(f"metadata incompleto: {missing_meta}")
    ingest = cfg.get("ingest", {})
    if ingest.get("auth") not in (None, "", ) and isinstance(ingest.get("auth"), str) and not ingest.get("auth", "").startswith("vault://"):
        status = "FAIL"
        failures += 1
        secret_flag = True
        messages.append("auth sem referência a vault://")
    if detect_secret(cfg):
        status = "FAIL"
        failures += 1
        secret_flag = True
        messages.append("possível segredo em config")
    schema_id = cfg.get("field_schema_id")
    field_schema, fd_path = get_fd(schema_id) if schema_id else (None, None)
    if not field_schema:
        status = "FAIL"
        failures += 1
        messages.append(f"field_schema_id '{schema_id}' inválido ou arquivo ausente ({fd_path})")
        fd_fields = set()
    else:
        fd_fields = {field.get("name") for field in field_schema.get("fields", [])}
        if field_schema.get("source_id") != source_id:
            status = "FAIL"
            failures += 1
            messages.append("field_designer.source_id divergente")
    dedup = cfg.get("deduplication", {}).get("keys", [])
    missing_keys = [k for k in dedup if k not in fd_fields]
    if missing_keys:
        status = "FAIL"
        failures += 1
        messages.append(f"dedup_keys fora do Field Designer: {missing_keys}")
    if status == "PASS" and (not cfg.get("ingest") or not cfg.get("parsing")):
        status = "WARN"
        warnings += 1
        messages.append("ingest/parsing incompletos")
    if status == "PASS":
        log_lines.append(f"[INFO] {source_id}: validação concluída sem erros")
    elif status == "WARN":
        log_lines.append(f"[WARN] {source_id}: {'; '.join(messages)}")
    else:
        log_lines.append(f"[ERROR] {source_id}: {'; '.join(messages)}")
    summary["sources"].append({
        "source_id": source_id,
        "config": os.path.relpath(cfg_path, root),
        "field_schema": os.path.relpath(fd_path, root) if fd_path else None,
        "status": status,
        "messages": messages
    })
missing_sources = sorted(expected_sources - seen_sources)
for missing in missing_sources:
    failures += 1
    summary["sources"].append({
        "source_id": missing,
        "config": None,
        "field_schema": None,
        "status": "FAIL",
        "messages": ["config ausente"]
    })
    log_lines.append(f"[ERROR] {missing}: config ausente para Sprint 4")
with open(log_path, "w", encoding="utf-8") as handle:
    handle.write("\n".join(log_lines) + ("\n" if log_lines else ""))
with open(summary_path, "w", encoding="utf-8") as handle:
    json.dump(summary, handle, indent=2, ensure_ascii=False)
status_flag = "PASS" if failures == 0 else "FAIL"
checks = []
checks.append({
    "name": "p0_sources_registered",
    "status": "PASS" if not missing_sources else "FAIL",
    "details": f"Fontes esperadas: {', '.join(sorted(expected_sources))}"
})
checks.append({
    "name": "field_designer_synced",
    "status": "PASS" if all(src.get("field_schema") for src in summary["sources"] if src["status"] != "FAIL") else "FAIL",
    "details": "Todos os field_schema_id apontam para arquivos válidos"
})
checks.append({
    "name": "no_blocker_errors",
    "status": "PASS" if failures == 0 else "FAIL",
    "details": f"Falhas críticas: {failures}"
})
checks.append({
    "name": "no_secrets_in_configs",
    "status": "PASS" if not secret_flag else "FAIL",
    "details": "Nenhum valor explícito de credencial encontrado"
})
metrics = {
    "p0_sources_total": len(expected_sources),
    "sources_pass": sum(1 for s in summary["sources"] if s["status"] == "PASS"),
    "sources_warn": sum(1 for s in summary["sources"] if s["status"] == "WARN"),
    "sources_fail": sum(1 for s in summary["sources"] if s["status"] == "FAIL")
}
scorecard = {
    "sprint_id": "S4",
    "gate_id": "S4_T2",
    "gate_name": "Sprint 4 - T2 Registry & Field Designer",
    "status": status_flag,
    "summary": "Validação das Fontes P0 no registry + Field Designer concluída",
    "invariants_guarded": [
        "#7 Nenhum ajuste estrutural em Fonte P0 apenas em código",
        "#1 Nenhum Item P0 sem evidência completa (groundwork)",
        "#3 Nenhuma Fonte P0 ativa invisível (observability metadata)"
    ],
    "checks": checks,
    "metrics": metrics,
    "artifacts": [
        {"path": os.path.relpath(summary_path, root)},
        {"path": os.path.relpath(log_path, root)},
        {"path": "config/sources/sprint_4/fontes_p0"},
        {"path": "config/field_designer/sprint_4"}
    ],
    "errors": []
}
with open(scorecard_path, "w", encoding="utf-8") as handle:
    json.dump(scorecard, handle, indent=2, ensure_ascii=False)
if status_flag != "PASS":
    sys.exit(1)
PY
