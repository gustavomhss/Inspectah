from pathlib import Path
import uuid
import sys
import importlib.util
from pathlib import Path as _Path

ROOT = _Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.ops.incidents import (  # noqa: E402
    Incident,
    IncidentService,
    IncidentSeverity,
    IncidentState,
    ALLOWED_TRANSITIONS,
)


def _load_migration():
    path = ROOT / "migrations/versions/0035_s33_incidents.py"
    spec = importlib.util.spec_from_file_location("s33_incidents", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _iid() -> str:
    return f"inc_{uuid.uuid4().hex[:8]}"


def test_create_incident_and_fetch(tmp_path: Path):
    db = tmp_path / "s33.sqlite"
    _load_migration().apply_migration(db)
    svc = IncidentService(db_path=db)
    inc = Incident(
        id=_iid(),
        title="Teste incidente",
        description="Fluxo básico",
        severity=IncidentSeverity.HIGH,
        component_id="fonte_noticias_principal",
        slo_ids=["s33_slo_recencia_fonte_noticias"],
    )
    svc.create_incident(inc)
    fetched = svc.get(inc.id)
    assert fetched is not None
    assert fetched.state == IncidentState.OPEN
    assert fetched.component_id == "fonte_noticias_principal"
    assert fetched.slo_ids == ["s33_slo_recencia_fonte_noticias"]


def test_invalid_severity_fails(tmp_path: Path):
    db = tmp_path / "s33.sqlite"
    _load_migration().apply_migration(db)
    svc = IncidentService(db_path=db)
    inc = Incident(
        id=_iid(),
        title="bad",
        description="bad",
        severity="INVALID",
    )
    try:
        svc.create_incident(inc)
    except ValueError:
        return
    raise AssertionError("esperava erro de severidade inválida")


def test_state_transitions_enforced(tmp_path: Path):
    db = tmp_path / "s33.sqlite"
    _load_migration().apply_migration(db)
    svc = IncidentService(db_path=db)
    inc = Incident(
        id=_iid(),
        title="Transições",
        description="",
        severity=IncidentSeverity.MEDIUM,
    )
    svc.create_incident(inc)
    # Valid transition OPEN -> TRIAGE
    inc = svc.transition(inc.id, IncidentState.TRIAGE)
    assert inc.state == IncidentState.TRIAGE
    # Invalid transition TRIAGE -> CLOSED (não permitido)
    try:
        svc.transition(inc.id, IncidentState.CLOSED)
    except ValueError:
        pass
    else:
        raise AssertionError("transição inválida permitida")
    # Valid TRIAGE -> RESOLVED -> CLOSED
    inc = svc.transition(inc.id, IncidentState.RESOLVED)
    assert inc.resolved_at is not None
    inc = svc.transition(inc.id, IncidentState.CLOSED)
    assert inc.closed_at is not None
    assert inc.state == IncidentState.CLOSED


def test_timestamps_monotonic(tmp_path: Path):
    db = tmp_path / "s33.sqlite"
    _load_migration().apply_migration(db)
    svc = IncidentService(db_path=db)
    inc = Incident(
        id=_iid(),
        title="Tempos",
        description="",
        severity=IncidentSeverity.LOW,
    )
    svc.create_incident(inc)
    inc = svc.transition(inc.id, IncidentState.TRIAGE)
    inc = svc.transition(inc.id, IncidentState.RESOLVED)
    inc = svc.transition(inc.id, IncidentState.CLOSED)
    assert inc.created_at <= inc.updated_at
    if inc.resolved_at:
        assert inc.updated_at <= inc.closed_at
