from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from ..config import EVIDENCE_DIR


@dataclass
class EvidencePaths:
    root: Path
    raw_path: Path
    text_path: Path
    manifest_path: Path
    evidence_sha256: str


def persist_evidence(
    source_id: str,
    item_id: str,
    canonical_url: str,
    raw_content: bytes,
    text_content: str,
    collected_at: datetime,
    content_hash: str,
) -> EvidencePaths:
    collected = collected_at.astimezone(timezone.utc)
    root = (
        EVIDENCE_DIR
        / source_id
        / collected.strftime("%Y")
        / collected.strftime("%m")
        / collected.strftime("%d")
        / item_id
    )
    root.mkdir(parents=True, exist_ok=True)
    raw_path = root / "raw.html"
    text_path = root / "text.txt"
    manifest_path = root / "manifest.json"
    raw_path.write_bytes(raw_content)
    text_path.write_text(text_content, encoding="utf-8")
    bundle_hash = hashlib.sha256()
    bundle_hash.update(raw_content)
    bundle_hash.update(text_content.encode("utf-8"))
    evidence_sha256 = bundle_hash.hexdigest()
    manifest = {
        "item_id": item_id,
        "source_id": source_id,
        "canonical_url": canonical_url,
        "collected_at": collected.isoformat(),
        "content_hash": content_hash,
        "raw_path": raw_path.as_posix(),
        "text_path": text_path.as_posix(),
        "evidence_sha256": evidence_sha256,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return EvidencePaths(
        root=root,
        raw_path=raw_path,
        text_path=text_path,
        manifest_path=manifest_path,
        evidence_sha256=evidence_sha256,
    )
