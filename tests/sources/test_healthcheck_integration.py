from app.sources.healthcheck import run_healthcheck
from app.sources import service


def test_healthcheck_creates_record_using_seed():
    seeds = service.list_sources()
    assert seeds, "Seeds devem existir"
    target = seeds[0]
    result = run_healthcheck(target.id)
    assert result is not None
    history = service.list_healthchecks(target.id)
    assert len(history) >= 1
    assert history[0].source_id == target.id
