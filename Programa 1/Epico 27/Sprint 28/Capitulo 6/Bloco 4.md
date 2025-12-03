# Inspectah — Sprint 28
## Capítulo 6 — Bloco 4
### Roadmap, Anti-gaps & Recomendações para as Próximas Sprints (E27.2, E27.3 e além)

---

### 6.4.1 Objetivo do Bloco 4

Este Bloco 4 fecha o Capítulo 6 transformando:
- as **lessons learned** (Bloco 2),
- a **dívida técnica consolidada e priorizada** (Bloco 3)

en três saídas práticas:

1. Um **ajuste explícito de roadmap** para o Épico E27 (E27.2, E27.3 e backlog de longo prazo).  
2. Um conjunto de **anti-gaps** (regras práticas para evitar buracos de especificação, execução e governança nas próximas sprints).  
3. Um **pacote de recomendações concretas** para squads, Codex e Conselho na hora de planejar e revisar as próximas sprints.

A ideia é que, terminado este bloco, qualquer pessoa consiga responder:  
“Dado o que aprendemos em S28, o que muda no plano daqui para frente e como evitamos repetir os mesmos erros?”

---

### 6.4.2 Roadmap ajustado para o Épico E27 (após a Sprint 28)

A partir das decisões e aprendizados da Sprint 28, o Épico E27 passa a ser visto em três camadas:

1. **E27.1 — Núcleo duro de CRUD & ON/OFF de fonte**  
   - Já entregue em S28.  
   - Define o piso operacional mínimo:  
     - entidade `Source` bem formada,  
     - Admin API `/admin/sources` como contrato canônico,  
     - console de fontes v2 com fluxos A–D,  
     - ingestão 2.0 obedecendo `mode` + `state`.

2. **E27.2 — Fundação de auditabilidade, validade e visibilidade (Sprint 29)**  
   S28 mostra que E27.2 deve focar em três eixos estruturantes:
   - **Auditoria**: `SourceActionLog` (D-28-AUD-1) como base inegociável.  
   - **Validações por tipo**: fase 1 de D-28-VAL-1 para tipos de fonte mais críticos.  
   - **Observabilidade**: D-28-OBS-1, introduzindo métricas por fonte/estado/mode.

   Resultado esperado de E27.2:
   - Cada ação relevante em fonte gera um log estruturado.  
   - Configurações absurdamente inválidas são bloqueadas já no cadastro.  
   - Operação consegue enxergar, em nível de métrica, quais fontes dão mais problema.

3. **E27.3 — Polimento avançado de operação e governança mínima (Sprint 30)**  
   E27.3, à luz de S28, ganha o papel de refinar UX e governança:
   - **UX de operação**:  
     - timeline de ações por fonte no console (D-28-AUD-2),  
     - wizards para fontes complexas (D-28-VAL-2).  
   - **Cockpit de fontes**:  
     - dashboards específicos de operação (D-28-OBS-2).  
   - **Governança mínima**:  
     - primeira camada sistêmica para fontes críticas (D-28-GOV-1).

   Resultado esperado de E27.3:
   - Console de fontes deixa de ser só CRUD e se torna painel de operação.  
   - Decisões em fontes de alta criticidade têm apoio sistêmico, não só processo humano.

Além disso, S28 projeta alguns tópicos de **longo prazo** (B-LONG-*), como:
- políticas automáticas de ON/OFF baseadas em comportamento,  
- integração profunda com Debunker & Comitês de Verdade,  
- mapeamento formal entre fontes e temas/casos.

Esses itens não entram em E27.2/E27.3 como obrigatório, mas já estão mapeados como continuação natural.

---

### 6.4.3 Anti-gaps de especificação, execução e governança

A partir dos erros, quase-erros e fricções percebidas em S28, este bloco registra anti-gaps — lembretes explícitos para as próximas sprints.

#### 6.4.3.1 Anti-gaps de especificação

1. **Sempre incluir glossário mínimo no Cap.1 quando surgirem novos conceitos de domínio**  
   - `mode`, `state`, `criticality`, etc., devem estar textualmente definidos.  
   - Evita divergência entre o que o PO, o backend e a operação entendem.

2. **Garantir que todo estado-alvo crítico tenha pelo menos um cenário E2E em Cap.2/Cap.5**  
   - Se um estado-alvo não é exercitado em nenhum cenário E2E, ele tende a ficar mal implementado ou mal testado.

3. **Separar de forma clara Cap.5 (riscos/backlog imediato) de Cap.6 (aprendizado/roadmap)**  
   - Cap.5: inventário e encaminhamento de riscos/dívidas.  
   - Cap.6: priorização, impacto em roadmap e recomendações de processo.

4. **Fixar convenções de IDs desde o começo da sprint**  
   - Não deixar para "inventar" IDs no final.  
   - Começar Cap.2 e Cap.5 já numerando riscos (R-XX-*), dívidas (D-XX-*) e backlog (B-epico.*).

---

#### 6.4.3.2 Anti-gaps de execução

1. **Gates de regressão (estilo G5) são obrigatórios em sprints que mexem em componentes centrais**  
   - Não confiar apenas em testes unitários locais.  
   - Explicitar no Cap.2 quais sprints legadas não podem ser quebradas.

