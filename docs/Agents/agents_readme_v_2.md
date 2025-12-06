# Inspectah — README dos Agentes de Sprint (v2)

> Versão v2 — alinhada ao **Spec Master v2**, **Sprint Planner Playbook v1** e **ACE Executor v2**.  
> Este README é o **mapa oficial do ecossistema de agentes** da esteira de desenvolvimento do Inspectah.

Ele responde, de forma direta e sem romance:
- Quem são os agentes.  
- Quais arquivos são a "constituição" de cada um.  
- Em que ordem eles trabalham.  
- Como usar tudo isso no dia a dia de uma sprint.

---

## 1. Panorama — Três agentes, três cérebros

Toda sprint do Inspectah passa, obrigatoriamente, por três agentes principais:

1. **Spec Master**  
   - Traduz o que o Stakeholder / Conselho quer em uma sprint **completamente especificada** no formato Playbook 6×4.  
   - Produto final: 24 arquivos de spec da sprint (`docs/sXX_cap_c_b_*.md`), sem lacunas.

2. **Sprint Planner Técnico**  
   - Pega os 24 arquivos da sprint e transforma em um **plano de execução técnica**: waves, tasks, arquivos-alvo, gates, evidências, YAML para o ACE e handoff textual.  
   - Produto final: Cap.4.4 de tasks/waves, `docs/sXX_tasks_execucao.yml`, log/scorecard do Planner e handoff textual.

3. **ACE Executor**  
   - Pega o plano do Planner e **executa**: código, scripts, testes, ajustes de CI/ORR, tudo em waves e tasks, com visão de túnel e contexto mínimo.  
   - Produto final: mudanças de código, testes, scripts, workflows e evidências que fazem os gates da sprint ficarem verdes.

Ordem canônica (não negociável):  
**Stakeholder → Spec Master → Sprint Planner → ACE Executor.**

Nenhum agente pula etapa, nenhum agente substitui o outro.

---

## 2. Constituições — Arquivos oficiais de cada agente

Aqui estão os arquivos que definem o "cérebro" e o contrato de cada agente.  
Se você quiser entender ou ajustar um agente, começa por aqui.

### 2.1. Spec Master

**Cérebro:**  
- `docs/Agents/sprint_spec_master_cerebro_v_2.md`

Define:
- como o Spec Master pensa;  
- como faz pesquisa na KB/DNA;  
- como estrutura os 24 arquivos da sprint;  
- como lida com gaps;  
- como se auto-revisa.

**Playbook / Estrutura de Sprint:**  
- `docs/Sprint Playbook.md`

Define:
- a estrutura 6×4 (Capítulos 1–6, Blocos 1–4);  
- conteúdos esperados por capítulo/bloco;  
- gates, DoD, métricas, ORR;  
- formato dos arquivos `docs/sXX_cap_c_b_*.md`.

**Saída obrigatória do Spec Master para a sprint SXX:**
- `docs/sXX_cap_1_1_*.md` … `docs/sXX_cap_6_4_*.md` — **24 arquivos preenchidos**, sem placeholders.

Sem esses 24 arquivos, a sprint **não existe** para o Planner.

---

### 2.2. Sprint Planner Técnico

**Cérebro:**  
- `docs/Agents/sprint_planner_cerebro_v_4.md`

Define:
- papel do Planner dentro do fluxo;  
- entradas obrigatórias (24 arquivos da sprint, DNA, repo, histórico);  
- outputs formais;  
- pipeline interno P0–P5 (ancoragem, waves, tasks, qualidade, YAML para ACE);  
- regras de gaps/débitos;  
- revisões internas e comitê técnico.

**Playbook:**  
- `docs/Agents/Sprint Planner Playbook V1.md`

Define, com precisão:
- responsabilidades do Planner;  
- insumos;  
- 4 outputs obrigatórios:
  1. `docs/sXX_cap_4_4_tasks_e_waves.md` — capítulo humano de waves e tasks;  
  2. `docs/sXX_tasks_execucao.yml` — plano técnico consumível pelo ACE;  
  3. `out/logs/sXX_planner_review.*` — log de revisão;  
  4. `out/scorecards/sXX_planner.yml` — scorecard de qualidade;  
- outputs auxiliares opcionais (`docs/sXX_planner/...`);  
- pipeline em waves internas P0–P5;  
- forma correta de gerar o handoff textual para o ACE.

**Saídas obrigatórias do Planner para a sprint SXX:**
- `docs/sXX_cap_4_4_tasks_e_waves.md`  
- `docs/sXX_tasks_execucao.yml`  
- `out/logs/sXX_planner_review.*`  
- `out/scorecards/sXX_planner.yml`

Sem, pelo menos, Cap.4.4 e `tasks_execucao.yml`, o ACE **não deve ser ligado**.

---

### 2.3. ACE Executor

**Cérebro:**  
- `docs/Agents/ACE Executor Cerebro V2.md`

Define:
- como o ACE usa `docs/sXX_tasks_execucao.yml` como trilho;  
- como opera com visão de túnel por wave e por task;  
- como usa `ace_resumo`, `waves[].ace_context` e `tasks[].ace_context` para limitar contexto;  
- como lida com testes, gates, ORR e erros estruturais;  
- como se mantém token-frugal e orientado a resultado.

