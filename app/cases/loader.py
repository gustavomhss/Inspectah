from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from app.cases.models import CaseClaim, CaseCollectionDefinition, CaseDefinition
from app.debunk.repository import DebunkRepository
from app.debunk.models import DebunkIssueTarget


CASE_DIR = Path(__file__).resolve().parents[2] / "docs" / "cases"


def _load_yaml(path: Path) -> Dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_cases() -> List[CaseDefinition]:
    cases: List[CaseDefinition] = []
    for path in sorted(CASE_DIR.glob("case_*.yaml")):
        raw = _load_yaml(path)
        cases.append(_to_case(raw))
    return cases


def load_case_by_id(case_id: str) -> Optional[CaseDefinition]:
    target = CASE_DIR / f"case_{case_id}.yaml"
    if target.exists():
        return _to_case(_load_yaml(target))
    for path in CASE_DIR.glob("case_*.yaml"):
        raw = _load_yaml(path)
        if raw.get("case_id") == case_id:
            return _to_case(raw)
    return None


def _to_case(raw: Dict) -> CaseDefinition:
    claims = [
        CaseClaim(
            claim_id=entry["claim_id"],
            description=entry.get("description", ""),
            truth_state=entry.get("truth_state"),
            debunk_target_id=entry.get("debunk_target_id"),
            tags=entry.get("tags", []) or [],
        )
        for entry in raw.get("claims", [])
    ]
    return CaseDefinition(
        case_id=raw["case_id"],
        title=raw["title"],
        summary=raw.get("summary", ""),
        theme=raw.get("theme", "general"),
        tags=raw.get("tags", []) or [],
        claims=claims,
        timeline=raw.get("timeline", []) or [],
        sources=raw.get("sources", []) or [],
        metadata=raw.get("metadata", {}) or {},
    )


def load_collections() -> List[CaseCollectionDefinition]:
    path = CASE_DIR / "collections.yaml"
    if not path.exists():
        return []
    raw = _load_yaml(path) or {}
    collections: List[CaseCollectionDefinition] = []
    for entry in raw.get("collections", []):
        collections.append(
            CaseCollectionDefinition(
                collection_id=entry["collection_id"],
                title=entry["title"],
                description=entry.get("description", ""),
                case_ids=entry.get("case_ids", []) or [],
                tags=entry.get("tags", []) or [],
            )
        )
    return collections


def build_debunk_summary(repo: DebunkRepository, case: CaseDefinition) -> Dict:
    """Summarize debunk issues per case by looking for open issues by target_id."""
    summary: Dict[str, int] = {"open": 0, "resolved": 0, "total": 0}
    issues = []
    for claim in case.claims:
        target_id = claim.debunk_target_id or claim.claim_id
        issue = repo.find_open_issue_for_target(DebunkIssueTarget.CLAIM, target_id)
        if issue:
            issues.append(issue)
    summary["total"] = len(issues)
    for issue in issues:
        if issue.status.value in {"RESOLVED", "CLOSED_WITH_DOUBT"}:
            summary["resolved"] += 1
        else:
            summary["open"] += 1
    summary["issues"] = [issue.id for issue in issues]
    return summary
