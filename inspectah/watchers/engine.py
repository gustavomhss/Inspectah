"""Watcher engine responsável por orquestrar fontes cadastradas."""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List

from inspectah.watchers import api_watcher, html_watcher, rss_watcher

WATCHERS = {
    "rss": rss_watcher.collect,
    "api": api_watcher.collect,
    "html": html_watcher.collect,
}


def _load_registry(path: Path) -> List[Dict[str, Any]]:
    data = path.read_text()
    try:
        import yaml  # type: ignore

        parsed = yaml.safe_load(data)
    except Exception:
        parsed = json.loads(data)
    sources = parsed.get("sources", []) if isinstance(parsed, dict) else []
    return [source for source in sources if isinstance(source, dict)]


def run_watchers(
    registry_path: str | Path = "inspectah/config/sources_registry.yaml",
    *,
    logger: logging.Logger | None = None,
    watcher_overrides: Dict[str, Any] | None = None,
    fixtures_base: str | Path | None = None,
) -> Dict[str, Any]:
    """Executa um ciclo de watchers e retorna resultados agregados."""

    logger = logger or logging.getLogger("inspectah.watchers")
    registry_file = Path(registry_path)
    if not registry_file.exists():
        raise FileNotFoundError(f"Registry não encontrado: {registry_file}")

    sources = _load_registry(registry_file)
    watcher_map = WATCHERS.copy()
    if watcher_overrides:
        watcher_map.update(watcher_overrides)

    fixtures_base_path = Path(fixtures_base) if fixtures_base else Path("fixtures/s5")

    results: Dict[str, Any] = {"runs": []}

    for source in sources:
        source_id = source.get("id")
        if not source.get("enabled", False):
            continue
        watcher_type = source.get("type")
        watcher_fn = watcher_map.get(watcher_type)
        run_id = f"{source_id}-{int(time.time() * 1000)}"
        start = time.perf_counter()
        try:
            if watcher_fn is None:
                raise ValueError(f"Watcher não implementado: {watcher_type}")
            items = watcher_fn(source, fixtures_base=fixtures_base_path)
            latency = time.perf_counter() - start
            logger.info(
                "watcher_run",
                extra={
                    "source_id": source_id,
                    "run_id": run_id,
                    "status": "success",
                    "count": len(items),
                    "latency_sec": round(latency, 3),
                },
            )
            results["runs"].append(
                {
                    "source_id": source_id,
                    "run_id": run_id,
                    "status": "success",
                    "items": items,
                    "latency_sec": latency,
                }
            )
        except Exception as exc:  # pylint: disable=broad-except
            latency = time.perf_counter() - start
            logger.error(
                "watcher_run_error",
                extra={
                    "source_id": source_id,
                    "run_id": run_id,
                    "status": "fail",
                    "error": str(exc),
                    "latency_sec": round(latency, 3),
                },
            )
            results["runs"].append(
                {
                    "source_id": source_id,
                    "run_id": run_id,
                    "status": "fail",
                    "error": str(exc),
                }
            )
            continue

    return results
