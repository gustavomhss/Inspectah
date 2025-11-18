from __future__ import annotations

import html

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from .. import runtime_bridge
from ..templating import render_fragment, render_page

router = APIRouter(tags=["model"], include_in_schema=False)


def _escape(value: str | None) -> str:
    return html.escape(value or "")


@router.get('/model/fields', response_class=HTMLResponse)
async def show_model_fields(request: Request) -> HTMLResponse:
    fields = runtime_bridge.list_fields()
    fields_table = _build_fields_table(fields)
    samples = runtime_bridge.get_samples_by_source()
    samples_grid = _build_samples_grid(samples)
    body = render_fragment('model_fields.html', {'fields_table': fields_table, 'samples_grid': samples_grid})
    return render_page(request, body, title="Modelo")


def _build_fields_table(fields) -> str:
    if not fields:
        return '<p>Configuração de campos não encontrada.</p>'
    header = '<tr><th>Campo</th><th>Tipo</th><th>Obrigatório</th><th>Descrição</th></tr>'
    rows = []
    for field in fields:
        required = 'Sim' if field.required else 'Não'
        rows.append(
            '<tr>'
            f'<td>{_escape(field.name)}</td>'
            f'<td>{_escape(field.type)}</td>'
            f'<td>{required}</td>'
            f'<td>{_escape(field.description)}</td>'
            '</tr>'
        )
    return f"<table class='table'><thead>{header}</thead><tbody>{''.join(rows)}</tbody></table>"


def _build_samples_grid(samples) -> str:
    if not samples:
        return '<p>Sem prévias canônicas disponíveis.</p>'
    cards = []
    for source_id, records in samples.items():
        snippets = []
        for record in records:
            price = f"R$ {record.price_brl:.2f}" if record.price_brl is not None else "—"
            snippets.append(
                "<div class='record-snippet'>"
                f"<div>{_escape(record.product_name)} — {price}</div>"
                f"<small>{_escape(record.region)} • {_escape(record.reported_at)}</small>"
                "</div>"
            )
        cards.append(f"<article class='card'><h3>{_escape(source_id)}</h3>{''.join(snippets)}</article>")
    return f"<div class='cards'>{''.join(cards)}</div>"
