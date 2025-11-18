from __future__ import annotations

from typing import Any, Dict

from app.core.models import UserResponse


def build_summary_card(response: UserResponse) -> Dict[str, Any]:
    summary = response.summary.copy()
    summary["status"] = response.status
    summary["confidence_level"] = response.confidence.get("level")
    summary["confidence_reasons"] = response.confidence.get("reasons", [])
    summary["limitations"] = response.limitations
    return summary


def build_evidence_links(response: UserResponse) -> Dict[str, Any]:
    evidence = response.evidence.copy()
    sources = evidence.get("sources", [])
    items_preview = evidence.get("items_preview", [])
    return {
        "bundle_id": evidence.get("bundle_id") or response.evidence_bundle_id,
        "bundle_path": evidence.get("bundle_path"),
        "sources": sources,
        "items_preview": items_preview,
    }


def build_user_response_view(response: UserResponse) -> Dict[str, Any]:
    return {
        "query_id": response.query_id,
        "response_id": response.id,
        "info_type": response.info_type,
        "query_type": response.query_type,
        "answer_text": response.answer_text,
        "summary_card": build_summary_card(response),
        "evidence_links": build_evidence_links(response),
        "status": response.status,
        "confidence": response.confidence,
        "limitations": response.limitations,
    }
