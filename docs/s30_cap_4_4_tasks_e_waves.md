# Sprint 30 — Capítulo 4.4 — Tasks e Waves (Planner)

## Visão Geral de Waves

- **W0 — Grounding & G0**  
  Domínios: documentação, higiene de sprint, scaffolding de scripts.  
  Dependências: nenhuma.  
  Saída: docs Cap.1–3 validados, script `bin/s30_g0_scope_and_alignment.sh` verde, pasta de evidências criada.

- **W1 — Núcleo de Fluxos v1.5 (G1)**  
  Domínios: backend (models, migrations, templates, serviço), roteamento base.  
  Dependências: W0.  
  Saída: modelo v1.5 aplicado em DB limpo e pós-S29, template `Fluxo_Noticias_Geral_v1` válido, serviço de fluxos operando com regras de estado/roteamento.

- **W2 — Console Operável (G2)**  
  Domínios: APIs do console, schemas, frontend (lista/detalhe/criação/timeline), testes.  
  Dependências: W1 (model/service/routing).  
  Saída: Console de Fluxos cria fluxo de notícias via template, muda estado, lista execuções e mostra timeline; testes API/front verdes.

- **W3 — Operações Seguras, Observabilidade e E2E (G3–G5 + CI)**  
  Domínios: FlowOperationLog, limites de reprocesso, instrumentação (métricas/logs), scripts de gates G3–G5, dataset E2E, metrics_summary, bundle e workflow de CI.  
  Dependências: W1–W2.  
  Saída: operações seguras com logs estruturados, métricas `inspectah_flow_*` visíveis, cenário E2E rodando com evidências, scorecards G0–G5 + metrics_summary + bundle publicados.

## Tabela de Tasks (fonte de verdade)

