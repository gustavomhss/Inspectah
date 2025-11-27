# 4.3 – Arquitetura & Filemap (Execução) – v2

Este 4.3 descreve a **arquitetura física** da sprint no repositório do Inspectah: onde cada peça vive (código, scripts, testes, scorecards, evidências, bundles, docs, workflows) e como isso se conecta ao desenho lógico do Cap. 3 e aos gates do 4.2.

Ele responde, de forma objetiva, a três perguntas:

1. *Se eu pegar qualquer entidade/fluxo do Cap. 3, onde está o código que implementa isso?*
2. *Se eu pegar qualquer gate do 4.2, quais scripts e arquivos ele toca/gera no filesystem?*
3. *Se eu quiser auditar a sprint, quais pastas e arquivos preciso abrir e em que ordem?*

O foco aqui é execução: **filemap como contrato**, não como sugestão.

---

## 4.3.1 – Princípios de organização física

Antes do mapa em si, o 4.3 fixa alguns princípios que valem para todas as sprints do arco S21–S25:

1. **Uma função → um lugar canônico**  
   Cada função macro do sistema (ingestão, claims, comitê, debunker, truth, evidências, observabilidade, gates) tem um diretório canônico. Scripts de gate em `bin/`, código de domínio em `app/`, testes em `tests/`, documentação em `docs/`, artefatos gerados em `out/`, automação de CI em `.github/workflows/`.

2. **Naming semântico e estável**  
   Tudo o que é específico da sprint leva o prefixo/sufixo `sXX` (número da sprint) e, para gates, o código `G0…G8`. Exemplos: `bin/s22_g2_ingestion.sh`, `out/scorecards/S22_G2_ingestion.json`, `docs/sprint_22_cap_4_execucao_e_evidencias.md`.

3. **Separação limpa entre fonte e evidência**  
   Código, scripts e config vivem em diretórios de fonte (`app`, `bin`, `docs`, `tests`). Saída de execução (logs, dumps, scorecards, bundles) vive apenas em `out/`. Nada gerado automaticamente deve ser salvo fora de `out/`.

4. **Simetria local ↔ CI**  
   O filemap é desenhado para que **os mesmos caminhos** funcionem em ambiente local, Codespaces e GitHub Actions. Workflows chamam scripts em `bin/` e gravam em `out/` – nunca reimplementam lógica dentro de YAML.

---

## 4.3.2 – Topologia macro do repositório na sprint

No contexto desta sprint, o repositório do Inspectah pode ser visto assim (pastas principais relevantes para execução):

- `app/` – código de aplicação (domínio e serviços).
- `bin/` – scripts executáveis (gates, cenários, utilitários de sprint).
- `docs/` – documentação de sprint e capítulos do Playbook.
- `tests/` – testes automatizados (unitários, integrados, e2e).
- `out/` – artefatos gerados (scorecards, evidências, bundles).
- `.github/workflows/` – pipelines de CI/CD que chamam scripts da sprint.

A seguir, detalhamos a função de cada um, mapeando entidades/fluxos do Cap. 3 e gates do 4.2.

---

## 4.3.3 – `app/` – código de domínio e serviços

O diretório `app/` abriga o código que implementa os blocos funcionais descritos no Cap. 3.3 (modelos) e 3.4 (integrações). Para a espinha dorsal S21–S25, a divisão recomendada é:

- `app/ingestion/`  
  Implementações relacionadas a **fontes e ingestão 2.0**:
  - `app/ingestion/models.py` – modelos de domínio (ou wrappers de ORM) para `Source`, `IngestionConfig`, `IngestionRun`, `IngestionItemRaw`, `IngestionItemNormalized`.
  - `app/ingestion/services.py` – orquestração de ingestão: criação de runs, agendamento, normalização, interação com clientes externos.
  - `app/ingestion/routes.py` (se houver API) – endpoints de administração/execução de ingestões.

