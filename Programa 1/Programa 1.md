# Programa 1 — Consoles & Truth Ops Foundation v1

> Intervalo de sprints: S26–S32  
> Dono lógico: Conselho de Produto Inspectah + Squads consolidados de Programa 1  
> Squads principais envolvidos:  
> • Squad Consoles & UI/Admin (E26)  
> • Squad Fontes & Ingestão 2.0 (E27)  
> • Squad Fluxos & Orquestração de Agentes (E28)  
> • Squad Verdade & Contestação (E29)  
> • Squad Verdade & Interpretação (E30)  
> • Squad Evidence & Traços (E31)  
> • Squad Casos & Narrativas (E32)

---

## 1. Identidade do Programa 1

**Código:** P1  
**Nome curto:** Consoles & Truth Ops Foundation  
**Janela de execução:** S26–S32 (com possibilidade de refinamentos em programas futuros)  
**Status:** Em design consolidado pós-Sprint 25

**Resumo em uma frase:**

> O Programa 1 constrói a fundação operacional do Inspectah para trabalhar com verdade: consoles coerentes, fontes consolidadas, fluxos de agentes operáveis, debunking, consulta de verdade, cofre de evidências e cockpit de casos — tudo integrado, utilizável e auditável, mas ainda sem exigir o Sistema de Blocos e blockchain completos.

### 1.1 Por que este programa existe

Depois da S25, o Inspectah tem:

- uma visão clara de produto;  
- um conjunto de sprints que criaram poderes específicos (ingestão inicial, pipelines, observabilidade, etc.);  
- um roadmap amplo (S26–S65) com ambições fortes (Sistema de Blocos, blockchain, governança, reputação, etc.).

O risco natural nessa fase é pular direto para Fase 2 (blocos, blockchain, reputação) sem ter uma camada operacional de verdade sólida para humanos trabalharem diariamente. O Programa 1 existe para blindar esse risco:

- garante que **antes de ancorar qualquer coisa em cadeia imutável**, a casa esteja arrumada no nível de consoles, fluxos, evidências e casos;  
- consolida uma visão **humanamente operável** da verdade (o que o sistema diz, com base em quê, em qual contexto, com qual história);  
- cria a base para que Programas futuros tratem bloco, âncora, reputação e contestação on-chain como uma evolução natural, e não um remendo em cima de bagunça.

### 1.2 O que o Programa 1 NÃO é

O Programa 1 **não** é a fase final de verdade do Inspectah; ele é a fundação operacional.  
Ele **não** pretende:

- implementar o Sistema de Blocos completo (com toda sua ontologia, promotion rules complexas, sub-blocos, anchors, etc.);  
- ancorar automaticamente todas as verdades em blockchain;  
- resolver governança avançada, staking, reputação e mecanismos on-chain de contestação;  
- expor uma UI pública completa para o mundo inteiro;  
- ser o fim da linha sobre políticas de verdade (é o começo estruturado).

O que Programa 1 faz é preparar o terreno para que tudo isso possa existir depois **sem refatorar a casa inteira**.

---

## 2. Missão, visão e estados-alvo do Programa

### 2.1 Missão do Programa 1

> Entregar uma camada operacional de verdade, centrada em consoles coerentes, que permita ingerir informação de fontes confiáveis, processá-la via fluxos de agentes, contestá-la, decidir sobre ela, registrar evidências e organizar investigações em casos — tudo de forma auditável, rastreável e utilizável por humanos.

### 2.2 Estado-alvo ao final de S32 (frases contratuais)

Ao final do Programa 1 (S26–S32), será verdade que:

1. **Consoles & UI/Admin (E26)** são consistentes, reutilizáveis e estáveis:  
   - existe um padrão de console admin (layout, componentes, estados, interações);  
   - todos os consoles principais (Fontes, Fluxos de Agentes, Debunker, Truth, Evidence, Case Cockpit) seguem esse padrão;  
   - novos consoles podem ser criados reusando a mesma gramática.

2. **Fontes & Ingestão 2.0 (E27)** estão consolidadas:  
   - fontes são cadastradas e geridas em console próprio;  
   - saúde de fontes é monitorada (status, erros, últimos eventos);  
   - ingestão produz eventos de dados coerentes, prontos para fluxos de agentes e verdade.

