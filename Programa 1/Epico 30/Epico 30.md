# Épico E30 — Truth Console v1 (Consulta & Linha do Tempo de Fatos)

> Programa 1 — Consolidação & Consoles Full  
> Dono lógico: Squad Verdade & Interpretação  
> (Judea Pearl, Karl Popper, Michael Stonebraker, Peter Norvig, Percy Liang, Steve Jobs)

---

## 1. Identidade do épico

**Código:** E30  
**Nome curto:** Truth Console v1 (Consulta & Linha do Tempo de Fatos)  
**Programa:** Programa 1 — Consolidação & Consoles Full (S26–S32)  
**Status:** Em design  

**Resumo em uma frase:**

> E30 entrega o primeiro Truth Console operacional do Inspectah: uma interface única para consultar o que o sistema sabe (ou não sabe) sobre um claim, entidade ou tema em determinado tempo, com linha do tempo de fatos, decisões de debunking e evidências associadas — ainda sem exigir o Sistema de Blocos completo ou ancoragem em blockchain.

---

## 2. Problema

Sem o Truth Console v1, o Inspectah tem um problema de identidade e confiança:

- Fatos, claims, contestações e evidências ficam espalhados em logs, tabelas e consoles específicos (Fontes, Debunker, Evidence Vault, Cases), mas não há um **ponto focal** de "o que o sistema está afirmando sobre X agora".  
- Usuários internos não conseguem responder com segurança perguntas básicas como:
  - "Qual é a posição atual do Inspectah sobre esse claim?"  
  - "Quando essa posição mudou pela última vez e por quê?"  
  - "Quais contestações foram feitas e que decisões já saíram?"  
  - "Quais evidências sustentam (ou derrubam) essa posição?"  
- Sem uma visão consolidada, cada time começa a construir suas próprias visões locais de verdade, abrindo espaço para inconsistência, divergências e perda de rastreabilidade.  
- A ausência de um Truth Console impede que, no futuro, o Sistema de Blocos e a camada de governança tenham um "front" simples para humanos entenderem o que foi promovido a fato.

E30 existe para criar esse **cérebro de consulta de verdade v1**, antes da fase mais pesada de blocos+blockchain, mas já respeitando os princípios de auditabilidade e rastreabilidade do Inspectah.

---

## 3. Visão & Estados-alvo

### 3.1 Frase de visão

> Quando E30 estiver completo, qualquer pessoa autorizada poderá abrir o Truth Console, buscar por um claim, entidade ou tema, e ver uma visão consolidada: qual é a posição atual do sistema, quais foram as posições anteriores, que contestações ocorreram, quais decisões de debunking existem e quais evidências centrais sustentam cada mudança.

### 3.2 Estados-alvo (lista canônica)

Ao final de E30, será verdade que:

1. **Existe um modelo lógico único de Proposição/Claim v1**: forma normalizada de representar "sobre o que estamos falando" (ex.: "IPCA Brasil 2024 = 4,5%", "Fulano ocupava cargo X em data Y").
2. **Existe um modelo de Posição de Verdade v1**, que registra a posição atual e posições passadas do sistema sobre uma Proposição (ex.: `nao_avaliado`, `inconclusivo`, `provavelmente_verdadeiro`, `provavelmente_falso`, etc.), com timestamps e causa da mudança.
3. **O Truth Console v1 permite consulta por claim, entidade, tema e período**, retornando lista de Proposições e suas Posições de Verdade atuais.
4. **Para cada Proposição, o Truth Console exibe uma linha do tempo de eventos relevantes**, incluindo: ingestão inicial, contestações (E29), decisões de debunking, mudanças de posição, anexos de evidência.
5. **Pelo menos um caminho de consulta "por entidade" existe**, permitindo responder perguntas como "o que o Inspectah afirma hoje sobre <entidade X>?".
6. **Toda Posição de Verdade v1 aponta para suas origens operacionais**, isto é: contestações e decisões de debunking associadas, execuções de fluxo de agentes (E28), fontes e evidências principais.
7. **O Truth Console v1 fornece respostas que são claramente rotuladas com seu grau de certeza e data** (nada de resposta solta sem timestamp ou contexto), e deixa explícito quando o sistema não sabe.