| ID | Wave | Área | Descrição | Arquivos principais | Gates relacionados | Done Condition | Evidências esperadas |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S30-BE-001 | W1 | backend | Ajustar modelos v1.5 de fluxos (`Flow`, `FlowStep`, `FlowExecution`, `FlowStepExecution`, `FlowTemplate`, `FlowOperationLog`) com estados, tipo_entrada, percentual_teste e metadata consistentes | app/flows/models.py | G1 | Modelos refletem v1.5, sem TODO/FIXME, com FKs/índices mínimos; testes/linters locais ok | Diff de models, referência em scorecard G1 |
| S30-BE-002 | W1 | backend | Migration principal v1.5 aplicável em DB limpo e pós-S29 | migrations/versions/0030_s30_flow_model_v15.py | G1 | `alembic upgrade head` passa em DB limpo e dump pós-S29; sem warnings críticos | Logs em out/evidence/S30_G1_flow_model_and_templates/ |
| S30-BE-003 | W1 | backend | Seed/validador do template `Fluxo_Noticias_Geral_v1` (topologia canônica) | migrations/versions/0031_s30_flow_templates_seed.py (ou equivalente), app/flows/service.py | G1 | Template ativo e válido para `noticia_texto`; validador/topologia sem loops proibidos | templates_report em out/evidence/S30_G1_flow_model_and_templates/ |
| S30-BE-004 | W1 | backend | Serviço de fluxos: create_from_template, set_state (máquina canônica), replace_agent, reprocess_items (com limites), registro em FlowOperationLog | app/flows/service.py | G1, G3 | Operações happy path e erros de transição/reprocesso respondem com códigos/erros claros; logs de operação persistidos | Tests/service logs em out/evidence/S30_G3_flow_operations_safety/ |
| S30-BE-005 | W1 | backend | Política de roteamento para `noticia_texto` (ativo único + percentual_teste + fallback) | app/flows/routing_policy.py, app/orchestration/dispatcher.py | G2, G5 | Eventos de ingestão elegíveis escolhem fluxo ativo; tráfego em teste respeita percentual_teste; ausência de ativo gera erro/fallback controlado | Logs/prints em evidências G2/G5 |
| S30-BE-006 | W1 | backend | Engine de execução de fluxo (percorre steps, chama agentes, registra FlowExecution/FlowStepExecution) | app/flows/execution_engine.py | G3, G4, G5 | Execução cria execuções/steps ordenadas; erros marcam status e não deixam zumbis; hooks de instrumentação chamados | Dumps de execuções em out/evidence/S30_G5_e2e_canonical_flow/ |
| S30-API-001 | W2 | backend | Schemas do console de fluxos (list/detail/create/state/replace/reprocess/executions) | app/flows/schemas.py | G2 | Schemas cobrindo rotas; validação de payloads; sem TODO/FIXME | Tests/ref usados em G2 |
| S30-API-002 | W2 | backend | Rotas do console (`/api/flows*`): listar, detalhar, criar de template, mudar estado, trocar agente, listar/mostrar execuções, reprocessar limitado | app/api/flow_console_routes.py | G2, G3 | Rotas 2xx no happy path e 4xx claros em erros de domínio; autorizadas; registram FlowOperationLog | Logs de testes API em out/evidence/S30_G2_flow_console_ops/ |
| S30-FE-001 | W2 | frontend | Módulo Console de Fluxos: lista, detalhe com steps/ações, drawer de execução, diálogo de criação, badges/operations bar | frontend/inspectah-ui/src/features/flows/* | G2 | Páginas renderizam dados mock/real; ações disparam hooks; estados visuais corretos por estado do fluxo | Snapshots/logs em out/evidence/S30_G2_flow_console_ops/ |
| S30-FE-002 | W2 | frontend | Hooks de API para fluxos (list/detail/executions/create/state/replace/reprocess) | frontend/inspectah-ui/src/features/flows/api.ts | G2 | Hooks com loading/erro; payloads corretos; integrados às páginas | Tests mockados registrando chamadas |
| S30-FE-003 | W2 | frontend | Testes de UI do console de fluxos (lista, detalhe, criação, timeline) | frontend/inspectah-ui/src/features/flows/__tests__/flows_console.spec.tsx | G2 | Suite roda verde no CI; cobre interações principais e erros básicos | Test logs em out/evidence/S30_G2_flow_console_ops/ |
| S30-OBS-001 | W3 | observability | Instrumentação de fluxos: métricas `inspectah_flow_*`, logs estruturados com IDs de correlação | app/flows/instrumentation.py, app/flows/execution_engine.py | G4, G5 | Métricas não nulas após execução de teste; logs contêm flow_id/exec_fluxo_id/exec_etapa_id/item_id/tipo_entrada/status | metrics_dump/logs_sample em out/evidence/S30_G4_flow_observability/ |
| S30-OBS-002 | W3 | observability | Painel/descrição de métricas + naming/labels documentado | docs/telemetria_fluxos_s30.md (ou Cap.3 ajuste) | G4 | Lista de métricas/labels oficiais; verificação automatizada ou manual registrada | Nota/arquivo em evidências G4 |
| S30-OPS-001 | W3 | ops | Scripts de gates G0–G2 | bin/s30_g0_scope_and_alignment.sh, bin/s30_g1_flow_model_and_templates.sh, bin/s30_g2_flow_console_ops.sh | G0, G1, G2 | Scripts idempotentes, retornam 0 quando verde, geram scorecards e evidências | out/scorecards/S30_G0..G2.json + evidências |
| S30-OPS-002 | W3 | ops | Script de gate G3 (operações seguras) | bin/s30_g3_flow_operations_safety.sh | G3 | Testes de pausa/retomada/reprocesso com limites; FlowOperationLog preenchido; scorecard PASS | out/scorecards/S30_G3_flow_operations_safety.json + evidências |
| S30-OPS-003 | W3 | ops | Script de gate G4 (observabilidade) | bin/s30_g4_flow_observability.sh | G4 | Métricas/logs checados; scorecard PASS | out/scorecards/S30_G4_flow_observability.json + evidências |
| S30-OPS-004 | W3 | ops | Cenário E2E de notícias + script G5 | bin/s30_g5_e2e_canonical_flow.sh, data/s30_e2e_noticias_sinteticas.* | G5 | Execução end-to-end ingestão→fluxo→console→telemetria termina com exit 0; evidências capturadas | out/scorecards/S30_G5_e2e_canonical_flow.json + out/evidence/S30_G5_* |
| S30-OPS-005 | W3 | ops | Metrics summary, bundle e workflow de CI | bin/s30_metrics_summary.sh, bin/s30_bundle.sh, .github/workflows/s30-gates.yml | G0–G5 | `S30_metrics_summary.json` PASS; bundle zip contém scorecards+evidências+ORR summary; workflow roda gates e publica artifacts | out/scorecards/S30_metrics_summary.json, out/bundles/inspectah_s30_evidence_bundle.zip |

## Estratégia, Riscos e Itens Não Negociáveis

- **Estratégia de ordem:** W0 garante docs e G0; W1 entrega espinha dorsal (modelo, template, serviço, roteamento, engine) alinhada ao G1; W2 habilita cockpit (APIs+UI) para operar o fluxo; W3 endurece operações, telemetria e prova E2E com bundle/CI.  
- **Riscos principais:** (1) Migrations v1.5 falharem em dump pós-S29 → mitigar testando cedo em G1; (2) Reprocessamento sem limites causar carga excessiva → obrigar `flows_limits` e testes negativos em G3; (3) Telemetria inconsistente → padronizar nomes/labels em S30-OBS-002 e validar em G4; (4) UI fora de sync com API → travar contratos em schemas e testar em G2.  
- **Itens não negociáveis:** nenhum gate G0–G5 pode ficar sem task; fluxos operados só via console/APIs oficiais; logs/métricas com IDs de correlação; bundle de evidências gerado antes de GO.***
