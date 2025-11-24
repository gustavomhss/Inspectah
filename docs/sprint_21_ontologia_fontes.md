# Sprint 21 — Ontologia de Fontes

Este documento consolida a definição canônica de **fonte** no Inspectah para a Fase 1 (Sprints 21–25). Ele é a referência para modelagem, serviços, UI e integrações futuras (ingestão, agentes, Debunker, governança).

## 1. Definição de fonte

Uma fonte é qualquer origem estruturada de informação que o Inspectah consulta para formar, contestar ou reforçar respostas. Cada fonte tem:
- Identidade única e estável (`id`, `slug`, `nome`).
- Tipo (gramática de coleta e interpretação).
- Domínios/temas que cobre.
- Configuração operacional (protocolo, autenticação, frequência).
- Estado de ciclo de vida (proposta → teste → ativa → revisão/suspeita → desativada).
- Trilhas de auditoria (quem criou/alterou, quando, por quê).
- Ligações para ingestão, Debunker e evidências.

## 2. Taxonomia de tipos de fonte (Fase 1)

| Tipo | Descrição | Protocolos/formatos típicos | Exemplos |
| --- | --- | --- | --- |
| `news_rss` | Feeds de notícias estruturados (RSS/Atom/JSON). | HTTP GET, RSS/Atom, JSON. | Agências oficiais, portais de notícias políticas. |
| `gossip_feed` | Conteúdo de celebridades/entretenimento com baixo controle editorial. | HTTP GET/HTML scraping simples, RSS/Atom. | Blogs de fofoca, colunas de celebridades. |
| `sports_api` | APIs de resultados esportivos e tabelas. | HTTP GET/POST, JSON. | API de campeonatos, placares em tempo quase real. |
| `weather_api` | Dados climáticos e alertas meteorológicos. | HTTP GET, JSON, possivelmente auth por token. | Serviços nacionais de meteorologia, NOAA-like. |
| `gov_record` | Registros oficiais (atos, mandatos, diários). | HTTP GET/POST, CSV, XML, JSON. | Diários oficiais, portais de transparência. |
| `legislation` | Projetos de lei e andamento legislativo. | HTTP GET, HTML/JSON, scraping leve. | Câmara/Assembleias, portais legislativos. |
| `science_dataset` | Bases científicas ou repositórios de papers/resultados. | HTTP GET, CSV/JSON, OAI-PMH. | CrossRef, arXiv subset, datasets oficiais. |
| `static_dataset` | Arquivos estáticos versionados (CSV, Parquet, JSON). | Download HTTP/HTTPS, checksum. | Releases periódicas de dados abertos. |

Tipos são extensíveis, mas a Sprint 21 fixa essa lista mínima para contratos com S22–S25.

## 3. Atributos obrigatórios e opcionais por fonte

- **Identidade**: `id`, `slug`, `name`, `description`.
- **Tipo**: um dos tipos acima.
- **Domínios/temas**: lista de temas (política, economia, esportes, clima, celebridades, ciência, governo, legislação).
- **Categorias**: classificação interna (oficial, comunitária, monitoramento, crítica, redundante).
- **Formato/protocolo**: `protocol` (http, https, file), `format` (rss, json, csv, html, xml).
- **Config operacional**:
  - `endpoint` / `url_base`.
  - `auth` (nenhum, token, basic, api_key) + `auth_params`.
  - `request_params` (query/body padrão), `headers`.
  - `frequency` (cron simples ou enum: manual, hourly, daily, weekly).
  - `timeout_ms`, `retry_policy` (tentativas, backoff).
  - `parsing` hints (path/selector quando necessário).
- **Estados** (ver seção 5): `state`, `state_reason`, `state_updated_at`.
- **Saúde**: último health-check, latência, status (`OK`, `DEGRADED`, `FAIL`), erro.
- **Auditoria**: `created_at`, `created_by`, `updated_at`, `updated_by`, `last_reviewed_by`.
- **Debunker/contestação**: flags e vínculos com conflitos (seções 6 e 7).
- **Metadados**: `tags` livres (poucas), `confidence_hint` declarada, `redundancy_group` para tripla redundância.

