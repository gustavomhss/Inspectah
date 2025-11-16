from __future__ import annotations

import html
from urllib.parse import parse_qs
from typing import Dict, List

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from .. import runtime_bridge
from ..templating import render_fragment, render_page
from ..view_models import FlashMessage

router = APIRouter(tags=["admin"], include_in_schema=False)


def _escape(value: str | None) -> str:
    return html.escape(value or "")


def _build_flashes(flashes: List[FlashMessage] | None) -> str:
    return ''.join(f"<div class='flash {msg.level}'>{_escape(msg.text)}</div>" for msg in (flashes or []))


async def _extract_form_data(request: Request) -> Dict[str, str]:
    body = await request.body()
    raw = body.decode('utf-8') if body else ''
    pairs = parse_qs(raw, keep_blank_values=True)
    return {key: values[-1] for key, values in pairs.items()}


@router.get('/admin/sources', response_class=HTMLResponse)
async def admin_sources(request: Request, source_id: str | None = None) -> HTMLResponse:
    return _render(request, source_id=source_id)


@router.post('/admin/sources/new', response_class=HTMLResponse)
async def create_source(request: Request) -> HTMLResponse:
    form = await _extract_form_data(request)
    source_id = form.get('id', '').strip()
    payload = {
        "id": source_id,
        "name": form.get('name', '').strip(),
        "description": form.get('description', '').strip(),
        "transport.url": form.get('transport_url', '').strip(),
        "sample_file": form.get('sample_file', '').strip(),
        "notes": [line.strip() for line in form.get('notes', '').splitlines() if line.strip()],
    }
    flashes: List[FlashMessage]
    try:
        runtime_bridge.create_source(payload)
        flashes = [FlashMessage(level="success", text=f"Fonte {source_id} criada.")]
    except Exception as exc:
        flashes = [FlashMessage(level="error", text=f"Falha ao criar fonte: {exc}")]
    return _render(request, source_id=source_id or None, flashes=flashes)


@router.post('/admin/sources/{source_id}', response_class=HTMLResponse)
async def update_source(request: Request, source_id: str) -> HTMLResponse:
    form = await _extract_form_data(request)
    updates: Dict[str, object] = {
        "name": form.get('name', '').strip(),
        "description": form.get('description', '').strip(),
        "sample_file": form.get('sample_file', '').strip(),
        "transport.url": form.get('transport_url', '').strip(),
        "enabled": form.get('enabled') == '1',
        "notes": [line.strip() for line in form.get('notes', '').splitlines() if line.strip()],
    }
    flashes: List[FlashMessage]
    try:
        runtime_bridge.update_source(source_id, updates)
        flashes = [FlashMessage(level="success", text="Fonte atualizada com sucesso.")]
    except Exception as exc:
        flashes = [FlashMessage(level="error", text=f"Erro ao atualizar fonte: {exc}")]
    return _render(request, source_id=source_id, flashes=flashes)


def _render(request: Request, *, source_id: str | None = None, flashes: List[FlashMessage] | None = None) -> HTMLResponse:
    sources = runtime_bridge.list_sources()
    selected = runtime_bridge.get_source(source_id) if source_id else None
    if selected is None and sources:
        selected = sources[0]
    body = render_fragment(
        'admin_sources.html',
        {
            'flashes': _build_flashes(flashes),
            'sources_table': _build_sources_table(request, sources),
            'edit_form': _build_edit_form(request, selected) if selected else '<p>Selecione uma fonte para editar.</p>',
            'create_form': _build_create_form(request),
        },
    )
    return render_page(request, body, title='Fontes')


def _build_sources_table(request: Request, sources) -> str:
    if not sources:
        return '<p>Não há fontes cadastradas.</p>'
    rows = []
    base_url = request.url_for('admin_sources')
    for source in sources:
        edit_url = f"{base_url}?source_id={source.id}"
        status = 'Ativa' if source.enabled else 'Desativada'
        rows.append(
            '<tr>'
            f"<td>{_escape(source.id)}</td>"
            f"<td>{_escape(source.name)}</td>"
            f"<td>{_escape(source.type)}</td>"
            f'<td>{status}</td>'
            f"<td><a class='btn-link' href='{edit_url}'>Editar</a></td>"
            '</tr>'
        )
    header = '<tr><th>ID</th><th>Nome</th><th>Tipo</th><th>Status</th><th></th></tr>'
    return f"<table class='table'><thead>{header}</thead><tbody>{''.join(rows)}</tbody></table>"


def _build_edit_form(request: Request, source) -> str:
    notes_text = '\n'.join(source.notes or [])
    checked = 'checked' if source.enabled else ''
    action = request.url_for('update_source', source_id=source.id)
    return (
        f"<h3>Editar fonte — {_escape(source.id)}</h3>"
        f"<form class='form-card' method='post' action='{action}'>"
        f"<label>Nome<input type='text' name='name' value='{_escape(source.name)}'/></label>"
        f"<label>Descrição<textarea name='description' rows='3'>{_escape(source.description)}</textarea></label>"
        f"<label>URL de transporte<input type='text' name='transport_url' value='{_escape(source.transport_url)}'/></label>"
        f"<label>Arquivo de amostra<input type='text' name='sample_file' value='{_escape(source.raw.get('sample_file', ''))}'/></label>"
        f"<label>Notas<textarea name='notes' rows='4'>{_escape(notes_text)}</textarea></label>"
        f"<label class='checkbox'><input type='checkbox' name='enabled' value='1' {checked}/> Fonte ativa</label>"
        "<button type='submit'>Salvar alterações</button></form>"
    )


def _build_create_form(request: Request) -> str:
    action = request.url_for('create_source')
    return (
        "<h3>Criar nova fonte</h3>"
        f"<form class='form-card' method='post' action='{action}'>"
        "<label>ID<input type='text' name='id' required/></label>"
        "<label>Nome<input type='text' name='name'/></label>"
        "<label>Descrição<textarea name='description' rows='3'></textarea></label>"
        "<label>URL de transporte<input type='text' name='transport_url'/></label>"
        "<label>Arquivo de amostra<input type='text' name='sample_file'/></label>"
        "<label>Notas<textarea name='notes' rows='4'></textarea></label>"
        "<button type='submit'>Adicionar fonte</button></form>"
    )