3. **Fluxos de Agentes (E28)** são explícitos, configuráveis e rastreáveis:  
   - existe modelo único de fluxo (Fluxo, Etapa, Nó de Agente, Execução);  
   - há console que mostra e opera esses fluxos (pausa, retoma, reprocessa);  
   - decisões não vêm de agentes soltos, mas de fluxos modelados.

4. **Debunker v1 (E29)** é camada real de contestação:  
   - contestações entram por canal estruturado;  
   - viram Casos de Debunking com ciclo de vida e console;  
   - fluxos de debunking rodando em cima de E28;  
   - decisões de debunking registradas com rastro de evidências.

5. **Truth Console v1 (E30)** responde o que o sistema diz sobre um claim:  
   - existe modelo de Proposição e Posição de Verdade v1;  
   - há linha do tempo de eventos de verdade (ingestão, contestações, decisões, updates);  
   - é possível consultar por claim ou entidade e obter posição atual + histórico.

6. **Evidence Vault v1 (E31)** é o cofre padrão de evidências:  
   - evidências são registradas com metadados;  
   - decisões sérias de debunking/verdade apontam para evidências no Vault;  
   - é possível rastrear onde uma evidência é usada.

7. **Case Cockpit v1 (E32)** organiza investigações em casos:  
   - casos agregam Proposições, evidências, contestações, decisões e tarefas;  
   - têm ciclo de vida, owner e síntese;  
   - são o ponto de entrada para acompanhar investigações complexas.

8. **A integração entre E26–E32 é real**, não só conceitual:  
   - é possível navegar de um claim (Truth Console) para Debunker, Evidence e Case, e voltar;  
   - consoles compartilham linguagem, estados e objetos (IDs, referências, schemas compatíveis);  
   - logs e IDs permitem reconstruir o caminho de uma informação da ingestão à decisão final.

Estas frases são o contrato macro do Programa 1. Toda Sprint Playbook de S26–S32 que toque esse programa deve apontar explicitamente quais dessas frases está tornando verdade.

---

## 3. Arquitetura conceitual do Programa 1

### 3.1 Mapa dos épicos E26–E32

O Programa 1 é composto pelos épicos:

- **E26 — Consoles & UI/Admin Full**: define a gramática de consoles (layout, componentes, estados, UX de admin).  
- **E27 — Fontes & Ingestão 2.0 em Operação**: cadastro, saúde e ingestão de fontes em console dedicado.  
- **E28 — Fluxo de Agentes Configurável v1**: modelo e console para fluxos de agentes (pipeline lógico).  
- **E29 — Debunker v1**: camada de contestação & revisão operacional.  
- **E30 — Truth Console v1**: consulta e linha do tempo de fatos/proposições.  
- **E31 — Evidence Vault v1**: repositório de evidências & ligações.  
- **E32 — Case Cockpit v1**: casos & narrativas de verdade.

Podemos pensar no Programa 1 como um "X" de duas diagonais:

- Diagonal 1 (fluxo operacional): **Fonte → Ingestão → Fluxo de Agentes → Debunker → Truth Console**.  
- Diagonal 2 (lastro e narrativa): **Evidence Vault → Truth Console → Case Cockpit → Debunker/Fontes**.

No centro desse X está o **modelo de Proposição/Posição de Verdade** (E30), que conversa tanto com operações (fluxos, debunking) quanto com evidência e casos.

### 3.2 Relação entre módulos

Narrando o fluxo típico:

1. **Fontes (E27)** alimentam o sistema com dados estruturados (RSS, APIs, datasets) gerando objetos de entrada (notícias, números, documentos).  
2. Esses objetos passam por **Fluxos de Agentes (E28)**, que interpretam, classificam, analisam, debunkam em pipeline definido.  
3. Quando há contestação explícita ou suspeita, criam-se **Contestações & Casos de Debunking (E29)** que disparam fluxos de debunking e geram decisões.  
4. **Evidence Vault (E31)** guarda documentos, trechos, dados e links que sustentam decisões; Debunker & Truth apontam para ele.  
5. **Truth Console (E30)** agrega isso numa visualização por Proposição: posição atual, histórico de eventos, decisões, evidências.  
6. **Case Cockpit (E32)** agrupa Proposições, evidências e decisões em casos maiores, com tasks e síntese.

