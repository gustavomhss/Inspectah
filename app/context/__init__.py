"""Context package — S38 Memory Controller."""

# S38 - Memory Controller (no external dependencies)
from app.context.memory_controller import (
    MemoryScope,
    MemoryType,
    RetentionPolicy,
    MemoryEntry,
    MemoryContext,
    MemoryStats,
    MemoryRepository,
    MemoryController,
)

# Lazy imports for modules with external dependencies
def __getattr__(name):
    if name in ("CaseContextDossier", "DossierClaim", "EntityContextDossier"):
        from app.context.models import CaseContextDossier, DossierClaim, EntityContextDossier
        return locals()[name]
    if name in ("build_case_dossier", "build_entity_dossier"):
        from app.context.service import build_case_dossier, build_entity_dossier
        return locals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    # Models (lazy)
    "CaseContextDossier",
    "DossierClaim",
    "EntityContextDossier",
    # Service (lazy)
    "build_case_dossier",
    "build_entity_dossier",
    # S38 - Memory Controller
    "MemoryScope",
    "MemoryType",
    "RetentionPolicy",
    "MemoryEntry",
    "MemoryContext",
    "MemoryStats",
    "MemoryRepository",
    "MemoryController",
]
