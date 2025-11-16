#!/usr/bin/env python3
"""
Audits Sprint 5 artifacts still living under Sprint 5/ and promotes them into
the repository root layout. Produces a JSON summary with everything that was
promoted, conflicted, or skipped.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


ROOT = Path(__file__).resolve().parents[1]
S5_ROOT = ROOT / "Sprint 5"

AUDIT_OUT = ROOT / "out" / "s5_gates" / "S5_layout_audit"
IGNORED_SUFFIXES = {".pyc"}
IGNORED_NAMES = {".DS_Store"}


def category_template() -> Dict[str, List[str]]:
    return {
        "promoted": [],
        "conflicts": [],
        "skipped_equal": [],
        "warnings": [],
        "found": [],
        "missing": [],
    }


def file_should_be_processed(path: Path) -> bool:
    return path.suffix not in IGNORED_SUFFIXES and path.name not in IGNORED_NAMES


class Auditor:
    def __init__(self, dry_run: bool) -> None:
        self.dry_run = dry_run
        self.log_events: List[str] = []
        self.report: Dict[str, object] = {
            "status": "OK",
            "dry_run": dry_run,
            "categories": {},
            "sprint5_remaining_technical_paths": [],
            "log": self.log_events,
        }

    def log(self, message: str) -> None:
        print(message)
        self.log_events.append(message)

    def cat(self, name: str) -> Dict[str, List[str]]:
        categories = self.report["categories"]  # type: ignore[assignment]
        if name not in categories:
            categories[name] = category_template()  # type: ignore[index]
        return categories[name]  # type: ignore[return-value]

    def same_content(self, src: Path, dest: Path) -> bool:
        if not dest.exists() or not dest.is_file():
            return False
        if src.stat().st_size != dest.stat().st_size:
            return False
        return self._hash(src) == self._hash(dest)

    @staticmethod
    def _hash(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def make_backup(self, dest: Path) -> Path:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        if dest.suffix:
            backup = dest.with_suffix(dest.suffix + f".pre_s5_backup_{timestamp}")
        else:
            backup = dest.with_name(dest.name + f".pre_s5_backup_{timestamp}")
        if self.dry_run:
            self.log(f"[DRY-RUN] Backup would be: {dest} -> {backup}")
        else:
            dest.rename(backup)
        return backup

    def promote_file(self, src: Path, dest: Path, *, category: str) -> None:
        cat = self.cat(category)
        rel_src = src.relative_to(ROOT)
        rel_dest = dest.relative_to(ROOT)

        if not dest.exists():
            if not self.dry_run:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dest))
            else:
                self.log(f"[DRY-RUN] Would move {rel_src} -> {rel_dest}")
            cat["promoted"].append(f"{rel_src} -> {rel_dest}")
            self.log(f"PROMOTE [{category}]: {rel_src} -> {rel_dest}")
            return

        if self.same_content(src, dest):
            cat["skipped_equal"].append(f"{rel_src} == {rel_dest}")
            self.log(f"SKIP_EQUAL [{category}]: {rel_src} == {rel_dest}")
            return

        backup = self.make_backup(dest)
        if not self.dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dest))
        else:
            self.log(f"[DRY-RUN] Would move {rel_src} -> {rel_dest} (after backup)")
        cat["conflicts"].append(
            f"{rel_src} -> {rel_dest} (backup={backup.relative_to(ROOT)})"
        )
        self.log(
            f"CONFLICT [{category}]: {rel_src} -> {rel_dest} (backup={backup.relative_to(ROOT)})"
        )

    def ensure_executable(self, path: Path, category: str) -> None:
        if not path.exists() or path.suffix != ".sh":
            return
        mode = path.stat().st_mode
        if mode & 0o111:
            return
        new_mode = mode | 0o111
        if self.dry_run:
            self.log(f"[DRY-RUN] Would chmod +x {path.relative_to(ROOT)}")
        else:
            path.chmod(new_mode)
        self.log(f"CHMOD [{category}]: {path.relative_to(ROOT)} set to executable")


def audit_inspectah(auditor: Auditor) -> None:
    category = "inspectah"
    auditor.cat(category)
    s5_inspectah = S5_ROOT / "inspectah"
    dest_root = ROOT / "inspectah"
    if not s5_inspectah.exists():
        auditor.log("Sprint 5/inspectah não encontrado, nada para promover.")
        return
    dest_root.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in s5_inspectah.rglob("*") if p.is_file())
    for file in files:
        if not file_should_be_processed(file):
            continue
        relative = file.relative_to(s5_inspectah)
        dest = dest_root / relative
        auditor.promote_file(file, dest, category=category)


def audit_schemas(auditor: Auditor) -> None:
    category = "schemas"
    cat = auditor.cat(category)
    s5_schemas = S5_ROOT / "schemas"
    dest_root = ROOT / "schemas"
    dest_root.mkdir(parents=True, exist_ok=True)
    if s5_schemas.exists():
        for file in sorted(p for p in s5_schemas.rglob("*") if p.is_file()):
            if not file_should_be_processed(file):
                continue
            relative = file.relative_to(s5_schemas)
            dest = dest_root / relative
            auditor.promote_file(file, dest, category=category)
    required = [
        "inspectah_item_v0_1.json",
        "inspectah_claim_v0_1.json",
    ]
    for name in required:
        path = dest_root / name
        if not path.exists():
            msg = f"Schema ausente: {path.relative_to(ROOT)}"
            auditor.log(msg)
            cat["warnings"].append(msg)


def audit_fixtures(auditor: Auditor) -> None:
    category = "fixtures"
    cat = auditor.cat(category)
    s5_fixtures = S5_ROOT / "fixtures" / "s5"
    dest_root = ROOT / "fixtures" / "s5"
    if s5_fixtures.exists():
        for file in sorted(p for p in s5_fixtures.rglob("*") if p.is_file()):
            if not file_should_be_processed(file):
                continue
            relative = file.relative_to(s5_fixtures)
            dest = dest_root / relative
            auditor.promote_file(file, dest, category=category)
    required = [
        "rss_feed.xml",
        "api_feed.json",
        "html_page.html",
    ]
    for name in required:
        path = dest_root / name
        if not path.exists():
            msg = f"Fixture ausente: {path.relative_to(ROOT)}"
            auditor.log(msg)
            cat["warnings"].append(msg)


def audit_tests(auditor: Auditor) -> None:
    category = "tests"
    cat = auditor.cat(category)
    s5_tests = S5_ROOT / "tests"
    dest_root = ROOT / "tests"
    if s5_tests.exists():
        for file in sorted(p for p in s5_tests.rglob("*") if p.is_file()):
            if not file_should_be_processed(file):
                continue
            relative = file.relative_to(s5_tests)
            dest = dest_root / relative
            auditor.promote_file(file, dest, category=category)
    required = [
        "test_schema_item.py",
        "test_schema_claim.py",
        "test_equivalence_key.py",
        "components/test_watchers_engine.py",
        "components/test_evidence_builder.py",
        "components/test_evidence_verifier.py",
        "components/test_normalizer_stub.py",
        "components/test_normalizer_ai_mode.py",
        "components/test_indexer.py",
        "components/test_query_api.py",
        "pipeline/test_pipeline_fixtures.py",
        "golden/s5_pipeline/expected_items_summary.json",
    ]
    for rel in required:
        path = dest_root / rel
        if not path.exists():
            msg = f"Teste ausente: {path.relative_to(ROOT)}"
            auditor.log(msg)
            cat["warnings"].append(msg)


def audit_bin(auditor: Auditor) -> None:
    category = "bin"
    cat = auditor.cat(category)
    s5_bin = S5_ROOT / "bin"
    dest_root = ROOT / "bin"
    required = [
        "s5_gate_g0_spec_lock.sh",
        "s5_gate_g1_schema_contracts.sh",
        "s5_gate_g2_components.sh",
        "s5_gate_g3_pipeline_fixtures.sh",
        "s5_gate_g4_ai_integration.sh",
        "s5_gate_g5_operator_journey.sh",
        "s5_pytest_shim.py",
        "s5_check_invariants.sh",
    ]
    if s5_bin.exists():
        for file in sorted(p for p in s5_bin.iterdir()):
            if not file.is_file() or not file_should_be_processed(file):
                continue
            if not file.name.startswith("s5_") and "s5_gate" not in file.name:
                continue
            dest = dest_root / file.name
            auditor.promote_file(file, dest, category=category)
    for rel in required:
        path = dest_root / rel
        if not path.exists():
            msg = f"Script binário ausente: {path.relative_to(ROOT)}"
            auditor.log(msg)
            cat["warnings"].append(msg)
        else:
            auditor.ensure_executable(path, category)


def audit_scripts(auditor: Auditor) -> None:
    category = "scripts"
    cat = auditor.cat(category)
    s5_scripts = S5_ROOT / "scripts"
    dest_root = ROOT / "scripts"
    if s5_scripts.exists():
        for file in sorted(p for p in s5_scripts.iterdir()):
            if not file.is_file() or not file_should_be_processed(file):
                continue
            if not file.name.startswith("s5_"):
                continue
            dest = dest_root / file.name
            auditor.promote_file(file, dest, category=category)
    required = [
        "s5_invariants_pipeline.py",
        "s5_ai_smoke_gpt4mini.py",
    ]
    for rel in required:
        path = dest_root / rel
        if not path.exists():
            msg = f"Script auxiliar ausente: {path.relative_to(ROOT)}"
            auditor.log(msg)
            cat["warnings"].append(msg)


def audit_docs(auditor: Auditor) -> None:
    category = "docs"
    cat = auditor.cat(category)
    chapters = [
        "s_5_capitulo_1_v_6_inspectah_data_hub_core.md",
        "s_5_capitulo_2_v_2_inspectah_gates.md",
        "s_5_capitulo_3_v_2_inspectah_filemap_e_plano.md",
        "s_5_capitulo_4_v_2_inspectah_guia_execucao_codex.md",
    ]
    for chapter in chapters:
        path = S5_ROOT / chapter
        if path.exists():
            cat["found"].append(str(path.relative_to(ROOT)))
        else:
            msg = f"Capítulo ausente: {path.relative_to(ROOT)}"
            auditor.log(msg)
            cat["warnings"].append(msg)

    s5_docs = S5_ROOT / "docs" / "sprint_5"
    dest_root = ROOT / "docs" / "sprint_5"
    expected_docs = set(
        [
            "s5_capitulo_1_core_v6.md",
            "s5_capitulo_2_gates_v2.md",
            "s5_capitulo_3_filemap_plano_v2.md",
            "s5_capitulo_4_execucao_codex_v2.md",
            "gates/G0_spec_lock_checklist.md",
            "gates/G1_schema_contracts_checklist.md",
            "gates/G2_components_checklist.md",
            "gates/G3_pipeline_fixtures_checklist.md",
            "gates/G4_ai_integration_checklist.md",
            "gates/G5_operator_journey_checklist.md",
            "gates/G5_operator_scenario.md",
        ]
    )

    for gate_script in ROOT.glob("bin/s5_gate_*.sh"):
        try:
            contents = gate_script.read_text(encoding="utf-8")
        except Exception:
            continue
        for marker in contents.split():
            if "docs/sprint_5/" in marker:
                rel_part = marker.split("docs/sprint_5/", 1)[1]
                rel_part = rel_part.strip("\"' ")
                rel_part = rel_part.split("$", 1)[0]
                rel_part = rel_part.split(")", 1)[0]
                rel_part = rel_part.strip()
                if rel_part:
                    expected_docs.add(rel_part)

    if s5_docs.exists():
        for file in sorted(p for p in s5_docs.rglob("*") if p.is_file()):
            if not file_should_be_processed(file):
                continue
            relative = file.relative_to(s5_docs)
            dest = dest_root / relative
            auditor.promote_file(file, dest, category=category)

    for rel in sorted(expected_docs):
        path = dest_root / rel
        if not path.exists():
            msg = f"Documento operacional ausente: {path.relative_to(ROOT)}"
            auditor.log(msg)
            cat["warnings"].append(msg)


def audit_out(auditor: Auditor) -> None:
    category = "out_s5_gates"
    auditor.cat(category)
    s5_out = S5_ROOT / "out" / "s5_gates"
    dest_root = ROOT / "out" / "s5_gates"
    if not s5_out.exists():
        auditor.log("Sprint 5/out/s5_gates não encontrado, nada para promover.")
        return
    for file in sorted(p for p in s5_out.rglob("*") if p.is_file()):
        if not file_should_be_processed(file):
            continue
        relative = file.relative_to(s5_out)
        dest = dest_root / relative
        auditor.promote_file(file, dest, category=category)


def collect_remaining_paths(auditor: Auditor) -> None:
    allowed_files = {
        "s_5_capitulo_1_v_6_inspectah_data_hub_core.md",
        "s_5_capitulo_2_v_2_inspectah_gates.md",
        "s_5_capitulo_3_v_2_inspectah_filemap_e_plano.md",
        "s_5_capitulo_4_v_2_inspectah_guia_execucao_codex.md",
        "README.md",
    }
    remaining: List[str] = []
    for path in sorted(S5_ROOT.iterdir()):
        if path.name in allowed_files:
            continue
        remaining.append(str(path.relative_to(ROOT)))
    auditor.report["sprint5_remaining_technical_paths"] = remaining
    if remaining:
        warning = (
            "WARNING: diretórios/arquivos técnicos ainda existem dentro de Sprint 5/. "
            "Revise manualmente."
        )
        auditor.log(warning)
        auditor.cat("docs")["warnings"].append(warning)


def update_status(auditor: Auditor) -> None:
    if auditor.report.get("status") == "WARN":
        return
    for cat in auditor.report["categories"].values():  # type: ignore[assignment]
        if cat["warnings"]:
            auditor.report["status"] = "WARN"
            return


def write_summary(auditor: Auditor) -> None:
    AUDIT_OUT.mkdir(parents=True, exist_ok=True)
    summary_path = AUDIT_OUT / "summary.json"
    data = auditor.report
    summary_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    auditor.log(f"Resumo salvo em {summary_path.relative_to(ROOT)}")


def print_human_summary(auditor: Auditor) -> None:
    promoted = sum(len(cat["promoted"]) for cat in auditor.report["categories"].values())  # type: ignore[index]
    conflicts = sum(len(cat["conflicts"]) for cat in auditor.report["categories"].values())  # type: ignore[index]
    skipped = sum(len(cat["skipped_equal"]) for cat in auditor.report["categories"].values())  # type: ignore[index]
    remaining = auditor.report["sprint5_remaining_technical_paths"]
    auditor.log("----- S5 Layout Audit Summary -----")
    auditor.log(f"Total promoted: {promoted}")
    auditor.log(f"Total conflicts (with backup): {conflicts}")
    auditor.log(f"Total skipped (already equal): {skipped}")
    auditor.log(f"Remaining technical paths in Sprint 5/: {len(remaining)}")
    if remaining:
        for item in remaining:
            auditor.log(f"  - {item}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Sprint 5 layout auditor")
    parser.add_argument("--dry-run", action="store_true", help="log actions without moving files")
    args = parser.parse_args()
    if not S5_ROOT.exists():
        print("Sprint 5 não encontrada, nada para auditar.")
        return 0

    auditor = Auditor(dry_run=args.dry_run)
    audit_inspectah(auditor)
    audit_schemas(auditor)
    audit_fixtures(auditor)
    audit_tests(auditor)
    audit_bin(auditor)
    audit_scripts(auditor)
    audit_docs(auditor)
    audit_out(auditor)
    collect_remaining_paths(auditor)
    update_status(auditor)
    write_summary(auditor)
    print_human_summary(auditor)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
