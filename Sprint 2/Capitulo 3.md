# Inspectah — Sprint 2
## Capítulo 3 — Plano de Execução, Threads e Orquestração dos Gates v0 (Core Data Hub) — v2.0

> Este capítulo responde à pergunta: **“Como executar, na prática, a Sprint 2 do Inspectah até todos os gates S2-G0…S2-G6 estarem em PASS?”**
>
> Capítulo 1 diz *o que* entregar. Capítulo 2 diz *como provar*. Este Capítulo 3 diz **como chegar lá**, passo a passo, com threads claras, donos implícitos e artefatos explícitos — pensado para humanos e para o Codex.

---

## 0) Modo de uso (humano + Codex)

Antes de começar qualquer trabalho da Sprint 2:

1. **Leia na ordem**:
   - Capítulo 1 (contexto, S2.x, personas, invariantes);
   - Capítulo 2 (gates S2-G0…S2-G6, checklists, matriz);
   - Este Capítulo 3 (threads T0…T6 e plano de execução).

2. **Se você é o Codex**:
   - Você **não altera** os capítulos 1 e 2; eles são contrato.
   - Você usa este Capítulo 3 como **roteiro de trabalho**: escolha a thread, siga os passos, gere código/scripts/tests, preencha evidências.
   - Sempre que completar um passo relevante, atualize:
     - o checklist correspondente em `evidence_s2/…`;
     - a matriz `evidence_s2/s2_summary_gate_matrix.json` (se um gate mudou de status);
     - o Capítulo 4 com lessons/ações (quando houver desvios ou dificuldades).

3. **Se você é humano**:
   - Use este capítulo para coordenar a sprint: priorizar threads, revisar entregas, identificar bloqueios e cobrar evidências concretas.
   - Nenhuma task entra no quadro se não estiver ligada a uma linha deste Capítulo 3, a um S2.x e a um gate.

Regra de ouro: **toda ação da Sprint 2 deve apontar para (S2.x, Gate, Thread, Checklist)**. Se não souber preencher esses quatro campos, a ação está mal definida.

---

## 1) Mapa S2.x ↔ Gates ↔ Threads

Tabela de rastreabilidade da Sprint 2:

- **S2.0 — Infraestrutura base & scaffolding**
  - Gate principal: **S2-G0** (Bootstrap & Ambiente Dev OK)
  - Thread dona: **T0**

- **S2.1 — Field Designer v0 (engine + API/CLI + IEL core)**
  - Gate principal: **S2-G1** (Field Designer v0 & IEL Core OK)
  - Thread dona: **T1**

- **S2.2 — Explore API v0**
  - Gate principal: **S2-G2** (Explore API v0 OK + Rate Limit ativo)
  - Thread dona: **T2**

- **S2.3 — Evidence Vault v0**
  - Gate principal: **S2-G3** (Evidence Vault v0 OK + LGPD mínimo)
  - Thread dona: **T3**

- **S2.4 — Pipeline de ingestão mínima (1–2 fontes)**
  - Gate principal: **S2-G4** (Ingestão v0 OK + Observabilidade básica)
  - Thread dona: **T4**

- **S2.5 — Observabilidade básica v0**
  - Gate principal: **S2-G4** (Ingestão v0 OK + Observabilidade básica)
  - Thread dona: **T4**

- **S2.6 — Testes & E2E local (script único)**
  - Gate principal: **S2-G5** (E2E Script OK + Testes básicos)
  - Thread dona: **T5**

- **S2.7 — Documentação operacional v0**
  - Gate principal: **S2-G6** (Docs operacionais v0 OK + Retro Sprint 2)
  - Thread dona: **T6**

Visualmente: **T0…T6 são as "rodovias" que levam cada S2.x até o seu gate em PASS.**

---

## 2) Loop padrão de trabalho por thread

Independentemente da thread (T0…T6), o ciclo de trabalho segue sempre o mesmo padrão:

1. **Ler & ancorar**  
   Ler as seções relevantes de:
   - Capítulo 1 (S2.x correspondente);
   - Capítulo 2 (gate correspondente);
   - D9.* aplicáveis (especialmente D9.2–D9.5);
   - Bloco 3 (filemap) quando a thread mexer em estrutura.

