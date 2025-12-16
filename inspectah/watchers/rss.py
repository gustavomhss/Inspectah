from __future__ import annotations
import hashlib
from datetime import datetime, timezone
import ipaddress
import logging
from pathlib import Path
import socket
import time
from typing import Dict, List, Optional
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


# SSRF protection: allowed schemes and blocked IP ranges
_ALLOWED_SCHEMES = {"http", "https"}
_BLOCKED_IP_RANGES = [
    ipaddress.ip_network("10.0.0.0/8"),       # Private
    ipaddress.ip_network("172.16.0.0/12"),    # Private
    ipaddress.ip_network("192.168.0.0/16"),   # Private
    ipaddress.ip_network("127.0.0.0/8"),      # Loopback
    ipaddress.ip_network("169.254.0.0/16"),   # Link-local (AWS metadata)
    ipaddress.ip_network("::1/128"),          # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),         # IPv6 private
    ipaddress.ip_network("fe80::/10"),        # IPv6 link-local
]


def _validate_url_ssrf(url: str) -> None:
    """Validate URL to prevent SSRF attacks."""
    parsed = urlparse(url)

    # Check scheme
    if parsed.scheme.lower() not in _ALLOWED_SCHEMES:
        raise ValueError(f"URL scheme '{parsed.scheme}' not allowed. Only {_ALLOWED_SCHEMES} permitted.")

    # Check hostname exists
    hostname = parsed.hostname
    if not hostname:
        raise ValueError("URL must have a valid hostname")

    # Resolve hostname to IP and check against blocked ranges
    try:
        # Get all IPs for the hostname
        addr_info = socket.getaddrinfo(hostname, parsed.port or 80, proto=socket.IPPROTO_TCP)
        for family, _, _, _, sockaddr in addr_info:
            ip_str = sockaddr[0]
            ip = ipaddress.ip_address(ip_str)
            for blocked in _BLOCKED_IP_RANGES:
                if ip in blocked:
                    raise ValueError(f"URL resolves to blocked IP range: {ip_str}")
    except socket.gaierror as e:
        raise ValueError(f"Cannot resolve hostname '{hostname}': {e}")

from ..evidence import persist_evidence
from ..fields import apply_field_definitions
from ..fields.designer import normalize_url
from ..metrics import record_run_latency, record_ingest_event
from ..registry.loader import get_field_config, get_source_config
from ..models import get_connection, init_db, insert_item, insert_item_kv, item_exists


def _parse_rss(content: bytes) -> List[Dict[str, str]]:
    root = ET.fromstring(content)
    channel = root.find('channel')
    if channel is None:
        raise ValueError('invalid rss feed: missing channel')
    items: List[Dict[str, str]] = []
    for node in channel.findall('item'):
        raw = ET.tostring(node, encoding='unicode')
        entry = {
            'title': (node.findtext('title') or '').strip(),
            'link': (node.findtext('link') or '').strip(),
            'published': (node.findtext('pubDate') or node.findtext('published') or '').strip(),
            'description': (node.findtext('description') or '').strip(),
            'raw': raw,
        }
        items.append(entry)
    return items


def _fetch_feed(url: str) -> bytes:
    """Fetch RSS feed with SSRF protection."""
    _validate_url_ssrf(url)  # Validate URL before fetching
    req = Request(url, headers={'User-Agent': 'Inspectah-D8-Watcher'})
    with urlopen(req, timeout=10) as resp:  # noqa: S310
        return resp.read()


def run_once_for_source(source_id: str, *, use_fixture: bool = False, fixture_path: Optional[str] = None) -> int:
    init_db()
    source_cfg = get_source_config(source_id)
    field_cfg = get_field_config(source_id)
    logger.info(
        "ingest_started",
        extra={
            "source_id": source_cfg.id,
            "use_fixture": use_fixture,
            "fixture_path": fixture_path or "",
        },
    )
    if use_fixture:
        if not fixture_path:
            raise ValueError('fixture_path required when use_fixture=True')
        feed_bytes = Path(fixture_path).read_bytes()
    else:
        feed_bytes = _fetch_feed(source_cfg.url)
    articles = _parse_rss(feed_bytes)
    metadata = {'source_name': source_cfg.name}
    start = time.perf_counter()
    created = 0
    now = datetime.now(timezone.utc)
    try:
        with get_connection() as conn:
            for article in articles:
                link = article.get('link', '')
                if not link:
                    continue
                try:
                    canonical_url = normalize_url(link)
                except ValueError:
                    continue
                raw_xml = article['raw'].strip()
                content_hash = hashlib.sha256(raw_xml.encode('utf-8')).hexdigest()
                if item_exists(conn, source_cfg.id, content_hash):
                    continue
                item_id_hash = hashlib.sha256(f"{source_cfg.id}:{canonical_url}:{content_hash}".encode("utf-8")).hexdigest()[:16]
                text_content = "\n".join(filter(None, [article.get("title"), article.get("description")]))
                evidence = persist_evidence(
                    source_cfg.id,
                    item_id_hash,
                    canonical_url,
                    raw_xml.encode('utf-8'),
                    text_content,
                    collected_at=now,
                    content_hash=content_hash,
                )
                db_item_id = insert_item(
                    conn,
                    source_cfg.id,
                    canonical_url,
                    content_hash,
                    now,
                    str(evidence.manifest_path),
                )
                context = {'item': article, 'metadata': metadata}
                field_values = apply_field_definitions(field_cfg.definitions, context)
                for fv in field_values:
                    value_string: Optional[str] = None
                    value_numeric: Optional[float] = None
                    value_timestamp: Optional[datetime] = None
                    if fv.type == 'timestamp' and isinstance(fv.value, datetime):
                        value_timestamp = fv.value
                    elif isinstance(fv.value, (int, float)) and fv.type in {'number', 'integer'}:
                        value_numeric = float(fv.value)
                    else:
                        value_string = str(fv.value)
                    insert_item_kv(
                        conn,
                        db_item_id,
                        fv.name,
                        fv.type,
                        value_string=value_string,
                        value_numeric=value_numeric,
                        value_timestamp=value_timestamp,
                    )
                created += 1
        duration_ms = (time.perf_counter() - start) * 1000.0
        record_run_latency(duration_ms)
        record_ingest_event(created, error=False, source_id=source_id)
        logger.info(
            "ingest_completed",
            extra={
                "source_id": source_cfg.id,
                "items_ingested": created,
                "duration_ms": duration_ms,
            },
        )
        return created
    except Exception:
        record_ingest_event(0, error=True, source_id=source_id)
        logger.exception(
            "ingest_failed",
            extra={
                "source_id": source_cfg.id,
                "use_fixture": use_fixture,
                "fixture_path": fixture_path or "",
            },
        )
        raise


__all__ = ['run_once_for_source']
logger = logging.getLogger(__name__)
