"""Cenários de ataque/stress reproduzíveis da Sprint 16."""
from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Mapping, MutableMapping, Sequence, Set

from inspectah.anchors.batcher import Batcher
from inspectah.anchors.chain_client import ChainClient
from inspectah.commands import OverrideViolation, apply_state_change
from inspectah.debunker.engine import analyze_claim, select_risky_claims
from inspectah.debunker.report_models import Recommendation, RiskLevel
from inspectah.committees.v1_validator import validate_submission
from inspectah.committees.v2_multibrain import run_v2_panel
from inspectah.committees.v3_coherence import check_coherence
from inspectah.truthdb.models import (
    BlocoTema,
    FatoRegistravel,
    TruthDB,
)
from inspectah.truthdb.state_machine import FactState


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    threat: str
    tags: Sequence[str]
    runner: Callable[[Path, bool], MutableMapping[str, object]]
    description: str


class _FlakyChain(ChainClient):
    """Chain que pode falhar de forma determinística para cenários de falha."""

    def __init__(self, chain_id: str = "testnet", fail_after: int = 0) -> None:
        super().__init__(chain_id=chain_id)
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
            bloco_id="b1",
            titulo="Bloco S16",
            descricao_curta="bloco para cenários de ataque",
            dominio="seguranca",
            referencias_iniciais=["r1"],
            hash_conteudo="abc",
        )
    )
    db.register_fato(
        FatoRegistravel(
            fato_id="f1",
            bloco_id="b1",
            resumo_fato="fato protegido",
            descricao_detalhada="cenario de teste",
            estado_inicial=FactState.INCERTO,
            evidencias=["ev1"],
            hash_conteudo="def",
            ancora_externa="anchor-x",
        )
    )
    return db


def _scenario_malicious_claim_high_risk(evidence_dir: Path, smoke: bool = False) -> MutableMapping[str, object]:
    claim = {
        "id": "claim-high-risk",
        "domain": "politica",
        "summary": "Alegação controversa com impacto alto e sem fonte",
        "impact": 0.95,
        "novelty": 0.8,
        "history_risk": 0.6,
        "evidence": [{"id": "ev-a", "stance": "against", "summary": "prova contrária"}],
    }
    report = analyze_claim(claim, context={"prior_disputes_ratio": 0.7})
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "malicious_claim_report.json").write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
    mitigated = report.risk is RiskLevel.HIGH and report.recommendation in {
        Recommendation.OPEN_DISPUTE,
        Recommendation.ESCALATE,
    }
    return {
        "scenario": "malicious_claim_high_risk",
        "status": "mitigated" if mitigated else "dangerous",
        "risk": report.risk.value,
        "recommendation": report.recommendation.value,
    }


def _scenario_contradictory_evidence_detection(evidence_dir: Path, smoke: bool = False) -> MutableMapping[str, object]:
    claim = {
        "id": "claim-contradiction",
        "domain": "esporte",
        "summary": "Relato incoerente com fontes divergentes",
        "impact": 0.6,
        "novelty": 0.4,
        "evidence": [
            {"id": "ev-for", "stance": "for", "summary": "fonte alinhada"},
            {"id": "ev-against", "stance": "against", "summary": "fonte discordante"},
        ],
    }
    report = analyze_claim(claim)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "contradiction_report.json").write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
    contradictions = len(report.contradictions)
    recommendation_safe = report.recommendation in {Recommendation.QUESTIONED, Recommendation.OPEN_DISPUTE, Recommendation.ESCALATE}
    return {
        "scenario": "contradictory_evidence_detection",
        "status": "mitigated" if contradictions and recommendation_safe else "dangerous",
        "contradictions": contradictions,
        "recommendation": report.recommendation.value,
    }


