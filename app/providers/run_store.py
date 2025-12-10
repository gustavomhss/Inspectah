from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ProfileRun:
    run_id: str
    provider_id: str
    profile_id: str
    started_at: str
    finished_at: str
    status: str
    items: int
    persisted: int
    calls: int
    evidence_path: Optional[str] = None
    message: Optional[str] = None


class RunStore:
    """
    Minimal run store backed by JSONL. Used to expose recent executions in the Console without
    introducing a new DB migration during the sprint.
    """

    def __init__(self, path: Optional[Path] = None):
        self.path = path or Path("out/evidence/S31_G3_console/profile_runs.jsonl")
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, run: ProfileRun) -> ProfileRun:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(run), ensure_ascii=False) + "\n")
        return run

    def list_runs(self, profile_id: Optional[str] = None, limit: int = 20) -> List[Dict]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as f:
            lines = f.readlines()
        records: List[Dict] = []
        for line in reversed(lines):
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            if profile_id and data.get("profile_id") != profile_id:
                continue
            records.append(data)
            if len(records) >= limit:
                break
        return list(reversed(records))

    def metrics(self, profile_id: Optional[str] = None) -> Dict[str, int | str | None]:
        runs = self.list_runs(profile_id=profile_id, limit=200)
        if not runs:
            return {"total_runs": 0, "success": 0, "fail": 0, "last_run_at": None, "items": 0, "persisted": 0}
        total = len(runs)
        success = len([r for r in runs if r.get("status") == "success"])
        fail = total - success
        last_run_at = runs[-1].get("finished_at")
        items = sum(r.get("items", 0) for r in runs)
        persisted = sum(r.get("persisted", 0) for r in runs)
        return {
            "total_runs": total,
            "success": success,
            "fail": fail,
            "last_run_at": last_run_at,
            "items": items,
            "persisted": persisted,
        }
