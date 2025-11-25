# Inspectah — Sprint 22 — Capítulo 3 (v2)

## 1. Objetivo do Capítulo 3

Este capítulo transforma a visão e os gates da Sprint 22 em um mapa concreto de código, arquivos, scripts, testes, scorecards, métricas e evidências dentro do repositório do Inspectah.

Ele responde, de forma rastreável, a três perguntas centrais:

1) Onde vive cada parte da ingestão 2.0 (domínio, API, UI, persistência, métricas)?  
2) Como cada gate S22-G0…S22-G8 é executado, em termos de comandos e arquivos?  
3) Onde ficam os artefatos de prova (scorecards e evidências) que demonstram que a S22 entregou o que prometeu?

O Capítulo 4 vai se apoiar diretamente neste filemap para definir o plano de execução (ordem de implementação, comandos, checklists). Aqui a meta é que qualquer pessoa que abra o repo consiga navegar S22 inteira apenas com este capítulo em mãos.

---

## 2. Arquitetura de pastas da S22

A Sprint 22 se encaixa na estrutura já usada no Inspectah, introduzindo uma “vertical” de ingestão 2.0 e mantendo a separação domínio ⇄ API ⇄ UI ⇄ operações.

Visão geral:

- docs/ — capítulos, anexos de modelos/FSM/contratos, observabilidade, cenários e ORR da S22.  
- app/ingestion/ — núcleo de domínio da ingestão 2.0 (modelos, FSM, serviços, repositórios, integração com scheduler).  
- app/api/ingestion/ — rotas HTTP específicas de ingestão (contratos externos).  
- app/admin/ingestion/ — backend da UI de admin voltado à ingestão.  
- db/ — migrations de schema da S22.  
- data/s22_scenarios/ — fixtures de cenários end-to-end.  
- tests/ingestion/ — suíte de testes da S22 (G1…G7).  
- metrics/ e dashboards/ — definição de métricas e painel mínimo da ingestão 2.0.  
- bin/ — scripts de gates S22-G0…S22-G8.  
- out/scorecards/ e out/evidence/ — scorecards e evidências da S22.

Todas as referências de gates, no Capítulo 2, terão pelo menos um “ponto de ancoragem” neste mapa.

---

## 3. Documentação da S22 (docs/)

A documentação da Sprint 22 é organizada em capítulos e anexos, mantendo o padrão do projeto.

### 3.1. Capítulos principais

- docs/sprint_22_capitulo_1_contexto.md  
- docs/sprint_22_capitulo_2_gates.md  
- docs/sprint_22_capitulo_3_filemap.md  
- docs/sprint_22_capitulo_4_execucao.md

Cada capítulo referencia explicitamente os anteriores. Este Capítulo 3 aponta para o 1 e o 2; o Capítulo 4 aponta para todos.

### 3.2. Anexos por gate

- docs/sprint_22_g0_summary.md — alinhamento de contexto e escopo (G0).  
- docs/sprint_22_g1_modelos_e_invariantes.md — modelos IngestionConfig/IngestionRun + invariantes (G1).  
- docs/sprint_22_g2_contratos_de_servico.md — contratos de serviço/API (G2).  
- docs/sprint_22_g3_maquina_de_estados.md — FSM de IngestionRun (G3).  
- docs/sprint_22_g4_persistencia_e_dados_brutos.md — modelo de persistência + consultas exemplo (G4).  
- docs/sprint_22_g5_admin_ui.md — fluxos de UI, prints anotados, decisões de UX (G5).  
- docs/sprint_22_g6_observabilidade.md — métricas, logs, painéis, thresholds de sanidade (G6).  
- docs/sprint_22_g7_cenarios_e_runbook.md — cenários E2E + runbooks (G7).  
- docs/sprint_22_orr_summary.md — wrap humano da S22 (G8).

Cada um desses arquivos é citado explicitamente nos scripts bin/s22_g*_*.sh e nos scorecards correspondentes.

---

## 4. Domínio da ingestão 2.0 (app/ingestion/)

O coração da ingestão 2.0 vive em app/ingestion/. Aqui estão os conceitos que não podem depender de detalhes de transporte ou UI.

### 4.1. Estrutura de arquivos

- app/ingestion/__init__.py  
- app/ingestion/models.py  
- app/ingestion/schemas.py  
- app/ingestion/state_machine.py  
- app/ingestion/services.py  
- app/ingestion/repository.py  
- app/ingestion/scheduler_adapter.py  
- app/ingestion/observability.py  
- app/ingestion/errors.py

### 4.2. Papéis detalhados

