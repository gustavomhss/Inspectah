import pytest

from inspectah.ui.consultation_models import ConsultationRequest, RiskLevel
from inspectah.ui.consultation_service import ConsultationService


def test_run_consultation_known_domain_returns_result():
    service = ConsultationService()
    request = ConsultationRequest(question="Eleição para prefeito confirmada em 2024?")
    result = service.run_consultation(request)
    assert result.request_id
    assert result.answer
    assert result.risk_level in {RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.UNKNOWN}
    assert result.evidences  # motor precisa ser acionado


def test_run_consultation_unknown_domain_raises():
    service = ConsultationService()
    user_question = "???"
    result = service.run_consultation(ConsultationRequest(question=user_question))
    assert result.risk_level == RiskLevel.UNKNOWN
    assert result.insufficient_data is True
    assert result.evidences == ()
    assert all(user_question not in (e.description or "") for e in result.evidences)
