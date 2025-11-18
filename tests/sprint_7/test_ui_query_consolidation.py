from __future__ import annotations

import re

from inspectah.ui import runtime_bridge
from inspectah.ui.views import query as query_view


def test_query_page_consolidates_records(client):
    payload = {"categoria": "graos"}
    resp = client.post("/query", data=payload)
    assert resp.status_code == 200
    assert "Decisão consolidada" in resp.text

    match = re.search(r"Valor consolidado:\s*<strong>R\$ ([0-9.,]+)</strong>", resp.text)
    assert match

    filters = query_view._parse_filters(payload)  # type: ignore[attr-defined]
    records = runtime_bridge.run_query(filters)
    decision = runtime_bridge.consolidate(records)
    assert decision.value is not None
    assert f"{decision.value:.2f}" in match.group(1).replace(",", ".")
