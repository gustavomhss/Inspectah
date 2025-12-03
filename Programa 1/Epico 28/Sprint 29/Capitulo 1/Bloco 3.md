# Sprint 29 — Capítulo 1
## Bloco 3 — Linguagem comum, objetivos de produto e premissas da S29

Com o contexto (Bloco 1) e o problema (Bloco 2) devidamente dissecados, este bloco fecha o Capítulo 1 definindo três coisas:

1. A **linguagem comum** que a S29 vai usar para falar de domínios, fluxos e agentes.  
2. Os **objetivos de produto** da sprint, isto é, o que precisa existir para que o E28 comece a ser real na prática.  
3. As **premissas e recortes de escopo** que mantêm a sprint ambiciosa, porém executável.

A ideia é que, ao final deste bloco, qualquer pessoa da equipe consiga responder sem gaguejar a pergunta: "O que exatamente a Sprint 29 está tentando colocar de pé?".

---

### 1. Linguagem comum da Sprint 29

Para reduzir ambiguidade e ruído, a S29 fixa um pequeno glossário operacional.

**Domínio**  
Um domínio é uma "caixa" de tratamento de itens que compartilham:

- um tipo de conteúdo (notícia, dado estatístico, documento oficial, sinal de mercado etc.);
- um recorte temático e/ou geográfico (política brasileira, economia global, saúde pública BR);
- políticas de tratamento e critérios de verdade que diferem de outros domínios.

Cada domínio é identificado por uma **chave estável** (`domain_key`), usada em ingestão, classificação e, a partir da S29, nos fluxos de agentes.

**Fluxo de agentes (agent flow)**  
É a sequência ordenada de papéis de agentes que processam um item pertencente a um domínio. Em S29, o fluxo é **estritamente linear**: passo 1, passo 2, passo 3, sem ramificações.

Exemplo simplificado para um domínio sensível:

- passo 1: `INTERPRETER`;  
- passo 2: `CLASSIFIER`;  
- passo 3: `ANALYST`;  
- passo 4: `DEBUNKER`;  
- passo 5: `DECISION_MAKER`.

Outros papéis podem existir (por exemplo, `EVIDENCE_MINER`, `SUMMARY_WRITER`), mas o conceito central permanece: o fluxo é a **coreografia** entre esses papéis.

**Papel de agente (agent role)**  
É a função conceitual desempenhada por um agente em um passo do fluxo. A S29 não inventa papéis novos; ela consome o catálogo que já vem sendo desenhado nas sprints de Verdade & Interpretação (S23–S25). Alguns exemplos típicos:

- `INTERPRETER`: entender o texto bruto, extrair entidades, contexto, relações;
- `CLASSIFIER`: atribuir categorias, labels internas, tipos de item;
- `ANALYST`: elaborar análises mais profundas, relações causais, sínteses interpretativas;
- `DEBUNKER`: testar hipóteses, procurar contradições, checar contra evidências externas;
- `DECISION_MAKER`: definir o estado final do item (fato, falso, controverso, inconclusivo etc.).

O fluxo trabalha com **papéis**, não com instâncias específicas de modelo/agente. O acoplamento a implementações concretas (por exemplo, qual conjunto de prompts/comitês implementa o papel de `DEBUNKER`) fica em camadas abaixo.

**Configuração de fluxo (AgentFlowConfig)**  
É o objeto de domínio que descreve o fluxo de agentes associado a um domínio. Em S29, esse objeto inclui:

- `domain_key`: chave do domínio;
- lista de passos (`AgentFlowStep`), cada um com posição, papel e parâmetros básicos;
- metadados de auditoria: quem criou/alterou, quando, com qual justificativa.

Esse objeto é guardado em banco, exposto via API e manipulado pela UI de admin.

**Passo de fluxo (AgentFlowStep)**  
É um elemento da lista que compõe o fluxo. Cada passo contém:

- `position`: a posição no fluxo (1, 2, 3…);
- `agent_role`: o papel do agente naquele ponto;
- `params`: parâmetros adicionais (por exemplo, qual comitê usar, thresholds, flags de modo estrito/relaxado).

**Invariantes de fluxo**  
São regras globais que determinam se um fluxo é válido. Em S29, elas incluem pelo menos:

- um fluxo não pode ser vazio;
- o primeiro passo deve ser um papel permitido como entrada (por exemplo, `INTERPRETER` ou equivalente);
- determinados domínios exigem presença de certos papéis (por exemplo, domínios sensíveis sempre precisam passar por `DEBUNKER` antes do `DECISION_MAKER`);
- papéis como `DECISION_MAKER` não podem aparecer em posições intermediárias arbitrárias;
- a lista de passos não pode ter posições duplicadas ou inconsistentes.

Essas invariantes são aplicadas tanto na API quanto na UI e cobertas por testes.

**UI de fluxo de agentes**  
É a tela do console admin onde o operador:

- escolhe um domínio;
- vê o fluxo atual como uma lista ordenada de passos;
- adiciona, remove ou reordena passos dentro das regras permitidas;
- salva alterações com uma justificativa textual.

A versão de S29 é **linear e minimalista**, porém funcional: o foco é clareza sobre o que o fluxo é e como ele impacta o runtime.

---

### 2. Objetivos de produto da Sprint 29

Do ponto de vista de produto (não de scripts/gates), a Sprint 29 será considerada bem-sucedida se, ao final do ciclo, o seguinte cenário for verdadeiro em ambiente de desenvolvimento.

**1. Um domínio real operando com fluxo configurado**  
Pelo menos um domínio relevante, por exemplo "Notícia — Política BR", deve estar sendo processado assim:

- seu fluxo de agentes está definido via `AgentFlowConfig` em banco;
- o operador consegue ver esse fluxo na UI de admin;
- o pipeline de ingestão consulta esse fluxo em tempo de execução e o respeita.

Ou seja, o caminho do dado até a decisão passa explicitamente pelo fluxo configurado, e não por regras escondidas no código.

**2. Operador com alavanca real sobre o fluxo**  
Um operador autorizado deve ser capaz de:

- abrir o console;
- navegar até a seção de fluxos;
- entender visualmente a sequência de papéis de um domínio;
- fazer uma alteração simples (por exemplo, inserir um `DEBUNKER` adicional ou reordenar dois passos);
- salvar a alteração com justificativa;
- ver essa mudança refletida em execuções subsequentes do pipeline.

Esse ciclo precisa ser **previsível e seguro**: a alteração não pode quebrar o sistema silenciosamente.

**3. Fluxos inválidos são bloqueados com explicação**  
Tentativas de criar ou salvar fluxos inválidos devem ser rejeitadas de forma consistente, tanto via API quanto via UI, com mensagens claras do tipo:

- "Fluxo não pode ser vazio";
- "Domínio X exige um passo DEBUNKER antes do DECISION_MAKER";
- "DECISION_MAKER só pode aparecer na última posição do fluxo".

Aqui, não basta lançar um erro genérico; a experiência precisa educar o operador sobre **qual invariantes foi violada**.

**4. Alterações deixam rastro mínimo auditável**  
Cada mudança de fluxo deve registrar pelo menos:

- quem fez a alteração (quando essa informação estiver disponível);
- quando a alteração foi feita;
- qual foi a justificativa textual fornecida;
- um snapshot resumido do fluxo antes e depois.

Mesmo que o histórico completo e ferramentas de diff visual fiquem para sprints futuras, a S29 precisa sair do zero para um patamar em que o sistema possa responder, de forma honesta: "Sim, sabemos quem mexeu no fluxo deste domínio e quando".

**5. Conselho técnico enxerga um modelo sólido e extensível**  
Por fim, a S29 deve entregar não só telas e endpoints, mas um **modelo de fluxo** que:

- faça sentido conceitual para o squad Verdade & Interpretação;
- seja compatível com futuras extensões (UI avançada, histórico rico, fluxos condicionais);
- não precise ser refeito do zero em E28.2/E28.3.

O teste implícito aqui é: se, ao terminar S29, o conselho achar que o modelo está "meia-boca" ou "pouco extensível", a sprint falhou, mesmo se todos os scripts estiverem verdes.

---

### 3. Premissas e recortes de escopo da S29

Para evitar que a Sprint 29 tente resolver o E28 inteiro de uma vez (e morra abraçada ao escopo), algumas premissas e cortes são assumidos desde o Capítulo 1.

**Premissa 1 — Fluxo estritamente linear nesta versão**  
S29 trabalha apenas com fluxos lineares. Nada de:

- grafos sofisticados;
- branching condicional por tipo de item dentro do mesmo domínio;
- loops ou rotas alternativas.

Esses recursos são desejáveis em versões futuras, mas aqui seriam um multiplicador de complexidade que atrapalha o objetivo principal: tirar o fluxo de dentro do código e torná-lo configurável.

**Premissa 2 — Reutilização do catálogo de papéis existente**  
A sprint não reinventa o universo de papéis de agentes. Ela consome o catálogo já definido ou em definição pelas sprints de agentes e governança (S23–S25). Se surgir a necessidade de novos papéis, a regra é:

- o catálogo é discutido no contexto de Verdade & Interpretação;  
- a S29 apenas expõe esses papéis no editor de fluxo.

**Premissa 3 — Integração mínima, mas real, com o runtime**  
Seria tentador empurrar a integração com o runtime para "depois", mas isso invalidaria metade do valor da sprint. Por outro lado, tentar migrar todos os pipelines de uma vez também seria inviável.

A regra adotada é:

- pelo menos um pipeline representativo deve usar o fluxo configurado;
- os demais podem continuar no modelo antigo temporariamente, desde que a arquitetura permita migrá-los de forma incremental em sprints posteriores.

**Premissa 4 — Nada de Sistema de Blocos ou blockchain aqui dentro**  
S29 não toca em ancoragem on-chain, Merkle trees, reputação de blocos ou qualquer parte do Sistema de Blocos. O foco da sprint é **fluxo de agentes**. A ligação entre decisões de fluxo e ancoragens em verdade/fato continua responsabilidade de outras sprints e da Fase 2.

**Premissa 5 — Segurança por invariantes, não por burocracia**  
A sprint não deve responder ao medo de fluxos errados com um excesso de travas burocráticas (como exigir dez cliques de confirmação para qualquer mudança). Em vez disso, a proteção vem de:

- invariantes bem definidas e testadas;
- mensagens de erro esclarecedoras;
- rastro mínimo de auditoria.

Se, no futuro, domínios específicos exigirem fluxos de aprovação mais formais (por exemplo, dois aprovadores humanos para alterar fluxos de alto impacto), isso será tratado em E28.3 e em sprints de governança.

---

### 4. Fechamento do Capítulo 1

Com este bloco, o Capítulo 1 da Sprint 29 fica completo:

- o **Bloco 1** posicionou a sprint no contexto geral do Inspectah e do Programa 1;
- o **Bloco 2** destrinchou o problema central que S29 precisa enfrentar;
- o **Bloco 3** fixou a linguagem comum, os objetivos de produto e as premissas que guiam as decisões de escopo.

A partir daqui, os próximos capítulos da sprint (Gates e métricas, Arquitetura e filemap, Execução e evidências) podem ser escritos com uma base conceitual sólida. Em vez de "fazer tela e endpoint", a Sprint 29 passa a ser explicitamente sobre **transformar o fluxo de agentes em um ativo de configuração governável**, dando ao Inspectah a sua primeira versão real de cérebro ajustável por domínio.

