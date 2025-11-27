# Capítulo 4 – Execução & Evidências da Sprint (Playbook v2)

Este capítulo 4 é o macro-capítulo de **Execução & Evidências** da sprint, seguindo o Sprint Playbook v2: quatro subcapítulos fixos – (4.1) Contexto & problemas a resolver, (4.2) Gates & métricas & DoD, (4.3) Arquitetura & filemap, (4.4) Execução & evidências. Ele conecta os capítulos anteriores (1–3) com o que realmente acontece em código, CI, logs e bundles de evidência.

A partir deste capítulo, qualquer pessoa deve conseguir responder sem ambiguidade:
- o que exatamente precisa ser construído e validado nesta sprint em termos de execução;
- como essa execução é medida, gateada e documentada;
- onde vivem os scripts, scorecards e artefatos de evidência;
- como rodar a sprint de ponta a ponta até o GO, de forma reprodutível.

---

## 4.1 – Contexto & problemas a resolver (Execução)

Este subcapítulo explica por que a execução desta sprint é crítica e quais problemas concretos ela precisa resolver.

### 4.1.1 – Papel do Capítulo 4 no arco da sprint

Nos capítulos anteriores foram definidos: o contexto e escopo da sprint (Cap. 1), os gates, métricas e Definition of Done globais (Cap. 2), e a arquitetura de domínio, modelos e integrações (Cap. 3). O Capítulo 4 entra como camada operacional: ele define **como** essa arquitetura é colocada de pé, **como** os gates são exercitados e **quais evidências** provam que a sprint atendeu às metas.

No arco S21–S25 (Fontes → Ingestão 2.0 → Cérebro/Comitês → Debunker v0 → Verdade/Truth‑DB), a execução desta sprint precisa entregar pelo menos um **fluxo vertical ponta a ponta funcional**, ainda que com escopo reduzido, e ao mesmo tempo preparar o terreno para sprints seguintes não precisarem “recomeçar do zero” em termos de scripts, cenários, evidências e rotinas de operação.

### 4.1.2 – Problemas de execução que este capítulo ataca

Os principais problemas que este Capítulo 4 precisa endereçar são:

1. Fragmentação da execução: sem um plano unificado, cada dev/squad tende a rodar comandos diferentes, em ordens diferentes, gerando incerteza sobre o que está realmente pronto. O Capítulo 4 define **uma sequência mínima oficial** de execução da sprint.
2. Falta de rastreabilidade: sem scorecards, logs e bundles padronizados, é impossível auditar a sprint depois. Este capítulo estabelece **onde e como todas as evidências** serão produzidas e armazenadas.
3. Dúvida sobre o que é “pronto”: Definition of Done genérico não é suficiente; é preciso ligar DoD à execução real. Aqui são definidos **critérios executáveis** de “pronto” para cada bloco da sprint.
4. Inconsistência entre ambiente local e CI: comandos diferentes entre máquina de desenvolvimento, Codespaces e runner do GitHub levam a bugs fantasma. Este capítulo exige que **os mesmos scripts de execução** rodem em todos esses ambientes.

### 4.1.3 – Objetivos de execução para esta sprint

A execução desta sprint tem três objetivos centrais:

1. **Ponta a ponta mínima**: conseguir, com um conjunto de comandos bem definido, ir de um cadastro de fonte real até um estado de verdade (`TruthRecord`) consultável, com claims, decisões de comitê e, se aplicável, uma contestação registrada.
2. **Gates automatizados sólidos**: todos os gates definidos no Cap. 2 para esta sprint precisam ter scripts idempotentes, scorecards em JSON e evidências associadas.
3. **Reprodutibilidade e auditabilidade**: qualquer pessoa com acesso ao repositório deve conseguir repetir a execução e chegar ao mesmo conjunto de scorecards e evidências, ou a diferenças explicáveis (por exemplo, timestamps ou IDs).

---

## 4.2 – Gates, métricas & Definition of Done (Execução)

Este subcapítulo adapta o framework de gates global (Cap. 2) para a camada de execução da sprint.

### 4.2.1 – Mapa de gates específicos de execução

