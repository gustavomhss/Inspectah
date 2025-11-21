# Inspectah – Sprint 12
## Capítulo 4 — Execução & Codex (Ingestão Contínua & Comunidade v0)

---

## 0. TL;DR — quando este capítulo está realmente “cumprido”

Este Capítulo 4 só é considerado **cumprido** quando todas estas condições forem verdade ao mesmo tempo:

1. Existe um **plano de execução em waves** (W0.5…W4) para a S12, claro o suficiente para qualquer dev + Codex seguirem sem “interpretar” a sprint.
2. Cada **cluster de trabalho** (ingestão, pipeline+Debunker+casos, Explorer+feedback, observabilidade) tem um **Superprompt Codex** associado, alinhado com os Capítulos 1–3 e com o DNA.
3. Todos os scripts `bin/s12_g0…bin/s12_g8` existem, rodam localmente e produzem scorecards + evidências nos caminhos definidos no Cap. 2–3.
4. A S12 consegue ser executada ponta a ponta a partir de um **runbook local único** (este capítulo), sem precisar “adivinhar” ordem, scripts ou arquivos.

Se qualquer uma dessas condições falhar, o Cap. 4 ainda é rascunho.

---

## 1. Papel do Capítulo 4 dentro da Sprint 12

Recap rápido dos capítulos anteriores:

- **Cap. 1 – Visão**: define o que a S12 promete (serviço 24/7, Debunker v0 em tudo, casos/temas com timeline, Explorer v0, feedback mínimo).
- **Cap. 2 – Gates**: crava como medimos essa promessa (SLIs/SLOs, G0…G8, DoD da sprint).
- **Cap. 3 – Arquitetura & Filemap**: fixa os componentes, a arquitetura e o lugar de cada arquivo no repo.

Este **Capítulo 4 – Execução & Codex** responde à pergunta:

> “Na prática, em que ordem eu faço as coisas, quais arquivos o Codex deve editar, que scripts eu rodo e como sei que a wave acabou?”

Ele entrega:

- plano em waves (W0.5…W4) com objetivos, escopo, gates e critérios de saída;
- orientação de como usar o Codex (Superprompts por wave);
- instruções de linha de comando para rodar gates e validar a S12 localmente e em CI.

---

## 2. Papéis e modo de trabalho

### 2.1. Papéis envolvidos

- **Você (PO/Arquiteto)**  
  Define prioridades da sprint, aprova docs, revisa scorecards, decide GO/NO-GO da S12.

- **ChatGPT (PO assistente)**  
  Refina Cap. 1–4, ajuda a criar Superprompts, lê scorecards/evidências e aponta gaps conceituais.

- **Codex (dev de linha)**  
  Implementa código e scripts a partir de Superprompts. Não decide escopo nem arquitetura: apenas executa o que está fixado nos capítulos e no DNA.

- **Guardião dos Contratos (Meyer + time)**  
  Confere que nenhuma implementação viola invariantes da S12, da S10 (Truth-DB + Guardião) ou do DNA. Tem poder de veto em mudanças que “remendam” gates.

### 2.2. Ciclo padrão de trabalho

1. Garantir que o repo está em um estado limpo e alinhado com main.
2. Escolher uma **wave** da S12 (W0.5…W4).
3. Rodar o **Superprompt da wave** no Codex, apontando para o repo local.
4. Deixar o Codex criar/editar arquivos conforme o filemap do Cap. 3.
5. Rodar os **gates ligados àquela wave**.
6. Ajustar o que for necessário até os scorecards ficarem verdes ou com WARN permitido.
7. Avançar para a próxima wave.
8. Ao final, rodar G0…G7 em série e, por fim, G8 para GO/NO-GO.

---

## 3. Pré‑flight local (antes de encostar na S12)

Passos obrigatórios antes de começar qualquer wave:

1. Confirmar repo/caminho

   ```bash
   cd /Users/gustavoschneiter/Documents/Inspectah
   git status
   ```

   - O repo deve ser o Inspectah canônico.

2. Atualizar branch base

   ```bash
   git checkout main
   git pull --ff-only
   ```

3. Criar/entrar na branch da S12

   Sugestão de nome:

   ```bash
   git checkout -b s12_ingestao_continua_comunidade_v0
   ```

   (ou reusar uma branch existente da S12, se já criada.)

4. Garantir que Cap. 1–3 da S12 estão presentes

   - `Sprint 12/Capitulo 1.md`
   - `Sprint 12/Capitulo 2.md`
   - `Sprint 12/Capitulo 3.md`

