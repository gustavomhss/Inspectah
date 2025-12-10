import pytest

from app.sources import service
from app.sources.schemas import SourceCreate


def _base_payload(**overrides) -> SourceCreate:
    data = dict(
        slug="news-refresh",
        name="Fonte Notícias",
        description="Fonte de notícias",
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
    data.update(overrides)
    return SourceCreate(**data)


def test_refresh_interval_default_by_type():
    src = service.create_source(_base_payload(refresh_interval=None))
    assert src.refresh_interval == service._default_refresh_interval("news_rss")  # type: ignore[attr-defined]


def test_refresh_interval_explicit_and_validation():
    src = service.create_source(_base_payload(slug="news-refresh-explicit", refresh_interval=60))
    assert src.refresh_interval == 60
    with pytest.raises(ValueError):
        service.create_source(_base_payload(slug="news-refresh-invalid", refresh_interval=5))


def test_official_open_requires_description_and_public_endpoint():
    ok_payload = _base_payload(
        slug="official-open",
        type="official_open",
        description="Portal oficial aberto",
        endpoint="https://dados.oficial.br/portal",
        auth_type="none",
        refresh_interval=None,
    )
    src = service.create_source(ok_payload)
    assert src.type == "official_open"
    assert src.refresh_interval == service._default_refresh_interval("official_open")  # type: ignore[attr-defined]

    with pytest.raises(ValueError):
        service.create_source(ok_payload.model_copy(update={"description": ""}))

    with pytest.raises(ValueError):
        service.create_source(ok_payload.model_copy(update={"auth_type": "token"}))
