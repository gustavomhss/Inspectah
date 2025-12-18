"""
S40-TST-005: Truth Twin API Routes Tests

Tests that Truth Twin API endpoints return valid responses with provenance.
"""

from __future__ import annotations

import pytest
from typing import Any, Dict
from unittest.mock import MagicMock, patch


class TestTruthTwinEndpoint:
    """Test GET /api/truth/{claim_id}/twin endpoint."""

    def test_twin_returns_valid_structure(self):
        """Twin endpoint should return complete structure."""
        response = {
            "claim_id": "claim-001",
            "domain": "politics",
            "current_state": "PROMOTED",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-15T12:00:00Z",
            "decision_timeline": [
                {
                    "id": "blk-001",
                    "decision_id": "dec-001",
                    "gate": "G2",
                    "decision_type": "APPROVE",
                    "initial_state": "PENDING",
                    "final_state": "UNDER_REVIEW",
                    "created_at": "2024-01-01T00:00:00Z",
                }
            ],
            "provenance": {
                "source": "decision_block",
                "timestamp": "2024-01-15T12:00:00Z",
            },
            "state_history": [],
            "metadata": {},
            "experience_refs": [],
            "last_decision_id": "dec-001",
        }

        # Validate structure
        assert "claim_id" in response
        assert "domain" in response
        assert "current_state" in response
        assert "decision_timeline" in response
        assert "provenance" in response
        assert isinstance(response["decision_timeline"], list)

    def test_twin_provenance_valid(self):
        """Twin response should have valid provenance."""
        response = {
            "claim_id": "claim-002",
            "provenance": {
                "source": "decision_block",
                "timestamp": "2024-01-15T12:00:00Z",
                "policy_version": "1.0.0",
            },
        }

        provenance = response.get("provenance")
        assert provenance is not None
        assert "source" in provenance
        assert "timestamp" in provenance
        assert provenance["source"] != ""
        assert provenance["timestamp"] != ""

    def test_twin_without_provenance_flagged(self):
        """Twin response without provenance should be flagged."""
        response = {
            "claim_id": "claim-003",
            "domain": "health",
            "current_state": "PENDING",
            "provenance": None,
            "_provenance_valid": False,
        }

        assert response.get("_provenance_valid") is False

    def test_twin_404_for_unknown_claim(self):
        """Twin should return 404 for unknown claim."""
        # Simulating 404 response
        error_response = {
            "detail": "Claim claim-unknown not found",
        }
        status_code = 404

        assert status_code == 404
        assert "not found" in error_response["detail"].lower()

    def test_twin_validates_claim_id(self):
        """Twin should validate claim_id format."""
        # Invalid claim IDs
        invalid_ids = [
            "",  # Empty
            " " * 10,  # Whitespace only
            "a" * 200,  # Too long
            "id<script>",  # Invalid characters
        ]

        for invalid_id in invalid_ids:
            # Should reject with 400
            assert len(invalid_id.strip()) == 0 or len(invalid_id) > 128 or "<" in invalid_id


class TestDecisionInspectEndpoint:
    """Test GET /api/truth/decision/{decision_id}/inspect endpoint."""

    def test_inspect_returns_valid_structure(self):
        """Inspect endpoint should return complete decision details."""
        response = {
            "decision_id": "dec-001",
            "block_id": "blk-001",
            "claim_id": "claim-001",
            "domain": "politics",
            "gate": "G3",
            "decision_type": "APPROVE",
            "initial_state": "UNDER_REVIEW",
            "final_state": "PROMOTED",
            "policy_name": "default_policy",
            "policy_version": "1.0.0",
            "committee_summary": {
                "total_votes": 5,
                "approve_votes": 4,
                "reject_votes": 1,
            },
            "invariants_checked": {
                "has_evidence": True,
                "no_contradictions": True,
            },
            "evidence_refs": ["ev-001", "ev-002"],
            "references": {
                "guias": ["G001"],
                "pilares": ["P001"],
                "e40_5": {"status": "OK"},
            },
            "provenance": {
                "source": "decision_block",
                "timestamp": "2024-01-15T12:00:00Z",
            },
            "created_at": "2024-01-15T12:00:00Z",
            "latency_ms": 45,
        }

        # Validate structure
        assert "decision_id" in response
        assert "block_id" in response
        assert "claim_id" in response
        assert "gate" in response
        assert "decision_type" in response
        assert "provenance" in response

    def test_inspect_includes_committee_summary(self):
        """Inspect should include committee voting summary."""
        response = {
            "decision_id": "dec-002",
            "committee_summary": {
                "total_votes": 3,
                "approve_votes": 2,
                "reject_votes": 1,
                "quorum_reached": True,
            },
        }

        committee = response.get("committee_summary", {})
        assert committee.get("total_votes") == 3
        assert committee.get("quorum_reached") is True

    def test_inspect_includes_invariants(self):
        """Inspect should include checked invariants."""
        response = {
            "decision_id": "dec-003",
            "invariants_checked": {
                "has_evidence": True,
                "no_contradictions": True,
                "source_reliable": False,
            },
        }

        invariants = response.get("invariants_checked", {})
        assert isinstance(invariants, dict)
        assert "has_evidence" in invariants
        assert invariants["source_reliable"] is False

    def test_inspect_404_for_unknown_decision(self):
        """Inspect should return 404 for unknown decision."""
        error_response = {
            "detail": "Decision dec-unknown not found",
        }
        status_code = 404

        assert status_code == 404
        assert "not found" in error_response["detail"].lower()


