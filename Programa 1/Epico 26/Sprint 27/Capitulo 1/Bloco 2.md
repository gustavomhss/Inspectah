# Inspectah — Sprint 27 (S27)
## Capítulo 1 — Bloco 2
### Problema central, riscos e sintomas operacionais

> Arquivo-alvo no repo: `docs/s27_cap_1_2_problema_e_riscos.md`
>
> Função: formular, com precisão cirúrgica, **qual é o problema que a S27 resolve**, quais são os **riscos de não resolvê-lo agora** e como ele se manifesta na vida real de operadores, squads e do produto. Este bloco é a "radiografia" do porquê da sprint.

---

## 1. Formulação precisa do problema

### 1.1 Versão enxuta em uma frase

Hoje, **Fontes, Ingestão 2.0 e Debunker são operados por consoles que não falam o mesmo idioma visual nem operacional**, o que aumenta a chance de erro humano, complica runbooks e enfraquece o Design System Admin v1 recém-criado.

### 1.2 Versão detalhada

O Inspectah depende, no dia a dia, de três capacidades operacionais centrais:

1. **Gerir Fontes** — decidir quais fontes existem, o que elas fazem, quando ligam/desligam.  
2. **Operar Ingestão** — acompanhar se os dados estão entrando, detectar atrasos/falhas, agir rápido.  
3. **Lidar com Disputas (Debunker)** — analisar casos, evidências e decidir o que é verdade ou não.

Na prática, essas capacidades deveriam ser três "salas" diferentes de um mesmo centro de controle (Admin).  
O que temos hoje é mais próximo de **três mini-sistemas diferentes**, cada um com um jeito próprio de:

- mostrar listas, detalhes e estados;  
- indicar erros, alertas e sucesso;  
- ordenar e filtrar o que importa;  
- conduzir o operador a agir.

O Design System Inspectah Admin v1, criado na S26, resolve esse problema **apenas para Fontes**.  
Enquanto Ingestão e Debunker não migrarem para o mesmo padrão, o sistema segue com UI/Admin fragmentada.

---

## 2. Sintomas concretos do problema hoje

### 2.1 Do ponto de vista do operador de Ingestão/Dados

- Ao sair do Console de Fontes v2 (Admin v1) para ver o estado da ingestão:
  - muda o layout de navegação (sidebar, header, espaçamentos, hierarquia visual);  
  - mudam cores e padrões de estados ("erro" numa tela não parece o mesmo tipo de coisa que "erro" na outra);  
  - filtros e colunas seguem lógicas levemente diferentes.
- Em incidentes de ingestão (jobs travados, filas atrasadas), o operador precisa "reaprender" onde olhar em cada console.

Efeito prático:
- mais tempo gasto **navegando** e menos **diagnosticando**;  
- maior risco de passar batido por estados importantes (por exemplo, ingestão atrasada porque não há um padrão claro de destaque para isso).

### 2.2 Do ponto de vista do analista/Debunker

- Ao comparar uma disputa (Debunker) com o estado atual de ingestão/fonte:
  - encontra telas com linguagens visuais diferentes, com nomenclaturas distintas para estados similares;  
  - tem dificuldade em criar um "mapa mental" único de onde as coisas estão;  
  - precisa de mais context-switching cognitivo em tarefas delicadas (tomar ou revisar decisões de verdade/fato).

Efeito prático:
- maior carga mental para reconciliar informações dos diferentes consoles;  
- maior probabilidade de erro de leitura (ex.: interpretar um status como menos grave do que é, simplesmente pela forma de apresentação).

### 2.3 Do ponto de vista de Truth Ops / on-call

- Em incidentes que envolvem múltiplas camadas (fonte errada gerando ingestão quebrada que alimenta um caso em disputa):
  - o on-call precisa entrar em três consoles com experiências diferentes;  
  - cada tela oferece uma forma distinta de ver "vermelhos" e "amarelos";  
  - runbooks precisam conter instruções específicas de navegação por console, em vez de se apoiar em padrões comuns.

Efeito prático:
- tempo de resposta mais lento;  
- dependência maior de pessoas "seniores" que memorizaram detalhes de cada console;  
- dificuldade em escalar operação para novos membros.

### 2.4 Do ponto de vista dos squads de produto/engenharia

- Evoluções de UI/UX precisam ser implementadas 3x (Fontes, Ingestão, Debunker), com estilos e componentes semelhantes, mas não iguais.  
- Bugs de UI/UX repetem nos diferentes consoles, porque consertar num não garante correção nos outros.  
- Gates e testes de frontend ficam pulverizados: cada console precisa da sua própria suíte, sem reaproveitar padrões.

