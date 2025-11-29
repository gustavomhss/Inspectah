#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python3"
fi

export PYTHONPATH="$ROOT_DIR"

"$PYTHON_BIN" - <<'PY'
from app.admin import service
from app.user import routes

service.ensure_default_sources()

queries = [
    "Qual o preço médio do arroz em São Paulo?",
    "Onde o arroz está mais barato em São Paulo?",
    "João Mendes foi condenado na Operação Horizonte?",
]

for query in queries:
    payload = routes.post_query({"query": query})
    dto = payload["dto"]
    print("=" * 80)
    print("Pergunta:", query)
    print("Resposta:", dto["answer_text"])
    print("Resumo:", dto["summary"])
    print("Confiança:", dto["confidence"])
    print("Evidências:", dto["evidence"])
PY
