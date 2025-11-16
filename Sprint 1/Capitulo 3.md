# D9 — Inspectah — Sprint 1 (Spec & Roadmap)
## Capítulo 3 — Plano de Execução, Rituais e Fluxo de Trabalho (v1.1)

> Leslie no comando: os Capítulos 1 e 2 definem **o que** precisa existir e **como** será avaliado. O Capítulo 3 responde **como executar a sprint D9 na prática** — em que ordem, com quais threads, quais rituais e como registrar o avanço até o encerramento. Este capítulo foi escrito explicitamente como **manual de instrução** para humanos e para o Codex: qualquer agente de implementação pode seguir estes passos como um playbook operacional.

---

## 0) Propósito do Capítulo 3

- Transformar o pacote de objetivos (Cap. 1) + gates (Cap. 2) em um **plano de trabalho concreto**, legível também por um agente Codex.  
- Garantir que D9 pode ser executada por **uma pessoa ou um time** sem depender de contexto implícito.  
- Definir:  
  - fases de execução;  
  - threads de trabalho e seus donos;  
  - relação threads → gates;  
  - ordem recomendada;  
  - rituais e checkpoints;  
  - como e quando preencher evidências e a matriz de gates.

Cap.3 é independente de ferramenta: pode ser aplicado usando issues do GitHub, Notion, um arquivo `.md` ou qualquer outro sistema de tarefas. Se no futuro forem criados scripts (ex.: `bin/d9_check_gates.sh`), eles apenas **automatizam** partes deste processo; o protocolo humano permanece o mesmo.

---

## 1) Fases da Sprint D9 (visão macro)

D9 é uma sprint de **especificação**, não de código. O fluxo recomendado:

1) **Fase 0 — Pré‑flight (G0)**  
   - Leitura obrigatória de DNA MBP/Oráculo, Lessons, Cap.1 e blueprint bruto.  
   - Preenchimento de `evidence/d9_g0_preflight_checklist.md`.  
2) **Fase 1 — Visão Macro & Narrativa (G1)**  
   - Consolidar D9.0 (blueprint) e D9.1 (overview).  
   - Garantir que a história do Inspectah está redonda e alinhada ao Cap.1.  
3) **Fase 2 — Núcleo Técnico de Dados (G2–G4)**  
   - D9.2 (Field Designer), D9.3 (Explore/API), D9.4 (Data Model) e D9.5 (LGPD/ToS).  
   - Aqui se definem contratos, esquemas, integrações e limites legais.  
4) **Fase 3 — Tempo & Evolução (G5)**  
   - D9.6 (roadmap) e D9.8 (mini‑playbook).  
   - Tradução de tudo em versões v0/v1/v1.x e regras de mudança.  
5) **Fase 4 — Ponte para Implementação (G6 + matriz final)**  
   - D9.7 (superprompt Codex) e `d9_summary_gate_matrix.json`.  
   - Fechamento e handoff para a próxima sprint (implementação do v0).

Fases 2 e 3 têm partes paralelizáveis, mas a recomendação é sempre **fechar G1 antes de mergulhar fundo** e **não declarar D9 pronta sem concluir G6**.

Os "dias" citados nas seções seguintes devem ser lidos como **slots de trabalho** (blocos de foco), não como calendário rígido. Um slot pode durar algumas horas ou mais, dependendo da disponibilidade do time.

---

## 2) Threads de Trabalho da D9

Para organizar melhor, D9 pode ser executada em até 6 threads lógicas. Uma mesma pessoa pode acumular várias threads; o importante é a clareza do "dono" e das dependências. Um agente Codex também pode ser instruído a operar "dentro" de uma thread específica, seguindo este capítulo.

### 2.1 Mapa threads → gates

| Thread | Foco principal                                   | Gates diretamente associados |
|--------|--------------------------------------------------|------------------------------|
| T‑0    | Pré‑flight & guardião do DNA                     | D9-G0                        |
| T‑1    | Visão macro (blueprint + overview)               | D9-G1                        |
| T‑2    | Field Designer                                   | D9-G2                        |
| T‑3    | Explore API & integrações                        | D9-G3                        |
| T‑4    | Data model + LGPD/ToS                            | D9-G4                        |
| T‑5    | Roadmap v0/v1/v1.x + mini-playbook de evolução   | D9-G5                        |
| T‑6    | Superprompt Codex v1 + matriz de gates           | D9-G6                        |

