# Sprint 13 — Cenários do Explorer v0

Este documento descreve o roteiro de testes automatizados usado no gate **S13_G4**. Cada cenário representa uma consulta ou abertura de caso no Explorer v0, cobrindo os seis domínios piloto definidos em `config/s13_pilotos.yml`. O formato abaixo é parseado diretamente por `scripts/s13_explorer_scenarios.py`.

## Como ler

- `type = "search"`: executar `GET /explorer/cases?query=...` e validar que o caso esperado aparece e que o total mínimo de resultados foi atingido.
- `type = "detail"`: executar `GET /explorer/cases/{case_id}` e validar timeline (mínimo de eventos) e domínio.
- `min_results` e `min_timeline_events` definem as checagens obrigatórias adicionais.

<!-- S13_EXPLORER_SCENARIOS:BEGIN -->
```json
[
  {
    "scenario_id": "obra_search_transcol",
    "domain": "obra_publica",
    "type": "search",
    "query": "obra_transcol_niteroi_2022",
    "expected_case_id": "obra_publica:obra_transcol_niteroi_2022",
    "min_results": 1
  },
  {
    "scenario_id": "obra_detail_transcol",
    "domain": "obra_publica",
    "type": "detail",
    "case_id": "obra_publica:obra_transcol_niteroi_2022",
    "min_timeline_events": 1
  },
  {
    "scenario_id": "clima_search_serrana",
    "domain": "evento_climatico",
    "type": "search",
    "query": "evento_clima_serrana_2023",
    "expected_case_id": "evento_climatico:evento_clima_serrana_2023",
    "min_results": 1
  },
  {
    "scenario_id": "clima_detail_serrana",
    "domain": "evento_climatico",
    "type": "detail",
    "case_id": "evento_climatico:evento_clima_serrana_2023",
    "min_timeline_events": 1
  },
  {
    "scenario_id": "pl_search_transparencia",
    "domain": "projeto_lei",
    "type": "search",
    "query": "pl_transparencia_energia_2024",
    "expected_case_id": "projeto_lei:pl_transparencia_energia_2024",
    "min_results": 1
  },
  {
    "scenario_id": "pl_detail_transparencia",
    "domain": "projeto_lei",
    "type": "detail",
    "case_id": "projeto_lei:pl_transparencia_energia_2024",
    "min_timeline_events": 2
  },
  {
    "scenario_id": "carreira_search_prefeitura",
    "domain": "carreira_politica",
    "type": "search",
    "query": "carreira_prefeitura_niteroi_2020_2024",
    "expected_case_id": "carreira_politica:carreira_prefeitura_niteroi_2020_2024",
    "min_results": 1
  },
  {
    "scenario_id": "carreira_detail_prefeitura",
    "domain": "carreira_politica",
    "type": "detail",
    "case_id": "carreira_politica:carreira_prefeitura_niteroi_2020_2024",
    "min_timeline_events": 2
  },
  {
    "scenario_id": "influencer_search_alpha",
    "domain": "influencer",
    "type": "search",
    "query": "influencer_obras_alpha_2023",
    "expected_case_id": "influencer:influencer_obras_alpha_2023",
    "min_results": 1
  },
  {
    "scenario_id": "influencer_detail_alpha",
    "domain": "influencer",
    "type": "detail",
    "case_id": "influencer:influencer_obras_alpha_2023",
    "min_timeline_events": 2
  },
  {
    "scenario_id": "atleta_search_bolsa",
    "domain": "atleta",
    "type": "search",
    "query": "atleta_bolsa_esporte_2024",
    "expected_case_id": "atleta:atleta_bolsa_esporte_2024",
    "min_results": 1
  },
  {
    "scenario_id": "atleta_detail_bolsa",
    "domain": "atleta",
    "type": "detail",
    "case_id": "atleta:atleta_bolsa_esporte_2024",
    "min_timeline_events": 2
  }
]
```
<!-- S13_EXPLORER_SCENARIOS:END -->
