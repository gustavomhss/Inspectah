from __future__ import annotations


def test_model_fields_page(client):
    resp = client.get("/model/fields")
    assert resp.status_code == 200
    assert "Modelo canônico" in resp.text
    # Ensure canonical fields appear
    assert "item_id" in resp.text
