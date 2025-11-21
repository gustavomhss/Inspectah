# Sprint 13 — Capítulo 4 — Plano de Execução (Codex, Waves, CI) — v2

Versão revisada em conjunto com a equipe (Jobs, Knuth, Kay, Lamport, Vitalik, Kleppmann, Meyer, Pavel), alinhada ao DNA, ao replanejamento de Fase 2 (sem blockchain / reputação / Sistema de Blocos agora) e aos Capítulos 1–3.

Este capítulo é o **manual operacional da Sprint 13**: se o Codex seguir isto com disciplina, o piloto multi-domínio sai do papel com todos os gates S13_G0…S13_G8 em PASS (ou WARN onde permitido), sem quebrar S12 e pronto para alimentar as próximas sprints.

---

## 0) Objetivo deste capítulo

Responder, de forma acionável, a quatro perguntas:

1. **Como o Codex deve trabalhar** durante a Sprint 13 (branch, estilo de mudanças, relação com S12).  
2. **Em que waves** a implementação se divide e o que cada wave precisa entregar.  
3. **Quais comandos** devem ser usados para validar o trabalho (local e CI).  
4. **Quando podemos declarar a Sprint 13 DONE**, do ponto de vista de execução.

Cap. 1 define o *porquê* e o *o quê*; Cap. 2 define *como validar*; Cap. 3 define *onde cada coisa vive*. Este Cap. 4 define **como chegar lá, passo a passo**.

---

## 1) Regras gerais de trabalho para o Codex

### 1.1 Estado inicial esperado

Antes de tocar em qualquer coisa da S13, o Codex assume que:

- o repositório `Inspectah` existe localmente, em um caminho do tipo:
  - `/Users/gustavoschneiter/Documents/Inspectah`
- a branch `main` está atualizada com a versão estável mais recente:
  - `git checkout main`
  - `git pull --ff-only origin main`
- a S12 está em **estado GO**, com os gates verdes:
  - `bash bin/s12_gates_all.sh`
  - `bash bin/s12_g8_decision.sh` (com `decision = "GO"`).

Se a S12 estiver quebrada, **a prioridade absoluta** é restaurar S12 (ou voltar para o tag estável) antes de prosseguir com a S13.

### 1.2 Branch da Sprint 13

A Sprint 13 roda em **branch dedicada**, seguindo o padrão das sprints anteriores:

- branch sugerida: `s13_piloto_multi_dominio_v0`

Fluxo recomendado:

1. Garantir `main` atualizado:
   - `git checkout main`
   - `git pull --ff-only origin main`
2. Criar a branch da sprint (se ainda não existir):
   - `git checkout -b s13_piloto_multi_dominio_v0`
3. Se a branch já existir:
   - `git checkout s13_piloto_multi_dominio_v0`
   - `git merge --ff-only main` (quando fizer sentido trazer updates).

Todas as mudanças da Sprint 13 devem acontecer nesta branch, até o momento do merge final para `main`.

### 1.3 Estilo de trabalho (Codex)

Princípios obrigatórios:

1. **Mudanças pequenas e coesas**  
   - Cada wave ou sub-tarefa deve focar em um grupo de arquivos/gates bem definido.  
   - Após cada bloco de mudanças, rodar os gates relevantes e corrigir falhas antes de seguir.

2. **Nunca quebrar S12 de forma silenciosa**  
   - Depois de alterações estruturais (especialmente em `scripts/`, `bin/` ou `config/`), rodar S12:
     - `bash bin/s12_gates_all.sh`
     - `bash bin/s12_g8_decision.sh`
   - Se algo da S12 falhar, **consertar imediatamente**.

3. **Escopo travado (sem blockchain / reputação / Sistema de Blocos)**  
   - A Sprint 13 usa **apenas** o backbone S12 (Debunker v0, Truth-DB em memória, casos/timeline, Explorer, feedback).  
   - Qualquer desejo de blockchain, reputação pesada ou Sistema de Blocos vai para backlog de Fase 2.

