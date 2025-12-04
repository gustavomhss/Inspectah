from __future__ import annotations

import json
from pathlib import Path

from app.ingestion.content_repo import ContentRepository
from app.ingestion.normalize_provider import normalize_news
from app.ingestion.providers.news_provider_client import NewsProviderClient
from app.providers.service import ProviderService


def run(limit: int = 3, evidence_dir: Path | None = None) -> dict:
    svc = ProviderService()
    repo = ContentRepository()
    profiles = [p for p in svc.list_profiles() if p.kind.value == "news"]
    client = NewsProviderClient()
    evidence_dir = evidence_dir or Path("out/evidence/S31_G2_provider_ingestion")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    summary = {"profiles": [], "items": 0, "persisted": 0}
    for profile in profiles:
        raw_items = client.fetch(profile, limit=limit)
        normalized = normalize_news(raw_items)
        for item in normalized:
            item["provider_id"] = profile.provider_id
            item["profile_id"] = profile.id
        inserted = repo.save_items(normalized)
        summary["profiles"].append({"profile": profile.slug, "items": len(normalized), "inserted": inserted})
        summary["items"] += len(normalized)
        summary["persisted"] += inserted
        out_path = evidence_dir / f"news_{profile.slug}.jsonl"
        with out_path.open("w", encoding="utf-8") as f:
            for item in normalized:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
    return summary


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2))
