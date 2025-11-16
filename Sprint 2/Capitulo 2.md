# Inspectah — Sprint 2
## Capítulo 2 — Gates, Evidências e Definição de Pronto da Implementação v0 (Core Data Hub) — v2.0

> Este capítulo responde a uma única pergunta: **“Como saber, sem discussão, se a Sprint 2 realmente entregou o Inspectah v0?”**
>
> Aqui transformamos os objetivos do Capítulo 1, o Sprint Macro e os Blocos 1–4 em **gates de implementação**, checklists de evidência e critérios de pronto. Nada é simbólico: ou passa com evidência concreta, ou não passa.

---

## 1) Mapa dos gates da Sprint 2

A Sprint 2 é validada por **sete gates sequenciais**, que cobrem do bootstrap até docs & retro:

- **S2-G0 — Bootstrap & Ambiente Dev OK**
  - Prova que o scaffolding existe e o ambiente de dev sobe de forma reprodutível.
  - Conecta principalmente a **S2.0** (infra & scaffolding) e ao filemap do Bloco 3.

- **S2-G1 — Field Designer v0 & IEL Core OK**
  - Prova que Field Designer v0 e IEL existem em código e funcionam em cenários simples.
  - Conecta a **S2.1** e a D9.2 (IEL).

- **S2-G2 — Explore API v0 OK + Rate Limit ativo**
  - Prova que a Explore API v0 cumpre D9.3 e respeita o contrato de rate limit v0.
  - Conecta a **S2.2** e às ações herdadas D9-API-001.

- **S2-G3 — Evidence Vault v0 OK + LGPD mínimo**
  - Prova que o Evidence Vault v0 grava e referencia evidências em conformidade com D9.4/D9.5.
  - Conecta a **S2.3** e às ações herdadas D9-LGPD-001.

- **S2-G4 — Ingestão v0 OK (1–2 fontes) + Observabilidade básica**
  - Prova que conseguimos ingerir dados de 1–2 fontes e enxergar o que acontece via logs/métricas.
  - Conecta a **S2.4** e **S2.5**.

- **S2-G5 — E2E Script OK (Fluxo Completo) + Testes básicos**
  - Prova que o fluxo end‑to‑end funciona com um comando único + testes básicos.
  - Conecta a **S2.6**.

- **S2-G6 — Docs operacionais v0 OK + Retro Sprint 2**
  - Prova que o Inspectah v0 pode ser entendido, rodado e evoluído por outros times.
  - Conecta a **S2.7** e alimenta o Capítulo 4 (retro & backlog).

Regra: **nenhum S2.x está “done” sem pelo menos um gate associado em PASS**, com evidência escrita.

---

## 2) Estrutura de evidências e matriz de gates

Na raiz da Sprint 2 (mesma pasta do Capítulo 1):

- `Capitulo 1.md` — contexto, objetivos, entregáveis da Sprint 2.
- `Capitulo 2.md` — este capítulo (gates, evidências, DoD).
- `Capitulo 3.md` — plano de execução / threads (será definido depois).
- `Capitulo 4.md` — lessons, retro e backlog da Sprint 2.

Subpasta exclusiva de evidências da Sprint 2:

- `evidence_s2/`
  - `s2_g0_bootstrap_checklist.md`
  - `s2_g1_field_designer_checklist.md`
  - `s2_g2_explore_api_checklist.md`
  - `s2_g3_evidence_vault_lgpd_checklist.md`
  - `s2_g4_ingest_obs_checklist.md`
  - `s2_g5_e2e_tests_checklist.md`
  - `s2_g6_docs_retro_checklist.md`
  - `s2_summary_gate_matrix.json`

### 2.1 Formato mínimo dos checklists

Cada `*_checklist.md` deve:

- Ter um cabeçalho com nome do gate, data e quem rodou (humano ou agente).
- Listar itens em formato binário (SIM/NÃO) com identificadores estáveis, ex.: `G0-BOOT-01`, `G1-FD-IEL-02`.
- Ter uma seção final “Notas e links” para apontar arquivos de log, comandos usados, PRs relevantes.

Exemplo de linha de checklist:

- `[G2-EXP-API-01] Endpoint principal de Explore responde 200 para consulta válida — SIM/NÃO`.

