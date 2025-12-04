from __future__ import annotations

import importlib
import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from app.flows.models import (
    Flow,
    FlowExecution,
    FlowExecutionStatus,
    FlowOperationLog,
    FlowState,
    FlowStep,
    FlowStepExecution,
    FlowStepExecutionStatus,
    FlowStepType,
    FlowTemplate,
)

flow_schema = importlib.import_module("migrations.versions.0030_s30_flow_model_v15")
flow_templates = importlib.import_module("migrations.versions.0031_s30_flow_templates_seed")

DEFAULT_DB_PATH = flow_schema.DEFAULT_DB_PATH

ALLOWED_TRANSITIONS: Dict[FlowState, List[FlowState]] = {
    FlowState.DRAFT: [FlowState.EM_TESTE],
    FlowState.EM_TESTE: [FlowState.ATIVO, FlowState.PAUSADO],
    FlowState.ATIVO: [FlowState.PAUSADO, FlowState.DEPRECADO],
    FlowState.PAUSADO: [FlowState.ATIVO, FlowState.DEPRECADO],
    FlowState.DEPRECADO: [],
}


def _generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


def _json_dump(payload: Dict) -> str:
    return json.dumps(payload or {}, ensure_ascii=False)


def _json_load(payload: Optional[str]) -> Dict:
    if payload is None:
        return {}
    try:
        return json.loads(payload)
    except Exception:
        return {}


