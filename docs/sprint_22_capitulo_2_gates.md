# Inspectah — Sprint 22 — Capítulo 2 (v2)

## 1. Papel dos gates da Sprint 22

A Sprint 22 é o ponto em que o Inspectah deixa de ser um catálogo de fontes (S21) e passa a ter um subsistema de ingestão contínua, previsível e auditável. Os gates desta sprint não servem apenas para “ver se funciona”, mas para garantir quatro propriedades fundamentais:

1) o modelo conceitual de ingestão (IngestionConfig, IngestionRun, relação com Source) está correto, completo o bastante para Fase 1 e protegido por invariantes claros;  
2) a implementação respeita esse modelo em runtime, sem atalhos, sem estados zumbis e sem caminhos mágicos;  
3) operadores humanos conseguem enxergar, a partir da UI e de métricas, o que está acontecendo com cada fonte;  
4) o que for construído na S22 é compatível com o futuro do Inspectah (S23–S25 e depois Truth-DB/Sistema de Blocos Fase 2), sem exigir reescrita total.

Os gates S22-G0…S22-G8 são o mecanismo para travar essas propriedades. Eles se alinham com o padrão de T0–T8 já consolidado no projeto, mas focados especificamente na camada de ingestão 2.0.

Visão geral:

- S22-G0 — Grounding & DNA: garantir que o Squad 2 entenda com precisão o papel da S22, seus limites e suas dependências.  
- S22-G1 — Modelo de dados & invariantes: validar modelos IngestionConfig e IngestionRun, relação com Source e invariantes formais.  
- S22-G2 — Contratos de serviços de ingestão: definir e testar os contratos de serviços e endpoints que operam a ingestão.  
- S22-G3 — Máquina de estados de ingestão: formalizar e testar a FSM de IngestionRun.  
- S22-G4 — Persistência de dados brutos e metadados: garantir que dados e metadados estejam armazenados de forma consultável e compatível com Truth-DB futura.  
- S22-G5 — UI de admin para ingestão: validar a experiência mínima de operação por humanos.  
- S22-G6 — Observabilidade & métricas: garantir que ingestão não seja caixa-preta.  
- S22-G7 — Cenários end-to-end & demo: comprovar ingestão 2.0 na prática em fontes reais/realistas.  
- S22-G8 — ORR / GO-NO_GO da Sprint 22: consolidar a decisão final da sprint.

Cada gate define propósito, escopo, critérios objetivos de aprovação, métricas mínimas e evidências obrigatórias. O Capítulo 3 irá amarrar esses gates a arquivos, scripts e diretórios específicos; aqui definimos “o que precisa ser verdade” para cada gate.

## 2. S22-G0 — Grounding & DNA

Propósito: travar entendimento comum do Squad 2 sobre o contexto da S22, o que ela entrega, o que ela não faz e como se encaixa nas Sprints 21–25 e na Fase 2 (Truth-DB/Sistema de Blocos completo).

Escopo: Capítulo 1 da S22 (v2), DNA relevante (ingestão, trilha de auditoria, Fase 1 sem reputação e sem blockchain automática), blueprint das Sprints 21–25, notas de escopo temporário (“sem reputação formal, sem blockchain automática, sem Sistema de Blocos completo, sem comunidade avançada nesta fase”).

Critérios de aprovação:

1) Todos os membros-chave do Squad 2 conseguem responder, de forma consistente, a três perguntas: “Para que serve a S22?”, “O que ela não faz por design?”, “Como S23–S25 dependem do que a S22 entrega?”.  
2) Há consenso explícito de que: (a) o Console de Fontes da S21 é a única fonte de verdade sobre fontes; (b) a ingestão 2.0 não toca Truth-DB nem blockchain; (c) a S22 é sobre encanamento, não sobre verdade/fato.  
3) Existe um resumo interno (1–2 páginas) para o Squad 2 com decisões de contexto, assinado (nem que simbolicamente) pelo PO e pelo revisor técnico.

