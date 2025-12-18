"""
Tests for S40-BE-026: Truth Twin and Decision Inspector DTOs.

Tests for app/api/truth_schemas.py.
"""

from __future__ import annotations

import pytest
from datetime import datetime

from app.api.truth_schemas import (
    ProvenanceInfo,
    StateTransitionInfo,
    DecisionBlockSummary,
    TruthTwinResponse,
    DecisionInspectResponse,
    build_truth_twin_response,
    build_decision_inspect_response,
)


class TestProvenanceInfo:
    """Tests for ProvenanceInfo dataclass."""

    def test_create_provenance_basic(self):
        """Test creating basic provenance info."""
        prov = ProvenanceInfo(
            source="decision_block",
            timestamp="2025-01-01T00:00:00Z",
        )
        assert prov.source == "decision_block"
        assert prov.timestamp == "2025-01-01T00:00:00Z"
        assert prov.policy_version is None
        assert prov.policy_name is None
        assert prov.actor is None
        assert prov.evidence_refs == []
        assert prov.references is None

    def test_create_provenance_full(self):
        """Test creating provenance with all fields."""
        prov = ProvenanceInfo(
            source="guardian_flow",
            timestamp="2025-01-02T12:00:00Z",
            policy_version="2.0.0",
            policy_name="saude_verification",
            actor="system",
            evidence_refs=["ev-001", "ev-002"],
            references={"guias": ["G1", "G2"], "pilares": ["P1"]},
        )
        assert prov.source == "guardian_flow"
        assert prov.policy_version == "2.0.0"
        assert prov.policy_name == "saude_verification"
        assert prov.actor == "system"
        assert prov.evidence_refs == ["ev-001", "ev-002"]
        assert prov.references["guias"] == ["G1", "G2"]

    def test_provenance_to_dict(self):
        """Test provenance to_dict serialization."""
        prov = ProvenanceInfo(
            source="test",
            timestamp="2025-01-01T00:00:00Z",
            policy_version="1.0",
            evidence_refs=["ref1"],
        )
        result = prov.to_dict()

        assert result["source"] == "test"
        assert result["timestamp"] == "2025-01-01T00:00:00Z"
        assert result["policy_version"] == "1.0"
        assert result["evidence_refs"] == ["ref1"]
        assert result["policy_name"] is None
        assert result["actor"] is None

    def test_provenance_to_dict_with_references(self):
        """Test provenance to_dict with references."""
        prov = ProvenanceInfo(
            source="test",
            timestamp="2025-01-01T00:00:00Z",
            references={"e40_5": {"status": "OK"}},
        )
        result = prov.to_dict()
        assert result["references"] == {"e40_5": {"status": "OK"}}


class TestStateTransitionInfo:
    """Tests for StateTransitionInfo dataclass."""

    def test_create_state_transition(self):
        """Test creating state transition info."""
        trans = StateTransitionInfo(
            from_state="PENDING",
            to_state="UNDER_REVIEW",
            reason="Initial submission",
            timestamp="2025-01-01T00:00:00Z",
        )
        assert trans.from_state == "PENDING"
        assert trans.to_state == "UNDER_REVIEW"
        assert trans.reason == "Initial submission"
        assert trans.decision_id is None

    def test_state_transition_with_decision_id(self):
        """Test state transition with decision ID."""
        trans = StateTransitionInfo(
            from_state="UNDER_REVIEW",
            to_state="PROMOTED",
            reason="Verified",
            timestamp="2025-01-01T12:00:00Z",
            decision_id="dec-123",
        )
        assert trans.decision_id == "dec-123"

    def test_state_transition_to_dict(self):
        """Test state transition to_dict."""
        trans = StateTransitionInfo(
            from_state="A",
            to_state="B",
            reason="test",
            timestamp="2025-01-01T00:00:00Z",
            decision_id="dec-456",
        )
        result = trans.to_dict()

        assert result["from_state"] == "A"
        assert result["to_state"] == "B"
        assert result["reason"] == "test"
        assert result["timestamp"] == "2025-01-01T00:00:00Z"
        assert result["decision_id"] == "dec-456"


