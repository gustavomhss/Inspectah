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
from app.observability import metrics_s9
from app.user import routes

scenarios = {
    "C1": "Qual é o preço médio atual da cesta básica padrão em São Paulo?",
    "C2": "Onde o botijão de gás 13kg está mais barato nesta semana, capital ou Baixada Fluminense?",
    "C3": "O preço médio do diesel caiu 12% em Belo Horizonte nos últimos 30 dias?",
}

base = Path("out/evidence")
print("=== Sprint 9 Demo ===")
for scenario_id, question in scenarios.items():
    print(f"\n>>> Preparando fontes para {scenario_id}")
    service.prepare_scenario_sources(scenario_id)
    metrics_s9.reset()
    response = routes.post_query({"question": question, "scenario_id": scenario_id})["response"]
    summary = response["summary_card"]

    print(f"Pergunta : {question}")
    print(f"Status   : {response['status']} | Confiança: {summary.get('confidence_level')} | num_sources: {summary.get('num_sources')}")
    for field in ("main_value", "range", "best_location", "best_value", "verdict"):
        if field in summary:
            print(f"{field:11}: {summary[field]}")
    print(f"Limitations: {summary.get('limitations')}")
    print(f"Answer    : {response['answer_text']}")

    query_id = response["query_id"]
    bundle_id = summary.get("bundle_id")
    response_id = response["response_id"]
    log_path = base / "s9_logs" / f"{query_id}.json"
    bundle_path = base / "s9_bundles" / f"{bundle_id}.json" if bundle_id else None
    response_path = base / "s9_responses" / f"{response_id}.json"
    print("Evidências:")
    print(indent(f"QueryLog   : {log_path}", "  "))
    if bundle_path:
        print(indent(f"Bundle     : {bundle_path}", "  "))
    print(indent(f"UserResponse: {response_path}", "  "))

    snapshot = metrics_s9.get_metrics_snapshot()
    print("Métricas (user_queries_total):")
    print(indent(str(snapshot.get("user_queries_total")), "  "))
    print("Métricas (user_latency_seconds):")
    print(indent(str(snapshot.get("user_latency_seconds")), "  "))

print("\nDemo concluída. Consulte os arquivos acima para a trilha completa.")
PY
