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


def test_state_transition_rules():
    payload = SourceCreate(
        slug="src-test-2",
        name="Fonte Teste 2",
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
    src = create_source(payload)
    assert src.state == SourceState.PROPOSED
    with pytest.raises(ValueError):
        change_source_state(src.id, SourceState.ACTIVE, "pular teste", "tester")
