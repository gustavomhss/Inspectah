# Sprint 29 — Capítulo 1
# Contexto, Problemas e Visão Geral

## 1. Contexto geral do Inspectah e posição da S29 no Programa 1

O Inspectah está saindo da fase de "apenas coletar dados" para a fase em que **a maneira como os dados são interpretados, verificados e promovidos a verdade** passa a ser um produto em si.

Até aqui, as sprints anteriores construíram camadas fundamentais:

- S21 consolidou o **Console de Fontes**, onde o operador cadastra e gerencia fontes de entrada (especialmente notícias e dados oficiais).  
- S22 evoluiu o pipeline de **Ingestão 2.0**, tornando o fluxo de entrada de dados mais previsível, observável e resiliente.  
- S23, S24 e S25 começaram a definir o universo de **agentes, debunkers, comitês e governança de verdade**, desenhando a arquitetura conceitual de como o sistema pensa, duvida, checa e decide.  
- S26 reforçou a camada de **admin e design system**, preparando o terreno para consoles mais ricos, coerentes e escaláveis.

O **Programa 1** organiza a transição do Inspectah para uma operação mais madura, onde:

- o operador humano consegue **ligar, desligar e ajustar** partes críticas do sistema sem precisar de deploy;
- o comportamento do sistema deixa de ser uma "caixa preta de código" e passa a ser uma **engenharia configurável de fluxos, políticas e estados**;
- a plataforma fica mais próxima da visão de **"Data Hub + Truth Engine"**, em vez de ser apenas uma coleção de scripts de ingestão.

Dentro desse programa, o **Épico E28 — Fluxo de Agentes Configurável v1** define um objetivo muito específico: tirar o fluxo de agentes de dentro do código e torná-lo um **objeto de domínio configurável, auditável e governável**.

A **Sprint 29** é a sprint que **abre o Épico E28**. Ela entrega a **v1 operável** do fluxo de agentes configurável, com foco em:

- modelo de dados e API de configuração de fluxo por domínio;
- UI linear mínima para visualizar e editar o fluxo;
- integração suficiente com o runtime para que, em pelo menos um caso real, o pipeline de ingestão use o fluxo definido em configuração em vez de código hardcoded;
- invariantes fortes que impeçam fluxos quebrados ou perigosos.

S29 não tenta resolver tudo sobre agentes. Ela é o passo em que o Inspectah **ganha a primeira alavanca de produto** sobre o cérebro de agentes: a ordem e o papel de cada agente deixam de ser uma decisão de código e passam a ser uma decisão de configuração.

---

## 2. Problema central que a Sprint 29 precisa resolver

Hoje, o fluxo de agentes por domínio sofre com uma combinação perigosa de fatores:

1. **Acoplamento ao código**  
   A ordem e o conjunto de agentes que processam um item (notícia, dado, evento) costumam estar embutidos em:
   - mapas e dicionários dentro do código;
   - enums e constantes espalhadas por módulos de ingestão;
   - condicionais ad hoc que definem qual agente entra em cena em qual momento.

   Qualquer ajuste de fluxo, por mais simples que seja (por exemplo, inserir um segundo debunker em sequência para um domínio crítico), exige:
   - alteração de código;
   - PR;
   - CI/CD;
   - deploy.

   Isso torna o sistema lento para reagir a eventos do mundo real, como:
   - uma onda de desinformação sobre eleições;
   - um surto de fake news sobre saúde;
   - uma crise econômica que demanda critérios mais rígidos em dados financeiros.

2. **Ausência de visibilidade única**  
   Não existe hoje um lugar único onde alguém consiga responder com segurança:
   - "Qual é o fluxo de agentes para o domínio X?";
   - "Qual é a sequência de papéis que processa notícias de política no Brasil?";
   - "Quem decide a verdade em casos de dados econômicos federais?".

   Sem essa visão, o comportamento do sistema é opaco, difícil de explicar para stakeholders e quase impossível de auditar.

