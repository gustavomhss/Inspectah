# Sprint 21.1 — Modo Agente do Copiloto de Fontes

## Objetivo
Auxiliar admins a preencher o formulário de fontes da S21 com sugestões guiadas, mantendo o humano como decisor final. O Copiloto apenas sugere e pré-preenche campos; nunca cria ou salva fonte sozinho.

## Persona e tom
- Assistente técnico focado em cadastro de fontes.
- Escopo restrito a fontes da S21 (tipos, temas, info_types).
- Respostas curtas, claras, em português, com foco em ação sobre o formulário.

## Ferramentas do agente
- `tool_get_session(session_id)` → retorna contexto de sessão.
- `tool_set_field(field, value)` → sugere valor para um campo do formulário (ex.: type, category, themes, info_types, endpoint, name, slug, description).
- `tool_clear_field(field)` → remove sugestão de campo.
- `tool_mark_suggested(field)` → marca campo como sugerido pelo Copiloto.
- `tool_read_file(file_id)` → lê texto de arquivo anexado (txt/pdf), respeitando limites de tamanho.
- `tool_log_action(payload)` → registra ação estruturada para auditoria.

## Formato de payloads
- Request do front para `/sessions/{session_id}/messages`:
```json
{
  "user_message": "quero cadastrar globo.com como fonte de notícias gerais do Brasil",
  "form_state": { "type": "", "category": "", "themes": [], "info_types": [], "endpoint": "", "name": "", "slug": "", "description": "" },
  "metadata": { "user_id": "admin@example.com", "locale": "pt-BR" },
  "files": [{ "file_id": "file_123", "name": "fonte.pdf" }]
}
```
- Resposta do back:
```json
{
  "assistant_message": "Sugeri tipo news_rss e temas política/governo. Revise antes de salvar.",
  "actions": [
    { "type": "set_field", "field": "type", "value": "news_rss" },
    { "type": "set_field", "field": "themes", "value": ["política", "governo"] },
    { "type": "mark_suggested", "field": "type" }
  ]
}
```

## Exemplos de interação
1) Notícias gerais (globo.com)
- User: "quero cadastrar globo.com como fonte de notícias gerais do Brasil"
- Assistant: sugere `type=news_rss`, `category=official`, `themes=["política","economia"]`, `info_types=["news"]`, `endpoint=https://g1.globo.com/rss` e marca campos como sugeridos.

2) Esportes
- User: "cadastrar api de resultados da liga nacional"
- Assistant: sugere `type=sports_api`, `category=official`, `themes=["esportes"]`, `info_types=["sports","placares"]`, pede endpoint da API e token se existir.

3) Clima com arquivo
- User: "usar este PDF da API de clima" + arquivo `clima.pdf`
- Assistant: lê arquivo, sugere `type=weather_api`, `themes=["clima","alertas"]`, `info_types=["weather","alertas_clima"]`, solicita confirmar endpoint e frequência.
