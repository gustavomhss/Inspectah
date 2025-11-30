from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

DEFAULT_BASE = Path("out/evidence/S27_G4_audit_logs_evidence")


def _resolve_base(base_dir: Optional[Path]) -> Path:
    if base_dir:
        return Path(base_dir)
    env_base = os.environ.get("INSPECTAH_AUDIT_LOG_BASE")
    if env_base:
        return Path(env_base)
    return DEFAULT_BASE


def record_admin_action(action: str, source_id: str, user: str, meta: Optional[Dict[str, object]] = None, base_dir: Optional[Path] = None) -> Path:
    base = _resolve_base(base_dir)
    base.mkdir(parents=True, exist_ok=True)
    entry = {
        "action": action,
        "source_id": source_id,
        "user": user,
        "meta": meta or {},
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    log_path = base / "sources_admin_actions.log"
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return log_path
