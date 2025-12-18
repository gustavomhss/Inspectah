"""
Tests for agents/trace_repository — S37

Additional tests for trace repository to increase coverage.
"""

import pytest
from datetime import datetime, timezone
from pathlib import Path

from app.agents.trace_repository import (
    TraceRepository,
    AgentTrace,
    ReasoningStep,
    CommitteeTrace,
    TraceLinkRefs,
    _deserialize_dt,
    _json_loads,
    _json_dumps,
    _serialize_dt,
)


class TestDeserializeDt:
    """Tests for _deserialize_dt function."""

    def test_deserialize_dt_none(self):
        """Return None for None input."""
        result = _deserialize_dt(None)
        assert result is None

    def test_deserialize_dt_empty(self):
        """Return None for empty string."""
        result = _deserialize_dt("")
        assert result is None

    def test_deserialize_dt_valid(self):
        """Parse valid ISO datetime."""
        result = _deserialize_dt("2024-01-15T10:30:00+00:00")
        assert result is not None
        assert result.year == 2024
        assert result.month == 1


class TestJsonLoads:
    """Tests for _json_loads function."""

    def test_json_loads_none(self):
        """Return None for None input."""
        result = _json_loads(None)
        assert result is None

    def test_json_loads_empty(self):
        """Return None for empty string."""
        result = _json_loads("")
        assert result is None

    def test_json_loads_valid(self):
        """Parse valid JSON."""
        result = _json_loads('{"key": "value"}')
        assert result == {"key": "value"}

    def test_json_loads_invalid(self):
        """Return None for invalid JSON."""
        result = _json_loads("not valid json {")
        assert result is None

    def test_json_loads_array(self):
        """Parse JSON array."""
        result = _json_loads('["a", "b", "c"]')
        assert result == ["a", "b", "c"]


class TestTraceRepositoryQueries:
    """Tests for TraceRepository query methods."""

    @pytest.fixture
    def repo(self, tmp_path: Path) -> TraceRepository:
        """Create repository with temporary database."""
        db_path = tmp_path / "test_traces.sqlite"
        return TraceRepository(db_path=db_path)

    @pytest.fixture
    def sample_trace(self) -> AgentTrace:
        """Create sample trace."""
        return AgentTrace(
            agent_trace_id="trace_test_1",
            decision_record_id="dec_123",
            claim_id="claim_456",
            domain="politics",
            risk_level="high",
        )

    @pytest.fixture
    def sample_step(self) -> ReasoningStep:
        """Create sample reasoning step."""
        return ReasoningStep(
            step_id="step_test_1",
            order=1,
            actor_role="analyst",
            step_kind="analysis",
            summary="Test step",
        )

    def test_list_traces_by_decision(self, repo: TraceRepository, sample_trace: AgentTrace):
        """List traces by decision ID."""
        repo.save_agent_trace(sample_trace)

        result = repo.list_traces_by_decision("dec_123")

        assert len(result) == 1
        assert result[0]["decision_record_id"] == "dec_123"

    def test_list_traces_by_decision_empty(self, repo: TraceRepository):
        """List traces by decision returns empty for no matches."""
        result = repo.list_traces_by_decision("nonexistent_dec")

        assert result == []

    def test_list_traces_by_claim(self, repo: TraceRepository, sample_trace: AgentTrace):
        """List traces by claim ID."""
        repo.save_agent_trace(sample_trace)

        result = repo.list_traces_by_claim("claim_456")

        assert len(result) == 1
        assert result[0]["claim_id"] == "claim_456"

    def test_list_traces_by_claim_empty(self, repo: TraceRepository):
        """List traces by claim returns empty for no matches."""
        result = repo.list_traces_by_claim("nonexistent_claim")

        assert result == []

    def test_list_recent_no_filter(self, repo: TraceRepository, sample_trace: AgentTrace):
        """List recent traces without domain filter."""
        repo.save_agent_trace(sample_trace)

        result = repo.list_recent(limit=10)

        assert len(result) == 1
        assert "steps_count" in result[0]

    def test_list_recent_with_domain(self, repo: TraceRepository, sample_trace: AgentTrace):
        """List recent traces with domain filter."""
        repo.save_agent_trace(sample_trace)

        result = repo.list_recent(domain="politics", limit=10)

        assert len(result) == 1

        result_empty = repo.list_recent(domain="health", limit=10)
        assert len(result_empty) == 0

    def test_list_recent_empty(self, repo: TraceRepository):
        """List recent returns empty when no traces."""
        result = repo.list_recent(limit=10)

        assert result == []

    def test_get_trace_found(self, repo: TraceRepository, sample_trace: AgentTrace):
        """Get trace by ID when exists."""
        repo.save_agent_trace(sample_trace)

        result = repo.get_trace("trace_test_1")

        assert result is not None
        assert result["agent_trace_id"] == "trace_test_1"

    def test_get_trace_not_found(self, repo: TraceRepository):
        """Get trace returns None when not found."""
        result = repo.get_trace("nonexistent_trace")

        assert result is None

    def test_list_steps_for_trace(self, repo: TraceRepository, sample_trace: AgentTrace, sample_step: ReasoningStep):
        """List steps for a trace."""
        sample_trace.steps = [sample_step]
        repo.save_agent_trace(sample_trace)

        result = repo.list_steps_for_trace("trace_test_1")

        assert len(result) == 1
        assert result[0]["step_id"] == "step_test_1"

    def test_list_steps_for_trace_empty(self, repo: TraceRepository):
        """List steps returns empty for nonexistent trace."""
        result = repo.list_steps_for_trace("nonexistent_trace")

        assert result == []


