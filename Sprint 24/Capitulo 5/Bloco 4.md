# 5.4 – Execução & Evidências (Produto & Experiência) – v2 extremo

Este 5.4 descreve **como operar e comprovar** a camada de produto do Capítulo 5 na prática. Se 5.1 fixa o contexto e dores, 5.2 define gates e métricas, e 5.3 desenha a arquitetura/filemap, o 5.4 responde:

- como subir e validar o ambiente de Casos Inspectah (backend + UI + configs);
- como executar fluxos reais para as personas A/B/C ligados aos gates GP1–GP4;
- como gerar evidências reprodutíveis em `out/evidence/` para cada gate;
- como conectar essas evidências ao ORR (G7) e à decisão de GO/NO-GO (G8);
- como deixar um trilho claro de feedback e próximos passos para o Cap. 6.

O objetivo é simples e rígido: qualquer pessoa do squad, com este subcapítulo em mãos e o repo em estado consistente, deve conseguir **reconstituir a experiência de produto desta sprint ponta a ponta**, sem depender da memória de ninguém.

---

## 5.4.1 – Objetivo operacional e premissas

A camada de produto do Cap. 5 só faz sentido se conseguir mostrar, com casos concretos, que:

- os **Casos Inspectah** canônicos estão definidos, ancorados na Truth-DB e acessíveis (GP1);
- cada caso possui uma **visão unificada** que atende a Persona A (GP2);
- existem **coleções temáticas navegáveis** que atendem a Persona B (GP3);
- curadores internos têm um **fluxo formal** para criar/editar casos e coleções, e a sprint mede um conjunto mínimo de **métricas de produto** (GP4).

Premissas para o 5.4:

1. A anatomia técnica do motor de verdade está estável (Cap. 3 e Cap. 4 completos para S21–S25).
2. O filemap de produto definido em 5.3 está implementado, pelo menos em sua versão mínima (módulo `app/cases/`, rotas de UI, `docs/cases/`, scripts em `bin/`).
3. Existem N casos canônicos definidos em `docs/cases/case_*.yaml` e pelo menos T coleções em `collections.yaml`, conforme 5.2.

A partir daqui, o 5.4 passa a tratar de **procedimentos**: sequência de passos, fluxos, scripts e evidências.

---

## 5.4.2 – Pré-flight: checklist antes de qualquer demo ou métrica

Antes de executar fluxos de persona ou coletar evidências, o squad segue este checklist rápido de sanidade:

1. Repositório sincronizado
   - Branch da sprint (ex.: `feature/sXX_cap5_produto`) atualizada com `main`.
   - Dependências do backend instaladas (ambiente virtual ou containers).
   - Dependências do frontend instaladas (`frontend/inspectah-ui`).

2. Motor de verdade saudável
   - Gates técnicos críticos (ingestão, brain, comitês, truth) passando em ambiente local/staging.
   - Base de dados contém Claims, TruthRecords, TruthChangeEvents, decisões de comitê e issues de debunker necessárias para os casos canônicos.

3. Config de casos/coleções carregável
   - Diretório `docs/cases/` presente com `case_model.md`, `case_*.yaml` e `collections.yaml`.
   - `bin/sXX_cases_check.sh` executa sem erro de schema ou referência quebrada.

4. Case Layer ativa
   - Servidor backend rodando com módulo `app/cases/` registrado.
   - Endpoints `/api/cases`, `/api/cases/{case_id}`, `/api/collections`, `/api/collections/{collection_id}` respondendo nominalmente.

5. Cockpit de casos disponível
   - `frontend/inspectah-ui` rodando em modo dev ou com build estático servido.
   - Rotas `/cases`, `/cases/:caseId`, `/collections`, `/collections/:collectionId` acessíveis.

Se qualquer item do pré-flight falhar, as demos e métricas são consideradas inválidas até a correção.

---

## 5.4.3 – Runbook operacional padrão da camada de produto