2. **Planejar o mini‑escopo local**  
   Escrever, em comentário ou doc curto, o que exatamente será feito no ciclo atual:
   - funções/módulos a criar ou alterar;
   - scripts;  
   - fixtures/datasets;  
   - testes e evidências.

3. **Implementar a menor unidade coerente**  
   Escrever código/scripts/testes para cumprir esse mini‑escopo sem espalhar mudanças desnecessárias.

4. **Verificar imediatamente**  
   Rodar comandos mínimos:
   - testes unitários específicos;  
   - scripts de smoke/mini‑E2E;  
   - inspeção de logs/métricas (quando aplicável).

5. **Registrar evidência**  
   Atualizar o checklist da thread (por exemplo `s2_g2_explore_api_checklist.md`) marcando itens SIM/NÃO e incluindo links para:
   - comandos usados;  
   - logs ou prints;  
   - PRs ou commits.

6. **Abrir lessons/backlog se necessário**  
   Se algo travar (limitação de lib, infra, tempo, etc.), registrar no Capítulo 4:
   - lesson bruta (o que aconteceu);
   - ação com ID (ex.: `S2-EXP-001`), tipo (`PATCH_S2`, `BACKLOG_S3+`) e dono.

Este loop se repete até todos os itens relevantes de checklist para aquela thread estarem em SIM, e o gate correspondente puder ser marcado como PASS.

---

## 3) T0 — Scaffolding & Ambiente Dev (S2.0 / S2-G0)

### 3.1 Objetivo da thread

Colocar em pé o **esqueleto do repositório do Inspectah v0**, alinhado ao filemap do Bloco 3, com um comando único para subir o ambiente de desenvolvimento. T0 destrava todas as outras threads.

### 3.2 Entradas obrigatórias

- Capítulo 1 (S2.0 contexto e escopo).  
- Capítulo 2 (gate S2-G0).  
- D9.0, D9.4, D9.6, D9.8.  
- Filemap do Bloco 3 (estrutura desejada de pastas).

### 3.3 Entregáveis concretos

- Estrutura inicial do repo Inspectah v0 (pastas de serviço, config, scripts, tests).  
- Script para subir o ambiente local, por exemplo `bin/dev_up.sh` (e `docker-compose.yml`, se aplicável).  
- README inicial com instruções para rodar o bootstrap.  
- Checklist `evidence_s2/s2_g0_bootstrap_checklist.md` preenchido.  
- Entrada S2-G0 na `s2_summary_gate_matrix.json` com `status = PASS`.

### 3.4 Plano de execução da thread (para Codex)

1. Criar ou ajustar a estrutura de pastas do repo conforme Bloco 3 (mínimo: `services/`, `configs/`, `scripts/`, `bin/`, `tests/`).  
2. Implementar `bin/dev_up.sh` com, no mínimo:
   - inicialização de banco (ex.: container local ou processo em background);  
   - inicialização de Object Store local/mocked (se não houver, simular com filesystem local);
   - start do serviço backend do Inspectah com healthcheck simples.
3. (Opcional mas recomendado) Implementar `bin/dev_down.sh` para derrubar ambiente de forma limpa.  
4. Criar/atualizar README com:
   - pré‑requisitos;  
   - comando(s) exatos para subir e derrubar;  
   - exemplo de saída esperada.
5. Rodar `bin/dev_up.sh` e `bin/dev_down.sh` em máquina limpa (repositório fresh + dependências mínimas) pelo menos 3 vezes.  
6. Preencher `s2_g0_bootstrap_checklist.md` com SIM/NÃO (itens G0‑BOOT‑01…05) e descrever brevemente o ambiente usado.  
7. Atualizar `s2_summary_gate_matrix.json` marcando S2-G0 como PASS (se todos itens críticos estiverem em SIM).

### 3.5 Critério de conclusão da thread

- Todos os itens críticos de G0 marcados como SIM.  
- Ambiente de dev sobe de forma reprodutível em máquina limpa, sem tweaks manuais.  
- Outras threads conseguem partir de `bin/dev_up.sh` como ponto de entrada único.

---

## 4) T1 — Field Designer v0 & IEL Core (S2.1 / S2-G1)

### 4.1 Objetivo da thread

