"""
Tests for Domain-Based Debunker Router.

S39 - Domain Routing Tests
"""
import pytest

from app.data.sharding.router import Domain
from app.debunk.domain_router import (
    DebunkPriority,
    DomainDebunkConfig,
    DomainDebunkStats,
    DomainDebunkResult,
    DomainDebunkRouter,
    get_domain_debunk_router,
    reset_domain_debunk_router,
)


class TestDebunkPriority:
    """Tests for DebunkPriority enum."""

    def test_priority_values(self):
        """Test priority enum values."""
        assert DebunkPriority.CRITICAL.value == "critical"
        assert DebunkPriority.HIGH.value == "high"
        assert DebunkPriority.MEDIUM.value == "medium"
        assert DebunkPriority.LOW.value == "low"


class TestDomainDebunkConfig:
    """Tests for DomainDebunkConfig."""

    def test_priority_multipliers(self):
        """Test default priority multipliers."""
        config = DomainDebunkConfig()

        assert Domain.POLITICA in config.PRIORITY_MULTIPLIERS
        assert Domain.SAUDE in config.PRIORITY_MULTIPLIERS
        assert config.PRIORITY_MULTIPLIERS[Domain.POLITICA] > 1.0

    def test_urgent_keywords(self):
        """Test urgent keywords configuration."""
        config = DomainDebunkConfig()

        assert "eleição" in config.URGENT_KEYWORDS[Domain.POLITICA]
        assert "vacina" in config.URGENT_KEYWORDS[Domain.SAUDE]

    def test_max_concurrent(self):
        """Test max concurrent limits."""
        config = DomainDebunkConfig()

        assert config.MAX_CONCURRENT_PER_DOMAIN[Domain.POLITICA] > 0
        assert config.MAX_CONCURRENT_PER_DOMAIN[Domain.DEFAULT] > 0


class TestDomainDebunkStats:
    """Tests for DomainDebunkStats."""

    def test_create_stats(self):
        """Test creating stats."""
        stats = DomainDebunkStats(domain=Domain.POLITICA)

        assert stats.domain == Domain.POLITICA
        assert stats.open_issues == 0
        assert stats.resolved_issues == 0

    def test_stats_with_values(self):
        """Test stats with values."""
        stats = DomainDebunkStats(
            domain=Domain.SAUDE,
            open_issues=10,
            resolved_issues=50,
            avg_resolution_time_hours=24.5,
        )

        assert stats.open_issues == 10
        assert stats.resolved_issues == 50
        assert stats.avg_resolution_time_hours == 24.5


class TestDomainDebunkResult:
    """Tests for DomainDebunkResult."""

    def test_create_result(self):
        """Test creating result."""
        result = DomainDebunkResult(
            domain=Domain.POLITICA,
            priority=DebunkPriority.HIGH,
            priority_score=85.0,
            is_urgent=True,
            routing_reason="Test reason",
            matched_keywords=["eleição"],
        )

        assert result.domain == Domain.POLITICA
        assert result.priority == DebunkPriority.HIGH
        assert result.is_urgent is True

    def test_to_dict(self):
        """Test converting result to dict."""
        result = DomainDebunkResult(
            domain=Domain.SAUDE,
            priority=DebunkPriority.CRITICAL,
            priority_score=120.0,
            is_urgent=True,
            routing_reason="Urgent health claim",
            matched_keywords=["vacina", "covid"],
        )

        d = result.to_dict()

        assert d["domain"] == "saude"
        assert d["priority"] == "critical"
        assert d["is_urgent"] is True
        assert "vacina" in d["matched_keywords"]


