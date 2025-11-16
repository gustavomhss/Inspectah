from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class EvidenceStoreConfig:
    backend: str
    bucket: str
    region: str
    kms_key_alias: str
    endpoint_url: Optional[str]
    default_ttl_seconds: int
    local_root: Path


__all__ = ["EvidenceStoreConfig"]
