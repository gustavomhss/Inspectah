"""
Sprint 40: Experiences model and repository.

Tasks: S40-BE-007, S40-BE-008
Experiences are append-only records of past decisions for retrieval by similarity.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


def _generate_id(prefix: str = "exp") -> str:
    """Generate a unique ID with prefix."""
    return f"{prefix}_{uuid4().hex[:12]}"


def _utcnow() -> datetime:
    """Return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


@dataclass
class Experience:
    """
    An experience from a past decision (S40-BE-007).

    Experiences are append-only - no updates or deletes allowed.
    Used for retrieval by similarity when making new decisions.
    """

    experience_id: str
    claim_id: str
    decision_id: str
    claim_text: str
    outcome: str  # ESTABLISHED_FACT, RETRACTED, UNDER_DISPUTE, PROVISIONAL
    domain: str | None = None
    embedding: list[float] | None = None  # 384-dim vector for similarity
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=_utcnow)

    @classmethod
    def create(
        cls,
        claim_id: str,
        decision_id: str,
        claim_text: str,
        outcome: str,
        domain: str | None = None,
        embedding: list[float] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "Experience":
        """Create a new Experience."""
        return cls(
            experience_id=_generate_id("exp"),
            claim_id=claim_id,
            decision_id=decision_id,
            claim_text=claim_text,
            outcome=outcome,
            domain=domain,
            embedding=embedding,
            metadata=metadata or {},
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "experience_id": self.experience_id,
            "claim_id": self.claim_id,
            "decision_id": self.decision_id,
            "claim_text": self.claim_text,
            "outcome": self.outcome,
            "domain": self.domain,
            "embedding": self.embedding,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


class ExperienceRepository:
    """
    Repository for experiences (S40-BE-008).

    Append-only storage with similarity search capability.
    Uses in-memory storage by default; can be extended for database.
    """

    def __init__(self) -> None:
        """Initialize repository with empty storage."""
        self._experiences: dict[str, Experience] = {}
        self._by_claim: dict[str, list[str]] = {}  # claim_id -> [experience_id]
        self._by_domain: dict[str, list[str]] = {}  # domain -> [experience_id]

    def add(self, experience: Experience) -> Experience:
        """
        Add an experience (append-only).

        Args:
            experience: Experience to add

        Returns:
            Added experience
        """
        self._experiences[experience.experience_id] = experience

        # Index by claim_id
        if experience.claim_id not in self._by_claim:
            self._by_claim[experience.claim_id] = []
        self._by_claim[experience.claim_id].append(experience.experience_id)

        # Index by domain
        if experience.domain:
            if experience.domain not in self._by_domain:
                self._by_domain[experience.domain] = []
            self._by_domain[experience.domain].append(experience.experience_id)

        logger.debug(f"Added experience {experience.experience_id}")
        return experience

    def get(self, experience_id: str) -> Experience | None:
        """Get an experience by ID."""
        return self._experiences.get(experience_id)

    def get_by_claim(self, claim_id: str) -> list[Experience]:
        """Get all experiences for a claim."""
        exp_ids = self._by_claim.get(claim_id, [])
        return [self._experiences[eid] for eid in exp_ids if eid in self._experiences]

    def get_by_domain(self, domain: str) -> list[Experience]:
        """Get all experiences for a domain."""
        exp_ids = self._by_domain.get(domain, [])
        return [self._experiences[eid] for eid in exp_ids if eid in self._experiences]

    def find_similar(
        self,
        claim_embedding: list[float],
        top_n: int = 5,
        domain: str | None = None,
    ) -> list[tuple[Experience, float]]:
        """
        Find similar experiences by embedding similarity.

        Uses cosine similarity. If no embeddings exist, returns empty list.

        Args:
            claim_embedding: Embedding vector to compare against
            top_n: Maximum number of results
            domain: Optional domain filter

        Returns:
            List of (Experience, similarity_score) tuples, sorted by score desc
        """
        if not claim_embedding:
            return []

        # Get candidate experiences
        if domain:
            candidates = self.get_by_domain(domain)
        else:
            candidates = list(self._experiences.values())

        # Filter to experiences with embeddings
        candidates = [e for e in candidates if e.embedding]

        if not candidates:
            return []

        # Calculate similarities
        similarities: list[tuple[Experience, float]] = []
        for exp in candidates:
            if exp.embedding:
                score = self._cosine_similarity(claim_embedding, exp.embedding)
                similarities.append((exp, score))

        # Sort by score descending
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_n]

    def find_similar_text(
        self,
        claim_text: str,
        top_n: int = 5,
        domain: str | None = None,
    ) -> list[tuple[Experience, float]]:
        """
        Find similar experiences by text (fallback for no embeddings).

        Uses simple word overlap as similarity metric.
        For production, use find_similar with proper embeddings.

        Args:
            claim_text: Text to compare
            top_n: Maximum number of results
            domain: Optional domain filter

        Returns:
            List of (Experience, similarity_score) tuples
        """
        if not claim_text:
            return []

        # Get candidate experiences
        if domain:
            candidates = self.get_by_domain(domain)
        else:
            candidates = list(self._experiences.values())

        if not candidates:
            return []

        # Simple word overlap similarity
        query_words = set(claim_text.lower().split())
        similarities: list[tuple[Experience, float]] = []

        for exp in candidates:
            exp_words = set(exp.claim_text.lower().split())
            if not exp_words:
                continue
            intersection = len(query_words & exp_words)
            union = len(query_words | exp_words)
            score = intersection / union if union > 0 else 0.0
            similarities.append((exp, score))

        # Sort by score descending
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_n]

    @staticmethod
    def _cosine_similarity(v1: list[float], v2: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(v1) != len(v2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm1 = sum(a * a for a in v1) ** 0.5
        norm2 = sum(b * b for b in v2) ** 0.5

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def count(self) -> int:
        """Get total number of experiences."""
        return len(self._experiences)

    def list_all(self, limit: int = 100) -> list[Experience]:
        """List all experiences (with limit)."""
        experiences = list(self._experiences.values())
        experiences.sort(key=lambda e: e.created_at, reverse=True)
        return experiences[:limit]


# Singleton instance for simple use cases
_default_repository: ExperienceRepository | None = None


def get_experience_repository() -> ExperienceRepository:
    """Get the default experience repository."""
    global _default_repository
    if _default_repository is None:
        _default_repository = ExperienceRepository()
    return _default_repository


def add_experience(experience: Experience) -> Experience:
    """Add an experience to the default repository."""
    return get_experience_repository().add(experience)


def find_similar_experiences(
    claim_embedding: list[float] | None = None,
    claim_text: str | None = None,
    top_n: int = 5,
    domain: str | None = None,
) -> list[tuple[Experience, float]]:
    """
    Find similar experiences from the default repository.

    Uses embedding similarity if embedding provided, otherwise falls back to text.
    """
    repo = get_experience_repository()

    if claim_embedding:
        return repo.find_similar(claim_embedding, top_n, domain)
    elif claim_text:
        return repo.find_similar_text(claim_text, top_n, domain)
    else:
        return []
