# Sprint 30 — Capítulo 2

## 2.1 Propósito dos gates da Sprint 30

A Sprint 30 está a serviço do Épico E28 — Fluxo de Agentes Configurável v1, com foco específico em E28.3 — Operação diária & pequenas mutações de topologia, alinhando o modelo de fluxos com o desenho mais profundo de agentes/committees do Programa 2.

Este capítulo define a malha de qualidade da sprint: quais gates existem, o que cada um protege, quais métricas precisam ser verdade e qual o critério de Definition of Done (DoD) para declarar a Sprint 30 como GO.

Todos os gates devem ser automatizados via scripts em `bin/` e orquestrados por um workflow dedicado em `.github/workflows/s30-gates.yml`. Nenhum gate pode depender de passo manual ou inspeção visual ad hoc.


## 2.2 Lista de gates e responsabilidades

### G0 — Escopo, alinhamento com E28 e Grounding de S30

Objetivo

Confirmar que:

- O escopo de S30 está estritamente alinhado com E28.3 (operação diária, pequenas mutações de topologia, templates e states de fluxo).
- O Capítulo 1 (Contexto & Problemas) de S30 referencia explicitamente os estados-alvo de E28 que a sprint pretende tornar verdade.
- Todos os artefatos de planejamento da sprint (Capítulos 1–4) existem, sem TODOs, sem placeholders e sem seções vazias.

Implementação

- Script: `bin/s30_g0_scope_and_alignment.sh`.
- Entradas esperadas:
  - Docs de S30 nas pastas definidas em Capítulo 3.
  - Documento do Épico E28 em `docs/epics/e28_fluxos_de_agentes.md` (ou caminho equivalente definido no Capítulo 3).
- Saídas:
  - Scorecard JSON: `out/scorecards/S30_G0_scope_and_alignment.json`.
  - Evidências textuais: `out/evidence/S30_G0_scope_and_alignment/` (diffs de escopo, checagem de links, validação de referências ao Épico E28).

Critério de aprovação

- `status` == `PASS` no scorecard.
- Nenhum alerta de seção vazia, TODO ou FIXME em docs da sprint.


### G1 — Modelo de Fluxo v1.5, templates e restrições de topologia

Objetivo

Garantir que o modelo lógico de Fluxo de Agentes v1 esteja:

- Refinado para contemplar os casos de operação diária e pequenas mutações (versão "v1.5"), sem quebrar compatibilidade com E28.
- Apoiado por templates formais de fluxo (ex.: `Fluxo_Noticias_Geral`, `Fluxo_Contestacao_V1`) com limites claros de topologia.
- Representado em schemas e migrations consistentes no código.

Implementação

- Script: `bin/s30_g1_flow_model_and_templates.sh`.
- Entradas esperadas:
  - Models e schemas em `app/flows/models.py` (ou módulo equivalente).
  - Migrations específicas de S30 (ex.: `migrations/versions/0030_s30_flow_model_v15.py`).
  - Diretório de templates: `app/flows/templates/*.yaml` ou similar.
- Checagens mínimas:
  - Validação de schema (tipos, campos obrigatórios, estados de fluxo, tipos de etapa, vínculos com agentes).
  - Existência de templates canônicos com metadados completos (tipo_entrada, owner, estados permitidos, flags de sandbox/produção).
  - Proibição de topologias proibidas (loops não intencionais, fan-out sem limite, caminhos sem etapa de decisão final, etc.).
- Saídas:
  - Scorecard JSON: `out/scorecards/S30_G1_flow_model_and_templates.json`.
  - Evidências: `out/evidence/S30_G1_flow_model_and_templates/` (logs de validação, diagramas textuais gerados, dumps de templates aprovados).

Critério de aprovação

- Todos os schemas e migrations aplicam com sucesso em um banco de teste.
- Todos os templates de fluxo obrigatórios estão presentes e válidos.
- Nenhuma topologia proibida é detectada.


### G2 — Console de Fluxos: operação diária e UX aderente a E26

Objetivo

Garantir que o Console de Fluxos de Agentes ofereça operacionalidade mínima de dia a dia, aderente à gramática de UI/Admin de E26, com pelo menos:

- Lista de fluxos com estados, saúde, última execução.
- Tela de detalhe com diagrama lógico textual e estados por etapa.
- Ações básicas: pausar, retomar, marcar como em teste/produção.