A sprint adota um conjunto de gates Sx_G* (nomes concretos definidos no Cap. 2), cada um com foco em um aspecto da execução:

- **G0 – Grounding & Setup**: prepara ambiente (virtualenv/containers), instala dependências, aplica migrações iniciais e verifica conectividade mínima com banco, mensageria e stack de observabilidade. DoD: scripts de setup idempotentes e scorecard confirmando sucesso.
- **G1 – Modelos & Migrações**: valida que o modelo de dados está consistente com o Cap. 3.3; todas as migrações rodam limpas em um banco “fresco”; invariantes de integridade básicas são testadas. DoD: zero violações de invariantes em queries de sanidade.
- **G2 – Ingestão 2.0**: garante que fluxos de ingestão e normalização rodam para fontes de teste. DoD: pelo menos uma `IngestionRun` bem-sucedida por tipo de fonte-alvo da sprint, itens crus e normalizados persistidos e eventos `ingestion.item.normalized` emitidos.
- **G3 – Cérebro (Interpretação & Claims)**: assegura que `InterpretationUnit`, `ClassificationResult` e `Claim` são gerados corretamente a partir de itens normalizados. DoD: cenários de teste que validam extração de claims em diferentes formatos de texto.
- **G4 – Comitê & Debunker v0**: verifica que `CommitteeEvaluation`, `CommitteeDecision`, `DebunkIssue` e `DebunkTask` funcionam ponta a ponta. DoD: ao menos um conjunto de cenários cobrindo vereditos divergentes, incerteza alta e uma contestação resolvida.
- **G5 – Truth‑DB operacional**: garante que `TruthRecord` e `TruthChangeEvent` refletem corretamente decisões de comitê e debunker. DoD: nenhuma claim com mais de um truth ativo; estados de verdade coerentes com cenários testados.
- **G6 – Observabilidade & Falhas controladas**: certifica que métricas, logs estruturados e traços distribuídos estão presentes e que cenários de falha controlada se comportam conforme o 3.4. DoD: painéis mínimos, alertas básicos e execução bem-sucedida de testes de falha.
- **G7 – ORR da sprint**: rodagem consolidada dos gates, coleta de scorecards e evidências, com resumo para o Conselho. DoD: todos os scorecards em estado OK ou com justificativa formal para qualquer exceção.
- **G8 – GO/NO‑GO**: decisão macro da sprint baseada nos scorecards e no bundle de evidências; nenhum bug crítico aberto em áreas cobertas por esta sprint.

### 4.2.2 – Métricas operacionais mínimas

Além de métricas de produto, a execução precisa expor métricas operacionais que os gates vão ler. Exemplos de métricas mínimas:

- ingestão: número de `IngestionRun` por fonte, taxa de sucesso/falha, latência média;
- claims: número de `Claim` por fonte e por dia, proporção de claims com `Evidence` associada;
- comitê: distribuição de `CommitteeDecision.final_verdict` e `uncertainty_score` médio por tipo de claim;
- debunker: número de `DebunkIssue` abertas, em revisão e resolvidas, tempo médio de resolução;
- Truth‑DB: número de `TruthRecord` por estado, número de `TruthChangeEvent` por dia.

Os valores alvo e limites aceitáveis são definidos no Cap. 2, mas aqui fica explícito que essas métricas precisam existir, ser coletadas e ser legíveis pelos scripts de gates.

### 4.2.3 – Definition of Done ligada à execução

Para esta sprint, algo só é considerado “feito” quando:

1. Há código implementado, versionado em branch correto e revisado;
2. Existem testes automatizados cobrindo o comportamento crítico (unitário, integrado ou end‑to‑end, conforme o caso);
3. O gate correspondente passa, gerando scorecard em estado OK;
4. Existe pelo menos uma evidência humana (cenário, log anotado, captura de painel) para casos complexos.

Features sem gate e sem scorecard são, por definição, **não entregues**, mesmo que estejam “rodando na máquina de alguém”.

---

## 4.3 – Arquitetura & filemap (Execução)

Este subcapítulo define onde no repositório vivem os artefatos de execução desta sprint e como eles se conectam ao resto do projeto.

