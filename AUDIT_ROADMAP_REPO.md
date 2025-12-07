# Inspectah — Auditoria Roadmap x Repositório
- Data/hora (UTC): 2025-12-06 01:41:31Z
- Branch: s35-ace-exec
- Commit: fd4629a26f26c858bc2b9b0e37d39ce1601d07f7
- Escopo coberto: Sprints 1–35. Inspeção profunda em Sprint 35 (governança de rollout/catalog) e verificação superficial (presença de scorecards/gates/evidências) nas demais sprints.

Juízo global do projeto: **Frágil** — Sprint 35 reporta GO com evidências sintéticas e gates que não exercitam contratos chave de rollout governado; SLO/alertas e integração com OracleOps/Truth estão ausentes. Conclusões sobre outros programas não avaliadas nesta rodada.

## Saúde por Programa (P1–P4)
- **P1 (Data Hub / Fluxos)**: Parcial. Estrutura de rollout/catalog criada, mas limites (canary_duration, timeouts, SLO) não são aplicados e pilotos são simulados em SQLite local. Risco de GO falso para Épico 28.
- **P2 (Claims/Agentes)**: Não auditado nesta rodada. Há módulos de agents/claims/debunk, sem verificação atual.
- **P3 (Truth‑DB/Lógica/Memória)**: Não auditado nesta rodada. Código de truthdb/blocos existe, integração com rollout/lógica não verificada.
- **P4 (Exposição/APIs/UI)**: Parcial. UI de rollout existe mas evidências de uso real são placeholders; API não aplica RBAC se actor ausente.

## Mapa de cobertura por bloco
| Bloco | Alinhamento roadmap | Lógica | Sintaxe/Indentação | Arquitetura local | Segurança | Esteira/Gates | UI/Admin |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P1‑E28‑S35 rollout governado (`app/flows`, `config/flow_catalog`, `bin/s35_*`) | Parcial — DoD exige catálogo assinado + SLO/OracleOps; implementação não conecta a SLO/Truth/OracleOps | Parcial — checa `% teste` e rollbacks/h; ignora `max_canary_duration`, timeouts, SLO | Verificado — código consistente | Parcial — rollout isolado em SQLite; sem integração com OracleOps/logic checker | Parcial — RBAC opcional; operação sem actor permitida | Parcial — gates G2/G3/G4 usam testes/unitários e placeholders, não fluxo real | Parcial — UI existe, mas evidências são capturas fictícias |
| S1–S3 (docs+scripts mínimos) | Parcial — roadmap macro só | Não verificado | Não verificado | Não verificado | Não verificado | Parcial — scripts S1–S3 presentes, sem execução | Não verificado |
| S4–S10 (gates v0/v1) | Parcial — alinhados a P1/P2 inicial | Parcial — baseado em scorecards | Não verificado | Parcial — arquitetura inicial | Parcial | Parcial — scorecards `out/scorecards/S4_*`, `S6_*`, `S7_*`, `S8_*`, `S9_*`, `S10_*` | Parcial — UI Alpha S7, não revalidada |
| S12–S19 (multi-domínio v0) | Parcial | Não verificado | Não verificado | Parcial — pipelines P1/P2 | Parcial | Parcial — scorecards `S12_*`..`S19_*` PASS; não reexecutados | Parcial — UIs e APIs não exercitadas |
| S20–S25 (front/Truth kernel/promotion policy) | Parcial | Não verificado | Não verificado | Parcial — modelos truth/promotion | Parcial | Parcial — scorecards `S20_*`..`S25_*` PASS; não reexecutados | Parcial — front/admin não revalidado |
| S26–S34 (multifluxo/rollout v1) | Parcial | Não verificado | Não verificado | Parcial — fluxo gov. v1 | Parcial | Parcial — scorecards `S29_*`..`S34_*` PASS; não reexecutados | Parcial — consoles/ops não revalidados |
| P1‑E28‑S35 rollout governado (`app/flows`, `config/flow_catalog`, `bin/s35_*`) | Parcial — DoD exige catálogo assinado + SLO/OracleOps; implementação não conecta a SLO/Truth/OracleOps | Parcial — checa `% teste` e rollbacks/h; ignora `max_canary_duration`, timeouts, SLO | Verificado — código consistente | Parcial — rollout isolado em SQLite; sem integração com OracleOps/logic checker | Parcial — RBAC opcional; operação sem actor permitida | Parcial — gates G2/G3/G4 usam testes/unitários e placeholders, não fluxo real | Parcial — UI existe, mas evidências são capturas fictícias |

