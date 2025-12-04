from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.ingestion.content_repo import ContentRepository
from app.ingestion.normalize_provider import normalize_news, normalize_social
from app.ingestion.providers.news_provider_client import NewsProviderClient
from app.ingestion.providers.social_provider_client import SocialProviderClient
from app.providers.models import ProfileKind
from app.providers.run_store import ProfileRun, RunStore, utcnow_iso
from app.providers.service import ProviderService


class ProfileRunner:
    def __init__(
        self,
        service: Optional[ProviderService] = None,
        run_store: Optional[RunStore] = None,
        evidence_dir: Optional[Path] = None,
    ):
        self.service = service or ProviderService()
        self.run_store = run_store or RunStore()
        self.content_repo = ContentRepository()
        self.evidence_dir = evidence_dir or Path("out/evidence/S31_G3_console/runs")
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

    def run_profile(self, profile_id: str, limit: int = 3) -> ProfileRun:
        profile = self.service.get_profile(profile_id)
        if not profile:
            raise ValueError("Profile not found")

        started_at = utcnow_iso()
        status = "success"
        persisted = 0
        items_len = 0
        message = None
        evidence_path: Optional[Path] = None
        try:
            if profile.kind == ProfileKind.NEWS:
                client = NewsProviderClient()
                raw_items = client.fetch(profile, limit=limit)
                normalized = normalize_news(raw_items)
            else:
                client = SocialProviderClient()
                raw_items = client.fetch(profile, limit=limit)
                normalized = normalize_social(raw_items)

            for item in normalized:
                item["provider_id"] = profile.provider_id
                item["profile_id"] = profile.id
            items_len = len(normalized)
            persisted = self.content_repo.save_items(normalized)
            evidence_path = self.evidence_dir / f"{profile.slug}_{int(datetime.utcnow().timestamp())}.jsonl"
            with evidence_path.open("w", encoding="utf-8") as f:
                for item in normalized:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")
        except Exception as exc:  # pragma: no cover - defensive path
            status = "fail"
            message = str(exc)

        finished_at = utcnow_iso()
        run = ProfileRun(
            run_id=f"run_{profile.id}_{int(datetime.utcnow().timestamp())}",
            provider_id=profile.provider_id,
            profile_id=profile.id,
            started_at=started_at,
            finished_at=finished_at,
            status=status,
            items=items_len,
            persisted=persisted,
            calls=items_len,
            evidence_path=str(evidence_path) if evidence_path else None,
            message=message,
        )
        self.run_store.record(run)
        return run

    def enqueue(self, profile_id: str, limit: int = 3) -> ProfileRun:
        # In this sprint, enqueue == run synchronously but the contract stays forward compatible.
        return self.run_profile(profile_id, limit=limit)

    def as_dict(self, run: ProfileRun) -> dict:
        return asdict(run)


def run_all(limit: int = 3) -> list[dict]:
    runner = ProfileRunner()
    runs: list[dict] = []
    for profile in runner.service.list_profiles():
        run = runner.enqueue(profile.id, limit=limit)
        runs.append(runner.as_dict(run))
    return runs


if __name__ == "__main__":  # pragma: no cover
    results = run_all()
    print(json.dumps({"runs": results}, indent=2, ensure_ascii=False))