class TestDomainDebunkRouter:
    """Tests for DomainDebunkRouter."""

    @pytest.fixture
    def router(self):
        """Create fresh router."""
        return DomainDebunkRouter()

    def test_create_router(self, router):
        """Test creating router."""
        assert router is not None
        assert len(router._stats) == 4  # 4 domains

    def test_detect_domain_politica(self, router):
        """Test detecting politica domain."""
        text = "Lula anuncia novo programa do governo"
        domain = router.detect_domain(text)

        assert domain == Domain.POLITICA

    def test_detect_domain_saude(self, router):
        """Test detecting saude domain."""
        text = "Nova vacina contra covid aprovada pela Anvisa"
        domain = router.detect_domain(text)

        assert domain == Domain.SAUDE

    def test_detect_domain_economia(self, router):
        """Test detecting economia domain."""
        text = "Banco Central aumenta juros da Selic"
        domain = router.detect_domain(text)

        assert domain == Domain.ECONOMIA

    def test_detect_domain_default(self, router):
        """Test default domain for unrecognized text."""
        text = "Texto genérico sem palavras-chave específicas"
        domain = router.detect_domain(text)

        assert domain == Domain.DEFAULT

    def test_calculate_priority_critical(self, router):
        """Test critical priority calculation."""
        priority, score = router.calculate_priority(
            "Fraude eleitoral confirmada",
            Domain.POLITICA,
            "critical",
        )

        assert priority == DebunkPriority.CRITICAL
        assert score >= 100

    def test_calculate_priority_high(self, router):
        """Test high priority calculation."""
        priority, score = router.calculate_priority(
            "Novo medicamento",
            Domain.SAUDE,
            "high",
        )

        assert priority in [DebunkPriority.HIGH, DebunkPriority.CRITICAL]

    def test_calculate_priority_medium(self, router):
        """Test medium priority calculation."""
        priority, score = router.calculate_priority(
            "Generic text",
            Domain.DEFAULT,
            "medium",
        )

        assert priority in [DebunkPriority.MEDIUM, DebunkPriority.LOW]

    def test_calculate_priority_low(self, router):
        """Test low priority calculation."""
        priority, score = router.calculate_priority(
            "Generic text",
            Domain.DEFAULT,
            "low",
        )

        assert priority == DebunkPriority.LOW

    def test_calculate_priority_urgent_boost(self, router):
        """Test priority boost for urgent keywords."""
        # Without urgent keyword
        _, score1 = router.calculate_priority(
            "Notícia sobre política",
            Domain.POLITICA,
            "high",
        )

        # With urgent keyword
        _, score2 = router.calculate_priority(
            "Fraude eleitoral nas urnas",
            Domain.POLITICA,
            "high",
        )

        assert score2 > score1

    def test_check_urgency_urgent(self, router):
        """Test urgency check for urgent claim."""
        is_urgent, keywords = router.check_urgency(
            "Vacina covid causa efeitos colaterais graves",
            Domain.SAUDE,
        )

        assert is_urgent is True
        assert len(keywords) > 0

    def test_check_urgency_not_urgent(self, router):
        """Test urgency check for non-urgent claim."""
        is_urgent, keywords = router.check_urgency(
            "Novo produto lançado no mercado",
            Domain.DEFAULT,
        )

        assert is_urgent is False
        assert len(keywords) == 0

    def test_route_auto_detect(self, router):
        """Test routing with auto domain detection."""
        result = router.route(
            "Bolsonaro faz declaração polêmica",
            risk_level="high",
        )

        assert result.domain == Domain.POLITICA
        assert result.priority in [DebunkPriority.HIGH, DebunkPriority.CRITICAL]
        assert "Auto-detected" in result.routing_reason

    def test_route_explicit_domain(self, router):
        """Test routing with explicit domain."""
        result = router.route(
            "Generic text about something",
            risk_level="medium",
            domain=Domain.ECONOMIA,
        )

        assert result.domain == Domain.ECONOMIA
        assert "Explicit domain" in result.routing_reason

    def test_route_urgent_claim(self, router):
        """Test routing urgent claim."""
        result = router.route(
            "Vacina causa autismo - fake news perigosa",
            risk_level="critical",
        )

        assert result.domain == Domain.SAUDE
        assert result.is_urgent is True
        assert result.priority == DebunkPriority.CRITICAL

    def test_register_handler(self, router):
        """Test registering a handler."""
        def dummy_handler():
            pass

        router.register_handler(Domain.POLITICA, dummy_handler)

        handlers = router.get_handlers(Domain.POLITICA)
        assert dummy_handler in handlers

    def test_get_handlers_empty(self, router):
        """Test getting handlers when none registered."""
        handlers = router.get_handlers(Domain.DEFAULT)
        assert handlers == []

    def test_can_accept_issue(self, router):
        """Test can accept issue check."""
        # Should be able to accept when no issues open
        assert router.can_accept_issue(Domain.POLITICA) is True

    def test_can_accept_issue_at_limit(self, router):
        """Test can accept issue at limit."""
        # Open max issues
        for _ in range(100):
            router.record_issue_opened(Domain.POLITICA)

        # Should not be able to accept more
        assert router.can_accept_issue(Domain.POLITICA) is False

    def test_record_issue_opened(self, router):
        """Test recording issue opened."""
        router.record_issue_opened(Domain.SAUDE)
        router.record_issue_opened(Domain.SAUDE)

        stats = router.get_stats(Domain.SAUDE)[0]
        assert stats.open_issues == 2

    def test_record_issue_resolved(self, router):
        """Test recording issue resolved."""
        router.record_issue_opened(Domain.ECONOMIA)
        router.record_issue_opened(Domain.ECONOMIA)
        router.record_issue_resolved(Domain.ECONOMIA, 24.0)

        stats = router.get_stats(Domain.ECONOMIA)[0]
        assert stats.open_issues == 1
        assert stats.resolved_issues == 1
        assert stats.avg_resolution_time_hours == 24.0

    def test_record_issue_resolved_avg_time(self, router):
        """Test average resolution time calculation."""
        router.record_issue_opened(Domain.POLITICA)
        router.record_issue_opened(Domain.POLITICA)

        router.record_issue_resolved(Domain.POLITICA, 10.0)
        router.record_issue_resolved(Domain.POLITICA, 20.0)

        stats = router.get_stats(Domain.POLITICA)[0]
        assert stats.avg_resolution_time_hours == 15.0  # (10 + 20) / 2

    def test_record_task_created(self, router):
        """Test recording task created."""
        router.record_task_created(Domain.SAUDE)

        stats = router.get_stats(Domain.SAUDE)[0]
        assert stats.pending_tasks == 1

    def test_record_task_completed(self, router):
        """Test recording task completed."""
        router.record_task_created(Domain.DEFAULT)
        router.record_task_completed(Domain.DEFAULT)

        stats = router.get_stats(Domain.DEFAULT)[0]
        assert stats.pending_tasks == 0
        assert stats.completed_tasks == 1

    def test_get_stats_all(self, router):
        """Test getting all stats."""
        stats = router.get_stats()
        assert len(stats) == 4

    def test_get_stats_single(self, router):
        """Test getting stats for single domain."""
        stats = router.get_stats(Domain.POLITICA)
        assert len(stats) == 1
        assert stats[0].domain == Domain.POLITICA

    def test_get_stats_dict(self, router):
        """Test getting stats as dict."""
        router.record_issue_opened(Domain.SAUDE)

        stats = router.get_stats_dict()

        assert "saude" in stats
        assert stats["saude"]["open_issues"] == 1

    def test_get_domain_load(self, router):
        """Test getting domain load."""
        router.record_issue_opened(Domain.POLITICA)

        loads = router.get_domain_load()

        assert Domain.POLITICA in loads
        assert loads[Domain.POLITICA] > 0

    def test_suggest_domain_for_load_balancing(self, router):
        """Test suggesting domain for load balancing."""
        # Load up one domain
        for _ in range(50):
            router.record_issue_opened(Domain.POLITICA)

        # Suggested domain should not be POLITICA
        suggested = router.suggest_domain_for_load_balancing()
        assert suggested != Domain.POLITICA

    def test_record_issue_resolved_no_negative(self, router):
        """Test that open issues don't go negative."""
        router.record_issue_resolved(Domain.DEFAULT, 10.0)

        stats = router.get_stats(Domain.DEFAULT)[0]
        assert stats.open_issues == 0

    def test_record_task_completed_no_negative(self, router):
        """Test that pending tasks don't go negative."""
        router.record_task_completed(Domain.DEFAULT)

        stats = router.get_stats(Domain.DEFAULT)[0]
        assert stats.pending_tasks == 0

    def test_get_handlers_unknown_domain_returns_empty(self, router):
        """Test getting handlers returns empty list for unknown/unregistered."""
        handlers = router.get_handlers(Domain.ECONOMIA)
        assert handlers == []


class TestSingleton:
    """Tests for singleton functions."""

    def test_get_domain_debunk_router(self):
        """Test getting singleton."""
        reset_domain_debunk_router()
        router1 = get_domain_debunk_router()
        router2 = get_domain_debunk_router()

        assert router1 is router2

    def test_reset_domain_debunk_router(self):
        """Test resetting singleton."""
        router1 = get_domain_debunk_router()
        reset_domain_debunk_router()
        router2 = get_domain_debunk_router()

        assert router1 is not router2
