"""
Tests for agents/kb_adapter — S37

Tests for KB context rendering.
"""

import pytest

from app.agents.kb_adapter import render_kb_context
from app.agents.models import AgentKBRef


class TestRenderKBContext:
    """Tests for render_kb_context function."""

    def test_render_empty_list(self):
        """Render empty list returns empty string."""
        result = render_kb_context([])

        assert result == ""

    def test_render_single_ref(self):
        """Render single KB reference."""
        refs = [
            AgentKBRef(id="kb_1", kind="doc", label="Policy Doc", path_or_uri="/docs/policy.md")
        ]

        result = render_kb_context(refs)

        assert "[doc] Policy Doc (/docs/policy.md)" in result

    def test_render_multiple_refs(self):
        """Render multiple KB references."""
        refs = [
            AgentKBRef(id="kb_1", kind="doc", label="Doc 1", path_or_uri="/docs/1.md"),
            AgentKBRef(id="kb_2", kind="api", label="API Ref", path_or_uri="https://api.example.com"),
            AgentKBRef(id="kb_3", kind="rule", label="Rule Set", path_or_uri="/rules/set.yaml"),
        ]

        result = render_kb_context(refs)

        lines = result.split("\n")
        assert len(lines) == 3
        assert "[doc] Doc 1 (/docs/1.md)" in lines[0]
        assert "[api] API Ref (https://api.example.com)" in lines[1]
        assert "[rule] Rule Set (/rules/set.yaml)" in lines[2]

    def test_render_preserves_order(self):
        """Render preserves order of references."""
        refs = [
            AgentKBRef(id="kb_z", kind="z", label="Z Ref", path_or_uri="/z"),
            AgentKBRef(id="kb_a", kind="a", label="A Ref", path_or_uri="/a"),
        ]

        result = render_kb_context(refs)

        lines = result.split("\n")
        assert "[z]" in lines[0]
        assert "[a]" in lines[1]
