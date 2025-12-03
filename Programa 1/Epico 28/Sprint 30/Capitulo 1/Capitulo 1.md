# Inspectah — Sprint 30 — Capítulo 1  
## Contexto, Problemas a Resolver e Objetivos de Resultado

---

### 1. Identidade da Sprint

**Código da sprint**: S30  
**Programa**: Programa 1 — Data Hub & Consoles 24/7  
**Épico dominante**: E28 — Fluxo de Agentes Configurável v1  
**Posição no épico**: 2ª sprint de 7 (E28 ocupa S29–S35)  
**Squad responsável**: Squad Fluxos & Orquestração  

**Frase‑guia da sprint**:  
> “Transformar o Console de Fluxos em a ferramenta onde o operador realmente controla o que acontece com as notícias — qual fluxo roda, em que modo, com quais agentes — sem precisar encostar em código.”

---

### 2. Contexto: de S29 para S30 dentro do E28

O Épico E28 define o **Fluxo de Agentes Configurável v1**: um modelo único de fluxo (pipeline de etapas e agentes) que recebe eventos brutos (ex.: notícias), os envia a uma cadeia de agentes (intérprete, classificador, analistas, debunkers, decision maker) e produz saídas estruturadas e auditáveis (alegações, evidências, estados de verdade, flags).  

A Sprint 29 cumpriu três papéis essenciais:

1. **Concretizou o modelo de Fluxo de Agentes** no domínio do código e dos dados (entidades Fluxo, Etapa, Nó/Agente, Execução de Fluxo, Execução de Etapa).  
2. **Criou o Console de Fluxos v1**, capaz de listar fluxos, mostrar estrutura básica (etapas, agentes ligados) e exibir um recorte de execuções recentes.  
3. **Conectou ingestão e fluxos** de forma mínima: eventos de pelo menos um tipo (notícias) já conseguem ser roteados para um fluxo configurado, ainda que com semântica operacional limitada.

Com isso, S29 levou o sistema do estado “fluxos existem no papel” para “fluxos existem no código e têm um console mínimo para inspeção”.  

A Sprint 30 entra exatamente aqui: não é mais sobre “fazer o console existir”; é sobre **tornar o console e o modelo de fluxos realmente operacionais** para um caso concreto e importante: o **fluxo de notícias**. A partir de S30, o operador precisa começar a confiar no console como a superfície onde toma decisões reais sobre:

- qual fluxo está recebendo eventos de notícias;  
- em que **modo** esse fluxo está (rascunho, em teste, ativo, pausado);  
- como trocar agentes problemáticos;  
- como pausar um fluxo que está se comportando mal;  
- como reprocessar itens críticos sem desencadear caos no sistema.

S30 é, portanto, a sprint que dá ao E28 o seu primeiro **“sistema nervoso operacional”**: um fluxo‑pivô (notícias) realmente controlável via Console, com estados que significam algo de verdade e com observabilidade mínima, ponta a ponta.

---

### 3. Problemas Centrais que S30 Precisa Eliminar

#### 3.1. Estados de fluxo sem semântica operacional forte

Hoje o modelo prevê estados (`draft`, `em_teste`, `ativo`, `pausado`, `deprecado`), mas na prática eles ainda são, na melhor das hipóteses, rótulos cosméticos. O tráfego real de notícias **não** é rigidamente guiado por esses estados. Isso abre brechas graves:

- fluxos marcados como `em_teste` podendo, na prática, processar 100% do tráfego;  
- fluxos `pausados` que continuam sendo usados por alguma parte do sistema;  
- ausência de uma regra única e audível de “quem é o fluxo ativo para tipo X de entrada”.

**Problema a matar**:
> “Estados de fluxo são apenas etiquetas visuais; o sistema não respeita esses estados como contratos operacionais.”

#### 3.2. Ausência de templates oficiais de fluxo para notícias

Um dos pilares de E28 é a existência de **templates de fluxo** para tipos de informação‑chave (ex.: “notícia geral”, “dado quantitativo oficial”, “contestação de alegação”). Sem templates, cada fluxo nasce como um arranjo artesanal, acoplado a quem implementou.  

