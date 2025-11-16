from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from .bundle import build_bundle, verify_bundle
from .collector import collect_once
from .config import load_domain_config, load_sources_config
from .metrics import snapshot_metrics
from .query_engine import export_results, format_table, load_canonical_records, run_query


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except Exception as exc:  # pragma: no cover - CLI guard
        print(f"[sprint6-cli] error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspectah Sprint 6 helper CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_sources = sub.add_parser("validate-sources")
    p_sources.add_argument("--domain", default="dominio_piloto")
    p_sources.add_argument("--output")
    p_sources.set_defaults(func=_cmd_validate_sources)

    p_fields = sub.add_parser("fields-preview")
    p_fields.add_argument("--domain", default="dominio_piloto")
    p_fields.add_argument("--source")
    p_fields.add_argument("--limit", type=int, default=5)
    p_fields.add_argument("--output")
    p_fields.set_defaults(func=_cmd_fields_preview)

    p_collect = sub.add_parser("collect")
    p_collect.add_argument("--domain", default="dominio_piloto")
    p_collect.add_argument("--output")
    p_collect.set_defaults(func=_cmd_collect)

    p_query = sub.add_parser("query")
    p_query.add_argument("--domain", default="dominio_piloto")
    p_query.add_argument("--from-date")
    p_query.add_argument("--to-date")
    p_query.add_argument("--categoria")
    p_query.add_argument("--regiao")
    p_query.add_argument("--fonte")
    p_query.add_argument("--search")
    p_query.add_argument("--page", type=int, default=1)
    p_query.add_argument("--page-size", type=int, default=10)
    p_query.add_argument("--format", choices=["table", "json", "csv"], default="table")
    p_query.add_argument("--export-prefix")
    p_query.add_argument("--meta-output")
    p_query.set_defaults(func=_cmd_query)

    p_show = sub.add_parser("show-evidence")
    p_show.add_argument("--domain", default="dominio_piloto")
    p_show.add_argument("item_id")
    p_show.set_defaults(func=_cmd_show_evidence)

    p_metrics = sub.add_parser("metrics")
    p_metrics.add_argument("--domain", default="dominio_piloto")
    p_metrics.set_defaults(func=_cmd_metrics)

    p_bundle = sub.add_parser("build-bundle")
    p_bundle.add_argument("--domain", default="dominio_piloto")
    p_bundle.set_defaults(func=_cmd_build_bundle)

    p_verify = sub.add_parser("verify-bundle")
    p_verify.set_defaults(func=_cmd_verify_bundle)

    return parser


def _cmd_validate_sources(args: argparse.Namespace) -> None:
    cfg = load_domain_config(args.domain)
    summary: Dict[str, Any] = {"domain": cfg.domain, "status": "PASS", "sources": {}}
    for source_id, source in load_sources_config(args.domain).items():
        exists = source.sample_file.exists()
        entry = {"sample_file": str(source.sample_file), "type": source.type, "exists": exists}
        if not exists:
            entry["error"] = "sample file missing"
            summary["status"] = "FAIL"
        summary["sources"][source_id] = entry
    _output_json(summary, args.output)


def _cmd_fields_preview(args: argparse.Namespace) -> None:
    from .collector import _canonicalize as canonicalize  # type: ignore[attr-defined]
    from .parsers import load_records

    cfg = load_domain_config(args.domain)
    payload = {"domain": cfg.domain, "samples": {}}
    for source_id, source in cfg.sources.items():
        if args.source and args.source != source_id:
            continue
        previews = []
        for record in load_records(source)[: args.limit]:
            canonical, errors = canonicalize(cfg, source, record)  # type: ignore[attr-defined]
            previews.append({"canonical": canonical, "errors": errors})
        payload["samples"][source_id] = {"records_analyzed": len(previews), "previews": previews}
    _output_json(payload, args.output)


def _cmd_collect(args: argparse.Namespace) -> None:
    summary = collect_once(args.domain)["summary"]
    _output_json(summary, args.output)


def _cmd_query(args: argparse.Namespace) -> None:
    result = run_query(
        args.domain,
        from_date=_parse_date(args.from_date),
        to_date=_parse_date(args.to_date),
        categoria=args.categoria,
        regiao=args.regiao,
        fonte=args.fonte,
        search=args.search,
        page=args.page,
        page_size=args.page_size,
    )
    if args.format == "json":
        print(json.dumps(result.items, indent=2, ensure_ascii=False))
    elif args.format == "csv":
        prefix = Path(args.export_prefix or f"out/queries/{args.domain}_query_{_timestamp()}")
        export_results(result.items, "csv", prefix.with_suffix(".csv"))
        print(f"[inspectah] csv salvo em {prefix.with_suffix('.csv')}")
    else:
        print(format_table(result.items))
    prefix = Path(args.export_prefix or f"out/queries/{args.domain}_query_{_timestamp()}")
    export_results(result.items, "json", prefix.with_suffix(".json"))
    export_results(result.items, "csv", prefix.with_suffix(".csv"))
    meta = {"domain": args.domain, "total": result.total, "page": result.page, "page_size": result.page_size, "export_prefix": str(prefix)}
    _output_json(meta, args.meta_output)


def _cmd_show_evidence(args: argparse.Namespace) -> None:
    records = load_canonical_records(args.domain)
    target = args.item_id
    selected = None
    evidence = None
    for record in records:
        if record.get("item_id") == target:
            selected = record
            break
        for entry in record.get("supporting_sources", []):
            if entry.get("item_id") == target:
                selected = record
                evidence = entry
                break
        if selected:
            break
    if not selected:
        raise ValueError(f"item {target} not found")
    evidence = evidence or selected.get("supporting_sources", [])[0]
    manifest = json.loads(Path(evidence["manifest_path"]).read_text(encoding="utf-8"))
    print(json.dumps({"record": selected, "manifest": manifest}, indent=2, ensure_ascii=False))


def _cmd_metrics(args: argparse.Namespace) -> None:
    payload = snapshot_metrics(args.domain)
    _output_json(payload["metrics"], None)


def _cmd_build_bundle(args: argparse.Namespace) -> None:
    payload = build_bundle(args.domain)
    _output_json(payload, None)


def _cmd_verify_bundle(_: argparse.Namespace) -> None:
    payload = verify_bundle()
    _output_json(payload, None)


def _output_json(data: Dict[str, Any], output: str | None) -> None:
    text = json.dumps(data, indent=2, ensure_ascii=False)
    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(text, encoding="utf-8")
    print(text)


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _timestamp() -> str:
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")


if __name__ == "__main__":  # pragma: no cover
    main()
