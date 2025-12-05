import sys
from pathlib import Path as _Path
import importlib.util

ROOT = _Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.api import ops_cockpit_routes  # noqa: E402
from app.api.ops_cockpit_routes import router  # noqa: E402
from app.ops.incidents import Incident, IncidentService  # noqa: E402


def _load_migration():
    path = ROOT / "migrations/versions/0035_s33_incidents.py"
    spec = importlib.util.spec_from_file_location("s33_incidents", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_cockpit_overview_and_components(tmp_path):
    _load_migration().apply_migration(tmp_path / "s33.sqlite")
    svc = IncidentService(db_path=tmp_path / "s33.sqlite")
    svc.create_incident(
        Incident(
            id="inc_cockpit",
            title="Teste cockpit",
            description="",
            severity="LOW",
            component_id="fonte_noticias_principal",
        )
    )
    # apontar router global para o DB temporário
    ops_cockpit_routes.incident_service.db_path = tmp_path / "s33.sqlite"

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    ov = client.get("/api/ops/cockpit/overview")
    assert ov.status_code == 200
    data = ov.json()
    assert data["components"] >= 1

    comps = client.get("/api/ops/cockpit/components")
    assert comps.status_code == 200
    comp_ids = [c["id"] for c in comps.json()]
    assert "fonte_noticias_principal" in comp_ids

    incs = client.get("/api/ops/cockpit/incidents")
    assert incs.status_code == 200
    assert any(i["id"] == "inc_cockpit" for i in incs.json())