Implementação

- Script: `bin/s30_g2_flow_console_ops.sh`.
- Entradas esperadas:
  - Código de frontend em `frontend/inspectah-ui/src/features/flows/*`.
  - Rotas de API em `app/api/flow_console_routes.py` (ou equivalente).
- Checagens mínimas:
  - Testes automatizados de UI (component/integration) para as principais ações.
  - Lint e build do frontend passando.
  - Snapshot ou golden tests de layout textual do diagrama de fluxo.
- Saídas:
  - Scorecard JSON: `out/scorecards/S30_G2_flow_console_ops.json`.
  - Evidências: `out/evidence/S30_G2_flow_console_ops/` (prints, snapshots, logs de testes, curl das rotas principais).

Critério de aprovação

- Todos os testes do módulo de fluxos passam.
- Console de Fluxos expõe, pelo menos, os fluxos mapeados em Capítulo 1 para esta sprint.


### G3 — Operações seguras: pausar, retomar, reprocessar com limites

Objetivo

As operações de controle de fluxo (pause/resume, toggle sandbox/produção, reprocessamento limitado) devem ser:

- Implementadas apenas via APIs e console, sem atalhos perigosos.
- Protegidas por limites de volume, timeouts e políticas de retry.
- Auditáveis via logs estruturados.

Implementação

- Script: `bin/s30_g3_flow_operations_safety.sh`.
- Entradas esperadas:
  - Serviços de backend responsáveis por operações de fluxo (ex.: `app/flows/service.py`).
  - Configurações de limites em `config/flows_limits.yaml`.
- Checagens mínimas:
  - Testes de API que tentam operações proibidas (ex.: reprocessar todo o backlog sem limite) e confirmam bloqueio.
  - Logs estruturados contendo IDs de fluxo, usuário/operator, tipo de operação e resultado.
  - Proteções contra storms de retry e loops de reprocessamento.
- Saídas:
  - Scorecard JSON: `out/scorecards/S30_G3_flow_operations_safety.json`.
  - Evidências: `out/evidence/S30_G3_flow_operations_safety/` (logs de testes, exemplos de eventos de log, configs lidas pelo serviço).

Critério de aprovação

- Todos os testes de segurança operacional passam.
- Nenhum caminho de operação crítica depende de script manual ou acesso direto ao banco.


### G4 — Observabilidade de Fluxos e Execuções

Objetivo

Confirmar que fluxos e etapas possuem observabilidade mínima:

- Métricas de execução por fluxo e por etapa.
- Latência p95 e taxas de falha.
- Logs estruturados por execução com correlação por IDs.

Implementação

- Script: `bin/s30_g4_flow_observability.sh`.
- Entradas esperadas:
  - Código de instrumentação (ex.: `app/flows/instrumentation.py`).
  - Configuração do collector/OTel e dashboards básicos.
- Checagens mínimas:
  - Export de métricas padrões (`fluxo_execucoes_total`, `fluxo_execucoes_falha_total`, `fluxo_latencia_p95`, etc.).
  - Presença de labels mínimas (fluxo_id, etapa_id, tipo_entrada, status).
  - Logs estruturados com `exec_fluxo_id` e `exec_etapa_id` em todos os pontos críticos.
- Saídas:
  - Scorecard JSON: `out/scorecards/S30_G4_flow_observability.json`.
  - Evidências: `out/evidence/S30_G4_flow_observability/` (scrapes de métricas, exemplos de logs, screenshots de dashboards estáticos exportados).

Critério de aprovação

- Todas as métricas mínimas estão presentes e com valor não nulo em ambiente de teste.
- Logs de pelo menos um fluxo de ponta a ponta mostram correlação consistente.


### G5 — Cenário End-to-End: fluxo canônico em produção de teste

Objetivo

Validar um cenário E2E completo, em ambiente de teste, para pelo menos um fluxo canônico (ex.: "Notícia política" ou "Notícias gerais"):

- Da ingestão inicial até a decisão final.
- Passando por todas as etapas do fluxo modelado em E28 (intérprete, classificador, analistas, debunkers, decision maker).
- Com rastreabilidade completa no Console de Fluxos e nas métricas/logs.

Implementação

