from app.sources import service
from app.sources.models import SourceState
from app.sources.schemas import SourceCreate, SourceUpdate


def _sample_payload() -> SourceCreate:
    return SourceCreate(
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


def test_create_and_change_state():
    payload = _sample_payload()
    src = service.create_source(payload)
    assert src.state == SourceState.PROPOSED
    changed = service.change_source_state(src.id, SourceState.TESTING, "iniciar teste", "tester")
    assert changed is not None
    assert changed.state == SourceState.TESTING


def test_update_and_healthcheck_flow():
    src = service.create_source(_sample_payload())
    updated = service.update_source(
        src.id,
        SourceUpdate(
          slug=src.slug,
          name="Fonte Atualizada",
          description="desc",
          type="news_rss",
          category="official",
          themes=["politica"],
          info_types=["news"],
          protocol="https",
          format="rss",
          endpoint="https://invalid.example/rss",
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
          updated_by="tester",
        ),
    )
    assert updated is not None
    hc = service.register_healthcheck(src.id, status=service.SourceHealthStatus.FAIL, latency_ms=123, error="fail")
    assert hc.source_id == src.id
    history = service.list_healthchecks(src.id)
    assert len(history) == 1
