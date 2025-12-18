"""
Tests for ClaimGraph export functionality.

Tasks: S40-BE-011, S40-BE-013
"""

from datetime import datetime, timezone

import pytest

from app.claims.export import (
    ClaimExportItem,
    ClaimGraphExport,
    ClaimPrior,
    EvidenceItem,
    NOGOSignal,
    export_claimgraph_v1,
    ingest_claimgraph_export,
)
from app.claims.graph_models import ClaimNode, ClaimState, EdgeType, GraphEdge


class TestClaimPrior:
    """Tests for ClaimPrior dataclass."""

    def test_create_prior(self):
        """Test creating a prior."""
        prior = ClaimPrior(
            probability=0.8,
            confidence=0.9,
            source="model",
            model_version="v1.0",
        )

        assert prior.probability == 0.8
        assert prior.confidence == 0.9
        assert prior.source == "model"
        assert prior.model_version == "v1.0"

    def test_prior_to_dict(self):
        """Test converting prior to dict."""
        prior = ClaimPrior(
            probability=0.75,
            confidence=0.85,
            source="expert",
        )

        prior_dict = prior.to_dict()

        assert prior_dict["probability"] == 0.75
        assert prior_dict["confidence"] == 0.85
        assert prior_dict["source"] == "expert"
        assert "computed_at" in prior_dict


class TestEvidenceItem:
    """Tests for EvidenceItem dataclass."""

    def test_create_evidence(self):
        """Test creating evidence item."""
        evidence = EvidenceItem(
            evidence_id="ev-001",
            type="fact_check",
            stance="supports",
            weight=0.9,
            url="https://example.com",
            snippet="Test snippet",
        )

        assert evidence.evidence_id == "ev-001"
        assert evidence.type == "fact_check"
        assert evidence.stance == "supports"
        assert evidence.weight == 0.9

    def test_evidence_to_dict(self):
        """Test converting evidence to dict."""
        evidence = EvidenceItem(
            evidence_id="ev-002",
            type="source",
            stance="refutes",
        )

        evidence_dict = evidence.to_dict()

        assert evidence_dict["evidence_id"] == "ev-002"
        assert evidence_dict["type"] == "source"
        assert evidence_dict["stance"] == "refutes"


class TestNOGOSignal:
    """Tests for NOGOSignal in export."""

    def test_create_signal(self):
        """Test creating a signal."""
        signal = NOGOSignal(
            type="INCONSISTENCY",
            severity="high",
            reason="Conflicting evidence",
        )

        assert signal.type == "INCONSISTENCY"
        assert signal.severity == "high"

    def test_signal_to_dict(self):
        """Test converting signal to dict."""
        signal = NOGOSignal(
            type="SUSPICION",
            severity="medium",
            reason="Rapid submission",
        )

        signal_dict = signal.to_dict()

        assert signal_dict["type"] == "SUSPICION"
        assert signal_dict["severity"] == "medium"


class TestClaimExportItem:
    """Tests for ClaimExportItem."""

    def test_create_export_item(self):
        """Test creating export item."""
        prior = ClaimPrior(probability=0.7, confidence=0.8, source="model")
        evidence = [
            EvidenceItem(evidence_id="ev1", type="source", stance="supports")
        ]

        item = ClaimExportItem(
            claim_id="claim-001",
            text="Test claim text",
            prior=prior,
            evidence_trail=evidence,
            current_state="ESTABLISHED_FACT",
            created_at=datetime.now(timezone.utc),
        )

        assert item.claim_id == "claim-001"
        assert item.text == "Test claim text"
        assert item.prior.probability == 0.7

    def test_export_item_to_dict(self):
        """Test converting export item to dict."""
        prior = ClaimPrior(probability=0.5, confidence=0.5, source="crowd")
        item = ClaimExportItem(
            claim_id="claim-002",
            text="Another claim",
            prior=prior,
            evidence_trail=[],
            current_state="UNDER_REVIEW",
            created_at=datetime.now(timezone.utc),
        )

        item_dict = item.to_dict()

        assert item_dict["claim_id"] == "claim-002"
        assert "prior" in item_dict
        assert item_dict["current_state"] == "UNDER_REVIEW"

    def test_export_item_to_dict_full(self):
        """Test converting export item with all optional fields."""
        prior = ClaimPrior(probability=0.6, confidence=0.7, source="model")
        signals = [NOGOSignal(type="INCONSISTENCY", severity="high", reason="Test")]
        item = ClaimExportItem(
            claim_id="claim-full",
            text="Full claim",
            prior=prior,
            evidence_trail=[],
            current_state="VERIFIED",
            created_at=datetime.now(timezone.utc),
            normalized_text="normalized full claim",
            signals=signals,
            relations=[{"type": "supports", "target": "other-claim"}],
            source_refs=[{"id": "src-1", "url": "http://example.com"}],
            updated_at=datetime.now(timezone.utc),
        )

        item_dict = item.to_dict()

        assert item_dict["normalized_text"] == "normalized full claim"
        assert len(item_dict["signals"]) == 1
        assert item_dict["signals"][0]["type"] == "INCONSISTENCY"
        assert len(item_dict["relations"]) == 1
        assert len(item_dict["source_refs"]) == 1
        assert "updated_at" in item_dict