5. Rodar G0 (mesmo que ainda seja simples)

   ```bash
   bash bin/s12_g0_env_repo.sh || echo "G0 ainda não finalizado — ok para início de implementação"
   ```

   O objetivo é garantir que o skeleton do gate existe e segue o padrão do DNA.

---

## 4. Execução em waves (W0.5…W4)

A S12 será entregue em **4 waves principais**, mais uma wave opcional de skeletons:

- **Wave 0.5 – Skeletons mínimos** (opcional, mas recomendada)
- **Wave 1 – Ingestão & Scheduler** (núcleo de G1 + preparação de G2)
- **Wave 2 – Pipeline + Debunker + Truth‑DB adapter + Casos/Timeline** (G2–G4)
- **Wave 3 – Explorer v0 + Feedback** (G5–G6)
- **Wave 4 – Observabilidade & CI** (G7–G8 + amarração de todos os gates)

Cada wave tem:

- **Objetivo** – o que precisa mudar no sistema;
- **Escopo** – arquivos/módulos a criar ou evoluir;
- **Gates alvo** – quais G* devem sair de stub e ficar “reais”;
- **Critério de saída** – quando a wave pode ser considerada concluída;
- **Superprompt Codex** – instruções de alto nível para o Codex.

---

## 5. Wave 0.5 — Skeletons mínimos (opcional, mas recomendada)

### 5.1. Objetivo

Criar skeletons (arquivos vazios ou quase) para **todos** os componentes citados no Cap. 3, de forma que:

- o repo não quebre ao rodar nenhum `bin/s12_g*` (mesmo que retornem “não implementado”);
- o Codex possa abrir e expandir arquivos existentes em vez de “inventar caminhos”.

### 5.2. Escopo mínimo

Skeletons para:

- scripts de gate: `bin/s12_g0_env_repo.sh` … `bin/s12_g8_decision.sh`;
- ingestão: `scripts/s12_sources_registry.py`, `scripts/s12_scheduler.py`, `scripts/s12_run_connector.py`, `scripts/s12_connectors/*.py`;
- pipeline: `scripts/s12_ingest_pipeline.py`, `scripts/s12_normalizers/*.py`;
- decisão: `scripts/s12_debunker_runner.py`, `scripts/s12_truthdb_adapter.py`;
- casos/timeline: `scripts/s12_case_service.py`, `scripts/s12_timeline_service.py`;
- feedback: `scripts/s12_feedback_service.py`;
- Explorer backend: `app/explorer/routes.py` (se não existir);
- Explorer frontend: `ui/explorer/*.tsx`;
- painel de feedback interno: `ui/admin/FeedbackListPage.tsx`.

### 5.3. Critério de saída

- Todos os arquivos do filemap S12 existem (mesmo que com implementação mínima).
- Rodar `bash bin/s12_g0_env_repo.sh` não resulta em “arquivo inexistente”.
- Rodar `bash bin/s12_g1_sources_scheduler.sh` falha de forma controlada e legível (ex.: `exit 1` com mensagem “G1 ainda não implementado”).

### 5.4. Superprompt Codex — Wave 0.5 (esqueleto)

Resumo do conteúdo (para ser usado ao chamar o Codex):

- Contexto: Sprint 12, Cap. 1–3, objetivo de skeletons.
- Instruções:
  - criar todos os arquivos listados acima, com docstrings e comentários claros do papel de cada módulo;
  - não implementar lógica “inteligente”: apenas estrutura, interfaces e mensagens de “not implemented yet” nos scripts de gate;
  - seguir padrões de estilo e logging já usados em sprints anteriores.
- Restrições:
  - nada de blockchain, reputação ou Sistema de Blocos completo;
  - nada de TODO/TBD genérico — os comentários devem descrever a intenção concreta do módulo.

---

## 6. Wave 1 — Ingestão & Scheduler (G1 + preparo de G2)

### 6.1. Objetivo

Fazer a S12 **começar a respirar**: fontes cadastradas, scheduler disparando conectores, eventos brutos chegando até o pipeline.

### 6.2. Escopo

- `scripts/s12_sources_registry.py`
  - definir estrutura de dados para fontes (id, domínio, tipo, URL, cadência, flags, auth);
  - implementar funções para listar fontes por domínio/cadência;
  - exportar snapshot das configurações em `out/evidence/S12_G1/sources_config.json`.

- `scripts/s12_scheduler.py`
  - implementar função principal que, numa janela de teste, decide quais fontes rodar;
  - chamar `s12_run_connector` por `id_fonte`;
  - logar cada tentativa de execução (sucesso/falha).

