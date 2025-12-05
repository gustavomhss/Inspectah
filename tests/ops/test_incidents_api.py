import sys
from pathlib import Path as _Path

ROOT = _Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import importlib.util
import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi import FastAPI  # type: ignore  # noqa: E402
from fastapi.testclient import TestClient  # type: ignore  # noqa: E402

from app.api.ops_incidents_routes import router, service, IncidentState  # noqa: E402


def _load_migration():
    path = ROOT / "migrations/versions/0035_s33_incidents.py"
    spec = importlib.util.spec_from_file_location("s33_incidents", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _setup_app(tmp_path):
    _load_migration().apply_migration(tmp_path / "s33.sqlite")
    service.db_path = tmp_path / "s33.sqlite"  # reuse service with tmp DB
    app = FastAPI()
    app.include_router(router)
    return app


def test_create_and_transition_incident_api(tmp_path):
    app = _setup_app(tmp_path)
    client = TestClient(app)
    payload = {
        "id": "inc_api_1",
        "title": "API incidente",
        "description": "Via API",
        "severity": "HIGH",
        "component_id": "fonte_noticias_principal",
        "slo_ids": ["s33_slo_recencia_fonte_noticias"],
    }
    resp = client.post("/api/ops/incidents", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["state"] == IncidentState.OPEN

    trans = client.post(f"/api/ops/incidents/{payload['id']}/transition", json={"new_state": IncidentState.TRIAGE})
    assert trans.status_code == 200
    assert trans.json()["state"] == IncidentState.TRIAGE

    bad = client.post(f"/api/ops/incidents/{payload['id']}/transition", json={"new_state": IncidentState.CLOSED})
    assert bad.status_code == 400