class TestClaimGraphExport:
    """Tests for ClaimGraphExport."""

    def test_create_export(self):
        """Test creating an export."""
        export = ClaimGraphExport(domain="saude")

        assert export.version == "1.0"
        assert export.domain == "saude"
        assert len(export.claims) == 0
        assert export.export_id is not None

    def test_export_to_dict(self):
        """Test converting export to dict."""
        export = ClaimGraphExport(
            domain="politica",
            metadata={"sprint": "S40"},
        )

        export_dict = export.to_dict()

        assert export_dict["version"] == "1.0"
        assert export_dict["domain"] == "politica"
        assert "exported_at" in export_dict
        assert export_dict["metadata"]["sprint"] == "S40"

    def test_export_to_dict_with_edges(self):
        """Test converting export with edges to dict."""
        export = ClaimGraphExport(
            domain="saude",
            edges=[
                {"edge_id": "e1", "source_id": "c1", "target_id": "c2", "relation_type": "supports"}
            ],
        )

        export_dict = export.to_dict()

        assert "edges" in export_dict
        assert len(export_dict["edges"]) == 1
        assert export_dict["edges"][0]["edge_id"] == "e1"


class TestExportClaimgraphV1:
    """Tests for export_claimgraph_v1 function."""

    def _create_claim(self, domain: str = "saude", content: str = "Test") -> ClaimNode:
        """Create a test claim."""
        claim = ClaimNode.create(
            domain=domain,
            content=content,
            state=ClaimState.VERIFIED,
        )
        claim.properties["prior"] = {
            "probability": 0.8,
            "confidence": 0.9,
            "source": "model",
        }
        claim.properties["evidence_trail"] = [
            {"evidence_id": "ev1", "type": "source", "stance": "supports", "weight": 0.7}
        ]
        return claim

    def test_export_empty_claims(self):
        """Test exporting with no claims."""
        export = export_claimgraph_v1([], domain="test")

        assert len(export.claims) == 0
        assert export.domain == "test"

    def test_export_single_claim(self):
        """Test exporting a single claim."""
        claim = self._create_claim()

        export = export_claimgraph_v1([claim], domain="saude")

        assert len(export.claims) == 1
        assert export.claims[0].claim_id == claim.id
        assert export.claims[0].prior.probability == 0.8

    def test_export_multiple_claims(self):
        """Test exporting multiple claims."""
        claims = [
            self._create_claim(content=f"Claim {i}")
            for i in range(5)
        ]

        export = export_claimgraph_v1(claims, domain="saude")

        assert len(export.claims) == 5

    def test_export_with_edges(self):
        """Test exporting with edges."""
        claim1 = self._create_claim(content="Claim 1")
        claim2 = self._create_claim(content="Claim 2")
        edge = GraphEdge.create(
            source_id=claim1.id,
            target_id=claim2.id,
            edge_type=EdgeType.SUPPORT,
            weight=0.8,
        )

        export = export_claimgraph_v1([claim1, claim2], edges=[edge], domain="saude")

        assert len(export.edges) == 1
        assert export.edges[0]["relation_type"] == "supports"
        assert export.edges[0]["weight"] == 0.8

    def test_export_with_edge_properties(self):
        """Test exporting with edges that have properties."""
        claim1 = self._create_claim(content="Claim with props 1")
        claim2 = self._create_claim(content="Claim with props 2")
        edge = GraphEdge.create(
            source_id=claim1.id,
            target_id=claim2.id,
            edge_type=EdgeType.OPPOSITION,
            weight=0.9,
        )
        edge.properties = {"created_by": "model", "confidence": 0.95}

        export = export_claimgraph_v1([claim1, claim2], edges=[edge], domain="saude")

        assert len(export.edges) == 1
        assert export.edges[0]["relation_type"] == "contradicts"
        assert "metadata" in export.edges[0]
        assert export.edges[0]["metadata"]["created_by"] == "model"

    def test_export_pagination(self):
        """Test export pagination info."""
        claims = [self._create_claim(content=f"C{i}") for i in range(10)]

        export = export_claimgraph_v1(claims, domain="saude", page=1, page_size=5)

        assert export.pagination["page"] == 1
        assert export.pagination["page_size"] == 5
        assert export.pagination["total_claims"] == 10
        assert export.pagination["total_pages"] == 2
        assert export.pagination["has_next"] is True

    def test_export_with_signals(self):
        """Test exporting with NO-GO signals."""
        claim = self._create_claim()
        claim.properties["signals"] = [
            {"type": "INCONSISTENCY", "severity": "high", "reason": "Test"}
        ]

        export = export_claimgraph_v1([claim], domain="saude", include_signals=True)

        assert len(export.claims[0].signals) == 1
        assert export.claims[0].signals[0].type == "INCONSISTENCY"

    def test_export_without_signals(self):
        """Test exporting without NO-GO signals."""
        claim = self._create_claim()
        claim.properties["signals"] = [
            {"type": "SUSPICION", "severity": "low", "reason": "Test"}
        ]

        export = export_claimgraph_v1([claim], domain="saude", include_signals=False)

        assert len(export.claims[0].signals) == 0

    def test_export_state_mapping(self):
        """Test state mapping in export."""
        states_map = [
            (ClaimState.PENDING, "CLAIMED"),
            (ClaimState.VERIFIED, "ESTABLISHED_FACT"),
            (ClaimState.FALSE, "RETRACTED"),
            (ClaimState.DISPUTED, "UNDER_DISPUTE"),
            (ClaimState.INCONCLUSIVE, "UNDER_REVIEW"),
        ]

        for internal_state, export_state in states_map:
            claim = ClaimNode.create(
                domain="test",
                content="Test",
                state=internal_state,
            )
            export = export_claimgraph_v1([claim], domain="test")
            assert export.claims[0].current_state == export_state, f"{internal_state} should map to {export_state}"


