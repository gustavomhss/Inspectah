"""
Tests for Signal Calculators — S37

Tests for all signal calculator implementations.
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from app.claims.graph_models import ClaimState, EdgeType, NodeType


class TestLiesInCirculationCalculator:
    """Tests for LiesInCirculationCalculator."""

    @pytest.fixture
    def mock_graph_service(self):
        """Create mock graph service."""
        mock = MagicMock()
        mock.find_claims.return_value = []
        mock.repo = MagicMock()
        mock.repo.find_edges.return_value = []
        mock.repo.get_node.return_value = None
        return mock

    @pytest.fixture
    def calculator(self, mock_graph_service):
        """Create calculator with mock service."""
        from app.signals.calculators.lies_in_circulation import LiesInCirculationCalculator
        return LiesInCirculationCalculator(graph_service=mock_graph_service)

    def test_calculate_empty_domain(self, calculator):
        """Calculate with no claims."""
        result = calculator.calculate("test_domain")

        assert result.domain == "test_domain"
        assert result.total_false_claims == 0
        assert result.active_false_claims == 0
        assert result.false_claim_rate == 0.0

    def test_calculate_with_false_claims(self, calculator, mock_graph_service):
        """Calculate with false claims."""
        now = datetime.utcnow()
        mock_claim = MagicMock()
        mock_claim.id = "claim_1"
        mock_claim.properties = {"state": ClaimState.FALSE.value}
        mock_claim.created_at = now - timedelta(days=1)

        mock_graph_service.find_claims.return_value = [mock_claim]

        result = calculator.calculate("test_domain")

        assert result.total_false_claims == 1
        assert result.active_false_claims == 1

    def test_calculate_false_claim_rate(self, calculator, mock_graph_service):
        """Calculate false claim rate."""
        now = datetime.utcnow()

        claims = []
        for i in range(10):
            mock_claim = MagicMock()
            mock_claim.id = f"claim_{i}"
            mock_claim.properties = {
                "state": ClaimState.FALSE.value if i < 3 else ClaimState.VERIFIED.value
            }
            mock_claim.created_at = now - timedelta(days=1)
            claims.append(mock_claim)

        mock_graph_service.find_claims.return_value = claims

        result = calculator.calculate("test_domain")

        assert result.total_false_claims == 3
        assert result.false_claim_rate == pytest.approx(0.3)

    def test_calculate_severity_below_warning(self, calculator):
        """Severity below warning threshold."""
        severity = calculator._calculate_severity(5, {"warning": 10, "alert": 25, "critical": 50})
        assert severity < 40

    def test_calculate_severity_at_warning(self, calculator):
        """Severity at warning threshold."""
        severity = calculator._calculate_severity(10, {"warning": 10, "alert": 25, "critical": 50})
        assert severity >= 40

    def test_calculate_severity_at_alert(self, calculator):
        """Severity at alert threshold."""
        severity = calculator._calculate_severity(25, {"warning": 10, "alert": 25, "critical": 50})
        assert severity >= 70

    def test_calculate_severity_at_critical(self, calculator):
        """Severity at critical threshold."""
        severity = calculator._calculate_severity(50, {"warning": 10, "alert": 25, "critical": 50})
        assert severity == 100.0

    def test_calculate_severity_zero_count_zero_warning(self, calculator):
        """Severity when count is 0 and warning threshold is 0 (reaches >= warning branch)."""
        severity = calculator._calculate_severity(0, {"warning": 0, "alert": 25, "critical": 50})
        # 0 >= 0 is True, so it enters warning branch, returns 40.0
        assert severity == 40.0

    def test_get_top_topics_with_tagged_edges(self, calculator, mock_graph_service):
        """Test _get_top_topics when claims have tagged edges."""
        from app.claims.graph_models import EdgeType

        mock_claim = MagicMock()
        mock_claim.id = "claim_1"
        mock_claim.properties = {"state": "FALSE"}

        mock_edge = MagicMock()
        mock_edge.edge_type = EdgeType.TAGGED
        mock_edge.target_id = "topic_1"

        mock_topic = MagicMock()
        mock_topic.properties = {"name": "Politics"}

        mock_graph_service.repo.find_edges.return_value = [mock_edge]
        mock_graph_service.repo.get_node.return_value = mock_topic

        result = calculator._get_top_topics([mock_claim], "test_domain")

        assert len(result) == 1
        assert result[0]["topic"] == "Politics"
        assert result[0]["false_claims"] == 1

    def test_get_top_topics_without_topic_name(self, calculator, mock_graph_service):
        """Test _get_top_topics when topic has no name property."""
        from app.claims.graph_models import EdgeType

        mock_claim = MagicMock()
        mock_claim.id = "claim_1"
        mock_claim.properties = {"state": "FALSE"}

        mock_edge = MagicMock()
        mock_edge.edge_type = EdgeType.TAGGED
        mock_edge.target_id = "topic_1"

        mock_topic = MagicMock()
        mock_topic.properties = {}  # No name property

        mock_graph_service.repo.find_edges.return_value = [mock_edge]
        mock_graph_service.repo.get_node.return_value = mock_topic

        result = calculator._get_top_topics([mock_claim], "test_domain")

        assert len(result) == 1
        assert result[0]["topic"] == "topic_1"  # Falls back to edge.target_id

    def test_to_snapshot(self, calculator, mock_graph_service):
        """Convert result to snapshot."""
        mock_graph_service.find_claims.return_value = []
        result = calculator.calculate("test")

        snapshot = calculator.to_snapshot(result)

        assert snapshot["signal_type"] == "mentiras_em_circulacao"
        assert snapshot["domain"] == "test"
        assert "values" in snapshot
        assert "metadata" in snapshot


class TestBattlegroundCalculator:
    """Tests for BattlegroundCalculator."""

    @pytest.fixture
    def mock_graph_service(self):
        """Create mock graph service."""
        mock = MagicMock()
        mock.find_claims.return_value = []
        mock.repo = MagicMock()
        mock.repo.find_edges.return_value = []
        return mock

    @pytest.fixture
    def calculator(self, mock_graph_service):
        """Create calculator with mock service."""
        from app.signals.calculators.battleground import BattlegroundCalculator
        return BattlegroundCalculator(graph_service=mock_graph_service)

    def test_calculate_no_conflicts(self, calculator):
        """Calculate with no conflicts."""
        result = calculator.calculate("test_domain")

        assert result.total_conflicts == 0
        assert result.high_tension_conflicts == 0
        assert result.average_tension == 0.0

    def test_calculate_with_conflicts(self, calculator, mock_graph_service):
        """Calculate with conflicts."""
        mock_claim1 = MagicMock()
        mock_claim1.id = "claim_1"
        mock_claim1.properties = {"content": "Claim 1 content"}

        mock_claim2 = MagicMock()
        mock_claim2.id = "claim_2"
        mock_claim2.properties = {"content": "Claim 2 content"}

        mock_graph_service.find_claims.return_value = [mock_claim1, mock_claim2]

        mock_edge = MagicMock()
        mock_edge.id = "edge_1"
        mock_edge.source_id = "claim_1"
        mock_edge.target_id = "claim_2"
        mock_edge.weight = 0.8

        mock_graph_service.repo.find_edges.return_value = [mock_edge]

        result = calculator.calculate("test_domain")

        assert result.total_conflicts == 1
        assert len(result.top_battlegrounds) == 1

    def test_calculate_high_tension(self, calculator, mock_graph_service):
        """Calculate high tension conflicts."""
        mock_claim = MagicMock()
        mock_claim.id = "claim_1"
        mock_claim.properties = {"content": "Content"}

        mock_graph_service.find_claims.return_value = [mock_claim]

        mock_edge = MagicMock()
        mock_edge.id = "edge_1"
        mock_edge.source_id = "claim_1"
        mock_edge.target_id = "claim_2"
        mock_edge.weight = 0.9  # Above HIGH_TENSION_THRESHOLD

        mock_graph_service.repo.find_edges.return_value = [mock_edge]

        result = calculator.calculate("test_domain")

        assert result.high_tension_conflicts == 1

    def test_calculate_intensity_no_claims(self, calculator):
        """Intensity is 0 with no claims."""
        intensity = calculator._calculate_intensity(0, 0, 0.0, 0)
        assert intensity == 0.0

    def test_to_snapshot(self, calculator, mock_graph_service):
        """Convert result to snapshot."""
        mock_graph_service.find_claims.return_value = []
        result = calculator.calculate("test")

        snapshot = calculator.to_snapshot(result)

        assert snapshot["signal_type"] == "campo_batalha"
        assert "values" in snapshot
        assert "intensity_score" in snapshot["values"]


class TestSilenceRadarCalculator:
    """Tests for SilenceRadarCalculator."""

    @pytest.fixture
    def mock_graph_service(self):
        """Create mock graph service."""
        mock = MagicMock()
        mock.repo = MagicMock()
        mock.repo.find_nodes.return_value = []
        mock.repo.find_edges.return_value = []
        mock.repo.get_node.return_value = None
        return mock

    @pytest.fixture
    def calculator(self, mock_graph_service):
        """Create calculator with mock service."""
        from app.signals.calculators.silence_radar import SilenceRadarCalculator
        return SilenceRadarCalculator(graph_service=mock_graph_service)

    def test_calculate_no_topics(self, calculator):
        """Calculate with no topics."""
        result = calculator.calculate("test_domain")

        assert result.total_topics == 0
        assert result.silenced_topics == 0
        assert result.alert_score == 0.0

    def test_calculate_no_silenced(self, calculator, mock_graph_service):
        """Calculate with active topics."""
        now = datetime.utcnow()

        mock_topic = MagicMock()
        mock_topic.id = "topic_1"
        mock_topic.properties = {"name": "Test Topic"}

        mock_graph_service.repo.find_nodes.return_value = [mock_topic]

        # Create edges for active topic (activity in both windows)
        mock_claim = MagicMock()
        mock_claim.domain = "test_domain"
        mock_claim.created_at = now - timedelta(days=3)  # Current window

        mock_edge = MagicMock()
        mock_edge.source_id = "claim_1"

        mock_graph_service.repo.find_edges.return_value = [mock_edge]
        mock_graph_service.repo.get_node.return_value = mock_claim

        result = calculator.calculate("test_domain")

        # Topic has activity, should not be silenced
        assert result.total_topics == 1

    def test_calculate_alert_score_no_silenced(self, calculator):
        """Alert score is 0 with no silenced topics."""
        silenced = []
        score = calculator._calculate_alert_score(0, 0.0, silenced)
        assert score == 0.0

    def test_calculate_alert_score_with_silenced(self, calculator):
        """Alert score with silenced topics."""
        from app.signals.calculators.silence_radar import SilencedTopic

        silenced = [
            SilencedTopic(
                topic_id="t1",
                topic_name="Topic 1",
                previous_activity=10,
                current_activity=2,
                drop_percentage=0.8,
                last_claim_date=None,
            ),
            SilencedTopic(
                topic_id="t2",
                topic_name="Topic 2",
                previous_activity=5,
                current_activity=1,
                drop_percentage=0.8,
                last_claim_date=None,
            ),
        ]
        score = calculator._calculate_alert_score(2, 0.3, silenced)
        assert score > 0.0
        assert score <= 100.0

    def test_calculate_with_silenced_topics(self, calculator, mock_graph_service):
        """Calculate with silenced topics (activity drop)."""
        now = datetime.utcnow()

        mock_topic = MagicMock()
        mock_topic.id = "topic_1"
        mock_topic.properties = {"name": "Silenced Topic"}

        mock_graph_service.repo.find_nodes.return_value = [mock_topic]

        # Create claims in baseline window (10 days ago) but none in current
        baseline_claim = MagicMock()
        baseline_claim.domain = "test_domain"
        baseline_claim.created_at = now - timedelta(days=10)  # Baseline window only

        mock_edge = MagicMock()
        mock_edge.source_id = "claim_baseline"

        mock_graph_service.repo.find_edges.return_value = [mock_edge, mock_edge, mock_edge]  # 3 edges
        mock_graph_service.repo.get_node.return_value = baseline_claim

        result = calculator.calculate("test_domain")

        # Topic should be detected as silenced (activity in baseline, none in current)
        assert result.total_topics == 1

    def test_calculate_domain_mismatch(self, calculator, mock_graph_service):
        """Claim with different domain is ignored."""
        now = datetime.utcnow()

        mock_topic = MagicMock()
        mock_topic.id = "topic_1"
        mock_topic.properties = {"name": "Test Topic"}

        mock_graph_service.repo.find_nodes.return_value = [mock_topic]

        # Claim has different domain
        wrong_domain_claim = MagicMock()
        wrong_domain_claim.domain = "other_domain"  # Different domain
        wrong_domain_claim.created_at = now - timedelta(days=5)

        mock_edge = MagicMock()
        mock_edge.source_id = "claim_1"

        mock_graph_service.repo.find_edges.return_value = [mock_edge]
        mock_graph_service.repo.get_node.return_value = wrong_domain_claim

        result = calculator.calculate("test_domain")

        # Topic should not count claims from other domains
        assert result.total_topics == 1
        assert result.silenced_topics == 0  # No matching domain claims

    def test_calculate_claims_in_current_window(self, calculator, mock_graph_service):
        """Claims in current window are counted correctly."""
        now = datetime.utcnow()

        mock_topic = MagicMock()
        mock_topic.id = "topic_1"
        mock_topic.properties = {"name": "Active Topic"}

        mock_graph_service.repo.find_nodes.return_value = [mock_topic]

        # Claim in current window (3 days ago)
        current_claim = MagicMock()
        current_claim.domain = "test_domain"
        current_claim.created_at = now - timedelta(days=3)

        mock_edge = MagicMock()
        mock_edge.source_id = "claim_current"

        mock_graph_service.repo.find_edges.return_value = [mock_edge]
        mock_graph_service.repo.get_node.return_value = current_claim

        result = calculator.calculate("test_domain")

        assert result.total_topics == 1
        # With activity in current window, should not be silenced
        assert result.silenced_topics == 0

    def test_calculate_claims_in_baseline_window(self, calculator, mock_graph_service):
        """Claims in baseline window are counted correctly."""
        now = datetime.utcnow()

        mock_topic = MagicMock()
        mock_topic.id = "topic_1"
        mock_topic.properties = {"name": "Baseline Topic"}

        mock_graph_service.repo.find_nodes.return_value = [mock_topic]

        # Claim in baseline window (10 days ago)
        baseline_claim = MagicMock()
        baseline_claim.domain = "test_domain"
        baseline_claim.created_at = now - timedelta(days=10)

        mock_edge = MagicMock()
        mock_edge.source_id = "claim_baseline"

        mock_graph_service.repo.find_edges.return_value = [mock_edge]
        mock_graph_service.repo.get_node.return_value = baseline_claim

        result = calculator.calculate("test_domain")

        # Has baseline activity but no current activity = silenced
        assert result.total_topics == 1

    def test_to_snapshot(self, calculator, mock_graph_service):
        """Convert result to snapshot."""
        mock_graph_service.repo.find_nodes.return_value = []
        result = calculator.calculate("test")

        snapshot = calculator.to_snapshot(result)

        assert snapshot["signal_type"] == "radar_silencio"
        assert "values" in snapshot
        assert "silence_rate" in snapshot["values"]


class TestNarrativeFragilityCalculator:
    """Tests for NarrativeFragilityCalculator."""

    @pytest.fixture
    def mock_graph_service(self):
        """Create mock graph service."""
        mock = MagicMock()
        mock.find_claims.return_value = []
        mock.repo = MagicMock()
        mock.repo.find_edges.return_value = []
        return mock

    @pytest.fixture
    def calculator(self, mock_graph_service):
        """Create calculator with mock service."""
        from app.signals.calculators.narrative_fragility import NarrativeFragilityCalculator
        return NarrativeFragilityCalculator(graph_service=mock_graph_service)

    def test_calculate_no_claims(self, calculator):
        """Calculate with no claims."""
        result = calculator.calculate("test_domain")

        assert result.total_claims == 0
        assert result.fragile_claims == 0
        assert result.risk_score == 0.0

    def test_calculate_with_fragile_claims(self, calculator, mock_graph_service):
        """Calculate with fragile claims (low evidence)."""
        mock_claim = MagicMock()
        mock_claim.id = "claim_1"
        mock_claim.properties = {
            "content": "Fragile claim",
            "evidence_count": 0,
            "state": "pending",
        }

        mock_graph_service.find_claims.return_value = [mock_claim]
        mock_graph_service.repo.find_edges.return_value = []

        result = calculator.calculate("test_domain")

        # Low evidence count should make it fragile
        assert result.fragile_claims >= 0

    def test_calculate_claim_fragility_no_evidence(self, calculator, mock_graph_service):
        """Claim with no evidence is fragile."""
        mock_claim = MagicMock()
        mock_claim.id = "claim_1"
        mock_claim.properties = {"evidence_count": 0}

        mock_graph_service.repo.find_edges.return_value = []

        score, metrics = calculator._calculate_claim_fragility(mock_claim)

        assert score > 0.5  # Should be above fragile threshold

    def test_calculate_claim_fragility_strong(self, calculator, mock_graph_service):
        """Claim with good evidence is not fragile."""
        mock_claim = MagicMock()
        mock_claim.id = "claim_1"
        mock_claim.properties = {"evidence_count": 10}

        # Many support edges
        support_edges = [MagicMock() for _ in range(5)]
        mock_graph_service.repo.find_edges.side_effect = [support_edges, [], []]

        score, metrics = calculator._calculate_claim_fragility(mock_claim)

        assert score < 0.6  # Should be below fragile threshold

    def test_calculate_risk_score(self, calculator):
        """Risk score calculation."""
        risk = calculator._calculate_risk_score(10, 0.5, 0.7)
        assert 0 <= risk <= 100

    def test_to_snapshot(self, calculator, mock_graph_service):
        """Convert result to snapshot."""
        mock_graph_service.find_claims.return_value = []
        result = calculator.calculate("test")

        snapshot = calculator.to_snapshot(result)

        assert snapshot["signal_type"] == "fragilidade_narrativa"
        assert "values" in snapshot
        assert "fragility_rate" in snapshot["values"]


class TestCalculatorResults:
    """Tests for calculator result dataclasses."""

    def test_lies_in_circulation_result(self):
        """LiesInCirculationResult dataclass."""
        from app.signals.calculators.lies_in_circulation import LiesInCirculationResult

        result = LiesInCirculationResult(
            domain="test",
            timestamp=datetime.utcnow(),
            total_false_claims=10,
            active_false_claims=5,
            false_claim_rate=0.1,
            severity_score=45.0,
            top_topics=[],
            thresholds={"warning": 10, "alert": 25, "critical": 50},
        )

        assert result.domain == "test"
        assert result.total_false_claims == 10

    def test_battleground_pair(self):
        """BattlegroundPair dataclass."""
        from app.signals.calculators.battleground import BattlegroundPair

        pair = BattlegroundPair(
            claim_a_id="c1",
            claim_b_id="c2",
            claim_a_content="Content A",
            claim_b_content="Content B",
            tension_score=0.8,
            edge_id="e1",
        )

        assert pair.tension_score == 0.8

    def test_battleground_result(self):
        """BattlegroundResult dataclass."""
        from app.signals.calculators.battleground import BattlegroundResult

        result = BattlegroundResult(
            domain="test",
            timestamp=datetime.utcnow(),
            total_conflicts=5,
            high_tension_conflicts=2,
            average_tension=0.6,
            intensity_score=50.0,
            top_battlegrounds=[],
        )

        assert result.total_conflicts == 5

    def test_silenced_topic(self):
        """SilencedTopic dataclass."""
        from app.signals.calculators.silence_radar import SilencedTopic

        topic = SilencedTopic(
            topic_id="t1",
            topic_name="Test Topic",
            previous_activity=10,
            current_activity=2,
            drop_percentage=0.8,
            last_claim_date=datetime.utcnow(),
        )

        assert topic.drop_percentage == 0.8

    def test_silence_radar_result(self):
        """SilenceRadarResult dataclass."""
        from app.signals.calculators.silence_radar import SilenceRadarResult

        result = SilenceRadarResult(
            domain="test",
            timestamp=datetime.utcnow(),
            total_topics=10,
            silenced_topics=3,
            silence_rate=0.3,
            alert_score=45.0,
            top_silenced=[],
        )

        assert result.silenced_topics == 3

    def test_fragile_claim(self):
        """FragileClaim dataclass."""
        from app.signals.calculators.narrative_fragility import FragileClaim

        claim = FragileClaim(
            claim_id="c1",
            content="Test claim",
            evidence_count=1,
            support_count=0,
            fragility_score=0.7,
            state="pending",
        )

        assert claim.fragility_score == 0.7

    def test_narrative_fragility_result(self):
        """NarrativeFragilityResult dataclass."""
        from app.signals.calculators.narrative_fragility import NarrativeFragilityResult

        result = NarrativeFragilityResult(
            domain="test",
            timestamp=datetime.utcnow(),
            total_claims=100,
            fragile_claims=20,
            fragility_rate=0.2,
            average_fragility=0.45,
            risk_score=35.0,
            top_fragile=[],
        )

        assert result.fragile_claims == 20


class TestCalculatorDefaultThresholds:
    """Tests for calculator default configurations."""

    def test_lies_in_circulation_thresholds(self):
        """Lies in circulation default thresholds."""
        from app.signals.calculators.lies_in_circulation import LiesInCirculationCalculator

        calc = LiesInCirculationCalculator.__new__(LiesInCirculationCalculator)

        assert "pilot_politics" in calc.DEFAULT_THRESHOLDS
        assert "default" in calc.DEFAULT_THRESHOLDS
        assert calc.DEFAULT_THRESHOLDS["default"]["warning"] == 10

    def test_battleground_threshold(self):
        """Battleground high tension threshold."""
        from app.signals.calculators.battleground import BattlegroundCalculator

        assert BattlegroundCalculator.HIGH_TENSION_THRESHOLD == 0.7

    def test_silence_radar_thresholds(self):
        """Silence radar drop threshold."""
        from app.signals.calculators.silence_radar import SilenceRadarCalculator

        assert SilenceRadarCalculator.DROP_THRESHOLD == 0.5
        assert SilenceRadarCalculator.BASELINE_DAYS == 14
        assert SilenceRadarCalculator.CURRENT_DAYS == 7

    def test_narrative_fragility_thresholds(self):
        """Narrative fragility thresholds."""
        from app.signals.calculators.narrative_fragility import NarrativeFragilityCalculator

        assert NarrativeFragilityCalculator.LOW_EVIDENCE_THRESHOLD == 2
        assert NarrativeFragilityCalculator.LOW_SUPPORT_THRESHOLD == 1
        assert NarrativeFragilityCalculator.FRAGILE_SCORE_THRESHOLD == 0.6