Implementar o **Field Designer v0** e a **Inspectah Expression Language (IEL)** em nível funcional, permitindo criar/atualizar/listar schemas e aplicar computed fields simples, em alinhamento com D9.2.

### 4.2 Entradas obrigatórias

- T0 concluída (S2-G0 = PASS).  
- Capítulo 1 (S2.1).  
- Capítulo 2 (gate S2-G1).  
- D9.2 (Field Designer + IEL) como spec central.

### 4.3 Entregáveis concretos

- Código do Field Designer v0 (entidades de schema/campos, camada de persistência).  
- API/CLI para criar, atualizar e listar schemas.  
- Implementação da IEL core (avaliador com operadores/funções mínimas).  
- Pelo menos 2 exemplos de computed fields testados end‑to‑end.  
- Checklist `evidence_s2/s2_g1_field_designer_checklist.md` preenchido.  
- S2-G1 = PASS na `s2_summary_gate_matrix.json`.

### 4.4 Plano de execução da thread (para Codex)

1. Mapear, a partir de D9.2, o conjunto mínimo de operadores/funções IEL para o v0.  
2. Modelar entidades do Field Designer:
   - Fonte, Schema, Campo, Tipo, Transform, ComputedField;
   - constraints mínimas (unicidade, obrigatoriedade, etc.).
3. Implementar camada de persistência (tabelas/coleções) conforme D9.4.  
4. Implementar API/CLI de Field Designer para:
   - criar schema;  
   - atualizar schema;  
   - listar schemas/fields;  
   - validar entradas (tipos, nomes, IEL sintaticamente válida).
5. Implementar avaliador IEL core:
   - escopo: apenas dados da mesma linha/item;  
   - sem I/O nem efeitos colaterais;  
   - erros com mensagens claras e estáveis.
6. Criar dois schemas de exemplo com computed fields (ex.: preço normalizado, flag booleana) e testar:
   - via testes unitários;  
   - via um pequeno script que simula ingestão+avaliação.
7. Preencher `s2_g1_field_designer_checklist.md` com SIM/NÃO (G1‑FD‑API‑01… G1‑FD‑LGPD‑01), colando trechos de comando/output relevantes em "Notas".  
8. Atualizar `s2_summary_gate_matrix.json` com S2-G1 = PASS se checklist completo.

### 4.5 Critério de conclusão da thread

- É possível criar e usar um schema real via API/CLI, com IEL funcionando.  
- Computed fields produzem resultados consistentes com D9.2.  
- Nenhuma outra thread precisa reabrir discussão sobre semântica core da IEL.

---

## 5) T2 — Explore API v0 & Rate Limit (S2.2 / S2-G2)

### 5.1 Objetivo da thread

Implementar a **Explore API v0**, com filtros, paginação determinística e rate limit v0 (120 req/min, burst 240), conforme D9.3, produzindo um endpoint utilizável pelo MBP e por scripts externos.

### 5.2 Entradas obrigatórias

- T0 concluída (S2-G0 = PASS).  
- T1 com schemas mínimos disponíveis.  
- Capítulo 1 (S2.2).  
- Capítulo 2 (gate S2-G2).  
- D9.3 (Explore API) como spec central.

### 5.3 Entregáveis concretos

- Endpoints de leitura da Explore API v0.  
- Implementação de filtros básicos (igual, >, <, in).  
- Paginação determinística (limit/offset ou cursor).  
- Rate limit v0 implementado com cabeçalhos X‑RateLimit‑* e resposta 429.  
- Exemplos de chamadas (curl/Postman/scripts).  
- Checklist `evidence_s2/s2_g2_explore_api_checklist.md`.  
- S2-G2 = PASS na `s2_summary_gate_matrix.json`.

### 5.4 Plano de execução da thread (para Codex)

1. Definir rotas da Explore API v0 (paths, métodos HTTP, parâmetros) a partir de D9.3.  
2. Implementar camada de query:
   - filtro por fonte;  
   - filtro temporal (quando aplicável);  
   - filtros por campos tipados.
3. Implementar paginação determinística:
   - escolha de chave de ordenação estável;  
   - payload com informações de página/cursor.
4. Implementar rate limit v0:
   - contador por chave (IP, token ou outro identificado definido);  
   - 120 req/min com burst 240;  
   - 429 com corpo e cabeçalhos X‑RateLimit‑* documentados.
