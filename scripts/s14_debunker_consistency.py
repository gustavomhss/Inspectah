"""
Sprint 14 Debunker consistency checks.

Constroi eventos fixos por domínio, passa pelo s12_debunker_runner
e mede debunker_explanation_coverage global e por domínio.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from scripts import s12_debunker_runner

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "config" / "s14_debunker_rules.yml"
KERNEL_CONFIG_PATH = ROOT_DIR / "config" / "s14_truth_kernel.yml"
EVIDENCE_DIR = ROOT_DIR / "out" / "evidence" / "S14_G2"
REPORT_PATH = EVIDENCE_DIR / "debunker_consistency_report.json"


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config não encontrada: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _load_configs() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    debunker_cfg = _load_json(CONFIG_PATH)
    kernel_cfg = _load_json(KERNEL_CONFIG_PATH)
    return debunker_cfg, kernel_cfg


def _synthetic_events(domains: List[str], case_keys: Dict[str, List[str]]) -> Dict[str, List[Dict[str, Any]]]:
    events: Dict[str, List[Dict[str, Any]]] = {}
    for dom in domains:
        key = (case_keys.get(dom) or [""])[0]
        base = {
            "dominio": dom,
            "case_id": key,
            "case_key": key,
        }
        if dom == "obra_publica":
            events[dom] = [
                {**base, "id_evento": f"{dom}_denuncia", "resumo": "Denuncia de paralisação da obra", "tipo_evento": "denuncia"},
                {**base, "id_evento": f"{dom}_financeiro", "resumo": "Pagamento de medição", "tipo_evento": "pagamento"},
            ]
        elif dom == "evento_climatico":
            events[dom] = [
                {**base, "id_evento": f"{dom}_laranja", "resumo": "Alerta INMET", "tipo_evento": "alerta", "metadata": {"nivel": "laranja"}},
                {**base, "id_evento": f"{dom}_verde", "resumo": "Clima estável", "tipo_evento": "informativo", "metadata": {"nivel": "verde"}},
            ]
        else:
            events[dom] = [
                {**base, "id_evento": f"{dom}_padrao", "resumo": "Evento sintético para domínio não calibrado", "tipo_evento": "sintetico"},
            ]
    return events


def _coverage(decisions: List[Dict[str, Any]]) -> float:
    if not decisions:
        return 0.0
    explained = sum(1 for d in decisions if str(d.get("rationale", "")).strip())
    return explained / len(decisions)


def _evaluate(events_by_domain: Dict[str, List[Dict[str, Any]]]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    all_decisions: List[Dict[str, Any]] = []
    per_domain_metrics: Dict[str, Any] = {}
    for dom, events in events_by_domain.items():
        decisions = s12_debunker_runner.evaluate_batch(events)
        all_decisions.extend(decisions)
        per_domain_metrics[dom] = {
            "total_events": len(events),
            "decisions": s12_debunker_runner.summarize_decisions(decisions),
            "explanation_coverage": round(_coverage(decisions), 4),
            "sample": decisions[:2],
        }

    global_coverage = round(_coverage(all_decisions), 4)
    return {
        "global": {
            "total_events": len(all_decisions),
            "explanation_coverage": global_coverage,
            "by_decision": s12_debunker_runner.summarize_decisions(all_decisions).get("by_decision", {}),
        },
        "per_domain": per_domain_metrics,
    }, all_decisions


def run() -> None:
    debunker_cfg, kernel_cfg = _load_configs()
    domains = list(debunker_cfg.get("domains", {}).keys())
    kernel_case_keys = kernel_cfg.get("case_keys", {})

    events = _synthetic_events(domains, kernel_case_keys)
    metrics, decisions = _evaluate(events)

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "config": {
            "defaults": debunker_cfg.get("defaults", {}),
            "domain_targets": {d: debunker_cfg["domains"].get(d, {}) for d in domains},
        },
        "metrics": metrics,
        "decisions_sample": decisions[:6],
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")


def main() -> None:
    run()


if __name__ == "__main__":
    main()
