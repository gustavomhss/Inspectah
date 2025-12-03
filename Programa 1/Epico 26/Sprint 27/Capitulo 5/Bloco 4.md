# Inspectah — Sprint 27 (S27)
## Capítulo 5 — Bloco 4
### Roteiro Operativo do ORR & Boas Práticas de Condução

> Arquivo-alvo sugerido no repo: `docs/s27_cap_5_4_orr_roteiro_operativo.md`
>
> Função: descrever **como conduzir**, na prática, o ORR da Sprint 27 — antes, durante e depois da sessão — garantindo disciplina, foco em evidências e registro sólido de decisões. Este bloco é o manual de operação do ORR.

---

## 1. Objetivos deste bloco

Este Bloco 4 traduz os capítulos anteriores em um roteiro operacional para o ORR da S27. Ele precisa garantir que:

1. A sessão de ORR **não começa torta** (pré-checklist cumprido, evidências no lugar).  
2. A reunião é **objetiva e guiada por dados**, não por opinião solta.  
3. As decisões são **registradas de forma estruturada** (G6, Cap.5 e Cap.6).  
4. O resultado é **acionável**: gera ações, riscos mapeados e impacto claro no roadmap.

---

## 2. Fases do ORR da S27

O ORR é dividido em três fases:

1. **Pré-ORR** — preparação silenciosa, sem reunião.  
2. **Sessão de ORR** — reunião formal com os owners e representantes.  
3. **Pós-ORR** — ajustes finos de registro, comunicação de decisão e alimentação do roadmap.

Cada fase tem responsáveis, entregas e checklists próprios.

---

## 3. Fase 1 — Pré-ORR (preparação)

### 3.1 Responsável principal

- **Representante de Qualidade / Gates** (chair designado do ORR) é o dono desta fase.  
- Owners de Admin v1, Fontes, Ingestão, Debunker e Ops colaboram para fechar pendências.

### 3.2 Checkpoints obrigatórios

Antes de marcar a sessão de ORR, o chair precisa garantir que:

1. **Checklist pré-ORR (Bloco 2) está verde ou com exceções claras**  
   - Todos os scorecards G0–G6 existem e estão atualizados.  
   - `out/evidence/S27_G*/` contém logs razoáveis.  
   - Bundle `inspectah_s27_evidence_bundle.zip` existe e abre.  
   - Cap.1–Cap.5 estão minimamente atualizados; Cap.6 pode estar em rascunho.  
   - Guia Admin v1.1 e runbooks existem.

2. **Ambiente de demonstração está pronto**  
   - Consoles de Fontes, Ingestão e Debunker sob Admin v1 estão acessíveis no ambiente que será usado na reunião (local, staging, etc.).

3. **G6 inicial foi gerado em modo rascunho**  
   - `S27_G6_orr_summary.json` existe com:  
     - `sprint_id`, `epic_id`;  
     - `gates_status` preenchido automaticamente;  
     - `bundle_created` e `bundle_path`;  
     - placeholders em `states_status`, `key_risks`, `actions_required`, `summary`.

4. **Convite e agenda foram enviados**  
   - Convite para a sessão de ORR inclui:  
     - objetivo;  
     - duração estimada;  
     - link/agenda;  
     - lista de docs a serem lidos antes da reunião (Cap.1, Cap.2, Cap.3, Cap.4, Bloco 1 e 2 de Cap.5, G6 rascunho).

### 3.3 Saída da fase de pré-ORR

- `S27_G6_orr_summary.json` em modo rascunho pronto para ser ajustado durante a sessão.  
- Checklist pré-ORR (Bloco 2) revisado e assinado pelo chair (nem que seja "assinado" em uma nota textual).  
- Participantes cientes de que o ORR **não é** uma revisão de código, mas de prontidão do sistema.

---

## 4. Fase 2 — Sessão de ORR (reunião)

### 4.1 Duração e formato sugeridos

- Duração alvo: **60 a 90 minutos**.  
- Formato: reunião síncrona (videoconferência ou presencial), com alguém compartilhando tela com:  
  - G6 rascunho;  
  - docs principais (Cap.1–Cap.4);  
  - consoles admin (em ambiente real).

### 4.2 Agenda sugerida (roteiro minuto-a-minuto)

1. **Abertura e contexto (5–10 min)**  
   - Chair relembra objetivo do ORR da S27 (Bloco 1).  
   - Revisão rápida dos estados-alvo SA-01..SA-05.  
   - Confirmação de que todos têm acesso aos docs e bundle.

2. **Passada rápida pelos gates (15–25 min)**  
   - Chair projeta um resumo de `gates_status` (G0–G5) a partir de G6.  
   - Para cada gate:  
     - visão geral do scorecard;  
     - discussão curta de qualquer campo crítico ou `notes` relevante;  
     - se necessário, abrir logs em `out/evidence/S27_G*/`.

3. **Demonstração dos consoles Admin (15–20 min)**  
   - Owner Admin v1 ou front compartilha tela e mostra:  
     - console de Fontes: fluxo principal (listagem, detalhe, ação típica);  
     - console de Ingestão: visão geral, relação com Fontes;  
     - Debunker: casos, evidências, decisão;  
     - pelo menos um fluxo combinado Fontes → Ingestão → Debunker.  
   - Durante a demo, o chair reforça qual cenário E2E de G2 está sendo representado.