2. **Cap.5 e Cap.6 precisam entrar no plano de execução (Cap.4)**  
   - Incluir tasks específicas de redação e revisão destes capítulos.  
   - Não deixar learnings e dívidas para um "pós-mortem" informal.

3. **Evitar que Codex trabalhe com Cap.1–3 instáveis**  
   - Só liberar prompts de execução pesada para Codex depois de Cap.1–3 estarem minimamente congelados.  
   - Coerente com LL-PR1: ordem Playbook não é decorativa.

4. **Usar IDs de riscos/dívidas/backlog em commits, PRs e tickets**  
   - Ex.: `feat: implementar validação RSS (D-28-VAL-1, B-27.2-2)`.  
   - Facilita rastrear, no futuro, como cada dívida foi quitada.

---

#### 6.4.3.3 Anti-gaps de governança

1. **Formalizar política de uso da Admin API como único caminho de mutação em produção**  
   - Registrar isso em documentos internos e, quando possível, em controles de permissão.  
   - Sempre que for necessário mexer direto em banco, registrar exceção via `SourceActionLog` ou equivalente.

2. **Definir owners para fontes críticas**  
   - E27.2/E27.3 devem aproveitar o campo `criticality` para associar responsáveis claros a grupos de fontes.  
   - Ajuda a responder "quem cuida disso?" quando der problema.

3. **Envolver cedo o squad Verdade & Interpretação em discussões de auditoria**  
   - `SourceActionLog` e políticas de aprovação de fontes críticas são o lugar natural onde verdade/fato e operação se encontram.  
   - Antecipar esse diálogo reduz retrabalho quando Sistema de Blocos entrar em jogo.

---

### 6.4.4 Recomendações concretas para E27.2 e E27.3

#### 6.4.4.1 Para E27.2 (Sprint 29)

Recomenda-se que E27.2 tenha, já no Cap.1/Cap.2:

- **Objetivos claros**:  
  - "Ter `SourceActionLog` funcional para operações principais".  
  - "Bloquear configurações absurdas via validações por tipo para ao menos 1–2 tipos críticos".  
  - "Expor métricas mínimas por fonte/estado/mode".

- **Gates dedicados**:  
  - Gx-AUD: validar gravação de logs em `SourceActionLog` em cenários essenciais.  
  - Gx-VAL: validar rejeição de fontes claramente inválidas por tipo.  
  - Gx-OBS: validar presença de séries de métricas em ambiente de teste.

- **Involvimento de squads**:  
  - Backend + Ingestão + Observabilidade + Produto, com apoio pontual de Verdade & Interpretação para modelar campos de auditoria.

#### 6.4.4.2 Para E27.3 (Sprint 30)

Recomenda-se que E27.3 se apresente explicitamente como sprint de **polimento de operação e governança mínima**:

- **Objetivos claros**:  
  - "Fornecer timeline de ações de fonte utilizável para investigações".  
  - "Reduzir atrito de cadastro em fontes complexas via wizards".  
  - "Dar ao time de operação um painel de saúde de fontes".  
  - "Evitar que fontes críticas sejam desativadas sem barreira sistêmica mínima".

- **Gates dedicados**:  
  - Gx-UI-HIST: exercício E2E de timeline.  
  - Gx-WIZ: exercício de wizard com caso real.  
  - Gx-DASH: verificação de dashboards mínimos em ambiente de teste.  
  - Gx-GOV: cenários de aprovação/bloqueio em fontes críticas.

- **Involvimento de squads**:  
  - Frontend/UX + Backend + Governança + Observabilidade, com avaliação final do Conselho (especialmente Pearl, Stonebraker, Norvig e Percy) sobre aderência a princípios de verdade, dados e agentes.

---

### 6.4.5 Fechamento — Como S28 eleva a linha de base do Programa 1

Com o Capítulo 6 e este Bloco 4, fica claro que S28:

1. **Não é apenas sobre ligar e desligar fontes**  
   É sobre transformar fontes em uma entidade operada com disciplina:  
   - contrato de API claro,  
   - UI funcional,  
   - ingestão obediente,  
   - e um plano concreto para auditabilidade, validação e observabilidade.

2. **Reposiciona E27.2/E27.3 como degraus bem definidos, não como "sprints de melhorias" vagas**  
   - E27.2: fundação (log, validação, métricas).  
   - E27.3: operação refinada (timeline, wizards, dashboards, governança mínima).

3. **Produz anti-gaps que fortalecem o Playbook e o próprio projeto Inspectah**  
   - Glossários obrigatórios para novos conceitos.  
   - Cap.5/Cap.6 como parte da definição de pronto.  
   - IDs estáveis e gates nomeados como linguagem comum entre spec, código e CI.

4. **Deixa um trilho claro para sprints futuras do Programa 1**  
   - O que S28 fez com `Source`, futuras sprints deverão fazer com `Case`, `Theme`, `Evidence`, `Block`, etc.:  
     modelo sólido, operações claras, auditabilidade, métricas e governança desde cedo.

Assim, o Bloco 4 encerra o Capítulo 6 e a documentação da Sprint 28, garantindo que o esforço investido nesta sprint continue rendendo dividendos cognitivos e estruturais nas próximas etapas do Épico E27 e do Programa 1 como um todo.