5. Criar scripts de teste (ex.: pequeno load local) para validar rate limit e comportamento normal.  
6. Expor métricas de requests (incluindo 429) em endpoint de métricas.  
7. Preencher `s2_g2_explore_api_checklist.md` com SIM/NÃO (G2‑EXP‑API‑01… G2‑EXP‑OBS‑01).  
8. Atualizar `s2_summary_gate_matrix.json` com S2-G2 = PASS se checklist completo.

### 5.5 Critério de conclusão da thread

- Explore API responde consultas típicas com 200, filtros corretos e paginação estável.  
- Rate limit se comporta conforme contrato.  
- Métricas de uso/limite estão visíveis e coerentes.

---

## 6) T3 — Evidence Vault v0 & LGPD mínimo (S2.3 / S2-G3)

### 6.1 Objetivo da thread

Colocar em operação o **Evidence Vault v0**, com integração a Object Store (S3‑like) e metadados em banco, respeitando as restrições de LGPD/ToS de D9.4/D9.5.

### 6.2 Entradas obrigatórias

- T0 concluída (S2-G0 = PASS).  
- T1/T2 já fornecendo entidades e queries básicas.  
- Capítulo 1 (S2.3).  
- Capítulo 2 (gate S2-G3).  
- D9.4 e D9.5.

### 6.3 Entregáveis concretos

- Configuração do Evidence Vault v0 (Object Store, região, criptografia).  
- APIs internas para gravar e recuperar evidências.  
- Persistência de metadados de evidência ligados a fontes/itens/eventos.  
- Pelo menos um fluxo real que grava e consulta uma evidência.  
- Checklist `evidence_s2/s2_g3_evidence_vault_lgpd_checklist.md`.  
- S2-G3 = PASS na `s2_summary_gate_matrix.json`.

### 6.4 Plano de execução da thread (para Codex)

1. Configurar cliente de Object Store local/mocked seguindo parâmetros de D9.4/D9.5 (região, SSE‑KMS ou similar).  
2. Definir modelo de metadados de evidência (tabela/coleção) conforme D9.4.  
3. Implementar funções para:
   - gravar evidência (upload + registro de metadados);  
   - consultar metadados;  
   - (opcional) baixar payload para verificações pontuais.
4. Integrar gravação de evidência a pelo menos uma operação do sistema (ex.: ingestão de fonte X ou execução de consulta crítica Y).  
5. Validar via teste/script:
   - gravação de arquivo;  
   - leitura de metadados;  
   - conferência de hash/ID imutável.
6. Auditar endpoints/rotas para garantir que não existe exposição indevida de dados do Vault.  
7. Preencher `s2_g3_evidence_vault_lgpd_checklist.md` com SIM/NÃO (G3‑EV‑01… G3‑LGPD‑02).  
8. Atualizar `s2_summary_gate_matrix.json` com S2-G3 = PASS se checklist completo.

### 6.5 Critério de conclusão da thread

- Evidence Vault grava e referencia evidências em fluxo real.  
- Configuração de região/criptografia aderente a D9.5.  
- Não há endpoints de exposição massiva de evidências.

---

## 7) T4 — Ingestão v0 (1–2 fontes) & Observabilidade básica (S2.4 + S2.5 / S2-G4)

### 7.1 Objetivo da thread

Demonstrar que o Inspectah v0 consegue **ingerir dados de 1–2 fontes reais ou representativas** e que é possível acompanhar esse fluxo por logs e métricas.

### 7.2 Entradas obrigatórias

- T0…T3 com gates G0–G3 em PASS.  
- Capítulo 1 (S2.4, S2.5).  
- Capítulo 2 (gate S2-G4).

### 7.3 Entregáveis concretos

- Scripts/CLIs de ingestão para 1–2 fontes (ou fixtures robustos).  
- Logs estruturados nas principais operações (ingest, schema, query, evidence).  
- Métricas básicas de ingestão e requests da Explore.  
- Checklist `evidence_s2/s2_g4_ingest_obs_checklist.md`.  
- S2-G4 = PASS na `s2_summary_gate_matrix.json`.

### 7.4 Plano de execução da thread (para Codex)

