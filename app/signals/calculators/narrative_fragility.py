"""
Signal Calculator: fragilidade_narrativa (Narrative Fragility) — S37

Identifies claims with weak evidence trails.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.claims.graph_models import ClaimState, EdgeType, NodeType
from app.claims.graph_service import ClaimGraphService


@dataclass
class FragileClaim:
    """A claim with weak evidence."""

    claim_id: str
    content: str
    evidence_count: int
    support_count: int
    fragility_score: float
    state: str


@dataclass
class NarrativeFragilityResult:
    """Result of narrative fragility calculation."""

    domain: str
    timestamp: datetime
    total_claims: int
    fragile_claims: int
    fragility_rate: float
    average_fragility: float
    risk_score: float
    top_fragile: List[FragileClaim]


class NarrativeFragilityCalculator:
    """
    Calculates the 'narrative fragility' signal for a domain.

    Signal measures:
    - Claims with low evidence count
    - Claims with few support relations
    - Claims with high contradiction ratio
    - Overall narrative reliability
    """

    # Thresholds for fragility
    LOW_EVIDENCE_THRESHOLD = 2
    LOW_SUPPORT_THRESHOLD = 1
    FRAGILE_SCORE_THRESHOLD = 0.6

    def __init__(self, graph_service: Optional[ClaimGraphService] = None):
        self.graph = graph_service or ClaimGraphService()

    def calculate(self, domain: str) -> NarrativeFragilityResult:
        """
        Calculate narrative fragility metrics for a domain.

        Args:
            domain: Domain to calculate for

        Returns:
            NarrativeFragilityResult with metrics
        """
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        # Get all claims in domain
        claims = self.graph.find_claims(domain=domain, limit=10000)
        total_claims = len(claims)

        fragile_claims: List[FragileClaim] = []
        fragility_scores: List[float] = []

        for claim in claims:
            # Calculate fragility score for this claim
            score, metrics = self._calculate_claim_fragility(claim)
            fragility_scores.append(score)

            if score >= self.FRAGILE_SCORE_THRESHOLD:
                fragile_claims.append(
                    FragileClaim(
                        claim_id=claim.id,
                        content=claim.properties.get("content", "")[:100],
                        evidence_count=metrics["evidence_count"],
                        support_count=metrics["support_count"],
                        fragility_score=score,
                        state=claim.properties.get("state", "pending"),
                    )
                )

        fragile_count = len(fragile_claims)
        fragility_rate = fragile_count / total_claims if total_claims > 0 else 0.0
        avg_fragility = sum(fragility_scores) / len(fragility_scores) if fragility_scores else 0.0

        # Calculate risk score (0-100)
        risk_score = self._calculate_risk_score(
            fragile_count, fragility_rate, avg_fragility
        )

        # Sort by fragility score
        top_fragile = sorted(
            fragile_claims, key=lambda x: x.fragility_score, reverse=True
        )[:10]

        return NarrativeFragilityResult(
            domain=domain,
            timestamp=now,
            total_claims=total_claims,
            fragile_claims=fragile_count,
            fragility_rate=fragility_rate,
            average_fragility=avg_fragility,
            risk_score=risk_score,
            top_fragile=top_fragile,
        )

    def _calculate_claim_fragility(
        self, claim: Any
    ) -> tuple[float, Dict[str, int]]:
        """
        Calculate fragility score for a single claim.

        Returns (score, metrics) where score is 0.0-1.0.
        """
        evidence_count = claim.properties.get("evidence_count", 0)

        # Count support relations
        support_edges = self.graph.repo.find_edges(
            target_id=claim.id, edge_type=EdgeType.SUPPORT, limit=100
        )
        support_count = len(support_edges)

        # Count opposition relations
        opposition_edges = self.graph.repo.find_edges(
            source_id=claim.id, edge_type=EdgeType.OPPOSITION, limit=100
        )
        opposition_edges += self.graph.repo.find_edges(
            target_id=claim.id, edge_type=EdgeType.OPPOSITION, limit=100
        )
        opposition_count = len(opposition_edges)

        # Calculate fragility components
        # 1. Evidence weakness (0-0.4)
        if evidence_count >= 5:
            evidence_weakness = 0.0
        elif evidence_count >= self.LOW_EVIDENCE_THRESHOLD:
            evidence_weakness = 0.2
        elif evidence_count >= 1:
            evidence_weakness = 0.3
        else:
            evidence_weakness = 0.4

        # 2. Support weakness (0-0.3)
        if support_count >= 3:
            support_weakness = 0.0
        elif support_count >= self.LOW_SUPPORT_THRESHOLD:
            support_weakness = 0.15
        else:
            support_weakness = 0.3

        # 3. Contradiction exposure (0-0.3)
        total_relations = support_count + opposition_count
        if total_relations > 0:
            contradiction_ratio = opposition_count / total_relations
            contradiction_exposure = contradiction_ratio * 0.3
        else:
            contradiction_exposure = 0.15  # No relations = somewhat fragile

        score = evidence_weakness + support_weakness + contradiction_exposure
        metrics = {
            "evidence_count": evidence_count,
            "support_count": support_count,
            "opposition_count": opposition_count,
        }

        return score, metrics

    def _calculate_risk_score(
        self,
        fragile_count: int,
        fragility_rate: float,
        avg_fragility: float,
    ) -> float:
        """Calculate overall risk score (0-100)."""
        # Factor 1: Number of fragile claims
        count_score = min(fragile_count * 5, 30)  # Max 30 points

        # Factor 2: Fragility rate
        rate_score = fragility_rate * 35  # Max 35 points

        # Factor 3: Average fragility
        avg_score = avg_fragility * 35  # Max 35 points

        return min(count_score + rate_score + avg_score, 100.0)

    def to_snapshot(self, result: NarrativeFragilityResult) -> Dict[str, Any]:
        """Convert result to snapshot format for persistence."""
        return {
            "signal_type": "fragilidade_narrativa",
            "domain": result.domain,
            "timestamp": result.timestamp.isoformat(),
            "values": {
                "total_claims": result.total_claims,
                "fragile_claims": result.fragile_claims,
                "fragility_rate": result.fragility_rate,
                "average_fragility": result.average_fragility,
                "risk_score": result.risk_score,
            },
            "metadata": {
                "top_fragile": [
                    {
                        "claim_id": f.claim_id,
                        "fragility_score": f.fragility_score,
                        "evidence_count": f.evidence_count,
                    }
                    for f in result.top_fragile[:5]
                ],
            },
        }
