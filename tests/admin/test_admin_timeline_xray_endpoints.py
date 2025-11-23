from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi.testclient import TestClient

from inspectah.api import build_app


def _client() -> TestClient:
    app = build_app()
    assert app is not None, "FastAPI app não criado"
    return TestClient(app)


def _parse(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def _timestamps_are_sorted(events: List[dict]) -> bool:
    parsed = [_parse(ev["timestamp"]) for ev in events]
    return parsed == sorted(parsed)


def test_timeline_happy_path():
    client = _client()
    case_id = "obra_publica:2025-123"
    resp = client.get(f"/admin/cases/{case_id}/timeline")
    assert resp.status_code == 200
    payload = resp.json()
    timeline = payload.get("timeline")
    assert timeline
    assert timeline["case_id"] == case_id
    events = timeline.get("events", [])
    assert len(events) >= 2
    assert _timestamps_are_sorted(events)
    for event in events:
        assert event["id"]
        assert event["event_type"]
        assert event["summary"]


def test_timeline_not_found():
    client = _client()
    resp = client.get("/admin/cases/unknown-case/timeline")
    assert resp.status_code == 404


def test_xray_happy_path():
    client = _client()
    case_id = "evento_climatico:inmet-2025-0901"
    resp = client.get(f"/admin/cases/{case_id}/xray")
    assert resp.status_code == 200
    payload = resp.json()
    xray = payload.get("xray")
    assert xray
    assert xray["case_id"] == case_id
    for section in ["debunker", "committees", "anchors", "evidences"]:
        assert section in xray
        assert xray[section], f"{section} não deveria estar vazio"
    assert xray["debunker"]["explanation"]
    assert xray["evidences"]["evidences"]


def test_xray_not_found():
    client = _client()
    resp = client.get("/admin/cases/unknown-case/xray")
    assert resp.status_code == 404
