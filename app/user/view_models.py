from __future__ import annotations

from typing import Any, Dict

from app.core.models import UserResponse


def build_summary_card(response: UserResponse) -> Dict[str, Any]:
    summary = dict(response.summary)
    summary["status"] = response.status
    summary["confidence_level"] = response.confidence.get("level")
    summary["confidence_reasons"] = response.confidence.get("reasons", [])
    summary["limitations"] = response.limitations
    return summary


def build_evidence_links(response: UserResponse) -> Dict[str, Any]:
    evidence = dict(response.evidence)
    return {
        "bundle_id": evidence.get("evidence_bundle_id"),
        "sources": evidence.get("sources", []),
        "items_preview": evidence.get("items_preview", []),
    }


def build_user_response_view(response: UserResponse) -> Dict[str, Any]:
    return {
        "query_id": response.query_id,
        "answer_text": response.answer_text,
        "summary_card": build_summary_card(response),
        "evidence_links": build_evidence_links(response),
        "status": response.status,
        "gpt_response_id": response.gpt_response_id,
    }