- models.py  
  - Define IngestionConfig, IngestionRun e, se necessário, tabelas auxiliares de payload bruto/ref.  
  - Reflete fidedignamente docs/sprint_22_g1_modelos_e_invariantes.md.  
  - Aplica restrições básicas (por exemplo, enum de estados, FKs para Source).

- schemas.py  
  - DTOs e Pydantic-schemas usados por services, API e UI.  
  - Expõe versões estáveis de payloads de request/response para rotas de ingestão.

- state_machine.py  
  - Implementa a FSM descrita em docs/sprint_22_g3_maquina_de_estados.md.  
  - Expõe funções como apply_event(run, event) que garantem transições válidas.  
  - Centraliza a lógica de estados, para evitar ifs espalhados.

- services.py  
  - Orquestra workflows de ingestão: start_ingestion_run, complete_ingestion_run, fail_ingestion_run, reprocess_run, toggle_ingestion_mode, etc.  
  - Aplica invariantes de G1 + transições de G3.  
  - Não conhece HTTP, apenas contratos internos.

- repository.py  
  - Lida com persistência: CRUD de IngestionConfig/IngestionRun, queries principais (por fonte, por período), acesso a dados brutos.  
  - Representa a camada que esconderá detalhes de ORM/SQL do resto do sistema.

- scheduler_adapter.py  
  - Exposição de hooks para o mecanismo de agendamento adotado (cron interno, celery-like, etc.).  
  - Funções como run_scheduled_ingestions(now) que:  
    - localizam configs elegíveis (modo AUTOMATIC, intervalos vencidos),  
    - disparam runs via services.py,  
    - registram resultados.

- observability.py  
  - Registro de métricas e logs estruturados da ingestão.  
  - Integração com metrics/ingestion_s22.py.  
  - Helpers para logar início/fim de run com run_id/source_id e resultados.

- errors.py  
  - Define exceções específicas da ingestão (FonteDesabilitada, ModoIncompativel, RunConflitante, etc.).  
  - Ajuda a manter erros padronizados entre services e API.

---

## 5. API de ingestão (app/api/ingestion/)

A camada de API adapta o domínio para HTTP/REST (ou equivalente). Nada de lógica de negócio aqui; apenas marshaling de requests/responses.

### 5.1. Estrutura

- app/api/ingestion/__init__.py  
- app/api/ingestion/routes.py  
- app/api/ingestion/dependencies.py

### 5.2. Endpoints típicos

Em routes.py, endpoints como:

- POST /admin/ingestion/{source_id}/run  
  - Aciona ingestão manual.  
  - Usa services.start_ingestion_run(source_id, mode="MANUAL").

- POST /admin/ingestion/{source_id}/toggle-mode  
  - Alterna modo MANUAL_ONLY/AUTOMATIC.  
  - Usa services.toggle_ingestion_mode().

- GET /admin/ingestion/{source_id}/runs  
  - Lista IngestionRuns de uma fonte, paginado.  
  - Usa repository.list_runs_by_source().

- GET /admin/ingestion/runs/{run_id}  
  - Detalhes de um run específico.

Esses endpoints implementam os contratos definidos em docs/sprint_22_g2_contratos_de_servico.md e são usados diretamente pelos testes de G2.

---

## 6. Backend da UI de admin (app/admin/ingestion/)

A UI de admin, entregue em S21, ganha a camada de ingestão 2.0 com handlers próprios.

### 6.1. Estrutura

- app/admin/ingestion/__init__.py  
- app/admin/ingestion/views.py  
- app/admin/ingestion/adapters.py  
- app/admin/ingestion/templates/ingestion/ (se templates server-side forem usados)

### 6.2. Responsabilidades

- views.py  
  - Expor páginas como:  
    - Lista de fontes com colunas de ingestão (modo, última execução, estado).  
    - Detalhe da fonte com histórico de runs.  
    - Ações para acionar ingestão manual.  
  - Consumir API interna/serviços de ingestão.

- adapters.py  
  - Converter modelos de domínio/schemas em view models adequados para UI.

- templates/ingestion/  
  - Implementar layouts usados nos fluxos descritos em docs/sprint_22_g5_admin_ui.md.

Os fluxos de G5 (max 3 cliques para achar última ingestão, etc.) devem ser rastreáveis até esses arquivos.

---

## 7. Persistência e schema (db/ e data/)

### 7.1. Migrations

- db/migrations/022_sprint22_ingestion.sql  
  - Cria tabelas/alterações para IngestionConfig, IngestionRun e, se adotado, tabela de payload bruto.  
  - Documenta FKs para Source e constraints de integridade coerentes com G1.

### 7.2. Dados brutos

Duas opções, uma delas precisa ser escolhida no Capítulo 4 e descrita em docs/sprint_22_g4_persistencia_e_dados_brutos.md:

1) **Armazenamento em DB**  
   - Tabelas ingestion_raw_data (run_id, chunk_index, payload, content_type, etc.).  
   - Recomendado se volume/forma forem compatíveis.

2) **Armazenamento em arquivos**  
   - data/ingestion_raw/{source_id}/{YYYY}/{MM}/{DD}/{run_id}.json (ou ndjson).  
   - IngestionRun guarda path/URI.

Independente da opção, o filemap fixa:

- db/migrations/022_sprint22_ingestion.sql como local da migration principal;  
- data/ingestion_raw/ como raiz, caso a opção arquivos seja adotada;  
- repository.py como única camada que conhece detalhes desta decisão.

---

## 8. Dados de cenário e fixtures (data/s22_scenarios/)

Para reprodutibilidade dos cenários G7, existe um diretório dedicado:

- data/s22_scenarios/  
  - news_rss/  
    - fonte_valor_economico.yaml  
    - fonte_globo_demo.yaml  
  - data_api/  
    - fonte_ibge_populacao.yaml  
  - prices_feed/ (ou outro tipo relevante)  
    - fonte_preco_btc_demo.yaml

Cada arquivo YAML descreve uma fonte e parâmetros extras usados no cenário (por exemplo, filtros, endpoints exatos, chaves de API fake para ambiente de teste). Os runbooks em docs/sprint_22_g7_cenarios_e_runbook.md apontam diretamente para estes arquivos.

---

## 9. Suíte de testes da S22 (tests/ingestion/)

Os testes da ingestão 2.0 são organizados de forma espelhada aos gates.

- tests/ingestion/test_models_and_invariants.py — cobre G1.  
- tests/ingestion/test_service_contracts.py — cobre G2.  
- tests/ingestion/test_state_machine.py — cobre G3.  
- tests/ingestion/test_persistence.py — cobre G4.  
- tests/ingestion/test_admin_ui_flows.py — cobre G5 (fluxos backend/API).  
- tests/ingestion/test_observability.py — cobre G6.  
- tests/ingestion/test_e2e_scenarios_s22.py — cobre G7.

A convenção é: qualquer arquivo bin/s22_gN_*.sh que rode testes aponta explicitamente para um desses arquivos ou para uma marcação de pytest (por exemplo, -m "s22_g1") definida dentro deles.

---

## 10. Scripts de gates S22 (bin/)

Os scripts de gates materializam o caminho para validar cada G0…G8.

### 10.1. Scripts individuais

- bin/s22_g0_grounding.sh  
  - Verifica presença/consistência de docs/sprint_22_capitulo_1_contexto.md e docs/sprint_22_g0_summary.md.  
  - Gera out/scorecards/S22_G0_grounding.json.  
  - Move evidências textuais para out/evidence/S22_G0_grounding/.

- bin/s22_g1_models_and_invariants.sh  
  - Roda pytest tests/ingestion/test_models_and_invariants.py.  
  - Gera out/scorecards/S22_G1_models_and_invariants.json com métricas (contagem de invariantes, taxa de sucesso).  
  - Armazena logs em out/evidence/S22_G1_models_and_invariants/.

- bin/s22_g2_service_contracts.sh  
  - Roda pytest tests/ingestion/test_service_contracts.py.  
  - Gera out/scorecards/S22_G2_service_contracts.json.  
  - Logs em out/evidence/S22_G2_service_contracts/.

- bin/s22_g3_state_machine.sh  
  - Roda pytest tests/ingestion/test_state_machine.py.  
  - Gera out/scorecards/S22_G3_state_machine.json.  
  - Evidências de FSM em out/evidence/S22_G3_state_machine/.

- bin/s22_g4_persistence.sh  
  - Roda pytest tests/ingestion/test_persistence.py + scripts de consulta exemplares (separados em tools/ ou scripts/).  
  - Gera out/scorecards/S22_G4_persistence.json.  
  - Dumps de consultas em out/evidence/S22_G4_persistence/.

- bin/s22_g5_admin_ui.sh  
  - Roda pytest tests/ingestion/test_admin_ui_flows.py.  
  - Copia prints/recordings de UI (produzidos manualmente ou via ferramenta) para out/evidence/S22_G5_admin_ui/.  
  - Gera out/scorecards/S22_G5_admin_ui.json.

- bin/s22_g6_observability.sh  
  - Executa testes/checs em tests/ingestion/test_observability.py.  
  - Opcionalmente, chama script dedicado: python metrics/check_ingestion_health.py.  
  - Gera out/scorecards/S22_G6_observability.json.  
  - Evidências em out/evidence/S22_G6_observability/.

