from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import yaml

from app.cases.models import CaseDefinition, CaseClaim


@dataclass
class GoldenCase:
    case_id: str
    domain: str
    title: str
    entities: List[str]
    claims: List[Dict]
    case_definition: CaseDefinition
    summary: str
    claim_entities: Dict[str, List[str]]
    claim_sources: Dict[str, List[str]]


def _load_yaml(path: Path) -> Dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_golden_case(case_slug: str, base_dir: Path = Path("data/s25/golden_sets")) -> GoldenCase:
    case_dir = base_dir / case_slug
    if not case_dir.exists():
        raise FileNotFoundError(f"Golden set não encontrado: {case_dir}")
    case_file = case_dir / "case.yaml"
    meta = _load_yaml(case_file)
    claims = meta.get("claims", [])
    case_def = CaseDefinition(
        case_id=meta["case_id"],
        title=meta.get("title", meta["case_id"]),
        summary=meta.get("summary", ""),
        theme=meta.get("domain", "general"),
        tags=meta.get("tags", []) or [],
        claims=[
            CaseClaim(
                claim_id=claim["id"],
                description=claim.get("description", ""),
                truth_state=claim.get("expected_state"),
                debunk_target_id=claim.get("debunk_issue_id"),
                tags=claim.get("tags", []) or [],
            )
            for claim in claims
        ],
        timeline=meta.get("timeline", []) or [],
        sources=meta.get("sources", []) or [],
        metadata=meta.get("metadata", {}) or {},
    )
    claim_entities = {c["id"]: c.get("entities", []) for c in claims}
    claim_sources = {c["id"]: c.get("sources", []) for c in claims}
    return GoldenCase(
        case_id=meta["case_id"],
        domain=meta.get("domain", "general"),
        title=meta.get("title", meta["case_id"]),
        entities=meta.get("entities", []),
        claims=claims,
        case_definition=case_def,
        summary=meta.get("expected_behaviour", ""),
        claim_entities=claim_entities,
        claim_sources=claim_sources,
    )
