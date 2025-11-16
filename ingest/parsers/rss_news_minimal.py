import xml.etree.ElementTree as ET
from typing import List, Dict


def parse_rss_news_minimal(xml_body: str, source_id: str) -> List[Dict]:
    root = ET.fromstring(xml_body)
    items: List[Dict] = []
    for item in root.findall('.//item'):
        normalized: Dict[str, str] = {
            "source_id": source_id,
            "title": (item.findtext('title') or '').strip(),
            "url": (item.findtext('link') or '').strip(),
            "published_at": (item.findtext('pubDate') or '').strip(),
            "summary": (item.findtext('description') or '').strip() or None,
            "source_name": (item.findtext('source_name') or '').strip()
        }
        items.append(normalized)
    return items
