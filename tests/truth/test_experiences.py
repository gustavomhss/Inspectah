"""
Tests for Experience model and repository.

Tasks: S40-BE-007, S40-BE-008 tests
"""

import pytest

from app.truth.experiences import (
    Experience,
    ExperienceRepository,
    add_experience,
    find_similar_experiences,
    get_experience_repository,
)


class TestExperience:
    """Tests for Experience model."""

    def test_create_experience(self):
        """Test creating an experience."""
        exp = Experience.create(
            claim_id="claim-001",
            decision_id="decision-001",
            claim_text="A test claim about health",
            outcome="ESTABLISHED_FACT",
            domain="saude",
        )

        assert exp.experience_id.startswith("exp_")
        assert exp.claim_id == "claim-001"
        assert exp.decision_id == "decision-001"
        assert exp.claim_text == "A test claim about health"
        assert exp.outcome == "ESTABLISHED_FACT"
        assert exp.domain == "saude"
        assert exp.embedding is None
        assert exp.created_at is not None

    def test_create_experience_with_embedding(self):
        """Test creating an experience with embedding."""
        embedding = [0.1] * 384  # 384-dim vector

        exp = Experience.create(
            claim_id="claim-002",
            decision_id="decision-002",
            claim_text="Another claim",
            outcome="RETRACTED",
            embedding=embedding,
        )

        assert exp.embedding is not None
        assert len(exp.embedding) == 384

    def test_experience_to_dict(self):
        """Test converting experience to dict."""
        exp = Experience.create(
            claim_id="claim-003",
            decision_id="decision-003",
            claim_text="Dict test claim",
            outcome="UNDER_DISPUTE",
            metadata={"source": "test"},
        )

        exp_dict = exp.to_dict()

        assert isinstance(exp_dict, dict)
        assert exp_dict["claim_id"] == "claim-003"
        assert exp_dict["outcome"] == "UNDER_DISPUTE"
        assert exp_dict["metadata"]["source"] == "test"
        assert "created_at" in exp_dict

    def test_valid_outcomes(self):
        """Test all valid outcome values."""
        valid_outcomes = ["ESTABLISHED_FACT", "RETRACTED", "UNDER_DISPUTE", "PROVISIONAL"]

        for outcome in valid_outcomes:
            exp = Experience.create(
                claim_id="c1",
                decision_id="d1",
                claim_text="test",
                outcome=outcome,
            )
            assert exp.outcome == outcome


