from __future__ import annotations

import logging
from typing import Any, Mapping, Optional, Sequence

from .consultation_models import RiskLevel

logger = logging.getLogger(__name__)


def log_consultation_started(request_id: str, question: str, *, origin: str = "api.consultation") -> None:
    logger.info(
        "consultation_started",
        extra={"request_id": request_id, "question_preview": question[:160], "origin": origin},
    )


def log_consultation_succeeded(
    request_id: str,
    risk_level: RiskLevel,
    *,
    duration_ms: float,
    evidence_count: int,
    risk_flags: Sequence[str],
    origin: str = "api.consultation",
) -> None:
    logger.info(
        "consultation_succeeded",
        extra={
            "request_id": request_id,
            "risk_level": risk_level.value if isinstance(risk_level, RiskLevel) else str(risk_level),
            "duration_ms": duration_ms,
            "evidence_count": evidence_count,
            "risk_flags": list(risk_flags),
            "origin": origin,
        },
    )


def log_consultation_failed(
    request_id: str,
    code: str,
    message: str,
    *,
    duration_ms: Optional[float] = None,
    origin: str = "api.consultation",
    extra_fields: Optional[Mapping[str, Any]] = None,
) -> None:
    extras = dict(extra_fields or {})
    extras.pop("message", None)
    exception_type = extras.pop("exception", None) or extras.pop("exception_type", None)
    payload = {
        "request_id": request_id,
        "error_code": code,
        "error_message": message,
        "origin": origin,
    }
    if duration_ms is not None:
        payload["duration_ms"] = duration_ms
    if exception_type:
        payload["exception_type"] = exception_type
    if extras:
        payload.update(extras)
    logger.warning("consultation_failed", extra=payload)


__all__ = [
    "log_consultation_failed",
    "log_consultation_succeeded",
    "log_consultation_started",
]