No contexto de Programa 1, o tipo mais óbvio e crítico para atacar primeiro é o **fluxo de notícias** (especialmente notícias vindas de RSS/APIs de jornais). Hoje:

- não há um template oficial para “Fluxo_Noticias_Geral_v1”;  
- não há catálogo versionado de templates;  
- não há fluxo claro para criar novos fluxos a partir de templates.

**Problema a matar**:  
> “O fluxo de notícias é um arranjo ad‑hoc; não existe um template oficial e versionado que sirva de base para criação e evolução.”

#### 3.3. Operador depende demais de código para operar fluxos

O Console de Fluxos v1 permite observar, mas **não é ainda o cockpit real**. Operações como:

- trocar o agente de uma etapa (ex.: classificador de tipo de notícia);  
- promover um fluxo de `em_teste` para `ativo`;  
- pausar um fluxo com comportamento ruim;  
- reencaminhar itens específicos para reprocessamento;

ainda dependem de **mudanças em código**, deploys ou scripts manuais. Isso é incompatível com:

- operação 24/7;  
- múltiplos fluxos em produção;  
- squads diferentes atuando em camadas distintas.

**Problema a matar**:  
> “Operar um fluxo ainda é uma atividade de desenvolvedor; o console não entrega autonomia real para o operador.”

#### 3.4. Rastreabilidade fraca do que aconteceu com cada notícia

Para um caso concreto (“essa notícia da Fonte X sobre o Tema Y”), ainda não é garantido que seja trivial responder:

- qual fluxo processou essa notícia;  
- quais etapas foram percorridas;  
- qual agente executou cada etapa;  
- quais outputs intermediários foram gerados;  
- qual foi a decisão final (ex.: classificar, flaggar, enviar para debunker manual, etc.).

**Problema a matar**:  
> “A jornada de uma notícia pelo fluxo não é rastreável ponta a ponta de maneira simples, via Console.”

#### 3.5. Observabilidade de fluxo ainda superficial

E28 exige que fluxos de agentes sejam entidades de primeira classe também na camada de **observabilidade**: métricas, logs, alertas.  

Na prática, as métricas hoje ainda estão mais próximas de serviços/infra do que de **fluxos**. Para o fluxo de notícias, ainda não temos, de forma robusta e visível:

- contadores de execuções por fluxo (sucesso/falha);  
- latência p95 por fluxo;  
- noção clara de backlog e gargalo por etapa;  
- condições básicas de alerta ligadas a esses números.

**Problema a matar**:  
> “O estado de saúde do fluxo de notícias ainda não é visível de forma consolidada; o operador voa parcialmente às cegas.”

---

### 4. Objetivo Central da Sprint 30

**Objetivo macro**:  
> “Pegar um fluxo de notícias e transformá‑lo em um fluxo realmente **operável**: criado a partir de template oficial, com estados que mandam de fato no roteamento de eventos, operações básicas (criar, promover, pausar, trocar agente, reprocessar) funcionando via Console, e observabilidade mínima que permita confiar nele em produção.”

Se, ao final da S30, **um fluxo de notícias‑pivô** não estiver operando com essas propriedades, a sprint é NO‑GO, independentemente de quantas tarefas “quase lá” tenham sido executadas.

---

### 5. Objetivos Específicos (Resultados, não Tarefas)

1. **Template oficial de Fluxo de Notícias v1 publicado e utilizável**  
   - Existência de um template “Fluxo_Noticias_Geral_v1”, versionado, armazenado em local canônico, capaz de gerar novos fluxos de notícias com poucas parametrizações (IDs de agentes, thresholds, flags).  
   - O template deve codificar a cadeia mínima: intérprete → classificador de tipo de notícia → analista(s) → debunker(s) → decision maker.