Tudo isso aparece para o usuário através da gramática visual única definida em **E26**.

---

## 4. Escopo IN / OUT do Programa 1

### 4.1 Escopo IN (Programa 1)

O Programa 1 **inclui**:

- Consolidação de **todos** os consoles internos críticos para operação de verdade (Fontes, Fluxos de Agentes, Debunker, Truth, Evidence, Case).  
- Modelo lógico mínimo de:
  - Proposição e Posição de Verdade (E30);  
  - Contestação, Caso de Debunking, Decisão (E29);  
  - Evidência e Ligações de Evidência (E31);  
  - Caso, Tasks e Eventos de Caso (E32);  
  - Fluxos de Agentes (E28) e seus estados.

- Integrações entre esses modelos:  
  - referências estáveis entre módulos (IDs, foreign keys, URIs internas);  
  - navegação cruzada entre consoles (links, rotas);  
  - consistência semântica (ex.: `claim_ref`, `proposicao_id`, `evidencia_id`).

- Observabilidade básica integrada:  
  - métricas mínimas em cada console;  
  - logs estruturados com correlação entre ingestão, fluxos, decisões e casos;  
  - scorecards e gates de sprint orientados a esses objetivos.

### 4.2 Escopo OUT (Programa 1)

O Programa 1 **não inclui**:

- Implementação do Sistema de Blocos completo (arquitetura de blocos/sub-blocos, promotion rules completas, anchoring, etc.).  
- Ancoragem automática em blockchain de Proposições, Posições de Verdade, Decisões ou Evidências.  
- Mecanismos avançados de reputação, staking, bonds, penalidades e incentivos econômicos.  
- UI pública externa (para cidadãos em geral) — consoles aqui são focados em operação interna e times especializados.  
- Ferramentas de analytics pesadas, dashboards altamente customizáveis ou camadas de BI avançado — o foco é operacional, não analítico.

---

## 5. Modelo operacional do Programa 1

### 5.1 Visão "por fluxo"

Um caso típico percorre os seguintes steps:

1. **Ingestão** (E27):
   - Fonte cadastrada gera item (notícia, dado, documento);  
   - item entra no pipeline de ingestão 2.0.

2. **Fluxo de Agentes** (E28):  
   - item acionado por fluxo padrão (ex.: "notícia política");  
   - passa por interpretação, classificação, análise, debunking leve, decisão preliminar.

3. **Verdade preliminar** (E30):  
   - outputs dos fluxos podem gerar/atualizar Proposições e Posições de Verdade preliminares (`nao_avaliado`, `inconclusivo`, `provavelmente_verdadeiro` etc.).

4. **Contestação & Debunking** (E29):  
   - se alguém contesta (ou se o sistema detecta inconsistência), abre-se Contestação e/ou Caso de Debunking;  
   - fluxos de debunking mais profundos rodam;  
   - decisões de debunking são registradas.

5. **Evidência** (E31):  
   - durante o processo, evidências são coletadas/registradas no Evidence Vault;  
   - decisões de debunking e Posições de Verdade apontam para essas evidências.

6. **Truth Console** (E30) e **Case Cockpit** (E32):  
   - exibem resultado consolidado por Proposição (Truth) e por caso/investigação (Case Cockpit).

### 5.2 Visão "por console"

- Consoles de **Cadastro/Admin (E26/E27/E28)**:  
  Fontes, fluxos, configurações de agentes, templates de fluxo.

- Consoles de **Verdade & Contestação (E29/E30)**:  
  Debunker (fila de casos de debunking); Truth (proposições e posições de verdade).

- Consoles de **Lastro & Narrativa (E31/E32)**:  
  Evidence Vault (evidências e ligações); Case Cockpit (casos e narrativas).

---

## 6. Uso do Sprint Playbook v2 no Programa 1

### 6.1 Capítulos & sub-capítulos

Cada sprint relacionada ao Programa 1 deve usar o Sprint Playbook v2 (6 capítulos × 4 blocos) de forma alinhada a este documento. Em particular:

- **Capítulo 1 — Contexto & Problemas a Resolver**:  
  - deve ancorar explicitamente os problemas do sprint em um ou mais épicos E26–E32 **e** nas frases deste Programa 1 (Seção 2.2);  
  - deve listar quais estados-alvo do Programa 1 estão sendo aproximados.

- **Capítulo 2 — Gates, Métricas & DoD**:  
  - deve incluir gates que garantam coerência com o Programa 1 (ex.: nenhum novo console fora do padrão E26, nenhuma decisão séria sem evidência no Vault, etc.);  
  - deve amarrar métricas de sprint às métricas de sucesso do Programa (Seção 9).

- **Capítulo 3 — Arquitetura & Filemap**:  
  - deve refletir o posicionamento de artefatos nos módulos correspondentes (app/api/..., frontend/..., schemas, migrations);  
  - deve explicitar dependências entre E26–E32 (ex.: API de Evidence sendo usada pelo Debunker).

- **Capítulo 4 — Execução & Evidências**:  
  - tasks/waves de Codex devem apontar diretamente para as mudanças de estados-alvo do Programa e dos épicos;  
  - evidências geradas (logs, prints, scorecards) devem provar que esses estados foram atingidos.

### 6.2 Integração com Codex (execução via waves)

Regras práticas para usar o Codex dentro do Programa 1:

- Nunca enviar "a sprint inteira" num prompt solto; sempre trabalhar com:
  - contexto macro (Programa 1 + épico);  
  - capítulo específico (Cap.3 ou Cap.4) como contrato;  
  - waves bem definidas (ex.: Wave 1 = schemas + migrations; Wave 2 = APIs; Wave 3 = frontend; Wave 4 = testes/gates).

- Sempre reforçar, no prompt para Codex:
  - qual parte do Programa 1 está sendo mexida;  
  - quais frases da Seção 2.2 são relevantes;  
  - quais épicos E26–E32 precisam ser respeitados.

---

## 7. Critérios de qualidade & guard-rails do Programa 1

### 7.1 Critérios específicos do Programa 1

Além dos critérios gerais do projeto Inspectah (gates, ORRs, scorecards, etc.), o Programa 1 tem critérios próprios de qualidade:

1. **Coerência de UI/Admin (E26)**:  
   - nenhum console pode ter UX "alienígena" em relação aos demais;  
   - qualquer componente genérico criado deve ser reutilizável (tabelas, filtros, empty states, etc.).

2. **Centralização de evidência (E31)**:  
   - nada de evidência séria vivendo só em texto solto ou anexo de decisão;  
   - Evidence Vault é o único lugar canônico para evidências.

3. **Rastreabilidade fim a fim**:  
   - deve ser sempre possível, a partir de uma Posição de Verdade ou decisão de debunking, navegar para: evidências, fluxos, contestações, fontes, casos.

4. **Estados explícitos em vez de magia**:  
   - nada de processos invisíveis;  
   - tudo deve ter estados formais (case state, debunk state, truth state, evidence status, etc.).

5. **Preparação para Sistema de Blocos, sem antecipá-lo**:  
   - modelos de Proposição, Evidência, Caso e Eventos devem ser desenhados de forma a ser promovidos a blocos mais tarde;  
   - mas o Programa 1 não implementa toda a mecânica de blocos.

### 7.2 Anti-objetivos do Programa 1

- Não transformar consoles internos em produto de analytics para usuário final.  
- Não criar workflows humanamente impossíveis de operar (complexidade teórica > utilidade prática).  
- Não duplicar entidades (ex.: ter "quase Proposição" em outro módulo só porque era mais rápido).  
- Não enfraquecer a separação conceitual:
  - claim de entrada ≠ Proposição;  
  - decisão de debunking ≠ posição de verdade;  
  - evidência ≠ verdade.

---

## 8. Riscos principais do Programa 1

