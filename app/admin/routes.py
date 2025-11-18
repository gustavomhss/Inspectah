from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict

from . import service
from .schemas import SourceCreateRequest


def list_sources() -> Dict[str, Any]:
    entries = service.list_sources()
    return {"sources": [asdict(entry) for entry in entries]}


def create_source(payload: Dict[str, Any]) -> Dict[str, Any]:
    request = SourceCreateRequest(**payload)
    source = service.create_or_update_source(request)
    status = service.get_source_status(source.id)
    return {
        "source": {
            "id": source.id,
            "name": source.name,
            "type": source.type,
            "info_type": source.config.params.get("info_type"),
            "url_base": source.config.url_base,
            "selected_fields": source.config.selected_fields,
            "params": source.config.params,
        },
        "status": asdict(status) if status else None,
    }


def test_source(source_id: str) -> Dict[str, Any]:
    return asdict(service.trigger_source_test(source_id))


def get_source_status(source_id: str) -> Dict[str, Any]:
    status = service.get_source_status(source_id)
    return asdict(status) if status else {"source_id": source_id, "error": "Fonte não encontrada"}
