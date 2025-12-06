from __future__ import annotations

import importlib
import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
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
    FlowVersion,
)
from app.flows import catalog as flow_catalog
from app.flows import policy_engine, templates
from app.flows.templates.loader import FALLBACK_TEMPLATE_DIR, TEMPLATE_DIR
from app.flows import instrumentation
from app.flows.ops_integration import emit_event
from app.flows.versioning import FlowVersioning, count_rollbacks_last_hour

flow_schema = importlib.import_module("migrations.versions.0036_s35_flow_governance_advanced")

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
    return datetime.now(timezone.utc).isoformat()


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
        self._limits_cache: Optional[Dict] = None
        self._flags_cache: Optional[Dict] = None
        self._catalog_cache: Optional[Dict[str, Dict]] = None
        self._rbac_cache: Optional[Dict[str, list]] = None

    @contextmanager
    def _conn(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        flow_schema.apply_migration(self.db_path)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            # sincroniza templates da sprint sempre que abrimos conexão
            templates.sync_templates_to_db(conn, templates.load_templates_from_dir())
            yield conn
        finally:
            conn.close()

    def _log_operation(
        self,
        conn: sqlite3.Connection,
        flow_id: str,
        operacao: str,
        payload: Dict,
        resultado: str,
        flow_version_id: Optional[str] = None,
        mode: Optional[str] = None,
        actor: Optional[str] = None,
        catalog_hash: Optional[str] = None,
    ) -> str:
        log_id = _generate_id("op")
        now = _now_iso()
        conn.execute(
            """
            INSERT INTO flow_flow_operation_logs (id, flow_id, flow_version_id, operacao, payload, resultado, mode, actor, catalog_hash, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                log_id,
                flow_id,
                flow_version_id,
                operacao,
                _json_dump(payload),
                resultado,
                mode,
                actor,
                catalog_hash,
                now,
                now,
            ),
        )
        return log_id

    def _row_to_flow(self, row: sqlite3.Row) -> Flow:
        rollout_started_raw = row["rollout_started_at"] if "rollout_started_at" in row.keys() else None
        rollout_started_at = datetime.fromisoformat(rollout_started_raw) if rollout_started_raw else None
        return Flow(
            id=row["id"],
            nome=row["nome"],
            slug=row["slug"],
            tipo_entrada=row["tipo_entrada"],
            estado=FlowState(row["estado"]),
            domain=row["domain"] if "domain" in row.keys() else "generic",
            flow_version_id=row["flow_version_id"] if "flow_version_id" in row.keys() else None,
            active_version_id=row["active_version_id"] if "active_version_id" in row.keys() else None,
            test_version_id=row["test_version_id"] if "test_version_id" in row.keys() else None,
            rollout_mode=row["rollout_mode"] if "rollout_mode" in row.keys() else None,
            rollout_state=row["rollout_state"] if "rollout_state" in row.keys() else None,
            rollout_started_at=rollout_started_at,
            rollout_criteria=_json_load(row["rollout_criteria"]) if "rollout_criteria" in row.keys() else {},
            catalog_hash=row["catalog_hash"] if "catalog_hash" in row.keys() else None,
            catalog_signature=row["catalog_signature"] if "catalog_signature" in row.keys() else None,
            flow_ops_profile_id=row["flow_ops_profile_id"] if "flow_ops_profile_id" in row.keys() else None,
            template_origem_id=row["template_origem_id"],
            percentual_teste=row["percentual_teste"],
            metadata=_json_load(row["metadata"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def delete_flow(self, flow_id: str) -> None:
        with self._conn() as conn:
            row = conn.execute("SELECT id FROM flow_flows WHERE id=?", (flow_id,)).fetchone()
            if not row:
                raise ValueError("Fluxo não encontrado")
            # registra antes de deletar para não violar FK
            self._log_operation(conn, flow_id, "delete_flow", {}, "ok")
            conn.execute("DELETE FROM flow_flows WHERE id=?", (flow_id,))
            conn.commit()

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

    def save_template(self, payload: Dict, slug_override: Optional[str] = None) -> FlowTemplate:
        slug = slug_override or payload.get("slug")
        if not slug:
            raise ValueError("slug obrigatório")
        tpl = dict(payload)
        tpl.setdefault("id", tpl.get("id") or f"tpl_{slug}")
        tpl["slug"] = slug
        tpl["version"] = str(tpl.get("version") or tpl.get("versao") or tpl.get("version_id") or "1")
        tpl.pop("versao", None)
        if not tpl.get("steps"):
            raise ValueError("steps são obrigatórios")
        if not tpl.get("entry_type"):
            raise ValueError("entry_type é obrigatório")
        if not tpl.get("domain"):
            raise ValueError("domain é obrigatório")
        path = None
        last_error: Optional[Exception] = None
        for base in (TEMPLATE_DIR, FALLBACK_TEMPLATE_DIR):
            try:
                base.mkdir(parents=True, exist_ok=True)
                candidate = base / f"{slug}.yaml"
                templates.validate_template(tpl, candidate)
                candidate.write_text(json.dumps(tpl, ensure_ascii=False, indent=2))
                path = candidate
                break
            except PermissionError as exc:
                last_error = exc
                continue
        if path is None:
            raise ValueError("Sem permissão para salvar template (config/flow_templates ou out/flow_templates)") from last_error
        with self._conn() as conn:
            templates.sync_templates_to_db(conn, templates.load_templates_from_dir())
            row = conn.execute("SELECT * FROM flow_flow_templates WHERE slug=?", (slug,)).fetchone()
            if not row:
                raise ValueError("Template não foi persistido")
            return self._row_to_flow_template(row)

    def _row_to_version(self, row: sqlite3.Row) -> FlowVersion:
        return FlowVersion(
            id=row["id"],
            flow_id=row["flow_id"],
            version_id=row["version_id"],
            template_slug=row["template_slug"],
            estado=row["estado"],
            catalog_hash=row["catalog_hash"] if "catalog_hash" in row.keys() else None,
            catalog_signature=row["catalog_signature"] if "catalog_signature" in row.keys() else None,
            metadata=_json_load(row["metadata"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def _load_simple_yaml(self, path: Path) -> Dict:
        text = path.read_text()
        try:
            import yaml  # type: ignore
        except ModuleNotFoundError:
            data: Dict[str, object] = {}
            current_key = None
            for line in text.splitlines():
                raw = line.strip()
                if not raw or raw.startswith("#"):
                    continue
                if ":" in raw and not raw.startswith("-"):
                    k, v = raw.split(":", 1)
                    current_key = k.strip()
                    val = v.strip()
                    if val:
                        data[current_key] = val
                    else:
                        data[current_key] = []
                elif raw.startswith("-") and current_key:
                    val = raw.lstrip("-").strip()
                    if isinstance(data.get(current_key), list):
                        data[current_key].append(val)
                else:
                    continue
            return data
        return yaml.safe_load(text) or {}

    def _limits(self) -> Dict:
        if self._limits_cache is None:
            path = Path("config/flows_limits.yaml")
            self._limits_cache = self._load_simple_yaml(path)
        return self._limits_cache

    def _flags(self) -> Dict:
        if self._flags_cache is None:
            path = Path("config/feature_flags.yaml")
            self._flags_cache = self._load_simple_yaml(path)
        return self._flags_cache

    def _catalog_index(self) -> Dict[str, Dict]:
        if self._catalog_cache is None:
            self._catalog_cache = flow_catalog.catalog_index_by_template()
        return self._catalog_cache

    def _catalog_entry(self, flow_slug: str, template_slug: str) -> Optional[Dict]:
        entries = list(self._catalog_index().values())
        for entry in entries:
            if str(entry.get("flow_id")) == flow_slug:
                return entry
        ref = f"config/flow_templates/{template_slug}.yaml"
        return self._catalog_index().get(ref)

    def _rbac(self) -> Dict[str, list]:
        if self._rbac_cache is None:
            path = Path("config/flow_rollout_rbac.yaml")
            self._rbac_cache = self._load_simple_yaml(path) if path.exists() else {}
        return self._rbac_cache

    def _check_rbac(self, action: str, actor: Optional[str]) -> None:
        rules = self._rbac().get(action) or []
        allowed_actors = set(self._rbac().get("actors") or [])
        # Fallback: se actor não foi fornecido, não bloqueia (modo dev/test ou chamadas internas)
        if not actor:
            return
        if allowed_actors and actor not in allowed_actors:
            raise ValueError(f"Actor {actor} não está na lista de atores permitidos")
        if rules and actor not in rules:
            raise ValueError(f"Actor {actor} não autorizado para {action}")

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
            if not self._flags().get("s34_flow_multidomain_enabled", False):
                raise ValueError("Flag s34_flow_multidomain_enabled desabilitada")
            tpl_row = conn.execute(
                "SELECT * FROM flow_flow_templates WHERE slug=? AND ativo=1", (template_slug,)
            ).fetchone()
            if not tpl_row:
                raise ValueError("Template não encontrado ou inativo")
            tpl = self._row_to_flow_template(tpl_row)
            domain = tpl.estrutura.get("domain") or tpl.metadata.get("domain") or "generic"
            catalog_entry = self._catalog_entry(slug, template_slug)
            flow_version_id = str(
                catalog_entry.get("flow_version_id")
                if catalog_entry
                else tpl.estrutura.get("version") or tpl.versao
            )
            catalog_hash = catalog_entry.get("hash") if catalog_entry else None
            catalog_signature = catalog_entry.get("signature") if catalog_entry else None
            versioning = FlowVersioning(conn, self._limits())
            flow_id = _generate_id("flow")
            conn.execute(
                """
                INSERT INTO flow_flows (
                    id, nome, slug, tipo_entrada, estado, domain, flow_version_id, active_version_id, test_version_id, rollout_mode, rollout_state,
                    rollout_started_at, rollout_criteria, catalog_hash, catalog_signature, flow_ops_profile_id,
                    template_origem_id, percentual_teste, metadata, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    flow_id,
                    nome,
                    slug,
                    tpl.tipo_entrada,
                    FlowState.DRAFT.value,
                    domain,
                    flow_version_id,
                    None,
                    None,
                    None,
                    None,
                    None,
                    _json_dump({}),
                    catalog_hash,
                    catalog_signature,
                    None,
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
            version_row = versioning.create_version(
                flow_id, tpl.slug, flow_version_id, estado="ativo", catalog_hash=catalog_hash, catalog_signature=catalog_signature
            )
            conn.execute(
                "UPDATE flow_flows SET active_version_id=?, flow_version_id=? WHERE id=?",
                (version_row.id, flow_version_id, flow_id),
            )
            self._log_operation(
                conn,
                flow_id,
                "create_from_template",
                {"template_slug": template_slug, "bindings": bindings, "flow_version_id": flow_version_id},
                "ok",
                flow_version_id=flow_version_id,
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
                self._log_operation(
                    conn,
                    flow_id,
                    "set_state",
                    {"from": atual.value, "to": novo_estado.value},
                    "erro",
                    flow_version_id=row["flow_version_id"],
                )
                raise ValueError(f"Transição proibida: {atual.value} -> {novo_estado.value}")
            pct_value = percentual_teste if percentual_teste is not None else row["percentual_teste"]
            max_pct = int(self._limits().get("max_test_percentual", 100))
            if pct_value > max_pct:
                raise ValueError(f"percentual_teste {pct_value} excede limite {max_pct}")
            policy_engine.validate_transition(row["domain"], novo_estado.value)
            conn.execute(
                "UPDATE flow_flows SET estado=?, percentual_teste=?, updated_at=? WHERE id=?",
                (novo_estado.value, pct_value, _now_iso(), flow_id),
            )
            self._log_operation(
                conn,
                flow_id,
                "set_state",
                {"from": atual.value, "to": novo_estado.value},
                "ok",
                flow_version_id=row["flow_version_id"],
            )
            conn.commit()
            row = conn.execute("SELECT * FROM flow_flows WHERE id=?", (flow_id,)).fetchone()
            return self._row_to_flow(row)

    def replace_agent_for_step(self, flow_id: str, step_id: str, novo_agent_binding: str) -> FlowStep:
        with self._conn() as conn:
            flow_row = conn.execute("SELECT flow_version_id FROM flow_flows WHERE id=?", (flow_id,)).fetchone()
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
                flow_version_id=flow_row["flow_version_id"] if flow_row else None,
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
            flow_row = conn.execute("SELECT flow_version_id FROM flow_flows WHERE id=?", (flow_id,)).fetchone()
            self._log_operation(
                conn,
                flow_id,
                "reprocess",
                {"criteria": criteria, "max_items": max_items},
                "ok",
                flow_version_id=flow_row["flow_version_id"] if flow_row else None,
            )
            conn.commit()
            log_row = conn.execute(
                "SELECT * FROM flow_flow_operation_logs WHERE flow_id=? ORDER BY created_at DESC LIMIT 1",
                (flow_id,),
            ).fetchone()
            return FlowOperationLog(
                id=log_row["id"],
                flow_id=log_row["flow_id"],
                flow_version_id=log_row["flow_version_id"],
                operacao=log_row["operacao"],
                payload=_json_load(log_row["payload"]),
                resultado=log_row["resultado"],
                user_id=log_row["user_id"],
                created_at=datetime.fromisoformat(log_row["created_at"]),
                updated_at=datetime.fromisoformat(log_row["updated_at"]),
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
        self,
        flow_id: str,
        item_id: str,
        tipo_entrada: str,
        status: FlowExecutionStatus,
        flow_version_id: Optional[str] = None,
        operation_id: Optional[str] = None,
        mode: Optional[str] = None,
    ) -> FlowExecution:
        exec_id = _generate_id("exec")
        op_id = operation_id or _generate_id("op")
        with self._conn() as conn:
            flow_row = conn.execute(
                "SELECT flow_version_id, rollout_mode FROM flow_flows WHERE id=?", (flow_id,)
            ).fetchone()
            version = flow_version_id or (flow_row["flow_version_id"] if flow_row else None)
            mode_value = mode or (flow_row["rollout_mode"] if flow_row else None)
            if not version:
                raise ValueError("flow_version_id obrigatório para registrar execução")
            conn.execute(
                """
                INSERT INTO flow_flow_executions (
                    id, flow_id, flow_version_id, mode, operation_id, item_id, tipo_entrada, status, started_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    exec_id,
                    flow_id,
                    version,
                    mode_value,
                    op_id,
                    item_id,
                    tipo_entrada,
                    status.value,
                    _now_iso(),
                    _json_dump({}),
                ),
            )
            conn.commit()
            row = conn.execute("SELECT * FROM flow_flow_executions WHERE id=?", (exec_id,)).fetchone()
            return FlowExecution(
                id=row["id"],
                flow_id=row["flow_id"],
                flow_version_id=row["flow_version_id"],
                mode=row["mode"] if "mode" in row.keys() else None,
                operation_id=row["operation_id"],
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
                    flow_version_id=r["flow_version_id"],
                    mode=r["mode"] if "mode" in r.keys() else None,
                    operation_id=r["operation_id"],
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
                flow_version_id=row["flow_version_id"],
                operation_id=row["operation_id"],
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

    def create_version(self, flow_id: str, template_slug: str, version_id: str, estado: str = "ativo") -> FlowVersion:
        with self._conn() as conn:
            versioning = FlowVersioning(conn, self._limits())
            flow_row = conn.execute(
                "SELECT catalog_hash, catalog_signature FROM flow_flows WHERE id=?", (flow_id,)
            ).fetchone()
            version_row = versioning.create_version(
                flow_id,
                template_slug,
                version_id,
                estado=estado,
                catalog_hash=flow_row["catalog_hash"] if flow_row else None,
                catalog_signature=flow_row["catalog_signature"] if flow_row else None,
            )
            conn.execute(
                "UPDATE flow_flows SET flow_version_id=?, active_version_id=?, updated_at=? WHERE id=?",
                (version_id, version_row.id, _now_iso(), flow_id),
            )
            self._log_operation(
                conn,
                flow_id,
                "create_version",
                {"template_slug": template_slug, "version_id": version_id},
                "ok",
                flow_version_id=version_id,
            )
            conn.commit()
            return version_row

    def list_versions(self, flow_id: str) -> List[FlowVersion]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM flow_flow_versions WHERE flow_id=? ORDER BY created_at DESC", (flow_id,)
            ).fetchall()
            return [self._row_to_version(r) for r in rows]

    def get_version(self, flow_id: str, version_id: str) -> Optional[FlowVersion]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM flow_flow_versions WHERE flow_id=? AND version_id=?", (flow_id, version_id)
            ).fetchone()
            return self._row_to_version(row) if row else None

    def start_rollout(
        self,
        flow_id: str,
        mode: str,
        test_percentual: int,
        criteria: Optional[Dict] = None,
        actor: Optional[str] = None,
    ) -> Flow:
        criteria = criteria or {}
        flags = self._flags()
        if not flags.get("s35_flow_rollout_enabled", False):
            raise ValueError("Flag s35_flow_rollout_enabled desabilitada")
        if mode not in {"test", "canary"}:
            raise ValueError("Modo de rollout inválido")
        limits = self._limits()
        max_pct = int(limits.get("max_test_percentual", 100))
        if test_percentual > max_pct:
            raise ValueError(f"Percentual {test_percentual} excede limite {max_pct}")
        with self._conn() as conn:
            flow_row = conn.execute("SELECT * FROM flow_flows WHERE id=?", (flow_id,)).fetchone()
            if not flow_row:
                raise ValueError("Fluxo não encontrado")
            if not flow_row["flow_version_id"]:
                raise ValueError("flow_version_id ausente para rollout")
            self._check_rbac("start_rollout", actor)
            # derive template slug from template id or slug
            template_slug = (flow_row["template_origem_id"] or "").replace("tpl_", "")
            if template_slug.startswith("flow_"):
                template_slug = template_slug.replace("flow_", "", 1)
            if not template_slug:
                template_slug = flow_row["slug"].replace("flow_", "", 1)
            entry = self._catalog_entry(flow_row["slug"], template_slug)
            if flags.get("s35_flow_catalog_enforced", False) and not entry:
                raise ValueError("Catálogo ausente para fluxo")
            catalog_hash = entry.get("hash") if entry else flow_row["catalog_hash"]
            catalog_signature = entry.get("signature") if entry else flow_row["catalog_signature"]
            if not policy_engine.policies_for_domain(flow_row["domain"]):
                raise ValueError(f"Domínio {flow_row['domain']} sem políticas definidas")
            now = _now_iso()
            conn.execute(
                """
                UPDATE flow_flows
                SET rollout_mode=?, rollout_state=?, rollout_started_at=?, rollout_criteria=?, catalog_hash=?, catalog_signature=?, test_version_id=?, percentual_teste=?, updated_at=?
                WHERE id=?
                """,
                (
                    mode,
                    "em_rollout",
                    now,
                    _json_dump(criteria),
                    catalog_hash,
                    catalog_signature,
                    flow_row["active_version_id"],
                    test_percentual,
                    now,
                    flow_id,
                ),
            )
            self._log_operation(
                conn,
                flow_id,
                "start_rollout",
                {"criteria": criteria, "test_percentual": test_percentual},
                "ok",
                flow_version_id=flow_row["flow_version_id"],
                mode=mode,
                actor=actor,
                catalog_hash=catalog_hash,
            )
            instrumentation.record_rollout_request(flow_id, flow_row["flow_version_id"], mode)
            conn.commit()
            row = conn.execute("SELECT * FROM flow_flows WHERE id=?", (flow_id,)).fetchone()
            return self._row_to_flow(row)

    def promote_rollout(self, flow_id: str, actor: Optional[str] = None) -> Flow:
        with self._conn() as conn:
            flow_row = conn.execute("SELECT * FROM flow_flows WHERE id=?", (flow_id,)).fetchone()
            if not flow_row:
                raise ValueError("Fluxo não encontrado")
            if not flow_row["rollout_mode"]:
                raise ValueError("Nenhum rollout em andamento para promover")
            self._check_rbac("promote", actor)
            now = _now_iso()
            conn.execute(
                """
                UPDATE flow_flows
                SET rollout_state=?, active_version_id=?, updated_at=?
                WHERE id=?
                """,
                ("promovido", flow_row["test_version_id"] or flow_row["active_version_id"], now, flow_id),
            )
            self._log_operation(
                conn,
                flow_id,
                "promote",
                {"from_mode": flow_row["rollout_mode"]},
                "ok",
                flow_version_id=flow_row["flow_version_id"],
                mode=flow_row["rollout_mode"],
                actor=actor,
                catalog_hash=flow_row["catalog_hash"],
            )
            if flow_row["rollout_started_at"]:
                try:
                    start_dt = datetime.fromisoformat(flow_row["rollout_started_at"])
                    duration = (datetime.now(timezone.utc) - start_dt).total_seconds()
                except Exception:
                    duration = None
            else:
                duration = None
            instrumentation.record_rollout_success(flow_id, flow_row["flow_version_id"], flow_row["rollout_mode"] or "unknown", duration)
            conn.commit()
            row = conn.execute("SELECT * FROM flow_flows WHERE id=?", (flow_id,)).fetchone()
            return self._row_to_flow(row)

    def list_operations(self, flow_id: str, limit: int = 50) -> List[FlowOperationLog]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM flow_flow_operation_logs WHERE flow_id=? ORDER BY created_at DESC LIMIT ?",
                (flow_id, limit),
            ).fetchall()
            return [
                FlowOperationLog(
                    id=r["id"],
                    flow_id=r["flow_id"],
                    flow_version_id=r["flow_version_id"],
                    operacao=r["operacao"],
                    payload=_json_load(r["payload"]),
                    resultado=r["resultado"],
                    mode=r["mode"] if "mode" in r.keys() else None,
                    actor=r["actor"] if "actor" in r.keys() else None,
                    catalog_hash=r["catalog_hash"] if "catalog_hash" in r.keys() else None,
                    user_id=r["user_id"],
                    created_at=datetime.fromisoformat(r["created_at"]),
                    updated_at=datetime.fromisoformat(r["updated_at"]),
                )
                for r in rows
            ]

    def rollback_rollout(
        self, flow_id: str, target_version_id: Optional[str] = None, actor: Optional[str] = None
    ) -> Flow:
        with self._conn() as conn:
            flow_row = conn.execute("SELECT * FROM flow_flows WHERE id=?", (flow_id,)).fetchone()
            if not flow_row:
                raise ValueError("Fluxo não encontrado")
            target_version = target_version_id or flow_row["active_version_id"] or flow_row["flow_version_id"]
            if not target_version:
                raise ValueError("Versão alvo não encontrada")
            if flow_row["flow_version_id"] == target_version:
                raise ValueError("Fluxo já está na versão solicitada")
            self._check_rbac("rollback", actor)
            rollbacks_used = count_rollbacks_last_hour(conn, flow_id)
            limit = int(self._limits().get("max_rollbacks_per_hour", 2))
            if rollbacks_used >= limit:
                raise ValueError("Limite de rollbacks por hora excedido")
            ver_row = conn.execute(
                "SELECT id FROM flow_flow_versions WHERE flow_id=? AND version_id=?", (flow_id, target_version)
            ).fetchone()
            if not ver_row:
                raise ValueError("Versão alvo não encontrada")
            conn.execute(
                "UPDATE flow_flows SET flow_version_id=?, active_version_id=?, updated_at=? WHERE id=?",
                (target_version, ver_row["id"], _now_iso(), flow_id),
            )
            self._log_operation(
                conn,
                flow_id,
                "rollback",
                {"target_version_id": target_version},
                "ok",
                flow_version_id=target_version,
                mode=flow_row["rollout_mode"],
                actor=actor,
                catalog_hash=flow_row["catalog_hash"],
            )
            conn.commit()
            row = conn.execute("SELECT * FROM flow_flows WHERE id=?", (flow_id,)).fetchone()
            emit_event("rollback", flow_id, target_version, {"result": "ok"})
            instrumentation.record_rollback(flow_id, target_version, None)
            instrumentation.record_rollout_rollback(flow_id, target_version, flow_row["rollout_mode"])
            return self._row_to_flow(row)

    def rollback_flow(self, flow_id: str, target_version_id: str) -> Flow:
        return self.rollback_rollout(flow_id, target_version_id=target_version_id)

    def rollout_status(self, flow_id: str) -> Dict:
        flow = self.get_flow(flow_id)
        if not flow:
            raise ValueError("Fluxo não encontrado")
        return {
            "flow_id": flow.id,
            "flow_version_id": flow.flow_version_id,
            "active_version_id": flow.active_version_id,
            "test_version_id": flow.test_version_id,
            "rollout_mode": getattr(flow, "rollout_mode", None),
            "rollout_state": getattr(flow, "rollout_state", None),
            "catalog_hash": getattr(flow, "catalog_hash", None),
            "catalog_signature": getattr(flow, "catalog_signature", None),
            "rollout_started_at": getattr(flow, "rollout_started_at", None),
            "rollout_criteria": getattr(flow, "rollout_criteria", {}) or {},
            "alerts": self._derive_alerts(flow),
            "policy_violations": [],
            "slo_status": self._derive_slo_status(flow),
        }

    def list_catalog(self) -> List[Dict]:
        return flow_catalog.load_catalog_entries()

    def _derive_alerts(self, flow: Flow) -> List[str]:
        alerts: List[str] = []
        limits = self._limits()
        entry = self._catalog_entry(flow.slug, (flow.template_origem_id or "").replace("tpl_", ""))
        if self._flags().get("s35_flow_catalog_enforced", False) and not entry:
            alerts.append("catalog_missing")
        if entry and entry.get("hash") and entry.get("hash") != getattr(flow, "catalog_hash", None):
            alerts.append("catalog_hash_drift")
            instrumentation.record_catalog_drift(flow.id, flow.flow_version_id)
        try:
            pct = flow.percentual_teste or 0
            max_pct = int(limits.get("max_test_percentual", 100))
            if pct > max_pct:
                alerts.append("rollout_percentual_exceeded")
        except Exception:
            pass
        try:
            with self._conn() as conn:
                rollbacks = count_rollbacks_last_hour(conn, flow.id)
            limit_rb = int(limits.get("max_rollbacks_per_hour", 2))
            if rollbacks >= limit_rb:
                alerts.append("alert_rollbacks_threshold")
        except Exception:
            pass
        return alerts

    def _derive_slo_status(self, flow: Flow) -> List[Dict]:
        criteria = getattr(flow, "rollout_criteria", {}) or {}
        slo_id = criteria.get("slo_id") if isinstance(criteria, dict) else None
        if not slo_id:
            return []
        breaches = []
        try:
            with self._conn() as conn:
                rows = conn.execute(
                    "SELECT payload FROM flow_flow_operation_logs WHERE flow_id=? AND operacao='slo_breach' ORDER BY created_at DESC LIMIT 5",
                    (flow.id,),
                ).fetchall()
                for r in rows:
                    payload = _json_load(r["payload"])
                    if payload.get("slo_id") == slo_id:
                        breaches.append(payload)
        except Exception:
            breaches = []
        status = "OK" if not breaches else "BREACH"
        return [{"slo_id": slo_id, "status": status, "recent_breaches": breaches}]