class TestIngestClaimgraphExport:
    """Tests for ingest_claimgraph_export function."""

    def test_ingest_empty_export(self):
        """Test ingesting empty export."""
        export_data = {
            "version": "1.0",
            "export_id": "test-id",
            "domain": "saude",
            "claims": [],
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }

        claims = ingest_claimgraph_export(export_data)

        assert len(claims) == 0

    def test_ingest_single_claim(self):
        """Test ingesting a single claim."""
        export_data = {
            "version": "1.0",
            "export_id": "test-id",
            "domain": "saude",
            "claims": [
                {
                    "claim_id": "c1",
                    "text": "Test claim",
                    "prior": {"probability": 0.7, "confidence": 0.8, "source": "model"},
                    "evidence_trail": [],
                    "current_state": "ESTABLISHED_FACT",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ],
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }

        claims = ingest_claimgraph_export(export_data)

        assert len(claims) == 1
        assert claims[0].claim_id == "c1"
        assert claims[0].prior.probability == 0.7

    def test_ingest_with_evidence(self):
        """Test ingesting with evidence trail."""
        export_data = {
            "version": "1.0",
            "claims": [
                {
                    "claim_id": "c1",
                    "text": "Test",
                    "prior": {"probability": 0.5, "confidence": 0.5, "source": "model"},
                    "evidence_trail": [
                        {"evidence_id": "e1", "type": "source", "stance": "supports", "weight": 0.9}
                    ],
                    "current_state": "CLAIMED",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ],
        }

        claims = ingest_claimgraph_export(export_data)

        assert len(claims[0].evidence_trail) == 1
        assert claims[0].evidence_trail[0].weight == 0.9

    def test_ingest_with_signals(self):
        """Test ingesting with signals."""
        export_data = {
            "version": "1.0",
            "claims": [
                {
                    "claim_id": "c1",
                    "text": "Test",
                    "prior": {"probability": 0.5, "confidence": 0.5, "source": "model"},
                    "evidence_trail": [],
                    "current_state": "CLAIMED",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "signals": [
                        {"type": "ABUSE", "severity": "critical", "reason": "Test abuse"}
                    ],
                }
            ],
        }

        claims = ingest_claimgraph_export(export_data)

        assert len(claims[0].signals) == 1
        assert claims[0].signals[0].type == "ABUSE"

    def test_ingest_invalid_version(self):
        """Test ingesting with invalid version."""
        export_data = {
            "version": "2.0",
            "claims": [],
        }

        with pytest.raises(ValueError, match="Unsupported export version"):
            ingest_claimgraph_export(export_data)

    def test_ingest_missing_claims(self):
        """Test ingesting without claims field."""
        export_data = {
            "version": "1.0",
        }

        with pytest.raises(ValueError, match="Missing 'claims'"):
            ingest_claimgraph_export(export_data)

    def test_ingest_skip_validation(self):
        """Test ingesting without validation."""
        export_data = {
            "version": "9.9",  # Invalid version
            "claims": [
                {
                    "claim_id": "c1",
                    "text": "Test",
                    "prior": {"probability": 0.5, "confidence": 0.5, "source": "model"},
                    "evidence_trail": [],
                    "current_state": "CLAIMED",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ],
        }

        # Should not raise when validation is disabled
        claims = ingest_claimgraph_export(export_data, validate=False)

        assert len(claims) == 1


class TestRoundTrip:
    """Tests for export/ingest round trip."""

    def test_roundtrip(self):
        """Test that export -> ingest preserves data."""
        claim = ClaimNode.create(
            domain="saude",
            content="Test claim for roundtrip",
            state=ClaimState.VERIFIED,
        )
        claim.properties["prior"] = {
            "probability": 0.85,
            "confidence": 0.95,
            "source": "expert",
        }
        claim.properties["evidence_trail"] = [
            {"evidence_id": "ev1", "type": "fact_check", "stance": "supports", "weight": 0.8}
        ]

        # Export
        export = export_claimgraph_v1([claim], domain="saude")
        export_dict = export.to_dict()

        # Ingest
        ingested = ingest_claimgraph_export(export_dict)

        assert len(ingested) == 1
        assert ingested[0].claim_id == claim.id
        assert ingested[0].prior.probability == 0.85
        assert len(ingested[0].evidence_trail) == 1