Esta seção define um **runbook único**, que serve de base tanto para uso local quanto para ambientes de staging.

### 5.4.3.1 – Preparar dados e configs de casos

1. Garantir que os scripts de ingestão e brain já rodaram pelo menos uma vez, gerando Claims e alimentando a Truth-DB.
2. Se existir um script de seed específico para casos (ex.: `bin/sXX_cases_seed.sh`), executá-lo em ambiente de demo para garantir dados mínimos coerentes com os casos canônicos.
3. Conferir manualmente que os arquivos em `docs/cases/` refletem exatamente os casos que se pretende demonstrar (casos canônicos atualizados, sem TODOs ou placeholders).
4. Executar `bin/sXX_cases_check.sh` e verificar o relatório em `out/evidence/SXX_cases_check/report.json`.
   - Se o report indicar casos com IDs de Claim/TruthRecord inexistentes, ou coleções com `case_id` fantasma, o runbook é interrompido até a correção dos arquivos.

### 5.4.3.2 – Subir backend e validar Case Layer

1. Iniciar o backend (FastAPI ou framework equivalente) com o módulo `app/cases/` carregado.
2. Testar endpoints de casos/coleções via HTTP client:
   - `GET /api/cases` deve retornar a lista de casos canônicos com `case_id`, título, tema e status de truth.
   - `GET /api/cases/{case_id}` para pelo menos dois casos canônicos deve retornar a visão unificada (claims, evidências, truth atual, timeline).
   - `GET /api/collections` deve listar coleções com `collection_id`, título, descrição e contagem de casos.
   - `GET /api/collections/{collection_id}` deve retornar a lista de casos daquela coleção, com link indireto para detalhe.
3. Erros nessas rotas são tratados como falha de GP1–GP3 e bloqueiam demos até correção.

### 5.4.3.3 – Subir cockpit de casos e validar navegação básica

1. Rodar o frontend `frontend/inspectah-ui` em modo desenvolvimento ou servir build de produção.
2. Acessar `/cases` no navegador:
   - verificar se a lista de casos é carregada;
   - conferir exibição de título, resumo, tema, status de truth e link para detalhe.
3. Acessar `/collections`:
   - verificar lista de coleções;
   - conferir descrição e contagem de casos por coleção.
4. Clicar em uma coleção e navegar até `/collections/:collectionId`:
   - verificar cards de casos corretos e links para `/cases/:caseId`.
5. Abrir `CaseDetailPage` para 1–2 casos canônicos e confirmar presença de todos os blocos essenciais:
   - contexto/resumo;
   - claims centrais;
   - painel de status de truth;
   - timeline simplificada;
   - links de evidência.

Esse runbook básico precisa ser executável em qualquer máquina de dev com acesso ao repo e à base adequada.

---

## 5.4.4 – Fluxos canônicos por persona (A, B, C) e suas evidências

Os fluxos de persona são **cenários obrigatórios** de uso que demonstram GP1–GP4.

### 5.4.4.1 – Fluxo Persona A (Analista / Jornalista) – GP2

Objetivo: a Persona A deve conseguir, em poucos passos, partir de uma afirmação e chegar a uma visão de caso com evidências.

Cenário canônico recomendado:

1. Escolher uma afirmação real correspondente a um caso canônico (ex.: uma frase sobre inflação, taxa de desemprego, homicídios, etc.), com `case_id` documentado em `docs/cases/case_<slug>.yaml`.
2. Abrir `/cases` e localizar o caso:
   - via busca ou por filtro de tema, se disponível;
   - ou diretamente via `/cases/:caseId` se o ID já for conhecido.
3. Em `CaseDetailPage`, verificar que a página responde a três perguntas básicas:
   - o que está sendo afirmado (claim/narrativa)?
   - qual é o estado atual de truth e por quê?
   - quais evidências sustentam esse estado?
