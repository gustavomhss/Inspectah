import tempfile

from inspectah.indexer.indexer import LocalIndexer
from inspectah.models import InspectahItem


BASE_ITEM = InspectahItem(
    source_id="rss",
    item_id="item-1",
    bundle_id="bundle-1",
    state="S3",
    run_id="run",
    watcher_type="rss",
    fetched_at="2025-03-10T10:00:00Z",
    request_url="http://example",
    status_code=200,
    response_size_bytes=10,
    content_type="text/plain",
    equivalence_key="metric__na__20250310",
    confidence_local=0.7,
    claims=[],
)


def test_indexer_persists_and_queries_by_filters():
    with tempfile.TemporaryDirectory() as tmpdir:
        indexer = LocalIndexer(storage_path=tmpdir)
        indexer.index(BASE_ITEM)
        results = indexer.query(source_id="rss")
        assert results
        assert results[0].equivalence_key == BASE_ITEM.equivalence_key
        assert not indexer.query(source_id="outro")
        assert indexer.query(equivalence_key=BASE_ITEM.equivalence_key)
