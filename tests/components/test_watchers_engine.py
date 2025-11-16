import io
import json
import logging
import tempfile
from pathlib import Path

from inspectah.watchers import engine


FIXTURES_BASE = Path("fixtures/s5")


def _registry_content(enabled_html: bool = False) -> str:
    return json.dumps(
        {
            "sources": [
                {
                    "id": "rss_fixture",
                    "type": "rss",
                    "url": "fixtures/s5/rss_feed.xml",
                    "frequency": "PT1H",
                    "timeout": 5,
                    "parse_spec": {"fixture": "rss_feed.xml"},
                    "enabled": True,
                },
                {
                    "id": "api_fixture",
                    "type": "api",
                    "url": "fixtures/s5/api_feed.json",
                    "frequency": "PT30M",
                    "timeout": 5,
                    "parse_spec": {"fixture": "api_feed.json"},
                    "enabled": True,
                },
                {
                    "id": "html_fixture",
                    "type": "html",
                    "url": "fixtures/s5/html_page.html",
                    "frequency": "PT1H",
                    "timeout": 5,
                    "parse_spec": {"fixture": "html_page.html"},
                    "enabled": enabled_html,
                },
            ]
        },
        indent=2,
    )


def _write_registry(content: str) -> Path:
    tmpdir = tempfile.mkdtemp()
    registry_path = Path(tmpdir) / "registry.yaml"
    registry_path.write_text(content)
    return registry_path


def test_engine_runs_multiple_sources():
    registry_path = _write_registry(_registry_content())
    log_stream = io.StringIO()
    handler = logging.StreamHandler(log_stream)
    test_logger = logging.getLogger("watcher_test_success")
    test_logger.setLevel(logging.INFO)
    test_logger.handlers = [handler]

    result = engine.run_watchers(registry_path, logger=test_logger, fixtures_base=FIXTURES_BASE)

    assert len(result["runs"]) == 2
    assert all(run["status"] == "success" for run in result["runs"])
    assert all(run["items"] for run in result["runs"])
    assert "watcher_run" in log_stream.getvalue()


def test_engine_isolates_failures():
    registry_path = _write_registry(_registry_content())

    def failing_watcher(_config, **_):
        raise RuntimeError("boom")

    overrides = {"rss": failing_watcher}
    result = engine.run_watchers(registry_path, watcher_overrides=overrides, fixtures_base=FIXTURES_BASE)

    statuses = {run["source_id"]: run["status"] for run in result["runs"]}
    assert statuses["rss_fixture"] == "fail"
    assert statuses["api_fixture"] == "success"


def test_engine_respects_enabled_flag():
    registry_path = _write_registry(_registry_content(enabled_html=False))

    result = engine.run_watchers(registry_path, fixtures_base=FIXTURES_BASE)

    source_ids = [run["source_id"] for run in result["runs"]]
    assert "html_fixture" not in source_ids
