import tempfile
from pathlib import Path

from inspectah.evidence import builder, verifier

SAMPLE_ITEM = {
    "source_id": "rss_fixture",
    "item_id": "rss-1",
    "run_id": "run-123",
    "watcher_type": "rss",
    "fetched_at": "2025-03-10T10:00:00Z",
    "request_url": "fixtures/s5/rss_feed.xml",
}


def test_verifier_pass_and_detect_corruption():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = builder.build_bundle(
            SAMPLE_ITEM,
            raw_content=b"dados",
            text_content="texto",
            base_dir=tmpdir,
        )
        response = verifier.verify_bundle(result["bundle_path"])
        assert response["status"] == "PASS"

        raw_path = Path(result["bundle_path"]) / "raw.bin"
        raw_path.write_bytes(b"alterado")
        response_fail = verifier.verify_bundle(result["bundle_path"])
        assert response_fail["status"] == "FAIL"
        assert "hash divergente" in response_fail["reason"]
