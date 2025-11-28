#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
export NET=0
export PYTHONPATH="${PYTHONPATH:-.}"
: "${INSPECTAH_DATA_DIR:=$ROOT/out/evidence/s9_demo}" && export INSPECTAH_DATA_DIR

python3 - <<'PY'
from pathlib import Path
from textwrap import indent

from app.admin import service
from app.user import routes
from app.observability import metrics_s9

scenarios = {
    "C1": "Qual é o preço médio atual da cesta básica padrão em São Paulo?",
    "C2": "Onde o botijão de gás 13kg está mais barato nesta semana, capital ou Baixada Fluminense?",
    "C3": "O preço médio do diesel caiu 12% em Belo Horizonte nos últimos 30 dias?",
}

base = Path("out/evidence")
print("=== Sprint 9 Demo ===")
for scenario_id, question in scenarios.items():
    print(f"\n>>> [{scenario_id}] Preparando fontes...")
    service.prepare_scenario_sources(scenario_id)
    metrics_s9.reset()
    resp = routes.post_query({"question": question, "scenario_id": scenario_id})["response"]

    summary = resp["summary_card"].copy()
    evidence = resp["evidence_links"].copy()
    print(f"Pergunta : {question}")
    print(f"Status   : {resp['status']} | Confiança: {summary.get('confidence_level')}")
    key_fields = [k for k in ("main_value", "best_location", "best_value", "verdict") if k in summary]
    for field in key_fields:
        print(f"{field:11}: {summary[field]}")
    print(f"num_sources: {summary.get('num_sources')} | limitations: {summary.get('limitations')}")

    query_id = resp["query_id"]
    bundle_id = summary.get("bundle_id")
    response_id = resp["response_id"]
    log_path = base / "s9_logs" / f"{query_id}.json"
    bundle_path = base / "s9_bundles" / f"{bundle_id}.json" if bundle_id else None
    response_path = base / "s9_responses" / f"{response_id}.json"
    print("Evidências:")
    print(indent(f"QueryLog   : {log_path}", "  "))
    if bundle_path:
        print(indent(f"Bundle     : {bundle_path}", "  "))
    print(indent(f"UserResponse: {response_path}", "  "))

    snapshot = metrics_s9.get_metrics_snapshot()
    print("Métricas (inspectah_s9_user_queries_total):")
    print(indent(str(snapshot.get("user_queries_total")), "  "))
    print("Latência (inspectah_s9_user_latency_seconds):")
    print(indent(str(snapshot.get("user_latency_seconds")), "  "))

print("\nDemo concluída. Consulte os paths acima para a trilha completa e métricas detalhadas.")
PY