4. **Operação & Runbooks (10–15 min)**  
   - Owner Ops/Runbooks apresenta a estrutura do guia Admin v1.1 e dos runbooks.  
   - Opcional, mas desejável: descrição breve de uma simulação de incidente resolvida via runbook (não precisa reencenar ao vivo, basta relatar com clareza).

5. **Discussão estruturada de riscos e ações (10–15 min)**  
   - Chair abre seções `key_risks` e `actions_required` de G6.  
   - Em grupo, listar os 3–7 riscos realmente importantes (sem inflar demais a lista).  
   - Para cada risco: validar impacto, likelihood, owner e sprint alvo recomendada.  
   - Em seguida, mapear ações correspondentes (ACT-XXX).

6. **Definição e registro do veredito (10–15 min)**  
   - Com base no que foi visto:  
     - definir `states_status` (SA-01..SA-05);  
     - definir `verdict_sprint` e `verdict_epic`;  
     - preencher `summary.what_was_decided` e rascunhar `why_decision_makes_sense` / `how_it_impacts_roadmap`.  
   - Chair valida coerência básica (regra da Seção 4 do Bloco 3).  
   - Se houver divergência séria entre participantes, registrar em `notes`.

### 4.3 Regras de disciplina durante a sessão

Para evitar que o ORR derrape:

- **Sem mergulhar em debugging de código**  
  - Se surgir bug ou dúvida profunda de implementação, registrar como ação/risk, não tentar resolver ali.

- **Falar com base em evidência**  
  - Opiniões devem ser ancoradas em scorecards, logs, demos ou docs.  

- **Time-box em cada parte da agenda**  
  - Chair mantém o tempo e corta discussões que não movem a decisão.

- **Registrar decisões em tempo real**  
  - Alguém (chair ou escriba) edita G6 e Cap.5 ao vivo, não "depois a gente preenche".

---

## 5. Fase 3 — Pós-ORR (consolidação e comunicação)

### 5.1 Ajustes finos em G6 e Cap.5

Depois da sessão, em um prazo curto (idealmente 24–48h):

- refinamentos de redação em `summary` e `notes` de G6 podem ser feitos;  
- `key_risks` e `actions_required` podem ganhar mais detalhes (IDs de issues, links, etc.);  
- Cap.5 (este capítulo) deve ser atualizado com:  
  - veredito final;  
  - breve relato da discussão;  
  - lista de riscos e ações mais relevantes.

Não é permitido alterar o veredito (`verdict_sprint`, `verdict_epic`) sem uma nova sessão de ORR ou, no mínimo, uma nota explícita em `notes` com data, motivo e participantes da reavaliação.

### 5.2 Alimentando Cap.6, backlog e roadmap

A partir do G6 final:

- Cap.6 (`docs/s27_cap_6_learnings_dividas_roadmap.md`) deve ser preenchido com:  
  - learnings (a partir de `key_strengths` e `summary`);  
  - dívidas (a partir de `key_risks` e `actions_required`);  
  - implicações de roadmap (`how_it_impacts_roadmap`).  

- As ações (ACT-XXX) devem ser convertidas em:  
  - tasks/sprints futuras (por exemplo, S2X, S2Y);  
  - eventualmente, épicos adicionais, se algum risco apontar para trabalho maior.

### 5.3 Comunicação do veredito

O veredito do ORR da S27 deve ser comunicado de forma simples e honesta, por exemplo:

- mensagem em canal interno (Slack/Teams/etc.);  
- breve resumo com:  
  - veredito da S27 e do Épico E26;  
  - principais riscos;  
  - principais próximos passos.

Sempre apontando para:

- o arquivo `S27_G6_orr_summary.json`;  
- este Cap.5;  
- Cap.6 (quando estiver pronto).

---

## 6. Boas práticas para ORRs futuros (reutilizáveis)

Embora este Bloco 4 seja escrito para a S27, algumas práticas deveriam virar padrão para ORRs futuros do Inspectah:

1. **ORR não é status meeting**  
   - É um gate de prontidão; só acontece quando há evidências minimamente maduras.

2. **Scorecards sempre antes da opinião**  
   - Discussão começa em `SXX_GX_*.json`, não em "eu sinto que".

3. **Poucos riscos, bem descritos**  
   - Melhor 3–7 riscos bem modelados do que 30 superficiais.

4. **Ação para cada risco importante**  
   - Se um risco é mantido, deve haver uma ação correspondente; se não há ação possível, o risco precisa ser reavaliado.

5. **Registro ao vivo**  
   - Decisões vão para o G6 e para Cap.5 enquanto a reunião acontece.

6. **Bundle como verdade congelada**  
   - Sempre que alguém questionar o veredito no futuro, a conversa recomeça a partir do bundle da sprint.

---

## 7. Resultado esperado deste bloco

Com o Bloco 4, o ORR da Sprint 27 deixa de ser um evento meio místico e passa a ser um processo operacional claro, repetível e auditável:

- a preparação é objetiva;  
- a sessão é focada e guiada por evidências;  
- o registro do veredito é estruturado;  
- os efeitos do ORR são imediatamente traduzidos em learnings, dívidas e plano de ação.

Esse é o fechamento natural do Capítulo 5: a ponte entre a produção de evidências da S27 e as decisões sérias sobre Admin v1 em Programa 1 (Épico E26).