4. **Determinismo e reprodutibilidade**  
   - Não introduzir chamadas externas imprevisíveis.  
   - Gates e helpers da S13 devem produzir sempre as mesmas evidências para os mesmos inputs.

5. **Legibilidade e logs para humanos**  
   - Scripts `bin/s13_*` devem imprimir logs curtos e claros (padrão `[S13] -> ...`).  
   - Scorecards JSON devem ser simples, fáceis de ler, sem estruturas desnecessariamente profundas.

---

## 2) Mapa de Waves da Sprint 13

A Sprint 13 é executada em **4 waves principais**, mais uma fase final de merge/tag. Cada wave tem:

- foco claro;  
- artefatos-alvo;  
- gates que deve destravar.

### Visão geral

- **Wave 0 — Scaffolding S13**  
  - Objetivo: fazer a S13 “existir” no repo (config, scripts, bin, workflow) sem lógica completa.  
  - Gates afetados: S13_G0…G8 (modo skeleton / FAIL controlado).

- **Wave 1 — Pilotos multi-domínio + G0/G1 reais**  
  - Objetivo: definir pilotos concretos nos 6 domínios e garantir cobertura.  
  - Gates-alvo: S13_G0 (env_repo) e S13_G1 (pilotos_multi_dominio) em PASS.

- **Wave 2 — Timelines & Debunker (G2, G3)**  
  - Objetivo: garantir integridade de timeline e Debunker v0 operando em todos os pilotos.  
  - Gates-alvo: S13_G2, S13_G3 em PASS.

- **Wave 3 — Explorer & narrativas (G4, G5)**  
  - Objetivo: Explorer encontrando pilotos por domínio e narrativas mínimas completas.  
  - Gates-alvo: S13_G4, S13_G5 em PASS (G4 aceita WARN em casos específicos definidos no Cap. 2).

- **Wave 4 — Feedback, observabilidade e decisão (G6, G7, G8)**  
  - Objetivo: ciclo de feedback funcionando, SLIs consolidados, decisão GO/NO-GO documentada.  
  - Gates-alvo: S13_G6, S13_G7, S13_G8 em PASS.

---

## 3) Wave 0 — Scaffolding S13

### 3.1 Objetivo

Criar a **estrutura mínima** da Sprint 13 no repo, sem ainda exigir que os gates passem. Tudo deve existir, compilar e falhar de forma controlada (scorecards FAIL com mensagem clara), permitindo evolução incremental.

### 3.2 Tarefas da Wave 0

1. **Criar/ajustar documentos da S13**

   - Garantir a existência de:
     - `Sprint 13/Capitulo 1.md`
     - `Sprint 13/Capitulo 2.md`
     - `Sprint 13/Capitulo 3.md`
     - `Sprint 13/Capitulo 4.md` (este capítulo)
   - Opcionalmente, criar espelhos em `docs/` conforme Cap. 3.

2. **Criar arquivo de configuração de pilotos**

   - Criar `config/s13_pilotos.yml` com a estrutura base dos 6 domínios (mesmo que, por enquanto, sem casos finalizados).

3. **Criar helpers S13 em `scripts/` com skeleton**

   - Criar arquivos:
     - `scripts/s13_pilots_registry.py`
     - `scripts/s13_timeline_checks.py`
     - `scripts/s13_debunker_checks.py`
     - `scripts/s13_explorer_scenarios.py`
     - `scripts/s13_narratives_registry.py`
     - `scripts/s13_feedback_backlog.py`
     - `scripts/s13_metrics_snapshot.py`
   - Por enquanto, cada módulo pode expor funções vazias ou que levantem `NotImplementedError`, desde que importem sem erro.

