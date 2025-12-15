"""
S38: Tests for Context package lazy imports - 100% coverage
"""
import pytest


class TestContextLazyImports:
    """Tests for lazy import mechanism in app.context."""

    def test_import_case_context_dossier(self):
        """Test lazy import of CaseContextDossier."""
        from app.context import CaseContextDossier
        assert CaseContextDossier is not None

    def test_import_dossier_claim(self):
        """Test lazy import of DossierClaim."""
        from app.context import DossierClaim
        assert DossierClaim is not None

    def test_import_entity_context_dossier(self):
        """Test lazy import of EntityContextDossier."""
        from app.context import EntityContextDossier
        assert EntityContextDossier is not None

    def test_import_build_case_dossier(self):
        """Test lazy import of build_case_dossier."""
        from app.context import build_case_dossier
        assert callable(build_case_dossier)

    def test_import_build_entity_dossier(self):
        """Test lazy import of build_entity_dossier."""
        from app.context import build_entity_dossier
        assert callable(build_entity_dossier)

    def test_import_nonexistent_raises_attribute_error(self):
        """Test that importing nonexistent attribute raises AttributeError."""
        import app.context as context_module

        with pytest.raises(AttributeError) as exc_info:
            _ = context_module.NonExistentClass

        assert "has no attribute" in str(exc_info.value)
        assert "NonExistentClass" in str(exc_info.value)

    def test_memory_controller_direct_import(self):
        """Test direct imports from memory_controller are available."""
        from app.context import (
            MemoryScope,
            MemoryType,
            RetentionPolicy,
            MemoryEntry,
            MemoryContext,
            MemoryStats,
            MemoryRepository,
            MemoryController,
        )

        assert MemoryScope is not None
        assert MemoryType is not None
        assert RetentionPolicy is not None
        assert MemoryEntry is not None
        assert MemoryContext is not None
        assert MemoryStats is not None
        assert MemoryRepository is not None
        assert MemoryController is not None

    def test_all_exports(self):
        """Test that __all__ contains expected exports."""
        import app.context as context_module

        expected = [
            "CaseContextDossier",
            "DossierClaim",
            "EntityContextDossier",
            "build_case_dossier",
            "build_entity_dossier",
            "MemoryScope",
            "MemoryType",
            "RetentionPolicy",
            "MemoryEntry",
            "MemoryContext",
            "MemoryStats",
            "MemoryRepository",
            "MemoryController",
        ]

        for name in expected:
            assert name in context_module.__all__
