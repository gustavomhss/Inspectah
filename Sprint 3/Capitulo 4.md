# Inspectah — Capítulo 4 v2
## Playbook do Codex & Fluxo de Execução da Sprint (Driven by Gates T0–T8, Versão 15/10)

---

### 0. TL;DR

Capítulo 1 define **o que** é o Inspectah.  
Capítulo 2 v3 define **quando** a máquina está saudável (Gates T0–T8, linha dura 15/10).  
Capítulo 3 v2 define **onde** tudo mora (filemap, scripts, scorecards, evidências).

Capítulo 4 v2 responde: **“Como o Codex e o time executam, no dia a dia, esse plano?”**

O objetivo é ser um **manual operacional** simples, repetível e sem improviso:

- dizer **em que ordem agir**;  
- como transformar demandas em tarefas ligadas a Gates;  
- como acionar o Codex com superprompts bem formados;  
- como validar, depurar e decidir Go/No‑Go usando sempre a linguagem dos Gates.

Princípio central:

> Se não encaixa em Gate, não entra na sprint.  
> Se quebra Gate crítico, não está pronto.  
> Se não grava evidência em `out/`, “não aconteceu” para o Inspectah.

---

### 1. Roteiro rápido (1 página) — Como trabalhar no Inspectah

Este é o roteiro diário simplificado, em 10 passos. Tudo mais detalhado no restante do capítulo aprofunda esses passos.

1. [OBRIGATÓRIO] **Escolha o Gate:** toda tarefa precisa declarar em quais Gates T0–T8 opera (principal e secundários).  
2. [OBRIGATÓRIO] **Mapeie arquivos:** use o Cap.3 para listar quais arquivos/pastas serão tocados (código, configs, scripts, scorecards).  
3. [OBRIGATÓRIO] **Defina resultado esperado:** descreva, em linguagem de Gates, o que deve estar verdadeiro quando a tarefa estiver pronta (ex.: “T5_performance.json continua PASS com p95 ≤ 200 ms”).  
4. [OBRIGATÓRIO] **Monte o superprompt:** pegue um template da Seção 6, preencha contexto, Gate(s), arquivos e restrições e só então acione o Codex.  
5. [OBRIGATÓRIO] **Executar em pequenos passos:** o Codex aplica mudanças focadas, mantendo o filemap do Cap.3 e sem alterar Cap.1–3 ou thresholds de Gates.  
6. [OBRIGATÓRIO] **Rodar os Gates afetados localmente:** executar `bin/orr_tX_*` relevantes e/ou `bin/orr_all.sh`, inspecionando os `T*_*.json` e `out/evidence/TX_*`.  
7. [OBRIGATÓRIO] **Garantir que Gates não relacionados não regrediram:** se a mudança não deveria afetar T3/T4/T5/T5.1/T7, eles precisam continuar PASS.  
8. [OBRIGATÓRIO] **Subir para CI/ORR:** abrir PR/branch e garantir que `.ci/orr_pipeline.yml` rode com sucesso, atualizando `T7_orr.json`.  
9. [OBRIGATÓRIO] **Checar foto de simultaneidade:** após a mudança, precisa existir pelo menos uma execução recente de ORR em CI com todos os Gates relevantes verdes simultaneamente (T0–T7).  
10. [RECOMENDADO] **Documentar em humano:** anotar no PR ou em doc leve qual Gate foi reforçado, quais scorecards mudaram e se houve impacto em métricas de confiança.

Se esses 10 passos forem seguidos, Cap.1–3 deixam de ser teoria e viram rotina concreta.

---

### 2. Papéis e responsabilidades no fluxo do Inspectah

Para efeitos deste playbook, consideramos quatro papéis:

1. **Product Owner (PO)**  
   Define objetivos da sprint, prioriza problemas e garante que cada tarefa aponte para Gates claros. Não escreve código nem mexe em Cap.1–3 diretamente.