### Cobertura por sprint (1–35)
- **S1–S3:** apenas docs e scripts iniciais; sem scorecards; não revalidados (status: Não verificado).  
- **S4:** scorecards `S4_T0`–`S4_T8` presentes; código/gates não reexecutados (status: Parcial).  
- **S5:** sem scorecards em `out/scorecards`; apenas scripts `bin/s5_*` e fixtures (status: Não verificado).  
- **S6–S7:** scorecards `S6_G0`–`G8` e `S7_G0`–`G8` presentes; UI Alpha não revalidada (status: Parcial).  
- **S8–S10:** scorecards completos (`S8_T0`–`T8`, `S9_T0`–`T8`, `S10_G0`–`G8`); sem rerun (status: Parcial).  
- **S12–S19:** scorecards `S12_*`–`S19_*` presentes; pipelines multi-domínio não revalidados (status: Parcial).  
- **S20–S25:** scorecards `S20_*`–`S25_*` presentes; truth/promotion/front não revalidados (status: Parcial).  
- **S26–S29:** scorecards `S26_*` (parcial), `S27_*`, `S29_*` presentes; exec não reexecutada (status: Parcial).  
- **S30–S34:** scorecards `S30_*`–`S34_*` presentes; rollout v1 e observabilidade não revalidados (status: Parcial).  
- **S35:** auditado em profundidade (findings F1–F5).

## Findings detalhados
**F1. Observabilidade de rollout aceita sem dados reais (G3)**  
- Contexto: P1‑E28‑S35 / Bloco observabilidade rollout / `bin/s35_g3_obs.sh`, `observability/dashboards/s35_flow_rollout_overview.json`.  
- Tipo/criticidade: Esteira/Observabilidade — Alto. Confiança: F+D.  
- F: Gate G3 apenas checa existência de arquivos e reexecuta os mesmos testes unitários de G2; não coleta nem valida métricas/alertas Prometheus ou painéis vivos. Instrumentação define counters, mas nenhuma validação de scrape/alerta ocorre e scorecard `out/scorecards/S35_G3_obs.json` marca PASS mesmo sem servidor ou dados.  
- D: Capítulo 2 (G3 exige métricas/alertas por modo e painel não vazio; DoD pede bloqueio quando catálogo diverge/SLO falha).  
- Impacto: GO falso para G3; SLOs e alertas de rollout podem estar inoperantes sem detecção, comprometendo operação 24/7.  
- Causa raiz: Exec (gate substituído por placeholder).  
- Prevenção:  
  1) **Gate**: adicionar verificação promtool + consulta real (`curl /metrics`) com asserts para métricas `inspectah_flow_*`, bloqueando ausência de séries.  
  2) **Teste**: smoke de alerta simulando breach (e.g., incrementar `inspectah_flow_rollout_rollback_total` e checar firing via alertmanager stub).  
  3) **Planner**: exigir evidência de painel com amostra real (PNG/JSON export) e fonte de dados referenciada no scorecard.

**F2. Limites e invariantes de rollout não são aplicados**  
- Contexto: P1‑E28‑S35 / Bloco modelo/serviço / `config/flows_limits.yaml`, `app/flows/service.py`.  
- Tipo/criticidade: Código/Processo — Alto. Confiança: F+D.  
- F: Limites `max_canary_duration_minutes`, `operation_timeout_seconds`, `alert_*` nunca são usados; promoção/rollback não consultam SLOs ou políticas além de `% teste` e rollbacks/h. Rollout pode ficar infinito e promover mesmo sem SLO.  
- D: Capítulo 2 (invariantes exigem respeito a limites e bloqueio de promoção com SLO/alerta negativo).  
- Impacto: Fluxos podem ser promovidos ou permanecer em canary sem qualquer guarda, anulando “governança avançada”.  
- Causa raiz: Exec (implementação incompleta).  
- Prevenção:  
  1) **Teste**: unitários cobrindo violação de `max_canary_duration` e `operation_timeout_seconds` com ValueError.  
  2) **Gate**: G1 deve rodar casos negativos para cada limite configurado.  
  3) **Spec**: documentar contracto mínimo `rollout_state` com timestamp e deadline obrigatório.

