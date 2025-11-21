"""Feedback service for Sprint 12 Explorer/Comunidade v0."""
from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

ROOT_DIR = Path(__file__).resolve().parents[1]
STORE_PATH = ROOT_DIR / "out" / "runtime" / "s12_feedback_store.json"
VALID_STATUSES = {"novo", "em_analise", "resolvido"}


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _ensure_store_dir() -> None:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)


@dataclass
class Feedback:
    """Represents a feedback entry produced by Explorer v0."""

    id_feedback: str
    target_type: str
    target_id: str
    mensagem: str
    status: str = "novo"
    autor: Optional[str] = None
    created_at: str = field(default_factory=_utcnow)
    updated_at: str = field(default_factory=_utcnow)
    canal: str = "explorer_v0"
    extra: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class FeedbackService:
    """Store and mutate feedback lifecycle for G5/G6 workflows."""

    def __init__(self, store_path: Path | None = None) -> None:
        self.store_path = store_path or STORE_PATH
        self._items: Dict[str, Feedback] = {}
        self._load()

    def _load(self) -> None:
        if not self.store_path.exists():
            self._items = {}
            return
        data = json.loads(self.store_path.read_text(encoding="utf-8"))
        self._items = {entry["id_feedback"]: Feedback(**entry) for entry in data}

    def _persist(self) -> None:
        _ensure_store_dir()
        payload = [feedback.to_dict() for feedback in self._items.values()]
        self.store_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def reset_store(self) -> None:
        """Remove all stored feedback (used by deterministic gates)."""

        self._items.clear()
        if self.store_path.exists():
            self.store_path.unlink()

    def _next_id(self) -> str:
        return f"fb-{uuid.uuid4().hex[:12]}"

    def _store_feedback(
        self,
        target_type: str,
        target_id: str,
        mensagem: str,
        autor: Optional[str],
        extra: Optional[Dict[str, str]] = None,
    ) -> Feedback:
        feedback = Feedback(
            id_feedback=self._next_id(),
            target_type=target_type,
            target_id=target_id,
            mensagem=mensagem,
            autor=autor,
            extra=extra or {},
        )
        self._items[feedback.id_feedback] = feedback
        self._persist()
        return feedback

    def create_feedback_for_case(
        self,
        case_id: str,
        mensagem: str,
        autor: Optional[str] = None,
        extra: Optional[Dict[str, str]] = None,
    ) -> Feedback:
        return self._store_feedback("case", case_id, mensagem, autor, extra)

    def create_feedback_for_event(
        self,
        event_id: str,
        mensagem: str,
        autor: Optional[str] = None,
        extra: Optional[Dict[str, str]] = None,
    ) -> Feedback:
        return self._store_feedback("event", event_id, mensagem, autor, extra)

    def list_feedbacks(self, status: Optional[str] = None) -> List[Feedback]:
        entries = list(self._items.values())
        entries.sort(key=lambda item: item.created_at, reverse=True)
        if status is None or status == "todos":
            return entries
        return [entry for entry in entries if entry.status == status]

    def update_feedback_status(self, feedback_id: str, status: str) -> Feedback:
        if status not in VALID_STATUSES:
            raise ValueError(f"Status inválido: {status}")
        entry = self._items[feedback_id]
        entry.status = status
        entry.updated_at = _utcnow()
        self._persist()
        return entry

    def to_dict(self) -> Dict[str, Dict[str, object]]:
        return {feedback_id: feedback.to_dict() for feedback_id, feedback in self._items.items()}


DEFAULT_FEEDBACK_SERVICE = FeedbackService()


__all__ = ["Feedback", "FeedbackService", "DEFAULT_FEEDBACK_SERVICE", "VALID_STATUSES"]