3. **Zero versionamento explícito de fluxos**  
   Ajustes em fluxo, quando existem, ficam implícitos em commits de código. Não existe:
   - histórico fácil de entender por domínio;
   - comparação clara de "antes" e "depois" do fluxo;
   - explicação textual associada a uma mudança (ex.: "endurecer o fluxo de agentes para o domínio X durante o período eleitoral").

   Isso fragiliza a governança. Em um sistema que pretende ser referência de verdade, é inaceitável não saber quem mexeu no cérebro dos agentes, quando e por quê.

4. **Risco real de incoerências e violações de invariantes**  
   Sem um modelo central de fluxo, é fácil criar combinações incorretas, por exemplo:
   - um Debunker tentando atuar antes de existir uma classificação consistente do item;
   - um Decision Maker tomando decisão sem ter passado por um conjunto mínimo de análises;
   - fluxos vazios ou quase vazios para domínios novos que alguém "esqueceu" de configurar.

   Essas incoerências podem gerar decisões fracas, inconsistentes ou até perigosas, minando a confiança na plataforma.

5. **Operação lenta e pouco responsiva**  
   Sem uma camada de configuração, o time de produto/ops não tem alavancas táticas.

   Em um cenário ideal, queremos que uma pessoa responsável pela operação possa, por exemplo:
   - abrir o console,
   - ir até "Agentes & Fluxos",
   - ajustar a ordem e papéis dos agentes para um domínio específico,
   - registrar o motivo da mudança,
   - e ver isso refletido na operação em poucos minutos.

   Hoje, isso está longe da realidade.

A Sprint 29 existe para atacar esse conjunto de problemas de forma concentrada, entregando um **primeiro modelo sólido de fluxo de agentes configurável**, com UI mínima, invariantes fortes e integração com o runtime de ingestão.

---

## 3. Definições e linguagem comum da Sprint 29

Para evitar confusão terminológica, a S29 fixa algumas definições:

1. **Domínio**  
   Um domínio é uma combinação de:
   - tipo de conteúdo (notícia, dado estatístico, documento oficial, etc.);
   - escopo temático ou geográfico (ex.: política BR, economia BR, saúde global);
   - regras de tratamento que distinguem esse caso de outros.

   Cada domínio possui uma **chave estável** (`domain_key`), usada:
   - no pipeline de ingestão;
   - nas regras de classificação;
   - e agora nos fluxos de agentes.

2. **Fluxo de agentes (Agent Flow)**  
   É uma **lista ordenada de passos**, onde cada passo corresponde a um **papel de agente**. Exemplos de papéis:
   - `INTERPRETER` — interpretar o texto bruto, identificar entidades, extrair contexto;
   - `CLASSIFIER` — classificar o item em categorias/labels internas;
   - `ANALYST` — fazer análise descritiva/explicativa mais profunda;
   - `DEBUNKER` — procurar inconsistências, checar contra evidências, buscar contraprovas;
   - `DECISION_MAKER` — decidir o estado final do item (fato, falso, controverso, inconclusivo, etc.);
   - outros papéis que venham a ser definidos pelo squad Verdade & Interpretação.

   Este fluxo é **linear** na S29: é uma sequência do tipo passo 1, passo 2, passo 3… sem branching, sem grafos complexos.

3. **Configuração de fluxo (AgentFlowConfig)**  
   É a entidade que descreve o fluxo ativo associado a um domínio. Ela contém, entre outras coisas:
   - a chave do domínio (`domain_key`);
   - a lista de passos, cada um com `position`, `agent_role` e parâmetros adicionais;
   - metadados de auditoria (quem criou/alterou, quando, com qual justificativa).

4. **Passo de fluxo (AgentFlowStep)**  
   Representa uma posição específica no fluxo. Contém:
   - posição ordinal (`position`);
   - papel de agente (`agent_role`);
   - parâmetros associados (ex.: comitê responsável, thresholds, flags de modo estrito/relaxado).