Esses estados são o contrato de E30. Sprints que atacarem Truth Console precisam declarar quais dessas frases pretendem tornar verdade.

---

## 4. Escopo IN / OUT

### 4.1 Escopo IN

E30 cobre, no mínimo:

- Definição do **modelo lógico de Proposição/Claim v1**:
  - identificador estável da proposição (ID lógico);  
  - texto normalizado;  
  - tipo de proposição (fato numérico, evento, relação entre entidades, afirmação booleana, etc.);  
  - entidades envolvidas;  
  - domínio/tema;  
  - granularidade temporal (ex.: "em 31/12/2024", "no período 2023", "no governo X").

- Definição do **modelo de Posição de Verdade v1**:
  - estado atual;  
  - histórico de estados anteriores;  
  - motivo da transição (ex.: nova decisão de debunking, atualização de dado oficial, correção de erro).

- Definição da **linha do tempo de eventos de verdade** para uma Proposição:
  - ingestões relevantes;  
  - contestações (E29);  
  - execuções de fluxos de debunking (E28);  
  - decisões de debunking;  
  - atualizações de fontes oficiais.

- Criação do **Truth Console v1 (UI/Admin)**, aderente a E26, com pelo menos:
  - busca por texto livre de claim;  
  - busca por entidade;  
  - filtros por tema, tipo de proposição, estado de verdade;  
  - visão detalhada de Proposição + linha do tempo.

- Integração mínima com E27 (Fontes/Ingestão):
  - saber de quais fontes vieram as informações usadas para gerar uma posição de verdade.

- Integração mínima com E29 (Debunker v1):
  - mostrar contestações e casos relacionados à Proposição;  
  - vincular decisões de debunking às mudanças de posição.

- Integração conceitual com a visão de Sistema de Blocos, mas **sem exigir** blocos plenos ou blockchain ainda:
  - o modelo de Proposição/Posição deve ser compatível com uma futura promoção a blocos.

### 4.2 Escopo OUT

E30 **não** cobre (nesta fase):

- Sistema de Blocos completo (blocos, sub-blocos, anchors, promotion rules) como implementado em Fase 2.  
- Ancoragem em blockchain de Posições de Verdade (isso é Fase 2, já mapeada em outros docs).  
- Mecanismo avançado de políticas de promoção automática de verdade (isso toca Programas de Governança & Truth Ops posteriores).  
- UI pública para qualquer cidadão consultar; o foco aqui é console operacional interno (mesmo que no futuro seja base para algo público).

---

## 5. Personas & casos de uso

### 5.1 Personas

- **Analista de Verdade** — precisa entender, para um claim ou tema, qual é a posição do Inspectah e por quê.  
- **Operator Debunker** — quer ver, para um caso de debunking, como a decisão afetou a posição de verdade de uma Proposição.  
- **Investigador de Casos** — trabalha no Case Cockpit e precisa abrir rapidamente a visão de verdade relacionada a um caso (quem disse o quê, quando mudou, que evidências existem).  
- **Truth/Policy Owner** — responsável pelas políticas de promoção de verdade e quer ver padrões de mudança (ex.: temas onde a posição muda muito, domínios com alta taxa de contestações).

### 5.2 Casos de uso principais

1. **"O Inspectah considera esse claim verdadeiro ou falso hoje?"**
   - Usuário cola o claim no campo de busca ou acessa via link a partir de outro console.  
   - Truth Console retorna a Proposição correspondente (ou sugere matches).  
   - Mostra a Posição de Verdade atual (estado + grau de certeza + data da última mudança).  
   - Mostra um resumo das principais evidências e contestações.

2. **"Quando e por que essa posição mudou?"**
   - Usuário abre a mesma Proposição.  
   - Vai para aba de linha do tempo.  
   - Vê eventos ordenados: ingestões, contestações, decisões, mudanças de posição.  
   - Consegue clicar em um evento de mudança para ver qual decisão/caso/evidência provocou a transição.

3. **"Quais claims relevantes existem sobre essa entidade?"**
   - Usuário busca por uma entidade (ex.: "Ministério da Fazenda", "Empresa XPTO").  
   - Truth Console lista Proposições associadas, com estados de verdade atuais.  
   - Permite filtrar por tema (economia, política, etc.) e por estado (inconclusivo, contestado, etc.).

