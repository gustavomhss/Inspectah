from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.admin import service
from app.user import routes


@pytest.fixture(autouse=True)
def _sandbox_storage(tmp_path, monkeypatch):
    data_dir = tmp_path / "evidence"
    monkeypatch.setenv("INSPECTAH_DATA_DIR", str(data_dir))
    return data_dir


def test_prepare_scenario_fails_with_unknown_id():
    with pytest.raises(ValueError):
        service.prepare_scenario_sources("UNKNOWN")


def test_prepare_scenario_detects_missing_fixtures(monkeypatch):
    spec = service.SCENARIO_SPECS["C2"]
    monkeypatch.setitem(service.SCENARIO_SPECS["C2"], "min_sources", 10)
    with pytest.raises(RuntimeError):
        service.prepare_scenario_sources("C2")
    monkeypatch.setitem(service.SCENARIO_SPECS["C2"], "min_sources", spec["min_sources"])


def test_trigger_source_test_handles_missing_source():
    result = service.trigger_source_test("inexistente")
    assert result.status == "erro"
    assert result.items_ingested == 0


def test_user_route_invalid_scenario_returns_error():
    result = routes.post_query({"question": "Qual o preço médio da cesta básica?", "scenario_id": "C99"})
    assert result["status"] == "erro"
    assert "Erro ao preparar fontes" in result["error"]


def test_user_route_missing_question():
    result = routes.post_query({})
    assert result["status"] == "erro"
    assert "question é obrigatório" in result["error"]


def test_user_route_out_of_scope_response():
    result = routes.post_query({"question": "Quem vai ganhar a eleição ano que vem?"})
    assert "response" in result
    assert result["response"]["status"] == "fora_de_escopo"


def test_user_route_surfaces_admin_error(monkeypatch):
    spec = service.SCENARIO_SPECS["C1"]
    monkeypatch.setitem(service.SCENARIO_SPECS["C1"], "min_sources", spec["min_sources"] + 5)
    result = routes.post_query({"question": "Qual o preço médio da cesta básica?", "scenario_id": "C1"})
    assert result["status"] == "erro"
    assert "Erro ao preparar fontes" in result["error"]
    monkeypatch.setitem(service.SCENARIO_SPECS["C1"], "min_sources", spec["min_sources"])


def test_user_route_reports_dados_insuficientes(monkeypatch, tmp_path):
    fixture_dir = tmp_path / "c1_single"
    fixture_dir.mkdir()
    payload = {
        "source": {
            "id": "single_src",
            "name": "Fonte única",
            "type": "precos_api_simples",
            "info_type": "C1_preco_medio",
            "url_base": "fixture://single",
            "selected_fields": ["produto", "cidade", "valor"],
        },
        "items": [
            {"id": "single_item", "produto": "cesta_basica_sp", "cidade": "sao paulo", "valor": 120.0, "info_type": "preco"}
        ],
    }
    (fixture_dir / "single_src.json").write_text(json.dumps(payload), encoding="utf-8")

    original = service.SCENARIO_SPECS["C1"].copy()
    monkeypatch.setitem(service.SCENARIO_SPECS, "C1", {**original, "fixture_dir": fixture_dir, "min_sources": 1})
    result = routes.post_query({"question": "Qual o preço médio da cesta básica em São Paulo?", "scenario_id": "C1"})
    assert "response" in result
    assert result["response"]["status"] == "dados_insuficientes"
    assert result["response"]["summary_card"]["num_sources"] == 1
    monkeypatch.setitem(service.SCENARIO_SPECS, "C1", original)
import json
from pathlib import Path
