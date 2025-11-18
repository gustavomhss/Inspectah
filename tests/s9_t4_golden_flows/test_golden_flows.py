from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pytest

from app.admin import service as admin_service
from app.observability import metrics_s9
from app.user import routes as user_routes

GOLDEN_CASES = [
    ("C1", Path("tests/goldens/s9_preco_medio.json")),
    ("C2", Path("tests/goldens/s9_comparacao_simples.json")),
    ("C3", Path("tests/goldens/s9_checagem_factual.json")),
]


@pytest.fixture(autouse=True)
def _sandbox_storage(tmp_path, monkeypatch):
    monkeypatch.setenv("INSPECTAH_DATA_DIR", str(tmp_path))
    return tmp_path


@pytest.mark.parametrize("scenario_id,golden_path", GOLDEN_CASES)
def test_golden_flows_match_expected(scenario_id: str, golden_path: Path) -> None:
    golden = json.loads(golden_path.read_text(encoding="utf-8"))
    metrics_s9.reset()
    admin_service.prepare_scenario_sources(scenario_id)
    payload = {"question": golden["query"], "scenario_id": scenario_id}
    response = user_routes.post_query(payload)["response"]

    assert response["status"] == golden["status"]
    assert response["answer_text"] == golden["answer_text"]
    _assert_summary(response["summary_card"], golden["summary_card"])
    assert response["confidence"]["level"] == golden["confidence"]["level"]
    assert response["limitations"] == golden["limitations"]


def _assert_summary(actual: Dict[str, Any], expected: Dict[str, Any]) -> None:
    for key, expected_value in expected.items():
        assert key in actual, f"{key} ausente no summary"
        actual_value = actual[key]
        if isinstance(expected_value, float):
            assert actual_value == pytest.approx(expected_value, rel=1e-3)
        elif isinstance(expected_value, dict):
            assert isinstance(actual_value, dict)
            _assert_summary(actual_value, expected_value)
        else:
            assert actual_value == expected_value
