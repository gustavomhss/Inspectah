from app.sources import service
from app.sources.models import SourceState
from app.sources.schemas import SourceCreate, SourceUpdate


def test_create_and_change_state(tmp_path, monkeypatch):
    # usar diretório temporário para não poluir evidências
    monkeypatch.setattr(service, "DATA_DIR", tmp_path)
    monkeypatch.setattr(service, "SOURCES_PATH", tmp_path / "sources.json")
    monkeypatch.setattr(service, "HEALTH_PATH", tmp_path / "health.json")
    monkeypatch.setattr(service, "STATE_PATH", tmp_path / "state.json")

    payload = SourceCreate(
        slug="src-test",
        name="Fonte Teste",
        description="",
        type="news_rss",
        category="official",
        themes=["politica"],
        info_types=["news"],
        protocol="https",
        format="rss",
        endpoint="https://example.com/rss",
        auth_type="none",
        auth_config={},
        request_params={},
        headers={},
        frequency="daily",
        timeout_ms=5000,
        retry_policy={},
        parsing_config={},
        redundancy_group=None,
        redundancy_role=None,
        meta={},
        created_by="tester",
    )
    src = service.create_source(payload)
    assert src.state == SourceState.PROPOSED
    changed = service.change_source_state(src.id, SourceState.TESTING, "iniciar teste", "tester")
    assert changed is not None
    assert changed.state == SourceState.TESTING