**F3. SLO/OracleOps inexistentes; status sempre “OK”**  
- Contexto: P1‑E28‑S35 / Bloco contratos ops / `app/flows/service.py::_derive_slo_status`, `app/flows/ops_integration.py`.  
- Tipo/criticidade: Observabilidade/Processo — Alto. Confiança: F+D.  
- F: `_derive_slo_status` apenas ecoa `slo_id` da requisição e retorna “OK” porque nenhuma operação grava `operacao='slo_breach'`; `ops_integration.emit_event` é placeholder de log. Não há integração com OracleOps nem lógica/Truth.  
- D: Capítulo 1/2 (objetivos incluem expor estado de rollout a OracleOps com `flow_version_id` e SLO/alertas). Doc `s35_slos.md` define SLOs que nunca são alimentados.  
- Impacto: Operação e conselho recebem sinal verde permanente mesmo com falha real; contestação/Truth não recebe modo/versão.  
- Causa raiz: Exec (integração ausente) + Plan (gates não cobrem SLO feed).  
- Prevenção:  
  1) **Gate**: simular breach e exigir registro em `flow_flow_operation_logs` + métrica `inspectah_flow_slo_breach_total`.  
  2) **Teste**: API de rollout deve propagar eventos para OracleOps mock (contract test).  
  3) **Playbook**: checklist de SLO/alertas com “fonte de verdade” obrigatória antes de marcar GO.

**F4. Pilotos e evidências S35 são sintéticos (G4)**  
- Contexto: P1‑E28‑S35 / Bloco pilotos / `bin/s35_g4_pilotos.sh`, `out/evidence/S35_G4_pilotos_rollout/*`.  
- Tipo/criticidade: Esteira/Produto — Crítico. Confiança: F+D.  
- F: Script apaga DB e cria flows em SQLite local via FlowService, duplica fixtures antigas para atingir volume, executa apenas start→promote (nenhum rollback real), gera screenshots placeholders e logs mínimos. Não usa API/UI/observabilidade nem catálogo externo; evidências são fabricadas no próprio script.  
- D: Capítulo 2 (G4 requer pilotos reais de notícias/contestação com catálogo publicado/consumido, promoção/rollback evidenciados, bundle multi-fluxo).  
- Impacto: GO G4 não prova operação real; risco de regressão em produção por ausência de validação ponta-a-ponta.  
- Causa raiz: Exec (piloto simulado) + Plan (gate permite placeholders).  
- Prevenção:  
  1) **Gate**: G4 deve orquestrar ambiente real (API+UI) e impedir placeholders; falhar se `console_screenshots/*.png` forem gerados por stub.  
  2) **Teste**: smoke HTTP nos endpoints `/api/flows/*` com rollback/promo, capturando métricas reais.  
  3) **Processo**: exigir carga de catálogo a partir de arquivo assinado externo e comparação de hash durante piloto.

**F5. RBAC/auditoria de rollout é opcional**  
- Contexto: P1‑E28‑S35 / Bloco segurança / `app/api/flow_console_routes.py`, `app/flows/service.py::_check_rbac`.  
- Tipo/criticidade: Segurança/Processo — Alto. Confiança: F+D.  
- F: `_check_rbac` retorna sucesso quando `actor` não é fornecido, permitindo start/promo/rollback sem usuário; API não aplica autenticação e aceita payload sem actor; logs gravam `actor=None`. DoD exige auditoria com `actor` e operação.  
- D: Capítulo 2 (auditoria completa com `flow_id`, `flow_version_id`, `mode`, `operation_id`, `actor`).  
- Impacto: Alterações críticas de rollout podem ocorrer sem trilha, violando governança e dificultando investigações.  
- Causa raiz: Exec.  
- Prevenção:  
  1) **Gate**: testes negativos para chamadas sem actor retornando 4xx.  
  2) **Spec**: tornar `actor` obrigatório em schema/API e logs.  
  3) **Processo**: integrar IdP/roles antes de expor endpoints de rollout.

