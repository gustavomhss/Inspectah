from __future__ import annotations

from typing import Any, Dict, List, Optional

from inspectah.agents import copiloto_fontes_fsm as fsm
from inspectah.agents.tools import form_state as form_tools
from inspectah.agents.tools import source_heuristics
from inspectah.agents.tools.file_reader import read_file_as_text
from inspectah.agents.tools.logging import log_tool_call
from inspectah.agents.tools.source_reader import read_source_as_form
from inspectah.agents.tools.status_planner import plan_status_change
from inspectah.agents.tools.update_planner import plan_updates

SYSTEM_PROMPT = (
    "Você é o Copiloto de Fontes do Inspectah, um agente 'powered by ChatGPT' para admins. "
    "Escopo: ajudar a CADASTRAR, EDITAR e PLANEJAR STATUS de fontes (news_rss, sports_api, weather_api, gossip_feed, official_open, data_api e similares). "
    "Fale em português, de forma direta e conversacional: explique o que entendeu, o que está sugerindo e por quê; faça perguntas abertas quando faltar dado; traga caminhos práticos "
    "(como achar RSS/feeds no site, como localizar documentação de API de dados, como limpar URLs). "
    "Você não tem acesso à internet: quando inferir algo, diga que é suposição plausível e peça confirmação humana. "
    "Nunca diga que salvou/ativou nada sozinho: você apenas propõe ações; o humano confirma na UI. "
    "Sempre devolva: (1) uma mensagem amigável e útil para o admin, (2) uma lista de actions estruturadas (SET_FIELD, SUGGEST_FIELD, FOCUS_FIELD, PROPOSE_UPDATE, PLAN_STATUS_CHANGE). "
    "Recuse temas fora de escopo de fontes, healthcheck e status."
)