1. Selecionar 1–2 fontes/fixtures representativas do v0.  
2. Para cada fonte:
   - registrar a fonte via Field Designer (T1);  
   - definir schema + computed fields úteis;  
   - implementar script/CLI que lê dados brutos (arquivo/API) e escreve no DB do Inspectah.
3. Tornar ingestão reexecutável (idempotência ou estratégia de truncamento/versão).  
4. Implementar logs estruturados:
   - chave mínima: fonte, operação, status, timestamp;  
   - incluir contexto suficiente para debugar falhas.
5. Implementar métricas:
   - itens ingeridos por fonte;  
   - erros de ingestão;  
   - contagem de requests/429 na Explore.
6. Rodar scripts de ingestão e, em seguida, consultas na Explore para verificar que dados apareceram corretamente.  
7. Inspecionar logs e métricas para garantir visibilidade do fluxo.  
8. Preencher `s2_g4_ingest_obs_checklist.md` com SIM/NÃO (G4‑ING‑01… G4‑MET‑02).  
9. Atualizar `s2_summary_gate_matrix.json` com S2-G4 = PASS se checklist completo.

### 7.5 Critério de conclusão da thread

- Pelo menos uma fonte de exemplo ingerida e visível via Explore API.  
- Logs e métricas suficientes para depurar falhas básicas de ingestão/consulta.

---

## 8) T5 — Testes & Script E2E (S2.6 / S2-G5)

### 8.1 Objetivo da thread

Garantir que existe um **script de E2E** que prova o fluxo completo e uma **suíte mínima de testes automatizados** cobrindo componentes críticos (Field Designer, Explore, Evidence, ingestão).

### 8.2 Entradas obrigatórias

- T0…T4 com gates G0–G4 em PASS.  
- Capítulo 1 (S2.6).  
- Capítulo 2 (gate S2-G5).

### 8.3 Entregáveis concretos

- Script E2E (por exemplo `bin/run_inspectah_v0_e2e.sh`).  
- Suíte mínima de testes unitários/internos.  
- Checklist `evidence_s2/s2_g5_e2e_tests_checklist.md`.  
- S2-G5 = PASS na `s2_summary_gate_matrix.json`.

### 8.4 Plano de execução da thread (para Codex)

1. Definir o fluxo E2E, espelhando as personas do Capítulo 1:
   - subir ambiente;  
   - criar schema via Field Designer;  
   - ingerir dados;  
   - consultar via Explore;  
   - verificar evidência no Vault.
2. Implementar `bin/run_inspectah_v0_e2e.sh` para executar esse fluxo em máquina limpa, aceitando apenas o mínimo de parâmetros/configs.  
3. Implementar testes unitários/internos para:
   - IEL (casos positivos e de erro);  
   - validação de schema;  
   - ingestão de pequena amostra;  
   - consultas simples na Explore.
4. Criar um wrapper de testes local (ex.: `bin/run_inspectah_tests.sh`) que rode testes unitários e, opcionalmente, o E2E.  
5. Executar testes+E2E múltiplas vezes para verificar determinismo (sem flakiness).  
6. Preencher `s2_g5_e2e_tests_checklist.md` com SIM/NÃO (G5‑E2E‑01… G5‑TEST‑02).  
7. Atualizar `s2_summary_gate_matrix.json` com S2-G5 = PASS se checklist completo.

### 8.5 Critério de conclusão da thread

- Script E2E roda do zero sem intervenção manual além do comando.  
- Testes unitários/internos rodam verdes de forma consistente.  
- Rodar testes+E2E em sequência é estável (sem flakiness).

---

## 9) T6 — Docs operacionais & Retro Sprint 2 (S2.7 / S2-G6)

### 9.1 Objetivo da thread

Concluir a Sprint 2 com **documentação operacional utilizável** e uma **retrospectiva honesta**, que alimenta o backlog das próximas sprints.

### 9.2 Entradas obrigatórias

- T0…T5 com gates G0–G5 em PASS.  
- Capítulo 1 (S2.7).  
- Capítulo 2 (gate S2-G6).

### 9.3 Entregáveis concretos

- README operacional final da Sprint 2/Inspectah v0.  
- Capítulo 4 preenchido com lessons, problemas, decisões e ações S3+.  
- Checklist `evidence_s2/s2_g6_docs_retro_checklist.md`.  
- S2-G6 = PASS na `s2_summary_gate_matrix.json`.

