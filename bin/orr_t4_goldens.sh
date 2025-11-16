#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}" )/.." && pwd)
EVIDENCE_DIR="$ROOT/out/evidence/S4_T4_goldens"
SCORECARD_PATH="$ROOT/out/scorecards/S4_T4_goldens.json"
mkdir -p "$EVIDENCE_DIR"
REPORT="$EVIDENCE_DIR/report.txt"
DIFF_JSON="$EVIDENCE_DIR/diff_examples.json"
TMP_RESULTS=$(mktemp -d)
export S4_T4_RESULTS_DIR="$TMP_RESULTS"
cd "$ROOT"
poetry run pytest tests/sprint_4 -k T4_ --maxfail=1
python3 <<'PY'
import json
import os
from pathlib import Path
root = Path(os.environ.get("ROOT", ".")).resolve()
evidence_dir = root / "out" / "evidence" / "S4_T4_goldens"
report_path = evidence_dir / "report.txt"
diff_path = evidence_dir / "diff_examples.json"
results_dir = Path(os.environ["S4_T4_RESULTS_DIR"])
expected_sources = ["api_market_prices", "html_market_watch", "rss_news_minimal"]
sources_data = {}
for src in expected_sources:
    results_file = results_dir / f"{src}.json"
    if results_file.exists():
        sources_data[src] = json.loads(results_file.read_text())
    else:
        sources_data[src] = []
report_lines = []
diffs = {}
fixtures_total = 0
fixtures_fail = 0
for source, entries in sources_data.items():
    for entry in entries:
        fixtures_total += 1
        status = entry.get("status", "UNKNOWN")
        diff_count = len(entry.get("diffs", []))
        if diff_count:
            fixtures_fail += 1
            diffs.setdefault(source, []).append(entry)
        report_lines.append(f"[{source}] {entry.get('fixture')} {status} diffs={diff_count}")
report_path.write_text("\n".join(report_lines) + ("\n" if report_lines else ""))
diff_path.write_text(json.dumps(diffs, indent=2, ensure_ascii=False))
status_flag = "PASS" if fixtures_fail == 0 and all(sources_data[src] for src in expected_sources) else "FAIL"
checks = [
    {"name": "api_market_prices_goldens", "status": "PASS" if all(e.get("status") == "PASS" for e in sources_data["api_market_prices"]) and sources_data["api_market_prices"] else "FAIL", "details": f"fixtures={len(sources_data['api_market_prices'])}"},
    {"name": "html_market_watch_goldens", "status": "PASS" if all(e.get("status") == "PASS" for e in sources_data["html_market_watch"]) and sources_data["html_market_watch"] else "FAIL", "details": f"fixtures={len(sources_data['html_market_watch'])}"},
    {"name": "rss_news_minimal_goldens", "status": "PASS" if all(e.get("status") == "PASS" for e in sources_data["rss_news_minimal"]) and sources_data["rss_news_minimal"] else "FAIL", "details": f"fixtures={len(sources_data['rss_news_minimal'])}"},
    {"name": "no_critical_diffs", "status": "PASS" if fixtures_fail == 0 else "FAIL", "details": f"diffs_críticos={fixtures_fail}"}
]
scorecard = {
    "sprint_id": "S4",
    "gate_id": "S4_T4",
    "gate_name": "Sprint 4 - T4 Goldens & Diffs",
    "status": status_flag,
    "summary": "Comparação fixture→golden executada para as Fontes P0",
    "invariants_guarded": [
        "Determinismo frente a fixtures reais",
        "Contrato de comportamento versionado",
        "Sem regressões silenciosas"
    ],
    "checks": checks,
    "metrics": {
        "goldens_total": sum(len(entries) for entries in sources_data.values()),
        "fixtures_compared": fixtures_total,
        "fixtures_diff_critical": fixtures_fail,
        "sources_without_goldens": [src for src, entries in sources_data.items() if not entries]
    },
    "artifacts": [
        {"path": "goldens/sprint_4/fontes_p0"},
        {"path": os.path.relpath(report_path, root)},
        {"path": os.path.relpath(diff_path, root)}
    ],
    "errors": []
}
(root / "out" / "scorecards" / "S4_T4_goldens.json").write_text(json.dumps(scorecard, indent=2, ensure_ascii=False))
if status_flag != "PASS":
    raise SystemExit(1)
PY
rm -rf "$TMP_RESULTS"
