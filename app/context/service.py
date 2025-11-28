from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Optional

from app.context.models import CaseContextDossier, DossierClaim, EntityContextDossier
from app.cases.loader import load_case_by_id
from app.debunk.repository import DebunkRepository
from app.debunk.models import DebunkIssueTarget
from app.truth.repository import TruthRepository
from app.demo.golden_sets_loader import load_golden_case


def _truth_events_for_claim(claim_id: str, domain: str, truth_repo: TruthRepository) -> List[Dict]:
    slug = f"{domain}:{claim_id}"
    record = truth_repo.get_record_by_slug(slug)
    if not record:
        return []
    events = truth_repo.list_events(record.id)
    return [asdict(e) for e in events]


def build_case_dossier(
    case_id: str,
    truth_repo: Optional[TruthRepository] = None,
    debunk_repo: Optional[DebunkRepository] = None,
    golden_base: Path = Path("data/s25/golden_sets"),
) -> CaseContextDossier:
    repo_truth = truth_repo or TruthRepository()
    repo_debunk = debunk_repo or DebunkRepository()
    golden = load_golden_case(case_id, base_dir=golden_base)
    case = load_case_by_id(case_id) or golden.case_definition

    claims: List[DossierClaim] = []
    debunk_issue_ids: List[str] = []
    for claim in case.claims:
        events = _truth_events_for_claim(claim.claim_id, case.theme, repo_truth)
        issues = []
        issue = repo_debunk.find_open_issue_for_target(DebunkIssueTarget.CLAIM, claim.claim_id)
        if issue:
            issues.append(issue.id)
            debunk_issue_ids.extend(issues)
        claims.append(
            DossierClaim(
                claim_id=claim.claim_id,
                domain=case.theme,
                description=claim.description,
                truth_state=claim.truth_state,
                debunk_issue_ids=issues,
                case_ids=[case.case_id],
                entities=golden.claim_entities.get(claim.claim_id, []),
                sources=golden.claim_sources.get(claim.claim_id, []),
                events=events,
            )
        )

    return CaseContextDossier(
        case_id=case.case_id,
        domain=case.theme,
        title=case.title,
        claims=claims,
        entities=list(golden.entities),
        debunk_issue_ids=debunk_issue_ids,
        truth_events=[event for claim in claims for event in claim.events],
        summary=golden.summary,
    )


def build_entity_dossier(
    entity_id: str,
    truth_repo: Optional[TruthRepository] = None,
    debunk_repo: Optional[DebunkRepository] = None,
    golden_base: Path = Path("data/s25/golden_sets"),
) -> EntityContextDossier:
    repo_truth = truth_repo or TruthRepository()
    repo_debunk = debunk_repo or DebunkRepository()
    # Agrega claims e casos a partir dos golden sets
    claims: List[DossierClaim] = []
    cases: List[str] = []
    for path in sorted(Path(golden_base).glob("*")):
        if not path.is_dir():
            continue
        golden = load_golden_case(path.name, base_dir=golden_base)
        for claim in golden.claims:
            if entity_id in claim.get("entities", []):
                cases.append(golden.case_id)
                events = _truth_events_for_claim(claim["id"], golden.domain, repo_truth)
                issue = repo_debunk.find_open_issue_for_target(DebunkIssueTarget.CLAIM, claim["id"])
                issues = [issue.id] if issue else []
                claims.append(
                    DossierClaim(
                        claim_id=claim["id"],
                        domain=golden.domain,
                        description=claim.get("description", ""),
                        truth_state=claim.get("expected_state"),
                        debunk_issue_ids=issues,
                        case_ids=[golden.case_id],
                        entities=claim.get("entities", []),
                        sources=claim.get("sources", []),
                        events=events,
                    )
                )
    cases_unique = sorted(set(cases))
    domain = claims[0].domain if claims else "general"
    return EntityContextDossier(
        entity_id=entity_id,
        domain=domain,
        claims=claims,
        cases=cases_unique,
        summary=f"{entity_id} com {len(claims)} claims monitoradas",
    )