2. **Planner (especificador)**  
   Lê Cap.1–3, refina os objetivos em tarefas e superprompts. Amarra cada tarefa a Gates, arquivos e expectativas de scorecards. Seu produto principal é o superprompt para o Codex.

3. **Codex (engenheiro executor)**  
   Atua dentro do repositório `inspectah/` seguindo Cap.2 (Gates), Cap.3 (filemap) e os superprompts do Planner. Cria/edita código, configs, scripts, migrações e garante que os Gates continuem verdes.

4. **CI/ORR + Operadores**  
   CI executa `.ci/orr_pipeline.yml` e scripts `bin/orr_tX_*`, produzindo scorecards e evidências em `out/`. Operadores usam o Inspectah e alimentam T8 com métricas reais e feedback.

Capítulo 4 v2 se concentra especialmente na interação Planner ↔ Codex ↔ CI.

---

### 3. Fluxo macro da sprint (do objetivo ao Go/No‑Go)

Visão end‑to‑end:

1. **Planejamento (PO + Planner)**  
   - PO define objetivos da sprint com base no blueprint e no estado atual dos Gates.  
   - Planner traduz em épicos/tarefas, cada uma com Gate(s) alvo(s) e artefatos de Cap.3.

2. **Especificação (Cap.1–3 first)**  
   - Planner lê Cap.1–3;  
   - escreve a mini‑spec da tarefa (Gate, arquivos, métricas/scorecards, riscos);  
   - prepara o superprompt (Seção 6).

3. **Execução (Codex)**  
   - Codex usa o superprompt, respeita filemap e contratos dos Gates;  
   - aplica mudanças em pequenos blocos.

4. **Validação local (Gates relevantes)**  
   - rodar `bin/orr_tX_*` dos Gates tocados;  
   - se necessário, `bin/orr_all.sh`;  
   - ajustar até os Gates visados estarem PASS sem quebrar outros.

5. **CI/ORR**  
   - enviar branch/PR;  
   - `.ci/orr_pipeline.yml` executa os Gates, atualiza scorecards T0–T7.

6. **Regra de simultaneidade (Lamport)**  
   - versão só é elegível para release se existir pelo menos uma execução recente (ex.: últimos 7 dias) de ORR em CI em que **todos os Gates T0–T7 relevantes estejam simultaneamente PASS**.

7. **T8 e decisão**  
   - em uso interno, T8 reúne métricas reais e feedback de operadores;  
   - se T8 for PASS, com T0–T7 também PASS na mesma foto, versão pode ser declarada Go.

---

### 4. Pré e pós-condições de trabalho (Meyer‑style)

Capítulo 4 define condições claras para iniciar e concluir tarefas.

#### 4.1 Pré-condições — Quando uma tarefa pode ser iniciada

Uma tarefa **só pode ser iniciada** se TODAS as condições abaixo forem verdadeiras:

1. [OBRIGATÓRIO] Pelo menos um **Gate T0–T8** está explicitamente declarado como alvo principal da tarefa.  
2. [OBRIGATÓRIO] Os **arquivos e pastas relevantes** foram apontados com base no Cap.3 (caminhos em `docs/`, `schema/`, `configs/`, `src/`, `ops/`, `bin/`, `out/`).  
3. [OBRIGATÓRIO] O **impacto esperado em Gates** está descrito: quais Gates devem ficar PASS no final, quais não podem piorar.  
4. [OBRIGATÓRIO] Existe pelo menos um **scorecard T*_*.json** correspondente ao Gate alvo, ou uma tarefa irmã para criá‑lo antes.  
5. [OBRIGATÓRIO] Se a tarefa mexe em thresholds ou semântica de Gates, um plano para atualizar Cap.2/Cap.3 foi explicitamente criado e aprovado (essas mudanças nunca são “ocultas” em código).  
6. [OBRIGATÓRIO] Um superprompt inicial (Seção 6) foi esboçado com contexto suficiente para o Codex.

