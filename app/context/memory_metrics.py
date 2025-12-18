"""
S39 - Memory Metrics for Dashboard Integration

Provides memory-specific metrics collection and health monitoring
that integrates with the ops dashboard.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from app.context.memory_controller import (
    MemoryController,
    MemoryScope,
    MemoryStats,
    MemoryType,
    RetentionPolicy,
)
from app.ops.dashboard_service import (
    AlertSeverity,
    HealthStatus,
    MetricType,
    MetricValue,
)

logger = logging.getLogger(__name__)


class MemoryHealthStatus(str, Enum):
    """Status de saude do sistema de memoria."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class MemoryHealthThresholds:
    """Thresholds for memory health checks."""
    max_entries_warning: int = 5000
    max_entries_critical: int = 10000
    max_expired_ratio_warning: float = 0.2
    max_expired_ratio_critical: float = 0.5
    min_avg_importance_warning: float = 0.3
    max_single_scope_ratio: float = 0.8


@dataclass
class MemoryHealthIssue:
    """An identified issue with memory health."""
    issue_type: str
    severity: AlertSeverity
    message: str
    metric_name: str
    current_value: float
    threshold: float


@dataclass
class MemoryHealthReport:
    """Full health report for memory system."""
    status: MemoryHealthStatus
    score: float  # 0-100
    issues: List[MemoryHealthIssue]
    recommendations: List[str]
    stats: MemoryStats
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "score": round(self.score, 2),
            "issues": [
                {
                    "type": i.issue_type,
                    "severity": i.severity.value,
                    "message": i.message,
                    "metric_name": i.metric_name,
                    "current_value": i.current_value,
                    "threshold": i.threshold,
                }
                for i in self.issues
            ],
            "recommendations": self.recommendations,
            "stats": {
                "total_entries": self.stats.total_entries,
                "active_entries": self.stats.active_entries,
                "expired_entries": self.stats.expired_entries,
                "by_scope": self.stats.by_scope,
                "by_type": self.stats.by_type,
                "by_retention": self.stats.by_retention,
                "total_access_count": self.stats.total_access_count,
                "avg_importance": round(self.stats.avg_importance, 4),
            },
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class MemoryTrendPoint:
    """A point in memory usage trend."""
    timestamp: datetime
    total_entries: int
    active_entries: int
    expired_entries: int
    avg_importance: float