**F6. Observabilidade S34 é só verificação de arquivos**  
- Contexto: P1‑E28‑S34 / Bloco observabilidade multifluxo / `bin/s34_g3_obs.sh`, `tests/flows/test_flow_alerts.py`.  
- Tipo/criticidade: Esteira/Observabilidade — Alto. Confiança: F+D.  
- F: Gate G3 roda pytest que apenas verifica existência de arquivos YAML e JSON de painel; nenhum scrape/alerta é exercitado. UI test roda `npm test` de um spec isolado, sem backend. Scorecard `S34_G3_obs.json` marca PASS mesmo se métricas/alertas estiverem inoperantes.  
- D: S34 Capítulo 2 (não copiado aqui) exige métricas/alertas/painel operantes por fluxo/mode.  
- Impacto: Possível GO falso desde S34; observabilidade de multifluxo pode estar quebrada sem detecção.  
- Causa raiz: Exec (gate mínimo).  
- Prevenção:  
  1) **Gate**: exigir coleta real de métricas `inspectah_flow_*` e firing de alertas simulados antes de PASS.  
  2) **Teste**: adicionar casos que falham se painel/queries retornam vazio ou se promtool acusa erro.  
  3) **Processo**: checklist de evidência com screenshot export + série não vazia.

**F7. Pilotos S34 são totalmente simulados**  
- Contexto: P1‑E28‑S34 / Bloco pilotos / `bin/s34_g4_pilotos.sh`, `out/evidence/S34_G4_pilotos_multifluxo/*`.  
- Tipo/criticidade: Esteira/Produto — Alto. Confiança: F+D.  
- F: Script cria flows em SQLite local, roda execuções com payloads artificiais (`item-news-1`, `item-cont-1`), gera rollback fake e escreve placeholders de screenshots; scorecard `S34_G4_pilotos.json` é sempre PASS. Não há ingestão real, nem UI/API exercitada.  
- D: S34 DoD (Capítulo 2/4) demanda pilotos multifluxo reais com console, rollback e evidência de operação.  
- Impacto: GO de S34 pode ser inválido; regressões multifluxo não são detectadas antes de expandir.  
- Causa raiz: Exec (piloto simulado) + Plan (gate permissivo).  
- Prevenção:  
  1) **Gate**: G4 deve usar API/UI reais com datasets de produção/fixtures e capturas reais; falhar se placeholders.  
  2) **Teste**: smoke end-to-end executando `FlowExecutionEngine` com itens reais e verificando métricas/logs.  
  3) **Processo**: exigir catálogo carregado de arquivo assinado e comparação de hash durante piloto.

**F8. SLOs S33 não medem métricas reais**  
- Contexto: P1‑E28‑S33 / Bloco SLOs / `bin/s33_g3_slos.sh`, `tests/ops/test_slos_evaluator.py`.  
- Tipo/criticidade: Observabilidade/Processo — Médio/Alto. Confiança: F+D.  
- F: Gate G3 executa apenas teste que parseia markdown `s33_slos.md` e verifica campos presentes; nenhuma consulta a métricas ou alertas. Scorecard `S33_G3_slos.json` fica PASS mesmo se métricas inexistirem.  
- D: S33 Capítulo 3 (SLOs) exige avaliação real de métricas/limites; DoD de observabilidade de incidentes.  
- Impacto: Indicadores de SLO/ops de S33 podem estar quebrados ou inexistentes sem detecção; risco de GO falso.  
- Causa raiz: Exec (gate substituído por parse de arquivo).  
- Prevenção:  
  1) **Gate**: avaliar métricas reais via Prometheus/fonte configurada e checar thresholds.  
  2) **Teste**: adicionar caso negativo que falha se série/métrica não existe.  
  3) **Processo**: exigir evidência de painel/alertas disparados para SLOs antes de GO.