4. **Criar scripts de gates S13 em `bin/` (modo skeleton)**

   - Scripts:
     - `bin/s13_g0_env_repo.sh`
     - `bin/s13_g1_pilotos_multi_dominio.sh`
     - `bin/s13_g2_cases_timeline_multi.sh`
     - `bin/s13_g3_debunker_multi_dominio.sh`
     - `bin/s13_g4_explorer_multi_dominio.sh`
     - `bin/s13_g5_narrativas_multi_dominio.sh`
     - `bin/s13_g6_feedback_multi_dominio.sh`
     - `bin/s13_g7_observabilidade.sh`
     - `bin/s13_g8_decision.sh`
   - Em modo skeleton, cada script deve:
     - escrever um scorecard `status = "FAIL"` com campo `reason = "S13 skeleton"`;  
     - sair com código ≠ 0.

5. **Criar orquestrador e workflow S13**

   - `bin/s13_gates_all.sh`:
     - rodar G0…G7 em ordem;  
     - parar no primeiro FAIL;  
     - logs padrão `[S13] -> s13_gX_*.sh`.
   - `.github/workflows/_s13-gates.yml`:
     - clonar padrão do `_s12-gates.yml`, mas chamando `bin/s13_gates_all.sh`.

### 3.3 Checkpoint da Wave 0

- Todos os arquivos S13 existem e rodam sem erro de import;  
- `bash bin/s13_gates_all.sh` falha de forma controlada (skeleton), **não por erro de import ou crash**;  
- S12 continua 100% verde.

---

## 4) Wave 1 — Pilotos multi-domínio + G0/G1

### 4.1 Objetivo

Colocar **pilotos reais** nos 6 domínios e transformar G0/G1 em gates de verdade: ambiente correto e cobertura de domínios em 100%.

### 4.2 Tarefas da Wave 1

1. **Preencher `config/s13_pilotos.yml` com casos concretos**

   - Para cada domínio:
     - `obra_publica`
     - `evento_climatico`
     - `projeto_lei`
     - `carreira_politica`
     - `influencer`
     - `atleta`
   - Definir **pelo menos 1 caso piloto real**, coerente com Cap. 1.  
   - Garantir campos mínimos: `id`, `dominio`, `nome`, `descricao_curta`, `periodo` (quando aplicável), `local` (quando fizer sentido).

2. **Implementar `scripts/s13_pilots_registry.py`**

   - Ler e validar `config/s13_pilotos.yml`;
   - verificar se há exatamente os 6 domínios esperados;
   - garantir unicidade de IDs dos pilotos;
   - expor funções:
     - `list_domains()`
     - `list_pilots()`
     - `get_pilots_by_domain(domain_id)`
     - `get_pilot(pilot_id)`

3. **Implementar `bin/s13_g0_env_repo.sh` (real)**

   Gate G0 deve checar:

   - se estamos dentro do repo correto (`Inspectah` oficial);
   - se `remote.origin.url` aponta para o repositório esperado;  
   - se a branch é `main` ou `s13_piloto_multi_dominio_v0`;  
   - se a S12 está em GO (scorecard `S12_G8_decision.json` presente e `decision = "GO"`);  
   - se os 4 Capítulos da S13 existem.

   Saídas:

   - `out/scorecards/S13_G0_env_repo.json`
   - `out/evidence/S13_G0/env_snapshot.txt`

4. **Implementar `bin/s13_g1_pilotos_multi_dominio.sh` (real)**

   - Usar `s13_pilots_registry` para carregar pilotos;
   - calcular `domain_pilot_coverage` (SLI-1);  
   - exigir pelo menos 1 piloto por domínio;
   - registrar, em evidência, a lista de pilotos por domínio.

   Saídas:

   - `out/scorecards/S13_G1_pilotos_multi_dominio.json`
   - `out/evidence/S13_G1/pilotos_resolved.json`

### 4.3 Checkpoint da Wave 1

