# 4.4 – Execução & Evidências (Plano Operativo) – v2

Este 4.4 é o **manual operacional** da sprint: ele pega o contexto do 4.1, os gates e métricas do 4.2 e o filemap do 4.3 e transforma tudo em um **roteiro passo a passo**, tanto para humanos quanto para automações (CI, agentes), de como a sprint é executada, validada e auditada.

A ideia é simples: alguém clona o repositório do Inspectah, abre este subcapítulo e, sem depender de conhecimento tribal, consegue:
- preparar o ambiente;
- rodar a cadeia de gates G0–G8;
- executar cenários ponta a ponta canônicos;
- gerar e interpretar scorecards e evidências;
- produzir o bundle final da sprint e tomar uma decisão de GO/NO‑GO baseada em fatos.

---

## 4.4.1 – Objetivo e escopo do plano operativo

O plano operativo do 4.4 tem quatro objetivos explícitos:

1. **Padronizar o “como rodar a sprint”**  
   Sair do padrão "pergunta para quem fez" e estabelecer uma sequência oficial, única, de execução – tanto local quanto no CI.

2. **Tornar a produção de evidências parte do fluxo normal**  
   Rodar gates e cenários passa a significar, automaticamente, gerar scorecards em `out/scorecards/` e evidências em `out/evidence/`, seguindo o filemap do 4.3.

3. **Permitir reexecução e auditoria independente**  
   Qualquer pessoa, semanas depois, consegue repetir a execução a partir de um commit e comparar scorecards, sem depender de scripts escondidos ou estados misteriosos de máquina.

4. **Conectar a execução às decisões de produto e verdade**  
   O que é decidido em G8 (GO/NO‑GO) precisa estar apoiado em artefatos produzidos por este plano: scorecards, bundles, cenários canônicos e timelines de truth.

O escopo deste subcapítulo cobre:
- fluxo local (dev na própria máquina ou Codespaces);
- fluxo de CI (PRs, branch de sprint, release);
- cenários ponta a ponta canônicos;
- gestão de evidências (o que guardar, o que limpar, como empacotar);
- ritual de fechamento da sprint.

---

## 4.4.2 – Linha do tempo operacional típica da sprint

Para amarrar execução com tempo, o 4.4 assume uma linha do tempo simplificada (adaptável à duração real da sprint):

- **Dia 0 (kickoff técnico)**:
  - garantir que scripts de base de `bin/` existem ao menos como stubs;
  - validar que `app/`, `tests/`, `docs/` e `out/` seguem o filemap do 4.3;
  - rodar G0 e G1 para estabelecer uma primeira rodada de sanidade de ambiente e schema.

- **Dias 1–N‑2 (desenvolvimento ativo)**:  
  Fase de maior iteração. Tipicamente:
  - desenvolvedores mexem em `app/` e `tests/`;
  - PRs disparam pipelines parciais (G0–G3, às vezes G4) para proteger a base;
  - devs rodam localmente G2–G5 sempre que mudam ingestão, cérebro, comitê, debunker ou truth;
  - evidências "representativas" vão sendo atualizadas em `out/evidence/` (não necessariamente a cada commit, mas em checkpoints significativos).

- **Dia N‑1 (hardening / pré‑fechamento)**:  
  A sprint já deveria ter:
  - scripts G0–G6 estáveis;
  - testes principais verdes no CI;
  - pelo menos uma rodada completa local de G0–G6, produzindo scorecards e evidências coerentes.
  
  Neste dia, é comum rodar:
  - uma "rodada dourada" de G0–G6 em ambiente limpo;
  - todos os cenários canônicos da sprint via `bin/sXX_scenario_*.sh`;
  - um primeiro `bin/sXX_make_bundle.sh` para validar que o bundle é gerável.

- **Dia N (fechamento / GO‑NO‑GO)**:  
  Fase de decisão:
  - rodar G0–G7 em ambiente de CI ou em um ambiente de staging o mais próximo possível do alvo;
  - gerar o bundle final de evidências;
  - rodar `bin/sXX_g8_go_no_go.sh` para gravar decisão em `SXX_G8_go_no_go.json`;
  - registrar lições de execução em `docs/sprint_xx_lessons_execucao.md`.

