from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from . import storage
from .models import EvidenceBundle, EvidenceItemRef, Item, ParsedQuery

MAX_ITEMS_PER_SOURCE = 10


def build_evidence_bundle(parsed: ParsedQuery, items: List[Item]) -> EvidenceBundle:
    bundle_id = storage.generate_entity_id("eb")
    items_by_source: Dict[str, List[EvidenceItemRef]] = {}
    manifest_paths: Dict[str, str] = {}

    for item in items:
        refs = items_by_source.setdefault(item.source_id, [])
        if len(refs) >= MAX_ITEMS_PER_SOURCE:
            continue
        ref = EvidenceItemRef(
            item_id=item.id,
            source_id=item.source_id,
            key_fields=_extract_key_fields(item),
        )
        refs.append(ref)
        manifest_paths[item.source_id] = str(storage.get_item_path(item.id))

    bundle = EvidenceBundle(
        id=bundle_id,
        query_type=parsed.query_type,
        query_filters=parsed.filters,
        items_by_source=items_by_source,
        manifest_paths=manifest_paths,
        created_at=datetime.utcnow(),
        meta={
            "num_sources": len(items_by_source),
            "num_items": sum(len(refs) for refs in items_by_source.values()),
        },
    )
    storage.save_evidence_bundle(bundle)
    return bundle


def _extract_key_fields(item: Item) -> Dict[str, object]:
    payload = item.payload
    keys: Dict[str, object] = {}
    for field in ("produto", "cidade", "pessoa", "caso", "valor", "valor_medio", "status"):
        if field in payload:
            keys[field] = payload[field]
    keys.setdefault("created_at", item.created_at.isoformat())
    return keys
