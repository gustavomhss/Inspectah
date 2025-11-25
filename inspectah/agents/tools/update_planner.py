from __future__ import annotations

from typing import Dict, List


def plan_updates(current: Dict, proposed: Dict) -> List[Dict]:
    changes: List[Dict] = []
    tracked_fields = [
        "name",
        "description",
        "endpoint",
        "themes",
        "info_types",
        "type",
        "refresh_interval",
    ]
    for field in tracked_fields:
        cur_val = current.get(field)
        new_val = proposed.get(field, cur_val)
        if new_val != cur_val and new_val is not None:
            changes.append({"field": field, "from": cur_val, "to": new_val})
    return changes