- `app/brain/` ou `app/claims/`  
  Implementações ligadas ao **Cérebro v1**:
  - `app/brain/models.py` – `InterpretationUnit`, `ClassificationResult`, `Claim`.
  - `app/brain/services.py` – pipeline que consome itens normalizados e produz unidades interpretadas e claims.
  - `app/brain/routes.py` – endpoints para debug/consulta de claims (se previstos na sprint).

- `app/committee/`  
  Camada de **comitês de avaliação**:
  - `app/committee/models.py` – `CommitteeEvaluation`, `CommitteeDecision`.
  - `app/committee/services.py` – agregação de avaliações, cálculo de vereditos, interface com agentes.

- `app/debunker/`  
  Camada de **contestação e análise crítica**:
  - `app/debunker/models.py` – `DebunkIssue`, `DebunkTask`.
  - `app/debunker/services.py` – abertura de issues, roteamento de tasks, integração com evidências.

- `app/truthdb/`  
  Núcleo de **Truth-DB & máquina de estados da verdade**:
  - `app/truthdb/models.py` – `TruthRecord`, `TruthChangeEvent`.
  - `app/truthdb/services.py` – transições de estado, política de promoção/rebaixamento, validações de invariantes.

- `app/clients/`  
  Connectors externos:
  - `app/clients/news_portal.py` – cliente para RSS/HTTP de fontes de notícias;
  - `app/clients/open_data.py` – cliente para dados abertos (ex.: IBGE);
  - `app/clients/evidence_vault.py` – cliente para o Evidence Vault (armazenamento de snapshots, hashes).

- `app/observability/` (ou `app/metrics/`, `app/logging/`)
  - helpers para métricas, logs estruturados e tracing (wrappers para Prometheus/OpenTelemetry, etc.).

- `app/models/` e `app/schemas/`  
  Em algumas versões do repo, os modelos ORM e schemas Pydantic podem estar centralizados aqui, com arquivos como:
  - `app/models/ingestion.py`, `app/models/claims.py`, `app/models/truthdb.py`;
  - `app/schemas/events.py`, `app/schemas/api.py`.

O 4.3 fixa que **qualquer entidade citada no 3.3 deve ter um módulo óbvio em `app/`**. Se um dev procurar “Claim”, deve encontrá-la em `app/brain/models.py` ou equivalente, e ver claramente os serviços associados.

---

## 4.3.4 – `bin/` – scripts de gates e cenários

`bin/` é o “painel de controle” da execução. Tudo o que o 4.2 descreve como gate ou cenário oficial aparece aqui como script versionado e executável.

### 4.3.4.1 – Scripts de gates

Para a sprint `XX`, a convenção é:

- `bin/sXX_g0_setup.sh` – Gate G0 (Grounding & Setup);
- `bin/sXX_g1_models_and_migrations.sh` – Gate G1 (Schema & invariantes);
- `bin/sXX_g2_ingestion.sh` – Gate G2 (Ingestão 2.0);
- `bin/sXX_g3_brain_and_claims.sh` – Gate G3 (Cérebro & Claims);
- `bin/sXX_g4_committees_and_debunker.sh` – Gate G4 (Comitês & Debunker);
- `bin/sXX_g5_truthdb.sh` – Gate G5 (Truth-DB);
- `bin/sXX_g6_observability_and_failures.sh` – Gate G6 (Observabilidade & Falhas);
- `bin/sXX_g7_orr.sh` – Gate G7 (ORR de Sprint);
- `bin/sXX_g8_go_no_go.sh` – Gate G8 (GO/NO-GO).

Cada script:
- é idempotente;
- recebe qualquer config via variáveis de ambiente (nunca hardcode segredos/caminhos absolutos);
- ao final, grava scorecards e evidências em locais previsíveis (ver 4.3.6).

### 4.3.4.2 – Scripts de cenários ponta a ponta e utilitários

Além dos gates, a sprint pode definir cenários oficiais de demonstração e debugging:

- `bin/sXX_scenario_01_noticia_economica.sh` – fluxo completo de uma notícia de economia até TruthRecord;
- `bin/sXX_scenario_02_dado_oficial_vs_discurso.sh` – conflito entre dado IBGE e declaração política;
- `bin/sXX_scenario_03_contestacao_depois_de_fact.sh` – claim vira FACT e é contestada depois.