class CopilotoAgent:
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}

    def run(
        self, session_id: str, user_message: str, form_state: Dict[str, Any], files: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        if self._is_out_of_scope(user_message):
            return self._refuse(
                "Não posso sair do escopo de cadastro/edição/status de fontes. Um humano precisa revisar e confirmar.",
                session_id,
            )

        normalized = form_tools.normalize_form_state(form_state or {})
        agent_mode = bool(normalized.get("agent_mode", True))
        intent = self._detect_intent(user_message)
        state = fsm.next_state(normalized, intent)

        if normalized.get("type") and normalized.get("type") not in form_tools.ALLOWED_TYPES:
            msg = "Há problemas no formulário: tipo de fonte não reconhecido. Use news_rss, sports_api, weather_api, gossip_feed, data_api ou official_open."
            return self._build_response(msg, [], session_id)

        heur = self._run_heuristics(user_message, normalized, form_state or {})

        if state.name == "consultor":
            return self._handle_consultor(user_message, heur, session_id)
        if state.name == "planejar_status":
            return self._handle_status_flow(normalized, user_message, agent_mode, session_id)
        if state.name == "editar_existente":
            return self._handle_edit_flow(normalized, user_message, agent_mode, session_id)
        return self._handle_creation_flow(normalized, heur, user_message, files, agent_mode, session_id, form_state or {})

    def _run_heuristics(self, user_message: str, form_state: Dict[str, Any], original_form: Dict[str, Any]) -> Dict[str, Any]:
        url = source_heuristics.extract_url(user_message) or original_form.get("endpoint")
        ftype = (
            original_form.get("type")
            or source_heuristics.infer_type_from_url(url or "")
            or source_heuristics.infer_type_from_text(user_message)
        )
        themes = form_state.get("themes") or source_heuristics.suggest_themes(ftype)
        info_types = form_state.get("info_types") or source_heuristics.suggest_info_types(ftype)
        refresh = form_state.get("refresh_interval") or source_heuristics.suggest_refresh_interval(ftype)
        feed_candidates = source_heuristics.feed_candidates(url) if url else []
        return {
            "url": url,
            "type": ftype,
            "themes": themes,
            "info_types": info_types,
            "refresh_interval": refresh,
            "feed_candidates": feed_candidates,
        }

    def _handle_creation_flow(
        self,
        normalized: Dict[str, Any],
        heur: Dict[str, Any],
        user_message: str,
        files: List[Dict[str, Any]],
        agent_mode: bool,
        session_id: str,
        raw_form: Dict[str, Any],
    ) -> Dict[str, Any]:
        actions: List[Dict[str, Any]] = []
        text_parts: List[str] = []
        refresh_provided = raw_form.get("refresh_interval") not in (None, "")

        # Tipo
        if agent_mode and heur.get("type") and not normalized.get("type"):
            actions.append({"type": "set_field", "field": "type", "value": heur["type"]})
            actions.append({"type": "suggest_field", "field": "type"})
            text_parts.append(f"Inferi que é do tipo {heur['type']}.")

        # Endpoint
        endpoint = source_heuristics.suggest_endpoint(heur.get("url"), normalized.get("endpoint"))
        if agent_mode and endpoint and not normalized.get("endpoint"):
            actions.append({"type": "set_field", "field": "endpoint", "value": endpoint})
            actions.append({"type": "suggest_field", "field": "endpoint"})
            text_parts.append(
                f"Usei a URL detectada ({endpoint}) como endpoint. Se houver um /rss, /feed ou rota de API específica, me envie para eu ajustar."
            )
        elif not normalized.get("endpoint"):
            actions.append({"type": "focus_field", "field": "endpoint"})
            text_parts.append("Preciso de um endpoint (ex.: /rss, /feed, /api/v1/... ou URL JSON).")

        # Temas e info_types
        if agent_mode and heur.get("themes") and not normalized.get("themes"):
            actions.append({"type": "set_field", "field": "themes", "value": heur["themes"]})
            actions.append({"type": "suggest_field", "field": "themes"})
            text_parts.append("Sugeri temas coerentes com o tipo.")
        if agent_mode and heur.get("info_types") and not normalized.get("info_types"):
            actions.append({"type": "set_field", "field": "info_types", "value": heur["info_types"]})
            actions.append({"type": "suggest_field", "field": "info_types"})

        # Refresh
        if agent_mode and heur.get("refresh_interval") and not refresh_provided:
            actions.append({"type": "set_field", "field": "refresh_interval", "value": heur["refresh_interval"]})
            actions.append({"type": "suggest_field", "field": "refresh_interval"})
            text_parts.append(f"Propus refresh de {heur['refresh_interval']} minutos (ajuste se precisar).")

        # Arquivos
        if files:
            summaries = [read_file_as_text(f.get("file_id", "")) for f in files]
            log_tool_call("file_reader", {"files": [f.get("file_id") for f in files]}, "read_files")
            if summaries and not normalized.get("description") and agent_mode:
                snippet = (summaries[0] or "").strip()[:200]
                if snippet:
                    actions.append({"type": "set_field", "field": "description", "value": snippet})
                    actions.append({"type": "suggest_field", "field": "description"})
                    text_parts.append("Usei um trecho do arquivo para preencher a descrição.")

        # Heurísticas de feed
        if heur.get("feed_candidates"):
            text_parts.append(
                "Possíveis feeds: " + ", ".join(heur["feed_candidates"]) + ". Abra no navegador e traga o que funcionar."
            )

        issues = form_tools.validate_form_state({**normalized, **{a.get("field"): a.get("value") for a in actions if a.get("field")}})
        if issues:
            text_parts.append("Faltam alguns pontos: " + "; ".join(issues))

        if heur.get("type") == "official_open" or normalized.get("type") == "official_open":
            text_parts.append("Fonte oficial aberta: sem prometer scraping automático; mantenha refresh conservador.")
        if heur.get("type") == "data_api" or normalized.get("type") == "data_api":
            text_parts.append("API de dados: sugiro confirmar rota (/api/v1/...) e parâmetros na documentação antes de salvar.")

        if not text_parts:
            text_parts.append("Me mande a URL ou detalhes do endpoint para eu sugerir o restante.")

        message = " ".join(text_parts)
        return self._build_response(message, actions if agent_mode else [], session_id)

    def _handle_edit_flow(self, normalized: Dict[str, Any], user_message: str, agent_mode: bool, session_id: str) -> Dict[str, Any]:
        snapshot = read_source_as_form(normalized.get("source_id"))
        if not snapshot:
            return self._refuse("Não encontrei esta fonte para edição.", session_id)

        proposed = snapshot.copy()
        for field in ["name", "description", "endpoint", "themes", "info_types", "refresh_interval", "type"]:
            if normalized.get(field) not in (None, ""):
                proposed[field] = normalized[field]
        url = source_heuristics.extract_url(user_message)
        if url:
            proposed["endpoint"] = url
        number = self._extract_number(user_message)
        if number:
            proposed["refresh_interval"] = number
        changes = plan_updates(snapshot, proposed)
        actions: List[Dict[str, Any]] = []
        if agent_mode and changes:
            actions.append({"type": "propose_update", "changes": changes})
        msg = "Plano de edição pronto: revise diffs antes/depois e salve." if changes else "Nenhum ajuste proposto ainda."
        return self._build_response(msg, actions if agent_mode else [], session_id)

    def _handle_status_flow(self, normalized: Dict[str, Any], user_message: str, agent_mode: bool, session_id: str) -> Dict[str, Any]:
        snapshot = read_source_as_form(normalized.get("source_id"))
        if not snapshot:
            return self._refuse("Não encontrei esta fonte para planejar status.", session_id)
        target = self._detect_status_target(user_message)
        if not target:
            return self._refuse("Não identifiquei intenção de status. Diga aprovar, suspender, desativar ou reativar.", session_id)
        try:
            plan = plan_status_change(snapshot.get("state", "PROPOSED"), target, reason="Solicitado via Copiloto")
        except Exception:
            return self._refuse("Transição de status não permitida conforme regras do domínio.", session_id)
        actions: List[Dict[str, Any]] = []
        if agent_mode:
            actions.append({"type": "plan_status_change", "plan": plan})
        msg = "Plano de status sugerido. Confirme no painel de status antes de aplicar." if agent_mode else "Modo orientador: status descrito, aplique manualmente."
        return self._build_response(msg, actions if agent_mode else [], session_id)

    def _handle_consultor(self, user_message: str, heur: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        tips = [
            "Endpoint é a URL que a ingestão vai consultar (ex.: /rss, /feed ou rota de API).",
            "Dicas para achar RSS: procure por 'rss', 'feed' ou 'atom' no código-fonte; tente /rss, /rss.xml, /feed, /feeds.",
            "Para API de dados: procure por '/api/', '/v1/' ou documentação tipo swagger/openapi; endpoints JSON são bons candidatos.",
            "Se for official_open, procure seção de dados abertos ou páginas CSV/HTML com tabelas fixas.",
        ]
        if heur.get("feed_candidates"):
            tips.append("Sugestões de feeds: " + ", ".join(heur["feed_candidates"]))
        message = " ".join(tips)
        return self._build_response(message, [], session_id)

    def _detect_intent(self, user_message: str) -> str:
        text = user_message.lower()
        consult_keys = ["não sei", "o que é", "como achar", "ajuda", "dúvida", "?"]
        if any(k in text for k in consult_keys):
            return "consultor"
        if any(word in text for word in ["aprovar", "suspender", "desativar", "reativar"]):
            return "status"
        if any(word in text for word in ["editar", "ajustar", "atualizar"]):
            return "editar"
        return "criar"

    def _detect_status_target(self, user_message: str) -> Optional[str]:
        text = user_message.lower()
        if "aprovar" in text or "ativar" in text or "reativar" in text:
            return "ACTIVE"
        if "suspender" in text or "pausar" in text:
            return "DISABLED_TEMP"
        if "desativar" in text or "desligar" in text:
            return "DISABLED_PERM"
        return None

    def _is_out_of_scope(self, user_message: str) -> bool:
        text = user_message.lower()
        forbidden_triggers = [
            "ignore",
            "verdade ou mentira",
            "debunker",
            "timeline",
            "usuário",
            "usuario",
            "token admin",
            "automaticamente",
            "cadastrar sozinho",
            "sem revisar",
            "sem eu revisar",
            "sem confirmar",
        ]
        return any(trigger in text for trigger in forbidden_triggers)

    def _extract_number(self, text: str) -> Optional[int]:
        import re
        match = re.search(r"(\d+)", text)
        if not match:
            return None
        try:
            return int(match.group(1))
        except ValueError:
            return None

    def _build_response(self, message: str, actions: List[Dict[str, Any]], session_id: str) -> Dict[str, Any]:
        return {"assistant_message": message, "message": message, "actions": actions, "session_id": session_id}

    def _refuse(self, reason: str, session_id: str) -> Dict[str, Any]:
        message = f"Não posso sair do escopo nem aplicar sozinho: {reason} Confirme sempre com um humano."
        return self._build_response(message, [], session_id)


def get_copiloto_agent(config: Optional[Dict[str, Any]] = None) -> CopilotoAgent:
    return CopilotoAgent(config)


def run_copiloto_interaction(
    session_id: str, user_message: str, form_state: Dict[str, Any], files: List[Dict[str, Any]]
) -> Dict[str, Any]:
    agent = get_copiloto_agent({"prompt": SYSTEM_PROMPT})
    return agent.run(session_id, user_message, form_state, files)
