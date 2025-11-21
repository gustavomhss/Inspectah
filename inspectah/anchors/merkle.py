"""Utilidades de Merkle tree para âncoras v1."""
from __future__ import annotations

from hashlib import sha256
from typing import Iterable, List, Sequence


def _hash_leaf(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _hash_pair(left: str, right: str) -> str:
    return sha256((left + right).encode("utf-8")).hexdigest()


def build_merkle_root(items: Sequence[str]) -> str:
    """Calcula a Merkle root de uma lista de strings. Reutiliza último nó em contagens ímpares."""
    if not items:
        return _hash_leaf("empty")
    level = [_hash_leaf(item) for item in items]
    while len(level) > 1:
        next_level: List[str] = []
        for idx in range(0, len(level), 2):
            left = level[idx]
            right = level[idx + 1] if idx + 1 < len(level) else left
            next_level.append(_hash_pair(left, right))
        level = next_level
    return level[0]


def generate_proof(items: Sequence[str], index: int) -> List[str]:
    """Gera proof simples contendo os hashes irmãos até a root."""
    if index < 0 or index >= len(items):
        raise IndexError("índice fora da lista de itens")
    hashes = [_hash_leaf(item) for item in items]
    proof: List[str] = []
    idx = index
    while len(hashes) > 1:
        if idx % 2 == 0 and idx + 1 < len(hashes):
            proof.append(hashes[idx + 1])
        elif idx % 2 == 1:
            proof.append(hashes[idx - 1])
        next_level: List[str] = []
        for j in range(0, len(hashes), 2):
            left = hashes[j]
            right = hashes[j + 1] if j + 1 < len(hashes) else left
            next_level.append(_hash_pair(left, right))
        hashes = next_level
        idx //= 2
    return proof


def verify_proof(leaf: str, proof: Iterable[str], root: str) -> bool:
    """Verifica proof gerada por `generate_proof`."""
    computed = _hash_leaf(leaf)
    for sibling in proof:
        computed = _hash_pair(computed, sibling)
    return computed == root


__all__ = ["build_merkle_root", "generate_proof", "verify_proof"]
