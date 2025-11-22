"""Orquestra cenários adversariais focados em Debunker v1 e Comitês V1/V2/V3."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Dict

from scripts.s16_attack_scenarios import list_scenarios, run_scenarios


def run_suite(evidence_dir: Path | None = None, *, smoke: bool = False) -> Dict[str, object]:
    evidence_dir = evidence_dir or Path("out/evidence/S16_T3_debunker_and_committees")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    candidates = list_scenarios(tags=["debunker", "committee"])
    scenario_ids = [item["id"] for item in candidates]
    manifest = run_scenarios(
        scenario_ids=scenario_ids,
        evidence_dir=evidence_dir,
        smoke=smoke,
        tags=["debunker", "committee"],
    )
    status_counter = Counter(res.get("status", "unknown") for res in manifest.get("results", []))
    dangerous = status_counter.get("dangerous", 0)
    mitigated = status_counter.get("mitigated", 0)
    detected_failure = status_counter.get("detected_failure", 0)
    summary = {
        "total": manifest.get("total", 0),
        "mitigated": mitigated,
        "dangerous": dangerous,
        "detected_failure": detected_failure,
        "unknown": status_counter.get("unknown", 0),
    }
    (evidence_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (evidence_dir / "MANIFEST.json").write_text(
        json.dumps(
            {"summary": summary, "scenarios": manifest.get("results", []), "smoke": smoke},
            indent=2,
        ),
        encoding="utf-8",
    )
    return {"metrics": summary, "results": manifest.get("results", [])}


def main() -> None:
    parser = argparse.ArgumentParser(description="Debunker + Comitês sob ataque (S16)")
    parser.add_argument("--evidence-dir", default="out/evidence/S16_T3_debunker_and_committees")
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    result = run_suite(Path(args.evidence_dir), smoke=args.smoke)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
