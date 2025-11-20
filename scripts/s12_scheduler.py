"""Sprint 12 scheduler skeleton.

Wave 1 wires the continuous ingestion loop here. The scheduler is responsible for
inspecting the registry, deciding which connectors to run in the current window
and orchestrating calls to ``scripts.s12_run_connector`` while leaving detailed
logging/evidence to the gate scripts.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, List, Sequence

from scripts.s12_sources_registry import DEFAULT_REGISTRY, SourceConfig, SourceRegistry


@dataclass
class ScheduledExecution:
    """Represents a connector run scheduled during a simulated window."""

    id_fonte: str
    janela: str
    tentativa: int = 1


class Scheduler:
    """Decides which sources run in each window.

    The real Wave 1 implementation will plug retry policies, cadence tracking
    and evidence collection. The skeleton keeps method signatures stable.
    """

    def __init__(self, registry: SourceRegistry | None = None) -> None:
        self.registry = registry or DEFAULT_REGISTRY

    def plan_window(self, window_start: datetime, duration: timedelta) -> List[ScheduledExecution]:
        """Return the executions that should happen inside the window.

        This method will soon use each source cadence to decide whether the
        connector must run. For the skeleton it returns an empty list so that
        callers have deterministic behavior without side effects.
        """

        _ = (window_start, duration)
        return []

    def run_window(self, window_start: datetime, duration: timedelta) -> None:
        """Placeholder for the execution loop that triggers connectors."""

        executions = self.plan_window(window_start, duration)
        if executions:
            raise NotImplementedError(
                "Wave 1 must implement connector execution for scheduled runs"
            )


def run_scheduler(window_seconds: int = 60) -> None:
    """Convenience entrypoint for shell scripts.

    Gate S12-G1 will invoke this function with deterministic inputs during Wave
    1. For now we only log a friendly message to avoid silent success.
    """

    duration = timedelta(seconds=window_seconds)
    window_start = datetime.utcnow()
    Scheduler().run_window(window_start, duration)
    raise SystemExit(
        "S12 scheduler skeleton: implement continuous execution in Wave 1 before running gates."
    )


if __name__ == "__main__":
    run_scheduler()