Se qualquer item for “não sei” ou “depois a gente vê”, a tarefa está mal definida e não deve começar.

#### 4.2 Pós-condições — Quando uma tarefa é considerada concluída

Uma tarefa **só pode ser concluída** quando TODAS as condições abaixo forem verdadeiras:

1. [OBRIGATÓRIO] Os scripts `bin/orr_tX_*` dos Gates alvo foram executados localmente, com `status=PASS` nos scorecards correspondentes.  
2. [OBRIGATÓRIO] Nenhum Gate que não deveria ser afetado (especialmente T3, T4, T5, T5.1, T7) ficou em FAIL após a mudança.  
3. [OBRIGATÓRIO] Existe pelo menos uma execução recente de ORR em CI pós‑mudança com todos os Gates relevantes simultaneamente PASS (T0–T7).  
4. [OBRIGATÓRIO] As evidências e scorecards em `out/evidence/TX_*/` e `out/scorecards/TX_*.json` foram atualizados e refletem o novo estado.  
5. [OBRIGATÓRIO] O PR ou a nota da tarefa menciona explicitamente quais Gates foram reforçados e quais scorecards foram usados para validar.  
6. [OBRIGATÓRIO] No caso de tarefas que tocam em confiança (`confidence_score` e `confidence_profile_id`), está claro que os dados de base para calibração futura (T5.2) continuam íntegros.

Se qualquer item falhar, o estado é “em andamento” ou “regressão”, nunca “concluído”.

---

### 5. Catálogo de tipos de tarefa → Gates e scripts

Para reduzir ambiguidade, este catálogo liga tipos comuns de tarefa a Gates e scripts de ORR.

#### 5.1 Nova Fonte + watcher

- Descrição: adicionar suporte a um novo site/app/API/RSS.  
- Gates principais: **T2, T3, T4**, possivelmente T5.  
- Scripts mínimos: `bin/orr_t2_field_designer_smoke.sh`, `bin/orr_t3_pipeline_invariants.sh`, `bin/orr_t4_evidence_audit.sh`, opcionalmente `bin/orr_t5_performance_gate.sh`.

#### 5.2 Ajuste no Confidence Engine

- Descrição: alterar heurísticas, features ou combinadores que geram `confidence_score`.  
- Gates principais: **T5.1** (e, no futuro, T5.2).  
- Scripts mínimos: `bin/orr_t5_1_confidence_gate.sh`.  
- Classificação: **High risk** (impacta confiança e integrações externas).

#### 5.3 Refactor de watcher ou pipeline

- Descrição: reorganizar código de ingestão, dedup, backfill, sem mudar comportamento funcional (idealmente).  
- Gates principais: **T3, T4**, e T5 se latência for tocada.  
- Scripts mínimos: `bin/orr_t3_pipeline_invariants.sh`, `bin/orr_t4_evidence_audit.sh`, `bin/orr_t5_performance_gate.sh` se houver alteração em caminhos de ingest.

#### 5.4 Mudança de schema ou DDL

- Descrição: adicionar/alterar/remover colunas/tabelas relacionadas a Fonte, Observação, Item, Sinal, confiança.  
- Gates principais: **T1, T2, T3**, possivelmente T4.  
- Scripts mínimos: `bin/orr_t1_schema_check.sh`, `bin/orr_t2_field_designer_smoke.sh`, `bin/orr_t3_pipeline_invariants.sh`.

#### 5.5 Ajustes em observabilidade (métricas, dashboards)

- Descrição: adicionar/ajustar métricas, Prometheus rules, dashboards, logging.  
- Gates principais: **T6**, com reflexos em T4–T5–T5.1.  
- Scripts mínimos: `bin/orr_t6_observability_smoke.sh`, e rodar Gates dependentes (T4/T5/T5.1) para garantir que as métricas continuam legíveis.

#### 5.6 Mudanças no ORR/CI

