# Sprint 33 — Capítulo 6

## Bloco 1 — Por que a S33 é uma sprint de operação de nova geração

Este bloco aprofunda a seção 6.1 do capítulo, explicando **por que** a Sprint 33 deve ser tratada como uma sprint de operação de nova geração dentro do Inspectah — e não apenas como “mais uma sprint de features”.

A S33 é o ponto em que o projeto dá um passo explícito da fase:

> “temos código que faz coisas”  
> para  
> “temos uma forma disciplinada de operar o que o código faz — especialmente no que toca à verdade que ele produz”.

Em outras palavras, ela marca a transição de um projeto centrado em funcionalidades para um projeto que **assume operação como parte do produto**.

---

### 6.1.1 O que diferencia a S33 de uma sprint de feature comum

Sprints clássicas de feature costumam ter como foco:

- adicionar endpoints, telas, entidades de domínio;
- entregar novos casos de uso para usuários finais;
- “aumentar escopo” visível.

A S33, por outro lado, tem como foco principal:

- **como o Inspectah é observado, entendido e cuidado no dia a dia**;
- **como falhas operacionais são detectadas, interpretadas e respondidas**;
- **como a qualidade da verdade exposta é protegida por práticas de operação**.

Isso se manifesta em alguns traços concretos:

1. **O principal artefato não é uma tela de usuário final, mas um cockpit de operação (OracleOps v1)**, com domínio próprio, API própria e UX orientada a personas de operação.

2. **A sprint entrega processos codificados de operação (runbooks, bundles, ORR) ao lado de código**, em vez de delegar a operação para wikis genéricas ou “bom senso de time”.

3. **A definição de “DONE” é operacional**, não apenas funcional: a S33 só se considera concluída quando alguém que não escreveu o código consegue operar o recorte da sprint usando o cockpit, SLOs, incidentes e runbooks — e isso foi demonstrado em ORR com evidência.

Esse deslocamento de foco é o que faz da S33 uma sprint de operação de nova geração.

---

### 6.1.2 O pacote OracleOps v1 como entrega central da S33

A Sprint 33 é organizada em torno da entrega de um pacote coerente, que chamamos de **OracleOps v1**. Ele é composto por cinco camadas interligadas:

1. **Domínio de operação**  
   Entidades que dão linguagem à operação do Inspectah:
   - `Incident` — problemas operacionais com lifecycle, severidade, vínculos com componentes e SLOs;
   - `ops_components` — visão tipada dos componentes que formam a jornada da informação (fontes, pipelines, Truth‑DB, APIs);
   - `ops_slos` — SLOs definidos para o recorte da sprint, com semântica clara (o que medem, onde medem, quando estão bons/ruins).

2. **Serviços de operação**  
   Módulos que implementam a lógica operacional:
   - `ops_health_summary` — consolida estado dos componentes em uma visão operável;
   - `ops_slo_evaluator` — traduz SLOs em queries concretas na stack de observabilidade e retorna estados interpretáveis;
   - `ops_cockpit_routes` — expõe uma API consistente para o cockpit consumir.

3. **Cockpit de operação (frontend `oracleops`)**  
   Uma feature dedicada, com:
   - páginas de overview, componentes, incidentes;
   - componentes como `ComponentHealthTable`, `SloSummaryPanel`, `RunbookLinks`;
   - navegação pensada para responder às perguntas do operador.

4. **Processos de operação codificados**  
   Procedimentos que definem como operar o sistema:
   - runbooks em `docs/runbooks/` (prefixo S33_*), com passos concretos para incidentes típicos;
   - bundles de incidentes em `out/evidence/S33_G4_incidents/`, encapsulando timelines, logs, prints, SLOs e runbook usado;
   - ORR operacional (G5), com roteiro, papéis e ata.

5. **Governança de sprint por gates, scorecards e evidência**  
   Estrutura que garante que nada disso é informal:
   - scripts `bin/s33_g0..g5_*.sh` representando as perguntas críticas de prontidão;
   - scorecards `out/scorecards/S33_G*_*.json` registrando o estado de cada gate;
   - diretórios `out/evidence/S33_G*/` contendo a trilha de execução e validação.

O resultado não é uma coleção de peças soltas, mas um **ecossistema de operação** minimamente completo.

---

### 6.1.3 A mudança de paradigma: operação como parte do produto de verdade

O ponto mais importante da S33 é cultural e arquitetural:

> A operação deixa de ser vista como “custo necessário” e passa a ser tratada como **parte do produto**.

No contexto do Inspectah, isso tem implicações fortes:

- **Para Produto:** toda decisão relevante sobre novas fontes, pipelines, casos, blocos de verdade ou APIs precisa, a partir da S33, ser acompanhada da pergunta "o que isso significa para o OracleOps?".

- **Para Engenharia:** desenhar novas features passa a exigir que elas se encaixem em componentes observáveis, com espaço para SLOs, incidentes e runbooks. Não é aceitável criar "caixas pretas" incuidáveis.

- **Para Operação/Governança:** o cockpit vira ferramenta central de trabalho; scorecards e bundles deixam de ser curiosidades para se tornarem parte das conversas de GO/NO_GO.

Essa mudança de paradigma é o que diferencia uma sprint "que adicionou uma UI de monitoramento" de uma sprint que realmente constituiu um **primeiro sistema nervoso operacional**.

---

### 6.1.4 Por que isso é “nova geração” e não só boa prática

Boas práticas de SRE, observabilidade e gestão de incidentes já existem há anos. O que justifica chamar a S33 de sprint de operação de **nova geração** é a combinação de dois fatores:

1. **Aplicação dessas práticas a um domínio pouco explorado:**  
   Em vez de operar apenas serviços técnicos, o OracleOps v1 começa a operar **cadeias de verdade** — integridade e recência de informação, tempo de reação a contestação, saúde de casos.

2. **Tratamento de operação como artefato de primeira classe no roadmap de produto:**  
   A S33 não é um “Projeto de Ops paralelo”, mas uma sprint central do roadmap, com capítulos, blocos, gates e DoD tão rigorosos quanto qualquer sprint de funcionalidade core.

Essa combinação coloca a Sprint 33 em uma categoria diferente de sprints que “apenas” implementam monitoria ou alertas. Aqui, operação é projetada desde o início como parte da missão do Inspectah.

---

### 6.1.5 Como este bloco deve ser usado

Este Bloco 1 serve como referência conceitual para:

- alinhar toda a equipe (Produto, Engenharia, Ops, Governança) sobre **o que está em jogo** na S33;
- orientar decisões de trade‑off durante a implementação (sempre perguntando se estamos preservando o caráter de sprint de operação de nova geração);
- validar, no encerramento, se o que foi entregue condiz com a ambição descrita aqui.

Se, ao final da sprint, o time olha para o que foi implementado e reconhece neste bloco a descrição fiel do resultado, então a S33 não foi apenas executada: ela cumpriu sua função de mudar o patamar da operação no Inspectah.