class TestExperienceRepository:
    """Tests for ExperienceRepository."""

    def test_add_experience(self):
        """Test adding an experience."""
        repo = ExperienceRepository()
        exp = Experience.create(
            claim_id="c1",
            decision_id="d1",
            claim_text="Test",
            outcome="ESTABLISHED_FACT",
        )

        added = repo.add(exp)

        assert added.experience_id == exp.experience_id
        assert repo.count() == 1

    def test_get_experience(self):
        """Test getting an experience by ID."""
        repo = ExperienceRepository()
        exp = Experience.create(
            claim_id="c1",
            decision_id="d1",
            claim_text="Test",
            outcome="ESTABLISHED_FACT",
        )
        repo.add(exp)

        retrieved = repo.get(exp.experience_id)

        assert retrieved is not None
        assert retrieved.experience_id == exp.experience_id

    def test_get_nonexistent(self):
        """Test getting a nonexistent experience."""
        repo = ExperienceRepository()

        retrieved = repo.get("nonexistent")

        assert retrieved is None

    def test_get_by_claim(self):
        """Test getting experiences by claim ID."""
        repo = ExperienceRepository()
        exp1 = Experience.create(
            claim_id="c1",
            decision_id="d1",
            claim_text="Test 1",
            outcome="ESTABLISHED_FACT",
        )
        exp2 = Experience.create(
            claim_id="c1",
            decision_id="d2",
            claim_text="Test 2",
            outcome="RETRACTED",
        )
        exp3 = Experience.create(
            claim_id="c2",
            decision_id="d3",
            claim_text="Test 3",
            outcome="PROVISIONAL",
        )
        repo.add(exp1)
        repo.add(exp2)
        repo.add(exp3)

        experiences = repo.get_by_claim("c1")

        assert len(experiences) == 2
        assert all(e.claim_id == "c1" for e in experiences)

    def test_get_by_domain(self):
        """Test getting experiences by domain."""
        repo = ExperienceRepository()
        exp1 = Experience.create(
            claim_id="c1",
            decision_id="d1",
            claim_text="Health claim",
            outcome="ESTABLISHED_FACT",
            domain="saude",
        )
        exp2 = Experience.create(
            claim_id="c2",
            decision_id="d2",
            claim_text="Politics claim",
            outcome="UNDER_DISPUTE",
            domain="politica",
        )
        repo.add(exp1)
        repo.add(exp2)

        saude_exps = repo.get_by_domain("saude")
        politica_exps = repo.get_by_domain("politica")

        assert len(saude_exps) == 1
        assert saude_exps[0].domain == "saude"
        assert len(politica_exps) == 1
        assert politica_exps[0].domain == "politica"

    def test_find_similar_by_embedding(self):
        """Test finding similar experiences by embedding."""
        repo = ExperienceRepository()

        # Create experiences with embeddings
        exp1 = Experience.create(
            claim_id="c1",
            decision_id="d1",
            claim_text="Claim about vaccines",
            outcome="ESTABLISHED_FACT",
            embedding=[1.0, 0.0, 0.0],  # Simple 3-dim for testing
        )
        exp2 = Experience.create(
            claim_id="c2",
            decision_id="d2",
            claim_text="Claim about medicine",
            outcome="PROVISIONAL",
            embedding=[0.9, 0.1, 0.0],  # Similar to exp1
        )
        exp3 = Experience.create(
            claim_id="c3",
            decision_id="d3",
            claim_text="Claim about politics",
            outcome="RETRACTED",
            embedding=[0.0, 0.0, 1.0],  # Different
        )
        repo.add(exp1)
        repo.add(exp2)
        repo.add(exp3)

        # Search for similar
        query = [1.0, 0.0, 0.0]
        similar = repo.find_similar(query, top_n=2)

        assert len(similar) == 2
        # exp1 should be most similar (exact match)
        assert similar[0][0].experience_id == exp1.experience_id
        assert similar[0][1] == 1.0  # Perfect similarity
        # exp2 should be second (high similarity)
        assert similar[1][0].experience_id == exp2.experience_id
        assert similar[1][1] > 0.9

    def test_find_similar_by_text(self):
        """Test finding similar experiences by text overlap."""
        repo = ExperienceRepository()

        exp1 = Experience.create(
            claim_id="c1",
            decision_id="d1",
            claim_text="vaccine safety is important for public health",
            outcome="ESTABLISHED_FACT",
        )
        exp2 = Experience.create(
            claim_id="c2",
            decision_id="d2",
            claim_text="economic policy affects markets",
            outcome="PROVISIONAL",
        )
        repo.add(exp1)
        repo.add(exp2)

        # Search for similar by text
        similar = repo.find_similar_text("vaccine safety concerns", top_n=2)

        assert len(similar) == 2
        # exp1 should be more similar (shares "vaccine" and "safety")
        assert similar[0][0].experience_id == exp1.experience_id
        assert similar[0][1] > similar[1][1]

    def test_find_similar_with_domain_filter(self):
        """Test finding similar with domain filter."""
        repo = ExperienceRepository()

        exp1 = Experience.create(
            claim_id="c1",
            decision_id="d1",
            claim_text="test claim",
            outcome="ESTABLISHED_FACT",
            domain="saude",
            embedding=[1.0, 0.0, 0.0],
        )
        exp2 = Experience.create(
            claim_id="c2",
            decision_id="d2",
            claim_text="test claim",
            outcome="PROVISIONAL",
            domain="politica",
            embedding=[1.0, 0.0, 0.0],  # Same embedding
        )
        repo.add(exp1)
        repo.add(exp2)

        # Search only in saude domain
        query = [1.0, 0.0, 0.0]
        similar = repo.find_similar(query, top_n=5, domain="saude")

        assert len(similar) == 1
        assert similar[0][0].domain == "saude"

    def test_find_similar_empty_embedding(self):
        """Test find_similar with empty embedding."""
        repo = ExperienceRepository()

        result = repo.find_similar([], top_n=5)

        assert result == []

    def test_find_similar_no_experiences(self):
        """Test find_similar when no experiences exist."""
        repo = ExperienceRepository()

        result = repo.find_similar([1.0, 0.0, 0.0], top_n=5)

        assert result == []

    def test_list_all(self):
        """Test listing all experiences."""
        repo = ExperienceRepository()

        for i in range(5):
            exp = Experience.create(
                claim_id=f"c{i}",
                decision_id=f"d{i}",
                claim_text=f"Claim {i}",
                outcome="ESTABLISHED_FACT",
            )
            repo.add(exp)

        all_exps = repo.list_all(limit=3)

        assert len(all_exps) == 3
        # Should be sorted by created_at descending
        assert all_exps[0].created_at >= all_exps[1].created_at

    def test_count(self):
        """Test counting experiences."""
        repo = ExperienceRepository()

        assert repo.count() == 0

        for i in range(3):
            exp = Experience.create(
                claim_id=f"c{i}",
                decision_id=f"d{i}",
                claim_text=f"Claim {i}",
                outcome="ESTABLISHED_FACT",
            )
            repo.add(exp)

        assert repo.count() == 3


