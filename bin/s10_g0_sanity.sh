#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S10_G0"
SCORECARD="$SCORECARD_DIR/S10_G0_sanity.json"
REPORT_FILE="$EVIDENCE_DIR/sanity_report.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
git_commit="$(git -C "$ROOT_DIR" rev-parse HEAD 2>/dev/null || echo "unknown")"
current_branch="$(git -C "$ROOT_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")"
ci_head_ref="${GITHUB_HEAD_REF:-}"
ci_env="${GITHUB_ACTIONS:-${CI:-}}"

if [[ -n "$ci_head_ref" ]]; then
  effective_branch="$ci_head_ref"
elif [[ "$current_branch" != "HEAD" ]]; then
  effective_branch="$current_branch"
else
  effective_branch="$current_branch"
fi

overall_status="PASS"
declare -a CHECK_LINES=()

add_check() {
  local id="$1"
  local description="$2"
  local status="$3"
  local details="$4"
  CHECK_LINES+=("${id}|${description}|${status}|${details}")
  if [[ "$status" != "PASS" ]]; then
    overall_status="FAIL"
  fi
}

# 1) Git repo sanity
if git -C "$ROOT_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  add_check "git-worktree" "Repositório git detectado" "PASS" ""
else
  add_check "git-worktree" "Repositório git detectado" "FAIL" "Não está em um repo git"
fi

# 2) Remote origin check
origin_url="$(git -C "$ROOT_DIR" remote get-url origin 2>/dev/null || echo "")"
if [[ -n "$origin_url" && "$origin_url" == *"Inspectah"* ]]; then
  add_check "git-origin" "Remote origin aponta para Inspectah" "PASS" "$origin_url"
else
  add_check "git-origin" "Remote origin aponta para Inspectah" "FAIL" "${origin_url:-indefinido}"
fi

# 3) Branch naming
if [[ "$effective_branch" == q2-s10-* || "$effective_branch" == "main" ]]; then
  add_check "git-branch" "Branch segue padrão da S10" "PASS" "$effective_branch"
elif [[ "$effective_branch" == "HEAD" && -n "$ci_env" ]]; then
  add_check "git-branch" "Branch segue padrão da S10" "PASS" "CI head: $effective_branch"
else
  add_check "git-branch" "Branch segue padrão da S10" "FAIL" "$effective_branch"
fi

# 4) Docs obrigatórios
doc_status="PASS"
missing_docs=()
for doc in \
  docs/sprint_10_cap_1_visao_truthdb_guardiao.md \
  docs/sprint_10_cap_2_gates_truthdb_guardiao.md \
  docs/sprint_10_cap_3_arquitetura_filemap_truthdb_guardiao.md \
  docs/sprint_10_cap_4_execucao_codex_guardiao_de_blocos.md; do
  if [[ ! -f "$ROOT_DIR/$doc" ]]; then
    missing_docs+=("$doc")
    doc_status="FAIL"
  fi
done
if [[ "$doc_status" == "PASS" ]]; then
  add_check "docs" "Documentos oficiais da S10 presentes" "PASS" ""
else
  add_check "docs" "Documentos oficiais da S10 presentes" "FAIL" "Ausentes: ${missing_docs[*]}"
fi

# 5) Estrutura Truth-DB básica
required_files=(
  inspectah/truthdb/models.py
  inspectah/truthdb/state_machine.py
  inspectah/truthdb/actions_contract.py
  inspectah/truthdb/engine.py
  inspectah/pipelines/s10_domain_a_obras.py
  inspectah/pipelines/s10_domain_b_precos.py
  inspectah/truthdb/exports.py
)
files_status="PASS"
missing_files=()
for file in "${required_files[@]}"; do
  if [[ ! -f "$ROOT_DIR/$file" ]]; then
    missing_files+=("$file")
    files_status="FAIL"
  fi
done
add_check "structure" "Estrutura central da S10 presente" "$files_status" "${missing_files[*]}"

# 6) Estrutura de saída
mkdir -p "$ROOT_DIR/out/scorecards" "$ROOT_DIR/out/evidence"
if [[ -d "$ROOT_DIR/out/scorecards" && -d "$ROOT_DIR/out/evidence" ]]; then
  add_check "out-structure" "Estrutura out/scorecards e out/evidence existe" "PASS" ""
else
  add_check "out-structure" "Estrutura out/scorecards e out/evidence existe" "FAIL" ""
fi

# G0 não aceita WARN: overall_status já reflete qualquer falha.

printf '%s\n' "${CHECK_LINES[@]}" > "$EVIDENCE_DIR/checks.lst"

python3 - <<'PY' "$EVIDENCE_DIR/checks.lst" "$REPORT_FILE"
import json
import sys
from pathlib import Path

checks_path = Path(sys.argv[1])
report_path = Path(sys.argv[2])
checks = []
if checks_path.exists():
    for line in checks_path.read_text().splitlines():
        if not line:
            continue
        cid, description, status, details = line.split("|", 3)
        checks.append(
            {"id": cid, "description": description, "status": status, "details": details}
        )
report_path.write_text(json.dumps({"checks": checks}, indent=2), encoding="utf-8")
PY

python3 - <<'PY' "$REPORT_FILE" "$SCORECARD" "$overall_status" "$ts" "$git_commit" "$effective_branch"
import json
import sys
from pathlib import Path
report_path, scorecard_path, status, ts, commit, branch = sys.argv[1:]
report = json.loads(Path(report_path).read_text())
scorecard = {
    "gate_id": "S10_G0",
    "name": "Sprint 10 sanity gate",
    "status": status,
    "checks": report["checks"],
    "meta": {"ts": ts, "git_commit": commit, "branch": branch},
}
Path(scorecard_path).write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
PY

if [[ "$overall_status" == "FAIL" ]]; then
  exit 1
fi
exit 0
