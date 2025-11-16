import json
import tempfile
from pathlib import Path

from inspectah.pipeline.pipeline_fixtures import run_pipeline_with_fixtures

GOLDEN_SUMMARY = Path("tests/golden/s5_pipeline/expected_items_summary.json")


def test_pipeline_with_fixtures_matches_golden():
    with tempfile.TemporaryDirectory() as evidence_dir, tempfile.TemporaryDirectory() as index_dir:
        result = run_pipeline_with_fixtures(
            evidence_base=evidence_dir,
            index_base=index_dir,
            summary_path=None,
        )
    summary = result["summary"]
    assert summary["items_total"] > 0
    assert summary["bundles_total"] == summary["items_total"]
    assert summary["items_by_state"]["S3"] == summary["items_by_state"]["S4"]
    assert all(state in {"S0", "S1", "S2", "S3", "S4"} for state in summary["items_by_state"])
    for item in result["items"]:
        assert item["equivalence_key"]
        assert item["state"] in {"S2", "S3", "S4"}
    golden = json.loads(GOLDEN_SUMMARY.read_text())
    assert summary["items_total"] == golden["items_total"]
    assert summary["items_by_state"] == golden["items_by_state"]
    assert summary["items_by_source"] == golden["items_by_source"]
