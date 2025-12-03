# Sprint 29 — Capítulo 5
## Bloco 3 — Estado do produto Inspectah após a Sprint 29

Este Bloco 3 desce do nível de "formato de ORR" (Bloco 2) para o nível de **conteúdo de produto**: o que, concretamente, muda no Inspectah depois que a S29 foi executada com todos os gates em PASS.

O foco aqui é descrever o estado do produto em linguagem de produto e operação, não em linguagem de implementação:

- o que passou a existir;  
- o que deixou de ser gambiarras espalhadas;  
- o que um operador/admin pode fazer agora que não podia antes;  
- em que escopo isso é recomendado (piloto vs amplo).

Estas descrições alimentam diretamente as seções 1, 2, 5 e 6 do `docs/sprint_29_orr_summary.md`.

---

### 1. Capacidade central liberada pela S29

A Sprint 29 introduz no Inspectah uma capacidade central nova, que pode ser descrita assim:

> "Agora o Inspectah permite configurar, por domínio, **fluxos explícitos de agentes** (INTERPRETER, CLASSIFIER, DEBUNKER, DECISION_MAKER, etc.), armazenados como entidade de domínio, editáveis via UI de admin e consumidos pelo pipeline de runtime."

Antes da S29, o caminho de uma notícia ou peça de informação pelos agentes era, na prática:

- codificado via lógica fixa no código (if/else, grafos implícitos);  
- pouco visível e nada editável por operadores;  
- difícil de auditar e de explicar para alguém de fora.

Depois da S29, pelo menos para domínios piloto, passa a existir:

- uma tabela/configuração formal de fluxo por domínio;  
- um editor gráfico (UI admin) que permite ver e alterar essa sequência;  
- um runtime que consulta essa configuração na hora de processar cada item.

É a diferença entre "o código decide" e "o fluxo está escrito e configurável em um lugar só".

---

### 2. O que muda para o operador/admin

Do ponto de vista de quem opera o Inspectah, as mudanças práticas são:

1. **Nova área no console admin: Fluxos de agentes**  
   - O menu admin passa a ter uma entrada (ex.: "Fluxos de agentes").  
   - Ao clicar, o operador vê uma listagem de domínios e o status de fluxo (configurado / não configurado / desatualizado).

2. **Editor de fluxo por domínio**  
   - Para um domínio piloto (por exemplo, `news.politics.br`), o operador consegue:  
     - ver a sequência atual de papéis (INTERPRETER → CLASSIFIER → DEBUNKER → DECISION_MAKER, etc.);  
     - adicionar passos intermediários (por exemplo, mais um CLASSIFIER especializado);  
     - remover passos desnecessários;  
     - reordenar passos para alterar a ordem de execução;  
     - ajustar parâmetros de cada agente (na medida em que a v1 suporte isso).

3. **Justificativa obrigatória para mudanças**  
   - Nenhuma alteração de fluxo é salva em silêncio: o operador precisa registrar uma justificativa (`change_reason`).  
   - Essa justificativa fica ligada aos metadados de auditoria (`updated_by`, `updated_at`).

4. **Feedback imediato de erros de configuração**  
   - Se a sequência violar invariantes (por exemplo, `DECISION_MAKER` no meio, ausência de DEBUNKER em domínio sensível), o sistema não deixa salvar;  
   - a UI exibe mensagens claras, baseadas nos códigos de erro (`DECISION_MAKER_NOT_LAST`, `MISSING_REQUIRED_ROLE`, etc.).

Na prática, S29 muda a relação do operador com o sistema: ele deixa de pedir "alguém mexe no código para trocar a ordem dos agentes?" e passa a ter um console dedicado para esse tipo de ajuste.

---

### 3. O que muda para o pipeline e runtime

Do lado do pipeline de ingestão/verdade, o efeito da S29 pode ser descrito assim:

1. **Consulta dinâmica de fluxo por domínio**  
   - Para cada item que entra no pipeline (por exemplo, uma notícia de um feed `news.politics.br`), o runtime pergunta:  
     - "Qual é o fluxo configurado para este domínio?"  
   - A resposta vem do `AgentFlowConfig` correspondente (ou de um fluxo de fallback se não houver um específico).

2. **Execução na ordem configurada**  
   - Em vez de seguir uma ordem fixa embutida no código, o pipeline percorre a lista de passos do fluxo configurado;  
   - para cada passo, aciona o agente correspondente (INTERPRETER, CLASSIFIER, DEBUNKER, etc.) usando seus parâmetros.

3. **Logs estruturados de execução de fluxo**  
   - O runtime registra logs do tipo:  
     - domínio, flow_id, sequência de papéis executados;  
     - indicador se houve uso de fallback;  
     - possíveis falhas ou timeouts em agentes específicos.  
   - Esses logs passam a ser fonte primária de evidência de que "o fluxo configurado está de fato sendo respeitado".

4. **Separação entre configuração e implementação de agentes**  
   - A forma como cada agente (Debunker, Classifier, etc.) funciona internamente pode continuar evoluindo;  
   - a sequência e as combinações de papéis deixam de depender dessa implementação e passam a ser declaradas via fluxo configurável.

Isso vai ser fundamental para as sprints futuras de E28 (versionamento, branching, métricas), mas já na S29 a diferença é nítida: o caminho de processamento deixa de ser uma caixa preta monolítica.

---

### 4. Domínios piloto e escopo recomendado de uso

A S29 não tenta resolver o problema de "configurar fluxos para todos os domínios do planeta". O estado pós-sprint é, propositalmente, mais contido.

Do ponto de vista de produto, o ORR deve deixar claro algo como:

