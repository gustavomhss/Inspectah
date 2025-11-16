#!/usr/bin/env python3
"""Smoke simples para testar GPT-4.1 mini com um texto real."""
from __future__ import annotations

import json
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "s5" / "rss_feed.xml"

if "OPENAI_API_KEY" not in os.environ:
    print("OPENAI_API_KEY não definido; smoke real abortado", file=sys.stderr)
    sys.exit(1)

try:
    from inspectah.normalizer.client_ai import generate_claims
except Exception as exc:  # pragma: no cover
    print(f"Falha ao importar cliente IA: {exc}", file=sys.stderr)
    sys.exit(1)

if not FIXTURE.exists():
    print(f"Fixture não encontrado: {FIXTURE}", file=sys.stderr)
    sys.exit(1)

root = ET.parse(FIXTURE).getroot()
item = root.find(".//item")
if item is None:
    print("Nenhum item no fixture RSS", file=sys.stderr)
    sys.exit(1)

text = item.findtext("description") or item.findtext("title") or ""
meta = {
    "source_id": "rss_economia",
    "item_id": item.findtext("guid") or "rss-smoke",
    "facts": {},
}

claims = generate_claims(text, meta, mode="gpt4mini")
print(json.dumps(claims, indent=2, ensure_ascii=False))
