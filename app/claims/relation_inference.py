"""
S38-BE-020: Inferencia de Relacoes entre Claims

Infere relacoes semanticas entre claims usando embeddings e heuristicas.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Protocol, Tuple

from app.claims.relation_types import (
    ClassificationResult,
    ClaimRelation,
    InferenceMethod,
    RelationConfig,
    RelationType,
    detect_negation_indicators,
    detect_support_indicators,
)

logger = logging.getLogger(__name__)


class EmbeddingProvider(Protocol):
    """Interface para provedor de embeddings."""

    def embed(self, text: str) -> List[float]:
        """Gera embedding para um texto."""
        ...

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Gera embeddings para varios textos."""
        ...


@dataclass
class Claim:
    """Representacao de um claim para inferencia."""
    id: str
    text: str
    embedding: Optional[List[float]] = None
    entities: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.entities is None:
            self.entities = []
        if self.metadata is None:
            self.metadata = {}


class RelationInferenceService:
    """
    Servico de inferencia de relacoes entre claims.

    Usa combinacao de:
    - Similaridade de embeddings
    - Deteccao de negacao/suporte
    - Match de entidades
    - Heuristicas de texto

    Uso:
        service = RelationInferenceService(embedding_provider)
        relations = service.infer_relations(source_claim, candidate_claims)
    """

    def __init__(
        self,
        embedding_provider: Optional[EmbeddingProvider] = None,
        config: Optional[RelationConfig] = None,
    ):
        self.embedding_provider = embedding_provider
        self.config = config or RelationConfig()

    def infer_relations(
        self,
        source_claim: Claim,
        candidate_claims: List[Claim],
        max_results: int = 10,
    ) -> List[ClaimRelation]:
        """
        Infere relacoes entre um claim fonte e candidatos.

        Args:
            source_claim: Claim de origem
            candidate_claims: Lista de claims candidatos
            max_results: Numero maximo de relacoes a retornar

        Returns:
            Lista de relacoes ordenadas por confianca
        """
        if not candidate_claims:
            return []

        relations = []

        for candidate in candidate_claims:
            if candidate.id == source_claim.id:
                continue

            result = self._classify_relation(source_claim, candidate)
            if result and result.confidence >= self.config.confidence_threshold:
                relation = ClaimRelation(
                    source_claim_id=source_claim.id,
                    target_claim_id=candidate.id,
                    relation_type=result.relation_type,
                    confidence=result.confidence,
                    method=result.method,
                    indicators=result.indicators,
                )
                relations.append(relation)

        # Ordenar por confianca e limitar
        relations.sort(key=lambda r: r.confidence, reverse=True)
        return relations[:max_results]

    def _classify_relation(
        self,
        source: Claim,
        target: Claim,
    ) -> Optional[ClassificationResult]:
        """Classifica a relacao entre dois claims."""
        indicators: Dict[str, Any] = {}

        # 1. Calcular similaridade por embedding
        similarity = self._compute_similarity(source, target)
        indicators["embedding_similarity"] = similarity

        if similarity < self.config.similarity_threshold:
            return None  # Nao relacionados

        # 2. Verificar duplicacao
        if similarity >= self.config.duplicate_threshold:
            return ClassificationResult(
                relation_type=RelationType.DUPLICATE,
                confidence=similarity,
                method=InferenceMethod.EMBEDDING,
                indicators=indicators,
            )

        # 3. Detectar contradicao
        contradiction_score = self._detect_contradiction(source, target)
        indicators["contradiction_score"] = contradiction_score

        if contradiction_score >= self.config.contradiction_threshold:
            confidence = min(1.0, contradiction_score * self.config.negation_boost)
            return ClassificationResult(
                relation_type=RelationType.CONTRADICTS,
                confidence=confidence,
                method=InferenceMethod.RULE,
                indicators=indicators,
            )

        # 4. Detectar suporte
        support_score = self._detect_support(source, target)
        indicators["support_score"] = support_score

        if support_score >= self.config.support_threshold:
            return ClassificationResult(
                relation_type=RelationType.SUPPORTS,
                confidence=support_score,
                method=InferenceMethod.RULE,
                indicators=indicators,
            )

        # 5. Verificar entidades em comum
        entity_overlap = self._compute_entity_overlap(source, target)
        indicators["entity_overlap"] = entity_overlap

        # 6. Default: related
        if similarity >= self.config.similarity_threshold:
            return ClassificationResult(
                relation_type=RelationType.RELATED,
                confidence=similarity,
                method=InferenceMethod.EMBEDDING,
                indicators=indicators,
            )

        return None

    def _compute_similarity(self, source: Claim, target: Claim) -> float:
        """Calcula similaridade coseno entre embeddings."""
        if not source.embedding or not target.embedding:
            # Fallback: similaridade de texto simples
            return self._text_similarity(source.text, target.text)

        return self._cosine_similarity(source.embedding, target.embedding)

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calcula similaridade coseno."""
        if len(a) != len(b):
            return 0.0

        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def _text_similarity(self, text_a: str, text_b: str) -> float:
        """Similaridade simples baseada em palavras."""
        words_a = set(text_a.lower().split())
        words_b = set(text_b.lower().split())

        if not words_a or not words_b:
            return 0.0

        intersection = words_a & words_b
        union = words_a | words_b

        return len(intersection) / len(union)  # Jaccard

    def _detect_contradiction(self, source: Claim, target: Claim) -> float:
        """Detecta indicadores de contradicao."""
        source_negations = detect_negation_indicators(source.text)
        target_negations = detect_negation_indicators(target.text)

        # Se um tem negacao e outro nao, pode ser contradicao
        if (source_negations and not target_negations) or \
           (target_negations and not source_negations):
            # Verificar se os claims sao sobre o mesmo assunto
            similarity = self._text_similarity(source.text, target.text)
            if similarity > 0.3:
                return 0.7 + (similarity * 0.3)

        # Ambos com negacao ou ambos sem
        combined = source_negations + target_negations
        if combined:
            return 0.5 * min(1.0, len(combined) / 3)

        return 0.0

    def _detect_support(self, source: Claim, target: Claim) -> float:
        """Detecta indicadores de suporte."""
        source_support = detect_support_indicators(source.text)
        target_support = detect_support_indicators(target.text)

        combined = source_support + target_support

        if combined:
            # Verificar similaridade
            similarity = self._text_similarity(source.text, target.text)
            if similarity > 0.5:
                return 0.7 + (similarity * 0.3)

        return 0.0

    def _compute_entity_overlap(self, source: Claim, target: Claim) -> float:
        """Calcula overlap de entidades."""
        if not source.entities or not target.entities:
            return 0.0

        source_set = set(e.lower() for e in source.entities)
        target_set = set(e.lower() for e in target.entities)

        intersection = source_set & target_set
        union = source_set | target_set

        if not union:
            return 0.0

        return len(intersection) / len(union)

    def find_similar(
        self,
        query_claim: Claim,
        all_claims: List[Claim],
        threshold: float = 0.7,
        limit: int = 10,
    ) -> List[Tuple[Claim, float]]:
        """
        Encontra claims similares a um claim de consulta.

        Returns:
            Lista de (claim, similarity) ordenada por similaridade
        """
        results = []

        for claim in all_claims:
            if claim.id == query_claim.id:
                continue

            similarity = self._compute_similarity(query_claim, claim)
            if similarity >= threshold:
                results.append((claim, similarity))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]


# Implementacao simples de embedding provider para testes
class SimpleEmbeddingProvider:
    """Provider de embeddings simples usando TF-IDF-like."""

    def __init__(self, vocab_size: int = 1000):
        self.vocab_size = vocab_size
        self._vocab: Dict[str, int] = {}
        self._next_idx = 0

    def embed(self, text: str) -> List[float]:
        words = text.lower().split()
        embedding = [0.0] * self.vocab_size

        for word in words:
            if word not in self._vocab:
                if self._next_idx < self.vocab_size:
                    self._vocab[word] = self._next_idx
                    self._next_idx += 1
                else:
                    continue

            idx = self._vocab[word]
            embedding[idx] = 1.0 / len(words)  # Normalizado

        return embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed(text) for text in texts]