class MemoryMetricsCollector:
    """
    Collects memory-related metrics for the ops dashboard.

    Provides:
    - Memory usage metrics (entries, by scope, by type)
    - Health monitoring with configurable thresholds
    - Trend tracking over time
    - Integration with dashboard alerting

    Usage:
        controller = MemoryController()
        collector = MemoryMetricsCollector(controller)

        # Get metrics for dashboard
        metrics = collector.collect_metrics()

        # Get health report
        report = collector.get_health_report()

        # Check for alerts
        alerts = collector.check_alerts()
    """

    def __init__(
        self,
        memory_controller: MemoryController,
        thresholds: Optional[MemoryHealthThresholds] = None,
        trend_window_minutes: int = 60,
        trend_interval_minutes: int = 5,
    ):
        self.controller = memory_controller
        self.thresholds = thresholds or MemoryHealthThresholds()
        self.trend_window_minutes = trend_window_minutes
        self.trend_interval_minutes = trend_interval_minutes
        self._trend_history: List[MemoryTrendPoint] = []
        self._max_trend_points = trend_window_minutes // trend_interval_minutes

    def collect_metrics(self) -> List[MetricValue]:
        """
        Collect memory metrics for the dashboard.

        Returns:
            List of MetricValue objects for dashboard display.
        """
        stats = self.controller.get_stats()
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        metrics = []

        # Total entries
        metrics.append(MetricValue(
            name="memory_entries_total",
            metric_type=MetricType.GAUGE,
            value=float(stats.total_entries),
            timestamp=now,
            labels={},
            unit="entries",
        ))

        # Active vs expired
        metrics.append(MetricValue(
            name="memory_entries_active",
            metric_type=MetricType.GAUGE,
            value=float(stats.active_entries),
            timestamp=now,
            labels={},
            unit="entries",
        ))

        metrics.append(MetricValue(
            name="memory_entries_expired",
            metric_type=MetricType.GAUGE,
            value=float(stats.expired_entries),
            timestamp=now,
            labels={},
            unit="entries",
        ))

        # By scope
        for scope, count in stats.by_scope.items():
            metrics.append(MetricValue(
                name="memory_entries_by_scope",
                metric_type=MetricType.GAUGE,
                value=float(count),
                timestamp=now,
                labels={"scope": scope},
                unit="entries",
            ))

        # By type
        for mem_type, count in stats.by_type.items():
            metrics.append(MetricValue(
                name="memory_entries_by_type",
                metric_type=MetricType.GAUGE,
                value=float(count),
                timestamp=now,
                labels={"type": mem_type},
                unit="entries",
            ))

        # By retention
        for retention, count in stats.by_retention.items():
            metrics.append(MetricValue(
                name="memory_entries_by_retention",
                metric_type=MetricType.GAUGE,
                value=float(count),
                timestamp=now,
                labels={"retention": retention},
                unit="entries",
            ))

        # Access stats
        metrics.append(MetricValue(
            name="memory_total_accesses",
            metric_type=MetricType.COUNTER,
            value=float(stats.total_access_count),
            timestamp=now,
            labels={},
            unit="accesses",
        ))

        metrics.append(MetricValue(
            name="memory_avg_importance",
            metric_type=MetricType.GAUGE,
            value=stats.avg_importance,
            timestamp=now,
            labels={},
            unit="score",
        ))

        # Derived metrics
        if stats.total_entries > 0:
            expired_ratio = stats.expired_entries / stats.total_entries
            metrics.append(MetricValue(
                name="memory_expired_ratio",
                metric_type=MetricType.GAUGE,
                value=expired_ratio,
                timestamp=now,
                labels={},
                unit="ratio",
            ))

        return metrics

    def get_health_report(self) -> MemoryHealthReport:
        """
        Generate a comprehensive health report for the memory system.

        Returns:
            MemoryHealthReport with status, score, issues, and recommendations.
        """
        stats = self.controller.get_stats()
        issues: List[MemoryHealthIssue] = []
        recommendations: List[str] = []
        score = 100.0

        # Check total entries
        if stats.total_entries >= self.thresholds.max_entries_critical:
            issues.append(MemoryHealthIssue(
                issue_type="high_entry_count",
                severity=AlertSeverity.CRITICAL,
                message=f"Memory entries critical: {stats.total_entries}",
                metric_name="total_entries",
                current_value=float(stats.total_entries),
                threshold=float(self.thresholds.max_entries_critical),
            ))
            recommendations.append("Run memory cleanup immediately")
            score -= 30
        elif stats.total_entries >= self.thresholds.max_entries_warning:
            issues.append(MemoryHealthIssue(
                issue_type="high_entry_count",
                severity=AlertSeverity.WARNING,
                message=f"Memory entries high: {stats.total_entries}",
                metric_name="total_entries",
                current_value=float(stats.total_entries),
                threshold=float(self.thresholds.max_entries_warning),
            ))
            recommendations.append("Consider scheduling memory cleanup")
            score -= 15

        # Check expired ratio
        if stats.total_entries > 0:
            expired_ratio = stats.expired_entries / stats.total_entries

            if expired_ratio >= self.thresholds.max_expired_ratio_critical:
                issues.append(MemoryHealthIssue(
                    issue_type="high_expired_ratio",
                    severity=AlertSeverity.CRITICAL,
                    message=f"Expired entries ratio critical: {expired_ratio:.1%}",
                    metric_name="expired_ratio",
                    current_value=expired_ratio,
                    threshold=self.thresholds.max_expired_ratio_critical,
                ))
                recommendations.append("Run cleanup_expired() immediately")
                score -= 25
            elif expired_ratio >= self.thresholds.max_expired_ratio_warning:
                issues.append(MemoryHealthIssue(
                    issue_type="high_expired_ratio",
                    severity=AlertSeverity.WARNING,
                    message=f"Expired entries ratio high: {expired_ratio:.1%}",
                    metric_name="expired_ratio",
                    current_value=expired_ratio,
                    threshold=self.thresholds.max_expired_ratio_warning,
                ))
                recommendations.append("Schedule cleanup_expired() task")
                score -= 10

        # Check importance
        if stats.total_entries > 0 and stats.avg_importance < self.thresholds.min_avg_importance_warning:
            issues.append(MemoryHealthIssue(
                issue_type="low_importance",
                severity=AlertSeverity.INFO,
                message=f"Average importance low: {stats.avg_importance:.2f}",
                metric_name="avg_importance",
                current_value=stats.avg_importance,
                threshold=self.thresholds.min_avg_importance_warning,
            ))
            recommendations.append("Review memory entries for relevance")
            score -= 5

        # Check scope concentration
        if stats.by_scope and stats.total_entries > 0:
            max_scope_count = max(stats.by_scope.values())
            max_scope_ratio = max_scope_count / stats.total_entries
            if max_scope_ratio > self.thresholds.max_single_scope_ratio:
                max_scope = max(stats.by_scope, key=stats.by_scope.get)
                issues.append(MemoryHealthIssue(
                    issue_type="scope_concentration",
                    severity=AlertSeverity.WARNING,
                    message=f"Scope '{max_scope}' has {max_scope_ratio:.1%} of entries",
                    metric_name="scope_concentration",
                    current_value=max_scope_ratio,
                    threshold=self.thresholds.max_single_scope_ratio,
                ))
                recommendations.append(f"Review entries in scope '{max_scope}'")
                score -= 10

        # Determine status
        if score >= 80:
            status = MemoryHealthStatus.HEALTHY
        elif score >= 50:
            status = MemoryHealthStatus.WARNING
        else:
            status = MemoryHealthStatus.CRITICAL

        return MemoryHealthReport(
            status=status,
            score=max(0, score),
            issues=issues,
            recommendations=recommendations,
            stats=stats,
        )

    def check_alerts(self) -> List[Dict[str, Any]]:
        """
        Check for conditions that should trigger alerts.

        Returns:
            List of alert dictionaries with name, severity, message, component.
        """
        report = self.get_health_report()
        alerts = []

        for issue in report.issues:
            if issue.severity in (AlertSeverity.WARNING, AlertSeverity.ERROR, AlertSeverity.CRITICAL):
                alerts.append({
                    "name": f"memory_{issue.issue_type}",
                    "severity": issue.severity,
                    "message": issue.message,
                    "component": "memory_controller",
                    "metadata": {
                        "metric_name": issue.metric_name,
                        "current_value": issue.current_value,
                        "threshold": issue.threshold,
                    },
                })

        return alerts

    def record_trend_point(self) -> MemoryTrendPoint:
        """
        Record current memory state for trend analysis.

        Returns:
            The recorded trend point.
        """
        stats = self.controller.get_stats()
        point = MemoryTrendPoint(
            timestamp=datetime.now(timezone.utc),
            total_entries=stats.total_entries,
            active_entries=stats.active_entries,
            expired_entries=stats.expired_entries,
            avg_importance=stats.avg_importance,
        )

        self._trend_history.append(point)

        # Keep only recent history
        if len(self._trend_history) > self._max_trend_points:
            self._trend_history = self._trend_history[-self._max_trend_points:]

        return point

    def get_trend(self, minutes: Optional[int] = None) -> List[MemoryTrendPoint]:
        """
        Get memory usage trend.

        Args:
            minutes: Number of minutes to look back (default: all available)

        Returns:
            List of trend points within the time window.
        """
        if minutes is None:
            return list(self._trend_history)

        cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        return [p for p in self._trend_history if p.timestamp >= cutoff]

    def get_trend_summary(self) -> Dict[str, Any]:
        """
        Get summary of memory trends.

        Returns:
            Dictionary with trend statistics.
        """
        if not self._trend_history:
            return {
                "points": 0,
                "window_minutes": self.trend_window_minutes,
                "trend_direction": "unknown",
                "growth_rate": 0.0,
            }

        points = self._trend_history
        first = points[0]
        last = points[-1]

        # Calculate growth rate
        time_diff = (last.timestamp - first.timestamp).total_seconds() / 3600  # hours
        if time_diff > 0 and first.total_entries > 0:
            growth_rate = (last.total_entries - first.total_entries) / first.total_entries / time_diff
        else:
            growth_rate = 0.0

        # Determine trend direction
        if growth_rate > 0.1:
            direction = "growing_fast"
        elif growth_rate > 0.01:
            direction = "growing"
        elif growth_rate < -0.1:
            direction = "shrinking_fast"
        elif growth_rate < -0.01:
            direction = "shrinking"
        else:
            direction = "stable"

        return {
            "points": len(points),
            "window_minutes": self.trend_window_minutes,
            "trend_direction": direction,
            "growth_rate": round(growth_rate, 4),
            "start_entries": first.total_entries,
            "current_entries": last.total_entries,
            "start_time": first.timestamp.isoformat(),
            "end_time": last.timestamp.isoformat(),
        }

    def get_scope_breakdown(self) -> Dict[str, Dict[str, Any]]:
        """
        Get detailed breakdown by scope.

        Returns:
            Dictionary with scope -> {count, percentage, entries}.
        """
        stats = self.controller.get_stats()
        breakdown = {}

        total = stats.total_entries or 1  # Avoid division by zero

        for scope in MemoryScope:
            count = stats.by_scope.get(scope.value, 0)
            breakdown[scope.value] = {
                "count": count,
                "percentage": round(count / total * 100, 2),
            }

        return breakdown

    def get_type_breakdown(self) -> Dict[str, Dict[str, Any]]:
        """
        Get detailed breakdown by memory type.

        Returns:
            Dictionary with type -> {count, percentage}.
        """
        stats = self.controller.get_stats()
        breakdown = {}

        total = stats.total_entries or 1

        for mem_type in MemoryType:
            count = stats.by_type.get(mem_type.value, 0)
            breakdown[mem_type.value] = {
                "count": count,
                "percentage": round(count / total * 100, 2),
            }

        return breakdown

    def get_retention_breakdown(self) -> Dict[str, Dict[str, Any]]:
        """
        Get detailed breakdown by retention policy.

        Returns:
            Dictionary with retention -> {count, percentage}.
        """
        stats = self.controller.get_stats()
        breakdown = {}

        total = stats.total_entries or 1

        for retention in RetentionPolicy:
            count = stats.by_retention.get(retention.value, 0)
            breakdown[retention.value] = {
                "count": count,
                "percentage": round(count / total * 100, 2),
            }

        return breakdown

    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get all data needed for dashboard display.

        Returns:
            Complete dashboard data dictionary.
        """
        report = self.get_health_report()

        return {
            "health": {
                "status": report.status.value,
                "score": report.score,
                "issues_count": len(report.issues),
            },
            "metrics": {
                "total_entries": report.stats.total_entries,
                "active_entries": report.stats.active_entries,
                "expired_entries": report.stats.expired_entries,
                "avg_importance": round(report.stats.avg_importance, 4),
                "total_accesses": report.stats.total_access_count,
            },
            "breakdowns": {
                "by_scope": self.get_scope_breakdown(),
                "by_type": self.get_type_breakdown(),
                "by_retention": self.get_retention_breakdown(),
            },
            "trend": self.get_trend_summary(),
            "issues": [i.message for i in report.issues],
            "recommendations": report.recommendations,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def reset_trends(self) -> None:
        """Clear trend history."""
        self._trend_history.clear()

    def get_prometheus_metrics(self) -> str:
        """
        Export metrics in Prometheus text format.

        Returns:
            Prometheus metrics string.
        """
        lines = []
        stats = self.controller.get_stats()

        # Memory entries
        lines.append("# HELP memory_entries_total Total memory entries")
        lines.append("# TYPE memory_entries_total gauge")
        lines.append(f"memory_entries_total {stats.total_entries}")

        lines.append("# HELP memory_entries_active Active memory entries")
        lines.append("# TYPE memory_entries_active gauge")
        lines.append(f"memory_entries_active {stats.active_entries}")

        lines.append("# HELP memory_entries_expired Expired memory entries")
        lines.append("# TYPE memory_entries_expired gauge")
        lines.append(f"memory_entries_expired {stats.expired_entries}")

        # By scope
        lines.append("# HELP memory_entries_by_scope Memory entries by scope")
        lines.append("# TYPE memory_entries_by_scope gauge")
        for scope, count in stats.by_scope.items():
            lines.append(f'memory_entries_by_scope{{scope="{scope}"}} {count}')

        # By type
        lines.append("# HELP memory_entries_by_type Memory entries by type")
        lines.append("# TYPE memory_entries_by_type gauge")
        for mem_type, count in stats.by_type.items():
            lines.append(f'memory_entries_by_type{{type="{mem_type}"}} {count}')

        # Health
        report = self.get_health_report()
        lines.append("# HELP memory_health_score Memory health score (0-100)")
        lines.append("# TYPE memory_health_score gauge")
        lines.append(f"memory_health_score {report.score}")

        lines.append("# HELP memory_health_issues Number of health issues")
        lines.append("# TYPE memory_health_issues gauge")
        lines.append(f"memory_health_issues {len(report.issues)}")

        return "\n".join(lines)

    def get_change_since_last_point(self) -> Optional[Dict[str, Any]]:
        """
        Get change in metrics since last trend point.

        Returns:
            Dictionary with absolute and percentage changes, or None if no history.
        """
        if len(self._trend_history) < 2:
            return None

        prev = self._trend_history[-2]
        curr = self._trend_history[-1]

        def pct_change(old: float, new: float) -> float:
            if old == 0:
                return 0.0 if new == 0 else 100.0
            return ((new - old) / old) * 100

        return {
            "entries": {
                "previous": prev.total_entries,
                "current": curr.total_entries,
                "change": curr.total_entries - prev.total_entries,
                "change_pct": round(pct_change(prev.total_entries, curr.total_entries), 2),
            },
            "active": {
                "previous": prev.active_entries,
                "current": curr.active_entries,
                "change": curr.active_entries - prev.active_entries,
                "change_pct": round(pct_change(prev.active_entries, curr.active_entries), 2),
            },
            "expired": {
                "previous": prev.expired_entries,
                "current": curr.expired_entries,
                "change": curr.expired_entries - prev.expired_entries,
                "change_pct": round(pct_change(prev.expired_entries, curr.expired_entries), 2),
            },
            "importance": {
                "previous": round(prev.avg_importance, 4),
                "current": round(curr.avg_importance, 4),
                "change": round(curr.avg_importance - prev.avg_importance, 4),
            },
            "time_delta_seconds": (curr.timestamp - prev.timestamp).total_seconds(),
        }


# Singleton instance
_memory_metrics: Optional[MemoryMetricsCollector] = None


def get_memory_metrics(
    controller: Optional[MemoryController] = None,
) -> MemoryMetricsCollector:
    """Get singleton memory metrics collector."""
    global _memory_metrics
    if _memory_metrics is None:
        if controller is None:
            from app.context.memory_controller import MemoryController
            controller = MemoryController()
        _memory_metrics = MemoryMetricsCollector(controller)
    return _memory_metrics


def reset_memory_metrics() -> None:
    """Reset singleton instance (for testing)."""
    global _memory_metrics
    _memory_metrics = None