Invariante operacional: **nenhuma thread pode ser marcada como "done" enquanto o gate correspondente não estiver em `PASS` na `d9_summary_gate_matrix.json`.** Status de thread e status de gate não podem divergir.

### Thread T‑0 — Pré‑flight & Guardião do DNA

- Responsável por:  
  - puxar leituras obrigatórias;  
  - garantir que ninguém avança sem D9-G0 em PASS;  
  - manter coerência com Blocos 0–5 e Lessons.  
- Entregáveis principais:  
  - `evidence/d9_g0_preflight_checklist.md`.  
- Depende de: nada (é sempre o primeiro passo).  
- Alimenta: todas as demais threads.

### Thread T‑1 — Visão Macro (Blueprint + Overview)

- Responsável por:  
  - consolidar o blueprint D9.0;  
  - escrever o overview D9.1;  
  - sincronizar narrativa com Cap.1.  
- Entregáveis:  
  - `d9_0_inspectah_blueprint_consolidado_v1_2_x.md`;  
  - `d9_1_inspectah_overview_human_friendly_v1_0.md`;  
  - `evidence/d9_g1_blueprint_overview_checklist.md`.  
- Depende de: T‑0 (G0).  
- Alimenta: T‑2, T‑3, T‑4, T‑5, T‑6.

### Thread T‑2 — Field Designer

- Responsável por:  
  - detalhar Anexo A (Field Designer);  
  - garantir exemplos concretos;  
  - amarrar tudo com o blueprint.  
- Entregáveis:  
  - `d9_2_anexo_a_field_designer_v1_0.md`;  
  - `evidence/d9_g2_field_designer_checklist.md`.  
- Depende de: T‑1 (G1 em progresso, visão estável).  
- Alimenta: T‑3 (como os campos aparecem em respostas e filtros) e T‑4 (quais tabelas/campos são necessários).

### Thread T‑3 — Explore API & Integrações

- Responsável por:  
  - especificar Anexo B (APIs, filtros, exports, webhooks);  
  - desenhar exemplos de consumo por MBP e outros sistemas.  
- Entregáveis:  
  - `d9_3_anexo_b_explore_api_integracoes_v1_0.md`;  
  - `evidence/d9_g3_explore_api_integracoes_checklist.md`.  
- Depende de: T‑1; conversa com T‑2 e T‑4 (para nomes de campos e esquema).  
- Alimenta: T‑6 (superprompt Codex) e futura sprint de implementação.

### Thread T‑4 — Data Model + LGPD/ToS

- Responsável por:  
  - modelar dados (Anexo C);  
  - definir envelope legal (Anexo D).  
- Entregáveis:  
  - `d9_4_anexo_c_data_model_ddl_migracao_v1_0.md`;  
  - `d9_5_anexo_d_lgpd_tos_envelope_risco_v1_0.md`;  
  - `evidence/d9_g4_data_model_lgpd_checklist.md`.  
- Depende de: T‑1; troca forte com T‑2 e T‑3.  
- Alimenta: T‑5 (roadmap/evolução) e decisões futuras de operação.

### Thread T‑5 — Roadmap & Evolução

- Responsável por:  
  - D9.6 (roadmap v0/v1/v1.x);  
  - D9.8 (mini‑playbook de evolução).  
- Entregáveis:  
  - `d9_6_roadmap_inspectah_v0_v1_v1x_v1_0.md`;  
  - `d9_8_miniplaybook_evolucao_inspectah_v1_0.md`;  
  - `evidence/d9_g5_roadmap_playbook_checklist.md`.  
- Depende de: T‑1, T‑2, T‑3, T‑4 (precisa ver o pacote quase inteiro).  
- Alimenta: T‑6 (superprompt) e planejamento da próxima sprint.

### Thread T‑6 — Superprompt Codex + Matriz de Gates

- Responsável por:  
  - escrever D9.7 (superprompt Codex v1);  
  - consolidar `d9_summary_gate_matrix.json`;  
  - garantir que tudo está pronto para handoff.  
- Entregáveis:  
  - `d9_7_superprompt_codex_v1_inspectah_v0_core_data_hub.md`;  
  - `evidence/d9_g6_superprompt_codex_checklist.md`;  
  - `evidence/d9_summary_gate_matrix.json`.  