4. Clicar em pelo menos uma evidência principal (via `EvidenceLink`) e chegar na fonte primária (dataset, documento, notícia, etc.).
5. Contar o número de ações entre “sei a afirmação/ID do caso” e “estou vendo uma evidência primária relevante”. Esse número alimenta a métrica `case_view_click_distance_A`.

Evidências a registrar:

- Dump JSON da resposta de `GET /api/cases/{case_id}` para o caso usado na demo, salvo em `out/evidence/SXX_product_cases/case_<slug>.json`.
- Captura de tela da `CaseDetailPage` mostrando claims, status de truth, linha do tempo e evidências, salva em `out/evidence/SXX_product_cases/case_<slug>_detail.png` (ou formato equivalente).
- Pequeno arquivo de texto/JSON com o valor medido de `case_view_click_distance_A` para esse caso, em `out/evidence/SXX_product_metrics/click_distance_A.json`.

### 5.4.4.2 – Fluxo Persona B (Cidadão curioso) – GP3

Objetivo: a Persona B deve conseguir explorar temas via coleções, entender o panorama e acessar casos sem conhecer o modelo interno.

Cenário canônico recomendado:

1. Abrir `/collections` e identificar visualmente pelo menos T coleções temáticas (por exemplo: Economia, Dados oficiais vs discurso, Contestação tardia).
2. Escolher uma coleção (ex.: Economia) e acessar `/collections/:collectionId`.
3. Na tela da coleção, verificar se é possível, com uma leitura rápida:
   - entender o tema da coleção;
   - ver quantos casos a compõem;
   - ter uma ideia do tipo de “histórias” que ela traz.
4. Clicar em dois casos da coleção e verificar em cada `CaseDetailPage`:
   - se a narrativa principal do caso está clara;
   - se o status de truth focal (FACT/CONTESTED/etc.) está explícito;
   - se existem links para evidências.

Evidências a registrar:

- Dump JSON de `GET /api/collections` em `out/evidence/SXX_product_collections/collections.json`.
- Dump JSON de `GET /api/collections/{collection_id}` para pelo menos uma coleção temática em `out/evidence/SXX_product_collections/collection_<id>.json`.
- Capturas de `/collections` e `/collections/:collectionId` em arquivos de imagem/HTML na mesma pasta.

### 5.4.4.3 – Fluxo Persona C (Curador interno) – GP4

Objetivo: garantir que o curador consegue usar caminhos oficiais para criar/ajustar casos e coleções, sem SQL manual ou hacks.

Cenário canônico recomendado (novo caso ou evolução de caso existente):

1. Descobrir candidato a caso
   - usar ferramentas existentes (consultas à Truth-DB, relatórios, insights de ingestão) para localizar uma narrativa interessante.
2. Criar/editar arquivo de caso
   - copiar um `case_<slug>.yaml` de exemplo em `docs/cases/`;
   - atualizar campos `case_id`, `title`, `summary`, `theme`;
   - preencher `claims` com refs reais (IDs de Claim ou critérios estáveis para encontrá-las);
   - preencher `evidences` com refs a datasets/documentos/links internos;
   - apontar `committee_decisions` e `debunk_issues` relevantes;
   - opcionalmente, indicar `truth_focus` (quais TruthRecords/Events devem aparecer na timeline principal).
3. Atualizar coleções
   - abrir `docs/cases/collections.yaml`;
   - incluir o novo `case_id` em uma ou mais coleções relevantes.
4. Validar consistência
   - rodar `bin/sXX_cases_check.sh` e verificar `out/evidence/SXX_cases_check/report.json` para garantir integridade;
   - se o report indicar inconsistências, ajustar arquivos e repetir.
5. Atualizar métricas
   - rodar `bin/sXX_cases_metrics.sh` e conferir `out/evidence/SXX_product_metrics/metrics.json` (ver se `N_casos_canonicos` e `coverage_casos_em_colecoes` foram atualizados conforme esperado).
