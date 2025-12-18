"""
S39: Tests for JSON Schema validation
"""
import json
import pytest
from pathlib import Path
from datetime import datetime, timezone

try:
    import jsonschema
    from jsonschema import validate, ValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False


SCHEMAS_DIR = Path(__file__).parent.parent.parent / "schemas"


@pytest.fixture
def response_envelope_schema():
    """Load response envelope schema."""
    schema_path = SCHEMAS_DIR / "response_envelope_v1.json"
    with open(schema_path) as f:
        return json.load(f)


@pytest.fixture
def explanation_schema():
    """Load explanation schema."""
    schema_path = SCHEMAS_DIR / "explanation_v1.json"
    with open(schema_path) as f:
        return json.load(f)


@pytest.fixture
def memory_context_schema():
    """Load memory context schema."""
    schema_path = SCHEMAS_DIR / "memory_context_v1.json"
    with open(schema_path) as f:
        return json.load(f)


@pytest.fixture
def signal_schema():
    """Load signal schema."""
    schema_path = SCHEMAS_DIR / "signal_v1.json"
    with open(schema_path) as f:
        return json.load(f)


@pytest.fixture
def contract_version_schema():
    """Load contract version schema."""
    schema_path = SCHEMAS_DIR / "contract_version_v1.json"
    with open(schema_path) as f:
        return json.load(f)


class TestSchemaFiles:
    """Tests for schema file existence and validity."""

    def test_schemas_directory_exists(self):
        """Verify schemas directory exists."""
        assert SCHEMAS_DIR.exists()

    def test_response_envelope_schema_exists(self):
        """Verify response envelope schema exists."""
        assert (SCHEMAS_DIR / "response_envelope_v1.json").exists()

    def test_explanation_schema_exists(self):
        """Verify explanation schema exists."""
        assert (SCHEMAS_DIR / "explanation_v1.json").exists()

    def test_memory_context_schema_exists(self):
        """Verify memory context schema exists."""
        assert (SCHEMAS_DIR / "memory_context_v1.json").exists()

    def test_signal_schema_exists(self):
        """Verify signal schema exists."""
        assert (SCHEMAS_DIR / "signal_v1.json").exists()

    def test_contract_version_schema_exists(self):
        """Verify contract version schema exists."""
        assert (SCHEMAS_DIR / "contract_version_v1.json").exists()

    def test_all_schemas_valid_json(self):
        """Verify all schemas are valid JSON."""
        for schema_file in SCHEMAS_DIR.glob("*.json"):
            with open(schema_file) as f:
                data = json.load(f)
                assert "$schema" in data or "properties" in data


