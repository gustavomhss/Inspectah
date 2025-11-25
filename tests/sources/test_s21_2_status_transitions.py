import pytest

from app.sources import service
from app.sources.models import SourceState
from app.sources.schemas import SourceCreate


def _payload(slug: str = "status-src") -> SourceCreate:
    return SourceCreate(
        slug=slug,
        name="Fonte Status",
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
        refresh_interval=None,
    )


def test_valid_status_progression():
    src = service.create_source(_payload())
    assert src.state == SourceState.PROPOSED
    active = service.change_source_state(src.id, SourceState.ACTIVE, "aprovar", "tester")
    assert active is not None and active.state == SourceState.ACTIVE
    suspended = service.change_source_state(src.id, SourceState.DISABLED_TEMP, "pausar", "tester")
    assert suspended is not None and suspended.state == SourceState.DISABLED_TEMP
    back_active = service.change_source_state(src.id, SourceState.ACTIVE, "retomar", "tester")
    assert back_active is not None and back_active.state == SourceState.ACTIVE


def test_invalid_backwards_or_terminal_transition():
    src = service.create_source(_payload(slug="status-src-2"))
    service.change_source_state(src.id, SourceState.ACTIVE, "aprovar", "tester")
    with pytest.raises(ValueError):
        service.change_source_state(src.id, SourceState.PROPOSED, "retroceder", "tester")
    terminal = service.change_source_state(src.id, SourceState.DISABLED_PERM, "desativar", "tester")
    assert terminal is not None and terminal.state == SourceState.DISABLED_PERM
    with pytest.raises(ValueError):
        service.change_source_state(src.id, SourceState.ACTIVE, "reativar", "tester")