1. **Complexidade conceitual demais cedo demais**: tentar modelar toda a ontologia de verdade, evidência e casos em v1, travando entregas.  
2. **Under-integration**: épicos entregues como silos (E29, E30, E31, E32) que não conversam bem, gerando sensação de "4 sistemas diferentes" em vez de uma plataforma.  
3. **Drift para Fase 2**: sprints começarem a empurrar blockchain, blocos e governança para dentro do Programa 1, sem base estável.  
4. **Déficit de usabilidade**: consoles muito corretos conceitualmente, porém inutilizáveis no dia a dia; operadores voltam para planilhas e docs externos.  
5. **Acoplamento exagerado entre camadas**: por exemplo, Truth Console dependendo diretamente de detalhes de fluxos de agentes, sem uma camada intermediária de eventos/states.

Mitigações esperadas:

- Revisões regulares de Programa 1 pelo conselho (Knuth, Jobs, Pearl, Stonebraker, Norvig, Percy, etc.).  
- Uso disciplinado do Sprint Playbook para garantir que cada sprint move o Programa 1 para frente sem quebrar nada.  
- Revisão cruzada entre squads (ex.: Squad Evidence revisando propostas de Debunker, etc.).

---

## 9. Métricas de sucesso do Programa 1

Alguns indicadores para saber se o Programa 1 cumpriu sua missão:

- **Adoção interna de consoles**: quantos times usam de fato Fontes, Fluxos, Debunker, Truth, Evidence, Case no dia a dia.  
- **Tempo médio para responder "o que o sistema diz sobre X"** (usando Truth Console) vs baseline anterior.  
- **Percentual de decisões de debunking com evidências formais vinculadas** (via Evidence Vault).  
- **Percentual de claims sensíveis com Proposição/Posição de Verdade associada**.  
- **Percentual de temas críticos que possuem pelo menos um Caso em Case Cockpit** quando necessário.  
- **Número de investigações que exigem docs externos para se organizar** — idealmente caindo fortemente.  
- **Nível de integração de navegação cruzada** (links funcionando entre consoles, sem ilhas).  
- Feedback qualitativo dos squads de operação (é possível trabalhar só dentro do Inspectah para um caso típico?).

---

## 10. Encerramento do Programa 1 e relação com Programas futuros

### 10.1 Critérios para considerar Programa 1 "encerrado"

Programa 1 pode ser considerado "encerrado" (para fins de S26–S32) quando:

- todos os épicos E26–E32 atingirem seus estados-alvo mínimos definidos em seus docs;  
- as frases de estado-alvo da Seção 2.2 forem verdadeiras em ambiente de produção v0.5+ (não só dev);  
- as principais métricas de sucesso (Seção 9) estiverem acima de thresholds acordados (a definir em Cap.2 de sprints específicas);  
- o sistema estiver pronto para que Programas de Fase 2 (Sistema de Blocos, blockchain, governança avançada) possam se apoiar nesses módulos sem migrar tudo.

### 10.2 Preparação para Programas futuros

Programa 1 deixa como legado:

- modelos estáveis para Proposição, Posição de Verdade, Evidência, Caso, Contestação, Fluxos;  
- consoles consistentes que podem ser ampliados ou "espelhados" em versões públicas;  
- padrões de rastreabilidade e auditabilidade que servem como blueprint para System of Blocks e ancoragem on-chain;  
- uma cultura de trabalho "por caso" e "por evidência" que conversa bem com o ideal de "database of truth" do Inspectah.

---

## 11. Notas finais

Este documento é a constituição do **Programa 1 — Consoles & Truth Ops Foundation v1**.  

Ele faz a ponte entre:

- o roadmap macro (S26–S65);  
- os épicos E26–E32 (nível épico);  
- e o Sprint Playbook v2 (nível sprint).

Qualquer sprint em S26–S32 que mexa com console, ingestão 2.0, fluxos de agentes, debunking, verdade, evidências ou casos **deve** se referenciar a este documento e aos épicos correspondentes, declarando explicitamente:

- quais frases de estado-alvo do Programa 1 (Seção 2.2) está tornando verdade;  
- quais épicos E26–E32 estão sendo movidos para frente;  
- quais métricas de sucesso do Programa 1 serão impactadas.

Mudanças profundas na forma como o Inspectah opera verdade, evidência ou casos devem primeiro ser refletidas neste Programa 1 e, em seguida, desdobradas nos épicos e sprints. Assim, o sistema cresce sem perder coerência e sem se afastar da missão central: ser um ambiente de verdade auditável, explicável e tecnicamente sólido.

