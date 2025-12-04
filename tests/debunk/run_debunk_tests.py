"""
Fallback runner for debunk tests when pytest is unavailable.
Executes the key tests from tests/debunk/test_debunk_service.py manually.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.debunk import test_debunk_service as tds  # noqa: E402


def _run():
    # Each test gets its own temp dir to mimic pytest's tmp_path fixture.
    tds.test_open_issue_prevents_duplicates(Path(tempfile.mkdtemp()))
    tds.test_queue_orders_by_risk_and_age(Path(tempfile.mkdtemp()))
    tds.test_tasks_drive_issue_to_ready_for_decision(Path(tempfile.mkdtemp()))
    tds.test_decision_requires_valid_state_and_updates_issue(Path(tempfile.mkdtemp()))
    tds.test_api_router_exposes_core_flows(Path(tempfile.mkdtemp()))


if __name__ == "__main__":
    _run()
