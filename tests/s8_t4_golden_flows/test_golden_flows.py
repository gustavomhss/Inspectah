from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest

SCENARIOS = [
    ("s8_preco_medio", "Qual o preço médio do arroz em São Paulo?"),
    ("s8_comparacao_simples", "Onde o arroz está mais barato em São Paulo?"),
    ("s8_checagem_factual", "João Mendes foi condenado na Operação Horizonte?"),
]


@pytest.fixture(autouse=True)
def _sandbox(tmp_path_factory, monkeypatch):
    data_dir = tmp_path_factory.mktemp("evidence")
    monkeypatch.setenv("INSPECTAH_DATA_DIR", str(data_dir))
    admin_service = importlib.import_module("app.admin.service")
    admin_service.ensure_default_sources()
    return data_dir


def _normalize(dto):
    evidence = dto.get("evidence", {})
    return {
        "answer_text": dto.get("answer_text"),
        "summary": dto.get("summary"),
        "confidence": dto.get("confidence"),
        "limitations": dto.get("limitations", []),
        "evidence": {
            "sources": evidence.get("sources", []),
            "items_preview": evidence.get("items_preview", []),
        },
    }


@pytest.mark.parametrize("name,query", SCENARIOS)
def test_golden_flow(name: str, query: str):
    user_routes = importlib.import_module("app.user.routes")
    payload = user_routes.post_query({"query": query})
    dto = payload["dto"]
    normalized = _normalize(dto)

    golden_path = Path("tests/goldens") / f"{name}.json"
    assert golden_path.exists(), f"Golden missing for {name}"
    expected = json.loads(golden_path.read_text(encoding="utf-8"))
    assert normalized == expected