**F9. Gate S31_G3 ignora falhas de testes**  
- Contexto: P1‑E28‑S31 / Bloco console/observabilidade providers / `bin/s31_g3_console_and_observability.sh`.  
- Tipo/criticidade: Esteira — Médio. Confiança: F+D.  
- F: Script roda pytest e npm test, mas não captura exit code; `STATUS` fica sempre PASS, scorecard `S31_G3_console.json` sempre verde mesmo se testes falharem.  
- D: S31 Capítulo 3 espera validação real de console/obs de providers.  
- Impacto: GO pode ser concedido com testes quebrados no console de providers; regressões não detectadas.  
- Causa raiz: Exec (script não checa rc).  
- Prevenção:  
  1) **Gate**: capturar `set +e`/rc e falhar se pytest/npm retornarem !=0.  
  2) **Processo**: checklist de gates impedindo STATUS forçado PASS.  
  3) **Teste**: adicionar caso negativo para abortar se run_now falhar.

**F10. S32 gates são unitários em DB limpo sem dados reais**  
- Contexto: P1‑E28‑S32 / Blocos G1/G3 / `bin/s32_g1_models_and_invariants.sh`, `bin/s32_g3_contestation_flows.sh`.  
- Tipo/criticidade: Código/Esteira — Médio. Confiança: F+D.  
- F: Gates aplicam migração SQLite local e rodam testes unitários com dados artificiais (`claim content c1`), sem ingestão real ou integração com P2/P4; fallback executa script direto se pytest indisponível.  
- D: S32 DoD (models/invariants/flows contestação) pressupõe validação em cenários próximos ao runtime; aqui é apenas DB limpo + unit test.  
- Impacto: Transições de contestação/promoção podem quebrar em dados reais sem detecção; GO pode ser superestimado.  
- Causa raiz: Exec (gates mínimos) + Plan (ausência de testes integrados).  
- Prevenção:  
  1) **Gate**: adicionar testes integrados com dados reais/fixtures P2 e consultas API.  
  2) **Teste**: cobrir caminhos negativos e invariantes em base com histórico.  
  3) **Processo**: exigir evidência de execução com dataset real antes de PASS.

**F11. S30 observabilidade/E2E dependem de dispatcher fictício**  
- Contexto: P1‑E28‑S30 / Bloco observabilidade e E2E (`bin/s30_g4_flow_observability.sh`, `bin/s30_g5_e2e_canonical_flow.sh`, `app/flows/dispatcher.py`).  
- Tipo/criticidade: Esteira/Produto — Médio. Confiança: F+D.  
- F: Gates G4/G5 usam dispatcher que cria fluxo ativo automaticamente em SQLite e processa dataset estático `tests/data/s30_e2e_news_sample.jsonl`; não há integração com APIs/UI nem validação de políticas/domínios. Status PASS é registrado mesmo sem validar métricas ou resultados (G4 só falha se houver erro de script; G5 grava PASS sem checar outputs).  
- D: S30 DoD (flow observability e E2E canônico) pressupõe validação ponta a ponta do fluxo real e métricas.  
- Impacto: GO pode mascarar falhas em pipelines reais; métricas/alertas de fluxo podem estar inoperantes.  
- Causa raiz: Exec (gates minimalistas) + Plan (sem exigência de API/UI/metrics reais).  
- Prevenção:  
  1) **Gate**: E2E deve usar API/UI reais e verificar métricas/alertas; marcar FAIL se séries vazias.  
  2) **Teste**: assertar resultados de execuções e comparar com políticas/domínios esperados.  
  3) **Processo**: impedir dispatcher que cria fluxo ad-hoc em gates de produção; usar flows/catalogo publicados.

**F12. S29 ORR/bundle confia só em scorecards e sanity mínimo**  
- Contexto: P1‑E28‑S29 / Bloco ORR / `bin/s29_g5_orr_and_bundle.sh`.  
- Tipo/criticidade: Esteira — Médio. Confiança: F+D.  
- F: ORR apenas verifica existência/status de scorecards e um pytest de ingest pipeline; ORR summary é checado só por presença; bundle gerado mesmo sem validar UI/API ou métricas. G4 compila módulos e roda dois testes unitários.  
- D: S29 DoD deveria consolidar validação do runtime/observabilidade/UI antes de GO.  
- Impacto: GO pode ser concedido com regressões em UI/API/runtime não cobertas; bundle não prova operação real.  
- Causa raiz: Exec (ORR superficial) + Plan (gates estreitos).  
- Prevenção:  
  1) **Gate**: ORR deve rerodar testes críticos (API/UI/metrics) e falhar se scorecards não forem reconfirmados.  
  2) **Teste**: incluir smoke UI/API e métricas no G5.  
  3) **Processo**: exigir evidências de resultado (prints, métricas) além de presença de scorecards.

