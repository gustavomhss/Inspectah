from __future__ import annotations

from http import HTTPStatus

try:  # pragma: no cover
    from fastapi import APIRouter, HTTPException
    from fastapi.responses import JSONResponse
except ModuleNotFoundError:  # pragma: no cover
    APIRouter = None  # type: ignore[misc]
    HTTPException = None  # type: ignore[misc]
    JSONResponse = None  # type: ignore[misc]

from .consultation_models import (
    ConsultationErrorResponse,
    ConsultationRequest,
    ConsultationResponse,
    ConsultationResult,
    ConsultationInternalError,
)
from .consultation_service import ConsultationService


router = APIRouter(prefix="/consultation", tags=["consultation"]) if APIRouter is not None else None
_SERVICE = ConsultationService()


def _to_error(status_code: HTTPStatus, exc: ConsultationInternalError) -> JSONResponse | HTTPException:
    payload = ConsultationErrorResponse(code=exc.code, message=exc.message).dict()
    payload["error"] = payload["message"]
    if JSONResponse is None:  # pragma: no cover
        if HTTPException is None:
            raise exc
        return HTTPException(status_code=status_code.value, detail=payload)
    return JSONResponse(status_code=status_code.value, content=payload)


if router is not None:
    @router.post("", response_model=ConsultationResponse, responses={500: {"model": ConsultationErrorResponse}})
    def post_consultation(body: ConsultationRequest) -> ConsultationResponse:
        try:
            result: ConsultationResult = _SERVICE.run_consultation(body)
        except ConsultationInternalError as exc:
            status = HTTPStatus.BAD_REQUEST if exc.code in {"unknown_domain", "validation_error"} else HTTPStatus.INTERNAL_SERVER_ERROR
            error_payload = _to_error(status, exc)
            if isinstance(error_payload, HTTPException):
                raise error_payload
            return error_payload  # type: ignore[return-value]
        return result.to_response()


__all__ = ["router"]
