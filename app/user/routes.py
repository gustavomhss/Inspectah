from __future__ import annotations

import time
from typing import Any, Dict, Optional

from app.admin import service as admin_service
from app.core import pipeline
from app.observability import metrics_s9

from . import schemas, view_models


class UserQueryError(Exception):
    def __init__(self, message: str, status: str = "erro") -> None:
        super().__init__(message)
        self.status = status


def post_query(payload: Dict[str, Any]) -> Dict[str, Any]:
    request = schemas.UserQueryRequest(
        question=payload.get("question") or payload.get("query") or "",
        scenario_id=payload.get("scenario_id"),
        info_type=payload.get("info_type"),
        filters=payload.get("filters") or {},
    )
    if not request.question.strip():
        metrics_s9.record_error("user", "missing_question")
        return {"status": "erro", "error": "question é obrigatório"}

    info_hint = _resolve_info_type(request)
    scenario_hint = request.scenario_id or _scenario_from_info_type(info_hint) or "unknown"
    start = time.perf_counter()

    try:
        _prepare_sources_if_needed(request)
    except UserQueryError as exc:
        duration = time.perf_counter() - start
        metrics_s9.record_error("user", "prepare_failed")
        metrics_s9.record_user_query(info_hint or "unknown", scenario_hint, "erro", duration)
        return {"status": exc.status, "error": str(exc)}

    try:
        response = pipeline.run_pipeline(request.question)
    except Exception:
        duration = time.perf_counter() - start
        metrics_s9.record_error("core", "pipeline_exception")
        metrics_s9.record_user_query(info_hint or "unknown", scenario_hint, "erro", duration)
        raise

    view = view_models.build_user_response_view(response)
    dto = schemas.UserQueryResponse.from_core_response(
        response=response,
        summary_card=view["summary_card"],
        evidence_links=view["evidence_links"],
        scenario_id=request.scenario_id or view["summary_card"].get("scenario_tag"),
    )
    duration = time.perf_counter() - start
    metrics_s9.record_user_query(response.info_type, view["summary_card"].get("scenario_tag", scenario_hint), response.status, duration)

    return {"response": dto.to_dict(), "view": view}


def _prepare_sources_if_needed(request: schemas.UserQueryRequest) -> None:
    scenario_id: Optional[str] = request.scenario_id
    if scenario_id:
        try:
            admin_service.prepare_scenario_sources(scenario_id)
        except Exception as exc:  # pragma: no cover
            raise UserQueryError(f"Erro ao preparar fontes para {scenario_id}: {exc}")
    elif request.info_type:
        try:
            admin_service.prepare_sources_for_info_type(request.info_type)
        except Exception as exc:
            raise UserQueryError(f"Erro ao preparar fontes para {request.info_type}: {exc}")


def _resolve_info_type(request: schemas.UserQueryRequest) -> Optional[str]:
    if request.info_type:
        return request.info_type
    if request.scenario_id and request.scenario_id in admin_service.SCENARIO_SPECS:
        return admin_service.SCENARIO_SPECS[request.scenario_id]["info_type"]
    return None


def _scenario_from_info_type(info_type: Optional[str]) -> Optional[str]:
    if not info_type:
        return None
    for scenario, spec in admin_service.SCENARIO_SPECS.items():
        if spec["info_type"] == info_type:
            return scenario
    return None
