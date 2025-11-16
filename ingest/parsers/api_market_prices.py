from typing import Iterable, List, Dict


def parse_api_market_prices(items: Iterable[Dict], source_id: str, collected_at: str) -> List[Dict]:
    parsed = []
    for raw in items:
        parsed.append(
            {
                "source_id": source_id,
                "collected_at": collected_at,
                "sku": raw["sku"],
                "product": raw["product"],
                "price": float(raw["price"]),
                "currency": raw["currency"],
                "region": raw["region"],
                "last_update": raw["last_update"],
                "promo_label": raw.get("promo_label")
            }
        )
    return parsed
