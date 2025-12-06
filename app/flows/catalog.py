from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict, List, Optional


def _load_yaml(path: Path) -> Dict:
    text = path.read_text()
    try:
        import yaml  # type: ignore
    except Exception:
        data: Dict[str, object] = {}
        for line in text.splitlines():
            raw = line.strip()
            if not raw or raw.startswith("#") or ":" not in raw:
                continue
            k, v = raw.split(":", 1)
            data[k.strip()] = v.strip()
        return data
    return yaml.safe_load(text) or {}


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_catalog_entries(base_dir: Path | str = Path("config/flow_catalog")) -> List[Dict]:
    base = Path(base_dir)
    if not base.exists():
        return []
    entries: List[Dict] = []
    for file in sorted(base.glob("*.yaml")):
        text = file.read_text()
        payload = _load_yaml(file)
        payload.setdefault("hash", payload.get("hash") or _hash_text(text))
        payload.setdefault("signature", payload.get("signature") or "unknown")
        payload.setdefault("template_ref", payload.get("template_ref") or f"config/flow_templates/{file.stem}.yaml")
        entries.append(payload)
    return entries


def catalog_index_by_template(base_dir: Path | str = Path("config/flow_catalog")) -> Dict[str, Dict]:
    index: Dict[str, Dict] = {}
    for entry in load_catalog_entries(base_dir):
        template_ref = str(entry.get("template_ref") or "")
        index[template_ref] = entry
    return index


def entry_for_template(template_slug: str, base_dir: Path | str = Path("config/flow_catalog")) -> Optional[Dict]:
    ref = f"config/flow_templates/{template_slug}.yaml"
    return catalog_index_by_template(base_dir).get(ref)