class TestDecisionBlockSummary:
    """Tests for DecisionBlockSummary dataclass."""

    def test_create_decision_summary(self):
        """Test creating decision block summary."""
        summary = DecisionBlockSummary(
            id="block-001",
            decision_id="dec-001",
            gate="G20",
            decision_type="ACCEPT",
            initial_state="PENDING",
            final_state="UNDER_REVIEW",
            created_at="2025-01-01T00:00:00Z",
        )
        assert summary.id == "block-001"
        assert summary.decision_id == "dec-001"
        assert summary.gate == "G20"
        assert summary.decision_type == "ACCEPT"
        assert summary.latency_ms is None
        assert summary.policy_name is None

    def test_decision_summary_full(self):
        """Test decision summary with all fields."""
        summary = DecisionBlockSummary(
            id="block-002",
            decision_id="dec-002",
            gate="G23",
            decision_type="PROMOTE",
            initial_state="UNDER_REVIEW",
            final_state="PROMOTED",
            created_at="2025-01-01T12:00:00Z",
            latency_ms=45,
            policy_name="saude_v2",
            policy_version="2.1.0",
        )
        assert summary.latency_ms == 45
        assert summary.policy_name == "saude_v2"
        assert summary.policy_version == "2.1.0"

    def test_decision_summary_to_dict(self):
        """Test decision summary to_dict."""
        summary = DecisionBlockSummary(
            id="block-003",
            decision_id="dec-003",
            gate="G22",
            decision_type="REJECT",
            initial_state="UNDER_REVIEW",
            final_state="REJECTED",
            created_at="2025-01-01T00:00:00Z",
            latency_ms=100,
        )
        result = summary.to_dict()

        assert result["id"] == "block-003"
        assert result["decision_id"] == "dec-003"
        assert result["gate"] == "G22"
        assert result["latency_ms"] == 100
        assert result["policy_name"] is None


class TestTruthTwinResponse:
    """Tests for TruthTwinResponse dataclass."""

    def test_create_truth_twin_minimal(self):
        """Test creating minimal truth twin response."""
        twin = TruthTwinResponse(
            claim_id="claim-001",
            domain="saude",
            current_state="PENDING",
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
        )
        assert twin.claim_id == "claim-001"
        assert twin.domain == "saude"
        assert twin.current_state == "PENDING"
        assert twin.decision_timeline == []
        assert twin.provenance is None
        assert twin.state_history == []
        assert twin.metadata == {}
        assert twin.experience_refs == []
        assert twin.last_decision_id is None

    def test_create_truth_twin_full(self):
        """Test creating full truth twin response."""
        prov = ProvenanceInfo(source="test", timestamp="2025-01-01T00:00:00Z")
        timeline = [DecisionBlockSummary(
            id="b1", decision_id="d1", gate="G20", decision_type="ACCEPT",
            initial_state="PENDING", final_state="UNDER_REVIEW", created_at="2025-01-01T00:00:00Z"
        )]
        history = [StateTransitionInfo(
            from_state="PENDING", to_state="UNDER_REVIEW", reason="test", timestamp="2025-01-01T00:00:00Z"
        )]

        twin = TruthTwinResponse(
            claim_id="claim-002",
            domain="politica",
            current_state="PROMOTED",
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-02T00:00:00Z",
            decision_timeline=timeline,
            provenance=prov,
            state_history=history,
            metadata={"key": "value"},
            experience_refs=["exp-001"],
            last_decision_id="dec-final",
        )

        assert len(twin.decision_timeline) == 1
        assert twin.provenance is not None
        assert len(twin.state_history) == 1
        assert twin.metadata == {"key": "value"}
        assert twin.experience_refs == ["exp-001"]
        assert twin.last_decision_id == "dec-final"

    def test_truth_twin_to_dict(self):
        """Test truth twin to_dict serialization."""
        prov = ProvenanceInfo(source="test", timestamp="2025-01-01T00:00:00Z")
        twin = TruthTwinResponse(
            claim_id="claim-003",
            domain="saude",
            current_state="PROMOTED",
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-02T00:00:00Z",
            provenance=prov,
        )
        result = twin.to_dict()

        assert result["claim_id"] == "claim-003"
        assert result["domain"] == "saude"
        assert result["current_state"] == "PROMOTED"
        assert result["provenance"]["source"] == "test"
        assert result["decision_timeline"] == []

    def test_truth_twin_to_dict_no_provenance(self):
        """Test truth twin to_dict without provenance."""
        twin = TruthTwinResponse(
            claim_id="claim-004",
            domain="saude",
            current_state="PENDING",
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
        )
        result = twin.to_dict()
        assert result["provenance"] is None

    def test_has_valid_provenance_true(self):
        """Test has_valid_provenance returns True."""
        prov = ProvenanceInfo(source="decision_block", timestamp="2025-01-01T00:00:00Z")
        twin = TruthTwinResponse(
            claim_id="claim-005",
            domain="saude",
            current_state="PENDING",
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
            provenance=prov,
        )
        assert twin.has_valid_provenance() is True

    def test_has_valid_provenance_false_no_provenance(self):
        """Test has_valid_provenance returns False when no provenance."""
        twin = TruthTwinResponse(
            claim_id="claim-006",
            domain="saude",
            current_state="PENDING",
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
        )
        assert twin.has_valid_provenance() is False

    def test_has_valid_provenance_false_empty_source(self):
        """Test has_valid_provenance returns False when source is empty."""
        prov = ProvenanceInfo(source="", timestamp="2025-01-01T00:00:00Z")
        twin = TruthTwinResponse(
            claim_id="claim-007",
            domain="saude",
            current_state="PENDING",
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
            provenance=prov,
        )
        assert twin.has_valid_provenance() is False


