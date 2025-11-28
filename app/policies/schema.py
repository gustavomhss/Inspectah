from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

import yaml

from .models import PromotionPolicyConfig


class InvalidPolicyError(ValueError):
    pass


REQUIRED_FIELDS = {"name", "domain", "min_confidence", "min_sources"}


def _validate_payload(data: dict) -> PromotionPolicyConfig:
    missing = REQUIRED_FIELDS - data.keys()
    if missing:
        raise InvalidPolicyError(f"Campos obrigatórios faltando: {sorted(missing)}")
    name = str(data["name"]).strip()
    domain = str(data["domain"]).strip()
    min_confidence = float(data["min_confidence"])
    min_sources = int(data["min_sources"])
    require_debunk = bool(data.get("require_debunk", False))
    require_human = bool(data.get("require_human", False))
    sensitive = bool(data.get("sensitive", False))
    default_decision = str(data.get("default_decision", "HOLD")).upper()
    if default_decision not in {"PROMOTE", "HOLD", "BLOCK"}:
        raise InvalidPolicyError(f"default_decision inválido: {default_decision}")
    return PromotionPolicyConfig(
        name=name,
        domain=domain,
        min_confidence=min_confidence,
        min_sources=min_sources,
        require_debunk=require_debunk,
        require_human=require_human,
        sensitive=sensitive,
        default_decision=default_decision,
        metadata=data.get("metadata") or {},
    )


def load_policy_file(path: Path) -> PromotionPolicyConfig:
    if not path.exists():
        raise InvalidPolicyError(f"Arquivo de policy não encontrado: {path}")
    raw = path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw) if path.suffix in {".yaml", ".yml"} else json.loads(raw)
    if not isinstance(data, dict):
        raise InvalidPolicyError(f"Policy deve ser um objeto no arquivo: {path}")
    return _validate_payload(data)


def load_policies_from_dir(base_dir: Path) -> Dict[str, PromotionPolicyConfig]:
    if not base_dir.exists():
        raise InvalidPolicyError(f"Diretório de policies não encontrado: {base_dir}")
    policies: Dict[str, PromotionPolicyConfig] = {}
    for path in sorted(base_dir.iterdir()):
        if path.suffix.lower() not in {".yaml", ".yml", ".json"} or not path.is_file():
            continue
        config = load_policy_file(path)
        policies[config.domain] = config
    if not policies:
        raise InvalidPolicyError("Nenhuma policy válida encontrada.")
    return policies


def main() -> int:
    base = Path("configs/promotion_policies")
    try:
        load_policies_from_dir(base)
    except InvalidPolicyError as exc:  # pragma: no cover - CLI path
        print(f"[policy schema] inválido: {exc}")
        return 1
    print("[policy schema] ok")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
