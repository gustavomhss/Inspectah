"""
Tests for S40-BE-023/024: Truth Twin and Decision Inspector endpoints.

Tests for the P4 exposure endpoints in app/api/truth_routes.py.
"""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime

# Skip tests if FastAPI is not available
try:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


class MockTruthRecord:
    """Mock TruthRecord for testing."""

    def __init__(
        self,
        id: str = "record-001",
        claim_id: str = None,
        slug: str = None,
        domain: str = "saude",
        current_state = None,
        created_at: str = "2025-01-01T00:00:00Z",
        updated_at: str = "2025-01-01T00:00:00Z",
        metadata: dict = None,
        last_decision_id: str = None,
    ):
        self.id = id
        self.claim_id = claim_id
        self.slug = slug or f"test-slug-{id}"
        self.domain = domain
        self.current_state = current_state or MockState("PENDING")
        self.created_at = created_at
        self.updated_at = updated_at
        self.metadata = metadata or {}
        self.last_decision_id = last_decision_id


class MockState:
    """Mock state enum."""

    def __init__(self, value: str):
        self.value = value


class MockEvent:
    """Mock state change event."""

    def __init__(
        self,
        previous_state = None,
        new_state = None,
        reason: str = "test",
        created_at: str = "2025-01-01T00:00:00Z",
        decision_id: str = None,
    ):
        self.previous_state = previous_state
        self.new_state = new_state or MockState("PENDING")
        self.reason = reason
        self.created_at = created_at
        self.decision_id = decision_id


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
class TestTruthTwinEndpoint:
    """Tests for GET /api/truth/{claim_id}/twin endpoint."""

    @pytest.fixture
    def mock_repos(self):
        """Create mock repositories."""
        with patch("app.api.truth_routes.TruthRepository") as mock_truth_repo, \
             patch("app.api.truth_routes.DecisionBlockRepository") as mock_decision_repo:

            truth_instance = MagicMock()
            decision_instance = MagicMock()

            mock_truth_repo.return_value = truth_instance
            mock_decision_repo.return_value = decision_instance

            yield {
                "truth_repo": truth_instance,
                "decision_repo": decision_instance,
            }

    @pytest.fixture
    def app(self, mock_repos):
        """Create test FastAPI app."""
        from app.api.truth_routes import router

        app = FastAPI()
        app.include_router(router)
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    def test_get_twin_with_record(self, client, mock_repos):
        """Test getting twin when record exists."""
        mock_record = MockTruthRecord(
            id="record-001",
            claim_id="claim-001",
            domain="saude",
            current_state=MockState("PROMOTED"),
        )
        # New: First lookup is by claim_id
        mock_repos["truth_repo"].get_record_by_claim_id.return_value = mock_record
        mock_repos["truth_repo"].get_record.return_value = None  # Fallback not used
        mock_repos["truth_repo"].list_events.return_value = []
        mock_repos["decision_repo"].get_by_claim.return_value = [
            {
                "id": "block-001",
                "decision_id": "dec-001",
                "gate": "G20",
                "decision_type": "ACCEPT",
                "initial_state": "PENDING",
                "final_state": "UNDER_REVIEW",
                "created_at": "2025-01-01T00:00:00Z",
                "policy_version": "1.0.0",
                "policy_name": "saude_v1",
                "evidence_refs": [],
                "references": None,
                "experience_refs": [],
            }
        ]

        response = client.get("/api/truth/claim-001/twin")

        assert response.status_code == 200
        data = response.json()
        assert data["claim_id"] == "claim-001"
        assert data["domain"] == "saude"
        assert data["current_state"] == "PROMOTED"
        assert "_latency_ms" in data

    def test_get_twin_with_slug_fallback(self, client, mock_repos):
        """Test getting twin by slug when claim_id not found."""
        # New: get_record_by_claim_id is called first, returns None
        mock_repos["truth_repo"].get_record_by_claim_id.return_value = None
        mock_repos["truth_repo"].get_record.return_value = None
        mock_repos["truth_repo"].get_record_by_slug.return_value = MockTruthRecord(
            id="record-002",
            claim_id="claim-by-slug",
            domain="politica",
        )
        mock_repos["truth_repo"].list_events.return_value = []
        mock_repos["decision_repo"].get_by_claim.return_value = []

        response = client.get("/api/truth/some-slug/twin")

        assert response.status_code == 200
        mock_repos["truth_repo"].get_record_by_slug.assert_called_once_with("some-slug")

    def test_get_twin_not_found(self, client, mock_repos):
        """Test getting twin when claim not found."""
        # New: get_record_by_claim_id is called first
        mock_repos["truth_repo"].get_record_by_claim_id.return_value = None
        mock_repos["truth_repo"].get_record.return_value = None
        mock_repos["truth_repo"].get_record_by_slug.return_value = None
        mock_repos["decision_repo"].get_by_claim.return_value = []

        response = client.get("/api/truth/nonexistent/twin")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_twin_from_blocks_only(self, client, mock_repos):
        """Test getting twin when only decision blocks exist."""
        # New: get_record_by_claim_id is called first
        mock_repos["truth_repo"].get_record_by_claim_id.return_value = None
        mock_repos["truth_repo"].get_record.return_value = None
        mock_repos["truth_repo"].get_record_by_slug.return_value = None
        mock_repos["decision_repo"].get_by_claim.return_value = [
            {
                "id": "block-001",
                "decision_id": "dec-001",
                "gate": "G20",
                "decision_type": "ACCEPT",
                "initial_state": "PENDING",
                "final_state": "UNDER_REVIEW",
                "created_at": "2025-01-01T00:00:00Z",
                "domain": "saude",
            }
        ]

        response = client.get("/api/truth/claim-orphan/twin")

        assert response.status_code == 200
        data = response.json()
        assert data["claim_id"] == "claim-orphan"
        assert data["domain"] == "saude"

    def test_get_twin_includes_events(self, client, mock_repos):
        """Test that twin includes state history from events."""
        mock_record = MockTruthRecord(
            id="record-001",
            claim_id="claim-001",
        )
        # New: get_record_by_claim_id is called first
        mock_repos["truth_repo"].get_record_by_claim_id.return_value = mock_record
        mock_repos["truth_repo"].get_record.return_value = None
        mock_repos["truth_repo"].list_events.return_value = [
            MockEvent(
                previous_state=MockState("PENDING"),
                new_state=MockState("UNDER_REVIEW"),
                reason="Initial review",
                decision_id="dec-001",
            ),
            MockEvent(
                previous_state=MockState("UNDER_REVIEW"),
                new_state=MockState("PROMOTED"),
                reason="Verified",
                decision_id="dec-002",
            ),
        ]
        mock_repos["decision_repo"].get_by_claim.return_value = []

        response = client.get("/api/truth/claim-001/twin")

        assert response.status_code == 200
        data = response.json()
        assert len(data["state_history"]) == 2
        assert data["state_history"][0]["to_state"] == "UNDER_REVIEW"
        assert data["state_history"][1]["to_state"] == "PROMOTED"


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
class TestDecisionInspectEndpoint:
    """Tests for GET /api/truth/decision/{decision_id}/inspect endpoint."""

    @pytest.fixture
    def mock_repos(self):
        """Create mock repositories."""
        with patch("app.api.truth_routes.TruthRepository") as mock_truth_repo, \
             patch("app.api.truth_routes.DecisionBlockRepository") as mock_decision_repo:

            truth_instance = MagicMock()
            decision_instance = MagicMock()

            mock_truth_repo.return_value = truth_instance
            mock_decision_repo.return_value = decision_instance

            yield {
                "truth_repo": truth_instance,
                "decision_repo": decision_instance,
            }

    @pytest.fixture
    def app(self, mock_repos):
        """Create test FastAPI app."""
        from app.api.truth_routes import router

        app = FastAPI()
        app.include_router(router)
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    def test_inspect_decision_found(self, client, mock_repos):
        """Test inspecting a decision that exists."""
        mock_repos["decision_repo"].get_by_decision.return_value = {
            "id": "block-001",
            "decision_id": "dec-001",
            "claim_id": "claim-001",
            "domain": "saude",
            "gate": "G23",
            "decision_type": "PROMOTE",
            "initial_state": "UNDER_REVIEW",
            "final_state": "PROMOTED",
            "created_at": "2025-01-01T12:00:00Z",
            "policy_name": "saude_v2",
            "policy_version": "2.0.0",
            "committee_summary": {"votes": 3},
            "invariants_checked": {"I1": True},
            "evidence_refs": ["ev-001"],
            "references": {"guias": ["G1"]},
            "latency_ms": 45,
        }

        response = client.get("/api/truth/decision/dec-001/inspect")

        assert response.status_code == 200
        data = response.json()
        assert data["decision_id"] == "dec-001"
        assert data["gate"] == "G23"
        assert data["decision_type"] == "PROMOTE"
        assert data["policy_name"] == "saude_v2"
        assert data["latency_ms"] == 45
        assert "_latency_ms" in data
        assert data["provenance"]["source"] == "decision_block"

    def test_inspect_decision_by_block_id(self, client, mock_repos):
        """Test inspecting by block ID when decision ID not found."""
        mock_repos["decision_repo"].get_by_decision.return_value = None
        mock_repos["decision_repo"].get.return_value = {
            "id": "block-002",
            "decision_id": "dec-002",
            "claim_id": "claim-002",
            "domain": "politica",
            "gate": "G20",
            "decision_type": "ACCEPT",
            "initial_state": "PENDING",
            "final_state": "UNDER_REVIEW",
            "created_at": "2025-01-01T00:00:00Z",
        }

        response = client.get("/api/truth/decision/block-002/inspect")

        assert response.status_code == 200
        data = response.json()
        assert data["block_id"] == "block-002"

    def test_inspect_decision_not_found(self, client, mock_repos):
        """Test inspecting a decision that doesn't exist."""
        mock_repos["decision_repo"].get_by_decision.return_value = None
        mock_repos["decision_repo"].get.return_value = None

        response = client.get("/api/truth/decision/nonexistent/inspect")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
