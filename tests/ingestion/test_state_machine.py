from datetime import datetime

import pytest

from app.ingestion.models import IngestionRun, IngestionStatus, IngestionTrigger
from app.ingestion.state_machine import IngestionEvent, apply_event, transition


def test_valid_transitions_sequence():
    assert transition(IngestionStatus.PENDING, IngestionEvent.START) == IngestionStatus.RUNNING
    assert transition(IngestionStatus.RUNNING, IngestionEvent.COMPLETE) == IngestionStatus.SUCCESS
    assert transition(IngestionStatus.RUNNING, IngestionEvent.TIMEOUT) == IngestionStatus.FAIL


def test_invalid_transition_raises():
    with pytest.raises(Exception):
        transition(IngestionStatus.PENDING, IngestionEvent.COMPLETE)


def test_apply_event_mutates_run():
    run = IngestionRun(
        id="run_fsm",
        config_id="cfg",
        source_id="src",
        trigger=IngestionTrigger.MANUAL,
        status=IngestionStatus.PENDING,
        started_at=datetime.utcnow(),
        finished_at=None,
        items_processed=0,
        error_code=None,
        error_message=None,
        payload_ref=None,
    )
    apply_event(run, IngestionEvent.START)
    assert run.status == IngestionStatus.RUNNING
    apply_event(run, IngestionEvent.COMPLETE)
    assert run.status == IngestionStatus.SUCCESS


def test_reprocess_from_final_state_goes_to_pending():
    status = transition(IngestionStatus.FAIL, IngestionEvent.REPROCESS)
    assert status == IngestionStatus.PENDING
