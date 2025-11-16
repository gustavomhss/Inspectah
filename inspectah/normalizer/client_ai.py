"""Clientes de IA para o normalizer (stub + GPT‑4.1 mini)."""
from __future__ import annotations

import json
import os
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, List

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "ai_gpt_4_1mini.json"


def generate_claims_stub(text: str, meta: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Gera claims determinísticos com base em metadados simples."""

    facts = meta.get("facts", {})
    metric = facts.get("metric") or meta.get("declared_metric") or "headline_metric"
    value = facts.get("value") or ("SIM" if "aprov" in text.lower() else text[:40])
    unit = facts.get("unit")
    subject = meta.get("declared_subject") or facts.get("subject") or "contexto_desconhecido"

    claim = {
        "claim_id": meta.get("item_id", "claim-1"),
        "claim_type": facts.get("claim_type") or "resultado_binario",
        "declared_metric": metric,
        "declared_subject": subject,
        "declared_value": value,
        "declared_unit": unit,
        "polarity": "informa_sem_julgar",
        "local_verdict": "segundo_esta_fonte_este_e_o_valor",
        "confidence_claim": 0.8,
    }
    return [claim]


def _load_ai_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {
        "model": "gpt-4.1-mini",
        "temperature": 0.2,
        "max_tokens": 600,
        "top_p": 0.9,
        "system_prompt": "Você é o AI Claim Normalizer do Inspectah. Responda apenas JSON válido.",
    }


def generate_claims(text: str, meta: Dict[str, Any], *, mode: str = "stub") -> List[Dict[str, Any]]:
    """Despacha entre stub e cliente real dependendo do modo."""

    if mode == "gpt4mini":
        return _generate_claims_gpt4mini(text, meta)
    return generate_claims_stub(text, meta)


def _generate_claims_gpt4mini(text: str, meta: Dict[str, Any]) -> List[Dict[str, Any]]:
    config = _load_ai_config()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY ausente para gpt4mini")

    system_prompt = config.get("system_prompt", "Você é o AI Claim Normalizer do Inspectah. Responda JSON." )
    model = config.get("model", "gpt-4.1-mini")
    temperature = config.get("temperature", 0.2)
    max_tokens = config.get("max_tokens", 600)
    top_p = config.get("top_p", 0.9)
    base_url = config.get("base_url")

    payload_meta = {
        "source_id": meta.get("source_id"),
        "item_id": meta.get("item_id"),
        "facts": meta.get("facts", {}),
    }
    user_prompt = (
        "Texto da fonte:\n---\n"
        f"{text}\n"
        "---\n"
        "Instruções:\n"
        "1. Produza uma lista JSON de claims conforme schemas/inspectah_claim_v0_1.json.\n"
        "2. Use apenas informações do texto.\n"
        "3. Não escreva nada fora do JSON.\n"
        f"Contexto: {json.dumps(payload_meta, ensure_ascii=False)}"
    )

    response_text = _call_openai(model, system_prompt, user_prompt, api_key, temperature, max_tokens, top_p, base_url)
    claims = _extract_json_array(response_text)
    if not isinstance(claims, list):
        raise RuntimeError("Resposta da IA não é uma lista de claims")
    return claims


def _call_openai(model: str, system_prompt: str, user_prompt: str, api_key: str, temperature: float, max_tokens: int, top_p: float, base_url: str | None) -> str:
    """Tenta chamar OpenAI usando API nova (OpenAI class) ou fallback ChatCompletion."""

    try:
        openai_mod = import_module("openai")
    except ImportError as exc:  # pragma: no cover - ambiente sem openai
        raise RuntimeError("Biblioteca openai não encontrada") from exc

    # preferir cliente moderno
    if hasattr(openai_mod, "OpenAI"):
        client = openai_mod.OpenAI(api_key=api_key, base_url=base_url)
        response = client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_output_tokens=max_tokens,
            top_p=top_p,
        )
        chunks: list[str] = []
        for block in getattr(response, "output", []) or []:
            for piece in getattr(block, "content", []) or []:
                if getattr(piece, "type", None) == "output_text":
                    chunks.append(piece.text)
                elif isinstance(piece, dict) and piece.get("type") == "output_text":
                    chunks.append(piece.get("text", ""))
        text = "".join(chunks).strip()
        if text:
            return text

    # fallback para ChatCompletion legacy
    if hasattr(openai_mod, "ChatCompletion"):
        openai_mod.api_key = api_key
        if base_url:
            openai_mod.base_url = base_url
        completion = openai_mod.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
        )
        return completion["choices"][0]["message"]["content"].strip()

    raise RuntimeError("API openai disponível, mas nenhum método compatível foi encontrado")


def _extract_json_array(raw_text: str) -> Any:
    text = raw_text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if "\n" in text:
            text = text.split("\n", 1)[1]
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1 or end <= start:
        raise RuntimeError("Resposta não contém JSON de lista")
    snippet = text[start : end + 1]
    return json.loads(snippet)
