"""
Signal Calculator: mentiras_em_circulacao (Lies in Circulation) — S37

Calculates the volume of false claims actively circulating in a domain.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from app.claims.graph_models import ClaimState, NodeType
from app.claims.graph_service import ClaimGraphService


@dataclass
class LiesInCirculationResult:
    """Result of lies_in_circulation calculation."""

    domain: str
    timestamp: datetime
    total_false_claims: int
    active_false_claims: int
    false_claim_rate: float
    severity_score: float
    top_topics: List[Dict[str, Any]]
    thresholds: Dict[str, float]


class LiesInCirculationCalculator:
    """
    Calculates the 'lies in circulation' signal for a domain.

    Signal measures:
    - Count of claims in FALSE state
    - Rate of false claims vs total claims
    - Recency weighting (recent false claims weight more)
    - Topic concentration (which topics have most lies)
    """

    # Default thresholds by domain
    DEFAULT_THRESHOLDS: Dict[str, Dict[str, float]] = {
        "pilot_politics": {
            "warning": 10,
            "alert": 25,
            "critical": 50,
        },
        "saude": {
            "warning": 5,
            "alert": 15,
            "critical": 30,
        },
        "default": {
            "warning": 10,
            "alert": 20,
            "critical": 40,
        },
    }

    def __init__(
        self,
        graph_service: Optional[ClaimGraphService] = None,
        active_window_days: int = 7,
    ):
        self.graph = graph_service or ClaimGraphService()
        self.active_window_days = active_window_days

    def calculate(self, domain: str) -> LiesInCirculationResult:
        """
        Calculate lies in circulation for a domain.

        Args:
            domain: Domain to calculate for

        Returns:
            LiesInCirculationResult with metrics
        """
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        cutoff = now - timedelta(days=self.active_window_days)

        # Get all claims in domain
        all_claims = self.graph.find_claims(domain=domain, limit=10000)
        total_claims = len(all_claims)

        # Filter false claims
        false_claims = [
            c for c in all_claims
            if c.properties.get("state") == ClaimState.FALSE.value
        ]
        total_false = len(false_claims)

        # Filter active (recent) false claims
        active_false = [
            c for c in false_claims
            if c.created_at >= cutoff
        ]
        active_count = len(active_false)

        # Calculate rate
        false_rate = total_false / total_claims if total_claims > 0 else 0.0

        # Calculate severity score (0-100)
        thresholds = self.DEFAULT_THRESHOLDS.get(
            domain, self.DEFAULT_THRESHOLDS["default"]
        )
        severity = self._calculate_severity(active_count, thresholds)

        # Get top topics with false claims
        top_topics = self._get_top_topics(false_claims, domain)

        return LiesInCirculationResult(
            domain=domain,
            timestamp=now,
            total_false_claims=total_false,
            active_false_claims=active_count,
            false_claim_rate=false_rate,
            severity_score=severity,
            top_topics=top_topics,
            thresholds=thresholds,
        )

    def _calculate_severity(
        self, active_count: int, thresholds: Dict[str, float]
    ) -> float:
        """Calculate severity score (0-100) based on thresholds."""
        if active_count >= thresholds["critical"]:
            return 100.0
        elif active_count >= thresholds["alert"]:
            # Scale between 70-99
            range_size = thresholds["critical"] - thresholds["alert"]
            progress = (active_count - thresholds["alert"]) / range_size
            return 70.0 + (progress * 29.0)
        elif active_count >= thresholds["warning"]:
            # Scale between 40-69
            range_size = thresholds["alert"] - thresholds["warning"]
            progress = (active_count - thresholds["warning"]) / range_size
            return 40.0 + (progress * 29.0)
        else:
            # Scale between 0-39
            if thresholds["warning"] > 0:
                progress = active_count / thresholds["warning"]
                return progress * 39.0
            return 0.0

    def _get_top_topics(
        self, false_claims: List[Any], domain: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get topics with most false claims."""
        topic_counts: Dict[str, int] = {}

        for claim in false_claims:
            # Get topic tags for this claim
            edges = self.graph.repo.find_edges(
                source_id=claim.id,
                edge_type=None,  # Get all edges
            )
            for edge in edges:
                if edge.edge_type.value == "tagged":
                    topic = self.graph.repo.get_node(edge.target_id)
                    if topic:
                        topic_name = topic.properties.get("name", edge.target_id)
                        topic_counts[topic_name] = topic_counts.get(topic_name, 0) + 1

        # Sort by count and return top N
        sorted_topics = sorted(
            topic_counts.items(), key=lambda x: x[1], reverse=True
        )[:limit]

        return [
            {"topic": name, "false_claims": count}
            for name, count in sorted_topics
        ]

    def to_snapshot(self, result: LiesInCirculationResult) -> Dict[str, Any]:
        """Convert result to snapshot format for persistence."""
        return {
            "signal_type": "mentiras_em_circulacao",
            "domain": result.domain,
            "timestamp": result.timestamp.isoformat(),
            "values": {
                "total_false_claims": result.total_false_claims,
                "active_false_claims": result.active_false_claims,
                "false_claim_rate": result.false_claim_rate,
                "severity_score": result.severity_score,
            },
            "metadata": {
                "top_topics": result.top_topics,
                "thresholds": result.thresholds,
            },
        }
