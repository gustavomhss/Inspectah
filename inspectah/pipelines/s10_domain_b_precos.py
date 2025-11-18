from __future__ import annotations

from dataclasses import dataclass, field, asdict, is_dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Sequence, Tuple

from inspectah.truthdb.engine import TruthDBEngine
from inspectah.truthdb.models import TruthDB


@dataclass(frozen=True)
class ScenarioResult:
    name: str
    counts_for_success: bool
    valid_actions_sent: int
    valid_actions_accepted: int
    invalid_actions_sent: int
    invalid_actions_rejected: int
    success: bool
    audit_complete: bool
    errors: Tuple[str, ...] = ()
    snapshot: Dict[str, object] = field(default_factory=dict)
    truthdb: TruthDB | None = None

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data.pop("truthdb", None)
        return data


class DomainBPipeline:
    def __init__(self, engine_factory=None) -> None:
        self._engine_factory = engine_factory or TruthDBEngine

    def run_scenario(self, scenario: Dict[str, object], engine: TruthDBEngine | None = None) -> ScenarioResult:
        eng = engine or self._engine_factory()
        valid_sent = valid_acc = invalid_sent = invalid_rej = 0
        errors: List[str] = []

        for event in scenario["events"]:
            action_name, payload, expect_invalid = self._event_to_action(event)
            result = eng.apply(action_name, payload)
            if expect_invalid:
                invalid_sent += 1
                if not result.accepted:
                    invalid_rej += 1
                else:
                    errors.append(f"{event['type']} deveria ser rejeitado")
            else:
                valid_sent += 1
                if result.accepted:
                    valid_acc += 1
                else:
                    errors.append(f"{event['type']} rejeitado: {result.errors}")

        audit_complete = self._audit_complete(eng.truthdb, scenario.get("expected_facts", []))
        counts_for_success = bool(scenario.get("counts_for_success", True))
        if counts_for_success:
            success = not errors and valid_sent == valid_acc and audit_complete
        else:
            success = not errors and invalid_sent == invalid_rej

        snapshot = _serialize_truthdb(eng.truthdb)
        return ScenarioResult(
            name=scenario["name"],
            counts_for_success=counts_for_success,
            valid_actions_sent=valid_sent,
            valid_actions_accepted=valid_acc,
            invalid_actions_sent=invalid_sent,
            invalid_actions_rejected=invalid_rej,
            success=success,
            audit_complete=audit_complete,
            errors=tuple(errors),
            snapshot=snapshot,
            truthdb=eng.truthdb,
        )

    def run_demo_scenarios(self) -> Tuple[ScenarioResult, ...]:
        return tuple(self.run_scenario(scenario) for scenario in DOMAIN_B_SCENARIOS)

    def _event_to_action(self, event: Dict[str, object]) -> Tuple[str, Dict[str, object], bool]:
        etype = event["type"]
        expect_invalid = bool(event.get("expect_invalid"))
        if etype == "create_bloco":
            payload = {
                "id_bloco": event["id_bloco"],
                "titulo": event["titulo"],
                "descricao_curta": event["descricao_curta"],
                "dominio": event.get("dominio", "indices_precos"),
                "referencias_iniciais": event.get("referencias_iniciais", []),
                "meta": event.get("meta", {}),
            }
            action = "criar_bloco_tema"
        elif etype == "create_fato":
            payload = {
                "id_bloco": event["id_bloco"],
                "id_fato": event["id_fato"],
                "resumo_fato": event["resumo_fato"],
                "descricao_detalhada": event["descricao_detalhada"],
                "estado_inicial": event.get("estado_inicial", "planejado"),
                "evidencias": event.get("evidencias", []),
                "relatorio_simples": event.get("relatorio_simples", ""),
                "hash_conteudo": event.get("hash_conteudo", ""),
                "ancora_externa": event.get("ancora_externa", ""),
            }
            action = "criar_fato_registravel"
        elif etype == "create_versao":
            payload = {
                "id_fato": event["id_fato"],
                "versao_id": event["versao_id"],
                "numero_versao": event["numero_versao"],
                "descricao": event["descricao"],
                "estado": event.get("estado", "planejado"),
                "evidencias": event.get("evidencias", []),
                "hash_conteudo": event.get("hash_conteudo", ""),
            }
            action = "criar_versao_fato"
        elif etype == "update_estado":
            payload = {
                "id_fato": event["id_fato"],
                "estado_anterior": event.get("estado_anterior", "planejado"),
                "estado_novo": event["estado_novo"],
                "justificativa": event.get("justificativa", ""),
                "relatorio_simples": event.get("relatorio_simples", ""),
                "evidencias": event.get("evidencias", []),
            }
            action = "atualizar_estado_fato"
        else:
            raise ValueError(f"Evento desconhecido: {etype}")
        return action, payload, expect_invalid

    def _audit_complete(self, truthdb: TruthDB, fact_ids: Iterable[str]) -> bool:
        snapshot = truthdb.snapshot()
        versoes = snapshot["versoes"]
        estados = snapshot["estados"]
        for fid in fact_ids:
            has_version = any(v.fato_id == fid for v in versoes.values())
            if not has_version or fid not in estados:
                return False
        return bool(fact_ids)


