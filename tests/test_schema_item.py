import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PROJECT_ROOT / "schemas" / "inspectah_item_v0_1.json"


def load_schema():
    return json.loads(SCHEMA_PATH.read_text())


def test_state_enum_and_required_fields():
    schema = load_schema()
    states = schema["properties"]["state"]["enum"]
    assert states == ["S0", "S1", "S2", "S3", "S4"]
    required = set(schema["required"])
    expected = {
        "source_id",
        "item_id",
        "bundle_id",
        "state",
        "run_id",
        "watcher_type",
        "fetched_at",
        "request_url",
        "status_code",
        "response_size_bytes",
        "content_type",
        "equivalence_key",
        "confidence_local",
    }
    assert expected <= required


def test_claims_reference_claim_schema():
    schema = load_schema()
    claims = schema["properties"]["claims"]
    assert claims["items"]["$ref"].startswith("inspectah_claim_v0_1.json")


def test_entities_are_unique_strings():
    schema = load_schema()
    entities = schema["properties"]["entities"]
    assert entities["type"] == "array"
    assert entities["items"]["type"] == "string"
    assert entities["uniqueItems"] is True