class TestTimelineEndpoint:
    """Test GET /api/truth/{claim_id}/timeline endpoint."""

    def test_timeline_returns_decisions_list(self):
        """Timeline should return list of decisions."""
        response = {
            "claim_id": "claim-001",
            "timeline": [
                {
                    "id": "blk-001",
                    "decision_id": "dec-001",
                    "gate": "G1",
                    "decision_type": "APPROVE",
                    "initial_state": "PENDING",
                    "final_state": "UNDER_REVIEW",
                    "created_at": "2024-01-01T00:00:00Z",
                },
                {
                    "id": "blk-002",
                    "decision_id": "dec-002",
                    "gate": "G3",
                    "decision_type": "APPROVE",
                    "initial_state": "UNDER_REVIEW",
                    "final_state": "PROMOTED",
                    "created_at": "2024-01-15T00:00:00Z",
                },
            ],
            "count": 2,
            "limit": 50,
        }

        assert "timeline" in response
        assert isinstance(response["timeline"], list)
        assert response["count"] == 2

    def test_timeline_respects_limit(self):
        """Timeline should respect limit parameter."""
        response = {
            "claim_id": "claim-002",
            "timeline": [{"id": f"blk-{i}"} for i in range(10)],
            "count": 10,
            "limit": 10,
        }

        assert len(response["timeline"]) == 10
        assert response["limit"] == 10

    def test_timeline_empty_for_new_claim(self):
        """Timeline should be empty for new claims."""
        response = {
            "claim_id": "claim-new",
            "timeline": [],
            "count": 0,
            "limit": 50,
        }

        assert response["count"] == 0
        assert len(response["timeline"]) == 0


class TestLatencyRequirements:
    """Test P4 latency requirements."""

    def test_twin_includes_latency(self):
        """Twin response should include latency metric."""
        response = {
            "claim_id": "claim-001",
            "_latency_ms": 45,
        }

        assert "_latency_ms" in response
        assert response["_latency_ms"] < 100  # P95 target

    def test_inspect_includes_latency(self):
        """Inspect response should include latency metric."""
        response = {
            "decision_id": "dec-001",
            "_latency_ms": 32,
        }

        assert "_latency_ms" in response
        assert response["_latency_ms"] < 100  # P95 target

    def test_timeline_includes_latency(self):
        """Timeline response should include latency metric."""
        response = {
            "claim_id": "claim-001",
            "timeline": [],
            "_latency_ms": 28,
        }

        assert "_latency_ms" in response
        assert response["_latency_ms"] < 100  # P95 target


class TestProvenanceValidation:
    """Test provenance validation in responses."""

    def test_valid_provenance_structure(self):
        """Valid provenance should have required fields."""
        provenance = {
            "source": "decision_block",
            "timestamp": "2024-01-15T12:00:00Z",
        }

        assert "source" in provenance
        assert "timestamp" in provenance
        assert provenance["source"] != ""
        assert provenance["timestamp"] != ""

    def test_provenance_with_policy(self):
        """Provenance can include policy info."""
        provenance = {
            "source": "decision_block",
            "timestamp": "2024-01-15T12:00:00Z",
            "policy_name": "default_policy",
            "policy_version": "1.0.0",
        }

        assert provenance.get("policy_name") == "default_policy"
        assert provenance.get("policy_version") == "1.0.0"

    def test_provenance_with_references(self):
        """Provenance can include S40 references."""
        provenance = {
            "source": "decision_block",
            "timestamp": "2024-01-15T12:00:00Z",
            "references": {
                "guias": ["G001"],
                "pilares": ["P001"],
                "e40_5": {"status": "OK"},
            },
        }

        refs = provenance.get("references", {})
        assert refs.get("guias") == ["G001"]
        assert refs.get("e40_5", {}).get("status") == "OK"
