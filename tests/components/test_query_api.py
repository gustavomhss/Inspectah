import json
import tempfile
from pathlib import Path

from inspectah.indexer.query_api import QueryAPI
from inspectah.models import InspectahItem


def _write_items(tmpdir: Path, items: list[InspectahItem]) -> Path:
    storage = tmpdir / "data/index"
    storage.mkdir(parents=True, exist_ok=True)
    data_file = storage / "items.jsonl"
    with data_file.open("w", encoding="utf-8") as handle:
        for item in items:
            handle.write(json.dumps(item.to_dict()) + "\n")
    return storage


def test_list_items_filters():
    with tempfile.TemporaryDirectory() as tmp:
        base_item = InspectahItem(
            source_id="rss",
            item_id="rss-1",
            bundle_id="bundle-1",
            state="S4",
            run_id="run",
            watcher_type="rss",
            fetched_at="2025-03-10T10:00:00Z",
            request_url="http://rss",
            status_code=200,
            response_size_bytes=100,
            content_type="text/xml",
            equivalence_key="metric__na__20250310",
            confidence_local=0.8,
        )
        items = [
            base_item,
            InspectahItem.from_dict({**base_item.to_dict(), "source_id": "api", "item_id": "api-1", "equivalence_key": "metric__na__20250311"}),
        ]
        storage = _write_items(Path(tmp), items)
        api = QueryAPI(storage)
        assert len(api.list_items()) == 2
        assert len(api.list_items(source_id="rss")) == 1
        assert len(api.list_items(equivalence_key="metric__na__20250311")) == 1


def test_get_item_and_list_sources():
    with tempfile.TemporaryDirectory() as tmp:
        base_item = InspectahItem(
            source_id="rss",
            item_id="rss-1",
            bundle_id="bundle-1",
            state="S4",
            run_id="run",
            watcher_type="rss",
            fetched_at="2025-03-10T10:00:00Z",
            request_url="http://rss",
            status_code=200,
            response_size_bytes=100,
            content_type="text/xml",
            equivalence_key="metric__na__20250310",
            confidence_local=0.8,
        )
        api_item = InspectahItem.from_dict({**base_item.to_dict(), "source_id": "api", "item_id": "api-1"})
        storage = _write_items(Path(tmp), [base_item, api_item])
        api = QueryAPI(storage)
        assert api.get_item("rss-1").item_id == "rss-1"
        assert api.get_item("missing") is None
        sources = set(api.list_sources())
        assert sources == {"rss", "api"}