Essa linha do tempo não engessa a sprint, mas estabelece um ritmo esperado: não se deixa para "descobrir o que é G2–G6" só no dia de fechar.

---

## 4.4.3 – Runbook local detalhado (G0–G6 + cenários)

### 4.4.3.1 – Pré‑requisitos

Antes de rodar qualquer script da sprint, o desenvolvedor precisa:
- ter o repositório clonado e atualizado (branch da sprint ou `main` com merge da sprint);
- ter as ferramentas básicas instaladas (por exemplo, Python 3.x, Docker se for usado, make, etc.);
- ter um `.env` (ou equivalente) configurado com variáveis de ambiente mínimas (conforme Cap. 4.1.4 e 4.3).

### 4.4.3.2 – Passo a passo de G0 a G6 local

1. **G0 – Setup de ambiente**  
   Comando típico:
   ```bash
   PYTHONPATH=. bin/sXX_g0_setup.sh
   ```
   Resultado esperado:
   - scorecard `out/scorecards/SXX_G0_setup.json` com `env_ok = true`;
   - pasta `out/evidence/SXX_G0_setup/` com logs de criação/ativação de venv, instalação de deps e checks de conexão.

2. **G1 – Modelos & Migrações**  
   ```bash
   PYTHONPATH=. bin/sXX_g1_models_and_migrations.sh
   ```
   Resultado esperado:
   - scorecard `SXX_G1_models_and_migrations.json` com `migrations_failed = 0` e `invariants_violated = 0`;
   - evidências de sanity de schema em `out/evidence/SXX_G1_schema_sanity/` (por exemplo, CSV/JSON com resultados de queries).

3. **G2 – Ingestão 2.0**  
   ```bash
   PYTHONPATH=. bin/sXX_g2_ingestion.sh
   ```
   Resultado esperado:
   - scorecard `SXX_G2_ingestion.json` com pelo menos uma run `SUCCESS` por tipo de fonte da sprint;
   - `out/evidence/SXX_G2_ingestion/` contendo amostras de `IngestionItemRaw` e `IngestionItemNormalized` e, opcionalmente, dumps de eventos de mensageria.

4. **G3 – Cérebro & Claims**  
   ```bash
   PYTHONPATH=. bin/sXX_g3_brain_and_claims.sh
   ```
   Resultado esperado:
   - scorecard `SXX_G3_brain_and_claims.json` com contagem de claims geradas, coverage de claims esperadas e taxa de claims lixo;
   - `out/evidence/SXX_G3_claims/` com tabelas input → claims, facilitando inspeção humana.

5. **G4 – Comitês & Debunker v0**  
   ```bash
   PYTHONPATH=. bin/sXX_g4_committees_and_debunker.sh
   ```
   Resultado esperado:
   - scorecard `SXX_G4_committees_and_debunker.json` com distribuição de vereditos, contagem de issues abertas/resolvidas e tempos médios de resolução;
   - evidências em `out/evidence/SXX_G4_committees/` mostrando fluxos completos (Claim → Evaluations → Decision → Issue → Task → Resolution).

6. **G5 – Truth‑DB**  
   ```bash
   PYTHONPATH=. bin/sXX_g5_truthdb.sh
   ```
   Resultado esperado:
   - scorecard `SXX_G5_truthdb.json` com `claims_with_multiple_active_truth = 0`;
   - `out/evidence/SXX_G5_truth_timelines/` com timelines de truth por claim, mostrando sequência de `TruthChangeEvent`.

7. **G6 – Observabilidade & Falhas controladas**  
   ```bash
   PYTHONPATH=. bin/sXX_g6_observability_and_failures.sh
   ```
   Resultado esperado:
   - scorecard `SXX_G6_observability_and_failures.json` com métricas mínimas presentes e cenários de falha marcados como OK;
   - `out/evidence/SXX_G6_failures/` com logs, snapshots de métricas e traces antes/durante/depois das falhas.

Depois de G0–G6, o dev pode rodar G7 e G8 localmente, mas isso costuma ser reservado para momentos de checkpoint ou fechamento.