- `bash bin/s13_g0_env_repo.sh` → PASS;  
- `bash bin/s13_g1_pilotos_multi_dominio.sh` → PASS e `domain_pilot_coverage = 1.0`;  
- `bash bin/s13_gates_all.sh` agora avança pelo menos até o G2.

---

## 5) Wave 2 — Timelines & Debunker (G2, G3)

### 5.1 Objetivo

Garantir que, para todos os pilotos:

- a **timeline** é íntegra e coerente com as invariantes;  
- o **Debunker v0** cobre os eventos principais com explicação mínima.

### 5.2 Tarefas da Wave 2

1. **Implementar `scripts/s13_timeline_checks.py`**

   - Para cada piloto em `s13_pilots_registry`:
     - montar timeline usando `scripts/s12_case_service.py` e `scripts/s12_timeline_service.py`;  
     - validar invariantes (ordem de eventos, estados válidos, ausência de loops/impossibilidades);  
     - exportar `out/evidence/S13_G2/timelines/<pilot_id>.json`.
   - Calcular `pilot_timeline_integrity_ratio` e lista de violações.

2. **Implementar `bin/s13_g2_cases_timeline_multi.sh`**

   - Orquestrar `s13_timeline_checks`;
   - escrever `out/scorecards/S13_G2_cases_timeline_multi.json` com status, `pilot_timeline_integrity_ratio` e violações.

3. **Implementar `scripts/s13_debunker_checks.py`**

   - Para cada piloto, obter eventos relevantes usando o backbone S12;  
   - chamar Debunker v0 (via `scripts/s12_debunker_runner.py` ou helper dedicado);  
   - exigir decisão + explicação mínima para a grande maioria dos eventos;
   - exportar decisões por domínio em `out/evidence/S13_G3/decisions_by_domain/<dominio>.json`;
   - calcular `debunker_explanation_coverage` por domínio e global.

4. **Implementar `bin/s13_g3_debunker_multi_dominio.sh`**

   - Orquestrar `s13_debunker_checks`;
   - gravar `out/scorecards/S13_G3_debunker_multi_dominio.json` com `debunker_explanation_coverage`.

### 5.3 Checkpoint da Wave 2

- G2 e G3 em PASS, com SLI-2/SLI-3 dentro do SLO de Cap. 2;  
- `bash bin/s13_gates_all.sh` avança até G4;  
- S12 continua verde.

---

## 6) Wave 3 — Explorer & Narrativas (G4, G5)

### 6.1 Objetivo

Assegurar que:

- o **Explorer** consegue achar e exibir os pilotos de todos os domínios;  
- cada caso piloto tem uma **narrativa mínima legível** e completa.

### 6.2 Tarefas da Wave 3

1. **Definir cenários do Explorer**

   - Preencher `docs/sprint_13_cenarios_explorer.md` com cenários por domínio:
     - query de busca (texto, filtros);  
     - piloto esperado;  
     - checks mínimos (timeline visível, estado atual, etc.).

2. **Implementar `scripts/s13_explorer_scenarios.py`**

   - Ler cenários do arquivo de docs ou de um JSON derivado;  
   - chamar backend do Explorer (função interna ou HTTP local com test client);  
   - validar se o caso retornado corresponde ao piloto esperado;  
   - calcular `explorer_success_rate` com breakdown por domínio;  
   - exportar evidências em `out/evidence/S13_G4/queries/<cenario_id>.json`.

3. **Implementar `bin/s13_g4_explorer_multi_dominio.sh`**

   - Orquestrar `s13_explorer_scenarios`;
   - gravar `out/scorecards/S13_G4_explorer_multi_dominio.json`.

4. **Criar/consolidar narrativas dos casos piloto**

   - Para cada piloto, criar narrativa mínima com:
     - título;  
     - descrição curta;  
     - estado atual em linguagem humana;  
     - parágrafo de resumo.
   - Fonte pode ser:
     - campos textuais em `config/s13_pilotos.yml`;  
     - arquivos `out/evidence/S13_G5/narrativas/<pilot_id>.md`;  
     - ou combinação, desde que consumo seja determinístico.