class TestTimelineEndpoint:
    """Tests for GET /api/truth/{claim_id}/timeline endpoint."""

    @pytest.fixture
    def mock_repos(self):
        """Create mock repositories."""
        with patch("app.api.truth_routes.TruthRepository") as mock_truth_repo, \
             patch("app.api.truth_routes.DecisionBlockRepository") as mock_decision_repo:

            truth_instance = MagicMock()
            decision_instance = MagicMock()

            mock_truth_repo.return_value = truth_instance
            mock_decision_repo.return_value = decision_instance

            yield {
                "truth_repo": truth_instance,
                "decision_repo": decision_instance,
            }

    @pytest.fixture
    def app(self, mock_repos):
        """Create test FastAPI app."""
        from app.api.truth_routes import router

        app = FastAPI()
        app.include_router(router)
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    def test_get_timeline(self, client, mock_repos):
        """Test getting decision timeline."""
        mock_repos["decision_repo"].get_by_claim.return_value = [
            {
                "id": "block-001",
                "decision_id": "dec-001",
                "gate": "G20",
                "decision_type": "ACCEPT",
                "initial_state": "PENDING",
                "final_state": "UNDER_REVIEW",
                "created_at": "2025-01-01T00:00:00Z",
                "latency_ms": 30,
            },
            {
                "id": "block-002",
                "decision_id": "dec-002",
                "gate": "G23",
                "decision_type": "PROMOTE",
                "initial_state": "UNDER_REVIEW",
                "final_state": "PROMOTED",
                "created_at": "2025-01-01T12:00:00Z",
                "latency_ms": 50,
            },
        ]

        response = client.get("/api/truth/claim-001/timeline")

        assert response.status_code == 200
        data = response.json()
        assert data["claim_id"] == "claim-001"
        assert data["count"] == 2
        assert len(data["timeline"]) == 2
        assert data["timeline"][0]["gate"] == "G20"
        assert data["timeline"][1]["gate"] == "G23"
        assert "_latency_ms" in data

    def test_get_timeline_empty(self, client, mock_repos):
        """Test getting empty timeline."""
        mock_repos["decision_repo"].get_by_claim.return_value = []

        response = client.get("/api/truth/claim-no-decisions/timeline")

        assert response.status_code == 200
        data = response.json()
        assert data["claim_id"] == "claim-no-decisions"
        assert data["count"] == 0
        assert data["timeline"] == []

    def test_get_timeline_with_limit(self, client, mock_repos):
        """Test getting timeline with limit parameter."""
        # Generate 100 blocks
        blocks = [
            {
                "id": f"block-{i:03d}",
                "decision_id": f"dec-{i:03d}",
                "gate": "G20",
                "decision_type": "ACCEPT",
                "initial_state": "PENDING",
                "final_state": "UNDER_REVIEW",
                "created_at": f"2025-01-{(i % 28) + 1:02d}T00:00:00Z",
                "latency_ms": 30,
            }
            for i in range(100)
        ]
        mock_repos["decision_repo"].get_by_claim.return_value = blocks

        response = client.get("/api/truth/claim-001/timeline?limit=10")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 10
        assert len(data["timeline"]) == 10