class TestDecisionInspectResponse:
    """Tests for DecisionInspectResponse dataclass."""

    def test_create_decision_inspect_minimal(self):
        """Test creating minimal decision inspect response."""
        inspect = DecisionInspectResponse(
            decision_id="dec-001",
            block_id="block-001",
            claim_id="claim-001",
            domain="saude",
            gate="G20",
            decision_type="ACCEPT",
            initial_state="PENDING",
            final_state="UNDER_REVIEW",
        )
        assert inspect.decision_id == "dec-001"
        assert inspect.block_id == "block-001"
        assert inspect.claim_id == "claim-001"
        assert inspect.policy_name is None
        assert inspect.committee_summary == {}
        assert inspect.invariants_checked == {}
        assert inspect.evidence_refs == []
        assert inspect.references is None
        assert inspect.provenance is None

    def test_create_decision_inspect_full(self):
        """Test creating full decision inspect response."""
        prov = ProvenanceInfo(source="test", timestamp="2025-01-01T00:00:00Z")
        inspect = DecisionInspectResponse(
            decision_id="dec-002",
            block_id="block-002",
            claim_id="claim-002",
            domain="politica",
            gate="G23",
            decision_type="PROMOTE",
            initial_state="UNDER_REVIEW",
            final_state="PROMOTED",
            policy_name="politica_v3",
            policy_version="3.0.0",
            committee_summary={"votes": 3, "consensus": True},
            invariants_checked={"I1": True, "I2": True},
            evidence_refs=["ev-001", "ev-002"],
            references={"guias": ["G1"], "pilares": ["P1"], "e40_5": {"status": "OK"}},
            state_transition={"from": "UNDER_REVIEW", "to": "PROMOTED"},
            experience_refs=["exp-001"],
            created_at="2025-01-01T12:00:00Z",
            latency_ms=75,
            provenance=prov,
        )

        assert inspect.policy_name == "politica_v3"
        assert inspect.policy_version == "3.0.0"
        assert inspect.committee_summary["votes"] == 3
        assert inspect.invariants_checked["I1"] is True
        assert len(inspect.evidence_refs) == 2
        assert inspect.references["e40_5"]["status"] == "OK"
        assert inspect.latency_ms == 75
        assert inspect.provenance is not None

    def test_decision_inspect_to_dict(self):
        """Test decision inspect to_dict."""
        prov = ProvenanceInfo(source="block", timestamp="2025-01-01T00:00:00Z")
        inspect = DecisionInspectResponse(
            decision_id="dec-003",
            block_id="block-003",
            claim_id="claim-003",
            domain="saude",
            gate="G22",
            decision_type="REJECT",
            initial_state="UNDER_REVIEW",
            final_state="REJECTED",
            latency_ms=50,
            provenance=prov,
        )
        result = inspect.to_dict()

        assert result["decision_id"] == "dec-003"
        assert result["block_id"] == "block-003"
        assert result["gate"] == "G22"
        assert result["latency_ms"] == 50
        assert result["provenance"]["source"] == "block"

    def test_decision_inspect_to_dict_no_provenance(self):
        """Test decision inspect to_dict without provenance."""
        inspect = DecisionInspectResponse(
            decision_id="dec-004",
            block_id="block-004",
            claim_id="claim-004",
            domain="saude",
            gate="G20",
            decision_type="ACCEPT",
            initial_state="PENDING",
            final_state="UNDER_REVIEW",
        )
        result = inspect.to_dict()
        assert result["provenance"] is None

    def test_has_valid_provenance_true(self):
        """Test has_valid_provenance returns True."""
        prov = ProvenanceInfo(source="decision_block", timestamp="2025-01-01T00:00:00Z")
        inspect = DecisionInspectResponse(
            decision_id="dec-005",
            block_id="block-005",
            claim_id="claim-005",
            domain="saude",
            gate="G20",
            decision_type="ACCEPT",
            initial_state="PENDING",
            final_state="UNDER_REVIEW",
            provenance=prov,
        )
        assert inspect.has_valid_provenance() is True

    def test_has_valid_provenance_false(self):
        """Test has_valid_provenance returns False."""
        inspect = DecisionInspectResponse(
            decision_id="dec-006",
            block_id="block-006",
            claim_id="claim-006",
            domain="saude",
            gate="G20",
            decision_type="ACCEPT",
            initial_state="PENDING",
            final_state="UNDER_REVIEW",
        )
        assert inspect.has_valid_provenance() is False