5. **Invariantes de fluxo**  
   São regras que tornam um fluxo **válido** ou **inválido**. Por exemplo:
   - um fluxo não pode ser vazio;
   - o primeiro passo deve ser um papel permitido como entrada (por exemplo, `INTERPRETER`);
   - não pode haver `DECISION_MAKER` antes de todos os passos analíticos exigidos para aquele domínio;
   - não pode haver dois `DECISION_MAKER` em posições diferentes;
   - posições do fluxo não podem ser duplicadas ou inconsistentes.

6. **UI de fluxo de agentes**  
   É a tela no console admin que permite ao operador:
   - ver o fluxo atual de um domínio;
   - adicionar/remover passos do fluxo;
   - alterar a ordem dos passos;
   - salvar alterações, desde que as invariantes sejam respeitadas;
   - registrar o motivo da mudança.

Essas definições são a base semântica do capítulo 1 e serão usadas nos capítulos seguintes (Gates, Arquitetura, Execução) para manter consistência.

---

## 4. Papel da S29 no Épico E28 e no roadmap

O Épico E28 foi desenhado em três blocos principais:

1. **E28.1 — Modelo & API de fluxo**  
   Foco em:
   - modelar `AgentFlowConfig` e `AgentFlowStep`;
   - criar migrations e storage de configuração;
   - expor APIs de admin para ler/criar/atualizar fluxos.

2. **E28.2 — UI de fluxo e integração com runtime**  
   Foco em:
   - construir a UI de configuração de fluxo;
   - integrar o runtime de ingestão para consumir o fluxo configurado;
   - implementar invariantes de fluxo e validações fortes na borda.

3. **E28.3 — Histórico, versionamento e governança avançada de fluxo**  
   Foco em:
   - dar visibilidade histórica completa de alterações;
   - permitir rollback e comparações de versões;
   - conectar essas mudanças com políticas de governança mais ricas.

A **Sprint 29** atua em **E28.1 inteiro** e na **base de E28.2**, entregando:

- modelo + API de fluxo por domínio;
- UI linear mínima (sem editor visual avançado, sem histórico rico);
- integração suficiente com o runtime para habilitar um caso real funcionando;
- validações e invariantes mínimas para que o fluxo não seja um brinquedo perigoso.

A **Sprint 30** terá espaço para atacar:

- a experiência de UI avançada (fluxo mais rico, feedback visual melhorado, ergonomia para múltiplos domínios);
- o histórico/versionamento detalhado de fluxos;
- regras de governança mais complexas ligadas a fluxos (por exemplo, exigência de aprovação dupla em domínios sensíveis).

S29, portanto, é a sprint que transforma o E28 de ideia em **infraestrutura real**. Depois dela, o time deixa de falar de "fluxo de agentes configurável" no condicional e passa a operar essa ideia na prática, mesmo que ainda em versão 1.

---

## 5. Objetivos da Sprint 29 (versão de produto, não de gate)

Do ponto de vista de produto e operação, a Sprint 29 será considerada bem-sucedida se, ao final, conseguirmos afirmar que:

1. Para pelo menos um domínio real e relevante (por exemplo, "Notícia — Política BR"), o fluxo de agentes:
   - está configurado em banco via `AgentFlowConfig`;
   - é visível e editável na UI de admin;
   - é utilizado pelo pipeline de ingestão para processar itens reais desse domínio.

2. Um operador com permissão adequada é capaz de:
   - abrir o console de admin;
   - navegar até a tela de "Fluxo por domínio";
   - entender a lista de passos atuais de um domínio;
   - realizar uma alteração simples (por exemplo, inserir um `DEBUNKER` adicional em uma posição específica);
   - salvar a mudança com uma justificativa;
   - ver o efeito da alteração em execuções subsequentes do pipeline.

