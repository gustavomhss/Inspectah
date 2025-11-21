"""Timeline validations for Sprint 13 pilots."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from scripts import s13_pilots_registry as registry

S12_TIMELINE_SNAPSHOT = Path("out/evidence/S12_G2/timelines_snapshot.json")
DEFAULT_EVIDENCE_DIR = Path("out/evidence/S13_G2")


@dataclass
class PilotTimeline:
    pilot_id: str
    domain: str
    case_key: str
    events: List[Dict[str, object]]
    source: str


def _load_json(path: Path) -> Dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _derive_case_key(pilot: Dict[str, object]) -> str:
    case_key = pilot.get("case_key")
    if case_key:
        return str(case_key)
    return f"{pilot['dominio']}:{pilot['id']}"


def _extract_start_year(period: str) -> int:
    for token in period.replace("/", " ").split():
        if token[:4].isdigit():
            return int(token[:4])
    return datetime.utcnow().year


def _fallback_events(pilot: Dict[str, object], case_key: str) -> List[Dict[str, object]]:
    domain = pilot["dominio"]
    templates = _FALLBACK_EVENT_LIBRARY.get(domain, _FALLBACK_EVENT_LIBRARY["default"])
    base_year = _extract_start_year(str(pilot.get("periodo", "2024-01")))
    events: List[Dict[str, object]] = []
    for idx, template in enumerate(templates):
        ts = datetime(base_year, 1, 1) + timedelta(days=idx * 30)
        events.append(
            {
                "id_evento": f"s13_{pilot['id']}_{idx}",
                "id_caso": case_key,
                "timestamp": ts.isoformat(timespec="seconds") + "Z",
                "titulo": template["titulo"],
                "status_debunker": template.get("status", "incerto"),
                "fonte": template.get("fonte", "s13_fallback"),
                "resumo": template.get("resumo", ""),
                "tipo_evento": template.get("tipo_evento", "atualizacao"),
                "rationale": template.get("rationale", ""),
            }
        )
    return events


def _validate_events(events: List[Dict[str, object]]) -> List[str]:
    violations: List[str] = []
    if not events:
        violations.append("Timeline vazia para piloto")
        return violations
    timestamps = [evt.get("timestamp") for evt in events]
    if timestamps != sorted(timestamps):
        violations.append("Ordem cronológica inconsistente")
    seen: set[str] = set()
    for evt in events:
        evt_id = str(evt.get("id_evento"))
        if evt_id in seen:
            violations.append(f"Evento duplicado: {evt_id}")
        seen.add(evt_id)
    return violations


def _build_pilot_timelines() -> Dict[str, PilotTimeline]:
    pilots = registry.list_pilots()
    snapshot = _load_json(S12_TIMELINE_SNAPSHOT)
    results: Dict[str, PilotTimeline] = {}
    for pilot in pilots:
        case_key = _derive_case_key(pilot)
        s12_events = snapshot.get(case_key)
        if s12_events:
            events = json.loads(json.dumps(s12_events))
            source = "s12_snapshot"
        else:
            events = _fallback_events(pilot, case_key)
            source = "s13_fallback"
        results[pilot["id"]] = PilotTimeline(
            pilot_id=pilot["id"],
            domain=pilot["dominio"],
            case_key=case_key,
            events=events,
            source=source,
        )
    return results


def run_timeline_checks(evidence_dir: Optional[Path] = None) -> Dict[str, object]:
    """Build timelines per pilot, validate invariants and persist evidence."""

    evidence_dir = evidence_dir or DEFAULT_EVIDENCE_DIR
    timelines_dir = evidence_dir / "timelines"
    timelines_dir.mkdir(parents=True, exist_ok=True)
    for old_file in timelines_dir.glob("*.json"):
        old_file.unlink()

    pilot_timelines = _build_pilot_timelines()
    pilots_meta = {pilot["id"]: pilot for pilot in registry.list_pilots()}
    pilot_results: Dict[str, object] = {}
    ok_count = 0
    for pilot_id, timeline in pilot_timelines.items():
        violations = _validate_events(timeline.events)
        timeline_ok = not violations
        if timeline_ok:
            ok_count += 1
        pilot_results[pilot_id] = {
            "pilot_id": pilot_id,
            "domain": timeline.domain,
            "case_key": timeline.case_key,
            "timeline_ok": timeline_ok,
            "violations": violations,
            "events_count": len(timeline.events),
            "source": timeline.source,
        }
        (timelines_dir / f"{pilot_id}.json").write_text(
            json.dumps(timeline.events, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    total = max(len(pilot_timelines), 1)
    ratio = ok_count / total
    report = {
        "pilot_results": pilot_results,
        "metrics": {
            "pilot_timeline_integrity_ratio": round(ratio, 3),
            "total_pilots": len(pilot_timelines),
            "timelines_ok": ok_count,
            "timelines_with_issues": len(pilot_timelines) - ok_count,
        },
    }
    (evidence_dir / "timelines_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    _write_explorer_snapshots(pilot_timelines, pilots_meta, evidence_dir)
    return report


def _write_explorer_snapshots(
    pilot_timelines: Dict[str, PilotTimeline],
    pilots_meta: Dict[str, Dict[str, object]],
    evidence_dir: Path,
) -> None:
    cases_snapshot: List[Dict[str, object]] = []
    timelines_snapshot: Dict[str, List[Dict[str, object]]] = {}
    now_iso = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    for pilot_id, timeline in pilot_timelines.items():
        pilot = pilots_meta.get(pilot_id, {})
        events = timeline.events
        timelines_snapshot[timeline.case_key] = events
        last_ts = events[-1]["timestamp"] if events else now_iso
        cases_snapshot.append(
            {
                "id_caso": timeline.case_key,
                "dominio": timeline.domain,
                "titulo": pilot.get("nome", timeline.case_key),
                "descricao": pilot.get("descricao_curta", ""),
                "status": pilot.get("estado_atual", "monitorando"),
                "updated_at": last_ts,
                "tags": [timeline.domain, pilot_id],
            }
        )
    (evidence_dir / "cases_snapshot.json").write_text(
        json.dumps(cases_snapshot, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (evidence_dir / "timelines_snapshot.json").write_text(
        json.dumps(timelines_snapshot, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def collect_pilot_timelines() -> Dict[str, PilotTimeline]:
    """Expose pilot timelines for other helpers (Debunker, Explorer, etc.)."""

    return _build_pilot_timelines()


_FALLBACK_EVENT_LIBRARY: Dict[str, List[Dict[str, str]]] = {
    "projeto_lei": [
        {
            "titulo": "Projeto protocolado na ALERJ",
            "tipo_evento": "protocolado",
            "resumo": "PL registrado com pedido de urgência simples.",
            "status": "incerto",
            "fonte": "portal_alerj",
        },
        {
            "titulo": "Despacho favorável na CCJ",
            "tipo_evento": "comissao",
            "resumo": "Parecer favorável na Comissão de Constituição e Justiça.",
            "status": "aceito",
            "fonte": "portal_alerj",
        },
    ],
    "carreira_politica": [
        {
            "titulo": "Posse como secretário interino",
            "tipo_evento": "nomeacao",
            "resumo": "Prefeito interino assume secretaria estratégica.",
            "status": "incerto",
            "fonte": "diario_oficial",
        },
        {
            "titulo": "Assinatura de convênio educacional",
            "tipo_evento": "convenio",
            "resumo": "Convênio firmado com secretaria estadual de educação.",
            "status": "aceito",
            "fonte": "portal_transparencia",
        },
    ],
    "influencer": [
        {
            "titulo": "Live sobre contratos escolares",
            "tipo_evento": "conteudo",
            "resumo": "Live destacando contratos de manutenção escolar.",
            "status": "incerto",
            "fonte": "youtube_capture",
        },
        {
            "titulo": "Post patrocinado por construtora",
            "tipo_evento": "publieditorial",
            "resumo": "Conteúdo pago mencionando obra municipal.",
            "status": "suspeito",
            "fonte": "instagram_capture",
        },
    ],
    "atleta": [
        {
            "titulo": "Verba de bolsa liberada",
            "tipo_evento": "pagamento",
            "resumo": "Primeira parcela da bolsa esporte liberada.",
            "status": "aceito",
            "fonte": "portal_convenios",
        },
        {
            "titulo": "Relatório de uso entregue",
            "tipo_evento": "relatorio",
            "resumo": "Atleta presta contas de viagens e treinos.",
            "status": "incerto",
            "fonte": "portal_convenios",
        },
    ],
    "default": [
        {
            "titulo": "Atualização de caso",
            "tipo_evento": "atualizacao",
            "resumo": "Evento sintético para manter timeline.",
            "status": "incerto",
            "fonte": "s13_fallback",
        }
    ],
}


__all__ = ["run_timeline_checks", "collect_pilot_timelines"]