O ACE não tem Playbook separado: o contrato dele é o **YAML do Planner + o cérebro v2**.

**Saídas práticas do ACE Executor em uma sprint SXX:**
- alterações de código (backend, frontend, infra);  
- criação/ajuste de testes;  
- criação/ajuste de scripts `bin/`;  
- ajustes em workflows `.github/workflows/`;  
- recomendações de comandos concretos para validar critérios de DONE e gates;  
- resumos claros do que foi feito por wave e por task.

Quem materializa bundles, scorecards de sprint e ORR final são os **scripts de gates/CI**, não o ACE diretamente, mas o ACE alimenta tudo isso com código e configurações corretas.

---

## 3. Fluxo oficial de uma sprint com agentes

A vida de uma sprint SXX com agentes segue sempre o mesmo roteiro:

1. **Spec Master — Criação da sprint**
   - Recebe tema/objetivo + contexto de Programa/Épico.  
   - Usa seu cérebro v2 + Sprint Playbook (estrutura 6×4).  
   - Pesquisa DNA, blueprints, histórico.  
   - Gera os **24 arquivos**: `docs/sXX_cap_1_1_*.md` … `docs/sXX_cap_6_4_*.md`.  
   - Garante que não há lacunas e que os gates de Cap.2 estão claros.

2. **Sprint Planner Técnico — Planejamento da sprint**
   - Usa o Sprint Planner Playbook v1 + cérebro v4.  
   - Lê a sprint SXX (24 arquivos) em ondas internas P0–P5, conforme Playbook:  
     - P0: ancoragem técnica (Cap.1, Cap.2, partes relevantes de Cap.3/Cap.4, histórico, repo);  
     - P1: definição de waves técnicas (W1, W2, W3…);  
     - P2: tasks núcleo (backend/dados/infra);  
     - P3: tasks frontend/UX/integrações;  
     - P4: tasks de testes, CI, ORR, observabilidade;  
     - P5: contexto para ACE + revisões.  
   - Preenche `docs/sXX_cap_4_4_tasks_e_waves.md` com waves, tasks e estratégia.  
   - Constrói `docs/sXX_tasks_execucao.yml` com `ace_resumo`, waves e tasks (incluindo `ace_context`).  
   - Gera log e scorecard do Planner.  
   - Escreve o **handoff textual** para o ACE (pronto para copiar/colar no terminal).

3. **ACE Executor — Execução da sprint**
   - Recebe o handoff textual e assume o cérebro v2.  
   - Carrega `docs/sXX_tasks_execucao.yml`.  
   - Lê **apenas** `ace_resumo` + `leitura_minima_spec`.  
   - Trabalha **wave por wave**:
     - para cada wave, lê `waves[k].ace_context` e apenas os `spec_refs` indicados;  
     - filtra tasks da wave;  
     - executa tasks uma a uma, implementando código, testes, scripts e ajustes de CI/ORR;  
     - propõe comandos concretos para validar critérios de DONE e gates;  
     - ao fechar a wave, faz um resumo e solta contexto detalhado.  
   - Ao final, faz resumo da sprint: waves concluídas, tasks pendentes, gates/ORR verdes/vermelhos, sugestões de sanity geral.

Esse fluxo é a **linha de montagem oficial**. Se algum agente for pulado, o risco de merda sobe exponencialmente.

---

## 4. Step 1 — README dos Agentes (este arquivo)

Este arquivo (`docs/Agents/agents_readme_v2.md`) é o **ponto de entrada oficial** para o ecossistema de agentes.

Funções principais:
- Explicar quem são Spec Master, Planner e ACE.  
- Apontar os arquivos de cérebro, Playbooks e outputs canônicos.  
- Descrever o fluxo oficial de sprint.  
- Amarrar as peças: se você mexer num cérebro ou num Playbook, você atualiza este README.

Uso recomendado:
- Sempre que alguém novo entrar no projeto, mande ler este README antes de qualquer outra coisa.  
- Sempre que você evoluir algum agente (Spec/Planner/ACE), revise esta versão v2 para não deixar o README desatualizado.

---

## 5. Step 2 — Checklist operacional por sprint

O README define o mapa. O **checklist** define o ritual.  
Ele vive em um arquivo separado:

- `docs/Agents/sprint_agent_checklist_v1.md`

Esse checklist descreve, em formato **marretar** (passo a passo), como rodar uma sprint com os agentes. Estrutura sugerida:

1. **Antes de tudo — validação da sprint**
   - Confirmar que a pasta da sprint SXX existe (ex.: `/Programa 1/Epico YY/Sprint SXX`).  
   - Conferir se os 24 arquivos da sprint foram gerados:
     - `docs/sXX_cap_1_1_*.md` … `docs/sXX_cap_6_4_*.md`.  
   - Se faltar qualquer arquivo ou houver placeholder, a sprint **não está pronta** para o Planner.