class TestCosineSimlarity:
    """Tests for cosine similarity calculation."""

    def test_identical_vectors(self):
        """Test cosine similarity of identical vectors."""
        v = [1.0, 2.0, 3.0]
        similarity = ExperienceRepository._cosine_similarity(v, v)
        assert abs(similarity - 1.0) < 0.0001

    def test_orthogonal_vectors(self):
        """Test cosine similarity of orthogonal vectors."""
        v1 = [1.0, 0.0, 0.0]
        v2 = [0.0, 1.0, 0.0]
        similarity = ExperienceRepository._cosine_similarity(v1, v2)
        assert abs(similarity) < 0.0001

    def test_opposite_vectors(self):
        """Test cosine similarity of opposite vectors."""
        v1 = [1.0, 2.0, 3.0]
        v2 = [-1.0, -2.0, -3.0]
        similarity = ExperienceRepository._cosine_similarity(v1, v2)
        assert abs(similarity + 1.0) < 0.0001

    def test_zero_vector(self):
        """Test cosine similarity with zero vector."""
        v1 = [1.0, 2.0, 3.0]
        v2 = [0.0, 0.0, 0.0]
        similarity = ExperienceRepository._cosine_similarity(v1, v2)
        assert similarity == 0.0

    def test_different_length_vectors(self):
        """Test cosine similarity with different length vectors."""
        v1 = [1.0, 2.0, 3.0]
        v2 = [1.0, 2.0]
        similarity = ExperienceRepository._cosine_similarity(v1, v2)
        assert similarity == 0.0


class TestGlobalFunctions:
    """Tests for global helper functions."""

    def test_get_experience_repository(self):
        """Test getting default repository."""
        repo1 = get_experience_repository()
        repo2 = get_experience_repository()

        # Should be same instance
        assert repo1 is repo2

    def test_find_similar_experiences_by_embedding(self):
        """Test find_similar_experiences with embedding."""
        # Add an experience to default repo
        exp = Experience.create(
            claim_id="global-test",
            decision_id="d1",
            claim_text="Test for global",
            outcome="ESTABLISHED_FACT",
            embedding=[1.0, 0.0, 0.0],
        )
        add_experience(exp)

        # Search
        similar = find_similar_experiences(claim_embedding=[1.0, 0.0, 0.0])

        # Should find at least the one we added
        assert any(e.claim_id == "global-test" for e, _ in similar)

    def test_find_similar_experiences_by_text(self):
        """Test find_similar_experiences with text."""
        exp = Experience.create(
            claim_id="global-text-test",
            decision_id="d1",
            claim_text="unique text for testing",
            outcome="ESTABLISHED_FACT",
        )
        add_experience(exp)

        similar = find_similar_experiences(claim_text="unique text testing")

        assert any(e.claim_id == "global-text-test" for e, _ in similar)

    def test_find_similar_experiences_no_input(self):
        """Test find_similar_experiences with no input."""
        similar = find_similar_experiences()

        assert similar == []


class TestExperienceRepositoryEdgeCases:
    """Edge case tests for ExperienceRepository."""

    def test_find_similar_text_empty_text(self):
        """Test find_similar_text with empty text."""
        repo = ExperienceRepository()

        result = repo.find_similar_text("", top_n=5)

        assert result == []

    def test_find_similar_text_no_candidates(self):
        """Test find_similar_text when no candidates exist."""
        repo = ExperienceRepository()

        result = repo.find_similar_text("test query", top_n=5)

        assert result == []

    def test_find_similar_text_with_domain_filter_no_matches(self):
        """Test find_similar_text with domain filter that has no matches."""
        repo = ExperienceRepository()
        exp = Experience.create(
            claim_id="c1",
            decision_id="d1",
            claim_text="test claim",
            outcome="ESTABLISHED_FACT",
            domain="saude",
        )
        repo.add(exp)

        result = repo.find_similar_text("test", domain="economia")

        assert result == []

    def test_find_similar_text_empty_claim_text(self):
        """Test find_similar_text with experience that has empty claim_text."""
        repo = ExperienceRepository()
        exp = Experience.create(
            claim_id="c1",
            decision_id="d1",
            claim_text="",
            outcome="ESTABLISHED_FACT",
        )
        repo.add(exp)

        result = repo.find_similar_text("test query", top_n=5)

        # Should not include the experience with empty claim_text
        assert len(result) == 0