def _scenario_committee_capture_low_evidence(evidence_dir: Path, smoke: bool = False) -> MutableMapping[str, object]:
    submission = {
        "case_id": "capture-low-evidence",
        "fact_id": "f1",
        "domain": "politica",
        "current_state": "incerto",
        "proposed_state": "confirmado",
        "evidence_count": 0,
        "claim": {
            "id": "claim-low-ev",
            "domain": "politica",
            "summary": "Promover estado sensível sem suporte",
            "impact": 0.8,
            "novelty": 0.3,
            "evidence": [],
        },
        "related": [],
    }
    v1 = validate_submission(dict(submission))
    report = analyze_claim(submission["claim"])
    v2 = run_v2_panel(submission, report)
    v3 = check_coherence(submission, submission.get("related", []))

    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "committee_capture.json").write_text(
        json.dumps(
            {
                "v1": v1.to_dict(),
                "v2": v2.to_dict(),
                "v3": v3.to_dict(),
                "debunker": report.to_dict(),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    blocked = v1.status.value == "rejected" or v2.status.value in {"need_more_evidence", "escalate"} or v3.status.value == "blocked"
    return {
        "scenario": "committee_capture_low_evidence",
        "status": "mitigated" if blocked else "dangerous",
        "v1": v1.status.value,
        "v2": v2.status.value,
        "v3": v3.status.value,
    }


def _scenario_override_without_dispute(evidence_dir: Path, smoke: bool = False) -> MutableMapping[str, object]:
    db = _bootstrap_db()
    evidence_dir.mkdir(parents=True, exist_ok=True)
    result: Dict[str, object] = {"scenario": "override_without_dispute"}
    try:
        apply_state_change(db, fact_id="f1", new_state="confirmado", cause={"motivo": "forcar"})
    except OverrideViolation as exc:
        result.update({"status": "mitigated", "reason": str(exc)})
    else:
        result.update({"status": "dangerous", "reason": "override_permitido_sem_disputa"})
    (evidence_dir / "anti_canetada.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def _scenario_anchor_chain_failure(evidence_dir: Path, smoke: bool = False) -> MutableMapping[str, object]:
    chain = _FlakyChain(fail_after=0 if smoke else 1)
    batcher = Batcher(max_entries=2, chain=chain)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    outcomes: List[Dict[str, object]] = []
    status = "mitigated"
    for idx in range(3 if not smoke else 2):
        try:
            batcher.add_entry(f"fact-{idx}")
            result = batcher.flush()
            outcomes.append({"anchor_id": result.anchor_id, "merkle_root": result.merkle_root, "status": "anchored"})
        except Exception as exc:  # noqa: BLE001
            status = "detected_failure"
            outcomes.append({"error": str(exc), "pending": True})
    (evidence_dir / "anchor_chain_failure.json").write_text(json.dumps(outcomes, indent=2), encoding="utf-8")
    return {"scenario": "anchor_chain_failure", "status": status, "attempts": len(outcomes)}


def _scenario_dispute_flood(evidence_dir: Path, smoke: bool = False) -> MutableMapping[str, object]:
    claims = [
        {
            "id": f"flood-{idx}",
            "domain": "esporte",
            "impact": 0.4 + (0.1 * (idx % 3)),
            "novelty": 0.3,
            "history_risk": 0.2,
            "evidence": [{"stance": "against", "summary": "spam"}] if idx % 4 == 0 else [],
        }
        for idx in range(20 if not smoke else 8)
    ]
    start = time.perf_counter()
    risky = select_risky_claims(claims)
    elapsed = time.perf_counter() - start
    throughput = len(claims) / elapsed if elapsed else float("inf")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "dispute_flood.json").write_text(
        json.dumps({"total": len(claims), "risky": len(risky), "elapsed": elapsed, "throughput": throughput}, indent=2),
        encoding="utf-8",
    )
    status = "mitigated" if throughput > 50 and len(risky) >= len(claims) * 0.2 else "degraded"
    return {"scenario": "dispute_flood", "status": status, "throughput": round(throughput, 3), "risky_detected": len(risky)}


SCENARIOS: List[Scenario] = [
    Scenario(
        scenario_id="malicious_claim_high_risk",
        threat="envenenamento_de_claim",
        tags=("debunker", "attack", "t3"),
        runner=_scenario_malicious_claim_high_risk,
        description="Claim malicioso com impacto alto deve ser marcado como risco alto e escalado.",
    ),
    Scenario(
        scenario_id="contradictory_evidence_detection",
        threat="contradicao_de_evidencias",
        tags=("debunker", "committee", "t3"),
        runner=_scenario_contradictory_evidence_detection,
        description="Claims com evidências conflitantes devem virar questioned/dispute.",
    ),
    Scenario(
        scenario_id="committee_capture_low_evidence",
        threat="captura_de_comite",
        tags=("committee", "attack", "t3"),
        runner=_scenario_committee_capture_low_evidence,
        description="Comitês precisam rejeitar ou escalar submissão sem evidência.",
    ),
    Scenario(
        scenario_id="override_without_dispute",
        threat="bypass_anti_canetada",
        tags=("commands", "anchors", "t4"),
        runner=_scenario_override_without_dispute,
        description="Override direto deve ser bloqueado e registrado.",
    ),
    Scenario(
        scenario_id="anchor_chain_failure",
        threat="falha_de_chain",
        tags=("anchors", "commands", "t4"),
        runner=_scenario_anchor_chain_failure,
        description="Âncoras precisam registrar falha de chain sem corromper histórico.",
    ),
    Scenario(
        scenario_id="dispute_flood",
        threat="negacao_de_servico",
        tags=("stress", "t5", "debunker"),
        runner=_scenario_dispute_flood,
        description="Flood de disputas deve ser identificado com throughput mínimo aceitável.",
    ),
]


def list_scenarios(tags: Iterable[str] | None = None) -> List[Dict[str, object]]:
    tag_set: Set[str] = {t.lower() for t in tags} if tags else set()
    data = []
    for scenario in SCENARIOS:
        if tag_set and not tag_set.intersection({t.lower() for t in scenario.tags}):
            continue
        data.append(
            {
                "id": scenario.scenario_id,
                "threat": scenario.threat,
                "tags": list(scenario.tags),
                "description": scenario.description,
            }
        )
    return data


def run_scenarios(
    scenario_ids: Iterable[str] | None = None,
    *,
    tags: Iterable[str] | None = None,
    evidence_dir: Path | None = None,
    smoke: bool = False,
) -> Dict[str, object]:
    evidence_dir = evidence_dir or Path("out/evidence/S16_T2_attack_scenarios")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    selected: List[Scenario] = []
    id_set = {sid for sid in scenario_ids} if scenario_ids else set()
    tag_set = {t.lower() for t in tags} if tags else set()
    for scenario in SCENARIOS:
        if id_set and scenario.scenario_id not in id_set:
            continue
        if tag_set and not tag_set.intersection({t.lower() for t in scenario.tags}):
            continue
        selected.append(scenario)

    results: List[Dict[str, object]] = []
    for scenario in selected:
        scenario_dir = evidence_dir / scenario.scenario_id
        try:
            res = scenario.runner(scenario_dir, smoke)
            status = res.get("status", "unknown")
        except Exception as exc:  # noqa: BLE001
            status = "error"
            res = {"scenario": scenario.scenario_id, "status": status, "error": str(exc)}
        res["id"] = scenario.scenario_id
        res["tags"] = list(scenario.tags)
        res["threat"] = scenario.threat
        results.append(res)

    manifest = {
        "total": len(selected),
        "results": results,
        "smoke": smoke,
    }
    (evidence_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Cenários de ataque da Sprint 16")
    parser.add_argument("--list", action="store_true", help="Listar cenários disponíveis")
    parser.add_argument("--run-all", action="store_true", help="Rodar todos os cenários")
    parser.add_argument("--run", nargs="*", help="IDs específicos para rodar")
    parser.add_argument("--tags", nargs="*", help="Filtrar cenários por tag")
    parser.add_argument("--evidence-dir", default="out/evidence/S16_T2_attack_scenarios", help="Diretório de evidências")
    parser.add_argument("--smoke", action="store_true", help="Modo rápido")
    args = parser.parse_args()

    if args.list and not args.run_all and not args.run:
        print(json.dumps(list_scenarios(args.tags), indent=2))
        return

    if not args.run_all and not args.run:
        parser.error("Use --run-all ou --run <ids> para executar cenários.")

    manifest = run_scenarios(
        scenario_ids=args.run,
        tags=args.tags,
        evidence_dir=Path(args.evidence_dir),
        smoke=args.smoke,
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