- Depende de: todos os outros threads (T‑1 a T‑5).  
- Alimenta: próxima sprint (implementação v0).

---

## 3) Rituais e Checkpoints da Sprint D9

D9 não exige reuniões formais, mas alguns rituais simples ajudam a manter tudo sob controle. Para o Codex, estes rituais funcionam como "loops de revisão" entre blocos de trabalho.

### 3.1 Kickoff da Sprint (D9‑K0)

Objetivo: alinhar todo mundo em 30–45 min (ou em uma única sessão de Codex).

- Revisar rapidamente o Cap.1 (contexto) e o Cap.2 (gates).  
- Confirmar quem assume cada thread T‑0…T‑6 (ou que ordem de threads o Codex seguirá).  
- Alinhar ordem de foco:  
  - começar por G0+G1;  
  - planejar janelas para D9.2–D9.5;  
  - reservar tempo final para D9.6–D9.7 e matriz de gates.  
- Abrir um checklist de sprint (pode ser um `.md` simples) com a lista de threads e status.

### 3.2 Checkpoints leves (D9‑Dailies)

Periodicidade sugerida: diária ou a cada 2 dias (ou, para o Codex, a cada bloco de 1–2 prompts relevantes).

Perguntas‑guia:

- O que avançou em cada thread desde o último checkpoint?  
- Algum gate está bloqueado por falta de decisão em outro doc?  
- Alguma pendência de Cap.2 (checagem/kill criteria) foi acionada?  
- Há algo que precisa ser reescrito no Cap.1 à luz do que surgiu em D9.2–D9.5?

### 3.3 Exemplo de quadro de status de threads

Um quadro de status pode ser tão simples quanto:

```text
T‑0 Pré‑flight: PASS (D9-G0 PASS, evidência salva)
T‑1 Blueprint + Overview: em revisão final (checklist G1 quase completo)
T‑2 Field Designer: rascunho pronto, checklist G2 com 2 pendências
T‑3 Explore API: em andamento, endpoints principais descritos
T‑4 Data Model + LGPD: bloqueado esperando definição de 1 campo crítico
T‑5 Roadmap & Evolução: não iniciado
T‑6 Superprompt + Matriz: não iniciado
```

Este quadro pode viver em um `.md` de status ou em qualquer ferramenta de tarefas.

### 3.4 Pré‑fechamento da Sprint (D9‑PF)

Quando todos os docs D9.0–D9.8 já têm rascunho completo:

- Executar, em bloco, as revisões de G1–G6 com os checklists do Cap.2 abertos.  
- Preencher o `d9_summary_gate_matrix.json` em modo rascunho (podem existir FAILs, desde que explicitados).  
- Listar em 1 página as pendências que impedem algum gate de ir para PASS.

### 3.5 Fechamento da Sprint (D9‑CLOSE)

Só ocorre quando:

- Todos os gates D9-G0…D9-G6 estão em PASS;  
- `d9_summary_gate_matrix.json` está consistente com os checklists;  
- Todos os arquivos D9.x estão versionados e salvos.

No fechamento:

- Congelar a versão dos docs (ex.: tag de repositório ou anotação de commit).  
- Registrar em um pequeno parágrafo (que depois irá para Cap.4) o que funcionou bem e o que foi mais difícil em D9.

---

## 4) Fluxo de Execução Sugerido (modo 1 pessoa ou 1 agente Codex)

Se apenas uma pessoa (ou um único agente Codex) for tocar D9, a sugestão é seguir esta ordem linear, usando as threads como blocos de foco. Cada "dia" abaixo significa um **slot de trabalho**, não 24h exatas.

1) **Slot 1–2: T‑0 + T‑1**  
   - Ler DNA + Lessons + Cap.1 + blueprint bruto (G0).  
   - Esboçar/ajustar D9.0 e D9.1 até ficarem coerentes (G1 rascunho).  
2) **Slot 3–4: T‑2 (Field Designer)**  
   - Escrever D9.2, focando em tipos, transforms, computed fields e exemplos.  
   - Preencher `evidence/d9_g2_field_designer_checklist.md`.  
3) **Slot 5–6: T‑3 (Explore API) + T‑4 (Data Model + LGPD)**  
   - Escrever D9.3 (endpoints, filtros, exports, webhooks).  
   - Escrever D9.4 (esquemas, índices, migração) e D9.5 (LGPD/ToS).  
   - Preencher evidências G3 e G4.  
