from __future__ import annotations

from typing import Dict

import pytest
import jwt
from pathlib import Path
import uuid
import time
import httpx

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


@pytest.fixture(autouse=True)
def _auth_header(monkeypatch):
    """
    Injeta Authorization: Bearer <token> em todas as requisições do TestClient/httpx,
    para não quebrar com o middleware JWT fail-closed.
    """

    key_path = Path("config/dev_jwt_private.pem")
    key = key_path.read_text()
    now = int(time.time())
    payload = {
        "iss": "inspectah-idp",
        "aud": "inspectah-api",
        "iat": now,
        "nbf": now,
        "exp": now + 900,
        "sub": "admin-user",
        "role": "admin",
        "op_id": str(uuid.uuid4()),
        "request_id": str(uuid.uuid4()),
    }
    token = jwt.encode(payload, key, algorithm="RS256", headers={"kid": "sf3-dev"})

    original_build_request = httpx.Client.build_request

    def _with_auth(self, method, url, *args, **kwargs):
        headers = kwargs.pop("headers", {}) or {}
        # Só adiciona se não houver Authorization explícito.
        headers.setdefault("Authorization", f"Bearer {token}")
        kwargs["headers"] = headers
        return original_build_request(self, method, url, *args, **kwargs)

    monkeypatch.setattr(httpx.Client, "build_request", _with_auth)
    yield