- `scripts/s12_run_connector.py`
  - carregar config da fonte no registry;
  - chamar conector correspondente em `scripts/s12_connectors/*`;
  - entregar eventos brutos ao pipeline (mesmo que o pipeline ainda faça pouco).

- `scripts/s12_connectors/*.py`
  - implementar 2–3 conectores piloto (ex.: 2 para `obra_publica`, 1 para `evento_climatico`).

- `bin/s12_g1_sources_scheduler.sh`
  - rodar scheduler em modo de teste (janela pequena);
  - medir frescor por fonte/domínio (SLI‑1, mínimo);
  - gerar `out/scorecards/S12_G1_sources_scheduler.json` + `out/evidence/S12_G1/scheduler_logs.txt`.

### 6.3. Gates alvo

- G1 sai de stub e passa a ter lógica real de ingestão + scheduler.
- G2 ainda parcial: pipeline pode apenas “aceitar” eventos brutos, sem normalização completa.

### 6.4. Critério de saída

- `bash bin/s12_g1_sources_scheduler.sh` roda do início ao fim sem crash.
- Scorecard `S12_G1_sources_scheduler.json` existe e responde às perguntas do Cap. 2.
- Evidências em `out/evidence/S12_G1/` estão legíveis (config de fontes + logs).

### 6.5. Superprompt Codex — Wave 1 (esqueleto)

Elementos que devem aparecer no prompt:

- link para Cap. 1–3 (ingestão + scheduler);
- lista de arquivos que podem ser editados;
- pedido explícito para: 
  - estruturar o registry de fontes;
  - implementar scheduler e run_connector;
  - criar conectores piloto;
  - implementar o gate G1 com scorecard e evidências;
- reforço das restrições (sem blockchain/reputação/Sistema de Blocos completo).

---

## 7. Wave 2 — Pipeline, Debunker, Truth‑DB adapter & Casos/Timeline (G2–G4)

### 7.1. Objetivo

Transformar a ingestão em **fatos coerentes**: pipeline de normalização, Debunker v0 integrado, adaptador Truth‑DB funcionando, casos e timelines com invariantes respeitadas.

### 7.2. Escopo

- `scripts/s12_ingest_pipeline.py`
  - ler eventos brutos produzidos na Wave 1;
  - chamar normalizadores em `scripts/s12_normalizers/*`;
  - produzir eventos normalizados com campos mínimos do Cap. 1/3;
  - resolver `id_caso` via `s12_case_service`;
  - enviar eventos elegíveis para `s12_debunker_runner`.

- `scripts/s12_normalizers/*.py`
  - para cada domínio piloto, mapear payload de origem → evento normalizado;
  - tratar edge cases (campos ausentes, formatos variáveis) com logs claros.

- `scripts/s12_debunker_runner.py`
  - integrar com Debunker v0 (já existente ou a partir de módulo interno);
  - registrar estado + racional por evento elegível;
  - chamar adaptador Truth‑DB.

- `scripts/s12_truthdb_adapter.py`
  - implementar operações de alto nível para S12 (register_event, apply_debunker_decision, get_case_snapshot);
  - garantir que nenhuma parte da S12 toca diretamente schema interno da Truth‑DB.

- `scripts/s12_case_service.py` & `scripts/s12_timeline_service.py`
  - manter a entidade `Caso` e suas timelines;
  - aplicar invariantes I1–I3 do Cap. 1;
  - exportar snapshots para evidência do G4.

- scripts de gate:
  - `bin/s12_g2_ingest_pipeline.sh` – testa pipeline com fixtures, idempotência e integridade;
  - `bin/s12_g3_debunker_coverage.sh` – mede `debunker_coverage` e produz amostra de decisões;
  - `bin/s12_g4_cases_timeline.sh` – testa invariantes de casos/timelines com cenários controlados.

### 7.3. Gates alvo

- G2: pipeline íntegro, idempotente, com `case_integrity_ratio` nas amostras de teste dentro do esperado.
- G3: `debunker_coverage = 1.0` nos cenários de teste.
- G4: invariantes de casos/timelines válidas em domínios piloto.

### 7.4. Critério de saída

- Scripts G2–G4 rodam sem crash:

  ```bash
  bash bin/s12_g2_ingest_pipeline.sh
  bash bin/s12_g3_debunker_coverage.sh
  bash bin/s12_g4_cases_timeline.sh
  ```

