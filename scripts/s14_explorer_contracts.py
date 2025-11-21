"""
Sprint 14 Explorer/feedback contracts gate (G3).

Usa os snapshots S13 como verdade estável para validar:
- buscas e detalhe de casos por domínio;
- fluxo básico de feedback (criar/listar/atualizar) usando o serviço da S12.

Evidência principal: out/evidence/S14_G3/explorer_contracts_report.json
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

from app.explorer import routes as explorer_backend
from scripts.s12_feedback_service import FeedbackService

ROOT_DIR = Path(__file__).resolve().parent.parent
S13_CASES_PATH = ROOT_DIR / "out" / "evidence" / "S13_G2" / "cases_snapshot.json"
S13_TIMELINES_PATH = ROOT_DIR / "out" / "evidence" / "S13_G2" / "timelines_snapshot.json"
PILOTOS_CFG = ROOT_DIR / "config" / "s13_pilotos.yml"
EVIDENCE_DIR = ROOT_DIR / "out" / "evidence" / "S14_G3"
REPORT_PATH = EVIDENCE_DIR / "explorer_contracts_report.json"
FEEDBACK_STORE = ROOT_DIR / "out" / "runtime" / "s12_feedback_store.json"


@dataclass
class ScenarioResult:
    domain: str
    scenario: str
    status: str
    reason: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "scenario": self.scenario,
            "status": self.status,
            "reason": self.reason,
        }


def _load_cases() -> List[Dict[str, Any]]:
    if not S13_CASES_PATH.exists():
        raise FileNotFoundError(f"Snapshot de casos S13 não encontrado em {S13_CASES_PATH}")
    return json.loads(S13_CASES_PATH.read_text(encoding="utf-8"))


def _load_timelines() -> Dict[str, List[Dict[str, Any]]]:
    if not S13_TIMELINES_PATH.exists():
        raise FileNotFoundError(f"Snapshot de timelines S13 não encontrado em {S13_TIMELINES_PATH}")
    return json.loads(S13_TIMELINES_PATH.read_text(encoding="utf-8"))


def _load_case_keys() -> Dict[str, str]:
    # Pilotos config é JSON; não depende de yaml
    data = json.loads(PILOTOS_CFG.read_text(encoding="utf-8"))
    mapping: Dict[str, str] = {}
    for domain, entries in data.items():
        if entries:
            mapping[domain] = entries[0].get("case_key", "")
    return mapping


def _prepare_explorer_snapshots() -> None:
    explorer_backend.CASES_SNAPSHOT_PATH = S13_CASES_PATH
    explorer_backend.TIMELINE_SNAPSHOT_PATH = S13_TIMELINES_PATH


def _search_case(case_id: str, query: str) -> Tuple[bool, str | None]:
    response = explorer_backend.list_cases(query=query, limit=50)
    ids = [entry.get("id_caso") for entry in response.get("results", [])]
    success = case_id in ids and response.get("total", 0) >= 1
    if success:
        return True, None
    return False, f"Busca não retornou o caso esperado ({case_id}) para query '{query}'"


def _detail_case(case_id: str, min_events: int = 1) -> Tuple[bool, str | None]:
    response = explorer_backend.get_case(case_id)
    timeline = response.get("timeline", [])
    case = response.get("case", {})
    if case.get("id_caso") != case_id:
        return False, f"Caso retornado inesperado: {case.get('id_caso')}"
    if len(timeline) < min_events:
        return False, f"Timeline com {len(timeline)} evento(s), mínimo exigido: {min_events}"
    return True, None


def _feedback_flow(case_id: str, service: FeedbackService) -> Tuple[bool, str | None]:
    try:
        fb = service.create_feedback_for_case(case_id, mensagem="Feedback de contrato S14", autor="g3_gate")
        listed = service.list_feedbacks()
        if not any(item.id_feedback == fb.id_feedback for item in listed):
            return False, "Feedback não encontrado na listagem após criação"
        service.update_feedback_status(fb.id_feedback, "em_analise")
        updated = service.list_feedbacks()
        target = next((item for item in updated if item.id_feedback == fb.id_feedback), None)
        if target is None or target.status != "em_analise":
            return False, "Feedback não atualizado para em_analise"
    except Exception as exc:  # pragma: no cover - guardrail do gate
        return False, str(exc)
    return True, None


def _evaluate_domain(domain: str, case_id: str, case_title: str, feedback_service: FeedbackService) -> List[ScenarioResult]:
    results: List[ScenarioResult] = []

    ok, reason = _search_case(case_id, query=case_title or case_id)
    results.append(ScenarioResult(domain, "search", "PASS" if ok else "FAIL", reason))

    ok, reason = _detail_case(case_id, min_events=1)
    results.append(ScenarioResult(domain, "detail", "PASS" if ok else "FAIL", reason))

    ok, reason = _feedback_flow(case_id, feedback_service)
    results.append(ScenarioResult(domain, "feedback", "PASS" if ok else "FAIL", reason))

    return results


def _compute_metrics(results: List[ScenarioResult]) -> Dict[str, Any]:
    total = len(results)
    passed = sum(1 for r in results if r.status == "PASS")
    per_domain: Dict[str, Dict[str, int]] = {}
    for r in results:
        stats = per_domain.setdefault(r.domain, {"total": 0, "pass": 0})
        stats["total"] += 1
        if r.status == "PASS":
            stats["pass"] += 1
    per_domain_ratio = {dom: round(stats["pass"] / stats["total"], 3) if stats["total"] else 0.0 for dom, stats in per_domain.items()}
    return {
        "explorer_contract_success_ratio": round(passed / total, 3) if total else 0.0,
        "per_domain_explorer_contract_ratio": per_domain_ratio,
    }


def run() -> None:
    cases = _load_cases()
    timelines = _load_timelines()
    case_keys = _load_case_keys()
    _prepare_explorer_snapshots()

    # Reset feedback store para evitar flutuação
    feedback_service = FeedbackService(store_path=FEEDBACK_STORE)
    feedback_service.reset_store()

    cases_by_domain: Dict[str, Dict[str, Any]] = {}
    for case in cases:
        dom = case.get("dominio")
        if not isinstance(dom, str):
            continue
        cases_by_domain.setdefault(dom, case)

    scenario_results: List[ScenarioResult] = []
    for domain, case in cases_by_domain.items():
        if domain not in case_keys:
            scenario_results.append(ScenarioResult(domain, "setup", "FAIL", "case_key não encontrado no config de pilotos"))
            continue
        case_id = case_keys[domain]
        title = case.get("titulo") or case_id
        if case_id not in timelines:
            scenario_results.append(ScenarioResult(domain, "setup", "FAIL", f"Timeline ausente para {case_id}"))
            continue
        scenario_results.extend(_evaluate_domain(domain, case_id, title, feedback_service))

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    metrics = _compute_metrics(scenario_results)
    report = {
        "inputs": {
            "cases_snapshot": str(S13_CASES_PATH),
            "timelines_snapshot": str(S13_TIMELINES_PATH),
            "pilotos_config": str(PILOTOS_CFG),
        },
        "metrics": metrics,
        "scenarios": [r.to_dict() for r in scenario_results],
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")


def main() -> None:
    run()


if __name__ == "__main__":
    main()