- Descrição: alterar `.ci/orr_pipeline.yml`, scripts `bin/orr_tX_*`, `bin/orr_all.sh`.  
- Gates principais: **T7**, com impactos indiretos em todos os outros.  
- Scripts mínimos: `bin/orr_t7_orr_pipeline.sh`, `.ci/orr_pipeline.yml` na CI.

#### 5.7 Ajustes de produto/UX que não mudam modelo

- Descrição: mudanças de UI, mensagens, pequenos ajustes que não afetam ingest, Vault, Explore ou Confiança.  
- Gates principais: normalmente nenhum; ainda assim, é desejável rodar `bin/orr_all.sh` para garantir que nada foi impactado.

Se surgir um tipo de tarefa novo, ele deve ser adicionado a este catálogo com mapeamento explícito para Gates e scripts.

---

### 6. Superprompts oficiais para o Codex

Os superprompts abaixo são templates oficiais. O Planner deve adaptá‑los, nunca inventar formato completamente novo.

#### 6.1 Template geral — Implementar ou ajustar uma tarefa

```text
Você é o Codex, engenheiro do projeto Inspectah.

Contexto fixo do projeto:
- Leia e respeite estes documentos no repositório:
  - docs/inspectah_cap_1_produto.md
  - docs/inspectah_cap_2_gates_orr.md
  - docs/inspectah_cap_3_filemap_evidencias.md
- O Capítulo 2 define os Gates T0–T8 (contratos, thresholds, pré/pós-condições).
- O Capítulo 3 define o filemap e onde ficam scripts, configs, scorecards e evidências.
- Você NÃO deve alterar Cap.1–3, nem mudar thresholds ou semântica de Gates, a menos que a tarefa diga explicitamente para atualizar esses capítulos.

TAREFA:
- Objetivo de negócio/técnico (2–4 frases): <preencher>
- Gate(s) diretamente afetado(s): <ex.: T2, T3, T4>
- Gates que NÃO devem regredir: <ex.: T3, T4, T5, T5.1, T7>

ARQUIVOS / PASTAS RELEVANTES (Cap.3):
- Código principal: <ex.: src/field_designer/*, src/watchers/api_watcher.py>
- Configs: <ex.: configs/sources/api_nova.yaml>
- Scripts de ORR: <ex.: bin/orr_t2_field_designer_smoke.sh, bin/orr_t3_pipeline_invariants.sh>
- Evidências/scorecards esperados: <ex.: out/scorecards/T2_field_designer.json>

REGRAS OBRIGATÓRIAS:
- Preserve o filemap do Cap.3; não crie pastas raiz novas.
- Qualquer teste ou script novo deve escrever evidência em out/evidence/... e scorecards em out/scorecards/..., seguindo o padrão dos Gates.
- Não altere thresholds ou critérios de PASS/FAIL dos Gates neste trabalho.

SAÍDAS ESPERADAS:
- Lista de arquivos a criar/editar.
- Conteúdo proposto para cada arquivo.
- Instruções de execução (comandos bin/orr_tX_* e/ou bin/orr_all.sh) para validar.
- Notas sobre impactos em Gates e métricas (explicitando PASS/FAIL esperado).
```

#### 6.2 Template — Nova Fonte + watcher

