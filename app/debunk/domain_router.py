"""
S39 - Domain-Based Debunker Routing

Routes debunk issues to domain-specific handlers based on claim content.
Integrates with the sharding system for domain detection.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from app.data.sharding.router import Domain, DOMAIN_KEYWORDS

logger = logging.getLogger(__name__)


class DebunkPriority(str, Enum):
    """Priority levels for debunk processing."""
    CRITICAL = "critical"   # Immediate attention required
    HIGH = "high"          # Process within hours
    MEDIUM = "medium"      # Process within 24 hours
    LOW = "low"            # Process when resources available


class DomainDebunkConfig:
    """Configuration for domain-specific debunking."""

    # Default priority multipliers per domain
    PRIORITY_MULTIPLIERS: Dict[Domain, float] = {
        Domain.POLITICA: 1.5,   # Political claims get higher priority
        Domain.SAUDE: 1.3,      # Health claims also important
        Domain.ECONOMIA: 1.0,   # Standard priority
        Domain.DEFAULT: 0.8,    # Lower priority for general claims
    }

    # Domain-specific keywords that increase urgency
    URGENT_KEYWORDS: Dict[Domain, List[str]] = {
        Domain.POLITICA: ["eleição", "voto", "fraude eleitoral", "urna"],
        Domain.SAUDE: ["vacina", "covid", "morte", "epidemia", "remédio falso"],
        Domain.ECONOMIA: ["golpe", "pirâmide", "fraude financeira"],
        Domain.DEFAULT: [],
    }

    # Maximum concurrent issues per domain
    MAX_CONCURRENT_PER_DOMAIN: Dict[Domain, int] = {
        Domain.POLITICA: 100,
        Domain.SAUDE: 80,
        Domain.ECONOMIA: 50,
        Domain.DEFAULT: 30,
    }


@dataclass
class DomainDebunkStats:
    """Statistics for domain-based debunking."""
    domain: Domain
    open_issues: int = 0
    resolved_issues: int = 0
    avg_resolution_time_hours: float = 0.0
    pending_tasks: int = 0
    completed_tasks: int = 0


@dataclass
class DomainDebunkResult:
    """Result of domain routing."""
    domain: Domain
    priority: DebunkPriority
    priority_score: float
    is_urgent: bool
    routing_reason: str
    matched_keywords: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain.value,
            "priority": self.priority.value,
            "priority_score": self.priority_score,
            "is_urgent": self.is_urgent,
            "routing_reason": self.routing_reason,
            "matched_keywords": self.matched_keywords,
        }


class DomainDebunkRouter:
    """
    Routes debunk issues to domain-specific handlers.

    Features:
    - Automatic domain detection from claim text
    - Priority calculation based on domain and content
    - Urgency detection for time-sensitive claims
    - Load balancing across domains

    Usage:
        router = DomainDebunkRouter()

        # Route a debunk issue
        result = router.route("Vacina causa autismo", risk_level="high")
        # Returns: DomainDebunkResult(domain=SAUDE, priority=CRITICAL, is_urgent=True, ...)

        # Route with explicit domain
        result = router.route("Lula anuncia nova medida", domain=Domain.POLITICA)
    """

    def __init__(self, config: Optional[DomainDebunkConfig] = None):
        self.config = config or DomainDebunkConfig()
        self._stats: Dict[Domain, DomainDebunkStats] = {
            d: DomainDebunkStats(domain=d) for d in Domain
        }
        self._handlers: Dict[Domain, List[Callable]] = {d: [] for d in Domain}

    def detect_domain(self, text: str) -> Domain:
        """
        Detect domain from text content.

        Uses the same keyword matching as the sharding router.
        """
        text_lower = text.lower()

        for keyword, domain in DOMAIN_KEYWORDS.items():
            if keyword in text_lower:
                logger.debug(f"Detected domain {domain.value} from keyword '{keyword}'")
                return domain

        return Domain.DEFAULT

    def calculate_priority(
        self,
        text: str,
        domain: Domain,
        base_risk_level: str = "medium",
    ) -> tuple[DebunkPriority, float]:
        """
        Calculate priority for a debunk issue.

        Returns:
            Tuple of (priority level, numeric score)
        """
        # Base score from risk level
        risk_scores = {
            "critical": 100,
            "high": 75,
            "medium": 50,
            "low": 25,
        }
        base_score = risk_scores.get(base_risk_level.lower(), 50)

        # Apply domain multiplier
        multiplier = self.config.PRIORITY_MULTIPLIERS.get(domain, 1.0)
        score = base_score * multiplier

        # Check for urgent keywords
        urgent_keywords = self.config.URGENT_KEYWORDS.get(domain, [])
        text_lower = text.lower()
        for keyword in urgent_keywords:
            if keyword in text_lower:
                score *= 1.2  # 20% boost per urgent keyword
                break

        # Determine priority level
        if score >= 100:
            priority = DebunkPriority.CRITICAL
        elif score >= 75:
            priority = DebunkPriority.HIGH
        elif score >= 50:
            priority = DebunkPriority.MEDIUM
        else:
            priority = DebunkPriority.LOW

        return priority, round(score, 2)

    def check_urgency(self, text: str, domain: Domain) -> tuple[bool, List[str]]:
        """
        Check if a debunk issue is urgent.

        Returns:
            Tuple of (is_urgent, matched_keywords)
        """
        urgent_keywords = self.config.URGENT_KEYWORDS.get(domain, [])
        text_lower = text.lower()
        matched = [kw for kw in urgent_keywords if kw in text_lower]

        return len(matched) > 0, matched

    def route(
        self,
        text: str,
        risk_level: str = "medium",
        domain: Optional[Domain] = None,
    ) -> DomainDebunkResult:
        """
        Route a debunk issue to the appropriate domain handler.

        Args:
            text: The claim text to analyze
            risk_level: Base risk level (critical, high, medium, low)
            domain: Explicit domain override (None = auto-detect)

        Returns:
            DomainDebunkResult with routing decision
        """
        # Detect or use provided domain
        detected_domain = domain or self.detect_domain(text)

        # Calculate priority
        priority, score = self.calculate_priority(text, detected_domain, risk_level)

        # Check urgency
        is_urgent, matched_keywords = self.check_urgency(text, detected_domain)

        # Build routing reason
        if domain:
            reason = f"Explicit domain: {domain.value}"
        else:
            reason = f"Auto-detected domain: {detected_domain.value}"
            if matched_keywords:
                reason += f" (urgent keywords: {', '.join(matched_keywords)})"

        result = DomainDebunkResult(
            domain=detected_domain,
            priority=priority,
            priority_score=score,
            is_urgent=is_urgent,
            routing_reason=reason,
            matched_keywords=matched_keywords,
        )

        logger.info(
            f"Routed debunk to {detected_domain.value}: priority={priority.value}, "
            f"score={score}, urgent={is_urgent}"
        )

        return result

    def register_handler(
        self,
        domain: Domain,
        handler: Callable,
    ) -> None:
        """Register a handler for a domain."""
        self._handlers[domain].append(handler)
        logger.info(f"Registered handler for domain {domain.value}")

    def get_handlers(self, domain: Domain) -> List[Callable]:
        """Get handlers for a domain."""
        return self._handlers.get(domain, [])

    def can_accept_issue(self, domain: Domain) -> bool:
        """Check if domain can accept more issues."""
        max_concurrent = self.config.MAX_CONCURRENT_PER_DOMAIN.get(domain, 50)
        current = self._stats[domain].open_issues
        return current < max_concurrent

    def record_issue_opened(self, domain: Domain) -> None:
        """Record that an issue was opened for a domain."""
        self._stats[domain].open_issues += 1

    def record_issue_resolved(
        self,
        domain: Domain,
        resolution_time_hours: float,
    ) -> None:
        """Record that an issue was resolved."""
        stats = self._stats[domain]
        stats.open_issues = max(0, stats.open_issues - 1)
        stats.resolved_issues += 1

        # Update average resolution time
        total = stats.resolved_issues
        if total > 0:
            stats.avg_resolution_time_hours = (
                (stats.avg_resolution_time_hours * (total - 1) + resolution_time_hours)
                / total
            )

    def record_task_created(self, domain: Domain) -> None:
        """Record that a task was created for a domain."""
        self._stats[domain].pending_tasks += 1

    def record_task_completed(self, domain: Domain) -> None:
        """Record that a task was completed."""
        stats = self._stats[domain]
        stats.pending_tasks = max(0, stats.pending_tasks - 1)
        stats.completed_tasks += 1

    def get_stats(self, domain: Optional[Domain] = None) -> List[DomainDebunkStats]:
        """Get statistics for domain(s)."""
        if domain:
            return [self._stats[domain]]
        return list(self._stats.values())

    def get_stats_dict(self) -> Dict[str, Dict[str, Any]]:
        """Get all stats as dictionary."""
        return {
            d.value: {
                "open_issues": s.open_issues,
                "resolved_issues": s.resolved_issues,
                "avg_resolution_time_hours": s.avg_resolution_time_hours,
                "pending_tasks": s.pending_tasks,
                "completed_tasks": s.completed_tasks,
            }
            for d, s in self._stats.items()
        }

    def get_domain_load(self) -> Dict[Domain, float]:
        """Get load percentage for each domain."""
        return {
            d: s.open_issues / self.config.MAX_CONCURRENT_PER_DOMAIN.get(d, 50)
            for d, s in self._stats.items()
        }

    def suggest_domain_for_load_balancing(self) -> Domain:
        """Suggest a domain with the lowest load for manual routing."""
        loads = self.get_domain_load()
        return min(loads, key=loads.get)


# Singleton instance
_domain_router: Optional[DomainDebunkRouter] = None


def get_domain_debunk_router() -> DomainDebunkRouter:
    """Get singleton domain debunk router instance."""
    global _domain_router
    if _domain_router is None:
        _domain_router = DomainDebunkRouter()
    return _domain_router


def reset_domain_debunk_router() -> None:
    """Reset singleton instance (for testing)."""
    global _domain_router
    _domain_router = None
