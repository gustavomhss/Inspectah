#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from inspectah.pipelines import s10_domain_a_obras, s10_domain_b_precos
from inspectah.truthdb.engine import TruthDBEngine
from inspectah.truthdb import exports

OUT_DIR = Path("out/evidence/S10_G7/exports")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    engine = TruthDBEngine()
    s10_domain_a_obras.build_domain_a_truthdb(engine=engine)
    s10_domain_b_precos.build_domain_b_truthdb(engine=engine)

    export_sets = {
        "domain_a_demo": ["obra_123_prazo"],
        "domain_b_demo": ["preco_media_sp_julho"],
    }

    for name, fact_ids in export_sets.items():
        data = exports.export_facts(engine.truthdb, fact_ids)
        (OUT_DIR / f"{name}.json").write_text(json.dumps(data, indent=2), encoding="utf-8")

    print(f"Exports gravados em {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