class TestBuildTruthTwinResponse:
    """Tests for build_truth_twin_response function."""

    def test_build_with_no_blocks_or_events(self):
        """Test building response with no decision blocks or events."""
        record = {
            "claim_id": "claim-001",
            "domain": "saude",
            "current_state": "PENDING",
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z",
            "metadata": {},
            "last_decision_id": None,
        }

        result = build_truth_twin_response(record, [], [])

        assert result.claim_id == "claim-001"
        assert result.domain == "saude"
        assert result.current_state == "PENDING"
        assert result.decision_timeline == []
        assert result.provenance is None
        assert result.state_history == []

    def test_build_with_blocks_and_events(self):
        """Test building response with decision blocks and events."""
        record = {
            "claim_id": "claim-002",
            "domain": "politica",
            "current_state": "PROMOTED",
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-02T00:00:00Z",
            "metadata": {"key": "val"},
            "last_decision_id": "dec-002",
        }
        blocks = [
            {
                "id": "block-001",
                "decision_id": "dec-001",
                "gate": "G20",
                "decision_type": "ACCEPT",
                "initial_state": "PENDING",
                "final_state": "UNDER_REVIEW",
                "created_at": "2025-01-01T06:00:00Z",
                "latency_ms": 30,
                "policy_name": "politica_v1",
                "policy_version": "1.0.0",
                "evidence_refs": ["ev-001"],
                "references": {"guias": ["G1"]},
                "experience_refs": [],
            },
            {
                "id": "block-002",
                "decision_id": "dec-002",
                "gate": "G23",
                "decision_type": "PROMOTE",
                "initial_state": "UNDER_REVIEW",
                "final_state": "PROMOTED",
                "created_at": "2025-01-02T00:00:00Z",
                "latency_ms": 50,
                "policy_name": "politica_v1",
                "policy_version": "1.0.0",
                "evidence_refs": ["ev-002"],
                "references": {"guias": ["G2"]},
                "experience_refs": ["exp-001"],
            },
        ]
        events = [
            {
                "previous_state": "PENDING",
                "new_state": "UNDER_REVIEW",
                "reason": "Initial",
                "created_at": "2025-01-01T06:00:00Z",
                "decision_id": "dec-001",
            },
            {
                "previous_state": "UNDER_REVIEW",
                "new_state": "PROMOTED",
                "reason": "Verified",
                "created_at": "2025-01-02T00:00:00Z",
                "decision_id": "dec-002",
            },
        ]

        result = build_truth_twin_response(record, blocks, events)

        assert result.claim_id == "claim-002"
        assert result.domain == "politica"
        assert result.current_state == "PROMOTED"
        assert len(result.decision_timeline) == 2
        assert result.decision_timeline[0].gate == "G20"
        assert result.decision_timeline[1].gate == "G23"
        assert result.provenance is not None
        assert result.provenance.source == "decision_block"
        assert len(result.state_history) == 2
        assert result.state_history[0].to_state == "UNDER_REVIEW"
        assert result.state_history[1].to_state == "PROMOTED"
        assert result.experience_refs == ["exp-001"]
        assert result.last_decision_id == "dec-002"

    def test_build_with_id_fallback(self):
        """Test building response when claim_id is missing but id is present."""
        record = {
            "id": "fallback-id",
            "domain": "saude",
            "current_state": "PENDING",
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z",
        }

        result = build_truth_twin_response(record, [], [])
        assert result.claim_id == "fallback-id"

    def test_build_provenance_from_last_block(self):
        """Test that provenance is built from the last decision block."""
        record = {
            "claim_id": "claim-003",
            "domain": "saude",
            "current_state": "PROMOTED",
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-02T00:00:00Z",
        }
        blocks = [
            {
                "id": "block-001",
                "decision_id": "dec-001",
                "gate": "G20",
                "decision_type": "ACCEPT",
                "initial_state": "PENDING",
                "final_state": "UNDER_REVIEW",
                "created_at": "2025-01-01T06:00:00Z",
                "policy_version": "1.0",
                "policy_name": "first_policy",
                "evidence_refs": ["ev-first"],
                "references": None,
            },
            {
                "id": "block-002",
                "decision_id": "dec-002",
                "gate": "G23",
                "decision_type": "PROMOTE",
                "initial_state": "UNDER_REVIEW",
                "final_state": "PROMOTED",
                "created_at": "2025-01-02T00:00:00Z",
                "policy_version": "2.0",
                "policy_name": "last_policy",
                "evidence_refs": ["ev-last"],
                "references": {"guias": ["G1"]},
            },
        ]

        result = build_truth_twin_response(record, blocks, [])

        assert result.provenance.policy_version == "2.0"
        assert result.provenance.policy_name == "last_policy"
        assert result.provenance.evidence_refs == ["ev-last"]
        assert result.provenance.references == {"guias": ["G1"]}


