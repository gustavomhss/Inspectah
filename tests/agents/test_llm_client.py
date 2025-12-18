"""
Tests for agents/llm_client — S37

Tests for LLM client stub.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from app.agents.llm_client import LLMClient
from app.agents.models import AgentProfile, ModelUpgradePolicy, AgentRole, AgentLayer, AgentStatus


class TestLLMClient:
    """Tests for LLMClient class."""

    @pytest.fixture
    def agent(self):
        """Create a test agent profile."""
        return AgentProfile(
            id="agent_test",
            name="Test Agent",
            description="A test agent",
            instructions="Test instructions",
            role=AgentRole.ANALYST,
            layer=AgentLayer.INTERPRETATION,
            model_name="gpt-4",
            recommended_model_name="gpt-4",
            temperature=0.7,
            max_tokens=1000,
            top_p=1.0,
            status=AgentStatus.ACTIVE,
        )

    def test_init_default_policy(self):
        """Initialize with default policy."""
        client = LLMClient()

        assert client.policy is not None
        assert isinstance(client.policy, ModelUpgradePolicy)

    def test_init_custom_policy(self):
        """Initialize with custom policy."""
        policy = ModelUpgradePolicy(global_default_model="gpt-3.5-turbo")
        client = LLMClient(policy=policy)

        assert client.policy == policy

    def test_resolve_model(self, agent):
        """Resolve model for agent."""
        client = LLMClient()

        result = client.resolve_model(agent)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_resolve_model_with_time(self, agent):
        """Resolve model with specific time."""
        client = LLMClient()
        now = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

        result = client.resolve_model(agent, now=now)

        assert isinstance(result, str)

    def test_generate_returns_dict(self, agent):
        """Generate returns dictionary with expected keys."""
        client = LLMClient()

        result = client.generate(agent, "Test prompt")

        assert isinstance(result, dict)
        assert "model" in result
        assert "prompt_preview" in result
        assert "output" in result
        assert "ts" in result

    def test_generate_prompt_preview_truncated(self, agent):
        """Generate truncates prompt preview to 200 chars."""
        client = LLMClient()
        long_prompt = "x" * 500

        result = client.generate(agent, long_prompt)

        assert len(result["prompt_preview"]) == 200

    def test_generate_prompt_preview_short(self, agent):
        """Generate preserves short prompts."""
        client = LLMClient()
        short_prompt = "Short test"

        result = client.generate(agent, short_prompt)

        assert result["prompt_preview"] == short_prompt

    def test_generate_stubbed_output(self, agent):
        """Generate returns stubbed output."""
        client = LLMClient()

        result = client.generate(agent, "Any prompt")

        assert result["output"] == "stubbed-response"

    def test_generate_with_time(self, agent):
        """Generate with specific time."""
        client = LLMClient()
        now = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

        result = client.generate(agent, "Test", now=now)

        assert "model" in result
        assert "ts" in result