### 2.2 Matriz s2_summary_gate_matrix.json

A matriz de gates registra o estado global da sprint. Formato mínimo:

```json
[
  {
    "gate": "S2-G0",
    "name": "Bootstrap & Ambiente Dev OK",
    "status": "PENDING | PASS | FAIL",
    "evidence_path": "evidence_s2/s2_g0_bootstrap_checklist.md",
    "notes": ""
  }
]
```

Regras:

- `status` só pode ser `PASS` se o checklist existir e estiver completo.
- `notes` deve mencionar, quando aplicável, IDs de lessons (ex.: `S2-FD-001`) e PRs.
- Não é permitido remover entradas da matriz; apenas atualizar `status` e `notes`.

---

## 3) Gate S2-G0 — Bootstrap & Ambiente Dev OK

### 3.1 Objetivo do gate

Provar que o **scaffolding do Inspectah v0** existe, respeita o filemap do Bloco 3 e que o ambiente de desenvolvimento pode ser subido de forma reprodutível, sem hacks manuais.

### 3.2 Escopo do gate

- Verifica **S2.0** (infra & scaffolding) e não entra ainda em lógica de negócios.
- Garante que o repositório está pronto para receber o restante da implementação.

### 3.3 Entradas obrigatórias

- Capítulo 1 da Sprint 2.
- D9.0 (blueprint), D9.4 (data model/DDL), D9.6 (roadmap v0/v1/v1.x), D9.8 (miniplaybook).
- Filemap do Bloco 3 como referência de estrutura.

### 3.4 Saídas obrigatórias

- Estrutura de repositório compatível com o filemap do Bloco 3 (pelo menos pastas base de serviço, config, scripts, tests).
- Script/comando para subir o ambiente, por exemplo:
  - `bin/dev_up.sh` e, se usado, `docker-compose.yml`.
- README (mesmo preliminar) descrevendo como rodar o bootstrap.
- Arquivo `evidence_s2/s2_g0_bootstrap_checklist.md` preenchido.

### 3.5 Checklist de evidência (exemplos de itens)

- `G0-BOOT-01` — Existe script documentado para subir o ambiente local (SIM/NÃO).
- `G0-BOOT-02` — O script funciona em máquina limpa (sem variáveis secretas escondidas) (SIM/NÃO).
- `G0-BOOT-03` — Serviço backend sobe e escuta na porta esperada (SIM/NÃO).
- `G0-BOOT-04` — Banco e Object Store são inicializados ou mockados conforme plano (SIM/NÃO).
- `G0-BOOT-05` — README explica claramente como rodar o script, com exemplo de comando (SIM/NÃO).

### 3.6 Critério de PASS/FAIL

- **PASS**: todos os itens críticos (G0-BOOT-01…05) marcados como SIM; o time consegue subir e derrubar o ambiente pelo menos 3 vezes seguidas sem ajustes manuais.
- **FAIL**: qualquer item crítico NÃO. Em caso de FAIL, a Sprint 2 não avança para S2-G1; o Capítulo 3 deve ser ajustado para focar em corrigir o bootstrap.

---

## 4) Gate S2-G1 — Field Designer v0 & IEL Core OK

### 4.1 Objetivo do gate

Validar que o **Field Designer v0** está implementado em nível funcional e que a IEL foi traduzida de D9.2 para código de forma fiel, sem surpresas.

### 4.2 Escopo do gate

- Verifica **S2.1** em código.
- Confirma que:
  - schemas podem ser criados/atualizados/listados;
  - IEL é avaliada com operadores/funções mínimos definidos em D9.2;
  - erros são claros e LGPD é respeitada (sem acesso indevido a dados).

### 4.3 Entradas obrigatórias

- Gate S2-G0 em PASS.
- D9.2 (Field Designer + IEL) como doc de referência.

### 4.4 Saídas obrigatórias

- Implementação mínima do Field Designer:
  - entidades de schema/campos salvas no banco;
  - API ou CLI para criar/atualizar/listar schemas;
  - avaliador de IEL implementado com exemplos de computed fields funcionais.
- Conjunto de exemplos de IEL (pelo menos 2) testados manualmente ou via testes automatizados.
- `evidence_s2/s2_g1_field_designer_checklist.md` preenchido.