2. **Rodar o Spec Master (se ainda não rodou)**
   - Ligar o Spec Master com o prompt oficial.  
   - Garantir que o Spec Master seguiu o Sprint Playbook (conteúdo de cada capítulo/bloco).  
   - Revisar rapidamente Cap.1 e Cap.2 para checar se a dor, o estado-alvo e os gates estão bem definidos.

3. **Rodar o Sprint Planner**
   - Ligar o Planner com o prompt oficial, apontando para a pasta da sprint SXX.  
   - Exigir os 4 outputs obrigatórios:
     - `docs/sXX_cap_4_4_tasks_e_waves.md`  
     - `docs/sXX_tasks_execucao.yml`  
     - `out/logs/sXX_planner_review.*`  
     - `out/scorecards/sXX_planner.yml`  
   - Conferir se o Scorecard do Planner está **verde** (especialmente: `gate_sem_task: false`, `wave_com_contexto_excessivo: false`).  
   - Se o scorecard acusar problemas críticos, o Planner precisa retrabalhar **antes** de ligar o ACE.

4. **Ligando o ACE Executor**
   - Só ligar o ACE depois que o Planner estiver ok.  
   - Usar o prompt oficial do ACE (que referencia `ACE Executor Cerebro V2.md` e `docs/sXX_tasks_execucao.yml`).  
   - Acompanhar waves e tasks, garantindo que critérios de DONE e gates estão sendo respeitados.

5. **Encerramento da sprint**
   - Rodar o script de gates/CI oficial da sprint (se existir, ex.: `bin/sXX_*`).  
   - Verificar se todos os gates esperados estão verdes.  
   - Se não estiverem, registrar claramente onde está o problema: spec, plano, execução, infra, etc.

Este checklist é o **procedimento operacional padrão (POP)** da sprint na era dos agentes.

---

## 6. Step 4 — Prompt Maestro dos Agentes

Além do README e do checklist, existe o **Prompt Maestro**, que vive em:

- `docs/Agents/agents_prompt_maestro_v1.md`

Função do Prompt Maestro:
- Ser o “prompt raiz” usado quando você abre uma nova sessão com o modelo.  
- Explicar rapidamente que:
  - você está no projeto Inspectah;  
  - existem três agentes (Spec Master, Planner, ACE);  
  - cada agente tem um cérebro e (quando aplicável) um Playbook;  
  - você vai informar **qual agente** quer ativar;  
  - o modelo deve carregar mentalmente o cérebro + Playbook correspondentes e seguir aquele papel com rigor.

Estrutura típica do Prompt Maestro:
- Introdução curtíssima do projeto Inspectah (1–2 linhas).  
- Lista dos três agentes e seus arquivos de cérebro/Playbook.  
- Instrução clara: "quando eu disser que você é o Spec Master/Planner/ACE, use o cérebro X e o Playbook Y".  
- Regras globais de excelência: nada de gaps silenciosos, nada de pular steps, nada de web para esses papéis, foco em docs/KB/repo.

Assim, você evita colar paredes de texto gigantes toda vez.  
O Maestro liga o cenário; o prompt específico do agente liga o modo.

---

## 7. Como evoluir o ecossistema sem virar bagunça

Quando quiser melhorar a esteira ou algum agente:

1. **Decida qual agente será afetado**  
   - Mudança de visão de produto/processo? Provavelmente Spec Master.  
   - Mudança de planejamento, waves, tasks, relação com ACE? Planner.  
   - Mudança de execução, ergonomia, consumo de contexto? ACE.

2. **Atualize primeiro o cérebro do agente**  
   - Ajuste o arquivo `*_cerebro_vN.md` correspondente.  
   - Se a mudança for grande, incremente a versão (v2 → v3, etc.).

3. **Atualize Playbooks se necessário**  
   - Ex.: se o pipeline do Planner mudou, atualize `Sprint Planner Playbook V1` (ou crie V2) para refletir a nova realidade.

4. **Atualize este README (v2)**  
   - Ajuste as seções relevantes para refletir novos papéis, novos outputs, novos caminhos.

5. **Ajuste o Prompt Maestro**  
   - Se o comportamento global mudou, o Maestro precisa saber.

6. **Registre a mudança no checklist da sprint**  
   - Se algum step operacional mudou, o checklist também muda.

Regra de ouro:  
> Nenhuma mudança séria em Spec, Planner ou ACE acontece “só no prompt de hoje”.  
> Tudo precisa virar instrução escrita e versionada (cérebro, Playbook, README, checklist, Maestro).

---

## 8. O que este README NÃO é

- Não é o lugar para detalhar cada sprint. Isso fica nos 24 arquivos da sprint + outputs do Planner.  
- Não é o lugar para escrever prompts inteiros de agentes. Isso fica nos arquivos específicos de prompt (ex.: prompt do Planner, prompt do ACE, Prompt Maestro).  
- Não é o lugar para discutir detalhes ultra finos de arquitetura; isso é tarefa dos blueprints e do DNA.

Este README é o **mapa fixo da orquestra de agentes**.  
Enquanto ele estiver consistente, qualquer sprint nova tem um caminho claro do caos do desejo do stakeholder até o código rodando e medido em produção.

