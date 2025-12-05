# Sprint 33 — Capítulo 4

## Bloco 3 — Fluxo de Git/PR/CI e rotina diária de execução

Este bloco detalha **como a Sprint 33 deve ser conduzida no repositório e no dia a dia**, traduzindo o plano tático em:

- convenções de branch;
- estilo de PR e revisão;
- integração com CI e gates;
- rotina diária de trabalho para manter a sprint saudável do primeiro ao último dia.

A ideia é reduzir ao mínimo a possibilidade de “mágica manual”: tudo que for repetível deve estar em script, workflow ou checklist claro.

---

### 4.3.1 Convenções de branch para a S33

A S33 segue o padrão de branches do projeto, com algumas ênfases específicas para a camada OracleOps.

#### Branch principal da sprint

- `feature/s33_oracleops_v1`  
  É a branch tronco da sprint 33.

Características:
- concentra o trabalho da S33 até a hora de integração final com `main`;
- é o alvo padrão de PRs temáticos da sprint;
- deve sempre estar em estado minimamente saudável (gates principais rodando localmente), evitando virar um “depósito de WIP quebrado”.

#### Branches temáticos de curto prazo

Sobre `feature/s33_oracleops_v1`, o time cria branches menores, focadas em temas específicos, por exemplo:

- `feature/s33_backend_incidents_domain`  
  Implementa/ajusta domínio de Incident, migrations e testes de G1.

- `feature/s33_backend_ops_components`  
  Implementa `ops_components` + integração com `s33_components_map.yaml`.

- `feature/s33_backend_health_summary`  
  Implementa `ops_health_summary` e primeiros endpoints de overview.

- `feature/s33_frontend_cockpit_overview`  
  Implementa `OverviewPage` + `ComponentHealthTable` conectados à API.

- `feature/s33_frontend_cockpit_incidents`  
  Implementa páginas de lista/detalhe de incidentes.

- `feature/s33_slos_and_observability`  
  Implementa `ops_slos`, `ops_slo_evaluator` e integrações com dashboards/alerts.

- `feature/s33_runbooks_and_evidence`  
  Foca em runbooks, simulação de incidentes e montagem de bundles G4.

Cada branch temática deve ser curta, com objetivo claro e PR pequeno, evitando ficar aberta por muitos dias.

---

### 4.3.2 Estilo de Pull Request na S33

PRs na S33 são tratados como **unidades de execução ligadas diretamente à especificação**.

#### Regras gerais

- Cada PR deve:
  - referenciar explicitamente qual parte da spec está implementando (ex.: “S33 Cap. 3 Bloco 2 — backend OracleOps: ops_components + incidents”);
  - listar quais gates são afetados (G0–G5) e como foram verificados;
  - incluir, quando possível, snippets de logs, prints ou paths de evidências gerados.

- Tamanho dos PRs:
  - preferir PRs pequenos, focados (por exemplo, domínio de Incident separado da UI de Incident);
  - PRs grandes só são aceitos em situações excepcionais, com revisão reforçada.

- Revisão:
  - pelo menos uma pessoa que **não implementou** o código deve revisar o PR;
  - revisores devem checar não só o código, mas a coerência com Capítulos 2 e 3 (gates, arquitetura, filemap).

#### Template sugerido de PR

Cada PR pode seguir um template simples:

- **Contexto**  
  “Implementa [trecho da spec] da Sprint 33: {link para Cap. 3/4}.”

- **Mudanças principais**  
  - `app/domain/...`
  - `app/services/...`
  - `app/api/...`
  - `frontend/inspectah-ui/src/features/oracleops/...`

- **Gates afetados**  
  - G0: [ ]  
  - G1: [x] scripts/domínio de incidentes  
  - G2: [ ]  
  - G3: [ ]  
  - G4: [ ]  
  - G5: [ ]

- **Como testar**  
  - comandos para rodar scripts (`bin/s33_g*_*.sh`, testes de domínio, build do frontend);
  - expectativa de resultado (ex.: “scorecard G1 em PASS”).

- **Evidências**  
  - paths em `out/evidence/...`;
  - prints do cockpit, quando relevante.

Essa estrutura conecta diretamente o PR à sprint e aos gates, evitando “PRs órfãos” sem relação clara com a spec.

---

### 4.3.3 Integração com CI: workflows e gates automatizados

A S33 adiciona/ajusta workflows de CI para que o estado dos gates seja visível e reproduzível.

#### Workflow específico da S33

Arquivo sugerido:

- `.github/workflows/s33-gates.yml`

Responsabilidades:
- preparar o ambiente (instalar dependências, aplicar migrations);
- rodar testes relevantes para a S33 (domínio de Incident, serviços de operação, cockpit);
- executar scripts de gate G0–G4;
- publicar scorecards e evidências como artifacts do CI (quando fizer sentido).

#### Estrutura de jobs (exemplo)

- `s33-prepare-env`  
  - checkout do repositório;
  - setup de Python/Node;
  - instalação de dependências backend/frontend;
  - aplicação de migrations (incluindo Incident).

- `s33-tests-backend`  
  - roda testes de domínio (`tests/domain/test_incidents_model.py` etc.);
  - pode gerar relatório JUnit.