3. Fluxos inválidos (sem papéis obrigatórios, ordem proibida, combinações perigosas) são rejeitados com mensagens claras, tanto na API quanto na UI.

4. Toda mudança em fluxo deixa ao menos um **rastro mínimo**:
   - quem mudou;
   - quando;
   - qual foi o motivo;
   - qual era o fluxo antes e depois em forma resumida.

5. O conselho técnico (Percy Liang, Martin Kleppmann, Judea Pearl, Stonebraker, Norvig e cia.) enxerga o resultado de S29 como:
   - um modelo sólido e extensível de fluxo de agentes;
   - um contrato razoavelmente estável com o runtime de ingestão;
   - uma base confiável para construir as camadas mais sofisticadas de E28.2 e E28.3 nas próximas sprints.

Os objetivos de S29 não são apenas "ter rotas e telas"; o ponto é que o Inspectah passe a ter um **muscle real de configuração de fluxo**, ainda que simples, com o qual a equipe pode experimentar, medir, endurecer e evoluir.

---

## 6. Restrições, premissas e alinhamentos importantes

Para manter S29 focada, algumas premissas e restrições são estabelecidas desde o capítulo 1:

1. **Fluxo estritamente linear na S29**  
   Não haverá grafos complexos, caminhos condicionais ou branching. Essas capacidades são desejadas no futuro, mas seriam veneno escopo nesta sprint. S29 trabalha com uma **lista ordenada simples**.

2. **Reutilização máxima de conceitos existentes**  
   S23–S25 já definiram papéis de agentes, comitês e semântica básica. S29 não redefine esse universo; ela o **reusa como catálogo** para montar fluxos configuráveis.

3. **Integração mínima, mas real, com o runtime**  
   Não faz sentido entregar só UI e modelo sem conectar ao pipeline. Porém, também não é realista reescrever todo o pipeline em uma sprint. A regra é: integrar o suficiente para que **um pipeline representativo** use o fluxo configurado, deixando extensões mais amplas para sprints futuras.

4. **Sem amarras com Sistema de Blocos ou blockchain nesta sprint**  
   A responsabilidade de S29 é o fluxo de agentes. Ancoragem em blocos, provas on-chain e sistema de reputação avançada continuam escopo da Fase 2 e de outros épicos.

5. **Segurança por invariantes, não por proibição total**  
   S29 não pretende engessar o sistema com regras arbitrárias, mas sim:
   - definir um conjunto sólido de invariantes mínimas;
   - permitir flexibilidade dentro dessas invariantes;
   - tornar a violação de regras visível, explicada e bloqueada.

Com essas premissas, a Sprint 29 fica suficientemente **ambiciosa para valer o esforço**, mas **finita o bastante para ser executada com excelência** dentro do ciclo da sprint.

---

## 7. Conclusão do Capítulo 1

O Capítulo 1 da Sprint 29 estabelece o pano de fundo:

- o Inspectah está amadurecendo do ponto de vista de governança de verdade e de configuração de comportamento;
- o Épico E28 existe para transformar o fluxo de agentes em um primeiro-cidadão do domínio, e não em detalhe interno de código;
- a Sprint 29 é a abertura concreta desse épico, focando em modelo, API, UI mínima, integração com runtime e invariantes fortes.

Os próximos capítulos vão derivar deste contexto:

- o **Capítulo 2** vai traduzir esses objetivos em **gates, métricas, scorecards e critérios de GO/NO-GO** para a sprint;
- o **Capítulo 3** vai materializar a arquitetura detalhada, o filemap e as decisões de design de modelo, API, UI e runtime;
- o **Capítulo 4** vai quebrar isso em execução concreta: waves, tarefas, scripts de gates, caminhos de evidência e bundles.

A partir deste capítulo, a S29 passa a ter uma **narrativa clara**: não é apenas criar mais tela ou mais endpoint; é dar ao Inspectah a sua **primeira versão controlável do cérebro de agentes por domínio**, com toda a responsabilidade que isso implica.