def _serialize_truthdb(truthdb: TruthDB) -> Dict[str, object]:
    snapshot = truthdb.snapshot()
    return _convert_snapshot(snapshot)


def _convert_snapshot(value):
    if is_dataclass(value):
        return _convert_snapshot(asdict(value))
    if isinstance(value, dict):
        return {k: _convert_snapshot(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_convert_snapshot(v) for v in value]
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def summarize_results(results: Sequence[ScenarioResult]) -> Dict[str, float]:
    valid_sent = sum(r.valid_actions_sent for r in results)
    valid_acc = sum(r.valid_actions_accepted for r in results)
    invalid_sent = sum(r.invalid_actions_sent for r in results)
    invalid_rej = sum(r.invalid_actions_rejected for r in results)
    required = [r for r in results if r.counts_for_success]
    required_total = len(required)
    required_pass = sum(1 for r in required if r.success)
    audit_targets = required if required else results
    audit_ratio = (
        sum(1 for r in audit_targets if r.audit_complete) / len(audit_targets)
        if audit_targets
        else 1.0
    )
    valid_ratio = valid_acc / valid_sent if valid_sent else 1.0
    invalid_ratio = invalid_rej / invalid_sent if invalid_sent else 1.0
    scenario_rate = required_pass / required_total if required_total else 1.0
    return {
        "ratio_valid_actions_accepted": round(valid_ratio, 4),
        "ratio_invalid_actions_rejected": round(invalid_ratio, 4),
        "audit_trace_completeness": round(audit_ratio, 4),
        "e2e_scenario_success_rate": round(scenario_rate, 4),
        "scenarios_total": required_total,
        "scenarios_passed": required_pass,
    }


def run_demo_report() -> Dict[str, object]:
    pipeline = DomainBPipeline()
    results = pipeline.run_demo_scenarios()
    summary = summarize_results(results)
    return {"summary": summary, "results": [r.to_dict() for r in results]}


def build_domain_b_truthdb(engine: TruthDBEngine | None = None) -> TruthDB:
    scenario = next(s for s in DOMAIN_B_SCENARIOS if s.get("counts_for_success", True))
    pipeline = DomainBPipeline()
    result = pipeline.run_scenario(scenario, engine=engine)
    return result.truthdb  # type: ignore[return-value]


DOMAIN_B_SCENARIOS: Tuple[Dict[str, object], ...] = (
    {
        "name": "precos_media_confirmada",
        "counts_for_success": True,
        "expected_facts": ["preco_media_sp_julho"],
        "events": [
            {
                "type": "create_bloco",
                "id_bloco": "precos_sp",
                "titulo": "Índice de preços SP",
                "descricao_curta": "Monitoramento mensal",
                "dominio": "indices_precos",
                "referencias_iniciais": ["https://fonte/indice"],
            },
            {
                "type": "create_fato",
                "id_bloco": "precos_sp",
                "id_fato": "preco_media_sp_julho",
                "resumo_fato": "Média de julho",
                "descricao_detalhada": "Média ponderada de julho",
                "estado_inicial": "planejado",
                "evidencias": ["https://fonte/dados"],
                "relatorio_simples": "Estimativa baseada em dados",
                "hash_conteudo": "hash_preco_sp_julho",
                "ancora_externa": "ancora_preco_sp_julho",
            },
            {
                "type": "create_versao",
                "id_fato": "preco_media_sp_julho",
                "versao_id": "preco_sp_julho_v1",
                "numero_versao": 1,
                "descricao": "Estimativa inicial",
                "estado": "planejado",
                "evidencias": ["https://fonte/dados"],
                "hash_conteudo": "hash_versao_preco_sp_julho_v1",
            },
            {
                "type": "update_estado",
                "id_fato": "preco_media_sp_julho",
                "estado_anterior": "planejado",
                "estado_novo": "confirmado",
                "justificativa": "Dados oficiais publicados",
                "relatorio_simples": "Índice validado",
                "evidencias": ["https://fonte/diario_oficial"],
            },
        ],
    },
    {
        "name": "precos_fato_sem_bloco",
        "counts_for_success": False,
        "expected_facts": ["preco_sem_bloco"],
        "events": [
            {
                "type": "create_fato",
                "id_bloco": "bloco_inexistente",
                "id_fato": "preco_sem_bloco",
                "resumo_fato": "Fato inválido",
                "descricao_detalhada": "Este fato deve falhar",
                "estado_inicial": "planejado",
                "evidencias": ["https://fonte/erro"],
                "relatorio_simples": "Registro inválido",
                "hash_conteudo": "hash_invalido",
                "ancora_externa": "ancora_invalida",
                "expect_invalid": True,
            }
        ],
    },
)