class TestBuildDecisionInspectResponse:
    """Tests for build_decision_inspect_response function."""

    def test_build_minimal_block(self):
        """Test building response from minimal block."""
        block = {
            "id": "block-001",
            "decision_id": "dec-001",
            "claim_id": "claim-001",
            "domain": "saude",
            "gate": "G20",
            "decision_type": "ACCEPT",
            "initial_state": "PENDING",
            "final_state": "UNDER_REVIEW",
            "created_at": "2025-01-01T00:00:00Z",
        }

        result = build_decision_inspect_response(block)

        assert result.decision_id == "dec-001"
        assert result.block_id == "block-001"
        assert result.claim_id == "claim-001"
        assert result.domain == "saude"
        assert result.gate == "G20"
        assert result.decision_type == "ACCEPT"
        assert result.initial_state == "PENDING"
        assert result.final_state == "UNDER_REVIEW"
        assert result.provenance is not None
        assert result.provenance.source == "decision_block"

    def test_build_full_block(self):
        """Test building response from full block."""
        block = {
            "id": "block-002",
            "decision_id": "dec-002",
            "claim_id": "claim-002",
            "domain": "politica",
            "gate": "G23",
            "decision_type": "PROMOTE",
            "initial_state": "UNDER_REVIEW",
            "final_state": "PROMOTED",
            "created_at": "2025-01-02T12:00:00Z",
            "policy_name": "politica_v3",
            "policy_version": "3.0.0",
            "committee_summary": {"votes": 5, "consensus": True},
            "invariants_checked": {"I1": True, "I2": True, "I3": False},
            "evidence_refs": ["ev-001", "ev-002", "ev-003"],
            "references": {
                "guias": ["G1", "G2"],
                "pilares": ["P1"],
                "e40_5": {"status": "OK", "checked_at": "2025-01-02T11:59:00Z"},
            },
            "state_transition": {"from": "UNDER_REVIEW", "to": "PROMOTED", "reason": "Verified"},
            "experience_refs": ["exp-001", "exp-002"],
            "latency_ms": 85,
        }

        result = build_decision_inspect_response(block)

        assert result.decision_id == "dec-002"
        assert result.policy_name == "politica_v3"
        assert result.policy_version == "3.0.0"
        assert result.committee_summary["votes"] == 5
        assert result.invariants_checked["I3"] is False
        assert len(result.evidence_refs) == 3
        assert result.references["e40_5"]["status"] == "OK"
        assert result.state_transition["reason"] == "Verified"
        assert len(result.experience_refs) == 2
        assert result.latency_ms == 85
        assert result.provenance.policy_name == "politica_v3"

    def test_build_block_empty_fields(self):
        """Test building response when optional fields are empty."""
        block = {
            "id": "",
            "decision_id": "",
            "claim_id": "",
            "domain": "",
            "gate": "",
            "decision_type": "",
            "initial_state": "",
            "final_state": "",
            "created_at": "",
        }

        result = build_decision_inspect_response(block)

        assert result.decision_id == ""
        assert result.block_id == ""
        assert result.committee_summary == {}
        assert result.invariants_checked == {}
        assert result.evidence_refs == []
        assert result.references is None
        assert result.provenance.timestamp == ""


