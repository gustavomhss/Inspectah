# S33 — Escopo operacional

Recorte fechado para o OracleOps Cockpit v1 na S33. IDs devem bater com `s33_components_map.yaml`, métricas/queries e UI.

## Fontes críticas (scope)
- `fonte_noticias_principal` — feed RSS notícias gerais (alta criticidade)
- `fonte_oficial_ibge` — API IBGE séries econômicas (alta criticidade)

## Pipelines representativos
- `pipeline_noticias` — ingestão rss -> normalização -> dispatch agentes
- `pipeline_ibge` — coleta API IBGE -> normalização -> Truth-DB ingest

## APIs internas essenciais
- `api_cockpit_ops` — `/api/ops/cockpit/*` (overview, components, incidents, SLOs)
- `api_ingest_status` — `/api/ingestion/status` (fonte/pipeline state usado no cockpit)

## SLOs priorizados (ver detalhes em s33_slos.md)
- `s33_slo_recencia_fonte_noticias`
- `s33_slo_recencia_fonte_ibge`
- `s33_slo_latencia_pipeline_noticias`
- `s33_slo_disponibilidade_api_cockpit`

## Componentes monitorados
- Ver `s33_components_map.yaml` para IDs, tipos, criticidade e vínculo com SLOs.

## Notas
- Indicadores fake proibidos: métricas/consultas devem existir ou ser implementadas nesta sprint.
- IDs aqui são fonte da verdade para backend, observabilidade e UI.*** End Patch"## out/scorecards/S32_G1_models_and_invariants.json