```text
Você é o Codex do Inspectah. Sua tarefa é adicionar suporte a uma nova Fonte.

Fonte:
- Tipo: <RSS / API JSON / HTML / outro>
- Nome lógico: <ex.: preco_frango_assai_sp>
- Campos de interesse: <lista de campos, tipos, validações>

Gate(s) alvo:
- T2: Field Designer deve conseguir cadastrar e extrair campos dessa Fonte.
- T3: pipeline (watchers + Evidence Vault) precisa manter dedup, imutabilidade e backfill corretos.
- T4: bundles de evidência completos para Itens desta Fonte.
- T5: não piorar as métricas de desempenho relevantes.

Arquivos (Cap.3):
- configs/sources/<nome>.yaml
- src/watchers/<tipo>_watcher.py
- src/evidence_vault/* (se necessário)
- bin/orr_t2_field_designer_smoke.sh
- bin/orr_t3_pipeline_invariants.sh
- bin/orr_t4_evidence_audit.sh

Regras:
- Siga o padrão das fontes existentes.
- Não crie pastas fora de configs/sources, src/watchers, src/evidence_vault, bin/.

Ao final, explique como rodar:
- bin/orr_t2_field_designer_smoke.sh
- bin/orr_t3_pipeline_invariants.sh
- bin/orr_t4_evidence_audit.sh
- (opcional) bin/orr_t5_performance_gate.sh
para garantir que T2, T3 e T4 continuem PASS.
```

#### 6.3 Template — Ajustes no Confidence Engine (High Risk)

```text
Você é o Codex do Inspectah. Sua tarefa é ajustar o Confidence Engine.

Contexto:
- O Confidence Engine vive em src/confidence_engine/*.
- Perfis de confiança são definidos em configs/profiles/confidence_profiles.yaml.
- T5.1 (confidence) precisa continuar PASS: cobertura ≥95%, scores em [0,100], distribuição saudável.
- Mudanças aqui são classificadas como HIGH RISK, pois impactam integrações externas e futuros experimentos de calibração (T5.2).

TAREFA:
- Objetivo do ajuste (ex.: reduzir saturação em 100%, diferenciar melhor multi-fonte vs single-fonte, etc.).

Regras:
- Não altere thresholds de T5.1 em Cap.2/Cap.3.
- Garanta que a lógica continue emitindo scores válidos (0–100, sem NaN) com cobertura ≥95%.
- Preserve os dados necessários para futuras calibrações T5.2.

Ao final, inclua instruções para:
- Rodar bin/orr_t5_1_confidence_gate.sh.
- Ler e interpretar out/scorecards/T5_1_confidence.json.
- Verificar se a nova distribuição de scores continua saudável.
```

Outros templates específicos podem ser derivados com o mesmo padrão.

---

### 7. Exemplo end‑to‑end — Nova API de preços

Esta seção mostra, em narrativa, como uma tarefa típica flui pelo sistema.

**Contexto:** queremos que o Inspectah acompanhe o preço de “frango resfriado” em determinados bairros, usando a API de um grande varejista.

1. **PO define a necessidade**  
   “Precisamos que o Inspectah consiga comparar o preço médio de frango resfriado em SP (zona leste) e RJ (zona norte) usando a API X, com atualização de hora em hora.”

2. **Planner identifica Gates e arquivos**  
   - Gates alvo: T2 (Field Designer & Fonte), T3 (invariantes de pipeline), T4 (Evidence Vault), T5 (desempenho).  
   - Arquivos: `configs/sources/api_frango_varejista.yaml`, `src/watchers/api_watcher.py` (nova função ou extensão), `bin/orr_t2_field_designer_smoke.sh`, `bin/orr_t3_pipeline_invariants.sh`, `bin/orr_t4_evidence_audit.sh`, `bin/orr_t5_performance_gate.sh`.

3. **Planner escreve mini‑spec e superprompt**  
   - Mini‑spec descreve campos (bairro, preço, timestamp, unidade), metas de latência e de `field_resolution_success`.  
   - Superprompt segue Seção 6.2, preenchido com detalhes da API e dos campos.

4. **Codex implementa**  
   - Cria `configs/sources/api_frango_varejista.yaml` com o mapeamento de campos.  
   - Ajusta `src/watchers/api_watcher.py` para suportar essa API.  
   - Garante que o watcher grava bundles completos no Evidence Vault.  
   - Se necessário, faz pequenos ajustes no Field Designer para que o Admin consiga cadastrar essa Fonte pela UI interna.

