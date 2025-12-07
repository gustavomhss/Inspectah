# Inspectah — Mapa Atual

## Visão geral (P1–P4)
- **P1 (Data Hub/Fluxos)**: ingestão e catálogos de fontes/fluxos, scripts de gates históricos, FlowService com rollout/catalogo em SQLite; consoles/admin UI presentes.
- **P2 (Interpretação/Claims/Sinais)**: agentes/claims/debunker/sinais estão no código, mas não auditados nesta rodada.
- **P3 (Truth‑DB/Lógica/Contestação/Memória)**: modelos de blocos/truthdb e migrações existem; integração com lógica/rollout/OracleOps não verificada.
- **P4 (Exposição/APIs/UI)**: frontend `frontend/inspectah-ui` inclui consoles de fontes/flows; APIs FastAPI em `app/api/*`; autenticação/autorizações não avaliadas.

## Arquitetura lógica atual (vista rápida)
- Backend Python com módulos `app/*` (flows, ingestion, explorer, debunk, truth, etc.) e camada de domínio em `inspectah/*`.
- Flow governance: `app/flows/service.py` + catálogo em `config/flow_catalog/*.yaml` + migrações SQLite `migrations/versions/0036_*`.
- Observabilidade: painéis/alertas versionados em `observability/dashboards` e `observability/alerts`; métricas Prometheus expostas via instrumentação local.
- Frontend: `frontend/inspectah-ui` com componentes de console (flows, sources, ops) e hooks para API REST.

## Mapas por programa
- **P1**: pipelines de ingestão, registry de fontes (`registry/sources`), field designer/configs. Sprint 35 adiciona rollout governado de fluxos, mas enforcement de limites/SLO/RBAC e integração com OracleOps/Truth estão faltantes.
- **P2**: agents/claims/debunker/sinais distribuídos em `app/agents`, `app/claims`, `app/debunk`, `app/flows/templates`; cobertura não inspecionada aqui.
- **P3**: blocos/TruthDB presentes (`inspectah/blocks`, `inspectah/truthdb`, `app/truth`), mas lógica formal/contestação/memória não verificada; nenhuma integração observada com fluxo de rollout/slo.
- **P4**: UI/Admin em `frontend/inspectah-ui`, rotas em `app/api/*`. Console de rollout existe, porém evidências de uso real não foram coletadas; RBAC opcional no backend.

## Estado por sprint (1–35)
- **S1–S3:** scripts e docs iniciais; sem scorecards versionados; não revalidados nesta auditoria.
- **S4:** scorecards `S4_T0`–`T8` presentes (discovery/specs/sources/fixtures/goldens/observability/ORR); execução não rerodada.
- **S5:** apenas scripts/fixtures; nenhum scorecard encontrado; estado desconhecido.
- **S6–S7:** scorecards `S6_G0`–`G8` e `S7_G0`–`G8` presentes (ingestão/registry/UI Alpha); não revalidados.
- **S8–S10:** scorecards completos (`S8_T0`–`T8`, `S9_T0`–`T8`, `S10_G0`–`G8`) indicando gates PASS na época; não rerodados.
- **S12–S19:** scorecards `S12_*`–`S19_*` presentes para multi-domínio; pipelines não revalidados.
- **S20–S25:** scorecards `S20_*`–`S25_*` presentes (front, truth kernel, promotion policy, threatmodel); não rerodados.
- **S26–S29:** scorecards `S26_*` (parcial), `S27_*`, `S29_*` presentes; estado operacional não revalidado.
- **S30–S34:** scorecards `S30_*`–`S34_*` presentes (flow model/console/rollout v1); não revalidados; S30 observabilidade/E2E usam dispatcher fictício com dataset estático e sem API/metrics reais; S31 gate G3 ignora falhas; S32 validações apenas em DB limpo/unit tests; S34 observabilidade/pilotos são simulações (checagem de arquivo e placeholders).
- **S35:** auditado em profundidade; rollout governado com gaps (limites/SLO/RBAC não aplicados; pilotos/observabilidade simulados).
- **S26–S29:** scorecards presentes; S29 ORR/G5 reusa scorecards e sanity mínimo; S27 backend/front sem smoke real; S26 frontend depende de node_modules e não valida UX/obs; S25 truth gates só DB/testes locais; S24 decisão baseada em golden offline.
- **S20–S21:** scorecards presentes; S21 ganchos/admin checam doc/campos e rotas, sem smoke real; S20 auth/protected routes roda apenas testes/build do frontend, sem backend/IdP real.
- **S12–S19:** scorecards presentes; S13 Explorer multi-domínio depende de snapshots estáticos (S13_G2); demais gates não revalidados.
- **S4–S11:** scorecards/artefatos antigos; S7 UI evidence trace é smoke mínimo local; S6 GO apenas lê scorecards; S5 G2 é checklist de arquivos + pytest opcional; não revalidados.

## Gaps estruturais
- Rollout governado não conectado a SLO/alertas reais nem OracleOps/Truth; status sempre “OK”.
- Limites configurados (`max_canary_duration_minutes`, timeouts, alert thresholds) não aplicados no serviço nem testados.
- RBAC/AUDIT opcional em endpoints críticos de rollout/promo/rollback.
- Evidências de pilotos/observabilidade são artificiais; falta validação ponta-a-ponta via API/UI e métricas reais.
- Sprints 1–34 não revalidadas: scorecards antigos podem estar desatualizados ou irrelevantes ao estado atual; S30 observabilidade/E2E sem API/metrics reais; S31 console gate não falha em testes; S32 gates cobrem só unitários em DB limpo; S33 SLOs não medem métricas reais; S34 observabilidade/pilotos simulados; S29 ORR/G5 só reusa scorecards e sanity mínimo; S27 backend/front sem smoke real; S26 frontend não garante build/test/UX completos; S25/S24 dependem de DB/golden offline; S21 ganchos/admin e S20 auth apenas FE/doc/presença; S13 Explorer depende de snapshots estáticos; S7 UI evidence trace é smoke mínimo/local; S6 GO só reusa scorecards; S5 G2 é checklist+pytest opcional.
