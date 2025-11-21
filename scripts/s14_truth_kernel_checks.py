"""
Sprint 14 truth kernel checks.

Lê snapshots de casos/timelines das S12/S13 e aplica invariantes mínimas:
- domínios permitidos;
- vínculo timeline → caso;
- cobertura de domínios.

Saída principal: out/evidence/S14_G1/kernel_integrity_report.json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "config" / "s14_truth_kernel.yml"
EVIDENCE_DIR = ROOT_DIR / "out" / "evidence" / "S14_G1"
REPORT_PATH = EVIDENCE_DIR / "kernel_integrity_report.json"


def _load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config não encontrada: {path}")
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Formato YAML permissivo não suportado sem dependências externas; fornecer erro explicativo
        raise ValueError(f"Config {path} precisa estar em JSON/YAML simples sem recursos avançados.")


def _load_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _collect_cases(paths: Iterable[Path]) -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []
    for base in paths:
        snapshot = base / "cases_snapshot.json"
        data = _load_json(snapshot)
        if isinstance(data, list):
            cases.extend(data)
    return cases


def _collect_timelines(paths: Iterable[Path]) -> Dict[str, List[Dict[str, Any]]]:
    timelines: Dict[str, List[Dict[str, Any]]] = {}
    for base in paths:
        snapshot = base / "timelines_snapshot.json"
        data = _load_json(snapshot)
        if isinstance(data, dict):
            timelines.update({k: v for k, v in data.items() if isinstance(v, list)})
    return timelines


def _domain_from_case_id(case_id: str) -> str:
    if ":" in case_id:
        return case_id.split(":", 1)[0]
    return ""


def _compute_metrics(
    cases: List[Dict[str, Any]],
    timelines: Dict[str, List[Dict[str, Any]]],
    allowed_domains: List[str],
) -> Tuple[Dict[str, Any], float]:
    case_map: Dict[str, str] = {}
    per_domain = {d: {"cases": 0, "cases_valid": 0, "timeline_events": 0, "timeline_valid": 0} for d in allowed_domains}
    cases_valid = 0

    for case in cases:
        case_id = case.get("id_caso")
        domain = case.get("dominio")
        if isinstance(case_id, str) and isinstance(domain, str):
            if domain in allowed_domains:
                case_map[case_id] = domain
                cases_valid += 1
                per_domain[domain]["cases_valid"] += 1
            derived = _domain_from_case_id(case_id)
            if derived in per_domain:
                per_domain[derived]["cases"] += 1

    total_cases = len(cases)
    cases_integrity_ratio = cases_valid / total_cases if total_cases else 0.0

    total_events = 0
    valid_events = 0
    timeline_keys_with_case = 0

    for case_id, events in timelines.items():
        total_events += len(events)
        has_case = case_id in case_map
        domain = _domain_from_case_id(case_id)
        if has_case:
            timeline_keys_with_case += 1
        if domain in per_domain:
            per_domain[domain]["timeline_events"] += len(events)
        for event in events:
            if has_case and domain in allowed_domains:
                valid_events += 1
                if domain in per_domain:
                    per_domain[domain]["timeline_valid"] += 1

    timeline_integrity_ratio = valid_events / total_events if total_events else 0.0
    domain_coverage_ratio = len(
        {dom for dom in allowed_domains if (per_domain.get(dom, {}).get("cases", 0) + per_domain.get(dom, {}).get("timeline_events", 0)) > 0}
    ) / len(allowed_domains) if allowed_domains else 0.0

    kernel_integrity_ratio = min(
        ratio for ratio in (cases_integrity_ratio, timeline_integrity_ratio, domain_coverage_ratio) if ratio is not None
    ) if allowed_domains else 0.0

    metrics = {
        "cases_total": total_cases,
        "cases_valid": cases_valid,
        "cases_integrity_ratio": round(cases_integrity_ratio, 4),
        "timeline_events_total": total_events,
        "timeline_events_valid": valid_events,
        "timeline_integrity_ratio": round(timeline_integrity_ratio, 4),
        "timeline_case_link_ratio": round(timeline_keys_with_case / len(timelines), 4) if timelines else 0.0,
        "domain_coverage_ratio": round(domain_coverage_ratio, 4),
        "kernel_integrity_ratio": round(kernel_integrity_ratio, 4),
    }
    return {"metrics": metrics, "per_domain": per_domain}, kernel_integrity_ratio


def run() -> None:
    config = _load_yaml(CONFIG_PATH)
    domains = config.get("domains", [])
    snapshots_cfg = config.get("snapshots", {})

    case_dirs = [
        ROOT_DIR / snapshots_cfg.get("s12_cases", "out/evidence/S12_G4/"),
        ROOT_DIR / snapshots_cfg.get("s13_timelines", "out/evidence/S13_G2/"),
    ]
    timeline_dirs = [
        ROOT_DIR / snapshots_cfg.get("s12_timelines", "out/evidence/S12_G2/"),
        ROOT_DIR / snapshots_cfg.get("s13_timelines", "out/evidence/S13_G2/"),
    ]

    cases = _collect_cases(case_dirs)
    timelines = _collect_timelines(timeline_dirs)

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    report: Dict[str, Any] = {
        "config_domains": domains,
        "input_paths": {
            "cases": [str(p) for p in case_dirs],
            "timelines": [str(p) for p in timeline_dirs],
        },
        "notes": [],
    }

    metrics_block, kernel_ratio = _compute_metrics(cases, timelines, domains)
    report.update(metrics_block)
    report["status"] = "ok" if kernel_ratio >= 0 else "error"

    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")


def main() -> None:
    run()


if __name__ == "__main__":
    main()