- Scorecards S12_G2, S12_G3, S12_G4 existem e seguem o formato do Cap. 2.
- Evidências em `out/evidence/S12_G2/`, `S12_G3/`, `S12_G4/` estão consistentes com o que os gates alegam.

### 7.5. Superprompt Codex — Wave 2 (esqueleto)

O prompt da Wave 2 deve:

- relembrar o estado da Wave 1 (ingestão funcionando);
- apontar arquivos que podem ser mexidos (pipeline, normalizers, debunker_runner, truthdb_adapter, case/timeline services, scripts de gate);
- exigir implementação completa do fluxo ingestão → normalização → Debunker → Truth‑DB → casos/timelines;
- reforçar SLIs/SLOs dos gates G2–G4 e invariantes I1–I3;
- proibir qualquer referência a blockchain/reputação/Sistema de Blocos completo.

---

## 8. Wave 3 — Explorer v0 + Feedback (G5–G6)

### 8.1. Objetivo

Colocar um humano na frente do Inspectah: Explorer v0 “usável de verdade” e fluxo de feedback completo.

### 8.2. Escopo

- Backend Explorer (`app/explorer/routes.py`)
  - implementar rotas:
    - `GET /explorer/cases?query=...`
    - `GET /explorer/cases/{id_caso}`
    - `POST /explorer/cases/{id_caso}/feedback`
    - `POST /explorer/events/{id_evento}/feedback`
  - integrar com `s12_case_service`, `s12_timeline_service`, `s12_feedback_service`.

- Frontend Explorer (`ui/explorer/*`)
  - `SearchPage.tsx` – busca de casos, lista com status geral;
  - `CasePage.tsx` – detalhes do caso, timeline, fontes;
  - `components/Timeline.tsx` – renderização da timeline;
  - `components/FeedbackButton.tsx` – botão ligado às rotas de feedback.

- Serviço de feedback (`scripts/s12_feedback_service.py`)
  - criar, listar e atualizar feedbacks com estados (`novo`, `em_analise`, `resolvido`).

- Painel interno de feedback (`app/feedback/routes.py`, `ui/admin/FeedbackListPage.tsx`)
  - listar feedbacks por status;
  - permitir alterar status.

- Scripts de gate:
  - `bin/s12_g5_explorer_e2e.sh` – executa fluxos F1–F3 do Cap. 2;
  - `bin/s12_g6_feedback_flow.sh` – cria feedbacks e mede entrega até a fila interna.

### 8.3. Gates alvo

- G5: Explorer v0 navegável, `explorer_success_rate` dentro do SLO.
- G6: feedback ponta a ponta com `feedback_delivery_ratio = 1.0` nos cenários de teste.

### 8.4. Critério de saída

- Scripts G5–G6 rodam sem crash:

  ```bash
  bash bin/s12_g5_explorer_e2e.sh
  bash bin/s12_g6_feedback_flow.sh
  ```

- Scorecards S12_G5 e S12_G6 existem, com `status = "PASS"` (ou WARN permitido pelo Cap. 2).
- Na prática, é possível:
  - buscar um caso;
  - abrir sua página;
  - ver timeline + fontes;
  - criar feedback e enxergá-lo na fila interna.

### 8.5. Superprompt Codex — Wave 3 (esqueleto)

O prompt da Wave 3 deve:

- partir do pressuposto de que ingestão + pipeline + casos/timelines já funcionam;
- focar em rotas e UI do Explorer v0 + feedback;
- listar explicitamente quais arquivos de backend/frontend e scripts de gate podem ser modificados;
- exigir testes E2E/smokes para alimentar G5 e G6;
- reforçar que não existe “comunidade avançada” — é só leitura + feedback mínimo.

---

## 9. Wave 4 — Observabilidade & CI (G7–G8 + amarração)

### 9.1. Objetivo

Garantir que a S12 pode rodar 24/7 sem voar cego e que os gates se encaixam em um fluxo reexecutável (local + CI).

### 9.2. Escopo

- Observabilidade
  - instrumentar serviços para expor métricas ligadas a SLI‑1…SLI‑5;
  - organizar logs por componente (ingestão, Debunker, Explorer, feedback);
  - criar coletores/dumps que `bin/s12_g7_observabilidade.sh` possa ler.

- `bin/s12_g7_observabilidade.sh`
  - calcular SLIs em uma janela de operação (real ou simulada);
  - gerar `out/scorecards/S12_G7_observabilidade.json` + `metrics_snapshot.json` + `logs_sample.txt`.

