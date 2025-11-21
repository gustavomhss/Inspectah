"""Cenários de âncoras e anti-canetada para gates T1/T4/T5/T6."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from inspectah.anchors import AnchorRecord, AnchorRegistry, Batcher
from inspectah.commands import OverrideViolation, apply_state_change, audit_trail
from inspectah.truthdb.models import BlocoTema, FatoRegistravel, TruthDB, VersaoFato
from inspectah.truthdb.state_machine import FactState


def _sample_truthdb() -> TruthDB:
    db = TruthDB()
    bloco = BlocoTema(
        bloco_id="bloco-anchor-demo",
        titulo="Auditoria de Âncoras",
        descricao_curta="Bloco de teste da S15",
        dominio="esporte",
        referencias_iniciais=["fonte1"],
        hash_conteudo="abc123",
    )
    db.register_bloco(bloco)
    fato = FatoRegistravel(
        fato_id="fato-anchor-1",
        bloco_id=bloco.bloco_id,
        resumo_fato="Título do campeonato X",
        descricao_detalhada="Quem venceu o campeonato X em 2023",
        estado_inicial=FactState.PLANEJADO,
        evidencias=["fonte1"],
        hash_conteudo="hash-fato-1",
        ancora_externa="",
    )
    db.register_fato(fato)
    return db


def run_anchor_and_guard_suite(evidence_dir: Path | None = None) -> Dict[str, object]:
    evidence_dir = evidence_dir or Path("out/evidence/S15_T1_contracts_and_states")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    anchors_dir = evidence_dir / "anchors"
    anchors_dir.mkdir(parents=True, exist_ok=True)

    db = _sample_truthdb()
    batcher = Batcher(max_entries=2)
    registry = AnchorRegistry(store_path=anchors_dir / "registry.json")

    versions = [
        VersaoFato(
            versao_id="v1",
            fato_id="fato-anchor-1",
            numero_versao=1,
            descricao="Placar inicial divulgado",
            estado=FactState.CONFIRMADO,
            evidencias=["fonte1"],
            hash_conteudo="hash-v1",
        ),
        VersaoFato(
            versao_id="v2",
            fato_id="fato-anchor-1",
            numero_versao=2,
            descricao="Recurso abriu disputa",
            estado=FactState.INCERTO,
            evidencias=["fonte2"],
            hash_conteudo="hash-v2",
        ),
    ]

    anchors: List[AnchorRecord] = []
    for version in versions:
        db.create_versao(version)
        batch_result = batcher.add_entry(f"{version.versao_id}:{version.descricao}")
        if batch_result:
            registry.register(
                AnchorRecord(
                    anchor_id=batch_result.anchor_id,
                    chain_id=batch_result.receipt.chain_id,
                    tx_hash=batch_result.receipt.tx_hash,
                    merkle_root=batch_result.merkle_root,
                    items=batch_result.items,
                ),
                facts=[version.fato_id],
            )
            anchors.append(registry.get(batch_result.anchor_id))  # type: ignore[arg-type]
    # Flush pending remainder
    if batcher.history:
        last_anchor = batcher.history[-1]
    else:
        last_anchor = batcher.flush()
        registry.register(
            AnchorRecord(
                anchor_id=last_anchor.anchor_id,
                chain_id=last_anchor.receipt.chain_id,
                tx_hash=last_anchor.receipt.tx_hash,
                merkle_root=last_anchor.merkle_root,
                items=last_anchor.items,
            ),
            facts=["fato-anchor-1"],
        )
        anchors.append(registry.get(last_anchor.anchor_id))  # type: ignore[arg-type]

    override_blocked = False
    try:
        apply_state_change(db, fact_id="fato-anchor-1", new_state="confirmado", cause={"override_request": True})
    except OverrideViolation:
        override_blocked = True

    apply_state_change(
        db,
        fact_id="fato-anchor-1",
        new_state="incerto",
        cause={"dispute_id": "d1", "reason": "disputa formal"},
        allow_override=False,
    )

    audit_path = evidence_dir / "override_log.json"
    audit_path.write_text(json.dumps(audit_trail(), indent=2), encoding="utf-8")
    registry_path = anchors_dir / "registry_snapshot.json"
    registry_path.write_text(json.dumps(registry.snapshot(), indent=2), encoding="utf-8")

    metrics = {
        "anchors_total": len(registry.snapshot().get("anchors", {})),
        "history_entries": len(batcher.history),
        "override_blocked": override_blocked,
        "override_log_entries": len(audit_trail()),
        "last_anchor_root": last_anchor.merkle_root if batcher.history else "",
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    (evidence_dir / "summary.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


__all__ = ["run_anchor_and_guard_suite"]
