"""Feedback backlog generator for Sprint 13 multi-domain pilots."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List

from scripts.s12_feedback_service import DEFAULT_FEEDBACK_SERVICE, VALID_STATUSES

DOC_PATH = Path("docs/sprint_13_cenarios_feedback.md")
DEFAULT_EVIDENCE_DIR = Path("out/evidence/S13_G6")
SCENARIOS_RESULTS = "feedback_scenarios_results.json"
BACKLOG_FILE = "backlog_s14_seed.json"
LOG_FILE = "feedback_log.txt"
BEGIN_MARKER = "<!-- S13_FEEDBACK_SCENARIOS:BEGIN -->"
END_MARKER = "<!-- S13_FEEDBACK_SCENARIOS:END -->"


class FeedbackScenarioError(RuntimeError):
    """Raised when the scenario roster is inconsistent."""


def _load_scenarios() -> List[Dict[str, object]]:
    if not DOC_PATH.exists():
        raise FeedbackScenarioError(f"Documento de cenários não encontrado: {DOC_PATH}")
    text = DOC_PATH.read_text(encoding="utf-8")
    begin = text.find(BEGIN_MARKER)
    end = text.find(END_MARKER)
    if begin == -1 or end == -1 or end <= begin:
        raise FeedbackScenarioError("Marcadores de cenário não encontrados em docs/sprint_13_cenarios_feedback.md")
    block = text[begin:end]
    match = re.search(r"```json\s*(.*?)```", block, re.S)
    if not match:
        raise FeedbackScenarioError("Bloco JSON com cenários não encontrado")
    try:
        scenarios = json.loads(match.group(1))
    except json.JSONDecodeError as exc:  # pragma: no cover - validação de arquivo
        raise FeedbackScenarioError(f"Cenários inválidos: {exc}") from exc
    if not isinstance(scenarios, list) or not scenarios:
        raise FeedbackScenarioError("Lista de cenários vazia ou inválida")
    return scenarios  # type: ignore[return-value]


def _reset_store() -> None:
    DEFAULT_FEEDBACK_SERVICE.reset_store()


def run_feedback_backlog(evidence_dir: Path | None = None) -> Dict[str, object]:
    evidence_dir = evidence_dir or DEFAULT_EVIDENCE_DIR
    evidence_dir.mkdir(parents=True, exist_ok=True)
    scenarios = _load_scenarios()

    _reset_store()
    service = DEFAULT_FEEDBACK_SERVICE

    per_domain: Dict[str, Dict[str, int]] = {}
    scenario_results: List[Dict[str, object]] = []
    success_count = 0
    log_lines: List[str] = []

    for scenario in scenarios:
        scenario_id = str(scenario.get("scenario_id"))
        domain = str(scenario.get("domain"))
        case_id = str(scenario.get("case_id"))
        operation = str(scenario.get("operation", "create"))
        payload = scenario.get("payload", {}) or {}
        expected = scenario.get("expected", {}) or {}
        per_domain.setdefault(domain, {"total": 0, "success": 0})["total"] += 1
        try:
            result = _execute_scenario(service, case_id, operation, payload, expected)
            success = result["success"]
            reason = result.get("reason")
            details = result.get("details", {})
        except Exception as exc:  # pragma: no cover - proteção adicional
            success = False
            reason = str(exc)
            details = {}
        if success:
            success_count += 1
            per_domain[domain]["success"] += 1
        scenario_results.append(
            {
                "scenario_id": scenario_id,
                "domain": domain,
                "case_id": case_id,
                "operation": operation,
                "status": "PASS" if success else "FAIL",
                "reason": reason,
                "details": details,
            }
        )
        log_lines.append(f"[{scenario_id}] {operation} -> {'PASS' if success else 'FAIL'} {reason or ''}".strip())

    total = len(scenarios)
    success_rate = success_count / total if total else 1.0
    per_domain_ratio = {
        domain: (stats["success"] / stats["total"]) if stats["total"] else 1.0
        for domain, stats in per_domain.items()
    }

    scenarios_path = evidence_dir / SCENARIOS_RESULTS
    scenarios_path.write_text(
        json.dumps(
            {
                "scenarios": scenario_results,
                "feedback_delivery_ratio": round(success_rate, 3),
                "per_domain_feedback_ratio": {k: round(v, 3) for k, v in per_domain_ratio.items()},
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    backlog = [entry.to_dict() for entry in service.list_feedbacks(status="todos")]
    (evidence_dir / BACKLOG_FILE).write_text(json.dumps(backlog, indent=2, ensure_ascii=False), encoding="utf-8")
    (evidence_dir / LOG_FILE).write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    return {
        "feedback_delivery_ratio": round(success_rate, 3),
        "per_domain_feedback_ratio": {k: round(v, 3) for k, v in per_domain_ratio.items()},
        "scenarios": scenario_results,
    }


def _execute_scenario(
    service,
    case_id: str,
    operation: str,
    payload: Dict[str, object],
    expected: Dict[str, object],
) -> Dict[str, object]:
    if operation == "create":
        feedback = service.create_feedback_for_case(
            case_id,
            mensagem=str(payload.get("mensagem", "Feedback automático da S13")),
            autor=str(payload.get("origem", "s13_g6")),
        )
        expected_status = expected.get("status")
        success = expected_status is None or feedback.status == expected_status
        reason = None if success else f"Status esperado {expected_status}, obtido {feedback.status}"
        return {"success": success, "reason": reason, "details": {"feedback_id": feedback.id_feedback}}
    if operation == "create_and_list":
        feedback = service.create_feedback_for_case(
            case_id,
            mensagem=str(payload.get("mensagem", "Feedback automático da S13")),
            autor=str(payload.get("origem", "s13_g6")),
        )
        listed = any(entry.id_feedback == feedback.id_feedback for entry in service.list_feedbacks(status="todos"))
        list_expected = expected.get("list_contains", True)
        success = listed == bool(list_expected)
        reason = None if success else "Feedback não encontrado na listagem"
        return {
            "success": success,
            "reason": reason,
            "details": {"feedback_id": feedback.id_feedback, "listed": listed},
        }
    if operation == "create_then_update":
        feedback = service.create_feedback_for_case(
            case_id,
            mensagem=str(payload.get("mensagem", "Feedback automático da S13")),
            autor=str(payload.get("origem", "s13_g6")),
        )
        update_to = str(payload.get("novo_status", "em_analise"))
        if update_to not in VALID_STATUSES:
            raise FeedbackScenarioError(f"Status inválido no cenário: {update_to}")
        updated = service.update_feedback_status(feedback.id_feedback, update_to)
        final_expected = expected.get("final_status")
        success = final_expected is None or updated.status == final_expected
        reason = None if success else f"Status final esperado {final_expected}, obtido {updated.status}"
        return {
            "success": success,
            "reason": reason,
            "details": {"feedback_id": feedback.id_feedback, "final_status": updated.status},
        }
    raise FeedbackScenarioError(f"Operação desconhecida no cenário: {operation}")


def main() -> None:
    report = run_feedback_backlog()
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":  # pragma: no cover
    main()