Efeito prático:
- custo de evolução mais alto;  
- risco de regressões visuais/comportamentais persistente;  
- menor alavancagem do trabalho da S26 (Admin v1 ainda não é "multiplicador").

---

## 3. Riscos de não resolver isso na S27

### 3.1 Risco R-A — Consolidação de dívida estrutural de UI/Admin

Se Ingestão e Debunker seguirem evoluindo fora do Admin v1, o sistema entra num estado de **"dois mundos" permanentes**:

- de um lado, consoles novos ou refatorados em Admin v1;  
- de outro, consoles antigos com padrões próprios.

Consequências:
- migrar mais tarde fica mais caro (mais telas, mais estados, mais casos especiais para trazer);  
- operações continuam sofrendo com falta de coerência;  
- Admin v1 corre o risco de ser visto como "mais um padrão em cima de tantos".

### 3.2 Risco R-B — Aumento do risco operacional por UX divergente

Ambientes de verdade/crise (ingestão travada, disputa sensível politicamente, etc.) exigem **interfaces previsíveis e coerentes**.

Se cada console tiver um jeito próprio de destacar problemas, ações críticas e prazos:
- aumenta a chance de clique errado (desativar/arquivar fonte errada, acionar ação incorreta em disputa, etc.);  
- aumenta a chance de **não perceber** um alerta relevante em meio ao ruído.

### 3.3 Risco R-C — Enfraquecimento do método de gates, ORR e runbooks

O modelo de Cap.5 e Cap.6 da S26 supõe um certo nível de **padronização de consoles**:
- gates que testam flows E2E entre consoles;  
- ORR que observa cenários multi-console;  
- runbooks que descrevem navegações e ações de maneira consistente.

Com consoles heterogêneos, esses mecanismos perdem força:
- ou ficam genéricos demais (não capturam nuances de cada console);  
- ou viram um "frankenstein" cheio de exceções.

### 3.4 Risco R-D — Desalinhamento entre Roadmap e realidade

O Roadmap pós-S25 e pós-S26 assume que E26 vai entregar **Admin v1 como padrão** para os principais consoles internos.

Se a S27 não cumprir essa promessa:
- epics futuros podem ser planejados em cima de uma premissa falsa ("é só reutilizar Admin v1"),
- o custo de implementação real será maior que o estimado,
- e o débito se espalha para outras trilhas (Ingestão, Verdade & Interpretação, Evidence Vault).

---

## 4. Não-problemas: o que a S27 *não* está tentando resolver

Para não diluir o foco, é importante explicitarmos o que **não** é o problema da S27:

1. **"Ingestão não é eficiente o suficiente"**  
   - Problema legítimo, mas escopo de sprints de Ingestão (jobs, filas, backoff).  
   - S27 mexe na **interface de operação**, não na arquitetura de ingestão.

2. **"Debunker ainda não tem todas as políticas desejadas"**  
   - Verdade, pertence a sprints de Verdade & Contestação.  
   - S27 cuida de **como** essas políticas aparecem e são operadas, não de quais são.

3. **"Precisamos de dashboards avançados e gráficos complexos"**  
   - Importante, mas faz parte de trilhas futuras de Observabilidade.  
   - S27 entrega o básico para operação coerente, não o cockpit definitivo.

Ao manter esses não-problemas fora do escopo, garantimos que a S27 ataque com profundidade o que, de fato, só ela pode resolver agora: a **coerência de Admin v1 entre os consoles críticos**.

---

## 5. Critérios para dizer que o problema da S27 foi resolvido

O problema descrito neste bloco será considerado tratado se, ao final da sprint:

1. Um operador conseguir navegar entre Fontes, Ingestão e Debunker e descrever a experiência como "**é tudo o mesmo sistema**".  
2. Runbooks de Fontes, Ingestão e Debunker puderem ser escritos usando a **mesma linguagem de componentes e estados**, com poucas exceções.  
3. Gates/ORR conseguirem testar fluxos E2E que passam pelos três consoles sem lidar com idiossincrasias visuais/estruturais específicas.  
4. Quaisquer pontos restantes de divergência forem poucos, mapeados e registrados como dívidas técnicas da S27.

Este Bloco 2 é o teste de sanidade para Cap.2–Cap.4: se algum gate, arquitetura ou task não tem ligação clara com a resolução desse problema, ele provavelmente está deslocado de sprint.