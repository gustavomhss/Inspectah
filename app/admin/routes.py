from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from . import service
from .schemas import SourceCreateRequest


router = APIRouter(prefix="/admin/sources", tags=["admin-sources"])


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
            "info_type": getattr(source, "info_type", source.config.params.get("info_type")),
            "url_base": source.config.url_base,
            "selected_fields": source.config.selected_fields,
            "params": source.config.params,
            "is_active": getattr(source, "is_active", True),
        },
        "status": asdict(status) if status else None,
    }


def test_source(source_id: str) -> Dict[str, Any]:
    result = service.trigger_source_test(source_id)
    return asdict(result)


def get_source_status(source_id: str) -> Dict[str, Any]:
    status = service.get_source_status(source_id)
    return asdict(status) if status else {"source_id": source_id, "error": "Fonte não encontrada"}


def set_source_active(source_id: str, active: bool) -> Dict[str, Any]:
    source = service.set_source_active(source_id, active)
    if not source:
        return {"source_id": source_id, "error": "Fonte não encontrada"}
    return {"source_id": source_id, "is_active": getattr(source, "is_active", True)}


def prepare_scenario(payload: Dict[str, Any]) -> Dict[str, Any]:
    scenario_id = payload.get("scenario_id")
    if not scenario_id:
        return {"error": "scenario_id é obrigatório"}
    prepared: List[str] = service.prepare_scenario_sources(scenario_id)
    return {"scenario_id": scenario_id, "sources_prepared": prepared}


@router.get("")
def list_sources_endpoint():
    return list_sources()


@router.post("")
def create_source_endpoint(payload: Dict[str, Any]):
    return create_source(payload)


@router.post("/{source_id}/test")
def test_source_endpoint(source_id: str):
    return test_source(source_id)


@router.get("/{source_id}/status")
def get_source_status_endpoint(source_id: str):
    return get_source_status(source_id)


@router.post("/{source_id}/active")
def set_source_active_endpoint(source_id: str, active: bool):
    return set_source_active(source_id, active)


@router.post("/prepare-scenario")
def prepare_scenario_endpoint(payload: Dict[str, Any]):
    result = prepare_scenario(payload)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