class TestCommitteeTraceQueries:
    """Tests for committee trace queries."""

    @pytest.fixture
    def repo(self, tmp_path: Path) -> TraceRepository:
        """Create repository with temporary database."""
        db_path = tmp_path / "test_committee_traces.sqlite"
        return TraceRepository(db_path=db_path)

    @pytest.fixture
    def sample_committee_trace(self) -> CommitteeTrace:
        """Create sample committee trace."""
        return CommitteeTrace(
            committee_trace_id="comm_trace_1",
            committee_id="comm_123",
            decision_record_id="dec_456",
            claim_id="claim_789",
            domain="politics",
            summary="Committee decision",
        )

    def test_list_committee_traces(self, repo: TraceRepository, sample_committee_trace: CommitteeTrace):
        """List committee traces by decision."""
        repo.save_committee_trace(sample_committee_trace)

        result = repo.list_committee_traces("dec_456")

        assert len(result) == 1
        assert result[0]["committee_trace_id"] == "comm_trace_1"

    def test_list_committee_traces_empty(self, repo: TraceRepository):
        """List committee traces returns empty for no matches."""
        result = repo.list_committee_traces("nonexistent_dec")

        assert result == []


class TestBuildTraceFromLinks:
    """Tests for build_trace_from_links method."""

    @pytest.fixture
    def repo(self, tmp_path: Path) -> TraceRepository:
        """Create repository with temporary database."""
        db_path = tmp_path / "test_build_trace.sqlite"
        return TraceRepository(db_path=db_path)

    def test_build_trace_from_links_minimal(self, repo: TraceRepository):
        """Build trace with minimal links."""
        links = TraceLinkRefs(
            truth_record_id="truth_1",
            decision_record_id="dec_1",
            claim_id="claim_1",
            domain="politics",
        )

        result = repo.build_trace_from_links(links)

        assert result.truth_record_id == "truth_1"
        assert result.decision_record_id == "dec_1"
        assert result.claim_id == "claim_1"
        assert result.domain == "politics"

    def test_build_trace_from_links_full(self, repo: TraceRepository):
        """Build trace with all options."""
        links = TraceLinkRefs(
            truth_record_id="truth_2",
            decision_record_id="dec_2",
            claim_id="claim_2",
            domain="health",
            risk_level="high",
            request_id="req_123",
        )

        step = ReasoningStep(
            step_id="step_1",
            order=1,
            summary="Test step",
        )

        result = repo.build_trace_from_links(
            links,
            agent_run_id="run_1",
            committee_trace_id="comm_1",
            steps=[step],
            input_hash="hash_abc",
            risk_level="critical",
        )

        assert result.agent_run_id == "run_1"
        assert result.committee_trace_id == "comm_1"
        assert len(result.steps) == 1
        assert result.input_hash == "hash_abc"
        assert result.risk_level == "critical"  # Override from param
        assert result.request_id == "req_123"

    def test_build_trace_from_links_no_domain(self, repo: TraceRepository):
        """Build trace defaults domain to unknown."""
        links = TraceLinkRefs(
            truth_record_id="truth_3",
            decision_record_id="dec_3",
            claim_id="claim_3",
            domain=None,
        )

        result = repo.build_trace_from_links(links)

        assert result.domain == "unknown"