class TestNewMethods:
    """Tests for new helper methods added during refinement."""

    def test_truth_twin_get_decision_count(self):
        """Test get_decision_count method."""
        twin = TruthTwinResponse(
            claim_id="c1", domain="saude", current_state="PROMOTED",
            created_at="", updated_at="",
            decision_timeline=[
                DecisionBlockSummary(id="b1", decision_id="d1", gate="G20",
                    decision_type="ACCEPT", initial_state="PENDING",
                    final_state="UNDER_REVIEW", created_at=""),
                DecisionBlockSummary(id="b2", decision_id="d2", gate="G23",
                    decision_type="PROMOTE", initial_state="UNDER_REVIEW",
                    final_state="PROMOTED", created_at=""),
            ]
        )
        assert twin.get_decision_count() == 2

    def test_truth_twin_get_decision_count_empty(self):
        """Test get_decision_count with no decisions."""
        twin = TruthTwinResponse(
            claim_id="c1", domain="saude", current_state="PENDING",
            created_at="", updated_at="",
        )
        assert twin.get_decision_count() == 0

    def test_truth_twin_get_last_decision(self):
        """Test get_last_decision method."""
        dec1 = DecisionBlockSummary(id="b1", decision_id="d1", gate="G20",
            decision_type="ACCEPT", initial_state="PENDING",
            final_state="UNDER_REVIEW", created_at="")
        dec2 = DecisionBlockSummary(id="b2", decision_id="d2", gate="G23",
            decision_type="PROMOTE", initial_state="UNDER_REVIEW",
            final_state="PROMOTED", created_at="")

        twin = TruthTwinResponse(
            claim_id="c1", domain="saude", current_state="PROMOTED",
            created_at="", updated_at="",
            decision_timeline=[dec1, dec2]
        )
        assert twin.get_last_decision() == dec2

    def test_truth_twin_get_last_decision_empty(self):
        """Test get_last_decision with no decisions."""
        twin = TruthTwinResponse(
            claim_id="c1", domain="saude", current_state="PENDING",
            created_at="", updated_at="",
        )
        assert twin.get_last_decision() is None

    def test_decision_inspect_is_state_changed_true(self):
        """Test is_state_changed when state changed."""
        inspect = DecisionInspectResponse(
            decision_id="d1", block_id="b1", claim_id="c1", domain="saude",
            gate="G23", decision_type="PROMOTE",
            initial_state="UNDER_REVIEW", final_state="PROMOTED"
        )
        assert inspect.is_state_changed() is True

    def test_decision_inspect_is_state_changed_false(self):
        """Test is_state_changed when state unchanged."""
        inspect = DecisionInspectResponse(
            decision_id="d1", block_id="b1", claim_id="c1", domain="saude",
            gate="G20", decision_type="HOLD",
            initial_state="PENDING", final_state="PENDING"
        )
        assert inspect.is_state_changed() is False

    def test_decision_inspect_get_invariant_violations(self):
        """Test get_invariant_violations method."""
        inspect = DecisionInspectResponse(
            decision_id="d1", block_id="b1", claim_id="c1", domain="saude",
            gate="G23", decision_type="REJECT",
            initial_state="UNDER_REVIEW", final_state="REJECTED",
            invariants_checked={"I1": True, "I2": False, "I3": True, "I4": False}
        )
        violations = inspect.get_invariant_violations()
        assert sorted(violations) == ["I2", "I4"]

    def test_decision_inspect_get_invariant_violations_none(self):
        """Test get_invariant_violations with no violations."""
        inspect = DecisionInspectResponse(
            decision_id="d1", block_id="b1", claim_id="c1", domain="saude",
            gate="G23", decision_type="PROMOTE",
            initial_state="UNDER_REVIEW", final_state="PROMOTED",
            invariants_checked={"I1": True, "I2": True}
        )
        assert inspect.get_invariant_violations() == []


