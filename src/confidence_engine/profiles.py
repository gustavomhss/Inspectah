from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Mapping

CONFIDENCE_PROFILES_PATH = Path("configs/profiles/confidence_profiles.json")


@dataclass
class ConfidenceProfile:
    profile_id: str
    weights: Dict[str, float]
    limits: Dict[str, float]


def load_profiles(path: Path | None = None) -> Dict[str, ConfidenceProfile]:
    target = path or CONFIDENCE_PROFILES_PATH
    data = json.loads(target.read_text(encoding="utf-8"))
    profiles: Dict[str, ConfidenceProfile] = {}
    for entry in data.get("profiles", []):
        profile = ConfidenceProfile(
            profile_id=entry["id"],
            weights=dict(entry.get("weights", {})),
            limits=dict(entry.get("limits", {})),
        )
        profiles[profile.profile_id] = profile
    if "default" not in profiles:
        raise ValueError("Confidence profiles must define a 'default' entry")
    return profiles
