"""
Signal Calculator: campo_batalha (Battleground) — S37

Identifies pairs of claim/counter-claim with high tension.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.claims.graph_models import EdgeType, NodeType
from app.claims.graph_service import ClaimGraphService


@dataclass
class BattlegroundPair:
    """A pair of claims in conflict."""

    claim_a_id: str
    claim_b_id: str
    claim_a_content: str
    claim_b_content: str
    tension_score: float
    edge_id: str


@dataclass
class BattlegroundResult:
    """Result of battleground calculation."""

    domain: str
    timestamp: datetime
    total_conflicts: int
    high_tension_conflicts: int
    average_tension: float
    intensity_score: float
    top_battlegrounds: List[BattlegroundPair]


class BattlegroundCalculator:
    """
    Calculates the 'battleground' signal for a domain.

    Signal measures:
    - Pairs of opposing claims (opposition edges)
    - Tension/strength of opposition
    - Overall conflict intensity
    """

    HIGH_TENSION_THRESHOLD = 0.7

    def __init__(self, graph_service: Optional[ClaimGraphService] = None):
        self.graph = graph_service or ClaimGraphService()

    def calculate(self, domain: str) -> BattlegroundResult:
        """
        Calculate battleground metrics for a domain.

        Args:
            domain: Domain to calculate for

        Returns:
            BattlegroundResult with metrics
        """
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        # Get all opposition edges in domain
        # First get all claims, then filter edges
        claims = self.graph.find_claims(domain=domain, limit=10000)
        claim_ids = {c.id for c in claims}
        claim_map = {c.id: c for c in claims}

        battlegrounds: List[BattlegroundPair] = []
        tensions: List[float] = []

        # Get opposition edges
        all_edges = self.graph.repo.find_edges(
            edge_type=EdgeType.OPPOSITION, limit=10000
        )

        for edge in all_edges:
            # Only count edges within the domain
            if edge.source_id not in claim_ids:
                continue

            tension = edge.weight if edge.weight is not None else 1.0
            tensions.append(tension)

            source_claim = claim_map.get(edge.source_id)
            target_claim = claim_map.get(edge.target_id)

            if source_claim and target_claim:
                battlegrounds.append(
                    BattlegroundPair(
                        claim_a_id=edge.source_id,
                        claim_b_id=edge.target_id,
                        claim_a_content=source_claim.properties.get("content", "")[:100],
                        claim_b_content=target_claim.properties.get("content", "")[:100],
                        tension_score=tension,
                        edge_id=edge.id,
                    )
                )

        total_conflicts = len(battlegrounds)
        high_tension = sum(1 for t in tensions if t >= self.HIGH_TENSION_THRESHOLD)
        avg_tension = sum(tensions) / len(tensions) if tensions else 0.0

        # Calculate intensity score (0-100)
        intensity = self._calculate_intensity(
            total_conflicts, high_tension, avg_tension, len(claims)
        )

        # Sort by tension and get top battlegrounds
        top_battlegrounds = sorted(
            battlegrounds, key=lambda x: x.tension_score, reverse=True
        )[:10]

        return BattlegroundResult(
            domain=domain,
            timestamp=now,
            total_conflicts=total_conflicts,
            high_tension_conflicts=high_tension,
            average_tension=avg_tension,
            intensity_score=intensity,
            top_battlegrounds=top_battlegrounds,
        )

    def _calculate_intensity(
        self,
        total_conflicts: int,
        high_tension: int,
        avg_tension: float,
        total_claims: int,
    ) -> float:
        """Calculate overall intensity score (0-100)."""
        if total_claims == 0:
            return 0.0

        # Factor 1: Conflict density (conflicts per claim)
        conflict_density = total_conflicts / total_claims
        density_score = min(conflict_density * 100, 40)  # Max 40 points

        # Factor 2: High tension ratio
        high_ratio = high_tension / total_conflicts if total_conflicts > 0 else 0
        tension_score = high_ratio * 30  # Max 30 points

        # Factor 3: Average tension
        avg_score = avg_tension * 30  # Max 30 points

        return min(density_score + tension_score + avg_score, 100.0)

    def to_snapshot(self, result: BattlegroundResult) -> Dict[str, Any]:
        """Convert result to snapshot format for persistence."""
        return {
            "signal_type": "campo_batalha",
            "domain": result.domain,
            "timestamp": result.timestamp.isoformat(),
            "values": {
                "total_conflicts": result.total_conflicts,
                "high_tension_conflicts": result.high_tension_conflicts,
                "average_tension": result.average_tension,
                "intensity_score": result.intensity_score,
            },
            "metadata": {
                "top_battlegrounds": [
                    {
                        "claim_a_id": b.claim_a_id,
                        "claim_b_id": b.claim_b_id,
                        "tension": b.tension_score,
                    }
                    for b in result.top_battlegrounds[:5]
                ],
            },
        }