Também é recomendado um utilitário para empacotar evidências:

- `bin/sXX_make_bundle.sh` – gera `out/bundles/inspectah_sXX_evidence_bundle.zip` a partir de `out/scorecards/` e `out/evidence/`.

---

## 4.3.5 – `tests/` – espelho de domínio e gates

Os testes automatizados são organizados para espelhar tanto o domínio do Cap. 3 quanto os gates do 4.2:

- `tests/ingestion/` – cobre principalmente o que G2 verifica (runs, itens, normalização, unicidade, erros externos);
- `tests/brain/` ou `tests/claims/` – cobre G3 (pipeline de interpretação/claims);
- `tests/committee/` – cobre aspectos unitários/integrados de G4 (consolidação de decisões);
- `tests/debunker/` – cobre G4 pelo lado do debunker (criação/resolução de issues/tasks);
- `tests/truthdb/` – cobre G5 (state machine, invariantes de Truth-DB);
- `tests/schema/` (ou similar) – sanity de migrações e invariantes estruturais (G1);
- `tests/e2e/` – cenários ponta a ponta invocados por G3–G6 quando conveniente.

O 4.3 não descreve cada teste individual, mas fixa o contrato de organização: 
> Se um gate fala sobre um comportamento, deve haver testes em `tests/` que exercitam esse comportamento, e a localização dos testes deve ser previsível pelo nome.

---

## 4.3.6 – `out/` – scorecards, evidências e bundles

O diretório `out/` é a **área de artefatos** da sprint. Nada aqui é versionado no repositório (normalmente é ignorado por `.gitignore`), mas a estrutura é estável e descrita no 4.3.

### 4.3.6.1 – Scorecards

Scorecards vivem em `out/scorecards/` e seguem o padrão:

- `out/scorecards/SXX_G0_setup.json`
- `out/scorecards/SXX_G1_models_and_migrations.json`
- `out/scorecards/SXX_G2_ingestion.json`
- `out/scorecards/SXX_G3_brain_and_claims.json`
- `out/scorecards/SXX_G4_committees_and_debunker.json`
- `out/scorecards/SXX_G5_truthdb.json`
- `out/scorecards/SXX_G6_observability_and_failures.json`
- `out/scorecards/SXX_G7_orr.json`
- `out/scorecards/SXX_G8_go_no_go.json`

Cada scorecard é um JSON com:
- status do gate (OK/WARN/FAIL);
- métricas-chave do gate (ver 4.2.3);
- metadados de execução (timestamp, commit hash, ambiente).

### 4.3.6.2 – Evidências

Evidências ricas (logs, dumps de dados, capturas de painel, etc.) vivem em `out/evidence/`, organizadas por gate e/ou cenário:

- `out/evidence/SXX_G0_setup/` – saída de setup, checagem de ambiente.
- `out/evidence/SXX_G1_schema_sanity/` – resultados de queries de integridade.
- `out/evidence/SXX_G2_ingestion/` – amostras de `IngestionItemRaw/Normalized`, health checks de fontes.
- `out/evidence/SXX_G3_claims/` – comparações input→claims, JSON com claims geradas.
- `out/evidence/SXX_G4_committees/` – trilhas completas de committee→debunker.
- `out/evidence/SXX_G5_truth_timelines/` – timelines de truth por claim.
- `out/evidence/SXX_G6_failures/` – logs, métricas e traces dos cenários de falha.
- `out/evidence/SXX_G7_orr_report/` – relatório ORR da sprint (se textual).

Quando existirem scripts de cenário (`bin/sXX_scenario_*.sh`), é recomendável também:
- `out/evidence/SXX_scenario_01_*` – artefatos do cenário 1;
- `out/evidence/SXX_scenario_02_*` – artefatos do cenário 2; etc.

### 4.3.6.3 – Bundles

Bundles de evidências ficam em `out/bundles/`:

- `out/bundles/inspectah_sXX_evidence_bundle.zip`

