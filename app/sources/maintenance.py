from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple

from app.ingestion.models import IngestionMode
from app.ingestion.services import toggle_ingestion_mode
from app.sources import service
from app.sources.models import Source, SourceState
from app.sources.normalizer import is_lab_endpoint, normalize_source_model


def _state_priority(state: SourceState) -> int:
    order = {
        SourceState.ACTIVE: 0,
        SourceState.TESTING: 1,
        SourceState.UNDER_REVIEW: 2,
        SourceState.SUSPECT: 3,
        SourceState.PROPOSED: 4,
        SourceState.DISABLED_TEMP: 5,
        SourceState.DISABLED_PERM: 6,
    }
    return order.get(state, 99)


def normalize_all_sources(changed_by: str = "normalizer") -> Dict[str, int]:
    sources = service.list_sources()
    updated = 0
    lab_ingestion_adjusted = 0
    with service.get_connection() as conn:
        for src in sources:
            normalized = normalize_source_model(src)
            if normalized != src:
                if normalized.state != src.state:
                    normalized.state_updated_at = datetime.utcnow()
                    normalized.updated_at = datetime.utcnow()
                    normalized.updated_by = changed_by
                service._update_source_record(conn, normalized)
                updated += 1
        conn.commit()

    for src in service.list_sources():
        if is_lab_endpoint(src.endpoint):
            try:
                toggle_ingestion_mode(
                    src.id,
                    new_mode=IngestionMode.MANUAL_ONLY,
                    enabled=False,
                    updated_by=changed_by,
                    source_fetcher=lambda sid: src if sid == src.id else service.get_source_detail(sid),
                )
                lab_ingestion_adjusted += 1
            except Exception:
                continue

    return {"normalized": updated, "lab_ingestion_adjusted": lab_ingestion_adjusted}


def deduplicate_sources(changed_by: str = "normalizer") -> Dict[str, int]:
    sources = service.list_sources()
    groups: Dict[Tuple[str, str, str], List[Source]] = defaultdict(list)
    for src in sources:
        key = (src.endpoint, src.type, src.category)
        groups[key].append(src)

    deduplicated = 0
    with service.get_connection() as conn:
        for key, entries in groups.items():
            if len(entries) <= 1:
                continue
            canonical = sorted(
                entries, key=lambda s: (_state_priority(s.state), s.created_at)
            )[0]
            for src in entries:
                if src.id == canonical.id:
                    continue
                src.meta = {**(src.meta or {}), "duplicated_into": canonical.slug}
                reason = f"Duplicada da fonte '{canonical.slug}'"
                if src.state != SourceState.DISABLED_PERM:
                    service._apply_state_transition(conn, src, SourceState.DISABLED_PERM, reason, changed_by)
                else:
                    src.state_reason = src.state_reason or reason
                    service._update_source_record(conn, src)
                deduplicated += 1
        conn.commit()
    return {"deduplicated": deduplicated}


__all__ = ["normalize_all_sources", "deduplicate_sources"]