4. **"Quais claims estão mais instáveis?"**
   - Truth/Policy Owner abre uma visão de Proposições com muitas mudanças de posição em janela recente.  
   - Usa isso para investigar temas mais voláteis ou de dados mais frágeis.

---

## 6. Modelos conceituais centrais

### 6.1 Proposição v1

A Proposição é a unidade lógica de "sobre o que é essa verdade".

Campos lógicos mínimos:

- `id`  
- `texto_normalizado` (ex.: "IPCA Brasil 2024 foi X%", com placeholders resolvidos)  
- `tipo` (`fato_numerico`, `evento`, `relacao_entidades`, `afirmacao_booleana`, `outro`)  
- `entidades` (lista de refs para entidades/actors relevantes)  
- `dominio` (ex.: `economia`, `politica`, `saude`, `clima`)  
- `escopo_temporal` (ponto ou intervalo)  
- `tags` (livres, mas controladas)  
- `created_at`, `updated_at`.

Observação: a normalização exata pode evoluir; v1 precisa ser consistente o suficiente para evitar duplicação trivial de proposições idênticas.

### 6.2 Posição de Verdade v1

Modela o que o Inspectah "afirma" sobre uma Proposição em determinado momento.

- `id`  
- `proposicao_id`  
- `estado_atual` (taxonomia de v1 sugerida):  
  - `nao_avaliado` (só ingestão, sem análise);  
  - `inconclusivo`;  
  - `provavelmente_falso`;  
  - `nao_suportado`;  
  - `parcialmente_verdadeiro`;  
  - `provavelmente_verdadeiro`.  
- `confianca` (opcional, ex.: escala 0–1 ou qual. `baixa/media/alta`)  
- `ultima_atualizacao` (timestamp)  
- `origem_decisao_atual` (ref para Decisão de Debunking, ingestão oficial, correção manual, etc.)

Histórico de mudanças pode ser modelado em entidade separada:

- **Evento de Posição de Verdade**  
  - `id`, `proposicao_id`, `estado_anterior`, `estado_novo`, `motivo`, `origem_evento_ref`, `timestamp`.

### 6.3 Evento de Verdade (linha do tempo)

Eventos que compõem a linha do tempo de uma Proposição:

- ingestão inicial de claim;  
- contestações (E29);  
- abertura/fechamento de Casos de Debunking;  
- execuções de fluxos de debunking;  
- decisões de debunking;  
- atualizações de fontes oficiais;  
- correções manuais excepcionais.

Campos mínimos:

- `id`  
- `proposicao_id`  
- `tipo_evento` (`ingestao`, `contestacao`, `caso_aberto`, `exec_fluxo`, `decisao_debunking`, `atualizacao_oficial`, `correcao_manual`, etc.)  
- `ref_origem` (ID específico do evento em outro módulo: ingestão, Caso, Execução de Fluxo, etc.)  
- `timestamp`  
- `resumo` (texto curto).

### 6.4 Ligações com Debunker e Evidence

- Proposição ↔ Casos de Debunking (E29): via `claim_ref` consistente.  
- Proposição ↔ Decisões de Debunking: usada como `origem_decisao_atual` de Posição de Verdade.  
- Proposição ↔ Evidências principais: lista de refs para evidências (E31/Evidence Vault) que são centrais para a posição atual.

---

## 7. Requisitos funcionais

### 7.1 Truth Console — Busca e descoberta

- Campo de **busca por texto livre** (claim textual).  
- Busca por **entidade** (com autosuggest de entidades cadastradas).  
- Filtros:
  - por domínio;  
  - por tipo de proposição;  
  - por estado de verdade;  
  - por criticidade/impacto (quando disponível).

- Resultados em lista, cada linha com:  
  - trecho do texto da Proposição;  
  - entidades principais;  
  - estado de verdade atual;  
  - data da última atualização;  
  - indicador de contestações ativas/recentes.

### 7.2 Detalhe da Proposição

Tela de detalhe deve conter, no mínimo:

- cabeçalho com texto da Proposição, entidades, domínio, escopo temporal;  
- bloco de **Posição de Verdade atual** (estado, confiança, data da última atualização, origem);  
- link para Casos de Debunking associados (E29);  
- bloco de evidências principais (referências ao Evidence Vault, quando existir);  
- trilha de navegação para voltar à busca ou navegar entre proposições relacionadas.

### 7.3 Linha do tempo de eventos

- Aba/área "Linha do tempo":
  - lista cronológica de eventos de verdade (ingestão, contestações, execuções de fluxo, decisões, atualizações oficiais);  
  - cada evento com tipo, timestamp, resumo, link para detalhe (em outro console quando aplicável).  
- Possibilidade de filtrar eventos por tipo (ex.: mostrar só decisões de debunking e mudanças de posição).

### 7.4 Integração com outros consoles

- A partir de um Claim em qualquer console (Debunker, Case, Evidence, etc.), deve haver forma de abrir diretamente a Proposição correspondente no Truth Console.  
- A partir do Truth Console, deve ser possível:
  - abrir Caso de Debunking relevante (E29);  
  - abrir evidência relevante no Evidence Vault (E31, quando existir);  
  - abrir casos/investigações no Case Cockpit (E32) quando acoplados.

### 7.5 Estados e vazios

- Quando não há Proposição correspondente a um claim buscado, o console deve:
  - deixar claro que o sistema "ainda não sabe";  
  - sugerir ações (ex.: criar Proposição a partir do claim, ou abrir contestação/investigação).  
- Quando há Proposição mas estado é `nao_avaliado`, exibir esse fato explicitamente, sem inventar certeza.

---

## 8. Requisitos não funcionais

### 8.1 Consistência e integridade

- Nenhuma mudança de Posição de Verdade pode acontecer sem criar um Evento de Posição correspondente.  
- IDs de Proposições devem ser estáveis e não depender de detalhes voláteis de representação textual.

### 8.2 Desempenho

- Consultas típicas (por claim ou entidade) devem responder em tempo aceitável (ex.: < 1–2s em dataset inicial), para que o console seja utilizável em operação diária.  
- Linha do tempo deve ser paginada ou agregada para Proposições com muitos eventos.

### 8.3 Observabilidade

- Métricas mínimas:
  - número de Proposições ativas;  
  - número de Proposições por estado de verdade;  
  - número de mudanças de posição em janela recente;  
  - tempo médio entre contestações e mudança de posição (quando aplicável).

- Logs estruturados para consultas e mudanças de posição (para auditoria e tuning).

### 8.4 Segurança

- Controle de acesso para evitar que pessoas sem permissão vejam Proposições sensíveis ou contestações com dados pessoais.  
- Posições de Verdade podem ser consultáveis em agregados (ex.: estatísticas por tema) mesmo quando detalhes são restritos.

### 8.5 Consistência com E26

- Truth Console é console admin de primeira classe:  
  - layout e componentes seguindo E26;  
  - mesma linguagem visual de estados e erros;  
  - experiência consistente com Debunker, Evidence, Case Cockpit.

---

## 9. Métricas de sucesso do épico

Indicadores que medem se E30 cumpriu seu papel:

- **Tempo médio para responder "o que o sistema diz sobre X"**: deve cair drasticamente quando o Truth Console é introduzido.  
- **Percentual de contestações/casos com Proposição associada**: deve subir com a introdução de Proposições v1.  
- **Número de consultas ao Truth Console por semana**: indica adoção interna.  
- **Quantidade de decisões/afirmações "sem contexto"** (sem link para Proposição/linha do tempo) deve cair a praticamente zero nos módulos que já integram com E30.

---

## 10. Decomposição em sprints

### 10.1 Entregas sugeridas

- **E30.1 — Modelo de Proposição & Posição de Verdade v1 + eventos básicos**  
  - Definição e implementação de Proposição v1;  
  - Posição de Verdade v1;  
  - Eventos de Posição;  
  - APIs internas mínimas para consulta.

- **E30.2 — Truth Console v1 (busca + detalhe + linha do tempo)**  
  - UI/Admin aderente a E26;  
  - busca por claim e entidade;  
  - detalhe de Proposição;  
  - linha do tempo com eventos básicos.

