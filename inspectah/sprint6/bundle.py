from __future__ import annotations

import hashlib
import shutil
import tarfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List

from .config import REPO_ROOT, load_domain_config


BUNDLE_ROOT = REPO_ROOT / "out" / "s6_bundle"


def build_bundle(domain: str = "dominio_piloto") -> Dict[str, str]:
    cfg = load_domain_config(domain)
    payload_dir = BUNDLE_ROOT / "payload"
    if payload_dir.exists():
        shutil.rmtree(payload_dir)
    payload_dir.mkdir(parents=True, exist_ok=True)

    included: List[str] = []
    included += _copy_tree_if_exists(Path("docs/sprint_6"), payload_dir / "docs/sprint_6")
    included += _copy_paths(["config/fields/dominio_piloto.yaml"], payload_dir)
    included += _copy_paths(sorted(str(path) for path in Path("config/sources").glob("fonte_*.yaml")), payload_dir)
    included += _copy_if_exists(cfg.canonical_records_path, payload_dir / f"out/{domain}")
    included += _copy_if_exists(cfg.summary_path, payload_dir / f"out/{domain}")
    included += _copy_tree_if_exists(cfg.evidence_root, payload_dir / f"out/evidence/{domain}")
    included += _copy_tree_if_exists(Path("out/queries"), payload_dir / "out/queries")
    included += _copy_tree_if_exists(Path("out/scorecards"), payload_dir / "out/scorecards")

    readme_text = _bundle_readme(domain, included)
    (payload_dir / "README.md").write_text(readme_text, encoding="utf-8")

    tar_path = BUNDLE_ROOT / "inspectah_s6_bundle.tar.gz"
    BUNDLE_ROOT.mkdir(parents=True, exist_ok=True)
    with tarfile.open(tar_path, "w:gz") as tar:
        for item in payload_dir.rglob("*"):
            tar.add(item, arcname=item.relative_to(payload_dir))

    checksums_path = BUNDLE_ROOT / "SHA256SUMS"
    checksums_path.write_text(
        "\n".join(
            [
                f"{_sha256_file(tar_path)}  inspectah_s6_bundle.tar.gz",
                f"{hashlib.sha256(readme_text.encode('utf-8')).hexdigest()}  README.md",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (BUNDLE_ROOT / "README.md").write_text(readme_text, encoding="utf-8")
    return {"tar_path": str(tar_path), "checksums": str(checksums_path), "readme": str(BUNDLE_ROOT / "README.md")}


def verify_bundle() -> Dict[str, bool]:
    tar_path = BUNDLE_ROOT / "inspectah_s6_bundle.tar.gz"
    checksum_path = BUNDLE_ROOT / "SHA256SUMS"
    readme_path = BUNDLE_ROOT / "README.md"
    if not tar_path.exists() or not checksum_path.exists() or not readme_path.exists():
        raise FileNotFoundError("bundle artifacts missing")
    expected = _parse_checksums(checksum_path)
    tar_ok = _sha256_file(tar_path) == expected.get("inspectah_s6_bundle.tar.gz")
    readme_ok = _sha256_file(readme_path) == expected.get("README.md")
    if not tar_ok or not readme_ok:
        raise ValueError("bundle checksum mismatch")
    with tarfile.open(tar_path, "r:gz") as tar:
        members = {Path(member) for member in tar.getnames()}
        required = {Path("docs/sprint_6/sprint_6_capitulo_1.md"), Path("config/fields/dominio_piloto.yaml")}
        if not required.issubset(members):
            raise ValueError("bundle missing required files")
    return {"tar": tar_ok, "readme": readme_ok}


def _copy_paths(paths: Iterable[str], target_root: Path) -> List[str]:
    copied: List[str] = []
    for path_str in paths:
        if not path_str:
            continue
        src = Path(path_str)
        if not src.exists():
            continue
        dst = target_root / src
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append(str(dst.relative_to(target_root)))
    return copied


def _copy_if_exists(src: Path, dst_dir: Path) -> List[str]:
    if not src.exists():
        return []
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / src.name
    shutil.copy2(src, dst)
    return [str(dst.relative_to(BUNDLE_ROOT / "payload"))]


def _copy_tree_if_exists(src: Path, dst: Path) -> List[str]:
    if not src.exists():
        return []
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    return [str(dst.relative_to(BUNDLE_ROOT / "payload"))]


def _bundle_readme(domain: str, included: List[str]) -> str:
    lines = [
        "# Inspectah Sprint 6 Bundle",
        "",
        f"- Domínio: {domain}",
        f"- Gerado em: {datetime.utcnow().isoformat()}Z",
        "",
        "## Conteúdo",
        "- Configurações de fontes e campos",
        "- Dados canônicos e evidências",
        "- Scorecards e consultas",
        "",
        "## Como verificar",
        "1. validar SHA256SUMS;",
        "2. extrair o tarball;",
        "3. rodar bin/inspectah_s6_verify_bundle.sh.",
        "",
        "## Arquivos inclusos",
    ]
    lines.extend(f"- {entry}" for entry in sorted(set(included)))
    return "\n".join(lines) + "\n"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_checksums(path: Path) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) == 2:
            mapping[parts[1]] = parts[0]
    return mapping