**F13. S27 backend/frontend gates não exercitam ambiente real**  
- Contexto: P1‑E28‑S27 / Blocos G2/G3 (`bin/s27_g2_backend_ingestion_ops.sh`, `bin/s27_g3_frontend_sources_console_ops.sh`).  
- Tipo/criticidade: Esteira — Médio. Confiança: F+D.  
- F: G2 roda apenas pytest local em serviços de ingestão/admin; G3 roda lint+unit tests de frontend. Não há integração com API real, nem validação de observabilidade ou dados. Scorecards registram GO/NO_GO sem métricas ou UI real.  
- D: S27 DoD (ingestion ops + console) deveria cobrir fluxo ponta a ponta e ops.  
- Impacto: GO pode passar com falhas em integração backend/frontend ou sem métricas de produção; console de fontes pode estar quebrado sem detecção.  
- Causa raiz: Exec (gates restritos a testes locais) + Plan (ausência de smoke e observabilidade).  
- Prevenção:  
  1) **Gate**: adicionar smoke API/UI com datasets reais e checagem de métricas/alertas.  
  2) **Teste**: incluir cenários de operações (ativar/pausar fonte) e inspeção de logs/metrics.  
  3) **Processo**: exigir evidências reais de console (capturas/requests) antes de GO.

**F14. S26 frontend gate depende de node_modules e não valida UX/obs**  
- Contexto: P1‑E28‑S26 / Bloco G3 (`bin/s26_g3_frontend_quality.sh`).  
- Tipo/criticidade: Esteira/UI — Médio. Confiança: F+D.  
- F: Gate só roda lint/vitest/build se `node_modules` existir; se não existir, marca erro, mas não instala. Mesmo quando roda, não há smoke UI, métricas ou acessibilidade.  
- D: S26 DoD (frontend quality) pressupõe build/test completos e qualidade de UX/obs.  
- Impacto: GO pode ser dado sem build/test reais ou sem validar UX; risco de regressões não capturadas.  
- Causa raiz: Exec (gate mínimo) + Plan (não inclui instalação/execução completa).  
- Prevenção:  
  1) **Gate**: garantir instalação (`npm ci`) e rodar smoke UI headless + snapshots.  
  2) **Teste**: adicionar checks de acessibilidade/performance básicos.  
  3) **Processo**: exigir métricas de build/test e capturas de UI antes de GO.

**F15. S25 truth state machine não valida integração**  
- Contexto: P1‑E28‑S25 / Bloco G1 (`bin/s25_g1_truthstate_machine.sh`).  
- Tipo/criticidade: Código/Esteira — Médio. Confiança: F+D.  
- F: Gate aplica migrations SQLite e roda pytest de `tests/truth` apenas; não integra com P2/P4 nem verifica promoção/rollback em dados reais; scorecard calcula “human_code_score” fixo.  
- D: S25 DoD (truthstate/promotion policy) pressupõe validação integrada da state machine com contratos de ingest/claims/UI.  
- Impacto: Falhas na máquina de estado/promoção podem passar sem detecção; GO superestimado.  
- Causa raiz: Exec (gate restrito a unit/integration local) + Plan (ausência de smoke cross-program).  
- Prevenção:  
  1) **Gate**: adicionar testes end-to-end envolvendo claims ingeridos e UI/console.  
  2) **Teste**: cenários negativos de transição e políticas de promoção/rollback.  
  3) **Processo**: remover score manual e exigir evidência de integrações.