class TestBuildFunctions:
    """Tests for build_truth_twin_response and build_decision_inspect_response."""

    def test_build_truth_twin_response_import(self):
        """Test that build function is importable."""
        from app.api.truth_schemas import build_truth_twin_response
        assert build_truth_twin_response is not None

    def test_build_decision_inspect_response_import(self):
        """Test that build function is importable."""
        from app.api.truth_schemas import build_decision_inspect_response
        assert build_decision_inspect_response is not None

    def test_build_truth_twin_has_provenance(self):
        """Test that built response has provenance when blocks exist."""
        from app.api.truth_schemas import build_truth_twin_response

        record = {
            "claim_id": "claim-001",
            "domain": "saude",
            "current_state": "PROMOTED",
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-02T00:00:00Z",
        }
        blocks = [
            {
                "id": "block-001",
                "decision_id": "dec-001",
                "gate": "G23",
                "decision_type": "PROMOTE",
                "initial_state": "UNDER_REVIEW",
                "final_state": "PROMOTED",
                "created_at": "2025-01-02T00:00:00Z",
                "policy_version": "1.0",
                "policy_name": "saude_v1",
                "evidence_refs": ["ev-001"],
                "references": {"guias": ["G1"]},
            }
        ]

        result = build_truth_twin_response(record, blocks, [])

        assert result.has_valid_provenance() is True
        assert result.provenance.source == "decision_block"
        assert result.provenance.policy_name == "saude_v1"

    def test_build_decision_inspect_has_provenance(self):
        """Test that built inspect response has provenance."""
        from app.api.truth_schemas import build_decision_inspect_response

        block = {
            "id": "block-001",
            "decision_id": "dec-001",
            "claim_id": "claim-001",
            "domain": "saude",
            "gate": "G23",
            "decision_type": "PROMOTE",
            "initial_state": "UNDER_REVIEW",
            "final_state": "PROMOTED",
            "created_at": "2025-01-02T00:00:00Z",
            "policy_version": "2.0",
            "policy_name": "saude_v2",
            "evidence_refs": ["ev-001", "ev-002"],
            "references": {"pilares": ["P1"]},
        }

        result = build_decision_inspect_response(block)

        assert result.has_valid_provenance() is True
        assert result.provenance.source == "decision_block"
        assert result.provenance.policy_version == "2.0"
        assert result.provenance.evidence_refs == ["ev-001", "ev-002"]
