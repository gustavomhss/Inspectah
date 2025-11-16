from inspectah.models import InspectahItem
from inspectah.normalizer import normalizer


def _base_item(state: str = "S2") -> InspectahItem:
    return InspectahItem(
        source_id="rss",
        item_id="item-1",
        bundle_id="bundle-1",
        state=state,
        run_id="run",
        watcher_type="rss",
        fetched_at="2025-03-10T10:00:00Z",
        request_url="http://example",
        status_code=200,
        response_size_bytes=10,
        content_type="text/plain",
        equivalence_key="metric__na__20250310",
        confidence_local=0.5,
    )


def test_normalizer_stub_generates_claims():
    item = _base_item()
    updated = normalizer.normalize_item(item, text="Projeto aprovado", meta={"facts": {"metric": "lei", "value": "SIM"}})
    assert updated.state == "S3"
    assert updated.claims
    assert updated.claims[0].declared_metric == "lei"


def test_normalizer_handles_invalid_claim():
    def bad_stub(_text, _meta):
        return [{"claim_type": "resultado_binario"}]

    item = _base_item()
    updated = normalizer.normalize_item(item, text="texto", client=bad_stub)
    assert updated.state == "S2"
    assert not updated.claims


def test_normalizer_handles_exception():
    def raising_stub(_text, _meta):
        raise RuntimeError("boom")

    item = _base_item()
    updated = normalizer.normalize_item(item, text="texto", client=raising_stub)
    assert updated.state == "S2"
