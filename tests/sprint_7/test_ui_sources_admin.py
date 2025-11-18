from __future__ import annotations

from pathlib import Path

import yaml

from inspectah.sprint7.gate_utils import preserved_file


def test_admin_sources_page_and_update(client):
    resp = client.get("/admin/sources")
    assert resp.status_code == 200
    assert "fonte_a" in resp.text

    source_path = Path("config") / "sources" / "fonte_a.yaml"
    with preserved_file(source_path):
        payload = {
            "name": "Boletim RSS Sindicato SP",
            "description": "Teste automático",
            "transport_url": "https://dados.sindicato-sp.org/boletim/rss",
            "sample_file": "fixtures/sprint_6/fonte_a_rss.xml",
            "notes": "Teste automático",
            "enabled": "1",
        }
        update = client.post("/admin/sources/fonte_a", data=payload)
        assert update.status_code == 200
        data = yaml.safe_load(source_path.read_text(encoding="utf-8"))
        assert "Teste automático" in data.get("notes", [])