Esse bundle é produzido por `bin/sXX_make_bundle.sh` ou incorporado em `bin/sXX_g7_orr.sh`/`bin/sXX_g8_go_no_go.sh` e normalmente contém:
- todos os JSON de `out/scorecards/`;
- subpastas relevantes de `out/evidence/`;
- um manifesto (por exemplo, `bundle_manifest.json`) descrevendo conteúdo, hash, commit e ambiente.

---

## 4.3.7 – `docs/` – capítulos da sprint e cenários de execução

`docs/` é onde o Sprint Playbook v2 “ganha corpo” no repositório. Para o Cap. 4 e esta sprint, esperamos:

- `docs/sprint_xx_cap_4_execucao_e_evidencias.md` – capítulo 4 macro, referenciando este 4.3.
- `docs/sprint_xx_cenarios_execucao.md` – lista de cenários oficiais: descrição em linguagem natural, objetivos, passos de alto nível, ligação com scripts de `bin/` e evidências em `out/evidence/`.
- `docs/sprint_xx_lessons_execucao.md` – lições de execução que serão destiladas no Cap. 6.

Outros capítulos (1–3, 5–6) também vivem em `docs/`, mas o 4.3 se limita a apontar como o Cap. 4 se ancora neles (por exemplo, links cruzados entre Cap. 3.3 e a organização de `app/`, ou entre Cap. 2 e a organização de `bin/` + `out/`).

---

## 4.3.8 – `.github/workflows/` – integração com CI/CD

O 4.3 fixa o princípio de que **CI não reimplementa lógica**: os workflows chamam scripts de `bin/` e dependem do filemap descrito aqui.

Exemplo de workflows esperados:

- `.github/workflows/sXX_gates.yml`  
  Pipeline principal da sprint, encadeando G0–G7 em jobs/steps que chamam:
  - `PYTHONPATH=. bin/sXX_g0_setup.sh`
  - `PYTHONPATH=. bin/sXX_g1_models_and_migrations.sh`
  - …
  - `PYTHONPATH=. bin/sXX_g7_orr.sh`

- `.github/workflows/sXX_pr_checks.yml`  
  Pipeline de PR que roda subset de gates (tipicamente G0–G3) e testes unitários/integrados relacionados.

Cada workflow:
- assume o mesmo layout de `app/`, `bin/`, `tests/` e `out/` que a execução local;
- publica `out/scorecards/` e, opcionalmente, partes de `out/evidence/` como artefatos de build.

---

## 4.3.9 – Check-list de sanidade do filemap

Para garantir que o filemap está coerente com o Cap. 3 e o 4.2, o 4.3 define um check-list simples que pode virar até um mini‑script de sanity:

1. **Existem scripts para todos os gates G0–G8 em `bin/` com o padrão `sXX_gY_*.sh`?**
2. **Para cada gate descrito no 4.2, existe um scorecard correspondente em `out/scorecards/` com o nome esperado?**
3. **Para cada grupo de entidades do Cap. 3.3 (ingestão, cérebro, comitê, debunker, truth), existe um módulo óbvio em `app/`?**
4. **Testes relacionados a cada gate existem em `tests/` e seguem a organização de domínio?**
5. **Docs da sprint (especialmente o Cap. 4 e cenários de execução) estão presentes em `docs/` com nomes padronizados?**
6. **`out/` é o único lugar onde scorecards, evidências e bundles são gerados?**
7. **Workflows de CI chamam scripts de `bin/` e escrevem em `out/`, sem duplicar lógica?**

Se qualquer item do check-list falhar, não é apenas um detalhe estético; é um sinal de que a execução corre o risco de voltar para o modo “tribal” que o Capítulo 4 quer eliminar.

---

Com isso, o 4.3 entrega um filemap de execução **denso, explícito e navegável**: qualquer pessoa (humana ou agente) que conheça os Capítulos 3 e 4 consegue localizar rapidamente o código responsável por um comportamento, o script que o testa, o scorecard que registra seu estado e a evidência que prova que ele funcionou. É o elo entre arquitetura lógica, gates de qualidade e prática diária de desenvolvimento no Inspectah.