**F16. S24 decision quality depende de golden estático e sem UI/API**  
- Contexto: P1‑E28‑S24 / Bloco G4 (`bin/s24_g4_decision_quality.sh`).  
- Tipo/criticidade: Produto/Esteira — Médio. Confiança: F+D.  
- F: Gate abre issues em DB local e compara com golden JSON (`goldens/s24_decision_golden.json`); não usa APIs/UI nem verifica logs/metrics de decisão. PASS depende só do script rodar, sem validar contra runbook ou produção.  
- D: S24 DoD (decision quality) deveria medir qualidade em fluxo real (Debunk/Decision) com evidências.  
- Impacto: GO pode ocultar regressões na qualidade de decisão em produção; métricas/observabilidade não consideradas.  
- Causa raiz: Exec (gate offline/golden) + Plan (sem smoke real).  
- Prevenção:  
  1) **Gate**: executar decisões via API/UI e comparar resultados; exigir métricas/alertas.  
  2) **Teste**: cobrir casos adversos e divergências do golden.  
  3) **Processo**: exigir amostras reais e logs como evidência.

**F17. S21 ganchos/fluxos admin só checam presença de docs/campos**  
- Contexto: P1‑E28‑S21 / Blocos G3/G4 (`bin/s21_g3_fluxos_admin.sh`, `bin/s21_g4_ganchos_debunker.sh`).  
- Tipo/criticidade: Produto/Esteira — Médio. Confiança: F+D.  
- F: G3 valida apenas doc presente + pytest de rotas; G4 usa `rg` para verificar campos em `models.py` e doc. Não há smoke end-to-end, nem métricas/ops, nem UI. Scorecards marcam PASS sem garantir funcionalidade.  
- D: S21 DoD (fluxos admin/ganchos debunker) exige operações reais e trilha de contestação.  
- Impacto: Administração de fontes/contestação pode estar quebrada sem detecção; GO possivelmente falso.  
- Causa raiz: Exec (gates por presença) + Plan (ausência de smoke real).  
- Prevenção:  
  1) **Gate**: adicionar smoke API/UI para fluxos admin e contestação; validar logs/metrics.  
  2) **Teste**: cenários de conflito/contestação reais, não só campos.  
  3) **Processo**: exigir evidência de operações realizadas e resultados.

**F18. S20 auth/protected routes não valida backend nem fluxos reais**  
- Contexto: P1‑E28‑S20 / Bloco G4 (`bin/s20_g4_auth_and_protected_routes.sh`).  
- Tipo/criticidade: UI/Segurança — Médio. Confiança: F+D.  
- F: Gate roda apenas `npm test` e `npm run build` no frontend; não há smoke de login/logout real, tokens, backend ou políticas. M4=1 se test+build passam, sem validar proteção real.  
- D: S20 DoD (auth/rotas protegidas) requer integração frontend/backend com IdP e proteção efetiva.  
- Impacto: Rotas podem estar desprotegidas ou quebradas em runtime, GO não detecta.  
- Causa raiz: Exec (gate restrito a testes de FE) + Plan (sem smoke full-stack).  
- Prevenção:  
  1) **Gate**: smoke end-to-end com backend/IdP stub, tokens e acesso negado/permitido.  
  2) **Teste**: cenários de bypass e falhas de login.  
  3) **Processo**: exigir métricas/logs de auth e capturas reais.

**F19. S13 Explorer multi-domínio depende de snapshots estáticos**  
- Contexto: P1‑E28‑S13 / Bloco G4 (`bin/s13_g4_explorer_multi_dominio.sh`, `scripts/s13_explorer_scenarios.py`).  
- Tipo/criticidade: Produto/Esteira — Médio. Confiança: F+D.  
- F: Scenários leem snapshots `out/evidence/S13_G2/cases_snapshot.json` e `timelines_snapshot.json`; não há ingestão/claims em tempo real nem chamadas HTTP. Se snapshots estiverem desatualizados, scorecard pode falhar silenciosamente ou passar sem refletir estado real.  
- D: S13 DoD (Explorer multi-domínio) pressupõe funcionamento da API/rotas reais com dados atuais.  
- Impacto: GO pode não representar estado do Explorer em produção; regressões de busca/detalhe não detectadas.  
- Causa raiz: Exec (dependência de snapshot offline) + Plan (sem smoke API/tempo real).  
- Prevenção:  
  1) **Gate**: executar cenários via API real carregando dados recentes; falhar se snapshot ausente.  
  2) **Teste**: incluir casos que invalidem snapshots defasados e forcem ingestão real.  
  3) **Processo**: exigir geração de snapshots durante o gate a partir do pipeline oficial.

