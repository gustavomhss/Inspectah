"""Sprint 13 pilots registry helper (skeleton).

Loads config/s13_pilotos.yml and exposes helper functions for gates/tests.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import yaml

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "s13_pilotos.yml"


def load_pilots() -> Dict[str, List[dict]]:
    """Load pilots configuration (placeholder)."""

    with CONFIG_PATH.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def list_domains() -> List[str]:
    raise NotImplementedError("Wave 1 will implement list_domains")
