"""Testes de âncoras e anti-canetada sob falha."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

from inspectah.anchors.batcher import Batcher
from inspectah.anchors.chain_client import ChainClient
from inspectah.anchors.registry import AnchorRecord, AnchorRegistry
from inspectah.commands import OverrideViolation, apply_state_change, audit_trail
from inspectah.truthdb.models import BlocoTema, FatoRegistravel, TruthDB
from inspectah.truthdb.state_machine import FactState


class _FlakyChain(ChainClient):
    def __init__(self, *, fail_after: int = 0) -> None:
        super().__init__(chain_id="testnet-flaky")
        self._fail_after = fail_after
        self._calls = 0

    def submit_anchor(self, merkle_root: str):
        self._calls += 1
        if self._calls > self._fail_after:
            raise RuntimeError("chain_unavailable")
        return super().submit_anchor(merkle_root)


def _bootstrap_db() -> TruthDB:
    db = TruthDB()
    db.register_bloco(
        BlocoTema(
            bloco_id="b-anchor",
            titulo="Bloco de teste S16",
            descricao_curta="teste de âncoras",
            dominio="seguranca",
            referencias_iniciais=["ref"],
            hash_conteudo="hash",
        )
    )
    db.register_fato(
        FatoRegistravel(
            fato_id="f-anchor",
            bloco_id="b-anchor",
            resumo_fato="fato protegido",
            descricao_detalhada="cadeia de teste",
            estado_inicial=FactState.INCERTO,
            evidencias=["ev"],
            hash_conteudo="hash2",
            ancora_externa="",
        )
    )
    return db


def run_tests(evidence_dir: Path | None = None, *, smoke: bool = False) -> Dict[str, object]:
    evidence_dir = evidence_dir or Path("out/evidence/S16_T4_anchors_and_anti_canetada")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    registry = AnchorRegistry()
    chain = _FlakyChain(fail_after=0 if smoke else 1)
    batcher = Batcher(max_entries=2, chain=chain)
    anchor_records: List[Dict[str, object]] = []
    failures = 0

    for idx in range(3 if not smoke else 2):
        try:
            batcher.add_entry(f"fact-{idx}")
            batch = batcher.flush()
            record = AnchorRecord(
                anchor_id=batch.anchor_id,
                chain_id=batch.receipt.chain_id,
                tx_hash=batch.receipt.tx_hash,
                merkle_root=batch.merkle_root,
                items=batch.items,
                metadata={"submitted_at": batch.receipt.submitted_at.isoformat()},
            )
            registry.register(record, facts=batch.items)
            anchor_records.append(record.to_dict())
        except Exception as exc:  # noqa: BLE001
            failures += 1
            anchor_records.append({"error": str(exc), "items": list(batcher.pending_items)})

    (evidence_dir / "anchors.json").write_text(json.dumps(anchor_records, indent=2), encoding="utf-8")

    db = _bootstrap_db()
    pre_log = len(audit_trail())
    override_results: List[Dict[str, object]] = []
    try:
        apply_state_change(db, fact_id="f-anchor", new_state="confirmado", cause={"motivo": "forcar"})
    except OverrideViolation as exc:
        override_results.append({"attempt": "blocked", "reason": str(exc)})
    else:
        override_results.append({"attempt": "danger", "reason": "override_permitido"})

    apply_state_change(
        db,
        fact_id="f-anchor",
        new_state="confirmado",
        cause={"claim_id": "claim-safe", "override_request": True},
        allow_override=True,
    )
    post_log = len(audit_trail())
    override_results.append({"attempt": "formal", "reason": "via_fluxo_formal"})
    (evidence_dir / "anti_canetada.json").write_text(json.dumps(override_results, indent=2), encoding="utf-8")

    status = "PASS"
    notes = []
    if failures == 0:
        notes.append("Nenhuma falha de chain simulada detectada")
    if pre_log == post_log:
        notes.append("Trilha de anti-canetada não registrou as tentativas")
    if any(item.get("attempt") == "danger" for item in override_results):
        status = "FAIL"
        notes.append("Override passou sem disputa")
    if not anchor_records:
        status = "FAIL"
        notes.append("Nenhum batch de âncoras processado")

    manifest = {
        "status": status,
        "anchors": anchor_records,
        "anchor_failures": failures,
        "override_events_recorded": post_log - pre_log,
        "notes": notes,
    }
    (evidence_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Âncoras e anti-canetada sob falha (S16)")
    parser.add_argument("--evidence-dir", default="out/evidence/S16_T4_anchors_and_anti_canetada")
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    result = run_tests(Path(args.evidence_dir), smoke=args.smoke)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
