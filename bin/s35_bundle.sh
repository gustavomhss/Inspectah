#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

OUT_DIR="out/bundles"
EVIDENCE_DIR="out/evidence/S35_bundle"
SNAPSHOT_DIR="$EVIDENCE_DIR/snapshot"
MANIFEST_PATH="out/evidence/S35_manifest.txt"
ZIP_PATH="$OUT_DIR/inspectah_s35_evidence_bundle.zip"
LOG="out/logs/SF1_bin_s35_bundle.log"
EVIDENCE_LOG="$EVIDENCE_DIR/run.log"

mkdir -p "$OUT_DIR" "$EVIDENCE_DIR" "$SNAPSHOT_DIR" out/logs

: > "$LOG"
: > "$EVIDENCE_LOG"

log() {
  echo "$@" | tee -a "$LOG" "$EVIDENCE_LOG"
}

log "[S35_bundle] Gerando manifest assinado (catalogo + s35_slos.md) e empacotando evidências"

python3 - <<'PY' 2>&1 | tee -a "$LOG" "$EVIDENCE_LOG"
import datetime
import hashlib
import json
import subprocess
from pathlib import Path

root = Path(".")
catalog_dir = root / "config/flow_catalog"
slos_path = root / "Programa 1/Epico 28/Sprint 35/s35_slos.md"
snapshot_dir = Path("out/evidence/S35_bundle/snapshot")
manifest_path = Path("out/evidence/S35_manifest.txt")

items = []
errors = []

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def read_declared(path: Path) -> tuple[str | None, str | None]:
    raw_text = path.read_text()
    declared_hash = None
    declared_signature = None
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(raw_text) or {}
        declared_hash = str(data.get("hash")) if data.get("hash") else None
        declared_signature = str(data.get("signature")) if data.get("signature") else None
    except Exception as exc:
        # fallback parsing manual para não depender de PyYAML
        for line in raw_text.splitlines():
            if ":" not in line or line.strip().startswith("#"):
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if key == "hash":
                declared_hash = value or None
            if key == "signature":
                declared_signature = value or None
        if declared_hash is None and declared_signature is None:
            errors.append(f"Erro parseando {path}: {exc}")
    return declared_hash, declared_signature

snapshot_dir.mkdir(parents=True, exist_ok=True)

for catalog_file in sorted(catalog_dir.glob("*.yaml")):
    text = catalog_file.read_text()
    content = text.encode("utf-8")
    filtered = "\n".join([line for line in text.splitlines() if not line.strip().startswith("hash:")])
    runtime_hash = sha256_bytes((filtered + "\n").encode("utf-8"))
    declared_hash, declared_signature = read_declared(catalog_file)
    item = {
        "path": str(catalog_file),
        "runtime_sha256": runtime_hash,
        "declared_hash": declared_hash,
        "signature": declared_signature or "missing_signature",
    }
    if declared_hash and declared_hash != runtime_hash:
        errors.append(
            f"Hash divergente em {catalog_file}: declarado {declared_hash}, runtime {runtime_hash}"
        )
    if not declared_hash:
        errors.append(f"Hash ausente em {catalog_file}")
    items.append(item)
    snapshot_target = snapshot_dir / catalog_file.name
    snapshot_target.write_bytes(content)

if not catalog_dir.exists():
    errors.append("Diretório config/flow_catalog ausente")

if not slos_path.exists():
    errors.append(f"Arquivo de SLOs ausente: {slos_path}")
else:
    slos_bytes = slos_path.read_bytes()
    slos_hash = sha256_bytes(slos_bytes)
    items.append(
        {
            "path": str(slos_path),
            "runtime_sha256": slos_hash,
            "declared_hash": None,
            "signature": "s35_slos",
        }
    )
    (snapshot_dir / "s35_slos.md").write_bytes(slos_bytes)

git_rev = (
    subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
    if (root / ".git").exists()
    else "unknown"
)

manifest = {
    "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "git_rev": git_rev,
    "status": "FAIL" if errors else "PASS",
    "items": items,
    "errors": errors,
}

manifest_path.write_text(json.dumps(manifest, indent=2))

if errors:
    print("[S35_bundle] Falhou na verificação de manifest/hash:")
    for err in errors:
        print(f" - {err}")
    raise SystemExit(1)

print(json.dumps(manifest, indent=2))
PY

log "[S35_bundle] Criando bundle em $ZIP_PATH com scorecards + evidências"
zip -r "$ZIP_PATH" out/scorecards out/evidence >/dev/null

log "[S35_bundle] Verificando integridade do zip"
zip -T "$ZIP_PATH" >/dev/null

log "[S35_bundle] Bundle pronto: $ZIP_PATH"
