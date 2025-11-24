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
   - Config: `feed_url=https://news.gov.br/rss`, formato RSS, frequência `hourly`.
   - Estado inicial: PROPOSED → TESTING → ACTIVE.
   - Fluxos: cadastro, teste, ativação, health-check diário.
   - Observações: redundância com portal independente.

2. **Portal de fofocas (FamaNow)**
   - Tipo: `gossip_feed`
   - Domínio: entretenimento/celebridades
   - Config: `feed_url=https://famanow.example/rss`, parsing HTML simples, frequência `daily`.
   - Estado inicial: PROPOSED → TESTING; pode ir para SUSPECT se ruído alto.
   - Fluxos: cadastro, teste, marcação suspeita, revisão.

3. **API de resultados esportivos (LigaPro Score)**
   - Tipo: `sports_api`
   - Domínio: esportes
   - Config: `url_base=https://api.ligapro.example/v1`, auth token, `competition_ids=[A,B]`, frequência `hourly`.
   - Estado inicial: PROPOSED → TESTING → ACTIVE.
   - Fluxos: cadastro, ativação, health-check manual em dias de jogo.

4. **API meteorológica (MeteoNacional)**
   - Tipo: `weather_api`
   - Domínio: clima
   - Config: `url_base=https://api.met.example/v3`, auth token, `location_scope=BR`, unidades métricas, frequência `hourly`.
   - Estado inicial: PROPOSED → TESTING → ACTIVE.
   - Fluxos: health-check programado; se falhar, UNDER_REVIEW.

5. **Base de atos de governo (Diário Oficial Digital)**
   - Tipo: `gov_record`
   - Domínio: governo/transparência
   - Config: `url_base=https://diario.oficial.example/api`, formato JSON/CSV, filtros por data/órgão.
   - Estado inicial: PROPOSED → TESTING → ACTIVE.
   - Fluxos: cadastro, edição de filtro, revisão sob alerta de Debunker.

6. **Projeto de lei (Legis Tracker)**
   - Tipo: `legislation`
   - Domínio: legislação
   - Config: `url_base=https://legis.example/api`, casa `federal`, parsing de HTML/JSON, frequência `daily`.
   - Estado inicial: PROPOSED → TESTING → ACTIVE.
   - Fluxos: cadastro, health-check; contestação se divergência com outra fonte legislativa.

7. **Repositório científico (SciData Hub)**
   - Tipo: `science_dataset`
   - Domínio: ciência
   - Config: `download_url=https://scidata.example/export.csv`, `schema_version=1.0`, `refresh_strategy=monthly`.
   - Estado inicial: PROPOSED → TESTING → ACTIVE.
   - Fluxos: cadastro, seed, health-check; revisão se schema mudar.

8. **Dataset estático mensal (Custo de obras)**	
   - Tipo: `static_dataset`
   - Domínio: obras públicas/economia
   - Config: `download_url=https://dados.obras.example/mensal.csv`, checksum opcional, frequência `monthly`.
   - Estado inicial: PROPOSED → TESTING → ACTIVE.
   - Fluxos: cadastro, health-check, desativação temporária se checksum falhar.

## 3. Mapeamento para seeds e testes
- Migration `*_s21_sources_seed_examples.py` deve inserir pelo menos um registro por cenário acima.
- `tests/sources/test_healthcheck_integration.py` deve usar esses ids/urls fictícios.
- UI de admin deve permitir navegar entre esses cenários e executar fluxos chave (criar/editar, health-check, marcar suspeita, revisão).

## 4. Cobertura de domínios obrigatórios
- Política/notícias, fofoca/celebridades, esportes, clima, mandatos/projetos, obras/atos de governo, ciência, dataset estático.