### 4.4.3.3 – Execução de cenários ponta a ponta

Além dos gates, o runbook local inclui scripts de cenários canônicos (quando definidos para a sprint):

```bash
PYTHONPATH=. bin/sXX_scenario_01_noticia_economica.sh
PYTHONPATH=. bin/sXX_scenario_02_dado_oficial_vs_discurso.sh
PYTHONPATH=. bin/sXX_scenario_03_contestacao_tardia.sh
```

Cada script de cenário deve:
- acionar a pipeline completa (da fonte até Truth‑DB) para um caso bem descrito em `docs/sprint_xx_cenarios_execucao.md`;
- gravar evidências em `out/evidence/SXX_scenario_0X_*` (por exemplo, JSONs com entidades, logs anotados);
- opcionalmente, atualizar um scorecard específico de cenário, se a sprint assim desejar.

Esses cenários são usados tanto para debugging diário quanto para demonstrações e revisões.

---

## 4.4.4 – Execução em CI: matriz de pipelines

### 4.4.4.1 – Pipelines de PR

Objetivo: proteger a base da sprint sem pesar demais.

Padrão recomendado:
- Workflow `.github/workflows/sXX_pr_checks.yml` acionado em `pull_request`;
- passos principais:
  - checkout do código;
  - setup de ambiente (equivalente a G0, podendo reutilizar o script);
  - aplicação de migrações e sanity de schema (G1);
  - testes unitários e integrados principais;
  - G2 e G3 em versão "reduzida" (datasets de teste pequenos, sem exaurir todas as fontes);
- scorecards gerados são anexados como artefatos de build, permitindo inspeção na interface do GitHub.

### 4.4.4.2 – Pipeline da branch de sprint

Objetivo: rodar a cadeia completa de gates de execução em base regular.

Workflow típico: `.github/workflows/sXX_gates.yml`, acionado:
- em push na branch da sprint;
- em schedule (por exemplo, nightly).

Passos:
- chamar `bin/sXX_g0_setup.sh` até `bin/sXX_g7_orr.sh` em ordem, falhando o job quando algum gate crítico falhar;
- publicar `out/scorecards/` e, possivelmente, subconjunto de `out/evidence/` como artefatos;
- opcionalmente, publicar um resumo de G7 em comentário de PR ou em canal de comunicação interno.

### 4.4.4.3 – Pipeline de release / staging

Objetivo: reproduzir a execução completa da sprint em ambiente mais próximo de produção e preparar a decisão de G8.

Workflow típico: `.github/workflows/sXX_release.yml`, acionado manualmente ou ao criar uma tag.

Passos:
- rodar G0–G7 em ambiente configurado com variáveis de staging;
- rodar os cenários canônicos via `bin/sXX_scenario_*.sh`;
- gerar bundle via `bin/sXX_make_bundle.sh`;
- persistir bundle e scorecards como artefatos de release.

A decisão formal de G8 pode ser registrada via `bin/sXX_g8_go_no_go.sh` rodado numa sessão manual (por exemplo, por um engenheiro líder) ou automatizado nesse workflow com input humano (
`workflow_dispatch` com parâmetros de decisão).

---

## 4.4.5 – Gestão de cenários ponta a ponta

Cenários ponta a ponta são peças centrais da narrativa da sprint. O 4.4 define como eles são criados, versionados e usados.

1. **Definição em documento vivo**  
   Todos os cenários canônicos devem ser descritos em `docs/sprint_xx_cenarios_execucao.md`, com:
   - contexto do cenário (história, fonte, tipo de conflito ou verificação);
   - objetivo (o que queremos comprovar com ele);
   - passos de alto nível (do ponto de vista do usuário/sistema);
   - ligação com scripts de `bin/` e com evidências em `out/evidence/`.

2. **Script oficial em `bin/`**  
   Cada cenário tem um script `bin/sXX_scenario_0X_nome_curto.sh` que implementa a narrativa do doc, usando apenas interfaces oficiais (APIs, CLI, jobs). Não é permitido que cenários "burlem" camadas (por exemplo, fazer inserts diretos em banco sem passar pela ingestão, salvo quando o próprio cenário for sobre dados pré‑semeados).

