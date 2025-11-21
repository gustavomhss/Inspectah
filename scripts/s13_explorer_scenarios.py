"""Explorer scenarios for Sprint 13 multi-domínio validation."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List

from app.explorer import routes as explorer_backend

DOC_PATH = Path("docs/sprint_13_cenarios_explorer.md")
EVIDENCE_DIR = Path("out/evidence/S13_G4")
QUERIES_DIR = EVIDENCE_DIR / "queries"
S13_CASES_PATH = Path("out/evidence/S13_G2/cases_snapshot.json")
S13_TIMELINES_PATH = Path("out/evidence/S13_G2/timelines_snapshot.json")
BEGIN_MARKER = "<!-- S13_EXPLORER_SCENARIOS:BEGIN -->"
END_MARKER = "<!-- S13_EXPLORER_SCENARIOS:END -->"


class ExplorerScenarioError(RuntimeError):
    """Raised when the scenario roster is inconsistent."""


def _load_scenarios() -> List[Dict[str, object]]:
    if not DOC_PATH.exists():
        raise ExplorerScenarioError(f"Documento de cenários não encontrado: {DOC_PATH}")
    text = DOC_PATH.read_text(encoding="utf-8")
    begin = text.find(BEGIN_MARKER)
    end = text.find(END_MARKER)
    if begin == -1 or end == -1 or end <= begin:
        raise ExplorerScenarioError("Marcadores de cenário não encontrados em docs/sprint_13_cenarios_explorer.md")
    block = text[begin:end]
    match = re.search(r"```json\s*(.*?)```", block, re.S)
    if not match:
        raise ExplorerScenarioError("Bloco JSON com cenários não encontrado")
    try:
        scenarios = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise ExplorerScenarioError(f"Cenários inválidos: {exc}") from exc
    if not isinstance(scenarios, list) or not scenarios:
        raise ExplorerScenarioError("Lista de cenários vazia ou inválida")
    return scenarios  # type: ignore[return-value]


def _prepare_explorer_backend() -> None:
    if not S13_CASES_PATH.exists() or not S13_TIMELINES_PATH.exists():
        raise ExplorerScenarioError(
            "Snapshots S13_G2 não encontrados. Rode G2 antes de executar os cenários do Explorer."
        )
    explorer_backend.CASES_SNAPSHOT_PATH = S13_CASES_PATH.resolve()
    explorer_backend.TIMELINE_SNAPSHOT_PATH = S13_TIMELINES_PATH.resolve()


def _evaluate_search_scenario(scenario: Dict[str, object]) -> Dict[str, object]:
    query = str(scenario.get("query", ""))
    expected_case_id = str(scenario.get("expected_case_id"))
    min_results = int(scenario.get("min_results", 1))
    response = explorer_backend.list_cases(query=query, limit=50)
    case_ids = [entry.get("id_caso") for entry in response.get("results", [])]
    has_expected = expected_case_id in case_ids
    meets_count = response.get("total", 0) >= min_results
    success = has_expected and meets_count
    return {
        "success": success,
        "reason": None if success else _build_search_failure_reason(has_expected, meets_count, expected_case_id),
        "evidence": {
            "request": {"query": query},
            "response": response,
        },
    }


def _build_search_failure_reason(has_expected: bool, meets_count: bool, expected_case_id: str) -> str:
    if not has_expected and not meets_count:
        return f"Resultado esperado {expected_case_id} não encontrado e total insuficiente."
    if not has_expected:
        return f"Resultado esperado {expected_case_id} não encontrado."
    return "Total de resultados abaixo do mínimo configurado."


def _evaluate_detail_scenario(scenario: Dict[str, object]) -> Dict[str, object]:
    case_id = str(scenario.get("case_id"))
    min_events = int(scenario.get("min_timeline_events", 1))
    response = explorer_backend.get_case(case_id)
    timeline = response.get("timeline", [])
    case = response.get("case", {})
    success = bool(timeline) and len(timeline) >= min_events and case.get("id_caso") == case_id
    reason = None
    if not success:
        if case.get("id_caso") != case_id:
            reason = f"Caso retornado inesperado ({case.get('id_caso')})."
        elif not timeline:
            reason = "Timeline vazia."
        else:
            reason = f"Timeline com {len(timeline)} evento(s), mínimo exigido: {min_events}."
    evidence = {
        "request": {"case_id": case_id},
        "response": {
            "case": case,
            "stats": response.get("stats", {}),
            "events_sample": timeline[:5],
        },
    }
    return {"success": success, "reason": reason, "evidence": evidence}


def run_explorer_scenarios() -> Dict[str, object]:
    _prepare_explorer_backend()
    scenarios = _load_scenarios()
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    QUERIES_DIR.mkdir(parents=True, exist_ok=True)

    per_domain: Dict[str, Dict[str, int]] = {}
    scenario_results: List[Dict[str, object]] = []
    success_count = 0

    for scenario in scenarios:
        scenario_id = str(scenario.get("scenario_id"))
        domain = str(scenario.get("domain"))
        scenario_type = str(scenario.get("type"))
        per_domain.setdefault(domain, {"total": 0, "success": 0})["total"] += 1
        try:
            if scenario_type == "search":
                evaluation = _evaluate_search_scenario(scenario)
            elif scenario_type == "detail":
                evaluation = _evaluate_detail_scenario(scenario)
            else:
                raise ExplorerScenarioError(f"Tipo de cenário desconhecido: {scenario_type}")
            success = evaluation["success"]
            reason = evaluation["reason"]
            evidence_payload = evaluation["evidence"]
        except Exception as exc:  # pragma: no cover
            success = False
            reason = str(exc)
            evidence_payload = {"error": reason}
        if success:
            success_count += 1
            per_domain[domain]["success"] += 1
        (QUERIES_DIR / f"{scenario_id}.json").write_text(
            json.dumps({"scenario": scenario, "result": evidence_payload}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        scenario_results.append(
            {
                "scenario_id": scenario_id,
                "domain": domain,
                "type": scenario_type,
                "status": "PASS" if success else "FAIL",
                "reason": reason,
            }
        )

    total = len(scenarios)
    success_rate = success_count / total if total else 1.0
    per_domain_success = {
        domain: (stats["success"] / stats["total"] if stats["total"] else 1.0)
        for domain, stats in per_domain.items()
    }

    return {
        "explorer_success_rate": round(success_rate, 3),
        "per_domain_success_rate": {k: round(v, 3) for k, v in per_domain_success.items()},
        "scenarios": scenario_results,
    }


__all__ = ["run_explorer_scenarios"]