6. Verificar UI
   - acessar `/cases` e verificar que o novo caso aparece;
   - acessar `/collections/:collectionId` das coleções em que o caso foi incluído e verificar sua presença;
   - abrir `CaseDetailPage` do novo caso e conferir se a visão faz sentido.

Evidências a registrar:

- Logs de execução dos scripts de check e metrics, salvos automaticamente em `out/evidence/SXX_cases_check/` e `SXX_product_metrics/`.
- Capturas de `/cases` e `/collections/:id` mostrando o caso inserido.
- Diffs de Git nos arquivos `docs/cases/case_<slug>.yaml` e `collections.yaml` anexados ao PR ou ao resumo de sprint.

---

## 5.4.5 – Cálculo e registro de métricas de produto

Os scripts de métricas são parte central de GP4. O 5.4 define como usá-los operacionalmente.

### 5.4.5.1 – Execução de métricas

1. Escolher ambiente onde as métricas serão calculadas (em geral, staging ou dev “congelado” para a sprint).
2. Garantir que `docs/cases/` e `app/cases/` estão na versão final da sprint.
3. Executar `bin/sXX_cases_metrics.sh`.
4. Confirmar que o script gera `out/evidence/SXX_product_metrics/metrics.json` sem erro.

### 5.4.5.2 – Conteúdo mínimo de `metrics.json`

O arquivo deve conter, no mínimo:

- `N_casos_canonicos`: contagem de casos canônicos definidos;
- `N_temas_com_colecao`: temas com coleções não vazias;
- `coverage_casos_em_colecoes`: proporção de casos canônicos que aparecem em pelo menos uma coleção;
- `cases_by_truth_status`: distribuição dos estados de truth agregados (ex.: quantos casos com status predominante FACT, CONTESTED, etc.);
- `sample_case_view_click_distance_A`: se medido, distância média ou worst-case em cliques para Persona A em 1–2 casos.

### 5.4.5.3 – Uso das métricas no ORR e no fechamento da sprint

1. O relatório de ORR (Cap. 2 / G7) deve incluir uma subseção “Métricas de Produto (Cap. 5)” com valores de `metrics.json` e um comentário rápido sobre seu significado.
2. A decisão de GO/NO-GO (G8) deve considerar explicitamente se:
   - `N_casos_canonicos` atinge o mínimo definido em 5.2;
   - `coverage_casos_em_colecoes` está em 1.0 (ou se há justificativa explicita para faltas);
   - `case_view_click_distance_A` está dentro do limite definido;
   - o pipeline de cálculo de métricas está funcionando, mesmo que os valores ainda indiquem espaço para melhoria.

---

## 5.4.6 – Evidências mínimas por gate GP1–GP4

Para facilitar revisão e auditoria, o 5.4 organiza as evidências de produto por gate.

### GP1 – Caso Inspectah como unidade de produto real

Evidências obrigatórias:

- `docs/cases/case_model.md` descrevendo o modelo oficial de caso;
- `docs/cases/case_*.yaml` para todos os casos canônicos;
- relatório em `out/evidence/SXX_cases_check/report.json` mostrando zero casos inválidos;
- dumps de `GET /api/cases/{case_id}` para pelo menos dois casos canônicos.

### GP2 – Página/endpoint único de caso para Persona A

Evidências obrigatórias:

- payloads em `out/evidence/SXX_product_cases/case_<slug>.json` com visão unificada completa;
- capturas da `CaseDetailPage` exibindo claims, truth, timeline, evidências;
- arquivo com medidas de `case_view_click_distance_A` para um ou mais casos.

### GP3 – Coleções temáticas mínimas para Persona B

Evidências obrigatórias:

- `docs/cases/collections.yaml` com pelo menos T coleções configuradas;
- `out/evidence/SXX_product_collections/collections.json` e `collection_<id>.json` com exemplos;
- capturas de `/collections` e `/collections/:id`.

