from __future__ import annotations

from typing import Dict

import pytest

from app.gpt_client.client import GptAnswer


@pytest.fixture(autouse=True)
def _gpt_stub(monkeypatch):
    def _fake_gpt(**kwargs):
        bundle = kwargs["bundle"]
        info_type = kwargs["info_type"]
        scenario_tag = kwargs["scenario_tag"]
        query_spec = kwargs.get("query_spec", {})
        num_sources = bundle.meta.get("num_sources", 0)
        num_items = bundle.meta.get("num_items", 0)
        resolution = "ok"
        if query_spec.get("query_type") == "fora_de_escopo":
            resolution = "fora_de_escopo"
        elif num_sources < 2 or num_items == 0:
            resolution = "dados_insuficientes"
        summary = {
            "resolution": resolution,
            "num_sources": num_sources,
            "num_items": num_items,
            "info_type": info_type,
            "scenario_tag": scenario_tag,
            "query_type": query_spec.get("query_type"),
        }
        if query_spec.get("query_type") == "comparacao_simples":
            summary.update({"best_location": "mock", "best_value": 10.0})
        elif query_spec.get("query_type") == "preco_medio":
            summary.update({"main_value": 10.0, "range": {"min": 10.0, "max": 10.0}})
        else:
            summary.update({"verdict": "indefinido", "confirmations": 0, "negatives": 0, "notes": []})
        return GptAnswer(
            answer_text="Resposta simulada",
            summary_structured=summary,
            confidence_flags={"level": "medium", "reasons": []},
            limitations=["Simulado"],
            prompt_used={},
        )

    monkeypatch.setattr("app.core.pipeline.gpt_run_query", _fake_gpt)
    yield
