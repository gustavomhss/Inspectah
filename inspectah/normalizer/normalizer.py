"""Normalizador que suporta stub e GPT-4.1 mini."""
from __future__ import annotations

import logging
from typing import Callable, Dict, List, Optional

from inspectah.models import Claim, InspectahItem
from inspectah.normalizer.client_ai import generate_claims

LOGGER = logging.getLogger("inspectah.normalizer")


def normalize_item(
    item: InspectahItem,
    *,
    text: str,
    meta: Optional[Dict[str, object]] = None,
    mode: str = "stub",
    client: Optional[Callable[[str, Dict[str, object]], List[Dict[str, object]]]] = None,
) -> InspectahItem:
    """Executa normalização usando stub ou IA real."""

    meta = meta or {}
    meta.setdefault("item_id", item.item_id)
    meta.setdefault("facts", {})

    if client is not None:
        active_client = client
    else:
        active_client = lambda text_value, meta_value: generate_claims(text_value, meta_value, mode=mode)  # noqa: E731

    try:
        claims_data = active_client(text, meta)
    except Exception as exc:  # pylint: disable=broad-except
        LOGGER.error(
            "normalizer_client_error",
            extra={"source_id": item.source_id, "item_id": item.item_id, "mode": mode, "error": str(exc)},
        )
        return item

    valid_claims: List[Claim] = []
    for idx, claim_payload in enumerate(claims_data, start=1):
        try:
            claim_payload.setdefault("claim_id", f"{item.item_id}_claim_{idx}")
            claim = Claim.from_dict(claim_payload)
            valid_claims.append(claim)
        except Exception as exc:  # pylint: disable=broad-except
            LOGGER.error(
                "normalizer_claim_invalid",
                extra={
                    "source_id": item.source_id,
                    "item_id": item.item_id,
                    "mode": mode,
                    "error": str(exc),
                    "payload": claim_payload,
                },
            )
            return item

    if not valid_claims:
        return item

    item.claims = valid_claims
    item.state = "S3"
    if not item.reasoning_short:
        item.reasoning_short = (
            "Claims gerados via GPT-4.1 mini" if mode == "gpt4mini" else "Stub IA determinística aplicada"
        )
    return item