### 4.5 Checklist de evidência (exemplos de itens)

- `G1-FD-API-01` — É possível criar uma fonte com schema mínimo via API/CLI (SIM/NÃO).
- `G1-FD-API-02` — É possível atualizar um schema existente sem corromper dados (SIM/NÃO).
- `G1-FD-API-03` — É possível listar schemas e ver seus campos (SIM/NÃO).
- `G1-FD-IEL-01` — IEL aceita os operadores e funções core definidos em D9.2 (SIM/NÃO).
- `G1-FD-IEL-02` — Computed fields funcionam em pelo menos 2 exemplos distintos, com resultados esperados (SIM/NÃO).
- `G1-FD-IEL-03` — Erros de IEL são relatados com mensagem clara (SIM/NÃO).
- `G1-FD-LGPD-01` — IEL não acessa dados fora do escopo autorizado (sem cross‑item indevido) (SIM/NÃO).

### 4.6 Critério de PASS/FAIL

- **PASS**: Field Designer gera schemas utilizáveis para ingestão real; IEL executa casos básicos sem divergência observável da D9.2.
- **FAIL**: se a IEL divergir da spec (operadores ausentes, semântica diferente) ou se não for possível criar/usar schemas de forma confiável; registrar lessons e voltar a ajustar S2.1 antes de seguir.

---

## 5) Gate S2-G2 — Explore API v0 OK + Rate Limit ativo

### 5.1 Objetivo do gate

Garantir que a **Explore API v0** está disponível, responde conforme D9.3 e aplica rate limit v0 (120 req/min, burst 240) com comportamento previsível.

### 5.2 Escopo do gate

- Verifica **S2.2** e partes da observabilidade (contagem de requests, 429)].
- Confirma contrato de filtros, paginação e limites de uso.

### 5.3 Entradas obrigatórias

- Gates S2-G0 e S2-G1 em PASS.
- D9.3 (Explore API) como doc de referência.

### 5.4 Saídas obrigatórias

- Endpoints de leitura implementados e testáveis (curl/postman/scripts).
- Paginação implementada e documentada (determinística).
- Rate limit implementado com cabeçalhos X‑RateLimit‑* e resposta 429 com corpo razoável.
- `evidence_s2/s2_g2_explore_api_checklist.md` preenchido.

### 5.5 Checklist de evidência (exemplos de itens)

- `G2-EXP-API-01` — Endpoint principal de Explore responde 200 para consulta válida (SIM/NÃO).
- `G2-EXP-API-02` — Filtros básicos (igual, >, <, in) funcionam como esperado (SIM/NÃO).
- `G2-EXP-API-03` — Paginação é determinística (mesmas entradas → mesma saída) (SIM/NÃO).
- `G2-EXP-RL-01` — Rate limit é aplicado em 120 req/min, burst 240 (SIM/NÃO).
- `G2-EXP-RL-02` — Em excesso, resposta é 429 com cabeçalhos X‑RateLimit‑* e mensagem clara (SIM/NÃO).
- `G2-EXP-OBS-01` — Métricas de requests e 429 estão visíveis no endpoint de métricas (SIM/NÃO).

### 5.6 Critério de PASS/FAIL

- **PASS**: é possível executar um conjunto de consultas representativas, ver os efeitos do rate limit e confirmar o contrato de D9.3.
- **FAIL**: se a API não seguir a spec (ex.: filtros quebrados, paginação instável) ou se o rate limit estiver ausente/incoerente; sprint não avança para S2-G3 sem correção.

---

## 6) Gate S2-G3 — Evidence Vault v0 OK + LGPD mínimo

### 6.1 Objetivo do gate

Confirmar que o **Evidence Vault v0** está operacional e alinhado ao envelope de risco LGPD/ToS descrito em D9.4/D9.5.

### 6.2 Escopo do gate

- Verifica **S2.3** e os aspectos mínimos de LGPD.
- Confirma que evidências podem ser escritas, localizadas e associadas a fontes/consultas.

### 6.3 Entradas obrigatórias

- Gates S2-G0, S2-G1, S2-G2 em PASS.
- D9.4 (data model/DDL/migração) e D9.5 (LGPD/ToS).

### 6.4 Saídas obrigatórias

