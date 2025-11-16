from __future__ import annotations

from .metadata import (  # re-export safe metadata symbols
    ALLOWED_LGPD_TAGS,
    CHECKSUM_OK,
    HASH_ALGORITHM,
    EvidenceFetchResult,
    EvidenceRecord,
    EvidenceVaultError,
)


def store_evidence(*args, **kwargs):
    from .writer import store_evidence as _impl

    return _impl(*args, **kwargs)


def fetch_evidence(*args, **kwargs):
    from .reader import fetch_evidence as _impl

    return _impl(*args, **kwargs)


__all__ = [
    "ALLOWED_LGPD_TAGS",
    "CHECKSUM_OK",
    "HASH_ALGORITHM",
    "EvidenceFetchResult",
    "EvidenceRecord",
    "EvidenceVaultError",
    "fetch_evidence",
    "store_evidence",
]
