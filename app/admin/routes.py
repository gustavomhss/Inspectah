from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict

try:  # pragma: no cover
    from fastapi import APIRouter, HTTPException
except ModuleNotFoundError:  # pragma: no cover
    APIRouter = None  # type: ignore[misc]
    HTTPException = None  # type: ignore[misc]

from . import service
from .schemas import SourceCreateRequest, to_dict


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


# --- FastAPI routes for S18 admin console ---


if APIRouter is not None:  # pragma: no cover
    router = APIRouter(prefix="/admin", tags=["admin"])

    @router.get("/sources")
    def _list_admin_sources() -> Dict[str, Any]:
        sources = service.list_admin_sources()
        return {"sources": [to_dict(src) for src in sources]}

    @router.get("/sources/{source_id}")
    def _get_admin_source(source_id: str) -> Dict[str, Any]:
        src = service.get_admin_source(source_id)
        if not src:
            raise HTTPException(status_code=404, detail="Fonte não encontrada")
        return {"source": to_dict(src)}

    @router.get("/cases")
    def _list_admin_cases() -> Dict[str, Any]:
        cases = service.list_admin_cases()
        return {"cases": [to_dict(c) for c in cases]}

    @router.get("/cases/{case_id}")
    def _get_admin_case(case_id: str) -> Dict[str, Any]:
        case = service.get_admin_case(case_id)
        if not case:
            raise HTTPException(status_code=404, detail="Caso não encontrado")
        return {"case": to_dict(case)}

    @router.get("/cases/{case_id}/timeline")
    def _get_admin_case_timeline(case_id: str) -> Dict[str, Any]:
        timeline = service.list_case_timeline(case_id)
        if not timeline:
            raise HTTPException(status_code=404, detail="Timeline não encontrada")
        return {"timeline": to_dict(timeline)}

    @router.get("/cases/{case_id}/xray")
    def _get_admin_case_xray(case_id: str) -> Dict[str, Any]:
        xray = service.get_case_xray(case_id)
        if not xray:
            raise HTTPException(status_code=404, detail="Raio-X não encontrado")
        return {"xray": to_dict(xray)}

    @router.get("/health")
    def _get_admin_health() -> Dict[str, Any]:
        health = service.get_admin_health()
        return {"health": to_dict(health)}

else:  # pragma: no cover
    router = None
