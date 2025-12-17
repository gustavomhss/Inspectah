"""
Tests for build_references function.

Task: S40-BE-004 tests
"""

import pytest

from app.truth.references import (
    ClaimContext,
    E40_5CheckResult,
    PolicyResult,
    build_references,
    build_references_dict,
)


class TestBuildReferences:
    """Tests for build_references function."""

    def test_build_references_from_dict(self):
        """Test building references from dict inputs."""
        claim = {"claim_id": "c1", "domain": "saude", "gate": "G23"}
        policy = {"version": "v1.0", "rules_applied": ["rule1", "rule2"]}
        e40_5 = {
            "status": "PASS",
            "invariants_checked": ["INV-DB-01", "INV-DB-02"],
            "violations": [],
        }

        refs = build_references(claim, policy, e40_5)

        assert len(refs.guias) > 0
        assert refs.guias[0].guia == "MQV"
        assert refs.guias[0].dominio == "saude"
        assert refs.guias[0].gate == "G23"

        assert len(refs.pilares) > 0
        assert refs.pilares[0].pilar == "P5"

        assert refs.e40_5.status == "PASS"
        assert "INV-DB-01" in refs.e40_5.invariants_checked

        assert refs.policy is not None
        assert refs.policy.version == "v1.0"
        assert "rule1" in refs.policy.rules_applied

    def test_build_references_from_dataclass(self):
        """Test building references from dataclass inputs."""
        claim = ClaimContext(claim_id="c1", domain="politica", gate="G24")
        policy = PolicyResult(version="v2.0", rules_applied=["policy_rule"])
        e40_5 = E40_5CheckResult(
            status="FAIL",
            invariants_checked=["INV-1"],
            violations=[{"invariant": "INV-1", "message": "Failed"}],
        )

        refs = build_references(claim, policy, e40_5)

        assert refs.guias[0].dominio == "politica"
        assert refs.e40_5.status == "FAIL"
        assert len(refs.e40_5.violations) == 1

    def test_build_references_without_policy(self):
        """Test building references without policy result."""
        claim = {"claim_id": "c1", "domain": "saude", "gate": "G23"}
        e40_5 = {"status": "PASS", "invariants_checked": [], "violations": []}

        refs = build_references(claim, None, e40_5)

        assert refs.policy is None
        assert refs.e40_5.status == "PASS"

    def test_build_references_without_e40_5(self):
        """Test building references without E40.5 result (defaults to SKIP)."""
        claim = {"claim_id": "c1", "domain": "saude", "gate": "G23"}

        refs = build_references(claim, None, None)

        assert refs.e40_5.status == "SKIP"

    def test_build_references_custom_guias(self):
        """Test building references with custom guias."""
        claim = {"claim_id": "c1", "domain": "saude", "gate": "G23"}
        custom_guias = [
            {"guia": "MAC", "documento": "Custom_Doc", "tabela": "T1", "secao": "S1"}
        ]
        e40_5 = {"status": "PASS", "invariants_checked": [], "violations": []}

        refs = build_references(claim, None, e40_5, custom_guias=custom_guias)

        assert len(refs.guias) == 1
        assert refs.guias[0].guia == "MAC"
        assert refs.guias[0].documento == "Custom_Doc"

    def test_build_references_custom_pilares(self):
        """Test building references with custom pilares."""
        claim = {"claim_id": "c1", "domain": "saude", "gate": "G23"}
        custom_pilares = [
            {"pilar": "P1", "documento": "P1-1", "secao": "§1.1"},
            {"pilar": "P6", "documento": "P6-2", "secao": "§2.2"},
        ]
        e40_5 = {"status": "PASS", "invariants_checked": [], "violations": []}

        refs = build_references(claim, None, e40_5, custom_pilares=custom_pilares)

        assert len(refs.pilares) == 2
        assert refs.pilares[0].pilar == "P1"
        assert refs.pilares[1].pilar == "P6"

    def test_build_references_to_dict(self):
        """Test converting references to dict."""
        claim = {"claim_id": "c1", "domain": "saude", "gate": "G23"}
        e40_5 = {"status": "PASS", "invariants_checked": ["INV-1"], "violations": []}

        refs = build_references(claim, None, e40_5)
        refs_dict = refs.to_dict()

        assert isinstance(refs_dict, dict)
        assert "guias" in refs_dict
        assert "pilares" in refs_dict
        assert "e40_5" in refs_dict
        assert refs_dict["e40_5"]["status"] == "PASS"

    def test_build_references_dict_function(self):
        """Test build_references_dict helper."""
        claim = {"claim_id": "c1", "domain": "economia", "gate": "G22"}
        e40_5 = {"status": "DEGRADED", "invariants_checked": [], "violations": []}

        refs_dict = build_references_dict(claim, None, e40_5)

        assert isinstance(refs_dict, dict)
        assert refs_dict["guias"][0]["dominio"] == "economia"
        assert refs_dict["e40_5"]["status"] == "DEGRADED"

    def test_domain_default_fallback(self):
        """Test that unknown domains use default guias."""
        claim = {"claim_id": "c1", "domain": "unknown_domain", "gate": "G23"}
        e40_5 = {"status": "PASS", "invariants_checked": [], "violations": []}

        refs = build_references(claim, None, e40_5)

        # Should fall back to default
        assert len(refs.guias) > 0
        assert refs.guias[0].dominio == "unknown_domain"

    def test_e40_5_all_statuses(self):
        """Test all valid E40.5 statuses."""
        claim = {"claim_id": "c1", "domain": "saude", "gate": "G23"}

        for status in ["PASS", "FAIL", "SKIP", "TIMEOUT", "DEGRADED"]:
            e40_5 = {"status": status, "invariants_checked": [], "violations": []}
            refs = build_references(claim, None, e40_5)
            assert refs.e40_5.status == status