@pytest.mark.skipif(not JSONSCHEMA_AVAILABLE, reason="jsonschema not installed")
class TestResponseEnvelopeSchema:
    """Tests for response envelope schema validation."""

    def test_valid_success_response(self, response_envelope_schema):
        """Test valid success response."""
        data = {
            "status": "success",
            "data": {"key": "value"},
            "meta": {
                "version": "1.0.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        }
        validate(instance=data, schema=response_envelope_schema)

    def test_valid_error_response(self, response_envelope_schema):
        """Test valid error response."""
        data = {
            "status": "error",
            "meta": {
                "version": "1.0.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            "errors": [
                {"code": "NOT_FOUND", "message": "Resource not found"},
            ],
        }
        validate(instance=data, schema=response_envelope_schema)

    def test_valid_paginated_response(self, response_envelope_schema):
        """Test valid paginated response."""
        data = {
            "status": "success",
            "data": [{"id": 1}, {"id": 2}],
            "meta": {
                "version": "1.0.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "request_id": "req_123",
                "duration_ms": 45,
            },
            "pagination": {
                "page": 1,
                "page_size": 10,
                "total_items": 100,
                "total_pages": 10,
                "has_next": True,
                "has_prev": False,
            },
        }
        validate(instance=data, schema=response_envelope_schema)

    def test_invalid_status(self, response_envelope_schema):
        """Test invalid status value."""
        data = {
            "status": "invalid_status",
            "meta": {
                "version": "1.0.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        }
        with pytest.raises(ValidationError):
            validate(instance=data, schema=response_envelope_schema)

    def test_missing_meta(self, response_envelope_schema):
        """Test missing required meta field."""
        data = {
            "status": "success",
            "data": {},
        }
        with pytest.raises(ValidationError):
            validate(instance=data, schema=response_envelope_schema)


@pytest.mark.skipif(not JSONSCHEMA_AVAILABLE, reason="jsonschema not installed")
class TestExplanationSchema:
    """Tests for explanation schema validation."""

    def test_valid_verdict_explanation(self, explanation_schema):
        """Test valid verdict explanation."""
        data = {
            "id": "exp_verdict_001",
            "type": "verdict",
            "target_id": "claim_123",
            "summary": "Claim was determined to be false based on evidence",
            "reasoning_path": [
                {
                    "step_number": 1,
                    "description": "Collected evidence",
                    "inputs": ["source:src_001"],
                    "output": "Found 3 evidence items",
                    "confidence": 0.9,
                },
            ],
            "factors": [
                {
                    "name": "evidence_count",
                    "value": "3",
                    "weight": 0.4,
                    "direction": "positive",
                },
            ],
        }
        validate(instance=data, schema=explanation_schema)

    def test_valid_signal_explanation(self, explanation_schema):
        """Test valid signal explanation."""
        data = {
            "id": "exp_signal_001",
            "type": "signal",
            "target_id": "sig_lies_001",
            "summary": "High lies in circulation detected",
            "reasoning_path": [
                {
                    "step_number": 1,
                    "description": "Aggregated signal components",
                    "inputs": ["region:br"],
                    "output": "Signal value: 0.75",
                },
            ],
            "counterfactuals": [
                {
                    "condition": "If evidence count were lower",
                    "outcome": "Signal would be 0.5",
                    "likelihood": 0.8,
                },
            ],
        }
        validate(instance=data, schema=explanation_schema)

    def test_invalid_explanation_type(self, explanation_schema):
        """Test invalid explanation type."""
        data = {
            "id": "exp_invalid",
            "type": "invalid_type",
            "target_id": "x",
            "summary": "Test",
            "reasoning_path": [],
        }
        with pytest.raises(ValidationError):
            validate(instance=data, schema=explanation_schema)

    def test_invalid_id_pattern(self, explanation_schema):
        """Test invalid ID pattern."""
        data = {
            "id": "invalid-id-pattern",  # Should start with exp_
            "type": "verdict",
            "target_id": "x",
            "summary": "Test",
            "reasoning_path": [],
        }
        with pytest.raises(ValidationError):
            validate(instance=data, schema=explanation_schema)


@pytest.mark.skipif(not JSONSCHEMA_AVAILABLE, reason="jsonschema not installed")
class TestMemoryContextSchema:
    """Tests for memory context schema validation."""

    def test_valid_session_context(self, memory_context_schema):
        """Test valid session context."""
        data = {
            "agent_id": "agent_debunker_001",
            "context_type": "session",
            "context_id": "sess_abc123",
            "entries": [
                {
                    "id": "mem_001",
                    "type": "fact",
                    "content": "User asked about COVID vaccines",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "relevance_score": 0.9,
                },
            ],
        }
        validate(instance=data, schema=memory_context_schema)

    def test_valid_claim_context(self, memory_context_schema):
        """Test valid claim context."""
        data = {
            "agent_id": "agent_verifier_001",
            "context_type": "claim",
            "context_id": "claim_xyz",
            "entries": [],
            "summary": {
                "key_facts": ["Original claim was about economy"],
                "active_claims": ["claim_xyz"],
                "confidence_level": 0.85,
            },
        }
        validate(instance=data, schema=memory_context_schema)

    def test_invalid_context_type(self, memory_context_schema):
        """Test invalid context type."""
        data = {
            "agent_id": "agent_001",
            "context_type": "invalid",
        }
        with pytest.raises(ValidationError):
            validate(instance=data, schema=memory_context_schema)

    def test_invalid_agent_id_pattern(self, memory_context_schema):
        """Test invalid agent ID pattern."""
        data = {
            "agent_id": "invalid-agent",  # Should start with agent_
            "context_type": "session",
        }
        with pytest.raises(ValidationError):
            validate(instance=data, schema=memory_context_schema)


@pytest.mark.skipif(not JSONSCHEMA_AVAILABLE, reason="jsonschema not installed")
class TestSignalSchema:
    """Tests for signal schema validation."""

    def test_valid_lies_signal(self, signal_schema):
        """Test valid lies in circulation signal."""
        data = {
            "id": "sig_lies_001",
            "signal_type": "lies_in_circulation",
            "value": 0.75,
            "scope": "national",
            "scope_filter": "BR",
            "components": [
                {
                    "name": "debunked_count",
                    "value": 45,
                    "weight": 0.4,
                    "source_count": 10,
                },
            ],
            "trend": {
                "direction": "up",
                "change_rate": 0.02,
                "period_hours": 24,
            },
        }
        validate(instance=data, schema=signal_schema)

    def test_valid_battleground_signal(self, signal_schema):
        """Test valid battleground signal."""
        data = {
            "id": "sig_battle_001",
            "signal_type": "battleground_index",
            "value": 0.65,
            "scope": "topical",
            "scope_filter": "topic_elections",
            "thresholds": {
                "warning": 0.6,
                "critical": 0.8,
                "current_level": "warning",
            },
        }
        validate(instance=data, schema=signal_schema)

    def test_invalid_signal_value_range(self, signal_schema):
        """Test signal value out of range."""
        data = {
            "id": "sig_001",
            "signal_type": "silence_radar",
            "value": 1.5,  # Should be 0-1
            "scope": "global",
        }
        with pytest.raises(ValidationError):
            validate(instance=data, schema=signal_schema)

    def test_invalid_signal_type(self, signal_schema):
        """Test invalid signal type."""
        data = {
            "id": "sig_001",
            "signal_type": "invalid_signal",
            "value": 0.5,
            "scope": "global",
        }
        with pytest.raises(ValidationError):
            validate(instance=data, schema=signal_schema)


@pytest.mark.skipif(not JSONSCHEMA_AVAILABLE, reason="jsonschema not installed")
class TestContractVersionSchema:
    """Tests for contract version schema validation."""

    def test_valid_active_contract(self, contract_version_schema):
        """Test valid active contract."""
        data = {
            "contract_name": "ClaimContract",
            "version": "2.1.0",
            "status": "active",
            "schema_ref": "https://inspectah.dev/schemas/claim_v2.json",
            "metadata": {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "author": "inspectah-team",
                "description": "Contract for claim data exchange",
            },
        }
        validate(instance=data, schema=contract_version_schema)

    def test_valid_deprecated_contract(self, contract_version_schema):
        """Test valid deprecated contract with compatibility info."""
        data = {
            "contract_name": "SourceContract",
            "version": "1.0.0",
            "status": "deprecated",
            "compatibility": {
                "backward_compatible_with": ["0.9.0"],
                "deprecation_date": "2025-06-01",
                "sunset_date": "2025-12-31",
            },
            "changelog": [
                {
                    "version": "1.0.0",
                    "date": "2025-01-15",
                    "changes": [
                        {"type": "added", "description": "Initial release"},
                    ],
                },
            ],
        }
        validate(instance=data, schema=contract_version_schema)

    def test_contract_with_breaking_changes(self, contract_version_schema):
        """Test contract with breaking changes."""
        data = {
            "contract_name": "VerdictContract",
            "version": "2.0.0",
            "status": "active",
            "compatibility": {
                "breaking_changes": [
                    {
                        "change_type": "field_removed",
                        "description": "Removed legacy_id field",
                        "affected_field": "legacy_id",
                        "migration_guide": "Use id field instead",
                    },
                ],
            },
        }
        validate(instance=data, schema=contract_version_schema)

    def test_contract_with_dependencies(self, contract_version_schema):
        """Test contract with dependencies."""
        data = {
            "contract_name": "ExplanationContract",
            "version": "1.0.0",
            "status": "active",
            "dependencies": [
                {
                    "contract_name": "VerdictContract",
                    "version_range": "^2.0.0",
                    "optional": False,
                },
                {
                    "contract_name": "SignalContract",
                    "version_range": ">=1.0.0",
                    "optional": True,
                },
            ],
        }
        validate(instance=data, schema=contract_version_schema)

    def test_invalid_version_format(self, contract_version_schema):
        """Test invalid semver format."""
        data = {
            "contract_name": "Test",
            "version": "invalid",  # Should be semver
            "status": "active",
        }
        with pytest.raises(ValidationError):
            validate(instance=data, schema=contract_version_schema)

    def test_invalid_status(self, contract_version_schema):
        """Test invalid status value."""
        data = {
            "contract_name": "Test",
            "version": "1.0.0",
            "status": "invalid_status",
        }
        with pytest.raises(ValidationError):
            validate(instance=data, schema=contract_version_schema)


class TestSchemaStructure:
    """Tests for schema structure without jsonschema dependency."""

    def test_response_envelope_has_required_defs(self, response_envelope_schema):
        """Test response envelope has required definitions."""
        assert "$defs" in response_envelope_schema
        assert "ResponseMeta" in response_envelope_schema["$defs"]
        assert "ApiError" in response_envelope_schema["$defs"]
        assert "Pagination" in response_envelope_schema["$defs"]

    def test_explanation_has_required_defs(self, explanation_schema):
        """Test explanation has required definitions."""
        assert "$defs" in explanation_schema
        assert "ReasoningStep" in explanation_schema["$defs"]
        assert "ExplanationFactor" in explanation_schema["$defs"]
        assert "Counterfactual" in explanation_schema["$defs"]

    def test_memory_context_has_required_defs(self, memory_context_schema):
        """Test memory context has required definitions."""
        assert "$defs" in memory_context_schema
        assert "MemoryEntry" in memory_context_schema["$defs"]
        assert "ContextSummary" in memory_context_schema["$defs"]

    def test_signal_has_required_defs(self, signal_schema):
        """Test signal has required definitions."""
        assert "$defs" in signal_schema
        assert "SignalComponent" in signal_schema["$defs"]
        assert "SignalTrend" in signal_schema["$defs"]
        assert "SignalThresholds" in signal_schema["$defs"]

    def test_contract_version_has_required_defs(self, contract_version_schema):
        """Test contract version has required definitions."""
        assert "$defs" in contract_version_schema
        assert "CompatibilityInfo" in contract_version_schema["$defs"]
        assert "BreakingChange" in contract_version_schema["$defs"]
        assert "ChangelogEntry" in contract_version_schema["$defs"]
        assert "ContractDependency" in contract_version_schema["$defs"]
