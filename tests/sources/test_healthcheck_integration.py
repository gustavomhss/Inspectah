from app.sources.healthcheck import run_healthcheck
from app.sources.models import SourceState
from app.sources.schemas import SourceCreate
from app.sources import service


def test_healthcheck_creates_record():
    src = service.create_source(
        SourceCreate(
            slug="hc-source",
            name="Fonte Healthcheck",
            description="",
            type="news_rss",
            category="official",
            themes=["politica"],
            info_types=["news"],
            protocol="https",
            format="rss",
            endpoint="http://localhost:9/invalid",  # força erro rápido
            auth_type="none",
            auth_config={},
            request_params={},
            headers={},
            frequency="daily",
            timeout_ms=1000,
            retry_policy={},
            parsing_config={},
            redundancy_group=None,
            redundancy_role=None,
            meta={},
            created_by="tester",
        )
    )
    assert src.state == SourceState.PROPOSED
    result = run_healthcheck(src.id)
    assert result is not None
    health_history = service.list_healthchecks(src.id)
    assert len(health_history) >= 1
