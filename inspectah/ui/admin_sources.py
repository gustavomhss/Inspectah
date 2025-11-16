"""Interface administrativa em terminal para CRUD de fontes."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
SUPPORTED_TYPES = {"rss", "api"}


def load_registry(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"sources": []}
    data = path.read_text(encoding="utf-8")
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        if yaml is None:
            raise
        return yaml.safe_load(data)


def save_registry(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _render_source(source: Dict[str, Any]) -> str:
    template = (TEMPLATES_DIR / "admin_source_detail.txt").read_text(encoding="utf-8")
    fixture = source.get("parse_spec", {}).get("fixture", "")
    return template.format(
        id=source.get("id"),
        type=source.get("type"),
        url=source.get("url"),
        frequency=source.get("frequency"),
        timeout=source.get("timeout"),
        enabled=source.get("enabled"),
        fixture=fixture,
    )


def _print_header() -> None:
    header = (TEMPLATES_DIR / "admin_sources_header.txt").read_text(encoding="utf-8")
    print(header)


def _select_source(sources: List[Dict[str, Any]]) -> Dict[str, Any] | None:
    if not sources:
        print("Não há fontes cadastradas.")
        return None
    for idx, source in enumerate(sources, start=1):
        status = "ON" if source.get("enabled") else "OFF"
        print(f"{idx}. {source.get('id')} [{status}]")
    choice = input("Selecione o número da fonte (ou pressione Enter para cancelar): ")
    if not choice.strip():
        return None
    try:
        index = int(choice) - 1
        return sources[index]
    except (ValueError, IndexError):
        print("Seleção inválida.")
        return None


def _prompt(text: str, default: str | None = None) -> str:
    if default is not None:
        prompt_text = f"{text} [{default}]: "
    else:
        prompt_text = f"{text}: "
    value = input(prompt_text).strip()
    return value or (default or "")


def _edit_source(source: Dict[str, Any]) -> None:
    source["url"] = _prompt("URL", source.get("url", ""))
    source["frequency"] = _prompt("Frequency (ex.: PT1H)", source.get("frequency", "PT1H"))
    source["timeout"] = int(_prompt("Timeout (s)", str(source.get("timeout", 5)) or "5"))
    parse_spec = source.setdefault("parse_spec", {})
    parse_spec["fixture"] = _prompt("Fixture", parse_spec.get("fixture", ""))


def run_admin_ui(registry_path: str | Path = "inspectah/config/sources_registry.yaml") -> None:
    path = Path(registry_path)
    registry = load_registry(path)
    registry.setdefault("sources", [])

    while True:
        _print_header()
        print("1. Listar fontes")
        print("2. Cadastrar nova fonte")
        print("3. Editar fonte")
        print("4. Ativar/Desativar fonte")
        print("5. Salvar e sair")
        option = input("Escolha uma opção: ").strip()

        if option == "1":
            for source in registry["sources"]:
                print(_render_source(source))
            input("Pressione Enter para continuar...")
        elif option == "2":
            new_source = {
                "id": _prompt("ID"),
                "type": _prompt("Tipo (rss/api)", "rss").lower(),
                "url": _prompt("URL"),
                "frequency": _prompt("Frequency", "PT1H"),
                "timeout": int(_prompt("Timeout (s)", "5")),
                "parse_spec": {"fixture": _prompt("Fixture", "")},
                "enabled": True,
            }
            if new_source["type"] not in SUPPORTED_TYPES:
                print("Tipo inválido. Somente rss ou api.")
            else:
                registry["sources"].append(new_source)
        elif option == "3":
            target = _select_source(registry["sources"])
            if target:
                _edit_source(target)
        elif option == "4":
            target = _select_source(registry["sources"])
            if target:
                target["enabled"] = not target.get("enabled", False)
                status = "ON" if target["enabled"] else "OFF"
                print(f"Fonte {target.get('id')} agora está {status}.")
        elif option == "5":
            save_registry(path, registry)
            print(f"Registry salvo em {path}.")
            break
        else:
            print("Opção inválida.")
