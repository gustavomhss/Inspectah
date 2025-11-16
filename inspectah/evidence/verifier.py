"""Evidence bundle verifier."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict


def verify_bundle(bundle_path: str | Path) -> Dict[str, Any]:
    """Verifica hashes do manifest e retorna status estruturado."""

    bundle_dir = Path(bundle_path)
    manifest_path = bundle_dir / "manifest.json"
    if not manifest_path.exists():
        return {"status": "FAIL", "reason": "manifest ausente", "bundle_path": str(bundle_dir)}

    manifest = json.loads(manifest_path.read_text())
    files = manifest.get("files", {})
    for name, expected_hash in files.items():
        file_path = bundle_dir / name
        if not file_path.exists():
            return {"status": "FAIL", "reason": f"arquivo ausente: {name}", "bundle_path": str(bundle_dir)}
        actual_hash = _sha256_file(file_path)
        if actual_hash != expected_hash:
            return {
                "status": "FAIL",
                "reason": f"hash divergente em {name}",
                "expected": expected_hash,
                "actual": actual_hash,
                "bundle_path": str(bundle_dir),
            }
    return {"status": "PASS", "bundle_path": str(bundle_dir), "bundle_id": manifest.get("bundle_id")}


def _sha256_file(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha256(data).hexdigest()
