"""Modelos centrais do Inspectah + shim legada da Sprint 3."""

from .claim import Claim
from .item import InspectahItem
from .storage_compat import (
    LegacyItemRecord,
    fetch_evidence_record,
    fetch_items_by_source,
    get_connection,
    get_legacy_item,
    init_db,
    insert_evidence_record,
    insert_item,
    insert_item_kv,
    item_exists,
    list_legacy_items,
    reset_db,
)

__all__ = [
    "Claim",
    "InspectahItem",
    "LegacyItemRecord",
    "fetch_evidence_record",
    "fetch_items_by_source",
    "get_connection",
    "get_legacy_item",
    "init_db",
    "insert_evidence_record",
    "insert_item",
    "insert_item_kv",
    "item_exists",
    "list_legacy_items",
    "reset_db",
]