- `s33-tests-frontend`  
  - roda tests/lint/build da feature `oracleops`.

- `s33-gates`  
  - depende de `s33-prepare-env`, `s33-tests-backend`, `s33-tests-frontend`;
  - executa:
    - `bin/s33_g0_scope_and_baseline.sh`;
    - `bin/s33_g1_incidents_domain.sh`;
    - `bin/s33_g2_cockpit_sanity.sh`;
    - `bin/s33_g3_slos_sanity.sh`;
    - `bin/s33_g4_runbooks_and_evidence.sh`;
  - falha se qualquer script retornar código ≠ 0;
  - garante que scorecards `S33_G0..G4` existam em `out/scorecards/`.

O gate G5 (ORR operacional) tende a ser mais manual; ainda assim, o workflow pode verificar a presença do scorecard `S33_G5_orr_operacional.json` em merges finais.

---

### 4.3.4 Política de “build verde” e merges na S33

Para manter estabilidade:

- PRs não devem ser mergeados na branch da sprint (`feature/s33_oracleops_v1`) se o workflow `s33-gates.yml` estiver falhando nos jobs relevantes ao escopo daquele PR.
- Antes de abrir um PR, a pessoa autora deve rodar localmente, pelo menos:
  - os testes de domínio impactados;
  - os scripts de gate diretamente relacionados (por exemplo, `bin/s33_g1_incidents_domain.sh` para PR de Incident).

Na transição da branch da sprint para `main`:

- Exigir que o último commit da branch de sprint tenha:
  - todos os gates G0–G4 em PASS no CI;
  - scorecard G5 preenchido (mesmo que a verificação de G5 no CI seja apenas checar existência de arquivo e flag PASS/NO_GO);
  - Capítulo 4 atualizado (em especial filemap e plano de execução).

Essa política evita que a camada OracleOps entre no tronco principal em estado indefinido.

---

### 4.3.5 Rotina diária de execução: manhã, bloco de foco, fechamento

A rotina diária é pensada para evitar a curva “tudo parece ótimo até o último dia”, típica de sprints com muito acoplamento.

#### Início do dia

Objetivo: garantir que o estado atual da sprint é compreendido e minimamente saudável antes de escrever mais código.

Passos sugeridos:
- atualizar a branch da sprint localmente;
- rodar rapidamente:
  - testes de domínio relevantes;
  - scripts de gates leves (por exemplo, `s33_g0`, `s33_g1`, `s33_g2`);
- revisar o estado dos scorecards para ver se algum gate regrediu.

Se algo quebrou durante a noite (por merges de PRs), a prioridade passa a ser **voltar o sprint ao estado verde**, não abrir novas frentes.

#### Blocos de foco

Separar o dia em blocos de foco, por exemplo:

- bloco 1 (manhã): backend/domínio/serviços;
- bloco 2 (tarde): frontend/UX/cockpit;
- bloco 3 (fim de tarde/início da noite): operação/runbooks/evidências.

Essa divisão não é rígida, mas evita que o time passe dias só na UI ou só em código de domínio sem testar nada de ponta a ponta.

#### Fechamento do dia

Antes de encerrar:
- rodar pelo menos uma vez os scripts de gate diretamente impactados pelas mudanças do dia;
- atualizar, se necessário, pequenos trechos do Capítulo 4 (por exemplo, filemap, passos de gate que mudaram);
- registrar rapidamente quaisquer riscos percebidos (por exemplo, SLO sem query, runbook que se mostrou frágil em teste interno).

Essa disciplina reduz a chance de surpresas de última hora na preparação da ORR.

---

### 4.3.6 Sinais de cheiro ruim (anti‑padrões de execução)

Alguns sinais indicam que a execução da S33 está saindo dos trilhos:

- PRs genéricos sem referência clara à spec (“ajustes cockpit”, “fixes diversos”);
- scripts de gate que “sempre passam” porque só fazem echos ou checam coisas triviais;
- branch da sprint passando vários dias com o workflow `s33-gates.yml` quebrado;
- acúmulo de trabalho de runbooks e bundles de evidência empurrado para o fim da sprint;
- pessoas precisando rodar comandos longos e manuais para “reproduzir o estado da S33” em vez de depender de scripts e workflows.

Quando um desses sinais aparece, a recomendação é **pausar novas features** e recuperar disciplina: deixar gates verdes, ajustar scripts, corrigir PRs mal estruturados.

---

### 4.3.7 Regra de ouro: CI e rotina diária como espelho da sprint

O objetivo final deste bloco é garantir que CI e rotina diária sirvam como **espelho fiel** da Sprint 33:

- Se G0–G4 estão em PASS no CI e a ORR foi executada com evidência, a S33 está realmente entregue.
- Se o CI conta uma história diferente da documentação (por exemplo, `s33_g3` sempre falha, mas documentos dizem que SLOs estão prontos), a sprint não está concluída — é a documentação que está mentindo.

A S33 só cumpre seu propósito quando **código, docs, scripts, scorecards, CI e prática diária** convergem para a mesma realidade operacional. Este bloco define o chão em que essa convergência acontece.