1. **Domínios piloto habilitados**  
   - Uma lista curta de domínios (ou famílias de domínios) para os quais:  
     - o fluxo v1 foi configurado;  
     - a combinação de agentes faz sentido;  
     - o time se sente confortável em operar com configuração editável.

2. **Ambiente de operação recomendado**  
   - Se a feature for estreada em staging ou em produção com "feature flag", isso deve ser dito;  
   - se o uso em produção for limitado a certos casos, esse recorte também deve ser explícito.

3. **Política de alterações durante o piloto**  
   - Quem está autorizado a alterar fluxos durante o piloto (por papel, não por nome);  
   - se há necessidade de dupla checagem manual para domínios mais sensíveis;  
   - se existe janela de manutenção recomendada para mexer em fluxos (por exemplo, "não alterar fluxo durante grandes eventos noticiosos").

Estado do produto pós-S29, portanto, não é "fluxos livres para todos"; é **fluxos configuráveis sob disciplina de piloto**.

---

### 5. O que ainda não está incluso na v1 de fluxo de agentes

Parte importante do estado do produto é registrar o que **não** está incluso. Isso alimenta seções de "limitações" e "riscos" do ORR.

Itens que a S29 **não pretende** entregar (mas prepara terreno):

1. **Versionamento avançado de fluxos**  
   - Nesta v1, há uma configuração ativa por domínio, com histórico implícito via auditoria (`updated_at`, `updated_by`, `change_reason`), mas:  
   - não há ainda conceito formal de "versão de fluxo" com rótulos (v1, v2, v3), estados (draft/active/deprecated) ou rollback automático.

2. **Branching e fluxos condicionais complexos**  
   - O fluxo v1 é essencialmente linear (lista ordenada de passos);  
   - condições do tipo "se o item for sobre X, vá por este ramo" ainda não são representadas no domínio;
   - decisões condicionais ainda dependem de lógica interna dos agentes.

3. **Aprovações e governance multiusuário**  
   - A v1 exige `change_reason` e registra o usuário que alterou, mas:  
   - não há workflow de approvals (ex.: dois admins precisam aprovar mudanças em domínios sensíveis);  
   - não há bloqueio baseado em perfis (além do fato de ser área admin).

4. **Métricas consolidadas de fluxo**  
   - Logs de runtime começam a registrar uso de fluxo, mas não há ainda:  
     - painel consolidado de quantos itens passaram por qual fluxo;  
     - tempos médios por agente;  
     - taxa de erro por papel.

5. **UI avançada de visualização**  
   - O editor v1 é focado em lista ordenada, com controles básicos (adicionar, remover, mover, editar);  
   - não há ainda visualizações de grafo, simulações "what-if" ou comparações visuais de fluxos entre domínios.

Registrar explicitamente esses "não inclusos" ajuda a:

- alinhar expectativas com stakeholders;  
- evitar a sensação de "achei que já vinha tudo";  
- preparar, com clareza, a pauta de E28.2/E28.3.

---

### 6. Benefícios concretos para o Programa 1

Dentro do Programa 1, o estado pós-S29 traz alguns benefícios que vão além da sprint em si:

1. **Fundação para camadas de verdade e debunking (S23–S25)**  
   - Os papéis de agentes (INTERPRETER, CLASSIFIER, DEBUNKER, DECISION_MAKER) deixam de ser uma abstração vaga e passam a integrar um fluxo configurável;  
   - isso facilita a conexão futura entre fluxos de agentes e políticas de promoção de verdade/fato.

2. **Redução de acoplamento rígido no pipeline**  
   - Ao mover a ordem dos agentes para uma camada de configuração, o pipeline fica mais flexível para experimentos:  
     - ex.: testar dois fluxos de debunking diferentes em domínios distintos sem reescrever o core.

3. **Melhor terreno para observabilidade e tuning**  
   - Logs estruturados de fluxo abrem espaço para, em sprints futuras, medir e ajustar o pipeline com base em dados (quais fluxos produzem melhores decisões, onde há gargalos, etc.).

4. **Coerência com a visão "System of Blocks" / Truth-DB**  
   - O fluxo de agentes passa a ser mais um "bloco" configurável do sistema, com identidade, evidência e trilha de auditoria;  
   - isso conversa diretamente com a filosofia geral do Inspectah de tratar peças-chave como entidades auditáveis, não como gambiarras escondidas.

---

### 7. Resumo do estado do produto pós-S29

Resumindo em termos de produto:

- **O que o Inspectah ganha:**  
  - fluxo de agentes configurável por domínio (v1), com UI de admin, API limpa e integração inicial com runtime;  
  - trilha de auditoria mínima para alterações de fluxo;  
  - logs estruturados de execução de fluxo em domínios piloto.

- **O que continua faltando (assumido para futuras sprints):**  
  - versionamento formal e approvals de fluxo;  
  - branching/condicionais complexos;  
  - métricas consolidadas de fluxo;  
  - UI avançada para visualização e simulação.

- **Como isso se encaixa no Programa 1:**  
  - S29 abre o Épico E28 e entrega a fundação configurável de fluxos de agentes, conectando UI, domínio, runtime e evidências;  
  - as próximas sprints de E28 vão, idealmente, construir em cima dessa fundação sem precisar reabrir essas bases.

Esse retrato é o que deve aparecer, sintetizado, nas seções de "Resumo executivo", "Impacto no produto" e "Riscos/limitações" do ORR da S29. A partir daqui, o Bloco 4 do Capítulo 5 foca em mapear explicitamente a integração entre S29, o Épico E28 e o roadmap de próximas sprints.

