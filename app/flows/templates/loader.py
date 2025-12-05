from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

PRIMARY_TEMPLATE_DIR = Path("config/flow_templates")
FALLBACK_TEMPLATE_DIR = Path("out/flow_templates")
TEMPLATE_DIR = PRIMARY_TEMPLATE_DIR


def _load_yaml(path: Path) -> Dict:
    try:
        import yaml  # type: ignore
    except ModuleNotFoundError as exc:  # pragma: no cover - ambiente sem PyYAML
        # fallback: tenta interpretar como JSON (válido em YAML)
        try:
            return json.loads(path.read_text())
        except Exception as json_exc:
            raise RuntimeError("PyYAML não instalado e não foi possível ler template como JSON.") from json_exc
    return yaml.safe_load(path.read_text()) or {}


def load_templates_from_dir(base_dir: Optional[Path] = None) -> List[Dict]:
    if base_dir:
        bases = [base_dir]
    else:
        bases = [PRIMARY_TEMPLATE_DIR, FALLBACK_TEMPLATE_DIR]
    templates: List[Dict] = []
    if not any(base.exists() for base in bases):
        return templates
    for base in bases:
        if not base.exists():
            continue
        for path in sorted(base.glob("*.yaml")):
            data = _load_yaml(path)
            # Normaliza ID faltante ou nulo para evitar falha de validação
            if not data.get("id"):
                data["id"] = f"tpl_{data.get('slug') or path.stem}"
            data["__file__"] = str(path)
            templates.append(data)
    return templates


def validate_template(payload: Dict, path: Path) -> None:
    required = ["id", "slug", "version", "domain", "entry_type", "steps"]
    missing = [k for k in required if k not in payload]
    if missing:
        raise ValueError(f"Template {path} faltando campos: {missing}")
    steps = payload.get("steps") or []
    if not isinstance(steps, list) or len(steps) == 0:
        raise ValueError(f"Template {path} sem steps válidos")


def sync_templates_to_db(conn, templates: List[Dict]) -> None:
    for tpl in templates:
        path = Path(tpl.get("__file__") or "desconhecido")
        validate_template(tpl, path)
        payload = {
            "id": tpl["id"],
            "slug": tpl["slug"],
            "versao": str(tpl["version"]),
            "tipo_entrada": tpl["entry_type"],
            "estrutura": json.dumps(tpl, ensure_ascii=False),
            "metadata": json.dumps({"domain": tpl.get("domain")}, ensure_ascii=False),
        }
        conn.execute(
            """
            INSERT INTO flow_flow_templates (id, slug, versao, tipo_entrada, estrutura, ativo, metadata, created_at, updated_at)
            VALUES (:id, :slug, :versao, :tipo_entrada, :estrutura, 1, :metadata, datetime('now'), datetime('now'))
            ON CONFLICT(slug) DO UPDATE SET
                versao=excluded.versao,
                estrutura=excluded.estrutura,
                metadata=excluded.metadata,
                updated_at=datetime('now');
            """,
            payload,
        )
