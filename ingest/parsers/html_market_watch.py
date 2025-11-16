import re
from typing import List, Dict

CARD_RE = re.compile(
    r'<(?:div|tr)[^>]*data-sku="(?P<sku>[^"]+)"[^>]*>'
    r'(?P<body>.*?)'
    r'</(?:div|tr)>',
    re.IGNORECASE | re.DOTALL,
)

FIELD_PATTERNS = [
    ("product", re.compile(r'<h2>(?P<value>[^<]+)</h2>', re.IGNORECASE)),
    ("product", re.compile(r'<td[^>]*class="name"[^>]*>(?P<value>[^<]+)</td>', re.IGNORECASE)),
    ("price", re.compile(r'<span[^>]*class="price"[^>]*>(?P<value>[^<]+)</span>', re.IGNORECASE)),
    ("price", re.compile(r'<td[^>]*class="price"[^>]*>(?P<value>[^<]+)</td>', re.IGNORECASE)),
    ("location", re.compile(r'<span[^>]*class="location"[^>]*>(?P<value>[^<]+)</span>', re.IGNORECASE)),
    ("location", re.compile(r'<td[^>]*class="location"[^>]*>(?P<value>[^<]+)</td>', re.IGNORECASE)),
    ("observed_at", re.compile(r'<time[^>]*datetime="(?P<value>[^"]+)"', re.IGNORECASE)),
    ("observed_at", re.compile(r'<td[^>]*class="observed-at"[^>]*>(?P<value>[^<]+)</td>', re.IGNORECASE)),
]


def _parse_price(raw):
    if raw is None:
        return None
    cleaned = raw.strip()
    cleaned = cleaned.replace("R$", "").replace(",", ".").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_html_market_watch(html: str, source_id: str, collected_at: str) -> List[Dict]:
    items: List[Dict] = []
    for match in CARD_RE.finditer(html):
        body = match.group("body")
        normalized: Dict[str, object] = {
            "source_id": source_id,
            "collected_at": collected_at,
            "sku": match.group("sku")
        }
        for field, pattern in FIELD_PATTERNS:
            value_match = pattern.search(body)
            if value_match:
                value = value_match.group("value").strip()
                normalized[field] = value
        if "price" in normalized:
            normalized["price"] = _parse_price(normalized.get("price"))
        items.append(normalized)
    return items
