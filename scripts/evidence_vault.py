#!/usr/bin/env python3
"""Deterministic Evidence Vault helper."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

REQUIRED_FIELDS = [
    "item_id",
    "source_id",
    "canonical_url",
    "event_time",
    "observed_at",
    "indexed_at",
    "timezone",
    "extractor_version",
    "user_agent",
    "allowlist_proof_ref",
    "fields",
]

JSON_SCHEMA_REQUIRED = REQUIRED_FIELDS + [
    "fetched_payload_sha256",
    "extracted_fields_sha256",
    "hashes",
]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def dump_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_json(value: Any) -> str:
    data = json.dumps(value, sort_keys=True).encode("utf-8")
    return sha256_bytes(data)


def validate_manifest(manifest: Dict[str, Any]) -> None:
    missing = [field for field in JSON_SCHEMA_REQUIRED if field not in manifest]
    if missing:
        raise ValueError(f"Manifest missing required fields: {missing}")

    hashes = manifest.get("hashes", {})
    for key in ("payload_sha256", "manifest_sha256"):
        if key not in hashes:
            raise ValueError(f"Manifest hashes missing {key}")


def build_manifest(metadata: Dict[str, Any], payload_path: Path) -> Dict[str, Any]:
    payload_bytes = payload_path.read_bytes()
    payload_sha = sha256_bytes(payload_bytes)
    fields = metadata.get("fields", {})
    manifest: Dict[str, Any] = {key: metadata[key] for key in REQUIRED_FIELDS}
    manifest["fields"] = fields
    manifest["fetched_payload_sha256"] = payload_sha
    manifest["extracted_fields_sha256"] = sha256_json(fields)
    manifest["hashes"] = {"payload_sha256": payload_sha, "manifest_sha256": ""}
    return manifest


def run(payload: Path, metadata: Path, out_dir: Path) -> Path:
    meta = load_json(metadata)
    manifest_dir = out_dir / meta["item_id"]
    manifest_dir.mkdir(parents=True, exist_ok=True)

    payload_bytes = payload.read_bytes()
    payload_out = manifest_dir / "payload.json"
    payload_out.write_bytes(payload_bytes)

    manifest = build_manifest(meta, payload_out)
    manifest["hashes"]["manifest_sha256"] = canonical_manifest_hash(manifest)
    manifest_path = manifest_dir / "manifest.json"
    dump_json(manifest, manifest_path)

    validate_manifest(manifest)

    summary = {
        "item_id": manifest["item_id"],
        "payload_path": str(payload_out),
        "manifest_path": str(manifest_path),
        "hashes": manifest["hashes"],
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }
    dump_json(summary, manifest_dir / "summary.json")
    return manifest_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Evidence Vault artifacts")
    parser.add_argument("--payload", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    manifest_path = run(args.payload, args.metadata, args.out_dir)
    print(f"Manifest written to {manifest_path}")


def canonical_manifest_hash(manifest: Dict[str, Any]) -> str:
    clone = json.loads(json.dumps(manifest))
    clone["hashes"]["manifest_sha256"] = ""
    canonical_bytes = json.dumps(clone, sort_keys=True).encode("utf-8")
    return hashlib.sha256(canonical_bytes).hexdigest()


if __name__ == "__main__":
    main()
