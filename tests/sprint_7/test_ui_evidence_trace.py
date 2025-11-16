from __future__ import annotations

from inspectah.ui import runtime_bridge


def test_evidence_page_links(client):
    record = runtime_bridge.get_record("api-202410-901")
    assert record is not None
    resp = client.get(f"/evidence/{record.item_id}")
    assert resp.status_code == 200
    assert "Manifesto" in resp.text
