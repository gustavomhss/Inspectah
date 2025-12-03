# Sprint 29 — Capítulo 1
## Bloco 4 — Riscos, não‑metas e narrativa de sucesso da S29

Os três primeiros blocos do Capítulo 1 definiram contexto, problema, linguagem e objetivos. Este bloco fecha o capítulo explicitando:

1. Os **principais riscos** da Sprint 29 e as formas de mitigá‑los.
2. As **não‑metas explícitas** (coisas tentadoras, mas fora de escopo nesta sprint).
3. A **narrativa de sucesso**: como queremos conseguir contar a história da S29 quando ela terminar.

A intenção é blindar a sprint contra dois extremos igualmente perigosos: a solução tímida, que "funciona" mas não muda nada, e a solução megalomaníaca, que tenta resolver o E28 inteiro de uma vez e implode no meio do caminho.

---

### 1. Principais riscos da Sprint 29

**Risco 1 — Modelo de fluxo ingênuo ou mal dimensionado**  
Perigo: escolher um modelo de `AgentFlowConfig`/`AgentFlowStep` simples demais (que não aguenta E28.2/E28.3) ou complexo demais (que ninguém consegue entender, testar ou usar).

Mitigação na S29:

- manter o fluxo linear, mas desenhar o modelo pensando em **extensões futuras óbvias** (histórico, versionamento, possíveis branches);
- envolver desde cedo o squad Verdade & Interpretação (Pearl, Stonebraker, Norvig, Percy) na escolha da estrutura mínima (campos, tipos, relação domínio ↔ fluxo);
- validar o modelo contra **cenários concretos** (ex.: domínios "Notícia — Política BR", "Dados econômicos — Brasil"), não só contra casos teóricos.

**Risco 2 — UI bonita, mas desconectada do runtime**  
Perigo: investir energia demais na tela de edição e sair da sprint com uma UI agradável, mas que não impacta o pipeline real — o famoso "configura, mas nada acontece".

Mitigação na S29:

- cravar como objetivo que **pelo menos um pipeline real** use o fluxo configurado;
- tratar a integração `get_agent_flow_for_domain(domain_key)` como parte central da sprint, não como detalhe final;
- priorizar primeiro um caminho funcional (API → adapter → pipeline) e, só depois, polir a experiência da tela.

**Risco 3 — Integração frágil com domínios existentes**  
Perigo: introduzir a configuração de fluxo de agentes e gerar inconsistências com domínios e pipelines que ainda não migraram para o novo modelo.

Mitigação na S29:

- garantir que o adapter de runtime tenha um comportamento de **fallback previsível** (fluxo padrão global + logs/flags quando usado);
- começar por um domínio piloto bem entendido, com dono claro e volume controlado;
- documentar explicitamente quais domínios estão usando o novo modelo e quais ainda dependem da lógica antiga.

**Risco 4 — Invariantes vagas ou mal implementadas**  
Perigo: definir invariantes "no papel" e implementá‑las de forma parcial ou inconsistente, permitindo fluxos perigosos passarem ou bloqueando fluxos válidos sem boa explicação.

Mitigação na S29:

- listar as invariantes da S29 em lugar único (Capítulo 2 e módulo `validator.py`);
- cobrir invariantes com **testes automatizados dedicados**, não apenas testes incidentais;
- garantir mensagens de erro explicativas, que ajudem o operador a ajustar o fluxo em vez de apenas dizer "não".

**Risco 5 — Histórico e auditoria tratados como "detalhe"**  
Perigo: marcar histórico/auditoria como coisa de E28.3 e, com isso, sair da S29 com zero rastro de alterações.

Mitigação na S29:

- definir um **mínimo irredutível de auditoria**: `who`, `when`, `why`, snapshot simples de antes/depois;
- tratar esse mínimo como requisito de DONE da sprint, especialmente para o domínio piloto;
- garantir que os logs estruturados de mudança de fluxo sejam incluídos no bundle de evidência da S29.

**Risco 6 — Escorregar para o E28 inteiro**  
Perigo: tentar incluir histórico completo, UI avançada, branching, mecanismos de aprovação complexos e integração total com todos os domínios de uma vez.

Mitigação na S29:

- usar as **não‑metas** (abaixo) como guardrails explícitos;
- amarrar as decisões de arquitetura a uma visão "E28 em 3 blocos" (E28.1 modelo, E28.2 UI+runtime, E28.3 histórico/governança), respeitando a ordem;
- revisar o escopo a cada gate, garantindo que nada crítico está sendo empurrado para a sprint sem alguém assumir conscientemente esse aumento de escopo.

---

### 2. Não‑metas explícitas da Sprint 29

A S29 abre o E28, mas **não é** o E28 inteiro. Algumas coisas são declaradas como não‑metas, mesmo que sejam desejáveis no futuro:

1. **Nada de fluxos condicionais ou multipercurso**  
   Não haverá, nesta sprint, suporte a:
   - caminhos alternativos dependendo do tipo de item dentro do mesmo domínio;
   - ramos de fluxo com condições complexas ("se X então passa por dois debunkers, se Y passa por um só");
   - loops ou ciclos de reanálise automática.

   O fluxo da S29 é linear. A complexidade de lógica condicional ficará para versões posteriores.

2. **Nada de editor visual avançado (grafo rico, minimapas, zoom)**  
   A UI de S29 é baseada em **lista ordenada**. Não haverá:
   - canvas visual com nós conectados por linhas;
   - drag & drop sofisticado com snapping e múltiplas trilhas;
   - representações gráficas complexas.

   O objetivo é clareza e funcionalidade, não espetáculo visual.

3. **Nada de histórico/rollback completo de versões de fluxo**  
   A sprint implementa rastro mínimo de mudanças, mas não entrega:
   - timeline rica com todas as versões detalhadas;
   - diff visual entre versões de fluxo;
   - botão de rollback automático para qualquer versão anterior.

   Esses recursos são parte natural de E28.3 e de sprints de governança.

4. **Nada de processos de aprovação humana complexos**  
   Não haverá, nesta sprint:
   - workflow de aprovação em múltiplos níveis para alterações de fluxo;
   - integrações com sistemas externos de permissão/approvals;
   - exigência de reviews formais para cada alteração.

   A S29 foca em construir a infraestrutura de fluxo. Gate de aprovação humano entra em sprints focadas em governança.

5. **Nada de acoplamento direto ao Sistema de Blocos / on‑chain**  
   As decisões tomadas pelo fluxo podem futuramente ser ancoradas em blocos, mas a S29 não liga diretamente
   a configuração de fluxo aos mecanismos on‑chain. A ponte entre fluxo de agentes e Sistema de Blocos permanece responsabilidade de outros épicos.

6. **Nada de migração total de todos os domínios existentes**  
   A sprint não busca portar todos os domínios para o novo modelo de fluxo. Ela busca provar o modelo com
   pelo menos um domínio piloto bem escolhido. A migração em massa é feita de forma incremental em sprints posteriores.

Essas não‑metas não são fraquezas; são **decisões conscientes de foco** para garantir que a sprint entregue algo sólido e extensível, em vez de um castelo incompleto.

---

### 3. Narrativa de sucesso da Sprint 29

Se tudo der certo, ao final da S29 a equipe deve ser capaz de contar a história da sprint mais ou menos assim:

> "Até a Sprint 28, o fluxo de agentes do Inspectah vivia escondido em código. A S29 pegou esse cérebro e colocou na mesa: hoje, para domínios pilotos como ‘Notícia — Política BR’, existe um fluxo de agentes configurável, visível em UI, com invariantes claras, rastro de mudanças e integração real com o pipeline de ingestão. Alterar a coreografia entre `INTERPRETER`, `CLASSIFIER`, `DEBUNKER` e `DECISION_MAKER` deixou de ser um PR e passou a ser uma operação guiada pelo console."

Em termos concretos, a narrativa de sucesso inclui:

- **Para produto/ops**:
  - "Eu consigo ver, em uma tela só, como o domínio X é processado pelo sistema".
  - "Eu consigo ajustar esse fluxo dentro de limites seguros, sem depender de deploy".

- **Para engenharia**:
  - "O modelo de fluxo que implementamos é simples, mas comporta as extensões que vamos precisar em E28.2/E28.3".
  - "A integração com o runtime está clara e isolada em um adapter; migrar novos domínios será repetitivo, não reinvenção".

- **Para governança/auditoria**:
  - "Sabemos quem mexeu no fluxo de um domínio sensível, quando mexeu e com qual justificativa".
  - "Estamos um passo mais perto de explicar não só *o que* o sistema decidiu, mas *como* ele chegou lá".

Se essa narrativa for verdadeira, a Sprint 29 terá cumprido seu papel: o E28 deixa de ser uma boa ideia e passa a ser uma **capacidade real** do Inspectah, em versão v1, pronta para ser ampliada por S30 e pelas sprints de governança.

---

### 4. Amarração final do Capítulo 1

O Bloco 4 fecha o Capítulo 1 da Sprint 29 com três âncoras:

1. A clareza de que a S29 resolve um problema estrutural do projeto (fluxo de agentes invisível, rígido e ingovernável).
2. A consciência dos principais riscos e das armadilhas de escopo, e como evitá‑los.
3. Uma narrativa de sucesso concreta, que vai orientar as decisões dos capítulos seguintes.

A partir daqui, o Capítulo 2 pode transformar esses elementos em **gates, métricas, scorecards e critérios formais de GO/NO‑GO**, enquanto o Capítulo 3 desenha a arquitetura e o filemap que tornam essa visão implementável.

A S29 deixa de ser um item abstrato no roadmap e passa a ter um **contrato conceitual claro**: abrir o E28 com uma fundação sólida para fluxos de agentes configuráveis por domínio, sem tentar abraçar o mundo em uma sprint, mas também sem entregar algo tímido demais para fazer diferença.

