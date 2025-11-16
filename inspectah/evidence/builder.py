"""Evidence bundle builder."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_bundle(
    item: Dict[str, Any],
    *,
    raw_content: bytes,
    text_content: str | None = None,
    base_dir: str | Path = "data/evidence",
) -> Dict[str, Any]:
    """Cria bundle write-once com layout fixo."""

    base_path = Path(base_dir)
    fetched_at = item.get("fetched_at") or item.get("meta", {}).get("fetched_at")
    if not fetched_at:
        raise ValueError("fetched_at obrigatório para criar bundle")
    date_token = _extract_date_token(fetched_at)
    bundle_dir = base_path / item["source_id"] / date_token / item["item_id"]
    if bundle_dir.exists():
        raise FileExistsError(f"Bundle já existe: {bundle_dir}")
    bundle_dir.mkdir(parents=True, exist_ok=False)

    files = {}
    raw_path = bundle_dir / "raw.bin"
    raw_path.write_bytes(raw_content)
    files["raw.bin"] = _sha256_bytes(raw_content)

    if text_content:
        text_bytes = text_content.encode("utf-8")
        text_path = bundle_dir / "text.txt"
        text_path.write_bytes(text_bytes)
        files["text.txt"] = _sha256_bytes(text_bytes)

    meta = {
        "source_id": item["source_id"],
        "item_id": item["item_id"],
        "run_id": item.get("run_id"),
        "watcher_type": item.get("watcher_type") or item.get("meta", {}).get("watcher_type"),
        "fetched_at": fetched_at,
        "request_url": item.get("request_url") or item.get("meta", {}).get("request_url"),
    }
    meta_bytes = json.dumps(meta, indent=2).encode("utf-8")
    (bundle_dir / "meta.json").write_bytes(meta_bytes)
    files["meta.json"] = _sha256_bytes(meta_bytes)

    manifest = {
        "bundle_id": f"{item['source_id']}::{item['item_id']}::{date_token}",
        "files": files,
    }
    manifest_bytes = json.dumps(manifest, indent=2).encode("utf-8")
    (bundle_dir / "manifest.json").write_bytes(manifest_bytes)

    return {
        "bundle_id": manifest["bundle_id"],
        "bundle_path": str(bundle_dir),
    }


def _extract_date_token(value: str) -> str:
    parsed = value.replace("Z", "+00:00")
    dt_obj = datetime.fromisoformat(parsed)
    return dt_obj.strftime("%Y-%m-%d")