- **E30.3 — Integrações com Debunker/Fontes & refinamentos de posição**  
  - ligação com Casos/Decisões de Debunking (E29);  
  - ligação básica com Fontes/Ingestão (E27);  
  - ajustes na taxonomia de estados de verdade e regras de atualização.

### 10.2 Relação com sprints S26–S32

- S26–S27: podem abrigar E30.1 em paralelo com a fundação de E27/E28/E29, preparando o terreno de Proposições.  
- S28–S29: foco em E30.2, entregando um Truth Console utilizável para alguns domínios prioritários.  
- S30–S32: E30.3 aprofunda integrações, adiciona refinamentos e cobre mais domínios.

---

## 11. Riscos, decisões e anti-objetivos

### 11.1 Riscos

- **Overmodeling cedo demais:** tentar criar um modelo de Proposição perfeito para todos os tipos de claim e travar o épico.  
- **Divergência com o futuro Sistema de Blocos:** se o modelo v1 for muito diferente do blueprint de blocos, gera retrabalho pesado depois.  
- **UX excessivamente abstrata:** console tão cheio de conceitos (proposição, posição, eventos) que o operador não entende.

### 11.2 Decisões de design esperadas

- Começar com um conjunto limitado de tipos de Proposição (fatos numéricos e relações básicas entre entidades) e evoluir.  
- Modelar Proposição/Posição de forma deliberadamente compatível com a visão de blocos:  
  - Proposição v1 pode virar um tipo de bloco raiz no futuro;  
  - Posições de Verdade podem virar estados anexados a blocos.  
- Manter o Truth Console focado em **responder perguntas concretas**, não em expor toda a ontologia interna.

### 11.3 Anti-objetivos

- E30 **não** é ainda o "Blocos UI" completo; ele é a face de consulta v1, em cima de um modelo que será promovido depois.  
- E30 **não** implementa políticas avançadas de promoção/reversão de verdade; isso pertence a Programas de Governança & Truth Ops.  
- E30 **não** tenta ser um motor de busca geral; ele é otimizado para perguntas sobre verdade/fatos.

---

## 12. Conexão com outros épicos e programas

- **E26 — Console Full:** Truth Console é um dos consoles mais importantes; deve ser exemplo de gramática visual e UX.  
- **E27 — Fontes & Ingestão:** Proposições frequentemente se baseiam em dados de fontes específicas; integrações permitirão responder "esta posição vem de quais fontes?".  
- **E28 — Fluxos de Agentes:** decisões de verdade podem depender de fluxos específicos; eventos de execução desses fluxos aparecem na linha do tempo.  
- **E29 — Debunker v1:** Debunker é o principal produtor de decisões de debunking que afetam Posições de Verdade; E30 deve exibir isso com clareza.  
- **E31 — Evidence Vault (épico futuro):** evidências usadas em decisões de verdade serão centralizadas em E31; E30 referencia essas evidências.  
- **E32 — Case Cockpit:** casos de investigação podem amarrar múltiplas Proposições e suas Posições de Verdade; E30 oferece a visão "por fato", E32 a visão "por caso".  
- **Programas de Fase 2 (Sistema de Blocos, Blockchain):** Proposição/Posição/Eventos aqui definidos deverão ser promovidos/espelhados para blocos e âncoras, mas E30 já oferece a UX e o modelo mental para isso.

---

## 13. Notas finais

Este documento define a visão, escopo, modelos e contratos do **Épico E30 — Truth Console v1 (Consulta & Linha do Tempo de Fatos)**.

Sprints que tocarem verdade/consulta de fatos devem usar este épico como referência:

- Cap.1 do Sprint Playbook: quais problemas de E30 estão sendo atacados e quais estados-alvo serão tornados verdade.  
- Cap.2: gates e scorecards relacionados a Proposições, Posições de Verdade e integridade da linha do tempo.  
- Cap.3: schemas, APIs e filemap do Truth Console e da camada de verdade.  
- Cap.4: tasks e Waves que implementam E30.1, E30.2 ou E30.3.

Qualquer mudança profunda na forma como o Inspectah representa e expõe "verdade" deve ser refletida neste épico antes de chegar a novas sprints ou ao Sistema de Blocos completo.