### 9.4 Plano de execução da thread (para Codex + humano)

1. Revisar todos os artefatos gerados (código, scripts, checklists, matriz, logs).  
2. Atualizar README operacional para refletir **como o sistema realmente funciona hoje**:
   - dependências reais;  
   - comandos definitivos para subir ambiente, rodar testes e E2E;
   - exemplos de chamadas à Explore API com payloads reais;  
   - explicação clara do que é v0 e o que fica para v0.1/v1.
3. Redigir Capítulo 4 (retro):
   - listar sucessos, dores, surpresas;  
   - para cada FAIL de gate, registrar lesson e ação (`S2-EXP-001`, `PATCH_S2_GATES`, `BACKLOG_S3+`, etc.);
   - classificar ações por tema (UI, fontes, performance, ORR, MBP).
4. Preencher `s2_g6_docs_retro_checklist.md` com SIM/NÃO (G6‑DOC‑01… G6‑BACKLOG‑01).  
5. Atualizar `s2_summary_gate_matrix.json` com S2-G6 = PASS se checklist completo.  
6. Validar que todos os gates S2-G0…S2-G6 estão em PASS e que não há checklists vazios.

### 9.5 Critério de conclusão da thread

- Um engenheiro externo consegue rodar o Inspectah v0 seguindo apenas o README.  
- Capítulo 4 documenta claramente o estado final da Sprint 2 e o plano para S3+.  
- Matriz de gates mostra todos S2-G0…S2-G6 em PASS, com evidências rastreáveis.

---

## 10) Orquestração geral: ordem, paralelismo e gestão de risco

### 10.1 Ordem mínima recomendada

1. **T0** — Scaffolding & Ambiente Dev.
2. **T1** — Field Designer & IEL.
3. **T2** — Explore API.
4. **T3** — Evidence Vault.
5. **T4** — Ingestão & Observabilidade.
6. **T5** — Testes & E2E.
7. **T6** — Docs & Retro.

### 10.2 Paralelismo seguro

- T0 deve ser concluída primeiro.
- T1 e T2 podem rodar em paralelo após T0, coordenando o modelo de dados.  
- T3 pode ser iniciada quando T1/T2 tiverem caminho de dados mínimo.  
- T4 depende funcionalmente de T1–T3, mas scripts podem ser esboçados antes.  
- T5 pode começar testes de unidades (IEL, validação) cedo, mas E2E final exige G0–G4 em PASS.  
- T6 acompanha desde o início (anotando decisões), mas fecha apenas quando todos gates estiverem em PASS.

### 10.3 Gestão de risco e uso de lessons

- TODO FAIL de gate gera entrada obrigatória de lesson + ação em Capítulo 4.
- Se um gate travar a sprint (ex.: G2 por causa de rate limit):
  - criar ação específica (ex.: `S2-EXP-002 — ajustar bucket de rate limit`);
  - pausar abertura de novas tasks não essenciais;  
  - focar a thread responsável até o gate sair de FAIL.
- Mudanças no sistema de gates (Capítulo 2) ou neste plano (Capítulo 3) exigem:
  - registro explícito em Capítulo 4 (`PATCH_S2_GATES` ou similar);
  - atualização de checklists/matriz mantendo rastreabilidade.

---

## 11) Encerramento da Sprint 2

A Sprint 2 só pode ser considerada concluída quando:

1. Todas as threads T0…T6 cumprirem seus critérios de conclusão.  
2. Todos os gates S2-G0…S2-G6 estiverem em PASS, com checklists completos e `s2_summary_gate_matrix.json` atualizado.  
3. O script E2E provar o fluxo completo em máquina limpa, sem intervenção manual (além da configuração mínima documentada).  
4. README + Capítulo 4 permitirem que qualquer novo time entenda o estado atual do Inspectah v0 e saiba exatamente o que falta para v0.1/v1.

Com isso, a Sprint 2 entrega não apenas código, mas um **núcleo de Data Hub operável, verificável e evolutivo**, pronto para receber as próximas ondas do Sprint Macro (UI‑min, FTS+bench, 10–15 fontes, ORR completo e integração profunda com o MBP).