Métricas mínimas:

- squad_grounding_checklist_completed: true/false.  
- team_members_ack_count: número de membros que confirmaram leitura e entendimento.  
- unresolved_conceptual_conflicts: deve ser 0.

Evidências obrigatórias:

- S22-G0-summary.md com resumo objetivo de contexto, escopo in/out e decisões conscientes de não-escopo.  
- Registro de revisão interna (comentários resolvidos, checklist, ou equivalente).  
- Scorecard S22_G0_grounding.json com campos {status, notes, team_members_ack_count}.

## 3. S22-G1 — Modelo de dados & invariantes

Propósito: garantir que IngestionConfig e IngestionRun, amarrados a Source, estejam especificados com clareza, com invariantes formais que previnam estados impossíveis e gambiarras futuras.

Escopo: definição dos modelos (campos, tipos, domínios), relacionamentos, restrições, estados possíveis e invariantes formais. Inclui tanto código (ORM/SQL) quanto documentação textual.

Critérios de aprovação:

1) IngestionConfig e IngestionRun estão descritos em documento próprio, com tabela de campos, tipo, obrigatoriedade, domínio de valores e significado.  
2) Invariantes estão explicitamente escritos (não apenas “implícitos no código”), incluindo ao menos:  
- IngestionConfig sempre referencia uma Source existente e não-deletada.  
- Source em estado DEPRECATED não pode ter IngestionConfig com modo AUTOMATIC.  
- IngestionRun criado sempre começa em PENDING ou RUNNING, nunca em estado final.  
- IngestionRun encerrado só pode estar em {SUCCESS, PARTIAL_SUCCESS, FAIL}.  
- Não existe mais de um IngestionRun RUNNING simultaneamente para a mesma fonte, salvo se houver decisão explícita em contrário e bem documentada.  
3) Existem testes automatizados (unitários e, se fizer sentido, de propriedade) que falham caso qualquer invariante seja violado.

Métricas mínimas:

- invariants_defined_count: número de invariantes explicitamente documentados.  
- invariants_tested_count: quantos invariantes possuem testes cobrindo happy path e violações.  
- invariants_tests_pass_rate: deve ser 1.0 na pipeline para PASS.

Evidências obrigatórias:

- S22-G1-modelos_e_invariantes.md com descrição detalhada de modelos e invariantes.  
- Suite de testes automatizados exercitando invariantes (por exemplo, pytest).  
- Scorecard S22_G1_models_and_invariants.json com status, invariants_defined_count, invariants_tested_count, invariants_tests_pass_rate.

## 4. S22-G2 — Contratos de serviços de ingestão

Propósito: definir e validar os contratos de serviços que operam a ingestão: endpoints HTTP (se houver), serviços internos e comandos de administração. Nada de endpoints “mágicos” não-documentados.

Escopo: operações como start_ingestion_run, trigger_manual_ingestion, toggle_ingestion_mode, reprocess_run, etc., incluindo entradas, saídas, erros esperados e requisitos de idempotência.

Critérios de aprovação:

1) Cada operação relevante está documentada em tabela com: nome, finalidade, parâmetros (com tipos e validações), respostas de sucesso, códigos de erro e efeitos colaterais.  
2) Erros comuns são padronizados: fonte inexistente, fonte desabilitada, modo incompatível, run em andamento, parâmetros inválidos, etc.  
3) Operações que prometem idempotência (por exemplo, reprocess_run com run_id fixo) são testadas para garantir que chamadas repetidas não corrompem estados nem dados.  
4) As pré-condições vindas de G1 são efetivamente aplicadas: por exemplo, o sistema não permite disparar ingestão automática para fonte desabilitada apenas porque o endpoint foi chamado.

Métricas mínimas:

- api_operations_documented: número de operações documentadas.  
- api_tests_count / api_tests_pass_rate: contagem e taxa de sucesso de testes de API/serviço.  
- error_cases_covered: número de cenários de erro explicitamente testados.

Evidências obrigatórias:

- S22-G2-contratos_de_servico.md listando operações e contratos.  
- Testes de API/serviço cobrindo happy path e erros típicos.  
- Scorecard S22_G2_service_contracts.json com status, api_operations_documented, api_tests_count, api_tests_pass_rate.

## 5. S22-G3 — Máquina de estados de ingestão

Propósito: formalizar a FSM de IngestionRun e garantir que ela se comporte como uma máquina de estados finita simples, sem buracos e sem transições ilegais.

Escopo: estados (por exemplo, PENDING, RUNNING, SUCCESS, PARTIAL_SUCCESS, FAIL), transições válidas, condições de entrada e saída, tratamento de timeouts e falhas inesperadas.

Critérios de aprovação:

1) A máquina de estados está documentada em forma de diagrama ou tabela (estado atual, evento, próximo estado), incluindo transições de erro e timeout.  
2) A implementação só permite transições válidas; tentativas de transições ilegais geram erros claros e são registradas em log.  
3) Timeouts e exceções durante a ingestão convergem para estados finais coerentes (por exemplo, FAIL com indicação de motivo), sem deixar runs presos em RUNNING indefinidamente.  
4) Testes automatizados de FSM simulam transições comuns e cenários de falha (erro de rede, timeout, exception interna) e verificam que a FSM converge para estados finais esperados.

Métricas mínimas:

- fsm_states_count: número de estados definidos.  
- fsm_transitions_covered: número de transições cobertas em testes.  
- illegal_transitions_caught: número de tentativas de transições ilegais que geram erro/log (pelo menos um teste deve exercitar isso).  
- fsm_tests_pass_rate: 1.0 para PASS.

Evidências obrigatórias:

- S22-G3-maquina_de_estados.md com a FSM documentada.  
- Testes focados em FSM (unitários ou de componente).  
- Scorecard S22_G3_state_machine.json com status e métricas de FSM.

## 6. S22-G4 — Persistência de dados brutos e metadados

Propósito: assegurar que os dados brutos ingeridos e os metadados de execução (IngestionRun) sejam armazenados de forma consistente, consultável e compatível com futura Truth-DB/Sistema de Blocos.

Escopo: estrutura de persistência de payloads brutos (ou referências a eles), metadados, links entre run e dados, consultas típicas (por fonte, por janela de tempo) e decisões mínimas de retenção.

Critérios de aprovação:

1) Há definição clara de onde e como os dados brutos são armazenados (tabelas, arquivos, blobs, etc.), com metadados incluindo pelo menos: source_id, run_id, timestamps, tamanho aproximado, e se fizer sentido, um hash simples do conteúdo.  
2) IngestionRun contém referência estável aos dados brutos (por exemplo, referência a tabela ou caminho).  
3) Existem consultas (SQL ou equivalente) documentadas que respondem: (a) “quais runs tivemos para esta fonte no período X–Y?” e (b) “onde estão os dados associados a este run?”.  
4) O formato escolhido para armazenamento não impede, no futuro, a criação de blocos de verdade com hashes e âncoras (ou seja, não cria acoplamentos fortes a formatos proprietários opacos).

Métricas mínimas:

- storage_schemes_documented: número de estruturas de armazenamento descritas.  
- sample_queries_executed: número de consultas de exemplo executadas com sucesso.  
- runs_with_data_linked_ratio: proporção de IngestionRun com referência válida para dados (idealmente 1.0 em testes).

Evidências obrigatórias:

- S22-G4-persistencia_e_dados_brutos.md detalhando o modelo de armazenamento.  
- Scripts/consultas de exemplo demonstrando buscas por fonte e período.  
- Scorecard S22_G4_persistence.json com status, storage_schemes_documented, sample_queries_executed, runs_with_data_linked_ratio.

## 7. S22-G5 — UI de admin para ingestão

Propósito: garantir que um operador humano consiga operar a ingestão 2.0 sem precisar de acesso de desenvolvedor, respondendo rapidamente a perguntas sobre estado, histórico e erros de uma fonte.