### GP4 – Curadoria funcional + métricas vivas

Evidências obrigatórias:

- scripts `bin/sXX_cases_check.sh`, `bin/sXX_cases_metrics.sh`, `bin/sXX_cases_demo.sh` presentes e mencionados no Cap. 4 e 5.3;
- relatórios de check e metrics em `out/evidence/SXX_cases_check/` e `SXX_product_metrics/`;
- documentação do fluxo de curadoria (seção 5.4.4.3) com pelo menos um ciclo completo executado e registrado;
- referência a essas métricas e fluxos no relatório ORR.

---

## 5.4.7 – Roteiro da reunião de GO/NO-GO para o Cap. 5

Na prática, o Cap. 5 passa por um mini-ORR de produto antes ou durante G8. O 5.4 propõe um roteiro objetivo para essa avaliação:

1. Revisão rápida de 5.1–5.3
   - lembrar personas A/B/C, problemas P1–P5 e gates GP0–GP4;
   - apontar onde vivem `docs/cases/`, `app/cases/`, UI de casos/coleções e scripts em `bin/`.

2. Demonstração guiada (10–20 minutos)
   - executar ao vivo (ou via gravação) o fluxo Persona A em um caso canônico;
   - executar o fluxo Persona B em uma coleção temática;
   - mostrar rapidamente o fluxo Persona C (curador) da criação/edição de um caso.

3. Apresentação de métricas
   - mostrar `metrics.json` e explicar cada valor relevante;
   - destacar especialmente `N_casos_canonicos`, `coverage_casos_em_colecoes` e `case_view_click_distance_A`.

4. Checagem de evidências
   - confirmar que todos os artefatos listados em 5.4.6 estão presentes no bundle da sprint;
   - confirmar que `bin/sXX_cases_check.sh` e `bin/sXX_cases_metrics.sh` rodaram na base de referência da sprint.

5. Decisão
   - se GP1–GP4 forem atendidos e nenhuma regressão crítica de produto for identificada, registrar GO para o Cap. 5;
   - caso contrário, registrar NO-GO parcial para Cap. 5 e definir ações corretivas (ajustes de casos, coleções, UI ou scripts) antes de chamar a sprint de fechada.

---

## 5.4.8 – Feedback, lições aprendidas e ponte para o Cap. 6

Por fim, o 5.4 define como o aprendizado da camada de produto alimenta o Cap. 6 (Lições aprendidas, riscos, ajustes de roadmap).

Procedimento mínimo:

1. Para cada sessão de demo com personas A/B reais ou proxies (analistas, jornalistas, colegas de produto), registrar:
   - o que foi fácil e o que foi difícil;
   - pontos de confusão (terminologia, layout, navegação);
   - casos onde a pessoa quis fazer algo que a UI/APIs ainda não suportam.

2. Consolidar essas observações em um doc de Cap. 6 (ex.: `docs/sprint_xx_cap_6_lições_produto.md`), referenciando explicitamente:
   - quais feedbacks são bugs/ajustes da sprint atual;
   - quais feedbacks sugerem novas histórias para sprints futuras (por exemplo, UI pública, filtros avançados, gráficos).

3. Garantir que qualquer gap grave identificado (ex.: caso canônico inconsistente, coleção enganosa, timeline de truth incoerente) seja tratado como bug de Cap. 5, e não apenas “insight para depois”.

Com isso, o Cap. 5 não termina em “parece bom”: ele termina em **evidência reprodutível de valor de produto** e em um conjunto claro de aprendizados que guiam as próximas iterações de Verdade & Interpretação.

O 5.4 v2 extremo, portanto, transforma a camada de produto em algo operacional, auditável e mensurável: qualquer pessoa que chegue ao repo depois desta sprint consegue não só ver como o Inspectah calcula verdade por dentro, mas também como essa verdade é apresentada em forma de casos, coleções e narrativas mínimas – e quais evidências sustentam essa promessa.