3. **Evidências associadas**  
   Ao rodar um cenário, o script deve escrever em `out/evidence/SXX_scenario_0X_*` artefatos que contem a história daquele caso: input original, entidades criadas, decisões, issues, timeline de truth, logs, etc.

4. **Ligação com testes automatizados**  
   Quando fizer sentido, um cenário também terá um ou mais testes em `tests/e2e/` que verificam propriedades mínimas (por exemplo, que claims esperadas foram criadas, que o estado final de truth é o previsto). O objetivo não é reproduzir todos os detalhes do script, mas garantir que propriedades-chave se mantenham.

5. **Uso em revisões e demos**  
   Em revisões com stakeholders (tanto técnicos quanto de produto), estes cenários canônicos são a base de demonstração. O 4.4 garante que qualquer pessoa consiga reproduzi-los em ambiente apropriado.

---

## 4.4.6 – Política de evidências, limpeza e bundles

Evidências tendem a crescer com o tempo; o 4.4 define uma política mínima para evitar caos:

1. **Executar scripts de limpeza controlada**  
   A sprint deve ter, idealmente, um script auxiliar como `bin/sXX_clean_evidence.sh` que:
   - preserva as execuções mais recentes (ou marcadas como "oficiais");
   - remove evidências antigas ou provisórias;
   - nunca apaga `out/scorecards/` e `out/bundles/` sem confirmação explícita.

2. **Marcar execuções "oficiais"**  
   Rodadas de G0–G7 consideradas de referência (por exemplo, a rodada dourada pré‑GO) podem ser marcadas no próprio scorecard com um campo `official_run = true` ou com um identificador de execução.

3. **Bundles como contratos de auditoria**  
   O bundle gerado por `bin/sXX_make_bundle.sh` é tratado como contrato:
   - contém scorecards de todos os gates;
   - contém pastas de evidência selecionadas como representativas;
   - vem acompanhado de `bundle_manifest.json` com commit, timestamp e hashes dos arquivos internos.

4. **Retenção e armazenamento externo**  
   Dependendo da importância da sprint, o bundle pode ser armazenado fora do ambiente de CI (por exemplo, em um bucket ou no Evidence Vault global do Inspectah), garantindo que a auditoria não dependa da retenção padrão do GitHub.

---

## 4.4.7 – Fechamento operacional da sprint (GO/NO‑GO)

O rito de fechamento, do ponto de vista do 4.4, envolve:

1. **Rodada completa de G0–G7 em ambiente limpo**  
   - reconfigurar ambiente (ou criar um novo) sem resíduos de execuções anteriores;
   - rodar `bin/sXX_g0_setup.sh` até `bin/sXX_g7_orr.sh` na sequência;
   - garantir que todos os scorecards existem e que nenhum gate crítico está em FAIL.

2. **Execução dos cenários canônicos**  
   - rodar todos os `bin/sXX_scenario_0X_*.sh`;
   - conferir que as evidências geradas correspondem ao esperado em `docs/sprint_xx_cenarios_execucao.md`.

3. **Geração do bundle**  
   - executar `bin/sXX_make_bundle.sh`;
   - validar que `out/bundles/inspectah_sXX_evidence_bundle.zip` foi criado e que `bundle_manifest.json` é consistente.

4. **Decisão de G8**  
   - rodar `bin/sXX_g8_go_no_go.sh`;
   - registrar em `SXX_G8_go_no_go.json` a decisão (GO/GO_WITH_RISKS/NO_GO), participantes, riscos residuais e ações de follow‑up.

5. **Registro de lições de execução**  
   - atualizar `docs/sprint_xx_lessons_execucao.md` com o que deu certo e errado na execução dos gates, cenários e bundles;
   - alimentar o Cap. 6 com essas lições, para que as próximas sprints tenham um Cap. 4 ainda melhor.

---

Com isso, o 4.4 v2 fecha o Capítulo 4 como um todo: não apenas diz que há gates, métricas e filemap, mas ensina como usá‑los na prática, dia após dia, até o momento em que a sprint pode, com alguma serenidade, dizer "GO" e expor o Inspectah ao mundo sem estar andando de olhos vendados.