- Script: `bin/s30_g5_e2e_canonical_flow.sh`.
- Entradas esperadas:
  - Instância de teste do Inspectah com fontes de notícia mínimas configuradas.
  - Fluxo canônico habilitado e marcado corretamente (ex.: `Fluxo_Noticias_Politica_v1`).
- Checagens mínimas:
  - Um conjunto de eventos sintéticos de notícia é injetado.
  - O fluxo correspondente é acionado; todas as etapas são executadas com sucesso.
  - A decisão final é registrada e visível no console ou em APIs de caso.
  - As execuções aparecem no Console de Fluxos (lista e detalhe) e nas métricas de observabilidade.
- Saídas:
  - Scorecard JSON: `out/scorecards/S30_G5_e2e_canonical_flow.json`.
  - Evidências: `out/evidence/S30_G5_e2e_canonical_flow/` (logs, dumps de execuções, capturas do console, queries de métricas).

Critério de aprovação

- Pelo menos um fluxo canônico roda E2E com 100% de sucesso nos testes.
- Toda a trilha é auditável via Console de Fluxos e observabilidade.


## 2.3 Métricas de sucesso da Sprint 30

Além do status PASS/FAIL de cada gate, a Sprint 30 responde por um conjunto de métricas agregadas que ligam S30 diretamente ao contrato de E28.

Mínimo esperado ao final da sprint:

- Pelo menos 1 fluxo canônico totalmente operando via modelo E28 (nenhum atalho ad hoc em código para esse caminho).
- Tempo para pausar um fluxo problemático (da decisão do operador até o fluxo estar efetivamente pausado) inferior a 5 minutos em ambiente de teste.
- Todas as operações de fluxo executadas via Console de Fluxos ou APIs oficiais, nunca via modificação direta de banco.
- Métricas `fluxo_execucoes_total` e `fluxo_execucoes_sucesso_total` não nulas para os fluxos em escopo da sprint.

Essas métricas devem ser consolidadas em um scorecard agregado:

- Arquivo: `out/scorecards/S30_metrics_summary.json`.
- Produzido via script: `bin/s30_metrics_summary.sh`.


## 2.4 Definition of Done (DoD) da Sprint 30

A Sprint 30 só pode ser marcada como GO se todas as condições abaixo forem verdade, simultaneamente:

1. Todos os gates G0–G5 foram executados pelo menos uma vez no CI principal da sprint.
2. Todos os scorecards `S30_G*_*.json` têm `status` == `PASS`.
3. O scorecard agregado `S30_metrics_summary.json` está presente e consistente com os valores esperados definidos neste capítulo.
4. Existe um bundle de evidências gerado e publicado pelo workflow da sprint:
   - Caminho: `out/bundles/inspectah_s30_evidence_bundle.zip`.
   - Contendo todas as pastas `out/evidence/S30_G*/` e todos os scorecards `out/scorecards/S30_G*.json` e `S30_metrics_summary.json`.
5. Não há TODO, FIXME ou seções vazias nos Capítulos 1–4 da Sprint 30.
6. Não existem diferenças locais não comitadas relacionadas a S30 no repositório no momento do merge.


## 2.5 Workflow de CI e ORR de S30

O workflow de CI da Sprint 30 deve ser explícito e legível:

- Arquivo recomendado: `.github/workflows/s30-gates.yml`.
- Responsabilidades mínimas do workflow:
  - Rodar `bin/s30_g0_scope_and_alignment.sh` até `bin/s30_g5_e2e_canonical_flow.sh` em jobs separados, mas encadeados.
  - Publicar todos os scorecards em `out/scorecards/` como artifacts.
  - Chamar `bin/s30_metrics_summary.sh` e `bin/s30_bundle.sh` ao final da pipeline.

O script `bin/s30_bundle.sh` deve:

- Verificar se todos os scorecards G0–G5 estão presentes e com `status` == `PASS`.
- Empacotar `out/evidence/` e `out/scorecards/` em `out/bundles/inspectah_s30_evidence_bundle.zip`.
- Produzir um resumo textual em `out/evidence/S30_ORR_summary.txt`, com os principais números de execução dos gates.

Somente quando o bundle estiver pronto e todos os gates estiverem verdes é que o PR da Sprint 30 pode ser considerado elegível para merge em branch principal ou branch de Programa 1, conforme orientação do Capítulo 4.

