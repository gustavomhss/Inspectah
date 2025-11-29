from __future__ import annotations

from typing import Dict

import pytest

from app.user import routes


@pytest.fixture(autouse=True)
def _sandbox(tmp_path, monkeypatch):
    data_dir = tmp_path / "evidence"
    monkeypatch.setenv("INSPECTAH_DATA_DIR", str(data_dir))
    return data_dir


def _assert_happy_response(result: Dict[str, object], scenario: str) -> None:
    response = result["response"]
    assert response["scenario_id"] == scenario
    assert response["status"] == "ok"
    summary = response["summary_card"]
    assert summary["num_sources"] >= 2
    evidence = response["evidence_links"]
    assert evidence["bundle_id"]
    assert evidence["bundle_path"]


def test_user_route_c1_happy_path():
    result = routes.post_query({"question": "Qual o preço médio da cesta básica em São Paulo?", "scenario_id": "C1"})
    assert "error" not in result
    _assert_happy_response(result, "C1")


def test_user_route_c2_happy_path():
    result = routes.post_query({"question": "Onde o GLP 13kg está mais barato no RJ?", "scenario_id": "C2"})
    assert "error" not in result
    _assert_happy_response(result, "C2")


def test_user_route_c3_happy_path():
    question = "O diesel caiu 12% em Belo Horizonte nos últimos 30 dias?"
    result = routes.post_query({"question": question, "scenario_id": "C3"})
    assert "error" not in result
    response = result["response"]
    assert response["scenario_id"] == "C3"
    assert response["info_type"] == "C3_checagem_factual"
    summary = response["summary_card"]
    assert summary["num_sources"] >= 2
