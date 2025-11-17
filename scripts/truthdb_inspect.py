#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from inspectah.pipelines import s10_domain_a_obras, s10_domain_b_precos


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspeciona dados demo da Truth-DB da S10.")
    parser.add_argument("--domain", choices=("a", "b"), default="a", help="Domínio a inspecionar")
    parser.add_argument("--output", type=Path, help="Arquivo JSON opcional para salvar o relatório")
    args = parser.parse_args()

    report = (
        s10_domain_a_obras.run_demo_report()
        if args.domain == "a"
        else s10_domain_b_precos.run_demo_report()
    )
    summary = report["summary"]

    print(f"[Domain {args.domain.upper()}] métricas principais:")
    for key, value in summary.items():
        print(f"- {key}: {value}")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as fp:
            json.dump(report, fp, indent=2)
        print(f"Relatório salvo em {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