5. **Validação local**  
   - Rodar `bin/orr_t2_field_designer_smoke.sh` → Verificar `T2_field_designer.json` e amostra de Itens em `T2_field_designer/*`.  
   - Rodar `bin/orr_t3_pipeline_invariants.sh` → Dedup/imutabilidade PASS, sem violações em `T3_pipeline_invariants/*`.  
   - Rodar `bin/orr_t4_evidence_audit.sh` → `evidence_completeness` e `evidence_hash_valid_rate` = 100%.  
   - Rodar `bin/orr_t5_performance_gate.sh` após alguns dias de operação interna para checar latência e SLOs.

6. **CI/ORR**  
   - PR aberto; `.ci/orr_pipeline.yml` executa Gates T1–T6/T7.  
   - `T7_orr.json` mostra todos os Gates relevantes PASS na nova foto.

7. **Uso interno e T8**  
   - Operadores usam o Inspectah para consultar o preço de frango nos bairros alvo.  
   - T8 consolida métricas de uso e feedback; se tudo ok, a funcionalidade é considerada Go.

Essa história completa serve como modelo mental para qualquer tarefa: declarar Gate, mapear arquivos, acionar Codex, validar Gates, checar ORR, usar na prática.

---

### 8. Rotina diária de operação técnica (Codex + CI)

Sugestão mínima de rotina:

- **Início do dia (técnico):**  
  - Checar a última execução do ORR em CI: ver status de T0–T7 em `T7_orr.json` e demais scorecards.  
  - Se algum Gate crítico (T3, T4, T5, T5.1, T7) estiver FAIL, priorizar correção antes de novas features.

- **Antes de abrir PR importante:**  
  - Rodar localmente os `bin/orr_tX_*` dos Gates impactados.  
  - Verificar scorecards e evidências; se algo ficou borderline, corrigir antes do PR.

- **Após merge em branch principal:**  
  - Acompanhar a próxima execução de ORR em CI.  
  - Confirmar que existe uma foto recente com T0–T7 PASS simultaneamente.

Disciplina aqui evita “surpresas” no fim da sprint.

---

### 9. Debug guiado por Gates (Kleppmann‑style)

Quando algo quebra, comece sempre pelo Gate correspondente.

- **Se T3 (pipeline invariants) está FAIL:**  
  - Verificar `out/scorecards/T3_pipeline_invariants.json` (tipo de violação).  
  - Abrir `out/evidence/T3_pipeline_invariants/*` para exemplos concretos.  
  - Inspecionar `src/watchers/*` e `src/evidence_vault/*` em busca de code paths que alterem Observações ou gerem duplicatas.  
  - Ação: corrigir lógica, adicionar testes de regressão e rerodar `bin/orr_t3_pipeline_invariants.sh`.

- **Se T4 (Evidence Vault) está FAIL:**  
  - Ver `T4_evidence_vault.json` (metas de completude/integridade).  
  - Em `T4_evidence_vault/*`, identificar quais Itens estão sem bundle ou com hash quebrado.  
  - Checar `vault_store.py` e watchers para ver se bundles estão sendo gravados corretamente.  
  - Ação: ajustar gravação, reprocessar janelas, rerodar `bin/orr_t4_evidence_audit.sh`.

- **Se T5 (performance) está FAIL:**  
  - Ler `T5_performance.json` e métricas brutas em `T5_performance/*`.  
  - Conferir alertas e histogramas em Prometheus/Grafana.  
  - Ver `src/watchers/*` e `src/explore/*` em busca de queries pesadas, loops, etc.  
  - Ação: otimizar, testar de novo, reacompanhar métricas e rerodar `bin/orr_t5_performance_gate.sh`.

- **Se T5.1 (confidence) está FAIL:**  
  - Ver `T5_1_confidence.json` (cobertura, buckets, valores inválidos).  
  - Conferir `src/confidence_engine/*` e `configs/profiles/confidence_profiles.yaml`.  
  - Avaliar se há saturação (tudo 100%) ou buracos (scores ausentes).  
  - Ação: ajustar heurísticas com superprompt High Risk (Seção 6.3), rerodar `bin/orr_t5_1_confidence_gate.sh`.

