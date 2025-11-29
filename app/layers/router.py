from __future__ import annotations

from app.layers.orchestrator import run_hardened_pipeline, run_standard_pipeline


SENSITIVE_DOMAINS = {"politics", "science"}


def route_and_run(claim_id: str, domain: str, case_id: str | None = None, truth_repo=None):
    if domain.lower() in SENSITIVE_DOMAINS:
        return run_hardened_pipeline(claim_id=claim_id, domain=domain, case_id=case_id, truth_repo=truth_repo)
    return run_standard_pipeline(claim_id=claim_id, domain=domain, case_id=case_id, truth_repo=truth_repo)
