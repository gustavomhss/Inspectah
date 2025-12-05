# Sprint 33 — Capítulo 6

## Bloco 2 — Padrões de referência que inspiram a S33

Este bloco aprofunda a seção 6.2, deixando explícito **quais são os referenciais concretos** que a S33 está usando como norte. A ideia é tirar o rótulo “state of the art” do terreno do marketing e ancorá‑lo em **famílias de práticas, papers, livros e ferramentas** que definem o que hoje é considerado operação de alto nível.

Em vez de uma bibliografia formal, o bloco descreve “linhagens” de ideias e como elas influenciam decisões da Sprint 33.

---

### 6.2.1 SRE (Site Reliability Engineering) como espinha dorsal conceitual

A primeira grande linha de referência é o corpo de conhecimento de SRE. Alguns conceitos centrais que a S33 absorve e reinterpreta:

1. SLOs, SLIs e error budgets  
   A S33 adota explicitamente a ideia de **SLO como contrato** e **SLI como medida concreta**. Embora o capítulo não cite nomes, a linha é clara:
   - todo objetivo operacional precisa de uma métrica que o represente (SLI);
   - todo SLI precisa de um alvo definido (SLO);
   - decisões de risco (lançar algo, assumir débito operacional) precisam se apoiar nesses alvos.

   A adaptação para o Inspectah é adicionar, além de latência/uptime, SLOs que capturam recência e integridade de informação.

2. Operação orientada a risco, não a superstição  
   Em vez de checagens arbitrárias, a S33 tenta ligar cada gate a uma pergunta de risco: 
   - “o que acontece se G1 estiver fraco?”
   - “que risco corremos se G3 não estiver implementado?”

   Essa forma de pensar vem diretamente da filosofia SRE de tratar confiabilidade como algo mensurável, com trade‑offs explícitos, e não como superstição ou checklist vazio.

3. Postmortems e aprendizado sistemático  
   Os bundles de incidentes da S33 são, na prática, uma implementação minimamente estruturada da ideia de postmortem moderno: fatos, linha do tempo, contexto de métricas, ações tomadas e learnings. A diferença é que tudo isso é pensado, desde o início, para poder ser versionado, consultado e, eventualmente, automatizado.

---

### 6.2.2 Observabilidade moderna: métricas, logs, traces e explorabilidade

A segunda linha de referência é o movimento de observabilidade moderna. A S33 não tenta reinventar essa roda; ela se apoia nela:

1. Três pilares, mas com foco em perguntas  
   Métricas, logs e traces são tratados como ferramentas, não como fins. O design de `ops_slos` e `ops_slo_evaluator` parte de perguntas como:
   - “o que o operador precisa saber para decidir se está tudo bem?”;
   - “quais sinais antecedem um problema grave?”

   A partir daí, a sprint define quais métricas e queries importam para o recorte, em vez de acumular gráficos arbitrários.

2. Adaptadores em vez de acoplamento rígido  
   A decisão arquitetural de centralizar consultas de SLO em um módulo (`ops_slo_evaluator`) é inspirada na prática de criar **camadas de adaptação** entre o sistema e a stack de observabilidade. Assim, a troca de provider (Prometheus, Grafana, Datadog, etc.) não implica reescrever o código inteiro.

3. Evidência observável por design  
   Quando a S33 define que evidências de G3 incluem resultados de queries, prints de dashboards e logs recortados, ela está aproximando o Inspectah da visão de que “logs e métricas não servem só para monitoramento ao vivo, mas também para reconstruir narrativas de falha e aprendizagem”. Isso ecoa diretamente a lógica da observabilidade moderna.

---

### 6.2.3 Gestão de incidentes como disciplina, não improviso

A terceira linha é a disciplina de gestão de incidentes, consolidada em práticas de empresas que lidam com alta criticidade.

A S33 incorpora elementos como:

1. Incident como átomo de aprendizado  
   Ao definir um modelo `Incident` com lifecycle, severidade e vínculos, a sprint assume que **cada incidente é uma unidade de aprendizado**. Ele não desaparece após a resolução; vira material de estudo (bundles), refino de runbooks e possível gatilho para mudanças de design.

2. Papéis e roteiro em situações de pressão  
   A ORR da S33, com papéis definidos (operador, facilitador, observador) e script, é diretamente inspirada por práticas de incident management onde roles como “incident commander” e “scribe” são usados para manter clareza em momentos de crise. Aqui, a ORR funciona como um “incidente simulado de luxo”.

3. Comunicação estruturada e pós‑evento  
   Ao exigir `s33_incidents_learnings.md` e registrar follow‑ups de ORR, a S33 coloca comunicação pós‑incidente no mesmo plano de importância que a técnica, seguindo a tradição de postmortems blameless e learning reviews.

---

### 6.2.4 Cockpits e control planes de plataformas complexas

A quarta linha é o padrão, hoje comum, de plataformas complexas terem um **control plane/cockpit**: um lugar onde se observa estado e se emite comandos (mesmo que alguns comandos ainda sejam manuais na S33).

O OracleOps v1 se inspira em:

1. Consoles de orquestradores (Kubernetes, sistemas de dados, filas)  
   A ideia de ter uma `OverviewPage` com visão agregada, drill‑down por componente, e detalhes de recursos lembra dashboards de clusters, sistemas de mensageria e orquestradores de ETL. O que muda é a semântica: aqui os componentes são degraus da cadeia de verdade.

2. Separação entre UI de produto e UI de operação  
   Ao isolar a feature `oracleops` no frontend, a S33 segue a prática de separar "console de operação" de "interface de usuário final". Isso evita misturar preocupações de usabilidade pública com necessidades mais cruas e técnicas de operação.

3. Componentização de insights operacionais  
   Componentes como `SloSummaryPanel`, `ComponentHealthTable` e `RunbookLinks` são desenhados como tijolos reutilizáveis para trazer contexto operacional a diferentes telas, de forma semelhante ao que painéis modernos fazem ao encaixar widgets de métricas, logs e ações.

---

### 6.2.5 Governança por gates, scorecards e ORR

Por fim, há uma linha de referência menos técnica e mais processual: a de governança de mudanças via gates e reviews formais.

A S33 bebe em experiências de:

1. Change management estruturado  
   Em ambientes críticos, mudanças passam por checkpoints formais (gates) onde riscos são avaliados e evidências são apresentadas. A S33 transforma isso em código e arquivos: scripts em `bin/`, scorecards em `out/scorecards/`, logs em `out/evidence/`.

2. ORR como prática recorrente  
   Em vez de tratar readiness reviews como evento raro, a sprint formaliza a ORR operacional (G5) como parte do ciclo de entrega. Isso acompanha o movimento de empresas que tratam readiness reviews como ingrediente fixo de lançamentos.

3. Evidência como requisito, não como opcional  
   A insistência em evidências versionadas como condição para GO é diretamente alinhada com culturas de compliance forte, auditoria e certificações — adaptadas aqui não para burocracia, mas para garantir confiabilidade da verdade que o Inspectah entrega.

---

### 6.2.6 Síntese: uma base sólida, mas conscientemente adaptada

A principal mensagem deste bloco é: **a S33 não está “inventando moda” no vazio**. Ela se ancora em linhas bem estabelecidas de SRE, observabilidade, incident management, control planes e governança por gates. O que existe de original não é a existência desses conceitos, mas a forma como são adaptados:

- para um sistema cujo ativo principal é verdade, não apenas throughput; 
- para uma organização que quer tratar operação como parte intrínseca do produto, não como preocupação tardia.

Esse encaixe entre referências sólidas e um domínio novo é o que dá sustentação à afirmação de que a S33 é uma sprint "state of the art" — não porque ignora o que já foi feito, mas precisamente porque sabe de onde está partindo e para onde está tentando empurrar a fronteira.