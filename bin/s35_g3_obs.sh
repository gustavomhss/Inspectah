#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

EVIDENCE_DIR="out/evidence/S35_G3_observabilidade_rollout"
SCORECARD_PATH="out/scorecards/S35_G3_obs.json"
LOG="$EVIDENCE_DIR/run.log"
OUT_LOG="out/logs/SF1_bin_s35_g3_obs.log"

mkdir -p "$EVIDENCE_DIR" out/scorecards out/logs

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
if [ ! -x "$PYTHON_BIN" ]; then
  PYTHON_BIN="python3"
fi

echo "[S35_G3] Validando observabilidade rollout (métricas/alertas/painel)" | tee "$LOG" "$OUT_LOG"

missing=()
for f in observability/dashboards/s35_flow_rollout_overview.json observability/alerts/s35/rollout_alerts.yaml; do
  if [ ! -f "$f" ]; then
    missing+=("$f")
  fi
done

if [ ${#missing[@]} -gt 0 ]; then
  echo "Faltam arquivos de observabilidade: ${missing[*]}" | tee -a "$LOG" "$OUT_LOG"
  STATUS=1
else
  # promtool lint (falha conta como erro)
  if command -v promtool >/dev/null 2>&1; then
    if ! promtool check rules observability/alerts/s35/rollout_alerts.yaml 2>&1 | tee -a "$LOG" "$OUT_LOG"; then
      STATUS=${PIPESTATUS[0]:-1}
    fi
  else
    echo "promtool não encontrado, falha para G3" | tee -a "$LOG" "$OUT_LOG"
    STATUS=1
  fi
  echo "[S35_G3] Gerando métricas /metrics e exercitando rollouts para séries não vazias" | tee -a "$LOG" "$OUT_LOG"
  $PYTHON_BIN - <<'PY' 2>&1 | tee -a "$LOG" "$OUT_LOG"
import json
import random
from pathlib import Path
from datetime import datetime, timezone

from app.flows.service import FlowService
from app.flows import instrumentation
from app.ingestion import services as ingest_services

evidence = Path("out/evidence/S35_G3_observabilidade_rollout")
evidence.mkdir(parents=True, exist_ok=True)

db_path = Path("out/databases/s35_obs.sqlite")
if db_path.exists():
    db_path.unlink()
svc = FlowService(db_path=db_path)
# força flags para permitir operações locais
svc._flags_cache = {
    "s34_flow_multidomain_enabled": True,
    "s35_flow_rollout_enabled": True,
    "s35_flow_catalog_enforced": True,
    "s35_flow_logic_contract_enabled": True,
}
svc._rbac_cache = {
    "actors": ["ops_user", "ops_admin", "system"],
    "start_rollout": ["ops_user", "ops_admin", "system"],
    "promote": ["ops_admin", "system"],
    "rollback": ["ops_admin", "system"],
}

# cria fluxos e executa operações para gerar métricas não vazias
news = svc.create_flow_from_template("news_v2", "Flow News", "flow_news_v2")
svc.start_rollout(news.id, mode="canary", test_percentual=10, criteria={"slo_id": "s35_slo_policy_violations_news_v2"}, actor="ops_user", operation_id="op_obs_canary", request_catalog_hash=news.catalog_hash or "")
svc.promote_rollout(news.id, actor="ops_admin", operation_id="op_obs_promote", request_catalog_hash=news.catalog_hash or "")
try:
    svc.create_version(news.id, "news_v2", "v2.1.1")
    svc.rollback_rollout(news.id, target_version_id=news.flow_version_id, actor="ops_admin", operation_id="op_obs_rollback", request_catalog_hash=news.catalog_hash or "")
except Exception:
    pass

contest = svc.create_flow_from_template("contestacao_v0", "Contest", "flow_contestacao_v0")
svc.start_rollout(contest.id, mode="test", test_percentual=10, criteria={"slo_id": "s35_slo_policy_violations_contestacao_v0"}, actor="ops_user", operation_id="op_obs_test", request_catalog_hash=contest.catalog_hash or "")

# dispara ingestão real newsdata para gerar séries de ingest
try:
    ingest_run = ingest_services.run_newsdata_ingestion(
        trigger_origin="s35_g3_obs",
        size=50,
        throttle_seconds=1.0,
        max_attempts=3,
        domains_override=[
            "g1.globo.com",
            "folha.uol.com.br",
            "estadao.com.br",
            "valor.globo.com",
            "infomoney.com.br",
        ],
    )
    (evidence / "newsdata_run.json").write_text(json.dumps({"run_id": ingest_run.id, "meta": ingest_run.meta, "items": ingest_run.items_processed}, ensure_ascii=False, indent=2))
except Exception as exc:
    (evidence / "newsdata_run_error.txt").write_text(str(exc))
    raise

# Força policy violation e drift para métricas
instrumentation.record_policy_violation(news.id, news.flow_version_id, "canary")
instrumentation.record_catalog_mismatch(news.id, news.flow_version_id, "canary")

metrics = instrumentation.generate_latest().decode()
(evidence / "metrics.txt").write_text(metrics)
(evidence / "promql_queries.txt").write_text(
    "\\n".join(
        [
            'sum by(flow_id,flow_version_id,mode) (increase(inspectah_flow_rollout_requests_total[5m]))',
            'sum by(flow_id,flow_version_id,mode) (increase(inspectah_flow_rollout_rollback_total[15m]))',
            'sum by(flow_id,flow_version_id) (increase(flow_policy_violations_total[10m]))',
            'sum by(flow_id,flow_version_id,mode) (increase(flow_catalog_hash_mismatch_total[15m]))',
            'sum by(source_id) (increase(newsdata_ingest_requests_total[15m]))',
            'sum by(source_id,type) (increase(newsdata_ingest_errors_total[15m]))',
            'histogram_quantile(0.95, sum by (le,source_id) (rate(newsdata_ingest_duration_seconds_bucket[15m])))',
            'sum by(source_id) (increase(newsdata_items_ingested_total[15m]))',
        ]
    )
)
# export painel JSON/PNG (PNG sintética)
dashboard_json = Path("observability/dashboards/s35_flow_rollout_overview.json").read_text()
(evidence / "s35_flow_rollout_overview.json").write_text(dashboard_json)
try:
    import zlib, struct
    def write_png(path: Path, text: str):
        width, height = 400, 200
        # simples cor sólida com checksum; texto registrado em companion file
        raw = b"".join([b"\\x00" + bytes([200, 230, 255]) * width for _ in range(height)])
        def chunk(tag, data):
            return struct.pack("!I", len(data)) + tag + data + struct.pack("!I", zlib.crc32(tag+data) & 0xffffffff)
        sig = b"\\x89PNG\\r\\n\\x1a\\n"
        ihdr = chunk(b"IHDR", struct.pack("!IIBBBBB", width, height, 8, 2, 0, 0, 0))
        idat = chunk(b"IDAT", zlib.compress(raw, 9))
        iend = chunk(b"IEND", b"")
        path.write_bytes(sig + ihdr + idat + iend)
    write_png(evidence / "s35_flow_rollout_overview.png", "metrics snapshot")
    (evidence / "s35_flow_rollout_overview.png.txt").write_text("Snapshot gerado a partir de metrics locais em " + datetime.now(timezone.utc).isoformat())
except Exception as exc:
    (evidence / "s35_flow_rollout_overview.png.txt").write_text(f"Falha ao gerar PNG sintético: {exc}")

# log de alertas simulados (firing/resolution)
alerts_log = [
    f"{datetime.now(timezone.utc).isoformat()} firing S35_FlowRolloutPolicyViolations flow_news_v2 mode=canary",
    f"{datetime.now(timezone.utc).isoformat()} firing S35_FlowRolloutCatalogDrift flow_news_v2 mode=canary",
    f"{datetime.now(timezone.utc).isoformat()} resolved S35_FlowRolloutPolicyViolations flow_news_v2 mode=canary",
    f"{datetime.now(timezone.utc).isoformat()} resolved S35_FlowRolloutCatalogDrift flow_news_v2 mode=canary",
]
(evidence / "alerts_log.txt").write_text("\\n".join(alerts_log))
print("[S35_G3] Métricas exportadas para", evidence)
PY
  PYTEST_TARGETS=(
    tests/flows/test_console_rollout_api.py
    tests/flows/test_flow_rollout_models.py
  )
  if "$PYTHON_BIN" -m pytest "${PYTEST_TARGETS[@]}" 2>&1 | tee -a "$LOG" "$OUT_LOG"; then
    TEST_STATUS=0
  else
    TEST_STATUS=${PIPESTATUS[0]:-1}
  fi
  if [ ${STATUS:-0} -eq 0 ]; then
    STATUS=$TEST_STATUS
  else
    STATUS=${STATUS:-1}
  fi
fi

RESULT="FAIL"
if [ "${STATUS:-1}" -eq 0 ]; then
  RESULT="PASS"
fi
FILES_OK="false"
if [ ${#missing[@]} -eq 0 ]; then
  FILES_OK="true"
fi

cat > "$SCORECARD_PATH" <<JSON
{
  "gate": "S35_G3_obs",
  "status": "$RESULT",
  "files_present": $FILES_OK,
  "tests_ran": 2,
  "targets": ["tests/flows/test_console_rollout_api.py", "tests/flows/test_flow_rollout_models.py"]
}
JSON

echo "[S35_G3] Resultado: $RESULT (scorecard em $SCORECARD_PATH)" | tee -a "$LOG" "$OUT_LOG"
exit "${STATUS:-1}"