class TestSafeHelpers:
    """Tests for _safe_list, _safe_dict, _safe_str functions."""

    def test_safe_list_with_none(self):
        """Test _safe_list with None input."""
        from app.api.truth_schemas import _safe_list
        assert _safe_list(None) == []

    def test_safe_list_with_list(self):
        """Test _safe_list with list input."""
        from app.api.truth_schemas import _safe_list
        original = [1, 2, 3]
        result = _safe_list(original)
        assert result == [1, 2, 3]
        assert result is not original  # Defensive copy

    def test_safe_list_with_default(self):
        """Test _safe_list with default value."""
        from app.api.truth_schemas import _safe_list
        assert _safe_list(None, default=["a"]) == ["a"]

    def test_safe_list_with_non_list(self):
        """Test _safe_list with non-list input."""
        from app.api.truth_schemas import _safe_list
        assert _safe_list("string") == []
        assert _safe_list(123) == []

    def test_safe_dict_with_none(self):
        """Test _safe_dict with None input."""
        from app.api.truth_schemas import _safe_dict
        assert _safe_dict(None) == {}

    def test_safe_dict_with_dict(self):
        """Test _safe_dict with dict input."""
        from app.api.truth_schemas import _safe_dict
        original = {"a": 1}
        result = _safe_dict(original)
        assert result == {"a": 1}
        assert result is not original  # Defensive copy

    def test_safe_dict_with_default(self):
        """Test _safe_dict with default value."""
        from app.api.truth_schemas import _safe_dict
        assert _safe_dict(None, default={"key": "val"}) == {"key": "val"}

    def test_safe_dict_with_non_dict(self):
        """Test _safe_dict with non-dict input."""
        from app.api.truth_schemas import _safe_dict
        assert _safe_dict("string") == {}
        assert _safe_dict([1, 2]) == {}

    def test_safe_str_with_none(self):
        """Test _safe_str with None input."""
        from app.api.truth_schemas import _safe_str
        assert _safe_str(None) == ""

    def test_safe_str_with_string(self):
        """Test _safe_str with string input."""
        from app.api.truth_schemas import _safe_str
        assert _safe_str("hello") == "hello"

    def test_safe_str_with_number(self):
        """Test _safe_str with number input."""
        from app.api.truth_schemas import _safe_str
        assert _safe_str(123) == "123"

    def test_safe_str_with_default(self):
        """Test _safe_str with default value."""
        from app.api.truth_schemas import _safe_str
        assert _safe_str(None, default="default") == "default"


class TestBuildInspectValidation:
    """Tests for build_decision_inspect_response validation."""

    def test_build_inspect_with_none_raises(self):
        """Test that None block raises ValueError."""
        with pytest.raises(ValueError, match="block cannot be None"):
            build_decision_inspect_response(None)

    def test_build_inspect_with_non_dict_raises(self):
        """Test that non-dict block raises ValueError."""
        with pytest.raises(ValueError, match="block must be a dict"):
            build_decision_inspect_response("not a dict")

        with pytest.raises(ValueError, match="block must be a dict"):
            build_decision_inspect_response([1, 2, 3])