- bin/s22_g7_e2e_scenarios.sh  
  - Usa data/s22_scenarios/* e tests/ingestion/test_e2e_scenarios_s22.py.  
  - Gera out/scorecards/S22_G7_e2e_scenarios.json.  
  - Evidências E2E em out/evidence/S22_G7_e2e_scenarios/.

- bin/s22_g8_orr.sh  
  - Consolida scorecards S22_G0…S22_G7.  
  - Valida presença de docs e evidências chave.  
  - Gera out/scorecards/S22_G8_orr.json e MANIFEST.json em out/evidence/S22_orr/.  
  - Não reexecuta testes; apenas agrega.

### 10.2. Wrapper de sprint

- bin/s22_all_gates.sh  
  - Executa G0…G7 em ordem, falhando no primeiro gate com status FAIL.  
  - Usado em CI local e no workflow dedicado.

---

## 11. Scorecards e evidências (out/scorecards/ e out/evidence/)

### 11.1. Scorecards

- out/scorecards/S22_G0_grounding.json  
- out/scorecards/S22_G1_models_and_invariants.json  
- out/scorecards/S22_G2_service_contracts.json  
- out/scorecards/S22_G3_state_machine.json  
- out/scorecards/S22_G4_persistence.json  
- out/scorecards/S22_G5_admin_ui.json  
- out/scorecards/S22_G6_observability.json  
- out/scorecards/S22_G7_e2e_scenarios.json  
- out/scorecards/S22_G8_orr.json

Cada JSON contém, no mínimo: status, métricas principais do gate, timestamp, commit hash e caminho das evidências.

### 11.2. Evidências

- out/evidence/S22_G0_grounding/  
- out/evidence/S22_G1_models_and_invariants/  
- out/evidence/S22_G2_service_contracts/  
- out/evidence/S22_G3_state_machine/  
- out/evidence/S22_G4_persistence/  
- out/evidence/S22_G5_admin_ui/  
- out/evidence/S22_G6_observability/  
- out/evidence/S22_G7_e2e_scenarios/  
- out/evidence/S22_orr/

Em out/evidence/S22_orr/ vive o MANIFEST.json que referencia os demais diretórios de evidência e o docs/sprint_22_orr_summary.md.

---

## 12. Métricas e painéis (metrics/ e dashboards/)

### 12.1. Métricas

- metrics/ingestion_s22.py  
  - Define counters/gauges/histograms como:  
    - ingestion_runs_total{source_id, status}  
    - ingestion_latency_ms_bucket{source_id}  
    - ingestion_last_success_timestamp{source_id}  
    - ingestion_last_failure_timestamp{source_id}

Este módulo é chamado a partir de app/ingestion/observability.py.

### 12.2. Painéis

- dashboards/ingestion_s22_overview.json  
  - Painel mínimo contendo:  
    - gráfico de runs_total por fonte;  
    - gráfico de taxa de sucesso/falha;  
    - tabela de fontes sem runs recentes;  
    - gráfico de latência p95.

A presença e consistência desses arquivos são verificadas por bin/s22_g6_observability.sh (ao menos superficialmente).

---

## 13. Integração com CI e ORR

### 13.1. Workflow de CI da S22

- .github/workflows/s22-gates.yml  
  - Job principal roda bin/s22_all_gates.sh.  
  - Publica artefatos out/scorecards/ e out/evidence/ como attachments de CI (ou subset relevante).  
  - Opcionalmente, roda apenas subset de gates em PRs pequenos (por tag/matriz).

### 13.2. Integração com ORR geral

- Atualização de scripts ORR globais (por exemplo, bin/orr_all.sh) para incluir leitura de S22_G8_orr.json na visão macro de sprints.  
- docs/orr_master_index.md (ou equivalente) passa a referenciar a S22 como sprint concluída, apontando para docs/sprint_22_orr_summary.md.

---

## 14. Definição de sucesso do Capítulo 3

O Capítulo 3 é considerado bem-sucedido se, ao iniciar o Capítulo 4, o Squad 2 conseguir:

- apontar, sem dúvida, onde deve implementar cada parte da ingestão 2.0;  
- saber exatamente quais scripts executar para validar cada gate;  
- localizar rapidamente scorecards e evidências da S22;
- conectar qualquer gate descrito no Capítulo 2 a arquivos concretos do repositório.

Se um desenvolvedor novo conseguir abrir apenas este capítulo, navegar o repo e reproduzir mentalmente a arquitetura + fluxo de validação da ingestão 2.0, então o Capítulo 3 (v2) cumpriu seu papel e a S22 está pronta para entrar em modo de execução disciplinada no Capítulo 4.