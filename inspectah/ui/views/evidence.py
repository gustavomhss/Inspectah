from __future__ import annotations

import html

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from .. import runtime_bridge
from ..templating import render_fragment, render_page

router = APIRouter(tags=["evidence"], include_in_schema=False)


def _escape(value: str | None) -> str:
    return html.escape(value or "")


@router.get('/evidence/{item_id}', response_class=HTMLResponse)
async def evidence_detail(request: Request, item_id: str) -> HTMLResponse:
    record = runtime_bridge.get_record(item_id)
    if record is None:
        content = '<p>Registro não encontrado nos dados canônicos.</p>'
        header = '#'
    else:
        price = f"R$ {record.price_brl:.2f}" if record.price_brl is not None else '—'
        packages = runtime_bridge.resolve_evidence_packages(record)
        parts = [
            f"<p><strong>{_escape(record.product_name)}</strong> • {price} • {_escape(record.region)}</p>",
            f"<p>Referência: {_escape(record.reported_at)} • URL: <a href='{_escape(record.source_url)}'>{_escape(record.source_url)}</a></p>",
        ]
        if packages:
            items = []
            for package in packages:
                items.append(
                    '<li>'
                    f"<strong>{_escape(package.source_id)}</strong> — coletado em {_escape(package.collected_at)}"
                    f"<div>Manifesto: <code>{_escape(package.manifest_path)}</code></div>"
                    f"<div>Pacote: <code>{_escape(package.evidence_path)}</code></div>"
                    f"<div>Hash: <code>{_escape(package.hash_sha256)}</code></div>"
                    '</li>'
                )
            parts.append(f"<h3>Pacotes de evidência</h3><ul class='evidence-list'>{''.join(items)}</ul>")
        else:
            parts.append('<p>Nenhum pacote de evidência associado ao registro.</p>')
        content = ''.join(parts)
        header = record.item_id
    body = render_fragment('evidence_detail.html', {'header': _escape(header), 'content': content})
    return render_page(request, body, title='Evidência')
