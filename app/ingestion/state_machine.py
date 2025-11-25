from __future__ import annotations

from enum import Enum

from app.ingestion.errors import InvalidTransitionError
from app.ingestion.models import IngestionRun, IngestionStatus


class IngestionEvent(str, Enum):
    START = "START"
    COMPLETE = "COMPLETE"
    PARTIAL_COMPLETE = "PARTIAL_COMPLETE"
    ERROR = "ERROR"
    TIMEOUT = "TIMEOUT"
    REPROCESS = "REPROCESS"


FINAL_STATES = {
    IngestionStatus.SUCCESS,
    IngestionStatus.PARTIAL_SUCCESS,
    IngestionStatus.FAIL,
}

VALID_TRANSITIONS = {
    (IngestionStatus.PENDING, IngestionEvent.START): IngestionStatus.RUNNING,
    (IngestionStatus.RUNNING, IngestionEvent.COMPLETE): IngestionStatus.SUCCESS,
    (IngestionStatus.RUNNING, IngestionEvent.PARTIAL_COMPLETE): IngestionStatus.PARTIAL_SUCCESS,
    (IngestionStatus.RUNNING, IngestionEvent.ERROR): IngestionStatus.FAIL,
    (IngestionStatus.RUNNING, IngestionEvent.TIMEOUT): IngestionStatus.FAIL,
}


def transition(status: IngestionStatus, event: IngestionEvent) -> IngestionStatus:
    # idempotência para estados finais
    if status in FINAL_STATES and event in {IngestionEvent.COMPLETE, IngestionEvent.PARTIAL_COMPLETE, IngestionEvent.ERROR, IngestionEvent.TIMEOUT}:
        return status
    if (status, event) in VALID_TRANSITIONS:
        return VALID_TRANSITIONS[(status, event)]
    if status in FINAL_STATES and event == IngestionEvent.REPROCESS:
        return IngestionStatus.PENDING
    raise InvalidTransitionError(f"Transição ilegal: {status} + {event}")


def apply_event(run: IngestionRun, event: IngestionEvent) -> IngestionRun:
    new_status = transition(run.status, event)
    run.status = new_status
    return run