## 4. Campos obrigatórios por tipo

- **`news_rss` / `gossip_feed`**: `url_base` ou `feed_url`, `encoding`, `item_selector` opcional, `rate_limit`.
- **`sports_api`**: `url_base`, `auth` opcional, `competition_ids`, `timezone`, `frequency`.
- **`weather_api`**: `url_base`, `auth`, `location_scope` (geo), `frequency`, `units`.
- **`gov_record`**: `url_base`, `format`, `section_filter`, `date_window`, `auth` opcional.
- **`legislation`**: `url_base`, `format`, `house`/`jurisdiction`, `id_fields`, `frequency`.
- **`science_dataset` / `static_dataset`**: `download_url`, `checksum` opcional, `schema_version`, `refresh_strategy` (full/incremental/manual).

Qualquer criação/edição deve ser validada contra esses requisitos.

## 5. Estados e ciclo de vida (visão conceitual)

Estados principais:
- `PROPOSED` — definida, ainda não testada.
- `TESTING` — em validação controlada.
- `ACTIVE` — coleta liberada.
- `UNDER_REVIEW` — revisão manual ou provocada pelo Debunker.
- `SUSPECT` — marcada como suspeita, coleta limitada.
- `DISABLED_TEMP` — desativada temporariamente.
- `DISABLED_PERM` — desativada permanentemente (não volta a ativo).

Transições permitidas:
- PROPOSED → TESTING → ACTIVE.
- ACTIVE → UNDER_REVIEW / SUSPECT / DISABLED_TEMP.
- UNDER_REVIEW → ACTIVE / SUSPECT / DISABLED_TEMP / DISABLED_PERM.
- SUSPECT → UNDER_REVIEW / DISABLED_TEMP / DISABLED_PERM.
- DISABLED_TEMP → UNDER_REVIEW / ACTIVE.
- DISABLED_PERM é terminal.

Cada transição exige motivo (`state_reason`) e autor (`changed_by`).

## 6. Relação com temas, casos e timelines

- Cada fonte referencia temas (taxonomia leve) e pode estar ligada a casos/timelines através de `info_types` e `scenario_tags`.
- Eventos de timeline podem registrar quais fontes suportam um caso e em que estado estavam no momento da evidência.
- Debunker e governança devem conseguir consultar fontes por tema e por histórico de estado para entender confiabilidade contextual.

## 7. Ganchos para Debunker e contestação

- Campos: `conflict_flags`, `contestation_open`, `contestation_notes`, `last_conflict_at`, `conflict_with_sources` (lista).
- Histórico: `SourceStateHistory` armazena eventos de conflito/contestação com severidade.
- Integração futura: Debunker (S24) pode abrir/fechar contestação e anexar `evidence_refs`.

## 8. Exemplos por domínio

- Política/notícias: feed RSS de agência oficial e portal independente, ambos tipo `news_rss`.
- Fofoca: blog de celebridades tipo `gossip_feed` com scraping simples.
- Esportes: API JSON de resultados (`sports_api`) com auth por token.
- Clima: API meteorológica nacional (`weather_api`) com geo e unidades.
- Mandatos/projetos: portal legislativo (`legislation`) com filtros por casa/jurisdição.
- Projetos públicos: base de obras (`gov_record`) com CSV/JSON.
- Ciência: repositório de papers (`science_dataset`) com schema versionado.
- Dataset estático: release mensal CSV (`static_dataset`) com checksum.

## 9. Ligação com redundância tripla

- Campos `redundancy_group` e `redundancy_role` (primária/secundária/sentinela) permitem combinar múltiplas fontes para o mesmo domínio.
- Health-check e Debunker usam esse agrupamento para escolher fallback e detectar divergências.

## 10. Saídas esperadas

Esta ontologia deve ser refletida em:
- `app/sources/models.py` (entidades e enums).
- `app/sources/schemas.py` e `validators.py` (validação por tipo).
- `docs/sprint_21_modelo_dados_fontes.md` e `docs/sprint_21_ciclo_vida_fontes.md`.
- Migrations da Sprint 21 e seeds de cenários.
