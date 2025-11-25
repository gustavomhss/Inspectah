from __future__ import annotations

from typing import Dict, Optional

from app.sources import service


def read_source_as_form(source_id: str) -> Optional[Dict]:
    source = service.get_source_detail(source_id)
    if not source:
        return None
    data = source.__dict__.copy()
    data["source_id"] = source.id
    return data
