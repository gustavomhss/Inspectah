from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from app.cases.loader import load_cases, load_collections


def compute_metrics() -> dict:
    cases = load_cases()
    collections = load_collections()
    themes = Counter(c.theme for c in cases)
    tags = Counter(tag for c in cases for tag in c.tags)
    metrics = {
        "cases_total": len(cases),
        "collections_total": len(collections),
        "cases_by_theme": dict(themes),
        "top_tags": dict(tags.most_common(10)),
    }
    return metrics


if __name__ == "__main__":
    print(json.dumps(compute_metrics(), indent=2))
