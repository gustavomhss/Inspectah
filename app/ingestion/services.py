from __future__ import annotations

import hashlib
import logging
import os
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Callable, Dict, List, Optional, Tuple

from app.ingestion import state_machine
from app.ingestion.errors import (
    ConfigDisabledError,
    ConfigNotFoundError,
    InvalidTransitionError,
    ModeIncompatibleError,
    RunInProgressError,
    RunNotFoundError,
    SourceNotEligibleError,
    SourceNotFoundError,
)
from app.ingestion.models import (
    IngestionConfig,
    IngestionMode,
    IngestionRun,
    IngestionStatus,
    IngestionTrigger,
    MIN_INTERVAL,
    validate_run_invariants,
)
from app.ingestion.repository import IngestionRepository
from app.ingestion import observability
from app.ingestion.providers.news_provider_client import NewsProviderClient, RawNewsItem
from app.sources.models import Source, SourceState
from app.sources.service import get_source_detail
from app.providers.models import IngestionProfile, ProfileKind, ProviderStatus
from metrics import newsdata_ingest
from inspectah.watchers.rss import _fetch_feed as _fetch_rss_feed, _parse_rss as _parse_rss_feed

logger = logging.getLogger(__name__)

NEWS_DATA_DOMAINS = [
    "g1.globo.com",
    "folha.uol.com.br",
    "estadao.com.br",
    "valor.globo.com",
    "infomoney.com.br",
    "agenciabrasil.ebc.com.br",
    "correiobraziliense.com.br",
    "gazetadopovo.com.br",
    "nsctotal.com.br",
    "correiodopovo.com.br",
    "diariodonordeste.verdesmares.com.br",
    "atarde.com.br",
    "diariodopara.dol.com.br",
    "adrenaline.com.br",
    "lance.com.br",
]


def _gen_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def _assert_source_available(source: Optional[Source], expected_id: str) -> Source:
    if source is None or source.id != expected_id:
        raise SourceNotFoundError("Fonte não encontrada.")
    if source.state in {SourceState.DISABLED_PERM, SourceState.DISABLED_TEMP}:
        raise SourceNotEligibleError("Fonte desabilitada para ingestão.")
    return source


def _build_newsdata_profile() -> IngestionProfile:
    return IngestionProfile.create(
        id="profile_newsdata_br",
        provider_id="newsdata",
        name="newsdata.io Brasil",
        slug="newsdata_br",
        kind=ProfileKind.NEWS,
        country="br",
        language="pt",
        categories=[],
        keywords=[],
        filters={"domainurl": ",".join(NEWS_DATA_DOMAINS)},
        frequency_minutes=60,
        enabled=True,
        status=ProviderStatus.ACTIVE,
    )


