from app.sources.models import Source, SourceState


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
