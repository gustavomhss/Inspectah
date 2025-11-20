#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S12_G5"
SCORECARD_PATH="$SCORECARD_DIR/S12_G5_explorer_e2e.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"
rm -f "$EVIDENCE_DIR"/*.json >/dev/null 2>&1 || true

python3 - <<'PY' "$EVIDENCE_DIR" "$SCORECARD_PATH"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from app.explorer import routes as explorer_routes
from scripts.s12_feedback_service import DEFAULT_FEEDBACK_SERVICE
from scripts.s12_ingest_pipeline import run_ingest_pipeline

evidence_dir = Path(sys.argv[1])
scorecard_path = Path(sys.argv[2])

DEFAULT_FEEDBACK_SERVICE.reset_store()
run_ingest_pipeline()

flows = []
logs = []
case_id = None
event_id = None

try:
    cases_resp = explorer_routes.list_cases(query="obra", limit=5)
    if not cases_resp["results"]:
        raise RuntimeError("Busca por 'obra' não retornou casos")
    case_id = cases_resp["results"][0]["id_caso"]
    (evidence_dir / "search_response.json").write_text(json.dumps(cases_resp, indent=2, ensure_ascii=False), encoding="utf-8")
    flows.append(("F1_buscar_caso", True))
    logs.append("F1: busca retornou casos")
except Exception as exc:  # pragma: no cover - mantido para logs
    flows.append(("F1_buscar_caso", False))
    logs.append(f"F1 falhou: {exc}")

if case_id:
    try:
        case_detail = explorer_routes.get_case(case_id)
        timeline = case_detail.get("timeline", [])
        if not timeline:
            raise RuntimeError("Caso não possui timeline para exibir")
        event_id = timeline[0]["id_evento"]
        (evidence_dir / "case_detail.json").write_text(json.dumps(case_detail, indent=2, ensure_ascii=False), encoding="utf-8")
        flows.append(("F2_abrir_caso", True))
        logs.append("F2: timeline carregada com sucesso")
    except Exception as exc:  # pragma: no cover
        flows.append(("F2_abrir_caso", False))
        logs.append(f"F2 falhou: {exc}")

if case_id:
    try:
        case_feedback = explorer_routes.create_case_feedback(case_id, {"mensagem": "Detalhe inconsistente no caso", "autor": "gate"})
        (evidence_dir / "case_feedback.json").write_text(json.dumps(case_feedback, indent=2, ensure_ascii=False), encoding="utf-8")
        event_payload = explorer_routes.create_event_feedback(event_id, {"mensagem": "Evento requer revisão", "autor": "gate"}) if event_id else None
        if event_payload:
            (evidence_dir / "event_feedback.json").write_text(json.dumps(event_payload, indent=2, ensure_ascii=False), encoding="utf-8")
        flows.append(("F3_feedback", True))
        logs.append("F3: feedback submetido para caso/evento")
    except Exception as exc:  # pragma: no cover
        flows.append(("F3_feedback", False))
        logs.append(f"F3 falhou: {exc}")

successes = len([flow for flow in flows if flow[1]])
total = len(flows) or 1
success_rate = successes / total
status = "PASS" if success_rate >= 0.98 else ("WARN" if success_rate >= 0.95 else "FAIL")

(evidence_dir / "flows_log.json").write_text(json.dumps({"flows": flows, "logs": logs}, indent=2, ensure_ascii=False), encoding="utf-8")

scorecard = {
    "gate": "S12-G5",
    "status": status,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "slis": {
        "SLI-4": {
            "value": round(success_rate, 3),
            "slo": 0.98,
            "status": status,
            "description": "Taxa de sucesso dos fluxos F1–F3 (Explorer v0)",
        }
    },
    "details": {
        "total_flows": total,
        "successes": successes,
        "logs": logs,
    },
}

scorecard_path.write_text(json.dumps(scorecard, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps({"status": status, "success_rate": round(success_rate, 3)}, indent=2, ensure_ascii=False))
if status != "PASS":
    raise SystemExit("S12-G5 falhou. Consulte evidências em out/evidence/S12_G5")
PY

echo "S12-G5 OK. Scorecard: $SCORECARD_PATH"
