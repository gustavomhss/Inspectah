from inspectah.models import InspectahItem
from inspectah.normalizer import normalizer


BASE_ITEM = InspectahItem(
    source_id="api",
    item_id="api-123",
    bundle_id="bundle-123",
    state="S2",
    run_id="run",
    watcher_type="api",
    fetched_at="2025-03-10T10:00:00Z",
    request_url="http://example",
    status_code=200,
    response_size_bytes=10,
    content_type="application/json",
    equivalence_key="metric__na__20250310",
    confidence_local=0.6,
)


def _fake_claim(metric: str = "metric_x", value: str = "SIM") -> dict:
    return {
        "claim_id": "claim-1",
        "claim_type": "resultado_binario",
        "declared_metric": metric,
        "declared_subject": "contexto",
        "declared_value": value,
        "declared_unit": None,
        "polarity": "informa_sem_julgar",
        "local_verdict": "segundo_esta_fonte_este_e_o_valor",
        "confidence_claim": 0.9,
    }


def test_normalizer_ai_mode_promotes_item():
    item = InspectahItem.from_dict(BASE_ITEM.to_dict())

    def fake_client(_text, _meta):
        return [_fake_claim()]

    updated = normalizer.normalize_item(item, text="Texto real", mode="gpt4mini", client=fake_client)
    assert updated.state == "S3"
    assert updated.claims
    assert updated.reasoning_short == "Claims gerados via GPT-4.1 mini"


def test_normalizer_ai_mode_handles_failures():
    item = InspectahItem.from_dict(BASE_ITEM.to_dict())

    def failing_client(_text, _meta):
        raise RuntimeError("api indisponível")

    updated = normalizer.normalize_item(item, text="Texto real", mode="gpt4mini", client=failing_client)
    assert updated.state == "S2"
    assert not updated.claims
