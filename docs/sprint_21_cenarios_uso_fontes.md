# Sprint 21 — Cenários de Uso do Console de Fontes

Este documento materializa cenários concretos para validar a ontologia, o modelo e os fluxos administrativos. Cada cenário pode ser convertido em seed/migration e em testes de integração.

## 1. Estrutura de cenário
- `nome`
- `tipo` (ontologia)
- `dominio` / `tema`
- `descricao_curta`
- `config` (endpoint, auth, frequência, parsing)
- `estado_inicial`
- `fluxos percorridos`
- `observacoes de redundancia/contestacao`

## 2. Cenários canônicos

1. **Agência de notícias política (NewsGov BR)**
   - Tipo: `news_rss`
   - Domínio: política/governo
   - Config: `endpoint=mock://ok`, formato RSS, frequência `hourly`.
   - Estado inicial: PROPOSED → TESTING → ACTIVE (seedada como ACTIVE).
   - Fluxos: cadastro, teste, ativação, health-check diário.
   - Observações: redundância com portal independente.

2. **Portal de fofocas (FamaNow)**
   - Tipo: `gossip_feed`
   - Domínio: entretenimento/celebridades
   - Config: `endpoint=mock://degraded`, parsing HTML simples, frequência `daily`.
   - Estado inicial: TESTING (seed); pode ir para SUSPECT se ruído alto.
   - Fluxos: cadastro, teste, marcação suspeita, revisão.

3. **API de resultados esportivos (LigaPro Score)**
   - Tipo: `sports_api`
   - Domínio: esportes
   - Config: `endpoint=mock://ok`, auth token opcional, frequência `hourly`.
   - Estado inicial: ACTIVE (seed).
   - Fluxos: cadastro, ativação, health-check manual em dias de jogo.

4. **API meteorológica (MeteoNacional)**
   - Tipo: `weather_api`
   - Domínio: clima
   - Config: `endpoint=mock://fail`, auth token opcional, frequência `hourly`.
   - Estado inicial: SUSPECT (seed) após falhas; transições esperadas: SUSPECT → UNDER_REVIEW → DISABLED_TEMP ou retorno para ACTIVE após correção.
   - Fluxos: health-check programado; revisão automática ao detectar falha.

5. **Base de atos de governo (Diário Oficial Digital)**
   - Tipo: `gov_record`
   - Domínio: governo/transparência
   - Config: `endpoint=https://diario.oficial.example/api` (ajustável), formato JSON/CSV, filtros por data/órgão.
   - Estado inicial: PROPOSED → TESTING → ACTIVE (não seedada, criar via UI).
   - Fluxos: cadastro, edição de filtro, revisão sob alerta de Debunker.

6. **Projeto de lei (Legis Tracker)**
   - Tipo: `legislation`
   - Domínio: legislação
   - Config: `endpoint=mock://ok`, casa `federal`, parsing de HTML/JSON, frequência `daily`.
   - Estado inicial: UNDER_REVIEW (seed) aguardando validação; transições esperadas: UNDER_REVIEW → ACTIVE ou DISABLED_TEMP.
   - Fluxos: cadastro, health-check; contestação se divergência com outra fonte legislativa.

7. **Repositório científico (SciData Hub)**
   - Tipo: `science_dataset`
   - Domínio: ciência
   - Config: `endpoint=mock://ok`, `schema_version=1.0`, `refresh_strategy=monthly`.
   - Estado inicial: ACTIVE (seed).
   - Fluxos: cadastro, seed, health-check; revisão se schema mudar.

8. **Dataset estático mensal (Custo de obras)**	
   - Tipo: `static_dataset`
   - Domínio: obras públicas/economia
   - Config: `download_url=https://dados.obras.example/mensal.csv`, checksum opcional, frequência `monthly`.
   - Estado inicial: PROPOSED → TESTING → ACTIVE (não seedada, criar via UI).
   - Fluxos: cadastro, health-check, desativação temporária se checksum falhar.

## 3. Mapeamento para seeds e testes
- Migration `0003_s21_sources_seed_examples.py` insere fontes: `seed_news_ok`, `seed_gossip`, `seed_sports`, `seed_weather`, `seed_legislation`, `seed_science` (cobrem domínios principais com endpoints `mock://`).
- `tests/sources/test_healthcheck_integration.py` usa seeds para validar healthchecks.
- UI de admin permite operar esses cenários (criar novos, revisar seeds, rodar healthcheck).

## 4. Cobertura de domínios obrigatórios
- Política/notícias, fofoca/celebridades, esportes, clima, mandatos/projetos, obras/atos de governo, ciência, dataset estático.
