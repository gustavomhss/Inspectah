from __future__ import annotations
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from ..config import EVIDENCE_VAULT_SETTINGS
from .settings import EvidenceStoreConfig

logger = logging.getLogger(__name__)


class EvidenceStoreError(RuntimeError):
    """Raised when an evidence store operation cannot be completed."""


@dataclass(frozen=True)
class EvidenceObjectHandle:
    bucket: str
    key: str
    region: str
    size_bytes: int
    kms_key_alias: str


class EvidenceStoreClient:
    def __init__(self, config: EvidenceStoreConfig):
        self._config = config
        self._validate_config()

    @property
    def config(self) -> EvidenceStoreConfig:
        return self._config

    def put_object(self, key: str, data: bytes, *, metadata: Optional[Dict[str, str]] = None) -> EvidenceObjectHandle:
        raise NotImplementedError

    def get_object(self, key: str) -> bytes:
        raise NotImplementedError

    def _validate_config(self) -> None:
        if self._config.region != "sa-east-1":
            raise EvidenceStoreError("Evidence Vault must use region sa-east-1 (per D9.4).")
        if not self._config.kms_key_alias:
            raise EvidenceStoreError("Evidence Vault requires a kms_key_alias.")


class LocalEvidenceStoreClient(EvidenceStoreClient):
    """
    Local stub that emulates an S3-compatible bucket by writing objects to disk.
    Used in development and sandbox environments where network access is restricted.
    """

    def __init__(self, config: EvidenceStoreConfig):
        super().__init__(config)
        self._root = config.local_root
        self._root.mkdir(parents=True, exist_ok=True)

    def put_object(self, key: str, data: bytes, *, metadata: Optional[Dict[str, str]] = None) -> EvidenceObjectHandle:
        safe_path = self._resolve_key(key)
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        safe_path.write_bytes(data)
        logger.info(
            "Stored evidence object key=%s bucket=%s size=%d",
            key,
            self.config.bucket,
            len(data),
        )
        return EvidenceObjectHandle(
            bucket=self.config.bucket,
            key=key,
            region=self.config.region,
            size_bytes=len(data),
            kms_key_alias=self.config.kms_key_alias,
        )

    def get_object(self, key: str) -> bytes:
        safe_path = self._resolve_key(key)
        if not safe_path.exists():
            raise EvidenceStoreError(f"Evidence object {key} not found.")
        logger.info("Fetched evidence object key=%s bucket=%s", key, self.config.bucket)
        return safe_path.read_bytes()

    def _resolve_key(self, key: str) -> Path:
        if not key or key.startswith("/"):
            raise EvidenceStoreError("Evidence key must be a relative path.")
        candidate = (self._root / key).resolve()
        try:
            candidate.relative_to(self._root)
        except ValueError as exc:  # path traversal attempt
            raise EvidenceStoreError("Evidence key escapes storage root.") from exc
        return candidate


def get_evidence_store_client(config: Optional[EvidenceStoreConfig] = None) -> EvidenceStoreClient:
    cfg = config or EVIDENCE_VAULT_SETTINGS
    backend = cfg.backend.lower()
    if backend == "local_stub":
        return LocalEvidenceStoreClient(cfg)
    raise EvidenceStoreError(f"Unsupported evidence store backend: {cfg.backend}")


__all__ = [
    "EvidenceStoreClient",
    "EvidenceStoreConfig",
    "EvidenceStoreError",
    "EvidenceObjectHandle",
    "LocalEvidenceStoreClient",
    "get_evidence_store_client",
]