class TestPostInit:
    """Tests for __post_init__ methods in dataclasses."""

    def test_provenance_info_post_init_none_evidence_refs(self):
        """Test ProvenanceInfo handles None evidence_refs."""
        prov = ProvenanceInfo(source="test", timestamp="", evidence_refs=None)
        assert prov.evidence_refs == []

    def test_truth_twin_post_init_none_fields(self):
        """Test TruthTwinResponse handles None list/dict fields."""
        twin = TruthTwinResponse(
            claim_id="c1", domain="saude", current_state="PENDING",
            created_at="", updated_at="",
            decision_timeline=None,
            state_history=None,
            metadata=None,
            experience_refs=None,
        )
        assert twin.decision_timeline == []
        assert twin.state_history == []
        assert twin.metadata == {}
        assert twin.experience_refs == []

    def test_decision_inspect_post_init_none_fields(self):
        """Test DecisionInspectResponse handles None list/dict fields."""
        inspect = DecisionInspectResponse(
            decision_id="d1", block_id="b1", claim_id="c1", domain="saude",
            gate="G20", decision_type="ACCEPT",
            initial_state="PENDING", final_state="UNDER_REVIEW",
            committee_summary=None,
            invariants_checked=None,
            evidence_refs=None,
            experience_refs=None,
        )
        assert inspect.committee_summary == {}
        assert inspect.invariants_checked == {}
        assert inspect.evidence_refs == []
        assert inspect.experience_refs == []


class TestDefensiveCopies:
    """Tests to verify defensive copies are made."""

    def test_to_dict_defensive_copy_metadata(self):
        """Test that to_dict returns defensive copy of metadata."""
        original_metadata = {"key": "value"}
        twin = TruthTwinResponse(
            claim_id="c1", domain="saude", current_state="PENDING",
            created_at="", updated_at="",
            metadata=original_metadata,
        )
        result = twin.to_dict()

        # Modifying the returned dict should not affect original
        result["metadata"]["new_key"] = "new_value"
        assert "new_key" not in twin.metadata

    def test_to_dict_defensive_copy_evidence_refs(self):
        """Test that to_dict returns defensive copy of evidence_refs."""
        original_refs = ["ev-001", "ev-002"]
        prov = ProvenanceInfo(source="test", timestamp="", evidence_refs=original_refs)
        result = prov.to_dict()

        # Modifying the returned list should not affect original
        result["evidence_refs"].append("ev-003")
        assert len(prov.evidence_refs) == 2


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_build_twin_response_missing_keys(self):
        """Test building twin response when keys are missing."""
        record = {}  # Empty record

        result = build_truth_twin_response(record, [], [])

        # Should handle missing keys gracefully
        assert result.claim_id == ""
        assert result.domain == ""
        assert result.current_state == ""

    def test_build_inspect_response_missing_keys(self):
        """Test building inspect response when keys are missing."""
        block = {}  # Empty block

        result = build_decision_inspect_response(block)

        # Should handle missing keys gracefully
        assert result.decision_id == ""
        assert result.block_id == ""
        assert result.domain == ""

    def test_timeline_with_none_values(self):
        """Test building timeline when block has None values."""
        record = {
            "claim_id": "claim-001",
            "domain": "saude",
            "current_state": "PENDING",
            "created_at": None,
            "updated_at": None,
        }
        blocks = [
            {
                "id": None,
                "decision_id": None,
                "gate": None,
                "decision_type": None,
                "initial_state": None,
                "final_state": None,
                "created_at": None,
                "latency_ms": None,
                "policy_name": None,
                "policy_version": None,
            }
        ]

        result = build_truth_twin_response(record, blocks, [])

        # Should convert None to empty strings using _safe_str
        assert len(result.decision_timeline) == 1
        assert result.decision_timeline[0].created_at == ""  # None becomes ""
        assert result.decision_timeline[0].id == ""
        assert result.decision_timeline[0].gate == ""

    def test_events_with_missing_optional_fields(self):
        """Test building state history when events have missing optional fields."""
        record = {
            "claim_id": "claim-001",
            "domain": "saude",
            "current_state": "UNDER_REVIEW",
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z",
        }
        events = [
            {
                "new_state": "UNDER_REVIEW",
                "reason": "Initial",
                "created_at": "2025-01-01T00:00:00Z",
                # previous_state and decision_id missing
            }
        ]

        result = build_truth_twin_response(record, [], events)

        assert len(result.state_history) == 1
        assert result.state_history[0].from_state == ""
        assert result.state_history[0].decision_id is None