def _newsdata_hash(entry: Dict) -> str:
    raw = "|".join(
        [
            str(entry.get("id", "")),
            entry.get("title") or "",
            entry.get("link") or "",
            entry.get("pubDate") or "",
            entry.get("source_id") or "",
            ",".join(entry.get("category") or []),
            entry.get("description") or entry.get("content") or "",
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _dedup_newsdata_items(items: List[RawNewsItem]) -> Tuple[List[Dict], int]:
    seen = set()
    deduped: List[Dict] = []
    duplicates = 0
    for item in items:
        key = (item.external_id, item.url, item.published_at)
        if key in seen:
            duplicates += 1
            continue
        seen.add(key)
        payload = {
            "id": item.external_id,
            "title": item.title,
            "link": item.url,
            "pubDate": item.published_at,
            "source_id": item.source_name,
            "category": item.categories,
            "description": item.summary,
            "language": item.language,
            "country": item.country,
            "raw": item.payload,
        }
        payload["hash"] = _newsdata_hash(payload)
        deduped.append(payload)
    return deduped, duplicates


async def run_newsdata_ingestion(
    *,
    trigger_origin: str = "ops_api",
    repo: Optional[IngestionRepository] = None,
    size: int = 50,
    throttle_seconds: float = 1.0,
    max_attempts: int = 3,
    domains_override: Optional[List[str]] = None,
) -> IngestionRun:
    """
    Ingestão real do newsdata.io com throttling/backoff e persistência (G4).
    - Fonte fixa: newsdata_br
    - RBAC: endpoint deve validar role externamente (ops_ingest)
    """
    repo = repo or IngestionRepository()
    source_id = "newsdata_br"
    now = datetime.now(timezone.utc)
    recent = repo.list_runs_by_source_between(source_id, now - timedelta(minutes=1), now)
    if len(recent) >= 3:
        raise RunInProgressError("Limite de 3 runs/min para newsdata_br excedido")
    runs_today = repo.list_runs_by_source_between(source_id, now - timedelta(days=1), now)
    daily_requests = sum(len((r.meta or {}).get("attempts", [])) or 0 for r in runs_today)
    if daily_requests >= 1000:
        raise RunInProgressError("Quota diária de 1000 requisições excedida para newsdata_br")
    config = repo.get_config(source_id) or IngestionConfig.create(
        id=_gen_id("cfg"),
        source_id=source_id,
        source_state=SourceState.ACTIVE,
        enabled=True,
        mode=IngestionMode.MANUAL_ONLY,
        interval_minutes=60,
        max_attempts=3,
        timeout_seconds=60,
        created_by="ops_ingest",
    )
    if not repo.get_config(source_id):
        repo.save_config(config)

    run = IngestionRun.create(
        id=_gen_id("run"),
        config=config,
        trigger=IngestionTrigger.MANUAL,
        status=IngestionStatus.RUNNING,
        meta={"trigger_origin": trigger_origin},
    )
    repo.insert_run(run)
    repo.set_last_run(config.id, run.id)
    observability.log_run_start(run)

    api_key = os.environ.get("NEWSDATA_API_KEY")
    if not api_key:
        raise ValueError("NEWSDATA_API_KEY environment variable must be set")
    base_url = os.environ.get("NEWSDATA_BASE_URL", "https://newsdata.io/api/1")
    profile = _build_newsdata_profile()
    client = NewsProviderClient(api_key=api_key, base_url=base_url)
    domains = domains_override or NEWS_DATA_DOMAINS
    requested_size = size
    per_request_size = min(max(size, 1), 10)  # newsdata aceita até 10 itens por requisição
    size = min(max(size, 1), 50)
    attempt_log: List[dict] = []

    start_time = time.time()
    try:
        all_items: List[RawNewsItem] = []
        for i in range(0, len(domains), 5):
            batch = domains[i : i + 5]
            raw_items = await client.fetch(
                profile,
                size=per_request_size,
                domains=batch,
                throttle_seconds=throttle_seconds,
                max_attempts=max_attempts,
                attempt_log=attempt_log,
            )
            all_items.extend(raw_items)
        deduped, duplicates = _dedup_newsdata_items(all_items)
        payload_ref = repo.save_raw_payload(run.id, source_id, deduped)
        duration = time.time() - start_time
        newsdata_ingest.record_request(source_id, "success", duration_seconds=duration)
        newsdata_ingest.record_items(source_id, len(deduped))
        _mark_run_success(repo, run, items_processed=len(deduped), payload_ref=payload_ref)
        run.meta.update(
            {
                "fetched": len(all_items),
                "deduped": len(deduped),
                "duplicates": duplicates,
                "domains": domains,
                "throttle_seconds": throttle_seconds,
                "max_attempts": max_attempts,
                "payload_ref": payload_ref,
                "items_sample": deduped[:5],
                "duration_seconds": duration,
                "attempts": attempt_log,
                "size": size,
                "requested_size": requested_size,
                "per_request_size": per_request_size,
                "trigger_origin": trigger_origin,
                "requests_count": len(attempt_log),
            }
        )
        repo.update_run(run)
        return run
    except Exception as exc:  # noqa: BLE001
        error_type = getattr(exc, "__class__", type("obj", (), {})).__name__.lower()
        newsdata_ingest.record_request(source_id, "error")
        newsdata_ingest.record_error(source_id, error_type)
        run.meta.update(
            {
                "domains": domains,
                "throttle_seconds": throttle_seconds,
                "max_attempts": max_attempts,
                "attempts": attempt_log,
                "size": size,
                "requested_size": requested_size,
                "per_request_size": per_request_size,
                "trigger_origin": trigger_origin,
                "error_type": error_type,
                "requests_count": len(attempt_log),
            }
        )
        repo.update_run(run)
        _mark_run_fail(
            repo,
            run,
            error_code=error_type,
            error_message=str(exc),
            items_processed=0,
            payload_ref=None,
        )
        raise


def _ensure_config_allows_trigger(config: IngestionConfig, trigger: IngestionTrigger) -> None:
    if not config.enabled:
        raise ConfigDisabledError("Config de ingestão desabilitada.")
    if trigger == IngestionTrigger.AUTOMATIC and config.mode != IngestionMode.AUTOMATIC:
        raise ModeIncompatibleError("Config em modo manual não aceita trigger automático.")


def start_ingestion_run(
    source_id: str,
    *,
    trigger: IngestionTrigger = IngestionTrigger.MANUAL,
    trigger_origin: str = "manual",
    repo: Optional[IngestionRepository] = None,
    source_fetcher: Callable[[str], Optional[Source]] = get_source_detail,
    execute_inline: bool = False,
) -> IngestionRun:
    repo = repo or IngestionRepository()
    source = _assert_source_available(source_fetcher(source_id), source_id)
    config = _get_or_create_config(repo, source)
    _ensure_config_allows_trigger(config, trigger)
    if repo.count_running_for_source(source_id) > 0:
        raise RunInProgressError("Já existe run em andamento para esta fonte.")

    run = IngestionRun.create(
        id=_gen_id("run"),
        config=config,
        trigger=trigger,
        status=IngestionStatus.RUNNING,
        meta={"trigger_origin": trigger_origin},
    )
    repo.insert_run(run)
    repo.set_last_run(config.id, run.id)
    observability.log_run_start(run)

    if execute_inline:
        _log_run_event(run, "run_inline_started", {"note": "Execução inline real (rss) se suportada"})
        try:
            items_processed, payload_ref = _run_ingestion_inline(repo, run, source)
            _mark_run_success(repo, run, items_processed=items_processed, payload_ref=payload_ref)
            _log_run_event(
                run,
                "run_inline_finished",
                {"items_processed": items_processed, "payload_ref": payload_ref},
            )
        except Exception as exc:  # noqa: BLE001
            _mark_run_fail(repo, run, error_code="inline_error", error_message=str(exc))
            _log_run_event(run, "run_inline_failed", extra={"error": str(exc)})
            raise

    return run


def complete_ingestion_run(
    run_id: str,
    *,
    items_processed: int,
    payload_ref: str,
    repo: Optional[IngestionRepository] = None,
) -> IngestionRun:
    repo = repo or IngestionRepository()
    run = repo.get_run(run_id)
    if not run:
        raise RunNotFoundError(f"Run {run_id} não encontrado.")
    config = repo.get_config(run.source_id)
    if not config:
        raise ConfigNotFoundError(f"Nenhuma config para fonte {run.source_id}")
    if run.status != IngestionStatus.RUNNING:
        raise InvalidTransitionError("Só é possível completar runs em RUNNING.")

    state_machine.apply_event(run, state_machine.IngestionEvent.COMPLETE)
    run.finished_at = datetime.now(timezone.utc)
    run.items_processed = items_processed
    run.payload_ref = payload_ref
    validate_run_invariants(run, config)
    repo.update_run(run)
    repo.set_last_run(config.id, run.id)
    observability.log_run_end(run)
    logger.info(
        "[ingestion_run_success] run_id=%s source_id=%s items_processed=%s payload_ref=%s",
        run.id,
        run.source_id,
        items_processed,
        payload_ref,
    )
    return run


def fail_ingestion_run(
    run_id: str,
    *,
    error_code: str,
    error_message: str,
    payload_ref: Optional[str] = None,
    partial: bool = False,
    items_processed: int = 0,
    repo: Optional[IngestionRepository] = None,
) -> IngestionRun:
    repo = repo or IngestionRepository()
    run = repo.get_run(run_id)
    if not run:
        raise RunNotFoundError(f"Run {run_id} não encontrado.")
    config = repo.get_config(run.source_id)
    if not config:
        raise ConfigNotFoundError(f"Nenhuma config para fonte {run.source_id}")

    event = state_machine.IngestionEvent.PARTIAL_COMPLETE if partial else state_machine.IngestionEvent.ERROR
    state_machine.apply_event(run, event)
    run.finished_at = datetime.now(timezone.utc)
    run.error_code = error_code
    run.error_message = error_message
    run.payload_ref = payload_ref
    run.items_processed = items_processed
    validate_run_invariants(run, config)
    repo.update_run(run)
    repo.set_last_run(config.id, run.id)
    observability.log_run_end(run)
    logger.warning(
        "[ingestion_run_fail] run_id=%s source_id=%s items_processed=%s error_code=%s error_message=%s",
        run.id,
        run.source_id,
        items_processed,
        error_code,
        error_message,
    )
    return run


def reprocess_run(
    run_id: str,
    *,
    repo: Optional[IngestionRepository] = None,
    source_fetcher: Callable[[str], Optional[Source]] = get_source_detail,
) -> IngestionRun:
    repo = repo or IngestionRepository()
    previous = repo.get_run(run_id)
    if not previous:
        raise RunNotFoundError(f"Run {run_id} não encontrado para reprocessar.")
    config = repo.get_config(previous.source_id)
    if not config:
        raise ConfigNotFoundError(f"Nenhuma config para fonte {previous.source_id}")
    _assert_source_available(source_fetcher(previous.source_id), previous.source_id)
    _ensure_config_allows_trigger(config, IngestionTrigger.MANUAL)
    if repo.count_running_for_source(previous.source_id) > 0:
        raise RunInProgressError("Já existe run em andamento; aguarde para reprocessar.")

    new_run = IngestionRun.create(
        id=_gen_id("run"),
        config=config,
        trigger=IngestionTrigger.REPROCESS,
        status=IngestionStatus.RUNNING,
        meta={"reprocess_of": run_id},
    )
    repo.insert_run(new_run)
    repo.set_last_run(config.id, new_run.id)
    observability.log_run_start(new_run)
    return new_run


def toggle_ingestion_mode(
    source_id: str,
    *,
    new_mode: IngestionMode,
    enabled: bool,
    updated_by: str,
    repo: Optional[IngestionRepository] = None,
    source_fetcher: Callable[[str], Optional[Source]] = get_source_detail,
) -> IngestionConfig:
    repo = repo or IngestionRepository()
    source = _assert_source_available(source_fetcher(source_id), source_id)
    config = repo.get_config(source_id)
    if not config:
        # cria config básica se não existir
        config = _create_default_config(source, new_mode, enabled, updated_by)
        return repo.save_config(config)

    config.mode = new_mode
    config.enabled = enabled
    config.updated_by = updated_by
    config.updated_at = datetime.now(timezone.utc)
    if enabled:
        _ensure_config_allows_trigger(config, IngestionTrigger.MANUAL if new_mode == IngestionMode.MANUAL_ONLY else IngestionTrigger.AUTOMATIC)
    return repo.save_config(config)


def _create_default_config(source: Source, mode: IngestionMode, enabled: bool, created_by: str) -> IngestionConfig:
    return IngestionConfig.create(
        id=_gen_id("ingcfg"),
        source_id=source.id,
        source_state=source.state,
        enabled=enabled,
        mode=mode,
        interval_minutes=source.refresh_interval if getattr(source, "refresh_interval", None) else MIN_INTERVAL,
        max_attempts=3,
        timeout_seconds=60,
        created_by=created_by,
    )


def _get_or_create_config(repo: IngestionRepository, source: Source) -> IngestionConfig:
    existing = repo.get_config(source.id)
    if existing:
        return existing
    cfg = _create_default_config(source, IngestionMode.MANUAL_ONLY, True, "admin_ui")
    return repo.save_config(cfg)


def _log_run_event(run: IngestionRun, event: str, extra: Optional[dict] = None) -> None:
    payload = {
        "event": event,
        "run_id": run.id,
        "source_id": run.source_id,
        "status": run.status.value,
        "started_at": run.started_at.isoformat(),
        "finished_at": run.finished_at.isoformat() if run.finished_at else None,
    }
    if extra:
        payload.update(extra)
    logger.info("[ingestion_run] %s", payload)


def _run_ingestion_inline(repo: IngestionRepository, run: IngestionRun, source: Source) -> tuple[int, Optional[str]]:
    if source.format != "rss":
        logger.info(
            "[ingestion_inline_skip] run_id=%s source_id=%s reason=unsupported_format format=%s",
            run.id,
            run.source_id,
            source.format,
        )
        return 0, None

    logger.info(
        "[ingestion_inline_fetch] run_id=%s source_id=%s endpoint=%s",
        run.id,
        run.source_id,
        source.endpoint,
    )
    feed_bytes = _fetch_rss_feed(source.endpoint)
    items = _parse_rss_feed(feed_bytes)
    total = len(items)
    if total == 0:
        logger.warning(
            "[ingestion_inline_no_items] run_id=%s source_id=%s endpoint=%s",
            run.id,
            run.source_id,
            source.endpoint,
        )
    payload_ref = repo.save_raw_payload(run.id, run.source_id, items)
    logger.info(
        "[ingestion_inline_parsed] run_id=%s source_id=%s items=%s payload_ref=%s",
        run.id,
        run.source_id,
        total,
        payload_ref,
    )
    return total, payload_ref


def _mark_run_success(repo: IngestionRepository, run: IngestionRun, *, items_processed: int, payload_ref: Optional[str]) -> IngestionRun:
    state_machine.apply_event(run, state_machine.IngestionEvent.COMPLETE)
    run.finished_at = datetime.now(timezone.utc)
    run.items_processed = items_processed
    run.payload_ref = payload_ref
    repo.update_run(run)
    repo.set_last_run(run.config_id, run.id)
    observability.log_run_end(run)
    logger.info(
        "[ingestion_run_success] run_id=%s source_id=%s items_processed=%s payload_ref=%s",
        run.id,
        run.source_id,
        items_processed,
        payload_ref,
    )
    return run


def _mark_run_fail(
    repo: IngestionRepository,
    run: IngestionRun,
    *,
    error_code: str,
    error_message: str,
    payload_ref: Optional[str] = None,
    items_processed: int = 0,
) -> IngestionRun:
    state_machine.apply_event(run, state_machine.IngestionEvent.ERROR)
    run.finished_at = datetime.now(timezone.utc)
    run.error_code = error_code
    run.error_message = error_message
    run.payload_ref = payload_ref
    run.items_processed = items_processed
    repo.update_run(run)
    repo.set_last_run(run.config_id, run.id)
    observability.log_run_end(run)
    return run
