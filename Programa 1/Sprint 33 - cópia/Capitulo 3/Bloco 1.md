# Sprint 33 — Capítulo 3

## Bloco 1 — Visão macro da arquitetura OracleOps v1 na S33

A Sprint 33 introduz o OracleOps v1 como uma camada de operação explícita sobre o que o Inspectah já construiu em mais de trinta sprints. Em vez de criar um sistema paralelo, a S33 se comporta como um par de óculos novos: ela não muda o mundo, mas muda a forma como o mundo é enxergado e operado. Este bloco descreve a visão macro dessa arquitetura, em um nível que permita a qualquer pessoa entender "como as coisas se encaixam" antes de descer à lista exata de arquivos e módulos nos blocos seguintes.

Do ponto de vista estrutural, o OracleOps v1 na S33 é organizado em cinco camadas principais, que se apoiam umas nas outras:

1. **Camada de dados operacionais: fontes, ingestão, pipelines e Truth‑DB**  
   É o plano de fundo sobre o qual o OracleOps olha. Inclui:
   - o **Data Hub** e o **Console de Fontes**, onde residem os registros formais das fontes de dados (RSS, APIs, bases oficiais, feeds especializados);
   - os **pipelines de ingestão 2.0**, que movem esses dados das fontes para estágios intermediários e, em alguns casos, até a Truth‑DB e o System of Blocks;
   - a infraestrutura de **filas, workers e jobs agendados** que fazem esse trânsito acontecer.
   A S33 não altera a lógica fundamental dessa camada; ela assume que esses componentes existem e funcionam, mas reconhece que, sem uma camada de operação, é difícil saber se estão saudáveis ou não.

2. **Camada de observabilidade e medições: métricas, logs, SLOs brutos**  
   Aqui vivem as medições que descrevem o comportamento da camada de dados operacionais:
   - métricas de recência de ingestão por fonte;
   - métricas de latência de pipelines;
   - contadores de erros e taxas de falha em serviços internos;
   - logs centralizados que registram eventos relevantes.
   A S33 não inventa uma nova stack de observabilidade; ela **usa a que já existe**, adicionando consultas, dashboards e regras de alerta focadas no recorte da sprint. Essa camada é a matéria‑prima a partir da qual SLOs são avaliados e estados de saúde são calculados.

3. **Camada de domínio de operação: componentes, Incident e SLOs como entidades**  
   Esta é a camada em que o sistema ganha linguagem operacional:
   - **componentes monitorados** são mapeados de forma explícita (fontes, pipelines, APIs internas, workers), com IDs estáveis e criticidade declarada;
   - **incidentes** são modelados como entidades persistentes, com estados, severidades, timestamps e vínculos a componentes e SLOs;
   - **SLOs** deixam de ser descrições soltas em documentos e passam a ser representações estruturadas, referenciando métricas concretas e componentes específicos.
   Essa camada fica principalmente no backend, em módulos de domínio e serviços, e é o coração semântico do OracleOps: sem ela, o cockpit viraria apenas um conjunto de gráficos soltos.

4. **Camada de serviços de operação: health summary, avaliação de SLO e orquestração de incidentes**  
   Sobre o domínio de operação, a S33 introduz serviços especializados que fazem o "trabalho pesado" da camada OracleOps:
   - o serviço de **health summary** lê métricas e sinais dos componentes do recorte e os classifica em estados como "OK", "degradado" ou "falhando";
   - o serviço de **SLO evaluation** lê a definição dos SLOs da S33, executa consultas na stack de observabilidade e produz um estado atual para cada SLO (dentro/fora/sem dados);
   - serviços de **orquestração de incidentes** expõem operações de criação, atualização, transições de estado e listagem de incidentes, sempre amarrados a componentes e, quando aplicável, a SLOs.
   Esses serviços são expostos via API para o frontend, mas também podem ser reutilizados por scripts de gates e ferramentas de ORR, reduzindo duplicação de lógica.

5. **Camada de experiência de operação: OracleOps Cockpit v1, runbooks e evidência**  
   No topo, a S33 adiciona a face visível para humanos:
   - o **OracleOps Cockpit v1**, um conjunto de telas no frontend que oferece:
     - visão geral de saúde do recorte da sprint;
     - visão detalhada de componentes (fontes, pipelines, APIs);
     - visão e manipulação de incidentes;
     - visibilidade mínima sobre SLOs e seu estado;
   - a integração com **runbooks**, expostos como links contextuais em componentes e incidentes, para guiar a resposta operacional;
   - a ligação com **bundles de evidência**, permitindo que operadores acessem rapidamente material de ORR e histórico de incidentes relevantes.

Essas camadas formam um pipeline conceitual:

> **Dados operacionais** (fontes, ingestão, Truth‑DB)  
> → geram **métricas e logs**  
> → que são interpretados pelo **domínio de operação** (componentes, Incident, SLOs)  
> → agregados por **serviços de operação** (health summary, SLO evaluation, orquestração de incidentes)  
> → e apresentados na **experiência de operação** (cockpit, runbooks, evidência) para que humanos tomem decisões.

Do ponto de vista de risco arquitetural, a S33 faz três escolhas importantes:

- **Não duplicar a lógica de domínio existente.**  
  Tudo que diz respeito à verdade dos dados (como o Truth‑DB promove fatos, como o System of Blocks guarda versões) permanece nas camadas já definidas em programas anteriores. O OracleOps apenas observa e relata o comportamento desses componentes, em vez de tentar “mandar” neles.

- **Tratar operação como domínio de primeira classe.**  
  Incident, componente monitorado e SLO não são mais anotações marginais: são entidades com modelo, invariantes, testes e lugar definido na arquitetura. Isso reduz a chance de o OracleOps virar uma coleção de scripts soltos.

- **Manter o cockpit fino e opinativo.**  
  O OracleOps Cockpit v1 não tenta ser uma ferramenta de BI genérica; ele é uma UI opinativa, desenhada para responder rapidamente às perguntas que importam para o recorte da S33 ("está saudável?", "o que está ruim?", "qual incidente representa isso?", "onde está o runbook?").

Finalmente, a visão macro da S33 é deliberadamente **evolutiva**: a arquitetura foi desenhada para que, nas próximas sprints, seja possível:

- adicionar novos componentes ao mapa de operação sem quebrar o cockpit;
- incorporar novos SLOs e regras de alerta sem refazer o motor de avaliação do zero;
- enriquecer o modelo de Incident e o fluxo de runbooks sem precisar reescrever toda a UI.

Os próximos blocos deste capítulo descem do diagrama conceitual para o nível de filemap, módulos, rotas e scripts específicos, garantindo que essa visão macro se mantenha alinhada com o código vivo do Inspectah.