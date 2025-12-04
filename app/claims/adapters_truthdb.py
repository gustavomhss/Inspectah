"""
Helpers to map claims (Programa 2) into Truth-DB building blocks for S32.
This is intentionally minimal for the sprint: claims are represented as simple dicts.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Dict, List


SUPPORTED_CLAIM_TYPE = "news_fact_simple"


@dataclass
class AdaptedClaim:
    claim_id: str
    claim_type: str
    content_hash: str
    evidences: List[Dict[str, Any]]


def extract_fact_from_claim(claim: Dict[str, Any]) -> AdaptedClaim:
    claim_id = claim.get("id")
    claim_type = claim.get("type")
    if not claim_id or not claim_type:
        raise ValueError("claim missing id or type")
    if claim_type != SUPPORTED_CLAIM_TYPE:
        raise ValueError(f"unsupported claim type {claim_type}")
    content = claim.get("content", "")
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    evidences = claim.get("evidences", [])
    return AdaptedClaim(
        claim_id=claim_id,
        claim_type=claim_type,
        content_hash=content_hash,
        evidences=evidences,
    )
