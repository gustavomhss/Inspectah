from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Mapping

from fastapi import Request
from fastapi.responses import HTMLResponse

from .config import get_settings

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
PLACEHOLDER = re.compile(r"{{\s*(\w+)\s*}}")


def _render_template(name: str, context: Mapping[str, str]) -> str:
    template = (TEMPLATES_DIR / name).read_text(encoding="utf-8")
    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        return context.get(key, "")

    return PLACEHOLDER.sub(replace, template)


def render_page(request: Request, body: str, *, title: str | None = None) -> HTMLResponse:
    settings = get_settings()
    static_css = str(request.url_for("static", path="css/main.css"))
    static_js = str(request.url_for("static", path="js/main.js"))
    nav_links = "".join(
        f'<a href="{html.escape(str(url))}">{html.escape(label)}</a>'
        for label, url in [
            ("Início", request.url_for("index")),
            ("Fontes", request.url_for("admin_sources")),
            ("Modelo", request.url_for("show_model_fields")),
            ("Consulta", request.url_for("query_get")),
        ]
    )
    page = _render_template(
        "base.html",
        {
            "title": html.escape(title or settings.title),
            "nav": nav_links,
            "content": body,
            "css_href": static_css,
            "js_href": static_js,
            "footer_note": f"Inspectah UI Alpha — {html.escape(settings.version)}",
        },
    )
    return HTMLResponse(page)


def render_fragment(name: str, context: Mapping[str, str]) -> str:
    return _render_template(name, context)