- **Se T7 (ORR/CI) está FAIL ou flaky:**  
  - Ver `T7_orr.json` e logs da pipeline `.ci/orr_pipeline.yml`.  
  - Identificar se é problema de ambiente, flakiness em testes ou script `bin/orr_tX_*` mal comportado.  
  - Ação: estabilizar scripts, reduzir dependências frágeis e garantir repetibilidade local/CI.

Essa abordagem reduz o debug a um ciclo: olhar scorecard → olhar evidências → olhar código → corrigir → rerodar Gate.

---

### 10. Regras de ouro e anti‑padrões (versão endurecida)

**Regras de ouro:**

1. Cap.2 e Cap.3 são lei.  
   Qualquer mudança estrutural de Gates, thresholds ou filemap começa por esses capítulos, nunca por um patch silencioso em código.

2. Tudo deve encaixar em um Gate.  
   Se uma atividade não aponta claramente para T0–T8 e para arquivos de Cap.3, ela não é trabalho de sprint, é no máximo pesquisa/descoberta.

3. Sem evidência, não aconteceu.  
   Melhorias que não resultam em scorecards/evidências em `out/` não existem para o Inspectah.

4. Simetria local/CI.  
   Scripts `bin/orr_tX_*` funcionam tanto local quanto em CI; se isso quebrar, o sistema está desalinhado.

5. Confiança é high risk.  
   Qualquer tarefa que mexa com `confidence_score` ou `confidence_profile_id` é automaticamente de alto risco, exige atenção extra em revisão e sempre passa por T5.1.

**Anti‑padrões (proibidos, exigem exceção formal):**

- Bypass de Gates: “temporariamente ignorar T3/T4/T5/T5.1/T7” sem exceção formal escrita, datada, com plano de reversão.  
- Alterar thresholds de Gates (SLOs, percentis, limites de PASS/FAIL) diretamente em código, sem atualizar Cap.2 e Cap.3.  
- Criar scripts de ORR ou pipelines de CI fora dos lugares definidos em Cap.3 (`bin/`, `.ci/`).  
- Introduzir novas pastas raiz para funções que já têm lugar mapeado (por exemplo `tools/`, `scripts/` paralelos).  
- Ignorar falhas de ORR com o argumento “passou na minha máquina” ou “é só flake” sem análise e estabilização.

Qualquer exceção a essas regras precisa aparecer registrada em evidência (ex.: anotação em `out/evidence/T0_spec_lock/*` ou doc de sprint), com vencimento claro.

---

### 11. Como humanos devem usar o Capítulo 4 v2

Para o PO e Planner:

- Usar o Cap.4 v2 como checklist ao criar tarefas: declarar Gates, arquivos, pré/pós-condições e superprompt.  
- Consultar o catálogo de tipos de tarefa (Seção 5) para saber quais Gates/scripts são obrigatórios.

Para revisores de PR:

- Verificar se o PR declara os Gates afetados e menciona os scorecards relevantes.  
- Confirmar que os arquivos modificados pertencem aos caminhos mapeados no Cap.3.  
- Garantir que Gates críticos não regrediram (T3, T4, T5, T5.1, T7).  
- Exigir evidência de ORR recente com T0–T7 PASS para considerar a mudança “concluída”.

Para operadores:

- Usar a linguagem dos Gates ao reportar problemas (“T4 parece quebrado para fonte X”, “T5.1 suspeito em domínio Y”).  
- Fornecer feedback para T8 em formato que possa ser anexado em `out/evidence/T8_go_nogo/*`.

Capítulo 4 v2 fecha o ciclo Cap.1–3 com um playbook operacional 15/10: Gates definem o contrato, o filemap organiza o código, e este capítulo garante que a execução do dia a dia respeite, sempre, esse contrato.