5. **Implementar `scripts/s13_narratives_registry.py`**

   - Carregar narrativas por piloto;  
   - validar completude;  
   - calcular `narrative_completeness_ratio`;  
   - gerar lista de casos incompletos.

6. **Implementar `bin/s13_g5_narrativas_multi_dominio.sh`**

   - Orquestrar `s13_narratives_registry`;  
   - gravar `out/scorecards/S13_G5_narrativas_multi_dominio.json` e narrativas em `out/evidence/S13_G5/narrativas/*.md`.

### 6.3 Checkpoint da Wave 3

- `explorer_success_rate` dentro do SLO (ou WARN bem justificado conforme Cap. 2);  
- `narrative_completeness_ratio = 1.0`;  
- G4 e G5 em PASS (com WARN só onde permitido);
- `bash bin/s13_gates_all.sh` avança até G6.

---

## 7) Wave 4 — Feedback, Observabilidade e Decisão (G6, G7, G8)

### 7.1 Objetivo

Fechar o ciclo do piloto multi-domínio:

- feedback funcionando ponta a ponta em todos os domínios;  
- métricas agregadas em um snapshot único;  
- decisão GO/NO-GO clara, com backlog para S14.

### 7.2 Tarefas da Wave 4

1. **Definir cenários de feedback**

   - Preencher `docs/sprint_13_cenarios_feedback.md` com cenários distribuídos entre os domínios:
     - tipo de problema (info errada, evento faltando, dúvida sobre Debunker etc.);  
     - piloto alvo;  
     - estado esperado no painel (novo, em análise, resolvido etc.).

2. **Implementar `scripts/s13_feedback_backlog.py`**

   - Exercitar o fluxo de feedback usando o backend da S12;  
   - criar feedbacks ligados a casos piloto;  
   - validar listagem e atualização de status;  
   - calcular `feedback_delivery_ratio` (SLI-5);  
   - exportar backlog consolidado em `out/evidence/S13_G6/backlog_s14_seed.json`.

3. **Implementar `bin/s13_g6_feedback_multi_dominio.sh`**

   - Orquestrar `s13_feedback_backlog`;  
   - gravar `out/scorecards/S13_G6_feedback_multi_dominio.json`.

4. **Implementar `scripts/s13_metrics_snapshot.py`**

   - Ler scorecards S13_G0…S13_G6;  
   - consolidar SLI-1…SLI-6;  
   - quando fizer sentido, comparar com números da S12;  
   - gravar `out/evidence/S13_G7/metrics_snapshot.json` e `out/evidence/S13_G7/risks_and_debts.md`.

5. **Implementar `bin/s13_g7_observabilidade.sh`**

   - Orquestrar `s13_metrics_snapshot`;  
   - gravar `out/scorecards/S13_G7_observabilidade.json` com SLIs consolidados e flags de regressão.

6. **Implementar `bin/s13_g8_decision.sh` (+ opcional `scripts/s13_decision.py`)**

   - Ler scorecards S13_G0…S13_G7;  
   - aplicar as regras de GO/NO-GO definidas no Cap. 2 (gates HARD vs SOFT);  
   - gerar `out/scorecards/S13_G8_decision.json` com `decision = "GO"` ou `"NO_GO"`;  
   - gerar `out/evidence/S13_G8/summary.md` com resumo textual da decisão, WARNs aceitos e riscos/próximos passos.

### 7.3 Checkpoint da Wave 4

- G6 e G7 em PASS (com WARNs apenas onde permitido);  
- `bash bin/s13_g8_decision.sh` → PASS com `decision = "GO"`;  
- backlog semente para S14 pronto em `out/evidence/S13_G6/backlog_s14_seed.json`.

---

## 8) Comandos de referência (execução local)

Ao longo da Sprint 13, o operador/Codex deve usar alguns comandos como rotina:

1. **Atualizar `main`**

```bash
cd /Users/gustavoschneiter/Documents/Inspectah
git checkout main
git pull --ff-only origin main
```

2. **Criar/entrar na branch da S13**

```bash
# primeira vez
git checkout -b s13_piloto_multi_dominio_v0

# vezes seguintes
git checkout s13_piloto_multi_dominio_v0
```

3. **Rodar gates da S12 (sanidade)**

```bash
bash bin/s12_gates_all.sh
bash bin/s12_g8_decision.sh
```

4. **Rodar gates da S13 (sanidade da sprint)**

```bash
bash bin/s13_gates_all.sh
bash bin/s13_g8_decision.sh
```

5. **CI local completo (quando S13 estiver plugada em ci_local)**

```bash
bash bin/ci_local.sh
```

---

## 9) Definition of Done (execução) da Sprint 13

A Sprint 13 só está **executada** quando todas as condições abaixo forem verdadeiras:

1. **Arquitetura e arquivos**

- Todos os arquivos definidos no Cap. 3 existem e estão implementados (config, scripts, bin, docs, workflow);
- `config/s13_pilotos.yml` lista os 6 domínios com pelo menos 1 caso piloto cada;
- helpers S13 em `scripts/` funcionam e alimentam os SLIs/Gates do Cap. 2.

2. **Gates S12**

- `bash bin/s12_gates_all.sh` → PASS;  
- `bash bin/s12_g8_decision.sh` → `decision = "GO"`.

3. **Gates S13**

- `bash bin/s13_gates_all.sh` → todos os gates S13_G0…S13_G7 em PASS (com WARN apenas onde permitido pelo Cap. 2);  
- `bash bin/s13_g8_decision.sh` → `status = "PASS"` e `decision = "GO"`.

4. **Evidências**

- Todos os scorecards S13 estão presentes em `out/scorecards/`;  
- As pastas `out/evidence/S13_G*/` contêm:
  - timelines por piloto;  
  - decisões do Debunker por domínio;  
  - queries do Explorer;  
  - narrativas por caso piloto;  
  - backlog semente de feedback;  
  - snapshot de métricas;  
  - resumo final de decisão.

5. **Integração em `main`**

- A branch `s13_piloto_multi_dominio_v0` foi mergeada em `main` via PR revisado;  
- CI em `main` passa com os gates da S12 e S13 verdes;  
- opcionalmente, foi criado um tag de release para o marco da S13.

---

## 10) Guardrails finais para o Codex

1. **Não alterar DNA e sprints anteriores sem pedido explícito**  
   - Ajustes em S1–S12 só devem ocorrer quando estritamente necessários e sempre mantendo gates S12 verdes.

2. **Nenhuma antecipação de Fase 2**  
   - Não implementar blockchain, contestação on-chain, reputação avançada ou Sistema de Blocos;  
   - A Sprint 13 foca exclusivamente no piloto multi-domínio sobre o backbone S12.

3. **Gates como contrato, não como gambiarra**  
   - Nunca aliviar SLOs ou remover checagens apenas para “ficar verde”;  
   - Se um gate falha, a solução é corrigir a causa.

4. **Logs e evidências pensados para humanos**  
   - Mensagens de log e scorecards devem ser legíveis por quem não participou da implementação;  
   - Evidências devem contar a história do piloto S13 de forma inspecionável e auditável.

5. **Planejar sempre antes de grandes mudanças**  
   - Antes de cada wave, o Codex deve “listar arquivos e funções” que pretende tocar e **só então** aplicar mudanças;  
   - Após cada wave, rodar os gates relevantes e ajustar até tudo ficar verde.

Com isso, a Sprint 13 deixa de ser apenas intenção e passa a ser um **roteiro operacional fechado**: o Codex sabe **onde mexer, em que ordem, como validar e qual é a linha de chegada** para o piloto multi-domínio do Inspectah.