4) **Slot 7: T‑5 (Roadmap & Evolução)**  
   - Escrever D9.6 (corte v0/v1/v1.x).  
   - Escrever D9.8 (mini‑playbook).  
   - Preencher `evidence/d9_g5_roadmap_playbook_checklist.md`.  
5) **Slot 8: T‑6 (Superprompt + Matriz)**  
   - Escrever D9.7 (superprompt Codex) referenciando todos os docs.  
   - Preencher `evidence/d9_g6_superprompt_codex_checklist.md`.  
   - Montar `d9_summary_gate_matrix.json` com o status final de cada gate.  
6) **Slot 9: Revisão geral + ajuste fino**  
   - Revisar Cap.1, Cap.2 e todos os D9.x à luz dos checklists.  
   - Garantir que não há TBD/TODO relevantes.  
   - Fechar a sprint (D9‑CLOSE).

Esse fluxo pode ser aplicado literalmente como roteiro de prompts para o Codex: cada slot pode virar um bloco de instruções, citando explicitamente os arquivos a criar/editar e os checklists a preencher.

---

## 5) Como registrar evidências na prática

Para cada gate:

1) Abrir o documento D9.x correspondente.  
2) Abrir o checklist de evidência em `evidence/` (ex.: `evidence/d9_g2_field_designer_checklist.md`).  
3) Ler o item no Cap.2, navegar até a seção do doc que cobre aquilo e marcar a checkbox com um comentário curto, se necessário.  
4) Ao terminar o gate, atualizar (ou preparar a atualização de) `d9_summary_gate_matrix.json` com:  
   - `gate_id`;  
   - `status` (`PASS`/`FAIL`);  
   - `checked_by`;  
   - `checked_at`;  
   - `evidence_path`;  
   - `notes` (se houver).

Se futuramente for criado um script tipo `bin/d9_check_gates.sh`, ele poderá:

- Ler `d9_summary_gate_matrix.json`.  
- Verificar se todos os gates estão em PASS.  
- Fazer sanity checks (ex.: arquivo de evidência existe, etc.).

O Cap.3 apenas garante que o design dos arquivos é estável o suficiente para essa automação ser criada sem retrabalho.

---

## 6) Relação com futuras sprints de implementação

O Cap.3 também serve como guia de pré‑condições para as próximas sprints. Qualquer sprint que use o Codex para escrever código do Inspectah deve declarar explicitamente quais gates D9 são pré‑condição.

Exemplos:

- Sprint de implementação do **Field Designer**:  
  - Pré‑condições mínimas: D9-G1 e D9-G2 em PASS.  
- Sprint de implementação do **Explore API**:  
  - Pré‑condições mínimas: D9-G1 e D9-G3 em PASS.  
- Sprint que mexa no **modelo de dados**:  
  - Pré‑condições mínimas: D9-G4 em PASS e leitura de D9.8 (playbook).  
- Sprint de integrações profundas com MBP ou oráculos externos:  
  - Pré‑condições mínimas: D9-G3, D9-G5 em PASS e respeito aos limites de D9.5.

Assim, D9 não é apenas "uma sprint passada", mas um **módulo de contratos** que governa como o Inspectah pode e deve evoluir, inclusive quando a execução for conduzida pelo Codex.

---

## 7) Fechamento do Capítulo 3

Recapitulando:

- Cap.1 define **contexto, objetivos, escopo e entregáveis**.  
- Cap.2 define **gates, evidências e DoD**.  
- Cap.3 define **como executar a sprint D9 na prática**, em linguagem apropriada tanto para humanos quanto para o Codex: fases, threads, relação threads→gates, rituais, fluxo linear e registro de evidências.

Roteiro em 7 passos para rodar D9:

1) Fazer o pré‑flight (G0) e registrar evidência.  
2) Consolidar blueprint + overview (G1).  
3) Especificar Field Designer (G2).  
4) Especificar Explore API + integrações (G3).  
5) Especificar Data Model + LGPD/ToS (G4).  
6) Definir roadmap + mini‑playbook (G5).  
7) Escrever superprompt Codex + matriz de gates (G6) e fechar a sprint.

A partir deste ponto, D9 está completamente especificada no nível de sprint: sabemos o que precisa existir, como validar, como trabalhar para chegar lá e como o Codex pode seguir este manual para produzir e validar os artefatos necessários.