- `bin/s12_g8_decision.sh`
  - consolidar scorecards G0…G7;
  - aplicar regras de decisão do Cap. 2;
  - gerar `out/scorecards/S12_G8_decision.json` + `out/evidence/S12_G8/summary.md`.

- Integração com CI/local
  - se existir um orquestrador de CI local (ex.: `bin/ci_local.sh`), adicionar uma etapa "S12" que roda `bin/s12_gates_all.sh`;
  - criar/ajustar workflow em `.ci/` ou `.github/workflows/` (ex.: `_s12-gates.yml`) para rodar G0…G7 em cron ou on-push, conforme DNA.

### 9.3. Gates alvo

- G7: observabilidade + SLIs da S12 dentro dos SLOs definidos.
- G8: decisão GO/NO-GO automatizada, com wrap humano mínimo e honesto.

### 9.4. Critério de saída

- `bash bin/s12_g7_observabilidade.sh` e `bash bin/s12_g8_decision.sh` rodam sem crash.
- Scorecards S12_G7 e S12_G8 existem e fazem sentido.
- Existe ao menos um comando ou workflow único que rode todos os gates da S12 (ex.: `bash bin/s12_gates_all.sh`).

### 9.5. Superprompt Codex — Wave 4 (esqueleto)

O prompt da Wave 4 deve:

- focar em instrumentação leve, mas completa para SLIs SLI‑1…SLI‑5;
- especificar como G7 e G8 devem funcionar (entradas, saídas, formatos);
- pedir integração da S12 em algum pipeline de CI/local existente;
- reforçar limites: nada de stack observabilidade gigante (S12 quer visibilidade suficiente, não um datacenter Prometheus completo).

---

## 10. Runbook rápido (modo humano)

Sequência sugerida para você tocar a S12 na prática:

1. Criar (ou entrar na) branch da S12:

   ```bash
   cd /Users/gustavoschneiter/Documents/Inspectah
   git checkout main
   git pull --ff-only
   git checkout -b s12_ingestao_continua_comunidade_v0
   ```

2. Verificar Cap. 1–3 em `Sprint 12/`.

3. (Opcional) Rodar Wave 0.5 com Codex para criar skeletons.

4. Wave 1 (ingestão & scheduler)
   - Rodar Superprompt W1 no Codex.
   - Rodar `bash bin/s12_g1_sources_scheduler.sh` e ajustar até o scorecard G1 ficar coerente.

5. Wave 2 (pipeline, Debunker, Truth‑DB adapter, casos/timelines)
   - Rodar Superprompt W2.
   - Rodar `bash bin/s12_g2_ingest_pipeline.sh`, `bash bin/s12_g3_debunker_coverage.sh`, `bash bin/s12_g4_cases_timeline.sh`.

6. Wave 3 (Explorer v0 + feedback)
   - Rodar Superprompt W3.
   - Rodar `bash bin/s12_g5_explorer_e2e.sh` e `bash bin/s12_g6_feedback_flow.sh`.

7. Wave 4 (observabilidade & CI)
   - Rodar Superprompt W4.
   - Rodar `bash bin/s12_g7_observabilidade.sh` e `bash bin/s12_g8_decision.sh`.

8. Ao final, rodar `bash bin/s12_gates_all.sh` (se implementado) e verificar todos os scorecards G0…G7.

9. Se `S12_G8_decision.json` trouxer `decision = "GO"` e o wrap humano em `out/evidence/S12_G8/summary.md` estiver honesto quanto a riscos e débitos técnicos, a S12 está pronta para merge e uso real do V0.

---

## 11. Restrições finais para o Codex (mantra da S12)

Todo Superprompt da S12 deve repetir explicitamente:

- Não implementar blockchain, smart contracts ou anchors on-chain nesta sprint.
- Não implementar reputação numérica de fontes/usuários/feedbacks.
- Não implementar Sistema de Blocos completo (blocos/sub-blocos/componentes com promoção/demote).
- Não implementar comunidade avançada (perfis públicos, followers, ranking, votação, threads públicas).

A Sprint 12 existe para entregar:

> **Ingestão contínua confiável + Debunker v0 em tudo + casos/temas com timeline + Explorer v0 + feedback mínimo + observabilidade/gates decentes.**

Com Cap. 1–4 alinhados, a S12 vira um pacote completo: visão, contrato de qualidade, arquitetura e execução. A partir daqui, o trabalho é disciplinar: seguir as waves, chamar o Codex com Superprompts corretos e deixar os gates dizerem, objetivamente, se a sprint está GO ou não.

