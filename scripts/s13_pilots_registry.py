"""Registry helpers for Sprint 13 pilot definitions."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

try:  # pragma: no cover - optional dependency
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    yaml = None

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "s13_pilotos.yml"
EXPECTED_DOMAINS = [
    "obra_publica",
    "evento_climatico",
    "projeto_lei",
    "carreira_politica",
    "influencer",
    "atleta",
]
REQUIRED_FIELDS = ["id", "dominio", "nome", "descricao_curta", "periodo", "local"]


class PilotRegistryError(RuntimeError):
    """Raised when the pilots registry is inconsistent."""


@dataclass(frozen=True)
class Pilot:
    """Convenience data holder."""

    raw: Dict[str, Any]

    @property
    def id(self) -> str:  # pragma: no cover - trivial
        return str(self.raw["id"])

    @property
    def domain(self) -> str:  # pragma: no cover
        return str(self.raw["dominio"])


def _load_yaml(path: Path) -> Dict[str, List[Dict[str, Any]]]:
    if not path.exists():
        raise PilotRegistryError(f"Arquivo de configuração ausente: {path}")

    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        data = yaml.safe_load(text) or {}
    else:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise PilotRegistryError("Estrutura inválida em s13_pilotos.yml (esperado dict).")
    return {str(k): v for k, v in data.items()}


def _validate_domains(data: Dict[str, Any]) -> None:
    missing = [domain for domain in EXPECTED_DOMAINS if domain not in data]
    extra = sorted(set(data) - set(EXPECTED_DOMAINS))
    if missing:
        raise PilotRegistryError(f"Domínios obrigatórios ausentes: {', '.join(missing)}")
    if extra:
        raise PilotRegistryError(f"Domínios inesperados no arquivo: {', '.join(extra)}")


def _validate_pilots(data: Dict[str, List[Dict[str, Any]]]) -> None:
    seen_ids: set[str] = set()
    for domain, pilots in data.items():
        if not isinstance(pilots, list) or not pilots:
            raise PilotRegistryError(f"Domínio {domain} precisa de uma lista de pilotos.")
        for pilot in pilots:
            if not isinstance(pilot, dict):
                raise PilotRegistryError(f"Piloto inválido em {domain}: {pilot!r}")
            missing_fields = [field for field in REQUIRED_FIELDS if field not in pilot]
            if missing_fields:
                raise PilotRegistryError(
                    f"Piloto {pilot.get('id', '<sem id>')} faltando campos: {', '.join(missing_fields)}"
                )
            if pilot["dominio"] != domain:
                raise PilotRegistryError(
                    f"Piloto {pilot['id']} tem dominio={pilot['dominio']} mas está listado em {domain}."
                )
            pilot_id = str(pilot["id"])
            if pilot_id in seen_ids:
                raise PilotRegistryError(f"ID de piloto duplicado: {pilot_id}")
            seen_ids.add(pilot_id)


def load_pilots_config(path: Optional[Path] = None) -> Dict[str, List[Dict[str, Any]]]:
    """Load and validate the pilots configuration file."""

    cfg_path = path or CONFIG_PATH
    data = _load_yaml(cfg_path)
    _validate_domains(data)
    _validate_pilots(data)
    return data


def list_domains(path: Optional[Path] = None) -> List[str]:
    """Return the ordered list of domains supported in Sprint 13."""

    data = load_pilots_config(path)
    return [domain for domain in EXPECTED_DOMAINS if domain in data]


def list_pilots(path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Return all pilots regardless of domain."""

    data = load_pilots_config(path)
    pilots: List[Dict[str, Any]] = []
    for domain in EXPECTED_DOMAINS:
        pilots.extend(data[domain])
    return pilots


def get_pilots_by_domain(domain: str, path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Return pilots for a specific domain."""

    domain = str(domain)
    data = load_pilots_config(path)
    if domain not in data:
        raise PilotRegistryError(f"Domínio desconhecido: {domain}")
    return data[domain]


def get_pilot(pilot_id: str, path: Optional[Path] = None) -> Dict[str, Any]:
    """Fetch a single pilot entry by its identifier."""

    pilot_id = str(pilot_id)
    for pilot in list_pilots(path):
        if str(pilot["id"]) == pilot_id:
            return pilot
    raise PilotRegistryError(f"Piloto não encontrado: {pilot_id}")


def _format_summary(pilots: Iterable[Dict[str, Any]]) -> str:
    by_domain: Dict[str, int] = {domain: 0 for domain in EXPECTED_DOMAINS}
    for pilot in pilots:
        domain = str(pilot["dominio"])
        if domain in by_domain:
            by_domain[domain] += 1
    return "\n".join(f"- {domain}: {count} piloto(s)" for domain, count in by_domain.items())


def _main() -> None:  # pragma: no cover - debug helper
    data = load_pilots_config()
    print("Pilotos carregados:")
    print(_format_summary(list_pilots(path=CONFIG_PATH)))
    print(f"Total: {sum(len(p) for p in data.values())}")


if __name__ == "__main__":  # pragma: no cover
    _main()


__all__ = [
    "CONFIG_PATH",
    "EXPECTED_DOMAINS",
    "load_pilots_config",
    "list_domains",
    "list_pilots",
    "get_pilots_by_domain",
    "get_pilot",
    "PilotRegistryError",
    "Pilot",
]