- Integração com Object Store (S3‑like) configurada (região, criptografia) e testada via pelo menos um cenário real.
- Metadados de evidências armazenados no banco e referenciáveis via chave/ID a partir de fontes ou consultas.
- `evidence_s2/s2_g3_evidence_vault_lgpd_checklist.md` preenchido.

### 6.5 Checklist de evidência (exemplos de itens)

- `G3-EV-01` — É possível gravar uma evidência no Vault a partir de uma operação de ingestão ou query (SIM/NÃO).
- `G3-EV-02` — É possível recuperar metadados da evidência (fonte, timestamp, hash, etc.) (SIM/NÃO).
- `G3-EV-03` — Hash ou identificador imutável da evidência está disponível para verificação (SIM/NÃO).
- `G3-LGPD-01` — Região e modo de criptografia são compatíveis com D9.5 (SIM/NÃO).
- `G3-LGPD-02` — Não há endpoints públicos expondo evidência em massa de forma indevida (SIM/NÃO).

### 6.6 Critério de PASS/FAIL

- **PASS**: Evidence Vault funciona em pelo menos um cenário real e obedece aos limites de LGPD/ToS.
- **FAIL**: se evidências não puderem ser gravadas/recuperadas ou se houver violação óbvia de envelope LGPD; nesse caso, a sprint deve ser pausada até mitigação.

---

## 7) Gate S2-G4 — Ingestão v0 OK (1–2 fontes) + Observabilidade básica

### 7.1 Objetivo do gate

Provar que o Inspectah v0 consegue ingerir dados de pelo menos 1–2 fontes e que há logs/métricas suficientes para enxergar o que está acontecendo.

### 7.2 Escopo do gate

- Verifica **S2.4** (pipeline de ingestão) e **S2.5** (observabilidade básica).
- Confirma que ingestão não é “mágica manual”, e sim fluxo claro e reprodutível.

### 7.3 Entradas obrigatórias

- Gates S2-G0…S2-G3 em PASS.

### 7.4 Saídas obrigatórias

- Scripts ou CLIs de ingestão funcionando para 1–2 fontes representativas (ou fixtures robustos).
- Logs estruturados emitidos nas principais operações (ingest, schema, query, evidence).
- Métricas básicas expostas em endpoint local.
- `evidence_s2/s2_g4_ingest_obs_checklist.md` preenchido.

### 7.5 Checklist de evidência (exemplos de itens)

- `G4-ING-01` — Script X ingere um dataset de exemplo sem falhas (SIM/NÃO).
- `G4-ING-02` — Dados ingeridos aparecem na Explore API com o schema correto (SIM/NÃO).
- `G4-LOG-01` — Logs incluem pelo menos fonte, operação, status e timestamp (SIM/NÃO).
- `G4-MET-01` — Métricas de ingestão (itens por fonte) estão visíveis (SIM/NÃO).
- `G4-MET-02` — Métricas de requests da Explore (incluindo 429) estão visíveis (SIM/NÃO).

### 7.6 Critério de PASS/FAIL

- **PASS**: é possível acompanhar o ciclo ingestão → armazenamento → consulta olhando logs/métricas.
- **FAIL**: se a ingestão depender de passos manuais não documentados ou se a observabilidade for insuficiente para diagnosticar problemas básicos.

---

## 8) Gate S2-G5 — E2E Script OK (Fluxo Completo) + Testes básicos

### 8.1 Objetivo do gate

Validar que o **script de E2E S2.6** realmente demonstra o fluxo completo e que há pelo menos uma suíte de testes automatizados rodando.

### 8.2 Escopo do gate

- Verifica **S2.6** e parte da disciplina de testes.
- Garante que o fluxo descrito nas personas (Capítulo 1) é exercitado de ponta a ponta.

### 8.3 Entradas obrigatórias

- Gates S2-G0…S2-G4 em PASS.
- S2.6 implementado.

### 8.4 Saídas obrigatórias

- Script `bin/run_inspectah_v0_e2e.sh` (ou equivalente) executando o fluxo completo em máquina limpa.
- Testes unitários/internos implementados e rodando em um comando (`cargo test`, `pytest`, etc.).
- `evidence_s2/s2_g5_e2e_tests_checklist.md` preenchido.

