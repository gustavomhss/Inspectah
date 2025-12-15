"""
Signal Calculator: radar_silencio (Silence Radar) — S37

Detects topics with sudden drop in coverage.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from app.claims.graph_models import EdgeType, NodeType
from app.claims.graph_service import ClaimGraphService


@dataclass
class SilencedTopic:
    """A topic that has gone silent."""

    topic_id: str
    topic_name: str
    previous_activity: int
    current_activity: int
    drop_percentage: float
    last_claim_date: Optional[datetime]


@dataclass
class SilenceRadarResult:
    """Result of silence radar calculation."""

    domain: str
    timestamp: datetime
    total_topics: int
    silenced_topics: int
    silence_rate: float
    alert_score: float
    top_silenced: List[SilencedTopic]


class SilenceRadarCalculator:
    """
    Calculates the 'silence radar' signal for a domain.

    Signal measures:
    - Topics with sudden drop in claim activity
    - Compares current window vs baseline window
    - Identifies potential suppression or narrative shifts
    """

    DROP_THRESHOLD = 0.5  # 50% drop triggers silence alert
    BASELINE_DAYS = 14
    CURRENT_DAYS = 7

    def __init__(
        self,
        graph_service: Optional[ClaimGraphService] = None,
        baseline_days: int = 14,
        current_days: int = 7,
    ):
        self.graph = graph_service or ClaimGraphService()
        self.baseline_days = baseline_days
        self.current_days = current_days

    def calculate(self, domain: str) -> SilenceRadarResult:
        """
        Calculate silence radar metrics for a domain.

        Args:
            domain: Domain to calculate for

        Returns:
            SilenceRadarResult with metrics
        """
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        current_start = now - timedelta(days=self.current_days)
        baseline_start = now - timedelta(days=self.baseline_days)
        baseline_end = current_start

        # Get all topics in domain
        topics = self.graph.repo.find_nodes(
            node_type=NodeType.TOPIC, domain=domain, limit=1000
        )

        silenced: List[SilencedTopic] = []
        total_topics = len(topics)

        for topic in topics:
            # Count claims tagged with this topic in each window
            tagged_edges = self.graph.repo.find_edges(
                target_id=topic.id, edge_type=EdgeType.TAGGED, limit=10000
            )

            baseline_count = 0
            current_count = 0
            last_claim: Optional[datetime] = None

            for edge in tagged_edges:
                claim = self.graph.repo.get_node(edge.source_id)
                if not claim or claim.domain != domain:
                    continue

                claim_date = claim.created_at

                # Update last claim date
                if last_claim is None or claim_date > last_claim:
                    last_claim = claim_date

                # Count in windows
                if baseline_start <= claim_date < baseline_end:
                    baseline_count += 1
                elif claim_date >= current_start:
                    current_count += 1

            # Check for silence (significant drop)
            if baseline_count > 0:
                drop_pct = 1.0 - (current_count / baseline_count)
                if drop_pct >= self.DROP_THRESHOLD:
                    silenced.append(
                        SilencedTopic(
                            topic_id=topic.id,
                            topic_name=topic.properties.get("name", topic.id),
                            previous_activity=baseline_count,
                            current_activity=current_count,
                            drop_percentage=drop_pct,
                            last_claim_date=last_claim,
                        )
                    )

        # Calculate metrics
        silenced_count = len(silenced)
        silence_rate = silenced_count / total_topics if total_topics > 0 else 0.0

        # Calculate alert score (0-100)
        alert_score = self._calculate_alert_score(
            silenced_count, silence_rate, silenced
        )

        # Sort by drop percentage
        top_silenced = sorted(
            silenced, key=lambda x: x.drop_percentage, reverse=True
        )[:10]

        return SilenceRadarResult(
            domain=domain,
            timestamp=now,
            total_topics=total_topics,
            silenced_topics=silenced_count,
            silence_rate=silence_rate,
            alert_score=alert_score,
            top_silenced=top_silenced,
        )

    def _calculate_alert_score(
        self,
        silenced_count: int,
        silence_rate: float,
        silenced: List[SilencedTopic],
    ) -> float:
        """Calculate alert score (0-100)."""
        if silenced_count == 0:
            return 0.0

        # Factor 1: Number of silenced topics
        count_score = min(silenced_count * 10, 40)  # Max 40 points

        # Factor 2: Silence rate
        rate_score = silence_rate * 30  # Max 30 points

        # Factor 3: Average drop severity
        avg_drop = sum(s.drop_percentage for s in silenced) / len(silenced)
        drop_score = avg_drop * 30  # Max 30 points

        return min(count_score + rate_score + drop_score, 100.0)

    def to_snapshot(self, result: SilenceRadarResult) -> Dict[str, Any]:
        """Convert result to snapshot format for persistence."""
        return {
            "signal_type": "radar_silencio",
            "domain": result.domain,
            "timestamp": result.timestamp.isoformat(),
            "values": {
                "total_topics": result.total_topics,
                "silenced_topics": result.silenced_topics,
                "silence_rate": result.silence_rate,
                "alert_score": result.alert_score,
            },
            "metadata": {
                "top_silenced": [
                    {
                        "topic_id": s.topic_id,
                        "topic_name": s.topic_name,
                        "drop_percentage": s.drop_percentage,
                    }
                    for s in result.top_silenced[:5]
                ],
            },
        }
