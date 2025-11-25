import pytest

from app.sources.models import Source, SourceState
from app.sources.service import change_source_state, create_source
from app.sources.schemas import SourceCreate


def test_source_creation_defaults():
    src = Source.create(
        id="src_test",
        slug="src-test",
        name="Fonte Teste",
        description="",
        type="news_rss",
        category="official",
        themes=["politica"],
        info_types=["news"],
        refresh_interval=None,
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
        created_by="tester",
    )
    assert src.state == SourceState.PROPOSED
    assert src.created_by == "tester"
    assert src.refresh_interval == 1440


def test_state_transition_rules():
    payload = SourceCreate(
        slug="src-test-2",
        name="Fonte Teste 2",
        description="",
        type="news_rss",
        category="official",
        themes=["politica"],
        info_types=["news"],
        refresh_interval=180,
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
    src = create_source(payload)
    assert src.state == SourceState.PROPOSED
    activated = change_source_state(src.id, SourceState.ACTIVE, "aprovar", "tester")
    assert activated is not None
    assert activated.state == SourceState.ACTIVE
    with pytest.raises(ValueError):
        change_source_state(src.id, SourceState.PROPOSED, "retroceder", "tester")