### 4.3.1 – Estrutura de diretórios relevante

Uma estrutura típica, adaptável para a sprint específica:

- `bin/` – scripts executáveis de gates, cenários e utilitários da sprint; por exemplo, `bin/sXX_g0_setup.sh`, `bin/sXX_g2_ingestion.sh`, `bin/sXX_demo_scenario_1.sh`.
- `app/` – código de aplicação (serviços, rotas, workers) que implementa ingestão, cérebro, comitê, debunker e Truth‑DB.
- `app/models/` e `app/schemas/` – modelos ORM e Pydantic descritos no Cap. 3.3.
- `app/services/` – serviços de domínio (por exemplo, `ingestion_service.py`, `committee_service.py`, `debunker_service.py`, `truthdb_service.py`).
- `app/clients/` – clientes externos para fontes de notícias, dados abertos e vault de evidência.
- `tests/` – testes automatizados; subpastas por domínio (`tests/ingestion`, `tests/claims`, `tests/committee`, `tests/truth`, `tests/e2e`).
- `out/scorecards/` – scorecards JSON por gate, nomeados como `SXX_GY_*.json`.
- `out/evidence/` – pastas por gate e cenário, com logs, dumps e capturas.
- `out/bundles/` – bundles ZIP consolidados de evidências da sprint.
- `docs/sprint_xx_cap_4_execucao_e_evidencias.md` – este próprio capítulo, em sua forma concreta para a sprint.

### 4.3.2 – Mapeamento gates → scripts → scorecards

Cada gate da Seção 4.2 é implementado por pelo menos um script em `bin/` que, quando rodado, gera um scorecard correspondente em `out/scorecards/` e, opcionalmente, uma pasta de evidências em `out/evidence/`.

Exemplo de mapeamento (nomes concretos ajustados na sprint real):

- G0: `bin/sXX_g0_setup.sh` → `out/scorecards/SXX_G0_setup.json`;
- G1: `bin/sXX_g1_models_and_migrations.sh` → `out/scorecards/SXX_G1_models_and_migrations.json`;
- G2: `bin/sXX_g2_ingestion.sh` → `out/scorecards/SXX_G2_ingestion.json`;
- G3: `bin/sXX_g3_claims_and_brain.sh` → `out/scorecards/SXX_G3_claims_and_brain.json`;
- G4: `bin/sXX_g4_committee_and_debunker.sh` → `out/scorecards/SXX_G4_committee_and_debunker.json`;
- G5: `bin/sXX_g5_truthdb.sh` → `out/scorecards/SXX_G5_truthdb.json`;
- G6: `bin/sXX_g6_observability_and_failures.sh` → `out/scorecards/SXX_G6_observability_and_failures.json`;
- G7: `bin/sXX_g7_orr.sh` → `out/scorecards/SXX_G7_orr.json`;
- G8: `bin/sXX_g8_go_decision.sh` → `out/scorecards/SXX_G8_go_decision.json`.

### 4.3.3 – Filemap de cenários ponta a ponta

Além dos gates, a sprint mantém um conjunto de cenários ponta a ponta mapeados em arquivos específicos, por exemplo:

- `docs/sprint_xx_cenarios_execucao.md` – lista de cenários, com objetivos, passos, comandos e resultados esperados;
- scripts de cenário em `bin/sXX_scenario_*.sh` – cada um encadeia chamadas a APIs, jobs de ingestão, consultas a banco ou CLI para demonstrar casos típicos.

Para cada cenário descrito neste filemap, espera‑se:

- ao menos um teste automatizado relacionado (em `tests/e2e` ou equivalente);
- uma pasta de evidências sob `out/evidence/SXX_scenario_*` com logs e dumps relevantes.

---

## 4.4 – Execução & evidências (plano operativo)

Este subcapítulo é o roteiro operacional da sprint: a sequência de passos que uma pessoa ou CI deve seguir para executar a sprint do zero até o bundle final de evidências.

### 4.4.1 – Sequência recomendada de execução local

Uma execução típica local segue esta ordem:

1. Preparar ambiente: rodar `bin/sXX_g0_setup.sh` ou comando equivalente descrito na Seção 4.3.
2. Validar modelos e migrações: rodar `bin/sXX_g1_models_and_migrations.sh` e conferir scorecard em `out/scorecards/`.
3. Exercitar ingestão: rodar `bin/sXX_g2_ingestion.sh`, verificar que `IngestionRun`, `IngestionItemRaw` e `IngestionItemNormalized` foram criados, e que eventos `ingestion.item.normalized` foram emitidos.
4. Exercitar cérebro: rodar `bin/sXX_g3_claims_and_brain.sh`, checando se `InterpretationUnit`, `ClassificationResult` e `Claim` foram gerados a partir de itens normalizados.
5. Exercitar comitê e debunker: rodar `bin/sXX_g4_committee_and_debunker.sh`, conferindo `CommitteeEvaluation`, `CommitteeDecision`, `DebunkIssue` e `DebunkTask` em banco e eventos emitidos.
6. Exercitar Truth‑DB: rodar `bin/sXX_g5_truthdb.sh`, garantindo que `TruthRecord` e `TruthChangeEvent` refletem corretamente os cenários.
7. Exercitar observabilidade e falhas: rodar `bin/sXX_g6_observability_and_failures.sh`, induzindo falhas controladas (ex.: desligar temporariamente um serviço, simular indisponibilidade de fila) e verificando que o comportamento é o esperado.
8. Consolidar ORR e GO: rodar `bin/sXX_g7_orr.sh` e `bin/sXX_g8_go_decision.sh`, produzindo scorecards consolidados e o bundle de evidências da sprint.

Cada passo deve atualizar scorecards e pastas de evidência, e qualquer falha deve ser tratada como sinal de que a sprint não está pronta para GO.

### 4.4.2 – Execução em CI e ambientes compartilhados

Em CI, a mesma sequência é aplicada, com adaptações:

- pipelines de PR executam um subconjunto dos gates (tipicamente G0–G3) para garantir que mudanças não quebram a base da sprint;
- pipeline principal da sprint roda G0–G7 em sequência, gerando scorecards que podem ser baixados como artefatos;
- em releases, G8 é acompanhado de um relatório humano de revisão (ORR) com base nos scorecards e nas evidências anexadas.

Os scripts em `bin/` são escritos para rodar igualmente bem em ambientes locais e no CI, sem dependências em caminhos absolutos ou configurações não versionadas.

### 4.4.3 – Evidências obrigatórias e bundle final

A sprint precisa produzir, no mínimo:

1. Scorecards JSON para todos os gates G0–G8;
2. Pastas de evidência para, pelo menos, cada gate principal (G1–G6) e alguns cenários ponta a ponta;
3. Um bundle ZIP consolidando scorecards e evidências principais.

O procedimento para gerar o bundle é descrito explicitamente neste subcapítulo, por exemplo:

- rodar um script `bin/sXX_make_bundle.sh` que:
  - verifica se todos os scorecards necessários existem;
  - compacta `out/scorecards/` e as pastas de `out/evidence/` relevantes em `out/bundles/inspectah_sXX_evidence_bundle.zip`;
  - escreve um pequeno manifesto (JSON ou markdown) descrevendo o conteúdo do bundle.

### 4.4.4 – Registro de lições de execução (hook para Cap. 6)

Embora o capítulo de lições aprendidas da sprint seja o Capítulo 6 macro, este 4.4 define um pequeno **hook operacional**: ao final da sprint, parte da rotina de fechamento de execução inclui registrar, em um arquivo apropriado (por exemplo, `docs/sprint_xx_lessons_execucao.md`), os principais aprendizados relativos aos scripts, cenários, gates e evidências.

Essa coleta alimenta diretamente o Capítulo 6, evitando que lições importantes fiquem dispersas em mensagens de chat ou comentários de PR. O objetivo é que cada nova sprint possa herdar um Capítulo 4 melhor do que o anterior, com menos fricção operacional e mais poder de diagnóstico.

Com isso, o Capítulo 4 fica alinhado ao Sprint Playbook v2 (4 subcapítulos fixos) e serve como contrato operacional completo para a execução da sprint, seus gates e suas evidências.