class FlowService:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH

    @contextmanager
    def _conn(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        flow_schema.apply_migration(self.db_path)
        flow_templates.apply_seed(self.db_path)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
        finally:
            conn.close()

    def _log_operation(self, conn: sqlite3.Connection, flow_id: str, operacao: str, payload: Dict, resultado: str) -> None:
        log_id = _generate_id("op")
        conn.execute(
            """
            INSERT INTO flow_flow_operation_logs (id, flow_id, operacao, payload, resultado, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (log_id, flow_id, operacao, _json_dump(payload), resultado, _now_iso()),
        )

    def _row_to_flow(self, row: sqlite3.Row) -> Flow:
        return Flow(
            id=row["id"],
            nome=row["nome"],
            slug=row["slug"],
            tipo_entrada=row["tipo_entrada"],
            estado=FlowState(row["estado"]),
            template_origem_id=row["template_origem_id"],
            percentual_teste=row["percentual_teste"],
            metadata=_json_load(row["metadata"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def _row_to_flow_template(self, row: sqlite3.Row) -> FlowTemplate:
        return FlowTemplate(
            id=row["id"],
            slug=row["slug"],
            versao=row["versao"],
            tipo_entrada=row["tipo_entrada"],
            estrutura=_json_load(row["estrutura"]),
            ativo=bool(row["ativo"]),
            metadata=_json_load(row["metadata"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def create_flow_from_template(
        self,
        template_slug: str,
        nome: str,
        slug: str,
        bindings: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict] = None,
        percentual_teste: int = 0,
    ) -> Flow:
        bindings = bindings or {}
        metadata = metadata or {}
        now = _now_iso()
        with self._conn() as conn:
            tpl_row = conn.execute(
                "SELECT * FROM flow_flow_templates WHERE slug=? AND ativo=1", (template_slug,)
            ).fetchone()
            if not tpl_row:
                raise ValueError("Template não encontrado ou inativo")
            tpl = self._row_to_flow_template(tpl_row)
            flow_id = _generate_id("flow")
            conn.execute(
                """
                INSERT INTO flow_flows (
                    id, nome, slug, tipo_entrada, estado, template_origem_id, percentual_teste, metadata, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    flow_id,
                    nome,
                    slug,
                    tpl.tipo_entrada,
                    FlowState.DRAFT.value,
                    tpl.id,
                    percentual_teste,
                    _json_dump(metadata),
                    now,
                    now,
                ),
            )
            steps = tpl.estrutura.get("steps", [])
            for step in steps:
                step_id = _generate_id("step")
                binding = bindings.get(step.get("agent_role")) or bindings.get(step.get("tipo_etapa"))
                conn.execute(
                    """
                    INSERT INTO flow_flow_steps (
                        id, flow_id, ordem, tipo_etapa, agent_role, agent_binding, config, flags, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        step_id,
                        flow_id,
                        step.get("ordem"),
                        step.get("tipo_etapa"),
                        step.get("agent_role"),
                        binding,
                        _json_dump(step.get("config") or {}),
                        _json_dump(step.get("flags") or {}),
                        now,
                        now,
                    ),
                )
            self._log_operation(
                conn,
                flow_id,
                "create_from_template",
                {"template_slug": template_slug, "bindings": bindings},
                "ok",
            )
            conn.commit()
            row = conn.execute("SELECT * FROM flow_flows WHERE id=?", (flow_id,)).fetchone()
            return self._row_to_flow(row)

    def set_flow_state(self, flow_id: str, novo_estado: FlowState, percentual_teste: Optional[int] = None) -> Flow:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM flow_flows WHERE id=?", (flow_id,)).fetchone()
            if not row:
                raise ValueError("Fluxo não encontrado")
            atual = FlowState(row["estado"])
            if novo_estado not in ALLOWED_TRANSITIONS.get(atual, []):
                self._log_operation(conn, flow_id, "set_state", {"from": atual.value, "to": novo_estado.value}, "erro")
                raise ValueError(f"Transição proibida: {atual.value} -> {novo_estado.value}")
            pct_value = percentual_teste if percentual_teste is not None else row["percentual_teste"]
            conn.execute(
                "UPDATE flow_flows SET estado=?, percentual_teste=?, updated_at=? WHERE id=?",
                (novo_estado.value, pct_value, _now_iso(), flow_id),
            )
            self._log_operation(conn, flow_id, "set_state", {"from": atual.value, "to": novo_estado.value}, "ok")
            conn.commit()
            row = conn.execute("SELECT * FROM flow_flows WHERE id=?", (flow_id,)).fetchone()
            return self._row_to_flow(row)

    def replace_agent_for_step(self, flow_id: str, step_id: str, novo_agent_binding: str) -> FlowStep:
        with self._conn() as conn:
            step_row = conn.execute(
                "SELECT * FROM flow_flow_steps WHERE id=? AND flow_id=?", (step_id, flow_id)
            ).fetchone()
            if not step_row:
                raise ValueError("Etapa não encontrada para este fluxo")
            conn.execute(
                "UPDATE flow_flow_steps SET agent_binding=?, updated_at=? WHERE id=?",
                (novo_agent_binding, _now_iso(), step_id),
            )
            self._log_operation(
                conn,
                flow_id,
                "replace_agent",
                {"step_id": step_id, "agent_binding": novo_agent_binding},
                "ok",
            )
            conn.commit()
            step_row = conn.execute("SELECT * FROM flow_flow_steps WHERE id=?", (step_id,)).fetchone()
            return FlowStep(
                id=step_row["id"],
                flow_id=step_row["flow_id"],
                ordem=step_row["ordem"],
                tipo_etapa=FlowStepType(step_row["tipo_etapa"]),
                agent_role=step_row["agent_role"],
                agent_binding=step_row["agent_binding"],
                config=_json_load(step_row["config"]),
                flags=_json_load(step_row["flags"]),
                created_at=datetime.fromisoformat(step_row["created_at"]),
                updated_at=datetime.fromisoformat(step_row["updated_at"]),
            )

    def reprocess_items(self, flow_id: str, criteria: Dict, max_items: int = 50) -> FlowOperationLog:
        total = len(criteria.get("item_ids", []))
        if total > max_items:
            raise ValueError("Reprocessamento excede limite permitido")
        if total == 0:
            raise ValueError("Nenhum item fornecido para reprocessamento")
        with self._conn() as conn:
            self._log_operation(
                conn,
                flow_id,
                "reprocess",
                {"criteria": criteria, "max_items": max_items},
                "ok",
            )
            conn.commit()
            log_row = conn.execute(
                "SELECT * FROM flow_flow_operation_logs WHERE flow_id=? ORDER BY created_at DESC LIMIT 1",
                (flow_id,),
            ).fetchone()
            return FlowOperationLog(
                id=log_row["id"],
                flow_id=log_row["flow_id"],
                operacao=log_row["operacao"],
                payload=_json_load(log_row["payload"]),
                resultado=log_row["resultado"],
                user_id=log_row["user_id"],
                created_at=datetime.fromisoformat(log_row["created_at"]),
            )

    def list_flows(self) -> List[Flow]:
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM flow_flows ORDER BY created_at DESC").fetchall()
            return [self._row_to_flow(r) for r in rows]

    def get_flow(self, flow_id: str) -> Optional[Flow]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM flow_flows WHERE id=?", (flow_id,)).fetchone()
            return self._row_to_flow(row) if row else None

    def list_steps(self, flow_id: str) -> List[FlowStep]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM flow_flow_steps WHERE flow_id=? ORDER BY ordem ASC", (flow_id,)
            ).fetchall()
            return [
                FlowStep(
                    id=r["id"],
                    flow_id=r["flow_id"],
                    ordem=r["ordem"],
                    tipo_etapa=FlowStepType(r["tipo_etapa"]),
                    agent_role=r["agent_role"],
                    agent_binding=r["agent_binding"],
                    config=_json_load(r["config"]),
                    flags=_json_load(r["flags"]),
                    created_at=datetime.fromisoformat(r["created_at"]),
                    updated_at=datetime.fromisoformat(r["updated_at"]),
                )
                for r in rows
            ]

    def record_execution(
        self, flow_id: str, item_id: str, tipo_entrada: str, status: FlowExecutionStatus
    ) -> FlowExecution:
        exec_id = _generate_id("exec")
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO flow_flow_executions (
                    id, flow_id, item_id, tipo_entrada, status, started_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (exec_id, flow_id, item_id, tipo_entrada, status.value, _now_iso(), _json_dump({})),
            )
            conn.commit()
            row = conn.execute("SELECT * FROM flow_flow_executions WHERE id=?", (exec_id,)).fetchone()
            return FlowExecution(
                id=row["id"],
                flow_id=row["flow_id"],
                item_id=row["item_id"],
                tipo_entrada=row["tipo_entrada"],
                status=FlowExecutionStatus(row["status"]),
                started_at=datetime.fromisoformat(row["started_at"]),
                finished_at=datetime.fromisoformat(row["finished_at"]) if row["finished_at"] else None,
                erro_resumo=row["erro_resumo"],
                metadata=_json_load(row["metadata"]),
            )

    def update_execution_status(
        self,
        execution_id: str,
        status: FlowExecutionStatus,
        erro_resumo: Optional[str] = None,
    ) -> None:
        with self._conn() as conn:
            conn.execute(
                "UPDATE flow_flow_executions SET status=?, finished_at=?, erro_resumo=? WHERE id=?",
                (status.value, _now_iso(), erro_resumo, execution_id),
            )
            conn.commit()

    def list_executions(self, flow_id: str, limit: int = 20) -> List[FlowExecution]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM flow_flow_executions WHERE flow_id=? ORDER BY started_at DESC LIMIT ?",
                (flow_id, limit),
            ).fetchall()
            return [
                FlowExecution(
                    id=r["id"],
                    flow_id=r["flow_id"],
                    item_id=r["item_id"],
                    tipo_entrada=r["tipo_entrada"],
                    status=FlowExecutionStatus(r["status"]),
                    started_at=datetime.fromisoformat(r["started_at"]),
                    finished_at=datetime.fromisoformat(r["finished_at"]) if r["finished_at"] else None,
                    erro_resumo=r["erro_resumo"],
                    metadata=_json_load(r["metadata"]),
                )
                for r in rows
            ]

    def get_execution(self, execution_id: str) -> Optional[FlowExecution]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM flow_flow_executions WHERE id=?", (execution_id,)).fetchone()
            if not row:
                return None
            return FlowExecution(
                id=row["id"],
                flow_id=row["flow_id"],
                item_id=row["item_id"],
                tipo_entrada=row["tipo_entrada"],
                status=FlowExecutionStatus(row["status"]),
                started_at=datetime.fromisoformat(row["started_at"]),
                finished_at=datetime.fromisoformat(row["finished_at"]) if row["finished_at"] else None,
                erro_resumo=row["erro_resumo"],
                metadata=_json_load(row["metadata"]),
            )

    def list_step_executions(self, execution_id: str) -> List[FlowStepExecution]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM flow_flow_step_executions WHERE flow_execution_id=? ORDER BY started_at ASC",
                (execution_id,),
            ).fetchall()
            return [
                FlowStepExecution(
                    id=r["id"],
                    flow_execution_id=r["flow_execution_id"],
                    step_id=r["step_id"],
                    status=FlowStepExecutionStatus(r["status"]),
                    started_at=datetime.fromisoformat(r["started_at"]),
                    finished_at=datetime.fromisoformat(r["finished_at"]) if r["finished_at"] else None,
                    output_resumo=r["output_resumo"],
                    erro_resumo=r["erro_resumo"],
                    raw_ref=r["raw_ref"],
                )
                for r in rows
            ]

    def list_templates(self) -> List[FlowTemplate]:
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM flow_flow_templates WHERE ativo=1").fetchall()
            return [self._row_to_flow_template(r) for r in rows]

    def record_step_execution(
        self,
        flow_execution_id: str,
        step_id: str,
        status: FlowStepExecutionStatus,
        output_resumo: Optional[str] = None,
        erro_resumo: Optional[str] = None,
    ) -> FlowStepExecution:
        exec_id = _generate_id("step_exec")
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO flow_flow_step_executions (
                    id, flow_execution_id, step_id, status, started_at, output_resumo, erro_resumo
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (exec_id, flow_execution_id, step_id, status.value, _now_iso(), output_resumo, erro_resumo),
            )
            conn.commit()
            row = conn.execute("SELECT * FROM flow_flow_step_executions WHERE id=?", (exec_id,)).fetchone()
            return FlowStepExecution(
                id=row["id"],
                flow_execution_id=row["flow_execution_id"],
                step_id=row["step_id"],
                status=FlowStepExecutionStatus(row["status"]),
                started_at=datetime.fromisoformat(row["started_at"]),
                finished_at=datetime.fromisoformat(row["finished_at"]) if row["finished_at"] else None,
                output_resumo=row["output_resumo"],
                erro_resumo=row["erro_resumo"],
                raw_ref=row["raw_ref"],
            )