2. **Semântica de estado `draft` / `em_teste` / `ativo` / `pausado` implementada para notícias**  
   - Para notícias, deve existir uma regra única e audível que define qual fluxo `ativo` recebe 100% do tráfego daquele tipo de entrada.  
   - Estados `em_teste` e `pausado` precisam ter efeito observável e verificável no roteamento real de eventos.  
   - Deve ser impossível, via configuração padrão, que um fluxo `em_teste` receba 100% do tráfego de forma silenciosa.

3. **Operações de fluxo via Console substituem intervenções de código para o caso de notícias**  
   - Criar fluxo a partir de template, promover de `draft`/`em_teste` para `ativo`, pausar e retomar fluxo passam a ser operações de Console (com trilha de auditoria), não de deploy.  
   - Trocar o agente principal de pelo menos uma etapa crítica (ex.: classificador) também é feito por configuração via Console, com persistência e histórico mínimo.

4. **Rastreabilidade ponta a ponta para notícias processadas pelo fluxo‑pivô**  
   - Dado um identificador de notícia, o operador consegue, em poucos cliques, ver:  
     - qual fluxo a processou;  
     - quais etapas foram executadas e em que ordem;  
     - o resultado de cada etapa (resumo textual estruturado);  
     - o status final da execução (sucesso/falha, decisão, próximos passos).

5. **Mínimo de observabilidade específica para o fluxo de notícias**  
   - Métricas consolidadas por fluxo para o fluxo‑pivô de notícias:  
     - `fluxo_execucoes_total`, `fluxo_execucoes_sucesso_total`, `fluxo_execucoes_falha_total`;  
     - `fluxo_latencia_p95` (ou equivalente claro);  
     - se aplicável, algum indicador simples de backlog/gargalo por etapa.  
   - Essas métricas devem ser consumíveis de fora (painel ou endpoint) e fazer parte do kit mínimo de operação 24/7 de notícias.

6. **Console de Fluxos reconhecido como cockpit real para notícias pelo squad**  
   - Não basta “teoricamente possível”: o squad precisa usar o Console em cenários reais (ou simulados com dados realistas) e atestar que ele é, de fato, a superfície primária de operação do fluxo de notícias.

---

### 6. Fora de Escopo (Deliberado) para S30

Para manter a sprint focada e atingível com qualidade **9.9/10**, explicitamos o que S30 **não** vai tentar resolver:

1. **Editor visual avançado de fluxos**  
   - Nada de construir um mini‑Airflow dentro do Inspectah nesta sprint. A representação do fluxo pode continuar sendo textual/estrutural, eventualmente com visualização simples, desde que clara.

2. **Sistema de versionamento avançado de pipelines**  
   - Rollouts canário, A/B testing de fluxos, múltiplas versões concorrentes com pesos finos e regras complexas de roteamento ficam para depois. S30 trata do “básico bem feito”: um fluxo ativo por tipo de entrada, um ou outro fluxo em teste com regras simples.

3. **Profundidade interna dos agentes (prompts, comitês, heurísticas)**  
   - Os agentes são tratados, nesta sprint, como caixas pretas com contratos bem definidos. A lapidação interna de prompts, lógica de comitês, etc., pertence a outros épicos/programas.

4. **Suporte full para múltiplos tipos de fluxo**  
   - O foco é **fluxo de notícias** como fluxo‑pivô. Outros tipos (ex.: contestação de alegações, dados quantitativos oficiais) podem ter impactos colaterais benéficos, mas não são critério de GO/NO‑GO de S30.

5. **Camada completa de explicabilidade e replay visual**  
   - Mapas ricos de raciocínio, explicações detalhadas por etapa voltadas ao usuário final e replays sofisticados ficam fora de S30. O alvo aqui é rastreabilidade robusta para o operador.

---

### 7. Métricas de Sucesso Específicas de S30

Para evitar ambiguidade, S30 é considerada **GO** apenas se, ao final, todas as condições abaixo forem verdadeiras:

1. **Fluxo‑pivô de notícias criado via template oficial**  
   - Existe pelo menos 1 fluxo de notícias em produção direta ou prontamente promovível, cujo nascimento se deu a partir de um template versionado.