Escopo: telas de admin que apresentam, no mínimo, para cada fonte: estado da ingestão (ligada/desligada, modo), última execução (timestamp, estado, duração, contagem de itens) e acesso ao histórico de runs; ações para acionar ingestões manuais e, se previsto, pausar/retomar ingestão automática.

Critérios de aprovação:

1) Em até 3 cliques, um operador consegue responder para qualquer fonte: “a ingestão está ligada ou desligada?”, “em qual modo?”, “quando foi a última ingestão?” e “qual foi o estado dessa última ingestão?”.  
2) É possível acionar manualmente uma ingestão de uma fonte específica a partir da UI, com feedback claro de sucesso/erro.  
3) Erros de ingestão ficam visíveis em nível humano (mensagem de erro interpretável), não apenas stack traces crus ou códigos obscuros.  
4) Os fluxos principais (consultar fonte, abrir histórico, acionar ingestão manual) foram exercitados por alguém que não implementou a funcionalidade (teste de usabilidade interno) e documentados.

Métricas mínimas:

- max_clicks_to_last_run_info: deve ser ≤ 3.  
- admin_flows_covered: número de fluxos básicos cobertos em testes/checklist.  
- ux_test_non_dev_participant: true/false indicando se alguém fora da implementação testou.

Evidências obrigatórias:

- Capturas de tela ou gravação curta mostrando os fluxos principais.  
- Checklist de QA/UX interno com cenários exercitados e observações.  
- Scorecard S22_G5_admin_ui.json com status, max_clicks_to_last_run_info, admin_flows_covered, ux_test_non_dev_participant.

## 8. S22-G6 — Observabilidade & métricas

Propósito: garantir que ingestão 2.0 seja observável: logs estruturados, métricas básicas de saúde e, idealmente, um painel mínimo ou script que permita enxergar fontes problemáticas e atrasos.

Escopo: logs estruturados por run, métricas agregadas (por fonte, por janela de tempo), scripts ou painéis para consultar essas métricas.

Critérios de aprovação:

1) Cada IngestionRun gera logs estruturados com run_id, source_id, timestamps, estado final, contagem de itens e, em caso de erro, código/motivo.  
2) Métricas mínimas estão disponíveis: runs_total por fonte, runs_success_total, runs_fail_total, latency_ms_avg/p95, last_success_timestamp por fonte.  
3) É possível identificar rapidamente: (a) fontes com erros recentes e (b) fontes sem ingestões recentes (por exemplo, acima de um threshold de atraso).  
4) Pelo menos um cenário de falha é gerado em ambiente de teste e verificado via métricas/painel para garantir que a falha “aparece” de forma clara.

Métricas mínimas:

- observability_metrics_defined: número de métricas definidas e implementadas.  
- sources_with_recent_errors: contagem (deve ser > 0 em ambiente de teste para provar que o alerta funciona).  
- sources_without_recent_runs: contagem de fontes com atraso acima do threshold de sanidade, em ambiente de teste controlado.  
- metrics_query_paths_documented: número de caminhos (painel, script, endpoint) documentados para consultar métricas.

Evidências obrigatórias:

- S22-G6-observabilidade.md descrevendo logs, métricas e como consultá-las.  
- Prints/exports de painel ou saída de scripts de agregação.  
- Scorecard S22_G6_observability.json com status, observability_metrics_defined, sources_with_recent_errors, sources_without_recent_runs.

## 9. S22-G7 — Cenários end-to-end & demo operável

Propósito: comprovar, em prática, que a ingestão 2.0 funciona de ponta a ponta em fontes de tipos diferentes e que um operador consegue seguir um runbook e visualizar resultado, erros e métricas.

Escopo: 3–5 cenários end-to-end envolvendo pelo menos: uma fonte de notícias via RSS, uma fonte de dados oficiais do tipo data_api e, se possível, um terceiro tipo relevante na Fase 1 (por exemplo, feed de preços simples).