**F20. S7 evidência em UI é smoke mínimo e local**  
- Contexto: P1‑E28‑S7 / Bloco G5 (`bin/s7_g5_ui_evidence_trace.sh`).  
- Tipo/criticidade: UI/Esteira — Médio. Confiança: F+D.  
- F: Gate usa cliente local para `/query`, extrai 2 links de evidência por regex e verifica se o HTML contém “Manifesto”; não garante backend real, autenticação, nem cobertura além de 2 links. Scorecard PASS se ambos retornam 200 e substring.  
- D: S7 DoD (UI evidence trace) pressupõe navegação completa e trilha de evidência confiável.  
- Impacto: Regressões de UI/links podem passar despercebidas; GO pode não refletir uso real.  
- Causa raiz: Exec (smoke superficial) + Plan (sem testes abrangentes/UI real).  
- Prevenção:  
  1) **Gate**: e2e UI headless cobrindo login, busca, navegação completa a evidência; verificar conteúdo esperado.  
  2) **Teste**: aumentar amostra de links e validar manifest real/JSON.  
  3) **Processo**: exigir captura/screenshot e logs HTTP como evidência.

**F21. S6 GO depende só de scorecards PASS/MISSING**  
- Contexto: P1‑E28‑S6 / Bloco G8 (`bin/s6_g8_sprint_go_no_go.sh`).  
- Tipo/criticidade: Esteira — Médio. Confiança: F+D.  
- F: Gate lê status dos scorecards G0–G7 e marca GO se todos são “PASS”; se algum está MISSING ou FAIL, marca NO_GO. Não reroda nenhum teste. Scorecards antigos podem estar desatualizados sem detecção.  
- D: S6 DoD deveria garantir reexecução ou verificação atualizada dos gates críticos.  
- Impacto: GO pode ser baseado em artefatos antigos; regressões podem passar.  
- Causa raiz: Exec (ORR superficial) + Plan (sem rerun).  
- Prevenção:  
  1) **Gate**: rerodar gates críticos ou adicionar checksum/data para detectar staleness.  
  2) **Processo**: exigir evidência fresca (logs/prints) na decisão GO/NO_GO.

**F22. S5 G2 components é checklist de arquivos + pytest opcional**  
- Contexto: P1‑E28‑S5 / Bloco G2 (`bin/s5_gate_g2_components.sh`).  
- Tipo/criticidade: Código/Esteira — Médio. Confiança: F+D.  
- F: Gate apenas verifica existência de arquivos e roda pytest de `tests/components` (ou shim se pytest ausente). Não há validação de integração, contratos ou observabilidade; scorecard PASS mesmo sem cobertura ampla.  
- D: S5 DoD deveria validar componentes centrais em fluxo integrado.  
- Impacto: Componentes podem existir mas estar quebrados em runtime; GO não detecta.  
- Causa raiz: Exec (checklist) + Plan (ausência de smoke/integração).  
- Prevenção:  
  1) **Gate**: incluir testes de contrato/integração e observabilidade mínima.  
  2) **Teste**: cenários negativos e uso real de componentes.  
  3) **Processo**: exigir evidência de execução em pipeline real, não só presença de arquivos.

## Módulos/sprints inaceitáveis
- **S35 — Pilotos e observabilidade de rollout (G3/G4)**: evidências fabricadas, ausência de integração real com API/UI/SLO; recomendado refazer pilotos com ambiente real e gates estritos antes de qualquer GO.

## Limitações da auditoria
- S1–S34: cobertura apenas superficial (presença de scorecards/scripts) sem rerun de gates, UI ou APIs; código interno não reavaliado.  
- S35: auditado em profundidade, porém sem executar serviços/CI por restrição de ambiente; validação baseada em código, scripts e evidências existentes.  
- Métricas/execução runtime não validadas em ambiente real; confiança operacional reduzida para todas as sprints.
