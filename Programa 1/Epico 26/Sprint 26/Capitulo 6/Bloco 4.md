# Inspectah — Sprint 26 (S26)
## Capítulo 6 — Bloco 6.4
### Sistema de Anti-gaps & Enforcement pós-S26

> Arquivo-alvo no repo: `docs/s26_cap_6_4_sistema_anti_gaps.md`
>
> Função: garantir que **nada importante da S26 se perca**: nenhum learning crítico esquecido, nenhuma dívida estrutural sumindo, nenhum ajuste de roadmap ficando só na conversa. Este bloco define o **Sistema de Anti-gaps** específico da S26 e como ele se conecta ao sistema global (Playbook + “Lessons Learned so far v1”).
>
> Ideia central: S26 só está verdadeiramente "fechada" quando tudo que ela ensinou ou revelou está ancorado em, pelo menos, uma destas três coisas:  
> (1) Playbook & normas gerais,  
> (2) backlog rastreável (issues/épicos),  
> (3) roadmap atualizado.

---

## 1. O que é considerado "gap" no contexto da S26

Para não virar buzzword, definimos gap assim:

> **Gap** = qualquer ponto relevante da S26 que, se esquecido, tende a gerar retrabalho, risco ou repetição de erro em S27–S65.

Na prática, caem nessa definição:

1. **Aprendizados não incorporados**  
   Ex.: learning técnico/processual importante (Cap.6.1) que não vira regra de Playbook nem pauta de planejamento.

2. **Dívidas técnicas sem dono/rápida ancoragem**  
   Ex.: itens do Cap.6.2 que não se tornam issues/épicos rastreáveis.

3. **Ajustes de roadmap só na cabeça**  
   Ex.: conclusões de Cap.6.3 que não tocam `Roadmap.md` nem documentos de Programa.

4. **Fragilidades de operação ignoradas**  
   Ex.: riscos e incidentes ligados a fontes (Cap.5) que não viram melhoria concreta (runbook, gate, monitoração) na trilha futura.

O Bloco 6.4 define como evitar que esses quatro tipos de buraco existam.

---

## 2. Checklist de Anti-gaps ao encerrar a S26

Antes de declarar S26 encerrada, o PO/Spec Office deve rodar o seguinte checklist (pode virar `bin/s26_anti_gaps_check.sh` + doc):

1. **Cap.6.1 → Playbook & normas**
   - [ ] Para cada learning "estrutural" do Bloco 6.1 (especialmente processuais), verificar se:  
     - já está refletido no **Sprint Playbook** atualizado (`Sprint Playbook.md`), ou  
     - foi criada uma tarefa explícita para o squad de método atualizar o Playbook.  
   - [ ] Verificar se referências a S26 foram adicionadas (quando fizer sentido) em `Leasson Learned so far v1.md` e addenda relevantes.

2. **Cap.6.2 → Backlog oficial**
   - [ ] Cada `S26-DT-XXX` está mapeada para pelo menos um item no sistema de tracking (issue/épico) com link para este doc.  
   - [ ] Dívidas classificadas como **Alto** risco (`S26-DT-004`, etc.) têm pelo menos uma sprint alvo sugerida (S27–S29) e foram discutidas com o Conselho ou dono de programa.

3. **Cap.6.3 → Roadmap & Programas**
   - [ ] Ajustes propostos em 6.3 foram refletidos em `Roadmap.md` (ou existe issue de atualização, se for guardado em repositório separado).  
   - [ ] Docs de Programa 1 (Admin & Fontes) e programas de Ingestão/Verdade foram revisados para citar explicitamente o estado pós-S26 quando relevante.

4. **Cap.5 ↔ Cap.6**
   - [ ] Incidentes e riscos R1–R5 de Cap.5.4 que se materializaram (ou que são claramente prováveis) foram mapeados para dívidas técnicas ou ajustes de roadmap.  
   - [ ] ORR Summary (`s26_cap_5_orr_local_summary.md`) tem seção apontando explicitamente quais itens foram empurrados para Cap.6.

Se qualquer item crítico desta lista ficar em "não" ou "em aberto sem dono", a S26 **não** está realmente fechada.

---

## 3. Integração com o sistema global de lessons & watchers

### 3.1 Lessons globais vs lessons locais

- **Lessons locais de S26** vivem em `docs/s26_cap_6_1_lessons_learned.md`.  
- **Lessons globais** do projeto vivem em `Leasson Learned so far v1.md` + addenda (`s_4_orr_lessons_learned_sprint_4.md`, etc.).

Regra pós-S26:

- Qualquer learning de S26 que for aplicável **a todas as sprints futuras** (ex.: formato de Cap.4, modelo de ORR, necessidade de runbooks para consoles críticos) deve ser:
  - replicado em forma condensada em `Leasson Learned so far v1.md`;  
  - referenciado no Sprint Playbook da versão atual.

### 3.2 Watchers e enforcement de processo

S26 reforça a ideia de "watchers" — pontos de verificação recorrentes que garantem disciplina de método.

Após S26, pelo menos estes watchers devem ser atualizados:

1. **Watcher Cap.4** — garantir que toda nova sprint use o modelo de Cap.4 da S26 (waves + evidências + tasks ligadas a gates).  
2. **Watcher Cap.5** — garantir que sprints críticas tenham Cap.5 minimamente estruturado (E2E + ORR + runbooks + riscos).  
3. **Watcher Cap.6** — garantir que, ao final de cada sprint, exista bloco de dívidas técnicas e impacto de roadmap equivalente ao 6.2 e 6.3.

Esses watchers podem ser registrados em `inspectah_esquecimentos_e_plano_anti_gaps.md` e ligados a automações (checklists em PRs, templates de docs, etc.).

---

## 4. Ferramentas práticas de Anti-gaps pós-S26

### 4.1 Template para issues de dívida técnica derivadas de S26

Recomendação de template mínimo para issues no tracker associadas a `S26-DT-XXX`:

```text
Título: [S26-DT-00X] <título curto>

Contexto (S26):
- Origem: <capítulo/gate/task>
- Referência: docs/s26_cap_6_2_dividas_tecnicas.md#S26-DT-00X

Descrição resumida:
- ...

Risco:
- Baixo/Médio/Alto — <frase curta>

Gates/domínios afetados:
- ...

Janela sugerida:
- S27–S29 (por exemplo)

Critério de pronto (DoD):
- ... (idealmente vinculado a gates/testes/docs)
```

### 4.2 Template para ajustes de roadmap derivados de S26

Para mudanças em `Roadmap.md` motivadas por S26:

```text
[Roadmap Adjustment] Pós-S26 — <domínio/programa>

Origem:
- S26 Cap.6.3 (seção X)

Mudança proposta:
- Antes: ...
- Depois: ...

Motivação (S26):
- ...

Impacto esperado:
- ...
```

Esses templates evitam que alguém, meses depois, pergunte "por que mudamos isso mesmo?".

### 4.3 Gatilhos automáticos possíveis

Mesmo que automação total venha depois, a S26 já sugere alguns gatilhos simples:

- Ao finalizar `s26_cap_5_orr_local_summary.md`, abrir automaticamente (via script ou hábito) uma issue de "Aplicar Cap.6.4" com checklist do item 2.  
- Ao criar nova sprint S27+, o template de Cap.1 deve perguntar explicitamente: "Quais learnings/dívidas de S26 esta sprint está atacando ou respeitando?".

---

## 5. Critério de "S26 realmente encerrada" no plano Anti-gaps

A S26 só é considerada **encerrada de verdade** quando as condições abaixo forem verdadeiras simultaneamente:

1. **Docs de Cap.1–6 publicados e versionados**  
   - Incluindo todos os blocos, com paths e nomes finais.

2. **ORR executado e registrado**  
   - `s26_cap_5_orr_local_summary.md` existe, com veredito claro (GO/NO-GO) e link para bundle de evidências.

3. **Anti-gaps checklist de S26 (seção 2) em estado OK**  
   - Aprendizados globais migrados para Playbook/LL global ou com tarefa aberta;  
   - Dívidas S26-DT-XXX registradas no tracker;  
   - Atualizações de roadmap aplicadas ou com issue rastreável.

4. **Ponto de ancoragem no Roadmap**  
   - `Roadmap.md` contém, explícita ou implicitamente, o marco "S26 executada" com as principais consequências descritas em 6.3.

Sem isso, S26 ainda está em "estado meta-estável".

---

## 6. Síntese do Bloco 6.4

O Bloco 6.4 transforma o Capítulo 6 em algo com dentes:

- define claramente o que é considerado gap na S26;  
- cria um **checklist de Anti-gaps** para garantir que learnings, dívidas e ajustes de roadmap sejam ancorados em artefatos reais;  
- integra S26 ao sistema global de lessons & watchers (Playbook, `Leasson Learned so far v1.md`, `inspectah_esquecimentos_e_plano_anti_gaps.md`);  
- define critérios objetivos para dizer que a S26 está, de fato, encerrada.

Na prática, isso reduz a chance de a S26 virar "aquela sprint que foi linda no papel, mas ninguém incorporou as lições". Em vez disso, ela passa a ser uma peça fixa do sistema nervoso do Inspectah: método, backlog e roadmap mudam por causa dela, e isso fica documentado.

