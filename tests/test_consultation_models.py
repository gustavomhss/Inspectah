import pytest
from pydantic import ValidationError

from inspectah.ui.consultation_models import ConsultationEvidence, ConsultationRequest, ConsultationResult, RiskLevel


def test_request_validation_and_trim():
    payload = ConsultationRequest(question="  Isso é um teste?  ", locale="pt-BR")
    assert payload.question == "Isso é um teste?"
    with pytest.raises(ValidationError):
        ConsultationRequest(question="   ")


def test_result_to_response_keeps_shape():
    evidence = ConsultationEvidence(
        id="ev-1",
        source_name="debunker",
        source_type="debunker",
        description="Evidência de teste",
        stance="for",
    )
    result = ConsultationResult(
        request_id="req-1",
        answer="ok",
        risk_level=RiskLevel.LOW,
        evidences=[evidence],
        risk_flags=("committee_v1:approved",),
    )
    response = result.to_response()
    assert response.request_id == "req-1"
    assert response.answer_text == response.answer
    assert response.evidences
    assert response.evidence is not None
    assert response.risk_level == RiskLevel.LOW

