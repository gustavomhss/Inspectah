#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S12_G6"
SCORECARD_PATH="$SCORECARD_DIR/S12_G6_feedback_flow.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"
rm -f "$EVIDENCE_DIR"/*.json >/dev/null 2>&1 || true

python3 - <<'PY' "$EVIDENCE_DIR" "$SCORECARD_PATH"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from app.explorer import routes as explorer_routes
from app.feedback import routes as feedback_routes
from scripts.s12_feedback_service import DEFAULT_FEEDBACK_SERVICE
from scripts.s12_ingest_pipeline import run_ingest_pipeline

EVIDENCE_DIR = Path(sys.argv[1])
SCORECARD_PATH = Path(sys.argv[2])

DEFAULT_FEEDBACK_SERVICE.reset_store()
run_ingest_pipeline()

# garante que existe um caso e um evento válidos
cases_snapshot = explorer_routes.list_cases(limit=5)["results"]
if not cases_snapshot:
    raise SystemExit("Nenhum caso disponível para testar feedbacks")
case_id = cases_snapshot[0]["id_caso"]
case_detail = explorer_routes.get_case(case_id)
timeline = case_detail.get("timeline", [])
if not timeline:
    raise SystemExit("Nenhum evento disponível para feedback")
event_id = timeline[0]["id_evento"]

created = []
case_feedback = explorer_routes.create_case_feedback(case_id, {"mensagem": "Caso com dados divergentes", "autor": "gate"})
created.append(case_feedback["feedback"]["id_feedback"])
(EVIDENCE_DIR / "case_feedback.json").write_text(json.dumps(case_feedback, indent=2, ensure_ascii=False), encoding="utf-8")

event_feedback = explorer_routes.create_event_feedback(event_id, {"mensagem": "Evento requer revisão", "autor": "gate"})
created.append(event_feedback["feedback"]["id_feedback"])
(EVIDENCE_DIR / "event_feedback.json").write_text(json.dumps(event_feedback, indent=2, ensure_ascii=False), encoding="utf-8")

novo_feedbacks = feedback_routes.list_feedbacks("novo")
(EVIDENCE_DIR / "feedback_list_novo.json").write_text(json.dumps(novo_feedbacks, indent=2, ensure_ascii=False), encoding="utf-8")

for fb_id, target_status in zip(created, ["em_analise", "resolvido"]):
    feedback_routes.update_feedback(fb_id, {"status": target_status})

after_update = feedback_routes.list_feedbacks("todos")
(EVIDENCE_DIR / "feedback_list_final.json").write_text(json.dumps(after_update, indent=2, ensure_ascii=False), encoding="utf-8")

created_count = len(created)
delivered = len(novo_feedbacks["items"])
delivery_ratio = delivered / created_count if created_count else 0.0
status = "PASS" if abs(delivery_ratio - 1.0) < 1e-9 else "FAIL"

scorecard = {
    "gate": "S12-G6",
    "status": status,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "slis": {
        "SLI-5": {
            "value": round(delivery_ratio, 3),
            "slo": 1.0,
            "status": status,
            "description": "Feedbacks entregues à fila interna / feedbacks enviados",
        }
    },
    "details": {
        "created": created_count,
        "listed_novo": delivered,
        "final_statuses": [entry["status"] for entry in after_update["items"] if entry["id_feedback"] in created],
    },
}

SCORECARD_PATH.write_text(json.dumps(scorecard, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps({"status": status, "feedback_delivery_ratio": delivery_ratio}, indent=2, ensure_ascii=False))
if status != "PASS":
    raise SystemExit("S12-G6 falhou. Consulte evidências em out/evidence/S12_G6")
PY

echo "S12-G6 OK. Scorecard: $SCORECARD_PATH"
