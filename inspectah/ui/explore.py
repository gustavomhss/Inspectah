"""UI de exploração de itens indexados."""
from __future__ import annotations

from pathlib import Path
from typing import List

from inspectah.indexer.query_api import QueryAPI

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


def _load_template(name: str) -> str:
    path = TEMPLATES_DIR / name
    return path.read_text(encoding="utf-8")


def _preview_text(bundle_path: str, limit: int = 400) -> str:
    text_file = Path(bundle_path) / "text.txt"
    if not text_file.exists():
        return "(sem texto disponível)"
    content = text_file.read_text(encoding="utf-8", errors="ignore").strip()
    if len(content) > limit:
        content = content[:limit] + "..."
    return content or "(texto vazio)"


def _render_claims(item) -> str:
    if not item.claims:
        return "(nenhum claim)"
    lines: List[str] = []
    for idx, claim in enumerate(item.claims, start=1):
        lines.append(
            f"[{idx}] {claim.declared_metric} = {claim.declared_value} {claim.declared_unit or ''} "
            f"| polarity={claim.polarity} | verdict={claim.local_verdict} | confidence={claim.confidence_claim}"
        )
    return "\n".join(lines)


def _show_item_detail(item) -> None:
    template = _load_template("explore_item_detail.txt")
    preview = _preview_text(item.bundle_path or "") if item.bundle_path else "(bundle não informado)"
    rendered = template.format(
        source_id=item.source_id,
        item_id=item.item_id,
        state=item.state,
        equivalence_key=item.equivalence_key,
        headline=item.headline or "(sem headline)",
        published_at=item.published_at or "(sem data)",
        bundle_path=item.bundle_path or "(desconhecido)",
        preview_text=preview,
        claims_block=_render_claims(item),
    )
    print(rendered)
    input("Pressione Enter para voltar...")


def run_explore_ui(index_path: str | Path = "data/index") -> None:
    api = QueryAPI(index_path)
    header = _load_template("explore_header.txt")
    sources = api.list_sources()
    if not sources:
        print("Nenhuma fonte encontrada no índice. Execute o pipeline primeiro.")
        return

    while True:
        print(header)
        for idx, source_id in enumerate(sources, start=1):
            print(f"{idx}. {source_id}")
        choice = input("Selecione a fonte (número) ou 'q' para sair: ").strip().lower()
        if choice == "q":
            break
        try:
            source = sources[int(choice) - 1]
        except (ValueError, IndexError):
            print("Seleção inválida.")
            continue

        eq_filter = input("Filtrar por equivalence_key (Enter para ignorar): ").strip()
        if not eq_filter:
            eq_filter = None
        items = api.list_items(source_id=source, equivalence_key=eq_filter)
        if not items:
            print("Nenhum item encontrado.")
            continue
        for idx, item in enumerate(items, start=1):
            headline = item.headline or "(sem headline)"
            print(f"{idx}. {item.item_id} | eq={item.equivalence_key} | state={item.state} | {headline}")
        selection = input("Escolha um item para ver detalhes ou Enter para voltar: ").strip()
        if not selection:
            continue
        try:
            selected_item = items[int(selection) - 1]
        except (ValueError, IndexError):
            print("Seleção inválida.")
            continue
        _show_item_detail(selected_item)
