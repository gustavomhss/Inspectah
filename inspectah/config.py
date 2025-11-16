from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Any, Dict

try:  # pragma: no cover - optional dependency
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    yaml = None

from .evidence_vault.settings import EvidenceStoreConfig

BASE_DIR = Path(os.environ.get("INSPECTAH_BASE_DIR", Path.cwd()))
DB_PATH = Path(os.environ.get("INSPECTAH_DB_PATH", BASE_DIR / "inspectah.db"))
REGISTRY_DIR = Path(os.environ.get("INSPECTAH_REGISTRY_DIR", BASE_DIR / "registry"))
FIELDS_DIR = REGISTRY_DIR / "fields"
SOURCES_DIR = REGISTRY_DIR / "sources"
EVIDENCE_DIR = Path(os.environ.get("INSPECTAH_EVIDENCE_DIR", BASE_DIR / "data" / "evidence"))
METRICS_NAMESPACE = "inspectah"
CONFIGS_DIR = Path(os.environ.get("INSPECTAH_CONFIGS_DIR", BASE_DIR / "configs"))

EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
CONFIGS_DIR.mkdir(parents=True, exist_ok=True)


def _load_yaml_config(filename: str) -> Dict[str, Any]:
    path = CONFIGS_DIR / filename
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return {}
    if yaml is not None:
        data = yaml.safe_load(text) or {}
    else:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError(f"Configuration file {filename} must contain a mapping.")
    return data


def _resolve_local_root(value: str | Path | None) -> Path:
    if value is None:
        return BASE_DIR / "data" / "vault_objects"
    path = Path(value)
    if not path.is_absolute():
        path = BASE_DIR / path
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_evidence_vault_settings() -> EvidenceStoreConfig:
    raw = _load_yaml_config("evidence_vault.yml")
    vault_section = raw.get("vault", {})
    bucket = os.environ.get("INSPECTAH_VAULT_BUCKET") or vault_section.get("bucket") or "inspectah-evidence-dev"
    region = os.environ.get("INSPECTAH_VAULT_REGION") or vault_section.get("region") or "sa-east-1"
    if region != "sa-east-1":
        raise ValueError("Evidence Vault region must be sa-east-1 per D9.4.")
    kms_key_alias = os.environ.get("INSPECTAH_VAULT_KMS_KEY") or vault_section.get("kms_key_alias")
    if not kms_key_alias:
        raise ValueError("Evidence Vault config requires a kms_key_alias or INSPECTAH_VAULT_KMS_KEY.")
    endpoint_url = os.environ.get("INSPECTAH_VAULT_ENDPOINT_URL") or vault_section.get("endpoint_url")
    backend = vault_section.get("backend") or "local_stub"
    default_ttl = int(
        os.environ.get(
            "INSPECTAH_VAULT_TTL",
            vault_section.get("default_ttl_seconds", 900),
        )
    )
    local_root_value = os.environ.get("INSPECTAH_VAULT_LOCAL_ROOT") or vault_section.get("local_root")
    local_root = _resolve_local_root(local_root_value)
    return EvidenceStoreConfig(
        backend=backend,
        bucket=bucket,
        region=region,
        kms_key_alias=kms_key_alias,
        endpoint_url=endpoint_url,
        default_ttl_seconds=default_ttl,
        local_root=local_root,
    )


EVIDENCE_VAULT_SETTINGS = load_evidence_vault_settings()
