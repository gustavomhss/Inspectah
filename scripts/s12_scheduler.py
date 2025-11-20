"""Sprint 12 scheduler responsible for orchestrating pilot sources."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from scripts.s12_run_connector import ConnectorRunResult, run_for_source
from scripts.s12_sources_registry import DEFAULT_REGISTRY, SourceRegistry, list_sources_due


@dataclass
class ExecutionResult:
    """Represents a connector run performed by the scheduler."""

    source_id: str
    status: str
    events: int
    started_at: str
    finished_at: str
    evidence_path: Optional[str] = None
    error: Optional[str] = None


class Scheduler:
    """Scheduler for Sprint 12 pilot sources."""

    def __init__(self, registry: SourceRegistry | None = None) -> None:
        self.registry = registry or DEFAULT_REGISTRY

    def run_once(
        self,
        *,
        mode: str = "test",
        log_path: Optional[Path] = None,
        raw_events_dir: Optional[Path] = None,
    ) -> List[ExecutionResult]:
        """Execute all sources that are due inside a short test window."""

        utc_now = datetime.now(timezone.utc)
        due_sources = list_sources_due(now=utc_now, registry=self.registry)
        log_lines: List[str] = []
        results: List[ExecutionResult] = []

        for source in due_sources:
            started_at = datetime.now(timezone.utc)
            log_lines.append(self._format_log(source.id_fonte, "starting"))
            try:
                connector_result = run_for_source(source, mode=mode, evidence_dir=raw_events_dir)
                result = self._build_success_result(connector_result, started_at)
                log_lines.append(
                    self._format_log(
                        source.id_fonte,
                        f"success events={result.events} artifact={result.evidence_path}",
                    )
                )
            except Exception as exc:  # pragma: no cover - defensive logging
                finished_at = datetime.now(timezone.utc)
                result = ExecutionResult(
                    source_id=source.id_fonte,
                    status="error",
                    events=0,
                    started_at=started_at.isoformat().replace("+00:00", "Z"),
                    finished_at=finished_at.isoformat().replace("+00:00", "Z"),
                    error=str(exc),
                )
                log_lines.append(self._format_log(source.id_fonte, f"error={exc}"))
            results.append(result)

        if log_path is not None:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text("\n".join(log_lines) + ("\n" if log_lines else ""), encoding="utf-8")

        return results

    def _build_success_result(self, connector_result: ConnectorRunResult, started_at: datetime) -> ExecutionResult:
        finished_at = datetime.now(timezone.utc)
        return ExecutionResult(
            source_id=connector_result.source_id,
            status="success",
            events=len(connector_result.events),
            started_at=started_at.isoformat().replace("+00:00", "Z"),
            finished_at=finished_at.isoformat().replace("+00:00", "Z"),
            evidence_path=str(connector_result.output_path),
        )

    def _format_log(self, source_id: str, message: str) -> str:
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        return f"{ts} [S12][scheduler] source={source_id} {message}"


def run_scheduler_once(
    *,
    mode: str = "test",
    log_path: Optional[Path] = None,
    raw_events_dir: Optional[Path] = None,
    registry: SourceRegistry | None = None,
) -> dict:
    """Public helper used by bin/s12_g1_sources_scheduler.sh."""

    scheduler = Scheduler(registry=registry)
    results = scheduler.run_once(mode=mode, log_path=log_path, raw_events_dir=raw_events_dir)
    successes = len([result for result in results if result.status == "success"])
    failures = len(results) - successes
    total_events = sum(result.events for result in results)
    return {
        "total_sources": len(results),
        "successes": successes,
        "failures": failures,
        "total_events": total_events,
        "results": [asdict(result) for result in results],
    }


if __name__ == "__main__":  # pragma: no cover - manual execution helper
    summary = run_scheduler_once()
    print(summary)
