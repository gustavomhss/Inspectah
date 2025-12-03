from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from . import service
from .schemas import SourceCreateRequest

# Dashboard/admin overview endpoints

dashboard_router = APIRouter(prefix="/admin", tags=["admin-dashboard"])

# Casos demo para atender endpoints de painel admin
DEMO_CASES = {
    "obra_publica:2025-123": {
        "id": "obra_publica:2025-123",
        "title": "Obra pública com indícios de superfaturamento",
        "category": "obra_publica",
        "status": "andamento",
        "risk": "medio",
        "updated_at": "",
        "key_sources": [],
        "description": "Caso demo para painel admin.",
        "top_evidence": [],
    },
    "evento_climatico:inmet-2025-0901": {
        "id": "evento_climatico:inmet-2025-0901",
        "title": "Evento climático extremo",
        "category": "evento_climatico",
        "status": "monitoramento",
        "risk": "alto",
        "updated_at": "",
        "key_sources": [],
        "description": "Caso demo para painel admin.",
        "top_evidence": [],
    },
}

DEMO_TIMELINES = {
    "obra_publica:2025-123": {
        "case_id": "obra_publica:2025-123",
        "events": [
            {
                "id": "ev-1",
                "event_type": "ingestion",
                "summary": "Ingestão inicial",
                "timestamp": "2025-01-02T10:00:00Z",
            },
            {
                "id": "ev-2",
                "event_type": "truth_event",
                "summary": "Primeiro evento de verdade",
                "timestamp": "2025-01-03T12:00:00Z",
            },
        ],
    }
}

DEMO_XRAYS = {
    "evento_climatico:inmet-2025-0901": {
        "case_id": "evento_climatico:inmet-2025-0901",
        "title": "Evento climático extremo",
        "category": "evento_climatico",
        "status": "monitoramento",
        "risk": "alto",
        "summary": "Raio-X consolidado do caso demo.",
        "debunker": {
            "risk_level": "moderate",
            "explanation": "Debunker identificou riscos e emitiu parecer inicial.",
            "flags": ["analisar fontes adicionais"],
            "last_evaluated_at": "2025-01-03T15:00:00Z",
        },
        "committees": [
            {"name": "core_committee", "verdict": "convergent", "score": 0.92},
        ],
        "anchors": [
            {"id": "anchor-1", "kind": "onchain", "status": "confirmed"},
        ],
        "evidences": {
            "summary": "Principais evidências coletadas.",
            "evidences": [
                {"id": "evidence-1", "type": "document", "relevance": "high"},
            ],
        },
    }
}


@dashboard_router.get("/health")
def get_health() -> Dict[str, Any]:
    """Retorna saúde básica para a UI de admin."""
    sources = service.list_sources()
    sources_total = len(sources)
    return {
        "health": {
            "sources_total": sources_total,
            "sources_healthy": sources_total,
            "sources_degraded": 0,
            "cases_total": 0,
            "cases_attention": 0,
            "cases_stable": 0,
            "integrations": {},
        }
    }


@dashboard_router.get("/cases")
def list_cases() -> Dict[str, Any]:
    """Lista casos/temas para o painel."""
    return {"cases": list(DEMO_CASES.values())}


@dashboard_router.get("/cases/{case_id}")
def get_case(case_id: str) -> Dict[str, Any]:
    case = DEMO_CASES.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="case not found")
    return {"case": case}


@dashboard_router.get("/cases/{case_id}/timeline")
def get_case_timeline(case_id: str) -> Dict[str, Any]:
    timeline = DEMO_TIMELINES.get(case_id)
    if not timeline:
        raise HTTPException(status_code=404, detail="case not found")
    return {"timeline": timeline}


@dashboard_router.get("/cases/{case_id}/xray")
def get_case_xray(case_id: str) -> Dict[str, Any]:
    xray = DEMO_XRAYS.get(case_id)
    if not xray:
        raise HTTPException(status_code=404, detail="case not found")
    return {"xray": xray}


# Admin de fontes (compatibilidade com UI atual)
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