Critérios de aprovação:

1) Existe pelo menos um cenário para cada tipo de fonte relevante da Fase 1 (news_rss, data_api, outro tipo escolhido para esta sprint).  
2) Cada cenário tem um runbook claro com: preparação da fonte, configuração de IngestionConfig, passos para acionar ingestão (manual ou automática em “modo demo”), o que verificar na UI, o que verificar em dados brutos e o que verificar em métricas.  
3) Os cenários foram reproduzidos por alguém que não implementou o código, apenas lendo o runbook, sem intervenção de “wizard” do time.  
4) Há registro de demo curta (ao vivo ou gravada) mostrando pelo menos dois cenários completos, do cadastro (se necessário) até visualização de dados ingeridos e métricas associadas.

Métricas mínimas:

- e2e_scenarios_defined: número de cenários definidos.  
- e2e_scenarios_passed: número de cenários executados com sucesso.  
- e2e_non_dev_runner_present: true/false indicando se houve execução por alguém fora da implementação.  
- e2e_demo_recorded: true/false indicando se demo foi registrada.

Evidências obrigatórias:

- S22-G7-cenarios_e_runbook.md descrevendo cenários, passos e critérios de sucesso.  
- Evidências em out/evidence/S22_G7_* (logs, prints, dumps de dados).  
- Scorecard S22_G7_e2e_scenarios.json com status, e2e_scenarios_defined, e2e_scenarios_passed, e2e_non_dev_runner_present, e2e_demo_recorded.

## 10. S22-G8 — ORR / GO-NO_GO da Sprint 22

Propósito: consolidar o estado dos gates S22-G0…S22-G7, gerar o scorecard agregado da S22, produzir o wrap humano e registrar, de forma auditável, a decisão GO/NO_GO da sprint.

Escopo: agregação dos scorecards individuais, verificação da presença de evidências obrigatórias, avaliação de riscos em aberto e produção de um resumo executivo.

Critérios de aprovação:

1) Todos os scorecards S22_G0…S22_G7 existem, estão acessíveis e em status PASS.  
2) Todas as evidências mínimas descritas neste capítulo estão presentes (documentos, testes, prints, painéis, runbooks, gravações).  
3) Existe wrap humano da S22 (por exemplo, docs/sprint_22_orr_summary.md) com: objetivo da sprint, descrição concisa da solução de ingestão 2.0, estado de cada gate, riscos pendentes, próximos passos e uma conclusão clara.  
4) O script/rotina de ORR da S22 produz um scorecard agregado S22_G8_orr.json com decisão GO/NO_GO, linkando para os demais scorecards e evidências.

Métricas mínimas:

- gates_total: deve ser 8.  
- gates_passed: deve ser 8 para GO.  
- orr_decision: "GO" ou "NO_GO".  
- missing_evidence_count: deve ser 0 para GO.

Evidências obrigatórias:

- Scorecard agregado S22_G8_orr.json com status, orr_decision e referências aos demais scorecards.  
- Wrap humano docs/sprint_22_orr_summary.md.  
- Manifesto/índice de evidências da S22 (por exemplo, MANIFEST.json em out/evidence/S22_orr/) para auditoria futura.

## 11. Definição de sucesso do Capítulo 2

O Capítulo 2 da Sprint 22 é bem-sucedido se, ao fim da sprint, for possível executar os gates S22-G0…S22-G7 de forma reprodutível, com scripts, testes e evidências claras, e tomar a decisão de GO/NO_GO na S22 com base em fatos.

Na prática, isso significa que qualquer pessoa olhando para os scorecards, documentos e evidências consegue responder sem adivinhação: “a ingestão 2.0 do Inspectah é confiável, operável e pronta para alimentar S23–S25 e, depois, a Truth-DB?”. Se a resposta for sim e todos os gates estiverem verdes, S22-G8 registra GO. Caso contrário, os gates em vermelho deixam explícito o que precisa ser corrigido antes de avançar.