2. **Estados de fluxo obedecidos pelo roteamento de notícias**  
   - Testes (automatizados e manuais) demonstram que mudar o estado do fluxo altera, de forma previsível, quem processa as notícias daquele tipo.  
   - Não existe caminho “secreto” em que código bypassa a configuração de estado.

3. **Operações críticas realizadas exclusivamente via Console em cenários de teste**  
   - Foram realizados, no mínimo:  
     - N≥3 ciclos completos de “criar fluxo de notícias a partir de template → testar → promover para ativo”;  
     - N≥3 operações de pausa/retomada de fluxo com efeitos visíveis;  
     - N≥2 trocas de agente em etapa crítica feitas via Console.

4. **Rastreabilidade ponta a ponta verificada**  
   - Dado um conjunto de notícias de teste, o squad consegue seguir a jornada de cada uma pelo fluxo, apenas usando ferramentas oficiais (Console + APIs/consultas previstas), sem gambiarras ad hoc.

5. **Observabilidade mínima do fluxo de notícias ativa**  
   - Métricas definidas em 5 são preenchidas com dados reais (ou simulados com realismo) e estão disponíveis em pelo menos um painel ou endpoint de inspeção.  
   - O squad consegue, com base nelas, responder perguntas como: “O fluxo de notícias está saudável? Onde está o gargalo?”

6. **Avaliação subjetiva do squad ≥ 9.9/10**  
   - Cada membro do Squad Fluxos & Orquestração atribui nota ≥ 9.9/10 para a pergunta:  
     > “Para o caso de notícias, o Console de Fluxos agora é, de fato, o cockpit operacional — eu consigo operar esse fluxo sem tocar em código.”

---

### 8. Riscos, Trade‑offs e Decisões Conscientes

1. **Risco de over‑engineering antecipado**  
   - Construir mecanismos muito sofisticados de roteamento, experimentação e versionamento cedo demais.  
   - Mitigação: S30 foca em **um fluxo‑pivô de notícias** com regras simples e claras; tudo o que cheirar a feature de “plataforma global de experimentos de fluxo” é adiado explicitamente.

2. **Risco de acoplamento excessivo com detalhes de agentes**  
   - Tentar resolver, nesta sprint, problemas que pertencem à camada de IA/comitês.  
   - Mitigação: os agentes são tratados como dependências externas com contratos definidos; S30 só garante que o fluxo saiba chamá‑los e operar sobre seus resultados.

3. **Risco de UI tentar virar IDE de fluxos**  
   - Forçar gráficos complexos, arraste‑e‑solte, etc., pode consumir a sprint inteira sem entregar o core operacional.  
   - Mitigação: priorizar clareza e confiabilidade das operações; visual enriquecido vem depois.

4. **Risco de reprocessamento gerar caos**  
   - Se mal desenhado, reprocessamento pode criar loops, duplicidade de eventos ou custos exagerados de LLM.  
   - Mitigação: começar com escopo controlado (faixas de IDs, janelas de tempo pequenas, limites de volume) e deixar bem explícitos os guard‑rails.

---

### 9. Contrato de S30 com E28 e com o Programa 1

S30 não é uma sprint de “embelezar console”, nem de “brincar de fluxo configurable”. Ela é a sprint que precisa colocar em produção o **primeiro fluxo verdadeiramente operável** do Inspectah — o fluxo de notícias — e demonstrar, de forma concreta, que:

- o modelo de Fluxo de Agentes v1 funciona fora do papel;  
- o Console de Fluxos é o cockpit e não um painel de observação;  
- estados de fluxo viram comportamento real;  
- templates começam a disciplinar a criação e evolução de fluxos;  
- observabilidade por fluxo deixa de ser promessa e vira ferramenta.

Tudo o que vier nos próximos capítulos (Gates & Métricas, Arquitetura & Filemap, Execução & Evidências, Tasks) será desenhado para tornar esse contrato verdade com qualidade **mínima de 9.9/10** na avaliação do squad responsável e do conselho técnico do projeto.

