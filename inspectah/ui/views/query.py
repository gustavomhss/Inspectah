from __future__ import annotations

import html
from urllib.parse import parse_qs
from datetime import datetime
from typing import Dict

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from .. import runtime_bridge
from ..schemas import QueryFilters
from ..templating import render_fragment, render_page

router = APIRouter(tags=["query"], include_in_schema=False)



async def _extract_form(request: Request) -> Dict[str, str]:
    body = await request.body()
    raw = body.decode('utf-8') if body else ''
    return {key: values[-1] for key, values in parse_qs(raw, keep_blank_values=True).items()}

def _escape(value: str | None) -> str:
    return html.escape(value or "")


@router.get('/query', response_class=HTMLResponse)
async def query_get(request: Request) -> HTMLResponse:
    filters = _parse_filters(dict(request.query_params))
    return _render(request, filters)


@router.post('/query', response_class=HTMLResponse)
async def query_post(request: Request) -> HTMLResponse:
    form = await _extract_form(request)
    filters = _parse_filters(
        {
            'from_date': form.get('from_date', ''),
            'to_date': form.get('to_date', ''),
            'categoria': form.get('categoria', ''),
            'regiao': form.get('regiao', ''),
            'fonte': form.get('fonte', ''),
            'search': form.get('search', ''),
        }
    )
    return _render(request, filters)


def _render(request: Request, filters: QueryFilters) -> HTMLResponse:
    records = runtime_bridge.run_query(filters)
    decision = runtime_bridge.consolidate(records) if records else None
    filters_form = _build_filters_form(request, filters)
    decision_block = _build_decision_block(decision)
    results_table = _build_results_table(request, records)
    body = render_fragment(
        'query.html',
        {
            'filters_form': filters_form,
            'decision_block': decision_block,
            'results_table': results_table,
        },
    )
    return render_page(request, body, title="Consulta")


def _build_filters_form(request: Request, filters: QueryFilters) -> str:
    values = _filters_to_strings(filters)
    action = request.url_for('query_post')
    return (
        f"<form class='filters' method='post' action='{action}'>"
        f"<label>De<input type='datetime-local' name='from_date' value='{values['from_date']}'/></label>"
        f"<label>Até<input type='datetime-local' name='to_date' value='{values['to_date']}'/></label>"
        f"<label>Categoria<input type='text' name='categoria' value='{_escape(values['categoria'])}' placeholder='graos, proteinas...'/></label>"
        f"<label>Região<input type='text' name='regiao' value='{_escape(values['regiao'])}' placeholder='Zona Norte...'/></label>"
        f"<label>Fonte<input type='text' name='fonte' value='{_escape(values['fonte'])}' placeholder='fonte_a'/></label>"
        f"<label>Busca textual<input type='text' name='search' value='{_escape(values['search'])}' placeholder='produto, notas...'/></label>"
        f"<div class='filter-actions'><button type='submit'>Consultar</button><a class='btn-link' href='{request.url_for('query_get')}'>Limpar</a></div>"
        "</form>"
    )


def _build_decision_block(decision) -> str:
    if decision is None:
        return '<p>Nenhum registro disponível para consolidar.</p>'
    if decision.value is None:
        return '<p>Nenhum preço disponível para aplicar a estratégia de consolidação.</p>'
    sources = ', '.join(decision.sources_used)
    return (
        f"<p class='highlight'>Valor consolidado: <strong>R$ {decision.value:.2f}</strong></p>"
        f"<p>{_escape(decision.explanation)}</p>"
        f"<ul><li>Registros usados: {decision.sample_count}</li><li>Fontes consideradas: {_escape(sources)}</li></ul>"
    )


def _build_results_table(request: Request, records) -> str:
    if not records:
        return '<p>Nenhum registro encontrado para os filtros atuais.</p>'
    rows = []
    for record in records:
        price = f"R$ {record.price_brl:.2f}" if record.price_brl is not None else "—"
        evidence_url = request.url_for('evidence_detail', item_id=record.item_id)
        sources = ''.join(f"<span class='badge'>{_escape(s.get('source_id'))}</span>" for s in record.supporting_sources)
        rows.append(
            '<tr>'
            f'<td>{_escape(record.item_id)}</td>'
            f'<td>{_escape(record.product_name)}</td>'
            f'<td>{price}</td>'
            f'<td>{_escape(record.region)}</td>'
            f'<td>{_escape(record.reported_at)}</td>'
            f'<td>{sources}</td>'
            f"<td><a class='btn-link' href='{evidence_url}'>Ver evidência</a></td>"
            '</tr>'
        )
    header = '<tr><th>Item</th><th>Produto</th><th>Preço</th><th>Região</th><th>Data</th><th>Fontes</th><th></th></tr>'
    return f"<table class='table'><thead>{header}</thead><tbody>{''.join(rows)}</tbody></table>"


def _parse_filters(raw: Dict[str, str]) -> QueryFilters:
    def parse_date(value: str) -> datetime | None:
        text = value.strip()
        if not text:
            return None
        try:
            return datetime.fromisoformat(text)
        except ValueError:
            pass
        for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d"):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue
        return None

    return QueryFilters(
        from_date=parse_date(raw.get("from_date", "")),
        to_date=parse_date(raw.get("to_date", "")),
        categoria=(raw.get("categoria") or "").strip() or None,
        regiao=(raw.get("regiao") or "").strip() or None,
        fonte=(raw.get("fonte") or "").strip() or None,
        search=(raw.get("search") or "").strip() or None,
    )


def _filters_to_strings(filters: QueryFilters) -> Dict[str, str]:
    def fmt(value: datetime | None) -> str:
        return value.strftime("%Y-%m-%dT%H:%M") if value else ""

    return {
        "from_date": fmt(filters.from_date),
        "to_date": fmt(filters.to_date),
        "categoria": filters.categoria or "",
        "regiao": filters.regiao or "",
        "fonte": filters.fonte or "",
        "search": filters.search or "",
    }