### 8.5 Checklist de evidência (exemplos de itens)

- `G5-E2E-01` — Script E2E sobe o ambiente do zero (SIM/NÃO).
- `G5-E2E-02` — Script E2E cria schema, ingere dados e consulta via Explore, sem intervenção manual (SIM/NÃO).
- `G5-E2E-03` — Script E2E verifica pelo menos uma evidência no Vault (SIM/NÃO).
- `G5-TEST-01` — Conjunto de testes unitários/internos roda com 0 falhas (SIM/NÃO).
- `G5-TEST-02` — Rodar os testes e o E2E em sequência é determinístico (sem flakiness) (SIM/NÃO).

### 8.6 Critério de PASS/FAIL

- **PASS**: E2E prova o fluxo, sem intervenção manual além do comando, e testes rodam verdes de forma estável.
- **FAIL**: se o E2E quebrar de forma não determinística ou depender de ajustes manuais; sprint não avança até estabilizar.

---

## 9) Gate S2-G6 — Docs operacionais v0 OK + Retro Sprint 2

### 9.1 Objetivo do gate

Garantir que a Sprint 2 terminou com documentação utilizável e memória institucional capturada, permitindo que outros times usem e evoluam o Inspectah v0.

### 9.2 Escopo do gate

- Verifica **S2.7** (docs operacionais) e o Capítulo 4 (retro & backlog).
- Amarra o fim da Sprint 2 com o planejamento das próximas sprints.

### 9.3 Entradas obrigatórias

- Gates S2-G0…S2-G5 em PASS.
- S2.7 implementado.

### 9.4 Saídas obrigatórias

- README operacional da Sprint 2/Inspectah v0 revisado e testado.
- Capítulo 4 da Sprint 2 preenchido (retrospectiva, lessons, ações S3+).
- `evidence_s2/s2_g6_docs_retro_checklist.md` preenchido.
- `evidence_s2/s2_summary_gate_matrix.json` atualizado com S2-G0…S2-G6 marcados como PASS/FAIL.

### 9.5 Checklist de evidência (exemplos de itens)

- `G6-DOC-01` — README permite que um engenheiro suba o ambiente e rode o E2E apenas seguindo o texto (SIM/NÃO).
- `G6-DOC-02` — Exemplos de chamadas à Explore API estão atualizados e funcionam (SIM/NÃO).
- `G6-RETRO-01` — Capítulo 4 contém retrospectiva preenchida, citando gates, sucessos e problemas reais (SIM/NÃO).
- `G6-BACKLOG-01` — Ações para Sprints 3+ estão registradas com IDs e tags (UI, fontes, performance, ORR, MBP) (SIM/NÃO).

### 9.6 Critério de PASS/FAIL

- **PASS**: documentação + retro permitem que outro time (não envolvido na Sprint 2) entenda o que foi feito, rode o v0 e tenha um caminho claro para evoluir.
- **FAIL**: se README estiver desatualizado, exemplos quebrarem ou se não houver retro/backlog; a sprint não deve ser declarada concluída.

---

## 10) Regras gerais e invariantes dos gates da Sprint 2

1. **Nenhum gate é simbólico**
   - Se não houver evidência escrita, o gate está PENDING ou FAIL, nunca PASS.

2. **Nenhum S2.x é “done” sem gate associado**
   - S2.0 sem S2-G0 em PASS não é considerado pronto; idem para os demais S2.x.

3. **Gates não podem ser “afrouxados” sem patch**
   - Qualquer mudança nos critérios ou checklists deve ser registrada como lesson + ação (`PATCH_S2_GATES` ou `PATCH_DNA`) e documentada em Capítulo 4.

4. **Flakiness é FAIL, não WARN**
   - Se scripts ou testes passarem de forma intermitente, o gate é FAIL até estabilizar.

5. **Lessons obrigatórias**
   - Todo FAIL de gate deve gerar ao menos uma entrada em `d9_lessons_log_raw.md` ou no equivalente da Sprint 2 + uma ação em backlog.

Com este capítulo, a Sprint 2 deixa de ser uma lista de desejos e passa a ter um conjunto de checkpoints objetivos, mecânicos e auditáveis. O Capítulo 3 (plano de execução) usará estes gates como trilho para organizar threads e prioridades da implementação.

