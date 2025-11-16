from __future__ import annotations

import json
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Iterator, Tuple

from fastapi.testclient import TestClient

from inspectah.ui import app

REPO_ROOT = Path(__file__).resolve().parents[2]


def prepare_gate_paths(slug: str) -> Tuple[Path, Path]:
    scorecard = REPO_ROOT / "out" / "scorecards" / f"{slug}.json"
    evidence_dir = REPO_ROOT / "out" / "evidence" / slug
    scorecard.parent.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    return scorecard, evidence_dir


def write_json(path: Path, payload: Dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def get_client() -> TestClient:
    return TestClient(app)


@contextmanager
def preserved_file(path: Path) -> Iterator[str]:
    original = path.read_text(encoding="utf-8")
    try:
        yield original
    finally:
        path.write_text(original, encoding="utf-8")


def monotonic_seconds() -> float:
    return time.perf_counter()
