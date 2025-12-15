"""
Batch Signal Calculator — S37

Orchestrates periodic calculation of all signals.
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.claims.graph_service import ClaimGraphService
from app.signals.calculators import (
    BattlegroundCalculator,
    LiesInCirculationCalculator,
    NarrativeFragilityCalculator,
    SilenceRadarCalculator,
)
from app.signals.signal_repository import SignalRepository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


class BatchSignalCalculator:
    """
    Calculates all signals for one or more domains.

    Designed to run as a batch job (e.g., every 1 hour).
    """

    DEFAULT_DOMAINS = ["pilot_politics"]

    def __init__(
        self,
        graph_service: Optional[ClaimGraphService] = None,
        signal_repo: Optional[SignalRepository] = None,
    ):
        self.graph = graph_service or ClaimGraphService()
        self.repo = signal_repo or SignalRepository()

        # Initialize calculators
        self.calculators = {
            "mentiras_em_circulacao": LiesInCirculationCalculator(self.graph),
            "campo_batalha": BattlegroundCalculator(self.graph),
            "radar_silencio": SilenceRadarCalculator(self.graph),
            "fragilidade_narrativa": NarrativeFragilityCalculator(self.graph),
        }

    def run(
        self,
        domains: Optional[List[str]] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Run all signal calculations for specified domains.

        Args:
            domains: List of domains to calculate. Defaults to DEFAULT_DOMAINS.

        Returns:
            Dict mapping domain to list of saved snapshots
        """
        domains = domains or self.DEFAULT_DOMAINS
        results: Dict[str, List[Dict[str, Any]]] = {}

        for domain in domains:
            logger.info(f"Calculating signals for domain: {domain}")
            domain_results = self._calculate_domain(domain)
            results[domain] = domain_results

        return results

    def run_single(
        self,
        signal_type: str,
        domain: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Run a single signal calculation.

        Args:
            signal_type: Type of signal to calculate
            domain: Domain to calculate for

        Returns:
            Saved snapshot or None if calculator not found
        """
        calculator = self.calculators.get(signal_type)
        if not calculator:
            logger.error(f"Unknown signal type: {signal_type}")
            return None

        result = calculator.calculate(domain)
        snapshot = calculator.to_snapshot(result)
        snapshot_id = self.repo.save_snapshot(snapshot)

        logger.info(f"Saved {signal_type} snapshot {snapshot_id} for {domain}")
        return {**snapshot, "id": snapshot_id}

    def _calculate_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Calculate all signals for a single domain."""
        snapshots = []

        for signal_type, calculator in self.calculators.items():
            try:
                logger.info(f"  Calculating {signal_type}...")
                result = calculator.calculate(domain)
                snapshot = calculator.to_snapshot(result)
                snapshot_id = self.repo.save_snapshot(snapshot)

                logger.info(f"    Saved snapshot {snapshot_id}")
                snapshots.append({**snapshot, "id": snapshot_id})

            except Exception as e:
                logger.error(f"  Error calculating {signal_type}: {e}")

        return snapshots

    def get_summary(self, domain: str) -> Dict[str, Any]:
        """Get a summary of latest signals for a domain."""
        latest = self.repo.get_all_latest(domain)

        summary = {
            "domain": domain,
            "timestamp": datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
            "signals": {},
        }

        for snapshot in latest:
            signal_type = snapshot["signal_type"]
            summary["signals"][signal_type] = {
                "timestamp": snapshot["timestamp"],
                "values": snapshot["values"],
            }

        return summary


def main():
    """CLI entry point for batch signal calculation."""
    parser = argparse.ArgumentParser(description="Batch Signal Calculator — S37")
    parser.add_argument(
        "--domains",
        nargs="+",
        default=["pilot_politics"],
        help="Domains to calculate signals for",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (instead of continuous mode)",
    )
    parser.add_argument(
        "--signal",
        type=str,
        help="Calculate only a specific signal type",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print summary of latest signals",
    )

    args = parser.parse_args()

    calculator = BatchSignalCalculator()

    if args.summary:
        for domain in args.domains:
            summary = calculator.get_summary(domain)
            print(f"\n=== Signal Summary for {domain} ===")
            for signal_type, data in summary.get("signals", {}).items():
                print(f"\n{signal_type}:")
                for key, value in data.get("values", {}).items():
                    print(f"  {key}: {value}")
        return 0

    if args.signal:
        for domain in args.domains:
            result = calculator.run_single(args.signal, domain)
            if result:
                print(f"Calculated {args.signal} for {domain}")
    else:
        results = calculator.run(args.domains)
        for domain, snapshots in results.items():
            print(f"\n{domain}: {len(snapshots)} signals calculated")
            for snap in snapshots:
                print(f"  - {snap['signal_type']}: {snap['id']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
